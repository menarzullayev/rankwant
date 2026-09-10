from __future__ import annotations

import logging

from celery import shared_task

from core.mailer import send_email as _send_email
from core.models import EmailDelivery

log = logging.getLogger(__name__)


@shared_task(name="core.send_email")
def send_email(
    to: str,
    subject: str,
    text: str,
    html: str = "",
    purpose: str = EmailDelivery.Purpose.OTHER,
) -> str:
    """Zanjirni fon rejimida yuritadi.

    So'rov ichida chaqirilmasligi kerak: zanjir ketma-ket ishlaydi va
    hamma provayder javob bermasa `EMAIL_TIMEOUT × 4` kutiladi — parol
    tiklash formasi shuncha muddat osilib turishi mumkin emas.
    """
    return _send_email(to=to, subject=subject, text=text, html=html, purpose=purpose).status


@shared_task(name="core.send_password_reset")
def send_password_reset(user_id: int, token: str, code: str, ip: str = "", ua: str = "") -> str:
    """Tiklash xatini renderlab zanjirga topshiradi.

    Xat SO'ROV ICHIDA yuborilmaydi: zanjir ketma-ket yuradi va eng yomon
    holatda `EMAIL_TIMEOUT × 4` kutiladi. Foydalanuvchi esa formani bosgach
    darhol javob olishi kerak — u xat kelishini pochtasida kutadi.
    """
    from core import emails
    from core.models import User

    user = User.objects.filter(pk=user_id).first()
    if user is None or not user.email:
        log.warning("tiklash xati yuborilmadi — foydalanuvchi yo'q: %s", user_id)
        return "skipped"
    return emails.send_password_reset(
        user, token=token, code=code, request_ip=ip, request_ua=ua
    ).status
