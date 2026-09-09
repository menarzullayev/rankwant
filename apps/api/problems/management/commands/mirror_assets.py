"""Tashqi hostdagi rasm va fayllarni o'z saqlashimizga ko'chiradi.

Ishlatish:  python manage.py mirror_assets [--dry-run] [--limit N]

ADR-0005: «o'z kontenti, uchinchi tomondan to'liq mustaqillik». Import
qilingan masalalarning rasmlari va ilova fayllari esa boshqa hostlarda
qolgan edi — o'lchandi: 23 ta fayl va matndagi 44 ta rasm beshta tashqi
hostda, ular orasida stock-foto sayti ham bor. Ikki muammo: o'sha host
o'chsa masala rasmsiz qoladi, va har tashrifchining IP'si o'sha hostga
ko'rinadi.

Kalit MAZMUNDAN olinadi (SHA-256), ya'ni bir xil fayl ikki marta
saqlanmaydi va manzil hech qachon boshqa faylni bermaydi.
"""

from __future__ import annotations

import hashlib
import ipaddress
import mimetypes
import re
import socket
import urllib.request
from argparse import ArgumentParser
from typing import Any
from urllib.parse import urlparse

from django.core.management.base import BaseCommand

from problems.models import Problem, ProblemAttachment
from problems.storage import MAX_MEDIA_BYTES, MEDIA_PREFIX, media_exists, put_media

#: Matndagi markdown rasmlari
IMAGE_RE = re.compile(r"(!\[[^\]]*\]\()(https?://[^)\s]+)(\))")
#: Bizning yo'l — takroriy ko'chirishning oldini oladi
LOCAL_PREFIX = "/api/v1/media/"
USER_AGENT = "RankWant-Importer/1.0 (+https://rankwant.uz)"
TIMEOUT = 20


def _check_public(url: str) -> None:
    """Manzil OMMAVIY internetga qaraydimi.

    Havolalar tashqi arxivdan keladi, ya'ni ular bizning ichki tarmog'imizga
    ham qarab turishi mumkin: `http://169.254.169.254/…` (bulut metadata),
    `http://minio:9000/…` yoki `http://127.0.0.1/…`. Bu buyruq ularni olib
    kelib, OMMAVIY manzilda e'lon qilib qo'yardi.
    """
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"sxema ruxsat etilmagan: {parsed.scheme}")
    host = parsed.hostname
    if not host:
        raise ValueError("host yo'q")
    try:
        infos = socket.getaddrinfo(host, parsed.port or (443 if parsed.scheme == "https" else 80))
    except OSError as exc:
        raise ValueError(f"nom yechilmadi: {exc}") from exc
    for info in infos:
        address = ipaddress.ip_address(info[4][0])
        if not address.is_global:
            raise ValueError(f"ichki manzil: {address}")


class _CheckedRedirects(urllib.request.HTTPRedirectHandler):
    """Har yo'naltirishni QAYTA tekshiradi.

    Boshlang'ich manzilni tekshirish yetarli emas: tashqi host 302 bilan
    `http://127.0.0.1/…` ga yuborishi mumkin edi.
    """

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[no-untyped-def]
        _check_public(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


_opener = urllib.request.build_opener(_CheckedRedirects)


def _fetch(url: str) -> tuple[bytes, str]:
    _check_public(url)
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with _opener.open(request, timeout=TIMEOUT) as response:
        body = response.read(MAX_MEDIA_BYTES + 1)
        if len(body) > MAX_MEDIA_BYTES:
            raise ValueError(f"fayl {MAX_MEDIA_BYTES // 1024 // 1024} MB dan katta")
        return body, response.headers.get("Content-Type", "")


def _key_for(url: str, body: bytes, content_type: str) -> str:
    digest = hashlib.sha256(body).hexdigest()[:32]
    suffix = ""
    name = urlparse(url).path.rsplit("/", 1)[-1]
    if "." in name:
        suffix = "." + name.rsplit(".", 1)[-1].lower()[:8]
    elif content_type:
        suffix = mimetypes.guess_extension(content_type.split(";")[0].strip()) or ""
    return f"{digest}{suffix}"


class Command(BaseCommand):
    help = "Tashqi rasm va ilova fayllarni o'z saqlashimizga ko'chiradi."

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--limit", type=int, default=0, help="Faqat N ta havola")

    def handle(self, *args: Any, **options: Any) -> None:
        self.dry = bool(options["dry_run"])
        self.limit = int(options["limit"])
        self.done = 0
        self.failed = 0

        self._attachments()
        self._problem_images()
        self._statements()

        holat = "(dry-run) " if self.dry else ""
        self.stdout.write(
            self.style.SUCCESS(f"{holat}{self.done} havola ko'chirildi, {self.failed} yiqildi")
        )

    # ── umumiy ──
    def _mirror(self, url: str) -> str | None:
        """Qaytaradi: yangi mahalliy manzil, yoki None (yiqildi/o'tkazildi)."""
        if url.startswith(LOCAL_PREFIX) or not url.startswith(("http://", "https://")):
            return None
        if self.limit and self.done >= self.limit:
            return None
        try:
            body, content_type = _fetch(url)
        except Exception as exc:
            self.stderr.write(f"  yiqildi {url}: {exc}")
            self.failed += 1
            return None

        key = _key_for(url, body, content_type)
        if not self.dry and not media_exists(MEDIA_PREFIX + key):
            put_media(MEDIA_PREFIX + key, body, content_type)
        self.done += 1
        self.stdout.write(f"  {urlparse(url).netloc}/…/{key}  {len(body) // 1024} KB")
        return LOCAL_PREFIX + key

    def _attachments(self) -> None:
        rows = ProblemAttachment.objects.exclude(url__startswith=LOCAL_PREFIX)
        self.stdout.write(f"Ilova fayllar: {rows.count()}")
        for row in rows:
            local = self._mirror(row.url)
            if local and not self.dry:
                ProblemAttachment.objects.filter(pk=row.pk).update(url=local)

    def _problem_images(self) -> None:
        rows = Problem.objects.exclude(image="").exclude(image__startswith=LOCAL_PREFIX)
        self.stdout.write(f"Masala rasmlari: {rows.count()}")
        for row in rows:
            local = self._mirror(row.image)
            if local and not self.dry:
                Problem.objects.filter(pk=row.pk).update(image=local)

    def _statements(self) -> None:
        rows = Problem.objects.filter(statement__contains="](http")
        self.stdout.write(f"Matnida tashqi havolasi bor masalalar: {rows.count()}")
        for row in rows:
            changed = False

            def swap(match: re.Match[str]) -> str:
                nonlocal changed
                local = self._mirror(match.group(2))
                if local is None:
                    return match.group(0)
                changed = True
                return f"{match.group(1)}{local}{match.group(3)}"

            new = IMAGE_RE.sub(swap, row.statement)
            if changed and not self.dry:
                Problem.objects.filter(pk=row.pk).update(statement=new)
