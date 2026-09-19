"""Ijtimoiy kirish — Google, GitHub, Telegram (ADR-0016).

Kutubxona qo'shilmadi. `django-allauth` o'z shablonlari, URL'lari va
modellari bilan keladi, bizda esa API headless va frontend alohida —
uchala provayder ham oddiy HTTP almashuvi, xuddi email zanjiridagi kabi.

Telegram **email bermaydi**. Shu sababli faqat Telegram bilan ochilgan
hisobda pochta bo'lmaydi va u parolni tiklashdan foydalana olmaydi —
foydalanuvchi keyin sozlamalarda pochta qo'shishi kerak.

2026-09-13 gacha Telegram iframe vidjeti bilan ishlardi: u bot tokeni
bilan imzolangan ma'lumotni to'g'ridan-to'g'ri yuborardi. Telegram o'sha
vidjetni legacy deb e'lon qilib, o'rniga OIDC (Authorization Code)
taklif qildi. Endi Telegram ham qolgan ikkitasi bilan bir xil naqshda:
havola -> provayder -> kod -> server almashuvi.
"""

from __future__ import annotations

import base64
import binascii
import hashlib
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
from core.http_retry import open_with_retry
from core.models import User

log = logging.getLogger(__name__)

USER_AGENT = "RankWant/1.0 (+https://rankwant.uz)"

#: Har provayder uchun: kalit sozlanganini bildiruvchi sozlama nomlari.
#: Kaliti yo'q provayder ro'yxatga umuman tushmaydi va uning tugmasi
#: frontendda ko'rinmaydi — email zanjiridagi bilan bir xil qoida.
REQUIRED: dict[str, tuple[str, ...]] = {
    "google": ("GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET"),
    "github": ("GITHUB_CLIENT_ID", "GITHUB_CLIENT_SECRET"),
    #: `TELEGRAM_BOT_TOKEN` bu yerda EMAS: u bot bildirishnomalari uchun
    #: qoladi (`notifications/tasks.py`), login esa Client ID/Secret ga
    #: o'tdi. Vidjet davrida aksincha edi — token imzoni tekshirardi.
    "telegram": ("TELEGRAM_CLIENT_ID", "TELEGRAM_CLIENT_SECRET"),
}


class OAuthError(Exception):
    """Almashuv yiqildi. Chaqiruvchi foydalanuvchini xato sahifasiga qaytaradi."""


@dataclass(frozen=True)
class Identity:
    """Provayder qaytargan kimlik. `email` bo'sh bo'lishi mumkin (Telegram)."""

    provider: str
    uid: str
    email: str
    suggested: str
    #: Provayder rasmi — «avatarni ulangan hisobdan olish» uchun saqlanadi.
    picture: str = ""
    #: Provayderdagi taxallus — GitHub `login`, Telegram `username` (bo'lsa).
    handle: str = ""


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
        # Manzil log'ga yozilmaydi: `label` ataylab umumiy — ba'zi
        # provayderlar token'ni query satrida olib yuradi.
        with open_with_retry(req, timeout=15, label="oauth") as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        detail = exc.read()[:300].decode("utf-8", "replace")
        raise OAuthError(f"HTTP {exc.code}: {detail}") from exc
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
        raise OAuthError(str(exc)) from exc


# ── Google ────────────────────────────────────────────────────────────


def _google_authorize(state: str, code_challenge: str = "") -> str:
    # `code_challenge` ishlatilmaydi: Google PKCE ni qo'llaydi, lekin bu
    # yerda so'ralmaydi. Imzo barcha provayderlarda bir xil turishi uchun
    # parametr qoldirilgan — chaqiruvchi shoxlanmasin.
    del code_challenge
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


def _google_identity(code: str, code_verifier: str = "") -> Identity:
    del code_verifier  # PKCE so'ralmagan — `_google_authorize` ga qarang
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
    return Identity(
        "google",
        str(info.get("sub", "")),
        email,
        email.split("@")[0],
        str(info.get("picture", "")),
    )


# ── GitHub ────────────────────────────────────────────────────────────


def _github_authorize(state: str, code_challenge: str = "") -> str:
    del code_challenge  # yuqoridagi izohga qarang (`_google_authorize`)
    query = urllib.parse.urlencode(
        {
            "client_id": settings.GITHUB_CLIENT_ID,
            "redirect_uri": redirect_uri("github"),
            "scope": "read:user user:email",
            "state": state,
        }
    )
    return f"https://github.com/login/oauth/authorize?{query}"


def _github_identity(code: str, code_verifier: str = "") -> Identity:
    del code_verifier  # PKCE so'ralmagan — `_github_authorize` ga qarang
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
    return Identity(
        "github",
        str(info.get("id", "")),
        email,
        str(info.get("login", "")),
        str(info.get("avatar_url", "")),
        handle=str(info.get("login", "")),
    )


# ── Telegram ──────────────────────────────────────────────────────────

TELEGRAM_ISSUER = "https://oauth.telegram.org"
TELEGRAM_AUTHORIZE = f"{TELEGRAM_ISSUER}/auth"
TELEGRAM_TOKEN = f"{TELEGRAM_ISSUER}/token"


def pkce_pair() -> tuple[str, str]:
    """PKCE: (`code_verifier`, S256 `code_challenge`).

    OAuth 2.0 Security BCP (RFC 9700) uni maxfiy klientlarga ham tavsiya
    qiladi — kodni ushlab qolgan odam uni almashib bera olmasin. Hisob
    stdlib bilan bo'ladi, ya'ni bu ham kutubxona talab qilmaydi.
    """
    verifier = secrets.token_urlsafe(64)
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    return verifier, base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")


def _telegram_authorize(state: str, code_challenge: str = "") -> str:
    query = urllib.parse.urlencode(
        {
            "client_id": settings.TELEGRAM_CLIENT_ID,
            "redirect_uri": redirect_uri("telegram"),
            "response_type": "code",
            # `profile` — ism, taxallus va rasm. `phone` so'ralmaydi:
            # kerak emas va rozilik ekranini og'irlashtiradi.
            "scope": "openid profile",
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }
    )
    return f"{TELEGRAM_AUTHORIZE}?{query}"


def _jwt_claims(token: str) -> dict[str, Any]:
    """JWT payload'ini ochadi. Imzo tekshirilmaydi — sababi pastda."""
    parts = token.split(".")
    if len(parts) != 3:
        raise OAuthError("id_token must have three parts")
    body = parts[1]
    try:
        claims = json.loads(base64.urlsafe_b64decode(body + "=" * (-len(body) % 4)))
    except (binascii.Error, ValueError, UnicodeDecodeError) as exc:
        raise OAuthError(f"id_token could not be read: {exc}") from exc
    if not isinstance(claims, dict):
        raise OAuthError("id_token is not an object")
    return claims


def _telegram_identity(code: str, code_verifier: str = "") -> Identity:
    """Kodni token'ga almashtiradi va `id_token` claims'ini tekshiradi.

    IMZO ATAYLAB TEKSHIRILMAYDI. OIDC Core 3.1.3.7 ning 6-qadami buni
    ochiq ruxsat etadi: `id_token` token endpoint'idan to'g'ridan-to'g'ri
    (brauzerdan o'tmasdan) kelganda TLS tekshiruvi imzo tekshiruvi
    O'RNIGA o'tadi. Loyiha Google'da ham shunga yaqin yo'l tutgan —
    `id_token` o'rniga `userinfo` so'raladi, faqat JWT kalit halqasini
    ko'tarmaslik uchun. Telegram'da `userinfo` YO'Q, ya'ni claims shu
    token ichidan o'qiladi va `iss`/`aud`/`exp` baribir tekshiriladi.

    Shu tufayli kripto kutubxonasi kerak emas: `cryptography` ~8 MB
    binary va o'z CVE tarixi bilan kelardi.
    """
    token = _request(
        TELEGRAM_TOKEN,
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri("telegram"),
            "client_id": settings.TELEGRAM_CLIENT_ID,
            "client_secret": settings.TELEGRAM_CLIENT_SECRET,
            "code_verifier": code_verifier,
        },
    )
    claims = _jwt_claims(str(token.get("id_token", "")))

    if claims.get("iss") != TELEGRAM_ISSUER:
        raise OAuthError(f"iss does not match: {claims.get('iss')!r}")
    audience = claims.get("aud")
    audiences = audience if isinstance(audience, list) else [audience]
    if str(settings.TELEGRAM_CLIENT_ID) not in {str(a) for a in audiences}:
        raise OAuthError("aud is not our client_id")
    try:
        expires = int(claims.get("exp", 0))
    except (TypeError, ValueError) as exc:
        raise OAuthError("exp could not be read") from exc
    if expires <= int(time.time()):
        raise OAuthError("id_token has expired")

    uid = str(claims.get("sub", ""))
    if not uid:
        raise OAuthError("id_token has no sub")
    username = str(claims.get("preferred_username", ""))
    # Telegram POCHTA BERMAYDI — bu bo'shlik ataylab, foydalanuvchi uni
    # keyin sozlamalarda to'ldiradi.
    return Identity(
        "telegram",
        uid,
        "",
        username or f"tg{uid}",
        str(claims.get("picture", "")),
        handle=username,
    )


# ── Umumiy ────────────────────────────────────────────────────────────

AUTHORIZE = {
    "google": _google_authorize,
    "github": _github_authorize,
    "telegram": _telegram_authorize,
}
IDENTITY = {
    "google": _google_identity,
    "github": _github_identity,
    "telegram": _telegram_identity,
}


def authorize_url(provider: str, state: str, code_challenge: str = "") -> str:
    """Ruxsat sahifasining manzili.

    `code_challenge` faqat PKCE ishlatadigan provayderga tegadi; qolgani
    uni e'tiborsiz qoldiradi. Imzo bir xil turishi ataylab: aks holda
    chaqiruvchi provayderga qarab shoxlanishi kerak bo'lardi.
    """
    if provider not in AUTHORIZE:
        raise OAuthError(f"unknown provider: {provider}")
    return AUTHORIZE[provider](state, code_challenge)


def identity(provider: str, code: str, code_verifier: str = "") -> Identity:
    if provider not in IDENTITY:
        raise OAuthError(f"unknown provider: {provider}")
    return IDENTITY[provider](code, code_verifier)


def new_state() -> str:
    return secrets.token_urlsafe(24)


def free_username(suggested: str) -> str:
    """Bo'sh taxallus tanlaydi.

    Provayder bergan nom qoidaga mos kelmasligi mumkin (bo'sh joy, `-`,
    juda uzun), band bo'lishi yoki mavjud nomga o'xshab qolishi mumkin —
    uchalasi ham raqam qo'shish bilan hal qilinadi.
    """
    from core.usernames import reserved

    base = "".join(ch for ch in suggested if handles.ALLOWED.match(ch or " ")) or "user"
    base = base[: handles.MAX_LENGTH - 4].strip("._") or "user"
    if len(base) < handles.MIN_LENGTH:
        base = f"{base}user"[: handles.MAX_LENGTH]

    for suffix in ("", *(str(n) for n in range(2, 1000))):
        candidate = f"{base}{suffix}"
        taken = User.objects.filter(username__iexact=candidate).exists() or (
            User.objects.filter(username_skeleton=handles.skeleton(candidate)).exists()
        )
        # Yaqinda boshqa hisobdan bo'shagan nom 90 kun band — avtomatik
        # tanlangan nom ham unga tushmasligi kerak.
        if not taken and not reserved(candidate):
            return candidate
    return f"user{secrets.token_hex(4)}"
