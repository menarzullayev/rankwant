"""Pochtani tasdiqlash va almashtirish — token chiqarish va iste'mol qilish.

`recovery` dan alohida modul, chunki qoidalari boshqa: kodni sanashning
keragi yo'q, muddati uzunroq va tasdiqlash HECH NARSANI ochmaydi — u
faqat manzil ishlashini qayd etadi.

Ikki maqsad bitta tokenda (`purpose`):
* `VERIFY` — joriy manzil ishlashini tasdiqlaydi;
* `CHANGE` — YANGI manzilni: u tasdiqlanmaguncha `User.email` eskisi
  bo'lib qoladi. Aks holda xato yozilgan manzil darhol kuchga kirar va
  parolni tiklash kanali yo'qolardi.
"""

from __future__ import annotations

import secrets
from dataclasses import dataclass

from django.db import IntegrityError, transaction
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
def issue(
    user: User,
    *,
    enforce_limit: bool = True,
    email: str | None = None,
    purpose: str = EmailVerifyToken.Purpose.VERIFY,
) -> Issued:
    """Yangi havola chiqaradi va SHU MAQSADDAGI eskilarini yopadi.

    Tasdiqlash va almashtirish tokenlari bir-birini yopmaydi: pochtani
    almashtirishni boshlagan odam eski manzilini tasdiqlash havolasini
    ham ishlata olishi kerak. Chegara esa ikkalasiga umumiy.
    """
    if enforce_limit:
        since = timezone.now() - EmailVerifyToken.TTL
        recent = EmailVerifyToken.objects.filter(user=user, created_at__gte=since).count()
        if recent >= EmailVerifyToken.PER_USER_HOUR:
            raise TooManyRequests("hisob chegarasi")

    EmailVerifyToken.objects.filter(user=user, used_at__isnull=True, purpose=purpose).update(
        used_at=timezone.now()
    )

    raw = secrets.token_urlsafe(TOKEN_BYTES)
    code = f"{secrets.randbelow(10**6):06d}"
    row = EmailVerifyToken.objects.create(
        user=user,
        token_hash=EmailVerifyToken.hash_value(raw),
        code_hash=EmailVerifyToken.hash_value(code),
        email=email or user.email,
        purpose=purpose,
        expires_at=timezone.now() + EmailVerifyToken.TTL,
    )
    return Issued(row=row, raw=raw, code=code)


@transaction.atomic
def consume(*, raw: str = "", code: str = "", username: str = "") -> User | None:
    """Tokenni ishlatadi va egasini qaytaradi. Yaroqsiz bo'lsa `None`."""
    if raw:
        row = (
            EmailVerifyToken.objects.select_for_update()
            .filter(token_hash=EmailVerifyToken.hash_value(raw))
            .first()
        )
    elif code and username:
        # Bir vaqtda ikki tirik token bo'lishi mumkin (tasdiqlash va
        # almashtirish) — kod qaysi biriga tegishli bo'lsa, o'shani oladi.
        row = (
            EmailVerifyToken.objects.select_for_update()
            .filter(
                user__username=username,
                used_at__isnull=True,
                code_hash=EmailVerifyToken.hash_value(code),
            )
            .order_by("-created_at")
            .first()
        )
    else:
        return None

    if row is None or not row.is_live:
        return None
    if row.purpose == EmailVerifyToken.Purpose.CHANGE:
        return _apply_change(row)

    user = row.user
    # Manzil almashtirilgan bo'lsa token ishlamaydi: u chiqarilgan paytdagi
    # manzilni tasdiqlaydi, hozirgisini emas.
    if row.email.lower() != user.email.lower():
        return None
    row.used_at = timezone.now()
    row.save(update_fields=["used_at"])
    # Ikkinchi marta bosilganda ham xato bermaydi — natija bir xil.
    if user.email_verified_at is None:
        user.email_verified_at = timezone.now()
        user.save(update_fields=["email_verified_at"])
    return user


def _apply_change(row: EmailVerifyToken) -> User | None:
    user = row.user
    if User.objects.filter(email__iexact=row.email).exclude(pk=user.pk).exists():
        return None
    old = user.email
    user.email = row.email
    user.email_verified_at = timezone.now()
    try:
        with transaction.atomic():
            user.save(update_fields=["email", "email_verified_at"])
    except IntegrityError:
        # Tekshiruv bilan yozuv orasida manzil band qilindi.
        return None
    now = timezone.now()
    row.used_at = now
    row.save(update_fields=["used_at"])
    # Eski manzil uchun chiqarilgan tokenlar endi ma'nosiz.
    EmailVerifyToken.objects.filter(user=user, used_at__isnull=True).update(used_at=now)
    if old and old.lower() != row.email.lower():
        from core.tasks import queue, send_email_changed

        queue(send_email_changed, user.pk, old)
    return user
