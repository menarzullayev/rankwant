"""Pochtani tasdiqlash — token chiqarish va iste'mol qilish (ADR-0016).

`recovery` dan alohida modul, chunki qoidalari boshqa: kodni sanashning
keragi yo'q, muddati uzunroq va tasdiqlash HECH NARSANI ochmaydi — u
faqat manzil ishlashini qayd etadi. Shu sababli uni bir joyda ushlab
turish soddalashtirmasdi, faqat ikkala oqimning qoidalarini chalkashtirardi.
"""

from __future__ import annotations

import secrets
from dataclasses import dataclass

from django.db import transaction
from django.utils import timezone

from core.models import EmailVerifyToken, User

TOKEN_BYTES = 32


class TooManyRequests(Exception):
    """Cheklovga urildi. Chaqiruvchi buni 429 ga aylantiradi."""


@dataclass(frozen=True)
class Issued:
    row: EmailVerifyToken
    raw: str
    code: str


@transaction.atomic
def issue(user: User, *, enforce_limit: bool = True) -> Issued:
    """Yangi havola chiqaradi va eskilarini yopadi."""
    if enforce_limit:
        since = timezone.now() - EmailVerifyToken.TTL
        if (
            EmailVerifyToken.objects.filter(user=user, created_at__gte=since).count()
            >= EmailVerifyToken.PER_USER_HOUR
        ):
            raise TooManyRequests("hisob chegarasi")

    EmailVerifyToken.objects.filter(user=user, used_at__isnull=True).update(used_at=timezone.now())

    raw = secrets.token_urlsafe(TOKEN_BYTES)
    code = f"{secrets.randbelow(10**6):06d}"
    row = EmailVerifyToken.objects.create(
        user=user,
        token_hash=EmailVerifyToken.hash_value(raw),
        code_hash=EmailVerifyToken.hash_value(code),
        email=user.email,
        expires_at=timezone.now() + EmailVerifyToken.TTL,
    )
    return Issued(row=row, raw=raw, code=code)


@transaction.atomic
def consume(*, raw: str = "", code: str = "", username: str = "") -> User | None:
    """Tokenni ishlatadi va egasini qaytaradi. Yaroqsiz bo'lsa `None`.

    Manzil almashtirilgan bo'lsa token ishlamaydi: u chiqarilgan paytdagi
    manzilni tasdiqlaydi, hozirgisini emas.
    """
    if raw:
        row = (
            EmailVerifyToken.objects.select_for_update()
            .filter(token_hash=EmailVerifyToken.hash_value(raw))
            .first()
        )
    elif code and username:
        row = (
            EmailVerifyToken.objects.select_for_update()
            .filter(user__username=username, used_at__isnull=True)
            .order_by("-created_at")
            .first()
        )
        if row is not None and not secrets.compare_digest(
            row.code_hash, EmailVerifyToken.hash_value(code)
        ):
            return None
    else:
        return None

    if row is None or not row.is_live or row.email.lower() != row.user.email.lower():
        return None

    row.used_at = timezone.now()
    row.save(update_fields=["used_at"])
    # Ikkinchi marta bosilganda ham xato bermaydi — natija bir xil.
    if row.user.email_verified_at is None:
        row.user.email_verified_at = timezone.now()
        row.user.save(update_fields=["email_verified_at"])
    return row.user
