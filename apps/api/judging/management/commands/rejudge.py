"""Tekshirilgan urinishlarni qayta navbatga qo'yadi.

Ishlatish:
    python manage.py rejudge --problem a-plus-b [--verdict AC] [--limit N] [--dry-run]
    python manage.py rejudge --contest kuz-2026

10-operations § 3: «Rejudge PARTIYADA va e'lon bilan». Noto'g'ri test yoki
buzuq checker tuzatilganda barcha ta'sirlangan yechimlar eski verdicti
bilan qolib ketardi — uni qayta ishga tushiradigan yo'l umuman yo'q edi,
holbuki ADR-0002, arxitektura hujjati va runbook uni va'da qiladi.

Natija kelganda quyi oqim O'ZI to'g'rilanadi (`judging.services.
apply_result`): AC bekor qilinsa yechim yozuvi, Skills va Qvant
qaytariladi, contest bo'lsa standings qayta hisoblanadi.
"""

from __future__ import annotations

from argparse import ArgumentParser
from typing import Any

from django.core.management.base import BaseCommand, CommandError
from django.db.models import QuerySet

from judging.models import Attempt
from judging.provider import get_provider
from judging.services import build_job
from judging.verdicts import Verdict

#: Hali javob kutayotgan urinishni qayta qo'yishning ma'nosi yo'q —
#: u navbatda yoki ishlanmoqda. Ular `reap_stuck` ning ishi.
LIVE = (Verdict.PENDING, Verdict.RUNNING)


class Command(BaseCommand):
    help = "Masala yoki contest bo'yicha urinishlarni qayta tekshiradi."

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--problem", help="Masala slug'i")
        parser.add_argument("--contest", help="Contest slug'i")
        parser.add_argument("--verdict", help="Faqat shu verdict (masalan AC)")
        parser.add_argument("--limit", type=int, default=500, help="Bir partiyada nechta")
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args: Any, **options: Any) -> None:
        # Filtrsiz rejudge butun arxivni navbatga tiqardi. Buni tasodifan
        # yozib yuborish oson, ortga qaytarish esa mumkin emas.
        if not options["problem"] and not options["contest"]:
            raise CommandError("--problem yoki --contest ko'rsating")

        rows: QuerySet[Attempt] = Attempt.objects.exclude(verdict__in=LIVE)
        if options["problem"]:
            rows = rows.filter(problem__slug=options["problem"])
        if options["contest"]:
            rows = rows.filter(contest__slug=options["contest"])
        if options["verdict"]:
            rows = rows.filter(verdict=options["verdict"].upper())

        total = rows.count()
        limit = options["limit"]
        self.stdout.write(f"Mos urinish: {total}, bu partiyada: {min(total, limit)}")
        if options["dry_run"]:
            self.stdout.write(self.style.WARNING("(dry-run) hech narsa yuborilmadi"))
            return

        provider = get_provider()
        sent = 0
        for attempt in rows.select_related("problem", "language").order_by("pk")[:limit]:
            try:
                provider.submit(build_job(attempt))
            except Exception as exc:
                self.stderr.write(f"  yiqildi #{attempt.pk}: {exc}")
                continue
            # `enqueue` ATAYIN ishlatilmaydi: u `attempt_count` ni
            # oshiradi, qayta tekshirish esa yangi urinish emas.
            Attempt.objects.filter(pk=attempt.pk).update(
                verdict=Verdict.PENDING, judged_at=None, requeued_at=None
            )
            sent += 1

        qoldi = total - sent
        self.stdout.write(
            self.style.SUCCESS(f"{sent} ta urinish qayta navbatga qo'yildi")
            + (f", yana {qoldi} ta qoldi — buyruqni takrorlang" if qoldi > 0 else "")
        )
