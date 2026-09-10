"""Yuborishlarni bekor qiladi — plagiat yoki qoida buzilishi uchun.

Ishlatish:
    python manage.py skip_attempts --user aziz --problem a-plus-b --dry-run
    python manage.py skip_attempts --user aziz --contest kuz-2026

`SKIPPED` verdikti Codeforces'dagi kabi: yuborish HISOBGA OLINMAYDI.
Ilgari bu kod e'lon qilingan, web'da yorlig'i bor edi, lekin uni hech
qanday kod yozmasdi.

Eng muhim qismi — AC ni bekor qilish yechim yozuvini ham olib tashlaydi:
usiz plagiat qilingan yechim Skills reytingida qolib ketardi va jazo
ma'nosiz bo'lardi.
"""

from __future__ import annotations

from argparse import ArgumentParser
from typing import Any

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from core.models import User
from judging.models import Attempt
from judging.verdicts import Verdict


class Command(BaseCommand):
    help = "Foydalanuvchining yuborishlarini SKIPPED qiladi."

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--user", required=True, help="Username")
        parser.add_argument("--problem", help="Masala slug'i")
        parser.add_argument("--contest", help="Contest slug'i")
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args: Any, **options: Any) -> None:
        user = User.objects.filter(username=options["user"]).first()
        if user is None:
            raise CommandError(f"foydalanuvchi topilmadi: {options['user']}")

        rows = Attempt.objects.filter(user=user).exclude(verdict=Verdict.SKIPPED)
        if options["problem"]:
            rows = rows.filter(problem__slug=options["problem"])
        if options["contest"]:
            rows = rows.filter(contest__slug=options["contest"])
        # Masalasiz va contestsiz chaqiruv butun tarixni o'chirardi.
        if not options["problem"] and not options["contest"]:
            raise CommandError("--problem yoki --contest ko'rsating")

        jami = rows.count()
        ac = rows.filter(verdict=Verdict.AC).count()
        self.stdout.write(f"Bekor qilinadi: {jami} urinish, ulardan {ac} tasi AC")
        if options["dry_run"]:
            self.stdout.write(self.style.WARNING("(dry-run) hech narsa o'zgarmadi"))
            return

        from ratings.services import on_accept_revoked

        bekor = 0
        for attempt in rows.select_related("user", "problem").order_by("pk"):
            edi_ac = attempt.verdict == Verdict.AC
            with transaction.atomic():
                Attempt.objects.filter(pk=attempt.pk).update(
                    verdict=Verdict.SKIPPED, judged_at=timezone.now()
                )
                if edi_ac:
                    attempt.verdict = Verdict.SKIPPED
                    # Yechim yozuvi, Skills va Qvant qaytariladi.
                    on_accept_revoked(attempt)
                    bekor += 1

        self.stdout.write(
            self.style.SUCCESS(f"{jami} urinish bekor qilindi, {bekor} ta yechim qaytarildi")
        )
