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
from django.http.response import HttpResponseBase

from core.middleware import EDGE_CACHE_FLAG

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


def edge_cacheable[R: HttpResponseBase](response: R, seconds: int) -> R:
    """Javobni CDN keshlay oladigan qilib belgilaydi.

    Faqat HAMMAGA BIR XIL, shaxsiy ma'lumotsiz javoblar uchun.

    `Vary` dan `Cookie` olib tashlanadi: DRF `request.user` ga tekkani
    uchun uni har javobga qo'shadi, CDN esa Cookie bo'yicha vary
    qilingan javobni amalda hech qachon keshlamaydi — har sessiyaning
    o'z cookie'si bor.

    O'lchandi: 500 qatorli jadval 59 KB. 110 000 tomoshabin uni
    to'g'ridan-to'g'ri olsa 3.5 Gbit/s chiqish kerak; 10 soniyalik
    kesh bilan origin'ga 10 soniyada BITTA so'rov tushadi.
    """
    response["Cache-Control"] = f"public, max-age={seconds}, s-maxage={seconds}"
    # `Vary` ni middleware tuzatadi: Django uni view'dan keyin qo'shadi.
    setattr(response, EDGE_CACHE_FLAG, True)
    return response
