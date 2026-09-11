from __future__ import annotations

import logging
from typing import Any

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


def queue(task: Any, *args: Any) -> bool:
    """Vazifani navbatga qo'yadi; broker yiqilsa YUTADI.

    Xat — yordamchi ta'sir. Broker o'chgan bo'lsa ham hisob ochilishi
    kerak, aks holda Redis uzilishi ro'yxatdan o'tishni butunlay
    to'xtatardi. O'lchandi: `.delay()` `OperationalError` otadi va u
    500 ga aylanadi, foydalanuvchi esa hisobsiz qoladi.
    """
    try:
        task.delay(*args)
    except Exception:  # broker xatosi oqimni to'xtatmaydi
        log.warning("navbatga qo'yilmadi: %s", getattr(task, "name", task), exc_info=True)
        return False
    return True


@shared_task(name="core.send_email_verify")
def send_email_verify(user_id: int, token: str, code: str, to: str = "") -> str:
    """Tasdiqlash xatini renderlab zanjirga topshiradi.

    Ro'yxatdan o'tish javobini kutib turmaydi: xat kelmasa ham hisob
    ochilgan bo'lishi kerak — tasdiqlash yumshoq, ya'ni majburiy emas.

    `to` — pochtani almashtirishda YANGI manzil: xat hali tasdiqlanmagan
    manzilga ketadi, `User.email` esa hozircha eskisi.
    """
    from core import emails
    from core.models import User

    user = User.objects.filter(pk=user_id).first()
    if user is None or not (to or user.email):
        log.warning("tasdiqlash xati yuborilmadi — foydalanuvchi yo'q: %s", user_id)
        return "skipped"
    return emails.send_email_verify(user, token=token, code=code, to=to or None).status


@shared_task(name="core.send_email_changed")
def send_email_changed(user_id: int, old_email: str) -> str:
    """Eski manzilga «pochta almashtirildi» ogohlantirishi."""
    from core import emails
    from core.models import User

    user = User.objects.filter(pk=user_id).first()
    if user is None or not old_email:
        return "skipped"
    return emails.send_email_changed(user, old_email).status


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
