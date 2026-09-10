"""Parolni tiklash — token chiqarish va iste'mol qilish (ADR-0015).

Bu modul xat YUBORMAYDI va HTTP ni bilmaydi: u faqat tokenning hayotini
boshqaradi. Shu sababli uni uchala kanal ham bir xil ishlatadi — email,
staff qo'lda yaratgan havola va (keyinchalik) Telegram bot.
"""

from __future__ import annotations

import logging
import secrets
from dataclasses import dataclass

from django.db import transaction
from django.utils import timezone

from core.models import PasswordResetToken, User

log = logging.getLogger(__name__)

#: Havola tokeni. `ApiToken` dagi kabi URL-xavfsiz va taxmin qilib bo'lmaydigan.
TOKEN_BYTES = 32


class TooManyRequests(Exception):
    """Cheklovga urildi. Chaqiruvchi buni 429 ga aylantiradi."""


@dataclass(frozen=True)
class Issued:
    """Chiqarilgan token. `raw` va `code` FAQAT shu yerda ko'rinadi."""

    row: PasswordResetToken
    raw: str
    code: str


def _recent(**filters: object) -> int:
    since = timezone.now() - PasswordResetToken.TTL
    return PasswordResetToken.objects.filter(created_at__gte=since, **filters).count()


@transaction.atomic
def issue(user: User, *, ip: str = "", user_agent: str = "", enforce_limit: bool = True) -> Issued:
    """Yangi havola va kod chiqaradi, eskilarini o'chiradi.

    Eskilarini bekor qilish shart: aks holda foydalanuvchi «yana yuboring»
    tugmasini uch marta bosgach, uchta amaldagi havola qolardi va ularning
    ikkitasi pochtada kutib turardi.

    `enforce_limit=False` — staff qo'lda yaratganda: staff so'rovi
    foydalanuvchining soatlik chegarasini yemasligi kerak, aynan chegaraga
    urilgan odamga yordam berish uchun chaqiriladi.
    """
    if enforce_limit:
        if _recent(user=user) >= PasswordResetToken.PER_USER_HOUR:
            raise TooManyRequests("hisob chegarasi")
        if ip and _recent(request_ip=ip) >= PasswordResetToken.PER_IP_HOUR:
            raise TooManyRequests("IP chegarasi")

    # Amaldagi tokenlarni yopamiz — o'chirmaymiz: `created_at` chegaralarni
    # hisoblashda kerak, ya'ni o'chirish cheklovni chetlab o'tish yo'li bo'lardi.
    PasswordResetToken.objects.filter(user=user, used_at__isnull=True).update(
        used_at=timezone.now()
    )

    raw = secrets.token_urlsafe(TOKEN_BYTES)
    code = f"{secrets.randbelow(10**6):06d}"
    row = PasswordResetToken.objects.create(
        user=user,
        token_hash=PasswordResetToken.hash_value(raw),
        code_hash=PasswordResetToken.hash_value(code),
        request_ip=ip or None,
        request_ua=user_agent[:200],
        expires_at=timezone.now() + PasswordResetToken.TTL,
    )
    return Issued(row=row, raw=raw, code=code)


def _live(**lookup: str) -> PasswordResetToken | None:
    row = PasswordResetToken.objects.select_for_update().filter(**lookup).first()
    return row if row is not None and row.is_live else None


@transaction.atomic
def consume(
    *, raw: str = "", code: str = "", username: str = "", commit: bool = True
) -> User | None:
    """Tokenni ishlatadi va egasini qaytaradi. Yaroqsiz bo'lsa `None`.

    `commit=False` — tokenni YOQMASDAN egasini aniqlaydi. Chaqiruvchiga
    yangi parolni tekshirish uchun kerak: parol qoidaga to'g'ri kelmasa
    token omon qolishi va foydalanuvchi qaytadan urinishi kerak. Aks holda
    bitta zaif parol havolani kuydirar va u yangi xat so'rashga majbur
    bo'lardi — soatlik kvotasini yeb.

    Noto'g'ri KOD esa `commit` dan qat'i nazar urinish sifatida sanaladi,
    aks holda `commit=False` brute-force uchun bepul yo'l bo'lardi.

    Havola bo'yicha qidirish kalitning O'ZI bilan bo'ladi. Kod bo'yicha esa
    foydalanuvchi ham kerak — 6 xonali kod butun baza bo'ylab yagona emas
    va uni kimningdir tokeniga tasodifan tushishiga yo'l qo'yib bo'lmaydi.
    """
    if raw:
        row = _live(token_hash=PasswordResetToken.hash_value(raw))
        if row is None:
            return None
    elif code and username:
        row = (
            PasswordResetToken.objects.select_for_update()
            .filter(user__username=username, used_at__isnull=True)
            .order_by("-created_at")
            .first()
        )
        if row is None or not row.is_live:
            return None
        if row.attempts >= PasswordResetToken.MAX_ATTEMPTS:
            # Urinishlar tugagan tokenni butunlay yopamiz, aks holda u
            # muddati tugaguncha yana-yana sinaladigan nishon bo'lib qolardi.
            row.used_at = timezone.now()
            row.save(update_fields=["used_at"])
            log.warning("tiklash kodi: urinishlar tugadi, token yopildi (%s)", row.user_id)
            return None
        if not secrets.compare_digest(row.code_hash, PasswordResetToken.hash_value(code)):
            row.attempts += 1
            row.save(update_fields=["attempts"])
            return None
    else:
        return None

    if commit:
        row.used_at = timezone.now()
        row.save(update_fields=["used_at"])
    return row.user
