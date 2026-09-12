"""Kesh yiqilganda ham o'qish ishlaydigan throttle.

DRF throttle'lari HAR so'rovda keshga tegadi. Redis uzilganda ular
istisno tashlaydi va butun API 503 bo'lib qoladi — o'lchandi: arxiv,
masala sahifasi, leaderboard, hammasi. Holbuki masala o'qish uchun kesh
umuman shart emas.

Shuning uchun: **o'qish o'tadi, yozish to'xtaydi**. Uzilish oynasida
o'qishga limit qo'yilmaydi (limitsiz o'qish bilan katta zarar yo'q),
yozish esa umuman qabul qilinmaydi — ya'ni suiiste'mol qiladigan narsa
ham qolmaydi.
"""

from __future__ import annotations

import logging
from ipaddress import ip_address
from typing import Any

from django.conf import settings
from rest_framework.permissions import SAFE_METHODS
from rest_framework.throttling import (
    AnonRateThrottle,
    ScopedRateThrottle,
    UserRateThrottle,
)

log = logging.getLogger(__name__)


class TrustedClientIdent:
    """Throttle kalitini ISHONCHLI manbadan oladi.

    DRF standart holatida, `NUM_PROXIES` ko'rsatilmaganda, BUTUN
    `X-Forwarded-For` sarlavhasini kalit qilib oladi — uni esa mijozning
    o'zi yozadi. O'lchandi: bitta manzildan 1600 so'rov yuborilganda 1270
    tasi 429 bo'ldi, keyin sarlavhani har safar o'zgartirib yuborilgan
    10 so'rovning HAMMASI o'tdi. Ya'ni ro'yxatdan o'tish, kirish va
    yechim yuborish cheklovlari bir qator bilan chetlab o'tilardi.

    `TRUSTED_CLIENT_IP_HEADER` — proksi QO'YADIGAN sarlavha nomi
    (Cloudflare uchun `HTTP_CF_CONNECTING_IP`). Proksi uni har so'rovda
    qayta yozadi, ya'ni mijoz soxtalashtira olmaydi. Sozlama bo'sh
    bo'lsa faqat `REMOTE_ADDR` ishlatiladi: xom `X-Forwarded-For` ga
    HECH QACHON ishonilmaydi.
    """

    def get_ident(self, request: Any) -> str:
        header = getattr(settings, "TRUSTED_CLIENT_IP_HEADER", "")
        if header:
            value = request.META.get(header)
            if value:
                # Ba'zi proksi ro'yxat yuboradi — birinchisi mijoz.
                return str(value).split(",")[0].strip()
        return str(request.META.get("REMOTE_ADDR", ""))


class CacheOutageTolerant:
    """Kesh yiqilsa: GET o'tadi, qolgani avvalgidek xato beradi."""

    def allow_request(self, request: Any, view: Any) -> bool:
        try:
            return bool(super().allow_request(request, view))  # type: ignore[misc]
        except Exception:
            log.warning("throttle keshi yiqildi: %s %s", request.method, request.path)
            if request.method in SAFE_METHODS:
                return True
            # Yozish uchun eski xatti-harakat saqlanadi (503).
            raise


class InternalRenderRate:
    """SSR chaqiruvlarini alohida, kengroq chegarada hisoblaydi.

    Next.js sahifani SERVERDA renderlab API'ga xususiy tarmoq manzilidan,
    proksi sarlavhasisiz murojaat qiladi — ya'ni butun saytning server
    tomoni bitta kalitga tushadi. O'lchandi (2026-09-12): krauler
    `/users/*` sahifalarini aylanib chiqqanda `anon` chegara tugadi va
    sahifalar 429 ni ushlamay 500 ga aylantirdi, ya'ni sayt hamma uchun
    ochilmay qoldi.

    `TRUSTED_CLIENT_IP_HEADER` sozlanmagan joyda hech narsa ichki deb
    hisoblanmaydi: aks holda proksi sarlavhasi yo'qolib qolganda himoya
    jimgina kengayib ketardi.

    `scope_internal` `None` bo'lsa ichki so'rov bu throttle'dan o'tib
    ketadi — anonim SSR so'rovi `user` chegarasida ham IP bo'yicha
    kalit olardi (DRF autentifikatsiyasiz `UserRateThrottle` ni IP ga
    tushiradi), ya'ni yana bitta umumiy idish paydo bo'lardi.
    """

    scope: str | None
    scope_internal: str | None = None

    def allow_request(self, request: Any, view: Any) -> bool:
        if self._is_internal(request):
            if self.scope_internal is None:
                return True
            self.scope = self.scope_internal
            self.rate = self.get_rate()  # type: ignore[attr-defined]
            self.num_requests, self.duration = self.parse_rate(self.rate)  # type: ignore[attr-defined]
        return bool(super().allow_request(request, view))  # type: ignore[misc]

    @staticmethod
    def _is_internal(request: Any) -> bool:
        header = getattr(settings, "TRUSTED_CLIENT_IP_HEADER", "")
        if not header or request.META.get(header):
            return False
        try:
            return ip_address(str(request.META.get("REMOTE_ADDR", ""))).is_private
        except ValueError:
            return False


class ResilientAnonRateThrottle(
    TrustedClientIdent, InternalRenderRate, CacheOutageTolerant, AnonRateThrottle
):
    scope_internal = "anon_internal"


class ResilientUserRateThrottle(
    TrustedClientIdent, InternalRenderRate, CacheOutageTolerant, UserRateThrottle
):
    # Ichki anonim so'rov `anon_internal` da hisoblangan — bu yerda yana
    # sanalmaydi. Kirgan foydalanuvchi esa o'z pk'si bo'yicha sanaladi.
    scope_internal = None


class ResilientScopedRateThrottle(TrustedClientIdent, CacheOutageTolerant, ScopedRateThrottle):
    """`submit` kabi nomlangan cheklovlar uchun — ular ham xuddi shu
    sarlavha bilan chetlab o'tilardi."""
