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


class ResilientAnonRateThrottle(TrustedClientIdent, CacheOutageTolerant, AnonRateThrottle):
    pass


class ResilientUserRateThrottle(TrustedClientIdent, CacheOutageTolerant, UserRateThrottle):
    pass


class ResilientScopedRateThrottle(TrustedClientIdent, CacheOutageTolerant, ScopedRateThrottle):
    """`submit` kabi nomlangan cheklovlar uchun — ular ham xuddi shu
    sarlavha bilan chetlab o'tilardi."""
