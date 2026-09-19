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
import urllib.error
import urllib.request
from http.client import HTTPMessage
from typing import IO, Any
from urllib.parse import urljoin, urlsplit

from django.conf import settings

log = logging.getLogger(__name__)

#: Brauzer rasmni 256 pikselga kichraytirib yuboradi; provayder rasmi ham
#: shu o'lchamda so'raladi. Bir megabayt — katta zaxira.
MAX_BYTES = 1024 * 1024
PREFIX = "avatars/"
NAME_RE = re.compile(r"^[A-Za-z0-9_-]{16,64}\.(png|jpg|webp)$")
CONTENT_TYPES = {"png": "image/png", "jpg": "image/jpeg", "webp": "image/webp"}
USER_AGENT = "RankWant/1.0 (+https://rankwant.uz)"

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
        raise AvatarError("The image must not exceed 1 MB")
    ext = sniff(data)
    if ext is None:
        raise AvatarError("Only PNG, JPEG, or WebP images")
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


PATH_PREFIX = "/api/v1/avatars/"


def url_for(name: str) -> str:
    return f"{settings.SITE_URL}{PATH_PREFIX}{name}"


def name_from_url(url: str) -> str | None:
    """Bizning omborimizdagi rasm bo'lsa — uning nomi.

    Domen almashganda bazada eski manzil qoladi (`rehost_avatars` ko'chiradi).
    Shu orada ham rasm bizniki deb taniladi — host ruxsat etilganlardan bo'lsa,
    aks holda avatar almashtirilganda eski fayl omborda qolib ketardi.
    """
    parts = urlsplit(url)
    ours = {urlsplit(settings.SITE_URL).netloc, *settings.ALLOWED_HOSTS} - {"*"}
    if parts.netloc not in ours or not parts.path.startswith(PATH_PREFIX):
        return None
    name = parts.path[len(PATH_PREFIX) :]
    return name if NAME_RE.match(name) else None


def _allowed(url: str) -> bool:
    parts = urlsplit(url)
    host = (parts.hostname or "").lower()
    return parts.scheme == "https" and any(
        host == h or host.endswith(f".{h}") for h in ALLOWED_HOSTS
    )


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """Yo'naltirishni o'zimiz kuzatamiz — har qadamda domen qayta tekshiriladi."""

    def redirect_request(
        self,
        req: urllib.request.Request,
        fp: IO[bytes],
        code: int,
        msg: str,
        headers: HTTPMessage,
        newurl: str,
    ) -> urllib.request.Request | None:
        return None


_OPENER = urllib.request.build_opener(_NoRedirect)
REDIRECTS = (301, 302, 303, 307, 308)


def fetch_remote(url: str) -> bytes:
    """Provayder rasmini yuklab oladi — faqat ruxsat etilgan domenlardan."""
    for _ in range(4):
        if not _allowed(url):
            raise AvatarError("An image cannot be fetched from this address")
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with _OPENER.open(request, timeout=10) as resp:
                data: bytes = resp.read(MAX_BYTES + 1)
        except urllib.error.HTTPError as exc:
            if exc.code in REDIRECTS:
                url = urljoin(url, exc.headers.get("Location", ""))
                continue
            raise AvatarError(f"The provider did not return an image (HTTP {exc.code})") from exc
        except OSError as exc:
            raise AvatarError("The provider did not respond") from exc
        if len(data) > MAX_BYTES:
            raise AvatarError("The image must not exceed 1 MB")
        return data
    raise AvatarError("Too many redirects")


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
