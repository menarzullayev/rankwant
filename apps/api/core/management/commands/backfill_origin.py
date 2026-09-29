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
from django.db.models import Q, QuerySet

from core.models import User

#: Demo email domenlari
DEMO_DOMAINS = ("@example.invalid", "@example.com")

#: Demo username prefikslari
DEMO_PREFIXES = ("neytron_", "stress_")

#: Bir partiyada yangilanadigan qatorlar soni
BATCH_SIZE = 2000


def _is_demo(user: User) -> bool:
    """Email yoki username bo'yicha demo foydalanuvchini aniqlaydi."""
    email = (user.email or "").lower()
    if any(email.endswith(d) for d in DEMO_DOMAINS):
        return True
    username = user.username.lower()
    if any(username.startswith(p) for p in DEMO_PREFIXES):
        return True
    return False


def _is_imported(user: User) -> bool:
    """Tashqi manbadan import qilingan foydalanuvchini aniqlaydi."""
    # terms_accepted_at IS NULL — ro'yxatdan o'tmagan (import)
    # Parol yo'q yoki ishlatib bo'lmaydigan
    if user.terms_accepted_at is not None:
        return False
    if not user.password or not is_password_usable(user.password):
        return True
    return False


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
