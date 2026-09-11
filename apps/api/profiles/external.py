"""Tashqi platformadagi profil — handle tekshiruvi va reytingni olish.

Reyting ochiq API'dan olinadi va `ExternalProfile` da keshlanadi: profil
har ochilganda Codeforces'ga borilmaydi. Yiqilish jim — reyting shunchaki
bo'sh qoladi.
"""

from __future__ import annotations

import http.client
import json
import logging
import re
import urllib.error
import urllib.request
from collections.abc import Callable
from typing import Any
from urllib.parse import quote, urlencode

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.utils import timezone

from profiles.models import ExternalProfile

log = logging.getLogger(__name__)

USER_AGENT = "RankWant/1.0 (+https://rankwant.bugvector.uz)"
TIMEOUT = 10

HANDLE_RE: dict[str, re.Pattern[str]] = {
    ExternalProfile.Kind.CODEFORCES: re.compile(r"^[A-Za-z0-9_.-]{3,24}$"),
    ExternalProfile.Kind.ATCODER: re.compile(r"^[A-Za-z0-9_]{3,16}$"),
    ExternalProfile.Kind.LEETCODE: re.compile(r"^[A-Za-z0-9_-]{1,40}$"),
    ExternalProfile.Kind.TELEGRAM: re.compile(r"^[A-Za-z][A-Za-z0-9_]{4,31}$"),
    ExternalProfile.Kind.GITHUB: re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9]|-(?=[A-Za-z0-9])){0,38}$"),
    ExternalProfile.Kind.INSTAGRAM: re.compile(r"^[A-Za-z0-9._]{1,30}$"),
    ExternalProfile.Kind.X: re.compile(r"^[A-Za-z0-9_]{1,15}$"),
    ExternalProfile.Kind.YOUTUBE: re.compile(r"^[A-Za-z0-9._-]{3,30}$"),
    ExternalProfile.Kind.KAGGLE: re.compile(r"^[A-Za-z0-9_-]{3,40}$"),
}
LINKEDIN_RE = re.compile(r"^https://([a-z]{2,3}\.)?linkedin\.com/in/[A-Za-z0-9_%-]{2,100}/?$")

#: AtCoder'ning rasmiy rang chegaralari.
ATCODER_COLORS = (
    (400, "gray"),
    (800, "brown"),
    (1200, "green"),
    (1600, "cyan"),
    (2000, "blue"),
    (2400, "yellow"),
    (2800, "orange"),
)


def normalize(kind: str, handle: str) -> str:
    """Handle'ni tekshiradi. Profil havolasi yuborilsa ham handle ajratiladi."""
    value = handle.strip()
    if kind == ExternalProfile.Kind.LINKEDIN:
        if not LINKEDIN_RE.match(value):
            raise ValueError("LinkedIn manzili https://linkedin.com/in/… ko'rinishida bo'lsin")
        return value.rstrip("/")
    if kind == ExternalProfile.Kind.BLOG:
        try:
            URLValidator(schemes=["https"])(value)
        except ValidationError:
            raise ValueError("Blog manzili https:// bilan boshlansin") from None
        return value
    # Havola (`https://t.me/nom?x=1`) yoki `@nom` yuborilsa ham taxallus ajratiladi.
    value = value.split("?", 1)[0].rstrip("/").rsplit("/", 1)[-1].lstrip("@")
    pattern = HANDLE_RE.get(kind)
    if pattern is None or not pattern.match(value):
        raise ValueError("Handle noto'g'ri")
    return value


def _json(
    url: str, *, payload: dict[str, Any] | None = None, headers: dict[str, str] | None = None
) -> Any:
    """GET (`payload` bo'lsa POST) va JSON javob.

    4xx — `None`: handle topilmadi (Codeforces noma'lum handle uchun 400,
    AtCoder 404 qaytaradi). Tarmoq xatosi esa chaqiruvchiga ko'tariladi.
    """
    body = json.dumps(payload).encode() if payload is not None else None
    request = urllib.request.Request(
        url,
        data=body,
        headers={
            "User-Agent": USER_AGENT,
            **({"Content-Type": "application/json"} if body is not None else {}),
            **(headers or {}),
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        if 400 <= exc.code < 500:
            return None
        raise


def _atcoder_color(rating: int) -> str:
    for upper, name in ATCODER_COLORS:
        if rating < upper:
            return name
    return "red"


def _codeforces(handle: str) -> dict[str, Any] | None:
    body = _json(f"https://codeforces.com/api/user.info?{urlencode({'handles': handle})}")
    if not body or body.get("status") != "OK":
        return None
    row = body["result"][0]
    return {
        "rating": row.get("rating"),
        "max_rating": row.get("maxRating"),
        "rank": row.get("rank", ""),
    }


def _atcoder(handle: str) -> dict[str, Any] | None:
    history = _json(f"https://atcoder.jp/users/{quote(handle)}/history/json")
    if history is None:
        return None
    rated = [row for row in history if row.get("IsRated")]
    if not rated:
        return {"rating": None, "max_rating": None, "rank": ""}
    rating = int(rated[-1]["NewRating"])
    return {
        "rating": rating,
        "max_rating": max(int(row["NewRating"]) for row in rated),
        "rank": _atcoder_color(rating),
    }


def _leetcode(handle: str) -> dict[str, Any] | None:
    body = _json(
        "https://leetcode.com/graphql",
        payload={
            "query": "query($u: String!) { userContestRanking(username: $u) { rating } }",
            "variables": {"u": handle},
        },
        headers={"Referer": "https://leetcode.com"},
    )
    if body is None:
        return None
    ranking = (body.get("data") or {}).get("userContestRanking")
    rating = round(ranking["rating"]) if ranking and ranking.get("rating") is not None else None
    return {"rating": rating, "max_rating": None, "rank": ""}


FETCHERS: dict[str, Callable[[str], dict[str, Any] | None]] = {
    ExternalProfile.Kind.CODEFORCES: _codeforces,
    ExternalProfile.Kind.ATCODER: _atcoder,
    ExternalProfile.Kind.LEETCODE: _leetcode,
}


def refresh(profile: ExternalProfile) -> bool:
    fetch = FETCHERS.get(profile.kind)
    if fetch is None:
        return False
    try:
        result = fetch(profile.handle)
    except (OSError, http.client.HTTPException, ValueError, KeyError, TypeError, IndexError):
        log.warning("tashqi reyting olinmadi: %s/%s", profile.kind, profile.handle)
        return False
    if result is None:
        return False
    profile.rating = result["rating"]
    profile.max_rating = result["max_rating"]
    profile.rank = str(result["rank"] or "")[:40]
    profile.fetched_at = timezone.now()
    profile.save(update_fields=["rating", "max_rating", "rank", "fetched_at"])
    return True


def _github_login(uid: str) -> str:
    """GitHub taxallusi identifikatordan — ochiq API, kalitsiz."""
    try:
        data = _json(f"https://api.github.com/user/{uid}")
    except (OSError, http.client.HTTPException, ValueError):
        log.warning("GitHub taxallusi olinmadi: %s", uid)
        return ""
    return str(data.get("login", "")) if isinstance(data, dict) else ""


def connected_handles(user: Any) -> dict[str, str]:
    """Ulangan Telegram va GitHub hisobidagi taxallus — profil havolasini
    bir bosishda to'ldirish uchun. Taxallus saqlanishidan oldin bog'langan
    GitHub hisobi uchun u identifikatordan bir marta olinib saqlanadi."""
    from core.models import SocialAccount

    out: dict[str, str] = {}
    for account in SocialAccount.objects.filter(user=user, provider__in=("telegram", "github")):
        handle = account.username
        if not handle and account.provider == "github" and account.uid.isdigit():
            handle = _github_login(account.uid)
            if handle:
                account.username = handle
                account.save(update_fields=["username"])
        if handle:
            out[account.provider] = handle
    return out
