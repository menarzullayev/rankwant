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

from rest_framework.permissions import SAFE_METHODS
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

log = logging.getLogger(__name__)


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


class ResilientAnonRateThrottle(CacheOutageTolerant, AnonRateThrottle):
    pass


class ResilientUserRateThrottle(CacheOutageTolerant, UserRateThrottle):
    pass
