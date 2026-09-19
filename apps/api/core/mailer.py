"""Email yuborish zanjiri — birinchi ishlagani g'olib.

Tartib `EMAIL_CHAIN` da: brevo → mailjet → resend → mailersend. Kaliti
sozlanmagan provayder jimgina tushib qoladi, ya'ni zanjir bitta kalit
bilan ham ishlayveradi va yangi kalit qo'shish faqat `.env` o'zgarishi.

Nega zanjir kerakligi — `core.mail_providers` boshidagi izohda.
"""

from __future__ import annotations

import logging
import re

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from core.mail_providers import PROVIDERS, Message, SendError
from core.models import EmailDelivery

log = logging.getLogger(__name__)

#: RFC 2606 / RFC 6761 zaxira nomlari — bu domenga pochta HECH QACHON
#: yetib bormaydi, ya'ni ularga yuborish faqat kvota yoqadi.
#:
#: ⚠️ Xuddi shu ro'yxat `tools/push_guard.py` da ham bor (`_PLACEHOLDER_DOMAIN`)
#: — u yerda commit muallifining manzili tekshiriladi. `tools/` ni API
#: import qila olmaydi, shuning uchun ro'yxat ikki joyda; RFC o'zgarmaydi,
#: lekin bittasini tahrirlaganda ikkinchisini ham ko'zdan kechiring.
_PLACEHOLDER_DOMAIN = re.compile(
    r"(^|\.)(example\.(com|net|org)|example|invalid|localhost|localdomain|test)$",
    re.IGNORECASE,
)


def is_placeholder(email: str) -> bool:
    """Manzil zaxira domendami — ya'ni unga yuborish ma'nosizmi.

    Bo'sh yoki `@` siz qiymat ham `True`: bunday manzil allaqachon
    `validate_email` da tushadi, lekin bu yerda ham xavfsiz tomonga
    og'ish yaxshiroq — kvota bekorga yonmasin.
    """
    local, at, domain = email.strip().rpartition("@")
    if not at or not local or not domain:
        return True
    return bool(_PLACEHOLDER_DOMAIN.search(domain))


def send_email(
    *,
    to: str,
    subject: str,
    text: str,
    html: str = "",
    purpose: str = EmailDelivery.Purpose.OTHER,
    chain: list[str] | None = None,
    allow_placeholder: bool = False,
) -> EmailDelivery:
    """Zanjir bo'ylab yuboradi va urinishlarni yozib qoladi.

    Hech qachon xato ko'tarmaydi — chaqiruvchi amal (ro'yxatdan o'tish,
    parol tiklash) email yiqilgani uchun yiqilmasligi kerak. Natijani
    qaytarilgan yozuvning `status` idan bilish mumkin.

    `chain` — faqat `send_test_email` uchun: bitta provayderni alohida
    sinash. Odatdagi chaqiruvlar `EMAIL_CHAIN` ni ishlatadi.

    `allow_placeholder` — zaxira domenlarga (`@example.com`, `@test` …)
    yuborishga ruxsat. Ataylab ODDIY holatda `False`: bunday manzilga
    yuborilgan xat hech kimga yetib bormaydi, kvotani esa yoqadi.
    `send_test_email` uni `True` qiladi — u provayderning javobini
    ko'rish uchun aynan shunday manzildan foydalanadi (hujjatida
    `siz@example.com` yozilgan), ya'ni bu yerda to'sish o'sha ish
    qurolini sindirardi.
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

    if not allow_placeholder and is_placeholder(to):
        # Provayderga UMUMAN murojaat qilinmaydi. O'lchandi 2026-09-17:
        # load test 301 ta shunday manzilga «yubordi» va Brevo'ning
        # 300/kun bevosita shiftini 85 soniyada yoqib yubordi; panel
        # «311 yuborildi» derdi, aslida 10 tasi haqiqiy edi.
        #
        # Holat `SKIPPED`, `SENT` emas — `mail_quota.usage()` faqat
        # `SENT` ni sanaydi, ya'ni qator iz sifatida qoladi, kvotaga
        # esa tushmaydi.
        delivery.status = EmailDelivery.Status.SKIPPED
        delivery.attempts = [{"provider": "", "error": "zaxira domen — yuborilmadi"}]
        delivery.save()
        log.info("email o'tkazib yuborildi (zaxira domen): %s (%s)", to, purpose)
        return delivery

    message = Message(to=to, subject=subject, text=text, html=html)
    attempts: list[dict[str, str]] = []
    for name in chain if chain is not None else settings.EMAIL_CHAIN:
        provider = PROVIDERS.get(name)
        if provider is None:
            log.warning("EMAIL_CHAIN da unknown provider: %s", name)
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
