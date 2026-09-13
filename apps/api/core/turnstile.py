"""Cloudflare Turnstile tekshiruvi — 9-qaror.

Turnstile KO'RINMAS rejimda ishlatiladi: foydalanuvchi odatda hech narsa
ko'rmaydi, Cloudflare shubhali deb hisoblasa o'zi chaqirib tekshiradi.
Ya'ni bu yerdagi kodning vazifasi — token bo'lsa uni tekshirish.

MUHIM: kalitlar sozlanmagan bo'lsa tekshiruv BUTUNLAY o'chadi. Bu
ataylab: `test` va lokal muhit tarmoqqa chiqmasligi kerak, ya'ni har
birlik testida Cloudflare'ga so'rov ketishi mumkin emas.
"""

from __future__ import annotations

import json
import urllib.parse
import urllib.request

from django.conf import settings

TIMEOUT = 5


class TurnstileError(Exception):
    """Token rad etildi yoki tekshirib bo'lmadi."""


def enabled() -> bool:
    """Kalitlar ikkalasi ham bo'lsa ishlaydi — bittasi bo'lsa ham o'chiq.

    Chala sozlama (faqat sayt kaliti) `enabled()` ni `True` qilib, keyin
    har urinishni yiqitardi — buning o'rniga tekshiruvni ochiq
    o'chiramiz va logda ko'rinadigan qoldiramiz.
    """
    return bool(settings.TURNSTILE_SITE_KEY and settings.TURNSTILE_SECRET_KEY)


def verify(token: str, *, remote_ip: str = "") -> None:
    """Tokenni Cloudflare'da tekshiradi. Rad etilsa `TurnstileError`.

    Tarmoq xatosi alohida: `TURNSTILE_FAIL_OPEN` bo'lsa O'TKAZIB
    YUBORILADI. Sabab: Cloudflare javob bermagan bir daqiqada butun
    ro'yxatdan o'tish to'xtab qolmasligi kerak — Turnstile qo'shimcha
    qavat, yagona himoya emas (throttle allaqachon ishlaydi).
    """
    if not enabled():
        return
    if not token:
        raise TurnstileError("Tekshiruv tokeni yo'q")

    payload = {"secret": settings.TURNSTILE_SECRET_KEY, "response": token}
    if remote_ip:
        payload["remoteip"] = remote_ip

    try:
        request = urllib.request.Request(
            settings.TURNSTILE_VERIFY_URL,
            data=urllib.parse.urlencode(payload).encode(),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            data = json.loads(response.read())
    except Exception as exc:  # tarmoq, JSON, HTTP — hammasi bir xil
        if settings.TURNSTILE_FAIL_OPEN:
            return
        raise TurnstileError("Tekshiruv xizmatiga ulanib bo'lmadi") from exc

    if not data.get("success"):
        raise TurnstileError("Tekshiruvdan o'tilmadi")
