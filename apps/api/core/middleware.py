"""Javob chizig'idagi kichik tuzatishlar."""

from __future__ import annotations

import logging
from collections.abc import Callable

from django.http import HttpRequest
from django.http.response import HttpResponseBase

#: `edge_cacheable()` javobga qo'yadigan belgi
EDGE_CACHE_FLAG = "_rw_edge_cacheable"


class EdgeCacheHeaders:
    """Chekkada keshlanadigan javoblardan `Vary: Cookie` ni olib tashlaydi.

    `SessionMiddleware` va `CsrfViewMiddleware` uni view'dan KEYIN
    qo'shadi, ya'ni view ichida yozib bo'lmaydi. CDN esa Cookie bo'yicha
    vary qilingan javobni amalda hech qachon keshlamaydi — har
    sessiyaning o'z cookie'si bor, ya'ni har tomoshabin origin'ga
    uriladi. Shu bois tuzatish javob chizig'ining ENG TASHQARISIDA.
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponseBase]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponseBase:
        response = self.get_response(request)
        if getattr(response, EDGE_CACHE_FLAG, False):
            response["Vary"] = "Accept"
        return response


class TrackSession:
    """Kirilgan qurilmani `UserSession` ga yozadi (sozlamalar → Sessiyalar).

    `last_seen` har so'rovda yozilmaydi — bu har bir sahifa ochilishini
    bazaga yozishga aylanardi. Besh daqiqada bir marta yetarli: ro'yxatda
    «hozir faol» va «kecha» ni ajratish uchun shu aniqlik kifoya.

    Kuzatuv yiqilsa so'rov yiqilmasligi kerak — xato yutiladi.
    """

    TOUCH_EVERY = 300

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponseBase]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponseBase:
        response = self.get_response(request)
        try:
            self._touch(request)
        except Exception:  # kuzatuv so'rovni yiqitmasligi kerak
            logging.getLogger(__name__).warning("sessiya kuzatuvi yiqildi", exc_info=True)
        return response

    def _touch(self, request: HttpRequest) -> None:
        from core.sessions import record

        record(request)
