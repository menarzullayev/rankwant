"""Hisob xatlarini yig'adi va zanjirga topshiradi (ADR-0015).

Bitta shablon ikkala xatga xizmat qiladi — ular tuzilishi jihatidan bir xil
(sarlavha, matn, tugma, kod, kontekst, footer) va faqat satrlari boshqacha.
Ikkinchi shablon nusxa bo'lardi va biri ikkinchisidan orqada qolardi.
"""

from __future__ import annotations

from urllib.parse import urlsplit

from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone

from core import email_text
from core.mailer import send_email
from core.models import EmailDelivery, User


def _context(
    table: dict[str, dict[str, str]],
    user: User,
    *,
    path: str,
    token: str,
    code: str,
    request_ip: str = "",
    request_ua: str = "",
) -> dict[str, object]:
    locale = user.locale or email_text.DEFAULT_LOCALE
    strings = {**email_text.strings(email_text.SHARED, locale), **email_text.strings(table, locale)}
    return {
        "t": strings,
        "locale": locale,
        "code": code,
        # Havola BIZNING domenimizda qoladi: kuzatuv o'chirilgan (ADR-0015),
        # ya'ni foydalanuvchi manzilni ko'rib ishonch hosil qila oladi.
        "link": f"{settings.SITE_URL}{path}?token={token}",
        "site_url": settings.SITE_URL,
        "site_host": urlsplit(settings.SITE_URL).netloc,
        "request_at": timezone.localtime().strftime("%d.%m.%Y %H:%M (UTC+5)"),
        "request_ip": request_ip,
        "request_ua": request_ua[:80],
    }


def _send(context: dict[str, object], purpose: str, to: str) -> EmailDelivery:
    strings = context["t"]
    assert isinstance(strings, dict)
    return send_email(
        to=to,
        subject=strings["subject"],
        text=render_to_string("email/base.txt", context),
        html=render_to_string("email/base.html", context),
        purpose=purpose,
    )


def send_password_reset(
    user: User, *, token: str, code: str, request_ip: str = "", request_ua: str = ""
) -> EmailDelivery:
    context = _context(
        email_text.RESET,
        user,
        path="/parolni-tiklash",
        token=token,
        code=code,
        request_ip=request_ip,
        request_ua=request_ua,
    )
    return _send(context, EmailDelivery.Purpose.PASSWORD_RESET, user.email)


def send_email_verify(user: User, *, token: str, code: str) -> EmailDelivery:
    # Tasdiqlashda kontekst ko'rsatilmaydi: foydalanuvchi bu so'rovni o'zi,
    # shu daqiqada yubordi — «bu men emasman» degan savol tug'ilmaydi.
    context = _context(email_text.VERIFY, user, path="/emailni-tasdiqlash", token=token, code=code)
    return _send(context, EmailDelivery.Purpose.EMAIL_VERIFY, user.email)
