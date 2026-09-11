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
