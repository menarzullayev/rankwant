"""Qvant ledgeri — balansni o'zgartirishning YAGONA yo'li.

ADR-0002: «balans hech qachon to'g'ridan-to'g'ri yozilmaydi». Bu qoida
audit va rejudge da qaytarish uchun emas, faqat ular uchun ham emas:
ledgersiz «foydalanuvchida qayerdan 5000 Qvant paydo bo'ldi?» degan
savolga javob berib bo'lmaydi.
"""

from __future__ import annotations

import logging
from datetime import date, datetime, time

from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from core.models import User
from qvant.models import DAILY_EARN_CAP, QvantTransaction, QvantWallet

log = logging.getLogger(__name__)

#: Kunlik shiftdan ozod sabablar — ADR-0002: «streak yutuqlari bundan tashqari».
CAP_EXEMPT = frozenset({QvantTransaction.Reason.STREAK, QvantTransaction.Reason.ADMIN})


class InsufficientBalance(Exception):
    """Balans yetarli emas — xarid bajarilmaydi."""


def get_wallet(user: User) -> QvantWallet:
    wallet, _ = QvantWallet.objects.get_or_create(user=user)
    return wallet


def earned_today(user: User, when: date | None = None) -> int:
    """Shiftga kiradigan bugungi emissiya."""
    day = when or timezone.localdate()
    start = timezone.make_aware(datetime.combine(day, time.min))
    end = timezone.make_aware(datetime.combine(day, time.max))
    total = (
        QvantTransaction.objects.filter(user=user, amount__gt=0, created_at__range=(start, end))
        .exclude(reason__in=CAP_EXEMPT)
        .aggregate(total=Sum("amount"))["total"]
    )
    return total or 0


def remaining_today(user: User) -> int:
    return max(0, DAILY_EARN_CAP - earned_today(user))


@transaction.atomic
def credit(
    user: User,
    amount: int,
    reason: str,
    *,
    ref_type: str = "",
    ref_id: str = "",
    respect_cap: bool = True,
) -> QvantTransaction | None:
    """Qvant qo'shadi. Shiftga yetgan bo'lsa QISMAN yoki umuman bermaydi.

    Qaytaradi: yozilgan tranzaksiya, yoki hech narsa berilmagan bo'lsa None.
    """
    if amount <= 0:
        raise ValueError("credit musbat miqdor talab qiladi")

    if respect_cap and reason not in CAP_EXEMPT:
        available = remaining_today(user)
        if available <= 0:
            log.info("kunlik Qvant shifti: %s uchun %s berilmadi", user.pk, amount)
            return None
        amount = min(amount, available)

    wallet = QvantWallet.objects.select_for_update().get_or_create(user=user)[0]
    wallet.balance += amount
    wallet.save(update_fields=["balance", "updated_at"])
    return QvantTransaction.objects.create(
        user=user,
        amount=amount,
        reason=reason,
        ref_type=ref_type,
        ref_id=str(ref_id),
        balance_after=wallet.balance,
    )


@transaction.atomic
def debit(
    user: User, amount: int, reason: str, *, ref_type: str = "", ref_id: str = ""
) -> QvantTransaction:
    """Qvant yechadi. Balans yetmasa `InsufficientBalance`.

    `select_for_update` shart: ikkita bir vaqtdagi xarid balansdan
    ikki marta yechib, manfiyga tushirishi mumkin edi.
    """
    if amount <= 0:
        raise ValueError("debit musbat miqdor talab qiladi")

    wallet = QvantWallet.objects.select_for_update().get_or_create(user=user)[0]
    if wallet.balance < amount:
        raise InsufficientBalance(f"balans {wallet.balance}, kerak {amount}")

    wallet.balance -= amount
    wallet.save(update_fields=["balance", "updated_at"])
    return QvantTransaction.objects.create(
        user=user,
        amount=-amount,
        reason=reason,
        ref_type=ref_type,
        ref_id=str(ref_id),
        balance_after=wallet.balance,
    )


@transaction.atomic
def refund_ref(user: User, ref_type: str, ref_id: str) -> int:
    """Berilgan havola bo'yicha berilgan Qvant ni qaytarib oladi.

    ADR-0002: «contest bekor qilinsa yoki rejudge natijasi o'zgarsa —
    Qvant qaytariladi». Balans manfiyga tushishi MUMKIN emas: foydalanuvchi
    allaqachon sarflagan bo'lsa, qaytarish mavjud balansgacha cheklanadi.
    """
    granted = (
        QvantTransaction.objects.filter(
            user=user, ref_type=ref_type, ref_id=str(ref_id), amount__gt=0
        ).aggregate(total=Sum("amount"))["total"]
        or 0
    )
    already = (
        QvantTransaction.objects.filter(
            user=user,
            ref_type=ref_type,
            ref_id=str(ref_id),
            reason=QvantTransaction.Reason.REFUND,
        ).aggregate(total=Sum("amount"))["total"]
        or 0
    )
    outstanding = granted + already  # already manfiy
    if outstanding <= 0:
        return 0

    wallet = QvantWallet.objects.select_for_update().get_or_create(user=user)[0]
    take = min(outstanding, max(0, wallet.balance))
    if take == 0:
        log.warning(
            "qaytarish imkonsiz: %s uchun %s %s — balans %s",
            user.pk,
            ref_type,
            ref_id,
            wallet.balance,
        )
        return 0

    wallet.balance -= take
    wallet.save(update_fields=["balance", "updated_at"])
    QvantTransaction.objects.create(
        user=user,
        amount=-take,
        reason=QvantTransaction.Reason.REFUND,
        ref_type=ref_type,
        ref_id=str(ref_id),
        balance_after=wallet.balance,
    )
    return take


def verify_balance(user: User) -> tuple[int, int]:
    """Kesh va ledger mos keladimi — audit uchun.

    Qaytaradi: (keshdagi balans, ledger yig'indisi).
    """
    cached = get_wallet(user).balance
    ledger = QvantTransaction.objects.filter(user=user).aggregate(total=Sum("amount"))["total"] or 0
    return cached, ledger
