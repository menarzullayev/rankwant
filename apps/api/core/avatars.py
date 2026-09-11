"""Avatar — yuklash, ulangan hisobdan olish va berish.

Rasm MinIO'da (`problems.storage` bilan bir xil ombor) saqlanadi va API
orqali beriladi: `/api/v1/avatars/<nom>`. Nom tasodifiy va o'zgarmas —
yangi rasm yangi nom oladi, ya'ni javobni abadiy keshlash mumkin.

Tashqi manzilni `avatar_url` ga to'g'ridan-to'g'ri yozish ATAYIN yo'q:
ixtiyoriy tashqi rasm har bir profil ko'rilishini uchinchi tomonga
bildirardi. Provayder rasmi ham shu sababli yuklab olinib, qayta
joylashtiriladi.
"""

from __future__ import annotations

import logging
import re
import secrets
from typing import Any
from urllib.parse import urljoin, urlsplit

import requests
from django.conf import settings

log = logging.getLogger(__name__)

#: Brauzer rasmni 256 pikselga kichraytirib yuboradi; provayder rasmi ham
#: shu o'lchamda so'raladi. Bir megabayt — katta zaxira.
MAX_BYTES = 1024 * 1024
PREFIX = "avatars/"
NAME_RE = re.compile(r"^[A-Za-z0-9_-]{16,64}\.(png|jpg|webp)$")
CONTENT_TYPES = {"png": "image/png", "jpg": "image/jpeg", "webp": "image/webp"}
USER_AGENT = "RankWant/1.0 (+https://rankwant.bugvector.uz)"

#: Provayder rasmini FAQAT shu domenlardan olamiz (SSRF: ichki tarmoqqa
#: so'rov yuborib bo'lmasin). Yo'naltirish ham har qadamda tekshiriladi.
ALLOWED_HOSTS = ("googleusercontent.com", "githubusercontent.com", "t.me", "telesco.pe")


class AvatarError(ValueError):
    """Foydalanuvchiga ko'rsatiladigan sabab bilan."""


def sniff(data: bytes) -> str | None:
    """Fayl turi — kengaytmaga emas, ichidagi imzoga qarab."""
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if data.startswith(b"\xff\xd8\xff"):
        return "jpg"
    if len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "webp"
    return None


def _client() -> Any:
    from problems.storage import client

    return client()


def put(data: bytes) -> str:
    if len(data) > MAX_BYTES:
        raise AvatarError("Rasm 1 MB dan oshmasligi kerak")
    ext = sniff(data)
    if ext is None:
        raise AvatarError("Faqat PNG, JPEG yoki WebP rasm")
    name = f"{secrets.token_urlsafe(18)}.{ext}"
    _client().put_object(
        Bucket=settings.S3_BUCKET, Key=PREFIX + name, Body=data, ContentType=CONTENT_TYPES[ext]
    )
    return name


def get(name: str) -> tuple[bytes, str] | None:
    if not NAME_RE.match(name):
        return None
    try:
        body = _client().get_object(Bucket=settings.S3_BUCKET, Key=PREFIX + name)["Body"]
        data: bytes = body.read(MAX_BYTES + 1)
    except Exception:
        return None
    return data, CONTENT_TYPES[name.rsplit(".", 1)[1]]


def delete(name: str) -> None:
    """Eski rasm — yo'qolsa ham hech narsa buzilmaydi."""
    try:
        _client().delete_object(Bucket=settings.S3_BUCKET, Key=PREFIX + name)
    except Exception:
        log.warning("avatar o'chirilmadi: %s", name)


def url_for(name: str) -> str:
    return f"{settings.SITE_URL}/api/v1/avatars/{name}"


def name_from_url(url: str) -> str | None:
    """Bizning omborimizdagi rasm bo'lsa — uning nomi."""
    prefix = f"{settings.SITE_URL}/api/v1/avatars/"
    if not url.startswith(prefix):
        return None
    name = url[len(prefix) :]
    return name if NAME_RE.match(name) else None


def _allowed(url: str) -> bool:
    parts = urlsplit(url)
    host = (parts.hostname or "").lower()
    return parts.scheme == "https" and any(
        host == h or host.endswith(f".{h}") for h in ALLOWED_HOSTS
    )


def fetch_remote(url: str) -> bytes:
    """Provayder rasmini yuklab oladi — faqat ruxsat etilgan domenlardan."""
    for _ in range(4):
        if not _allowed(url):
            raise AvatarError("Bu manzildan rasm olinmaydi")
        try:
            resp = requests.get(
                url,
                timeout=10,
                stream=True,
                allow_redirects=False,
                headers={"User-Agent": USER_AGENT},
            )
        except requests.RequestException as exc:
            raise AvatarError("Provayder javob bermadi") from exc
        with resp:
            if resp.status_code in (301, 302, 303, 307, 308):
                url = urljoin(url, resp.headers.get("Location", ""))
                continue
            if resp.status_code != 200:
                raise AvatarError(f"Provayder rasmni bermadi (HTTP {resp.status_code})")
            data: bytes = resp.raw.read(MAX_BYTES + 1, decode_content=True)
        if len(data) > MAX_BYTES:
            raise AvatarError("Rasm 1 MB dan oshmasligi kerak")
        return data
    raise AvatarError("Juda ko'p yo'naltirish")


def provider_picture(account: Any) -> str:
    """Ulangan hisobning rasmi — 256 pikselda so'raladi."""
    picture: str = account.picture or ""
    if picture and account.provider == "google":
        # `…=s96-c` — Google o'lchamni manzil oxirida oladi.
        picture = re.sub(r"=s\d+(-c)?$", "=s256-c", picture)
    if not picture and account.provider == "github" and str(account.uid).isdigit():
        # GitHub rasmi identifikatordan hosil qilinadi — bog'lanish rasm
        # saqlanishidan oldin qilingan bo'lsa ham ishlaydi.
        picture = f"https://avatars.githubusercontent.com/u/{account.uid}?s=256"
    return picture
