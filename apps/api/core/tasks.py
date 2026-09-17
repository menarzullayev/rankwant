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


@shared_task(name="core.warn_email_quota")
def warn_email_quota() -> str:
    """Kunlik email kvotasi tugayotganini xodimlarga bildiradi.

    NEGA KERAK: zanjir bepul planlar ustiga qurilgan, ya'ni kunlik shift
    tugashi ODATIY holat — lekin buni hech kim ko'rmaydi. 2026-09-17 da
    o'lchandi: `brevo` 311 ta yuborgan, shifti esa 300 — ya'ni u allaqachon
    navbatdan ishlayotgan edi va buni faqat qo'lda hisoblab bilish mumkin
    edi. Panel `?when=` bilan ko'rsatadi, lekin panelni ochish kerak; bu
    vazifa esa o'zi aytadi.

    NEGA FON REJIMIDA: ogohlantirish hech narsani TO'XTATMAYDI va hech
    qanday hisob-kitobga ta'sir qilmaydi. Xato bo'lsa ham yutiladi —
    bildirishnoma tizimi yiqilsa ro'yxatdan o'tish ishlashda davom etishi
    kerak (`notifications.services.notify` xatoni o'zi yutadi).

    Faqat sayt kanali (`is_staff` larga) — Telegram ataylab qo'shilmagan:
    foydalanuvchi tanlovi shu, va botga so'ramasdan yuborish uni spamga
    aylantirardi (`DEFAULT_CHANNELS`).
    """
    from core import mail_quota
    from core.models import User
    from notifications.models import Notification

    matn = mail_quota.summary()
    if not matn:
        return "ok"  # hech narsa tugamagan — jim

    xodimlar = list(User.objects.filter(is_staff=True, is_active=True))
    if not xodimlar:
        log.warning("kvota ogohlantirilmadi — xodim yo'q")
        return "skipped"

    # ⚠️ `notifications.notify()` ATAYLAB ishlatilmaydi: u foydalanuvchi
    # sozlamasini hurmat qiladi (`channels()`), xodim esa bu xabarni
    # o'chirib qo'yishi mumkin — va aynan o'shanda kvota jimgina tugaydi.
    # Bu TIZIM xabari, ya'ni kanal tanlovi emas, burch.
    kun = mail_quota.day_start().date().isoformat()
    yaratildi = 0
    for xodim in xodimlar:
        try:
            # Bir kunda bir marta: vazifa kuniga bir marta yursa ham,
            # qo'lda qayta chaqirilsa takror yozilmasin.
            _, created = Notification.objects.get_or_create(
                user=xodim,
                kind=Notification.Kind.SYSTEM,
                ref_type="mail_quota",
                ref_id=kun,
                defaults={"title": mail_quota.ALERT_TITLE, "body": matn},
            )
            yaratildi += int(created)
        except Exception:
            # Ogohlantirish hech narsani to'xtatmaydi — xato yutiladi.
            log.exception("kvota bildirishnomasi yozilmadi: %s", xodim.pk)

    log.info("kvota ogohlantirildi: %s yangi / %s xodim — %s", yaratildi, len(xodimlar), matn)
    return "ok"
