"""Taxallusni almashtirish — yiliga bir marta bepul, qolgani Qvant evaziga.

Taxallus reyting platformasida kimlik: standings, profil havolasi va
musobaqa jadvallari unga bog'langan. Shu sababli almashtirish ikki shart
bilan keladi (`UsernameHistory`): eski nom yangi profilga yo'naltiradi va
90 kun boshqaga berilmaydi — aks holda yangi egasi eski egasining obro'si
bilan standings'da tura olardi.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone

from core import handles
from core.models import User, UsernameHistory

#: Bepul almashtirish oralig'i.
FREE_EVERY = timedelta(days=365)
#: Bepul imkoniyat ishlatilgach — Qvant bilan istalgan payt.
PRICE = 500

#: Vaqtinchalik nom belgisi va uzunligi — `TEMP_PREFIX` + 12 belgi.
#: Format `RegisterSerializer._temp_username` da yasaladi; bu yerdagi
#: tekshiruv o'sha formatni taniydi.
TEMP_PREFIX = "u"
TEMP_LENGTH = 13


def is_temp_username(name: str) -> bool:
    """Nom ro'yxatdan o'tishda berilgan VAQTINCHALIK nommi.

    Nega kerak: `MeView` ikki xil holatni ajratishi kerak —
    (a) odam hali o'z nomini tanlamagan (2-qadam) va (b) odam
    allaqachon tanlagan nomini almashtiryapti. Birinchisida
    `claim_temp` (bepul, izsiz), ikkinchisida `change` (narx va
    `UsernameHistory`) ishlaydi.

    Formatni ajratish uchun uzunlik va prefiks yetarli: haqiqiy
    nomlar 3–30 belgi va `handles` qoidalariga bo'ysunadi, ya'ni
    `u` + aynan 12 ta kichik harf/raqam dan iborat nom amalda
    faqat mashina yasagan bo'ladi. Aks holda odam shunchaki shunday
    nom tanlagan bo'lishi mumkin — bu ziddiyat ATaylab qoldirilgan:
    noto'g'ri tomonga tushsa, u `claim_temp` bo'lardi, ya'ni bepul
    almashtirish sarflanmasdi (yo'qotish yo'q).
    """
    if len(name) != TEMP_LENGTH or not name.startswith(TEMP_PREFIX):
        return False
    return all(c.isdigit() or ("a" <= c <= "z") for c in name[1:])


class ChangeError(Exception):
    def __init__(self, message: str, *, code: str = "invalid", price: int | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.price = price


def reserved(name: str, *, exclude: User | None = None) -> bool:
    """Nom so'nggi 90 kunda boshqa hisobdan bo'shaganmi."""
    since = timezone.now() - UsernameHistory.RESERVE
    rows = UsernameHistory.objects.filter(old_username__iexact=name, changed_at__gte=since)
    if exclude is not None:
        rows = rows.exclude(user=exclude)
    return rows.exists()


def next_free_at(user: User) -> datetime | None:
    """Keyingi bepul almashtirish sanasi; `None` — hozir bepul."""
    if user.username_changed_at is None:
        return None
    at = user.username_changed_at + FREE_EVERY
    return at if at > timezone.now() else None


@transaction.atomic
def claim_temp(user: User, new: str) -> User:
    """VAQTINCHALIK nomni haqiqiysiga almashtiradi — ro'yxatdan o'tishning
    2-qadami (3-qaror).

    `change` dan farqi: bu ALMASHTIRISH emas, TUGALLASH. Hisob
    yaratilganda nom berilmagan (`u` + tasodifiy belgilar), ya'ni
    odam hali o'z nomini tanlamagan. Shu sababli bu yerga uchta yengillik
    kiradi va ularsiz oqim ishlamaydi:

    1. Bepul almashtirish imkoniyati SARFLANMAYDI. Aks holda har bir
       yangi hisob o'z «yiliga bir marta» ini birinchi daqiqada
       yo'qotardi va keyingi almashtirish uchun Qvant to'lashi kerak
       bo'lardi — bu adolatsiz va foydalanuvchi kutmagani.
    2. `UsernameHistory` yozilmaydi: vaqtinchalik nom hech qachon
       hech kimga ko'rinmagan (sessiya ochilmagan, ya'ni profil
       manzili tarqalmagan) va uni 90 kun band qilish ma'nosiz.
    3. Narx so'ralmaydi — bu birinchi va majburiy qadam.

    Tekshiruvlar `change` bilan bir xil TARTIBDA: nom qoidalari,
    registrsiz yagonalik, skelet, 90 kunlik bandlik.
    """
    new = new.strip()
    try:
        handles.validate(new)
    except DjangoValidationError as exc:
        raise ChangeError(exc.messages[0]) from None
    others = User.objects.exclude(pk=user.pk)
    if others.filter(username__iexact=new).exists():
        raise ChangeError("Bu username band")
    if others.filter(username_skeleton=handles.skeleton(new)).exists():
        raise ChangeError("Bu username mavjud nomga juda o'xshash")
    if reserved(new, exclude=user):
        raise ChangeError("Bu nom yaqinda boshqa foydalanuvchiga tegishli bo'lgan", code="reserved")

    # Qulf: parallel so'rovlar bitta nomni ikki marta olishga urinmasin.
    locked = User.objects.select_for_update().get(pk=user.pk)
    locked.username = new
    try:
        with transaction.atomic():
            locked.save(update_fields=["username", "username_skeleton"])
    except IntegrityError as exc:
        raise ChangeError("Bu username band") from exc
    return locked


@transaction.atomic
def change(user: User, new: str, *, pay: bool = False) -> User:
    from qvant import ledger
    from qvant.models import QvantTransaction

    new = new.strip()
    if new == user.username:
        raise ChangeError("Bu sizning hozirgi taxallusingiz")
    try:
        handles.validate(new)
    except DjangoValidationError as exc:
        raise ChangeError(exc.messages[0]) from None
    others = User.objects.exclude(pk=user.pk)
    if others.filter(username__iexact=new).exists():
        raise ChangeError("Bu username band")
    if others.filter(username_skeleton=handles.skeleton(new)).exists():
        raise ChangeError("Bu username mavjud nomga juda o'xshash")
    if reserved(new, exclude=user):
        raise ChangeError("Bu nom yaqinda boshqa foydalanuvchiga tegishli bo'lgan", code="reserved")

    # Qulf: ikki parallel so'rov bitta bepul imkoniyatni ikki marta ishlata olmasin.
    locked = User.objects.select_for_update().get(pk=user.pk)
    free = next_free_at(locked) is None
    if not free:
        if not pay:
            raise ChangeError(
                "Bepul almashtirish yiliga bir marta", code="payment_required", price=PRICE
            )
        try:
            ledger.debit(
                locked,
                PRICE,
                QvantTransaction.Reason.PURCHASE,
                ref_type="username_change",
                ref_id=new,
            )
        except ledger.InsufficientBalance as exc:
            raise ChangeError(
                f"Balans yetarli emas ({exc})", code="insufficient_balance", price=PRICE
            ) from exc

    UsernameHistory.objects.create(user=locked, old_username=locked.username)
    locked.username = new
    fields = ["username", "username_skeleton"]
    if free:
        locked.username_changed_at = timezone.now()
        fields.append("username_changed_at")
    try:
        with transaction.atomic():
            locked.save(update_fields=fields)
    except IntegrityError as exc:
        raise ChangeError("Bu username band") from exc
    return locked
