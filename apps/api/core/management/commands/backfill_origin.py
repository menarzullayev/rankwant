"""User.origin backfill — M3 (WP3).

Ishlatish:
    python manage.py backfill_origin
    python manage.py backfill_origin --dry-run
"""

from __future__ import annotations

from argparse import ArgumentParser
from typing import Any

from django.contrib.auth.hashers import is_password_usable
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import QuerySet

from core.models import User

#: Demo username prefikslari — YAGONA haqiqiy marker.
#: O'lchandi (QA 2026-09-29): `seed_stress.py` neytronlarni EMAIL'SIZ
#: yaratadi (`bulk_create`, email maydoni yo'q), `prune_test_users.py` ham
#: prefiks bo'yicha o'chiradi, `seed_contest_scale.py` pool'ni ham
#: `username__startswith="neytron_"` bilan tanlaydi. Email-domenga tayanadigan
#: hech qanday yozuv yo'q — domen qoidasi o'ylab topilgan edi va uni olib
#: tashladik: `@example.com` zaxira domen bo'lsa-da, qoida faqat xayoliy
#: holatlarni ushlaydi va real user'ni demo'ga aylantirib yuborardi.
DEMO_PREFIXES = ("neytron_", "stress_")

#: Bir partiyada yangilanadigan qatorlar soni
BATCH_SIZE = 2000


def _is_demo(user: User) -> bool:
    """Stress/demo foydalanuvchini username prefiksi bo'yicha aniqlaydi."""
    username = user.username.lower()
    return any(username.startswith(p) for p in DEMO_PREFIXES)


def _is_imported(user: User) -> bool:
    """Tashqi manbadan import qilingan foydalanuvchini aniqlaydi.

    O'lchandi: `sync_codeforces.py` import qilinganlarda `email=""` va
    ishlatib bo'lmaydigan parol bilan yaratadi; ular ro'yxatdan o'tmagan,
    shuning uchun `terms_accepted_at` NULL bo'ladi.
    """
    if user.terms_accepted_at is not None:
        return False
    return bool(not user.password or not is_password_usable(user.password))


def _is_staff(user: User) -> bool:
    """Xodim yoki superuser."""
    return user.is_staff or user.is_superuser


def classify(user: User) -> str:
    """Bitta foydalanuvchini toifalaydi.

    Tartib: staff > demo > imported > real.
    """
    if _is_staff(user):
        return User.Origin.STAFF
    if _is_demo(user):
        return User.Origin.DEMO
    if _is_imported(user):
        return User.Origin.IMPORTED
    return User.Origin.REAL


class Command(BaseCommand):
    help = "User.origin maydonini backfill qiladi (M3)"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Faqat sanaydi, yangilamaydi",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        dry_run: bool = options["dry_run"]

        counts: dict[str, int] = {
            User.Origin.REAL: 0,
            User.Origin.DEMO: 0,
            User.Origin.IMPORTED: 0,
            User.Origin.STAFF: 0,
        }

        qs: QuerySet[User] = User.objects.order_by("pk")
        total = qs.count()

        if dry_run:
            for user in qs.iterator(chunk_size=BATCH_SIZE):
                counts[classify(user)] += 1
        else:
            with transaction.atomic():
                # Partiyalarda yangilash — butun jadvalni qulflamaydi
                batch: list[User] = []
                for user in qs.iterator(chunk_size=BATCH_SIZE):
                    origin = classify(user)
                    if user.origin != origin:
                        user.origin = origin
                        batch.append(user)
                        counts[origin] += 1
                    else:
                        counts[origin] += 1

                    if len(batch) >= BATCH_SIZE:
                        User.objects.bulk_update(batch, ["origin"])
                        batch = []

                if batch:
                    User.objects.bulk_update(batch, ["origin"])

        self.stdout.write(
            f"real={counts[User.Origin.REAL]}, "
            f"demo={counts[User.Origin.DEMO]}, "
            f"imported={counts[User.Origin.IMPORTED]}, "
            f"staff={counts[User.Origin.STAFF]}, "
            f"total={total}"
        )

        if dry_run:
            self.stdout.write(self.style.WARNING("(dry-run — hech narsa o'zgartirilmadi)"))
        else:
            self.stdout.write(self.style.SUCCESS("Backfill tugadi"))
