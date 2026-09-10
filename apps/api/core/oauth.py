"""Ijtimoiy kirish — Google, GitHub, Telegram (ADR-0016).

Kutubxona qo'shilmadi. `django-allauth` o'z shablonlari, URL'lari va
modellari bilan keladi, bizda esa API headless va frontend alohida —
uchala provayder ham oddiy HTTP almashuvi, xuddi email zanjiridagi kabi.

Telegram qolgan ikkitasidan farq qiladi: u OAuth emas, imzolangan
ma'lumot beradi va **email bermaydi**. Shu sababli faqat Telegram bilan
ochilgan hisobda pochta bo'lmaydi va u parolni tiklashdan foydalana
olmaydi — foydalanuvchi keyin sozlamalarda pochta qo'shishi kerak.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import secrets
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any

from django.conf import settings

from core import handles
from core.models import User

log = logging.getLogger(__name__)

USER_AGENT = "RankWant/1.0 (+https://rankwant.bugvector.uz)"

#: Har provayder uchun: kalit sozlanganini bildiruvchi sozlama nomlari.
#: Kaliti yo'q provayder ro'yxatga umuman tushmaydi va uning tugmasi
#: frontendda ko'rinmaydi — email zanjiridagi bilan bir xil qoida.
REQUIRED: dict[str, tuple[str, ...]] = {
    "google": ("GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET"),
    "github": ("GITHUB_CLIENT_ID", "GITHUB_CLIENT_SECRET"),
    "telegram": ("TELEGRAM_BOT_TOKEN",),
}

#: Telegram widget imzosi shuncha vaqt amal qiladi. Qayta yuborishning
#: oldini oladi: eski imzolangan ma'lumot bilan kirib bo'lmaydi.
TELEGRAM_MAX_AGE = 300


class OAuthError(Exception):
    """Almashuv yiqildi. Chaqiruvchi foydalanuvchini xato sahifasiga qaytaradi."""


@dataclass(frozen=True)
class Identity:
    """Provayder qaytargan kimlik. `email` bo'sh bo'lishi mumkin (Telegram)."""

    provider: str
    uid: str
    email: str
    suggested: str


def configured() -> list[str]:
    """Sozlangan provayderlar — frontend shu ro'yxat bo'yicha tugma chizadi."""
    return [
        name for name, keys in REQUIRED.items() if all(getattr(settings, key, "") for key in keys)
    ]


def redirect_uri(provider: str) -> str:
    return f"{settings.SITE_URL}/api/v1/auth/{provider}/callback/"


def _request(
    url: str, *, data: dict[str, str] | None = None, headers: dict[str, str] | None = None
) -> Any:
    body = urllib.parse.urlencode(data).encode() if data else None
    req = urllib.request.Request(
        url,
        data=body,
        method="POST" if data else "GET",
        headers={"Accept": "application/json", "User-Agent": USER_AGENT, **(headers or {})},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        detail = exc.read()[:300].decode("utf-8", "replace")
        raise OAuthError(f"HTTP {exc.code}: {detail}") from exc
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
        raise OAuthError(str(exc)) from exc


# ── Google ────────────────────────────────────────────────────────────


def _google_authorize(state: str) -> str:
    query = urllib.parse.urlencode(
        {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": redirect_uri("google"),
            "response_type": "code",
            "scope": "openid email",
            "state": state,
            # Ro'yxatni har safar ko'rsatadi — bir nechta Google hisobi
            # bo'lgan odam qaysi biri bilan kirayotganini bilishi kerak.
            "prompt": "select_account",
        }
    )
    return f"https://accounts.google.com/o/oauth2/v2/auth?{query}"


def _google_identity(code: str) -> Identity:
    token = _request(
        "https://oauth2.googleapis.com/token",
        data={
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": redirect_uri("google"),
            "grant_type": "authorization_code",
        },
    )
    # `id_token` ni o'zimiz tekshirmaymiz: `userinfo` shu ma'lumotni
    # beradi va JWT imzosini tekshirish uchun kalit halqasini yuklab,
    # keshlab yurish kerak bo'lardi — bitta so'rov ancha arzon.
    info = _request(
        "https://www.googleapis.com/oauth2/v3/userinfo",
        headers={"Authorization": f"Bearer {token.get('access_token', '')}"},
    )
    email = info.get("email", "") if info.get("email_verified") else ""
    return Identity("google", str(info.get("sub", "")), email, email.split("@")[0])


# ── GitHub ────────────────────────────────────────────────────────────


def _github_authorize(state: str) -> str:
    query = urllib.parse.urlencode(
        {
            "client_id": settings.GITHUB_CLIENT_ID,
            "redirect_uri": redirect_uri("github"),
            "scope": "read:user user:email",
            "state": state,
        }
    )
    return f"https://github.com/login/oauth/authorize?{query}"


def _github_identity(code: str) -> Identity:
    token = _request(
        "https://github.com/login/oauth/access_token",
        data={
            "code": code,
            "client_id": settings.GITHUB_CLIENT_ID,
            "client_secret": settings.GITHUB_CLIENT_SECRET,
            "redirect_uri": redirect_uri("github"),
        },
    )
    auth = {"Authorization": f"Bearer {token.get('access_token', '')}"}
    info = _request("https://api.github.com/user", headers=auth)
    # GitHub asosiy pochtani profilda bermasligi mumkin — u alohida
    # endpointda va faqat TASDIQLANGANI olinadi.
    email = ""
    try:
        rows = _request("https://api.github.com/user/emails", headers=auth)
        if isinstance(rows, list):
            email = next((r["email"] for r in rows if r.get("primary") and r.get("verified")), "")
    except OAuthError:
        log.warning("GitHub pochtasi olinmadi")
    return Identity("github", str(info.get("id", "")), email, str(info.get("login", "")))


# ── Telegram ──────────────────────────────────────────────────────────


def telegram_identity(payload: dict[str, str]) -> Identity:
    """Widget imzosini tekshiradi.

    Telegram OAuth emas: u ma'lumotni bot tokeni bilan imzolab beradi.
    Imzo bot tokenining SHA-256 xeshi kalit qilingan HMAC — ya'ni tokenni
    bilmasdan soxtalashtirib bo'lmaydi.
    """
    received = payload.get("hash", "")
    check = "\n".join(
        f"{key}={payload[key]}" for key in sorted(payload) if key != "hash" and payload[key]
    )
    secret = hashlib.sha256(settings.TELEGRAM_BOT_TOKEN.encode()).digest()
    expected = hmac.new(secret, check.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, received):
        raise OAuthError("telegram imzosi mos kelmadi")

    try:
        age = time.time() - int(payload.get("auth_date", "0"))
    except ValueError as exc:
        raise OAuthError("telegram auth_date yaroqsiz") from exc
    if age > TELEGRAM_MAX_AGE:
        raise OAuthError("telegram imzosi eskirgan")

    uid = payload.get("id", "")
    suggested = payload.get("username") or f"tg{uid}"
    # Telegram POCHTA BERMAYDI — bu bo'shlik ataylab, foydalanuvchi uni
    # keyin sozlamalarda to'ldiradi.
    return Identity("telegram", uid, "", suggested)


# ── Umumiy ────────────────────────────────────────────────────────────

AUTHORIZE = {"google": _google_authorize, "github": _github_authorize}
IDENTITY = {"google": _google_identity, "github": _github_identity}


def authorize_url(provider: str, state: str) -> str:
    if provider not in AUTHORIZE:
        raise OAuthError(f"noma'lum provayder: {provider}")
    return AUTHORIZE[provider](state)


def identity(provider: str, code: str) -> Identity:
    if provider not in IDENTITY:
        raise OAuthError(f"noma'lum provayder: {provider}")
    return IDENTITY[provider](code)


def new_state() -> str:
    return secrets.token_urlsafe(24)


def free_username(suggested: str) -> str:
    """Bo'sh taxallus tanlaydi.

    Provayder bergan nom qoidaga mos kelmasligi mumkin (bo'sh joy, `-`,
    juda uzun), band bo'lishi yoki mavjud nomga o'xshab qolishi mumkin —
    uchalasi ham raqam qo'shish bilan hal qilinadi.
    """
    base = "".join(ch for ch in suggested if handles.ALLOWED.match(ch or " ")) or "user"
    base = base[: handles.MAX_LENGTH - 4].strip("._") or "user"
    if len(base) < handles.MIN_LENGTH:
        base = f"{base}user"[: handles.MAX_LENGTH]

    for suffix in ("", *(str(n) for n in range(2, 1000))):
        candidate = f"{base}{suffix}"
        taken = User.objects.filter(username__iexact=candidate).exists() or (
            User.objects.filter(username_skeleton=handles.skeleton(candidate)).exists()
        )
        if not taken:
            return candidate
    return f"user{secrets.token_hex(4)}"
