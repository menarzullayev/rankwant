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
