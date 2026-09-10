"""Email yuborish zanjiri — birinchi ishlagani g'olib.

Tartib `EMAIL_CHAIN` da: brevo → mailjet → resend → mailersend. Kaliti
sozlanmagan provayder jimgina tushib qoladi, ya'ni zanjir bitta kalit
bilan ham ishlayveradi va yangi kalit qo'shish faqat `.env` o'zgarishi.

Nega zanjir kerakligi — `core.mail_providers` boshidagi izohda.
"""

from __future__ import annotations

import logging

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from core.mail_providers import PROVIDERS, Message, SendError
from core.models import EmailDelivery

log = logging.getLogger(__name__)


def send_email(
    *,
    to: str,
    subject: str,
    text: str,
    html: str = "",
    purpose: str = EmailDelivery.Purpose.OTHER,
    chain: list[str] | None = None,
) -> EmailDelivery:
    """Zanjir bo'ylab yuboradi va urinishlarni yozib qoladi.

    Hech qachon xato ko'tarmaydi — chaqiruvchi amal (ro'yxatdan o'tish,
    parol tiklash) email yiqilgani uchun yiqilmasligi kerak. Natijani
    qaytarilgan yozuvning `status` idan bilish mumkin.

    `chain` — faqat `send_test_email` uchun: bitta provayderni alohida
    sinash. Odatdagi chaqiruvlar `EMAIL_CHAIN` ni ishlatadi.
    """
    delivery = EmailDelivery(
        to_email=to[:254],
        purpose=purpose,
        subject=subject[:200],
        status=EmailDelivery.Status.FAILED,
    )
    try:
        validate_email(to)
    except ValidationError:
        # Yagona holat: zanjirga umuman kirmaymiz. Qolgan xatolarda esa
        # keyingi provayderga o'tamiz — qarang `SendError`.
        delivery.attempts = [{"provider": "", "error": "manzil yaroqsiz"}]
        delivery.save()
        return delivery

    message = Message(to=to, subject=subject, text=text, html=html)
    attempts: list[dict[str, str]] = []
    for name in chain if chain is not None else settings.EMAIL_CHAIN:
        provider = PROVIDERS.get(name)
        if provider is None:
            log.warning("EMAIL_CHAIN da noma'lum provayder: %s", name)
            continue
        if not provider.configured:
            continue
        try:
            provider.send(message)
        except SendError as exc:
            attempts.append({"provider": name, "error": exc.detail[:500]})
            log.warning("email yuborilmadi (%s → %s): %s", name, to, exc.detail)
            continue
        delivery.provider = name
        delivery.status = EmailDelivery.Status.SENT
        break

    delivery.attempts = attempts
    delivery.save()
    if delivery.status == EmailDelivery.Status.FAILED:
        log.error("email zanjiri tugadi, yuborilmadi: %s (%s)", to, purpose)
    return delivery
