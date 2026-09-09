"""Keshga chidamli murojaat.

Kesh — ta'rifi bo'yicha IXTIYORIY qatlam: u yiqilganda sahifa
sekinlashishi mumkin, lekin o'chib qolmasligi kerak. Django ning o'z
`RedisCache` backendida `IGNORE_EXCEPTIONS` yo'q, shuning uchun har
`cache.get` Redis uzilganda istisno tashlaydi va sahifani 500 qiladi.
"""

from __future__ import annotations

import logging
from typing import Any

from django.core.cache import cache

log = logging.getLogger(__name__)


def cache_get(key: str, default: Any = None) -> Any:
    """Kesh yiqilsa — o'qib bo'lmadi, ya'ni «yo'q»."""
    try:
        return cache.get(key, default)
    except Exception:
        log.warning("kesh o'qilmadi: %s", key)
        return default


def cache_set(key: str, value: Any, timeout: int | None = None) -> None:
    """Kesh yiqilsa — jim o'tadi. Yozib bo'lmagani xato emas."""
    try:
        cache.set(key, value, timeout)
    except Exception:
        log.warning("kesh yozilmadi: %s", key)
