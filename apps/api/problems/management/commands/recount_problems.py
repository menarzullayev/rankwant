"""Masaladagi denormallashtirilgan sanoqlarni haqiqat bilan tenglashtiradi.

Ishlatish:  python manage.py recount_problems [--dry-run]

`solved_count` va `attempt_count` jonli yo'lda to'g'ri yuritiladi (AC da
oshadi, rejudge da kamayadi), lekin qatorlar kodni chetlab yo'qolganda
o'sha joyda qotib qoladi: foydalanuvchi o'chirilsa `UserSolvedProblem`
kaskad bilan ketadi, sanoq esa qolaveradi. O'lchandi — bitta
foydalanuvchini o'chirish arxivdagi «N kishi yechgan» ni doimiy ravishda
bittaga oshirib yuborardi.

Haqiqat manbai — `UserSolvedProblem` va `Attempt` jadvallari.
"""

from __future__ import annotations

from argparse import ArgumentParser
from typing import Any

from django.core.management.base import BaseCommand
from django.db.models import Count

from problems.models import Problem


class Command(BaseCommand):
    help = "Masalalardagi solved_count va attempt_count ni qayta hisoblaydi."

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--dry-run", action="store_true", help="Faqat farqni ko'rsatadi")

    def handle(self, *args: Any, **options: Any) -> None:
        solved = dict(
            Problem.objects.annotate(n=Count("solvers", distinct=True)).values_list("pk", "n")
        )
        attempts = dict(
            Problem.objects.annotate(n=Count("attempts", distinct=True)).values_list("pk", "n")
        )

        stale = []
        for problem in Problem.objects.all().only("pk", "solved_count", "attempt_count"):
            want_solved = solved.get(problem.pk, 0)
            want_attempts = attempts.get(problem.pk, 0)
            if (problem.solved_count, problem.attempt_count) == (want_solved, want_attempts):
                continue
            self.stdout.write(
                f"  #{problem.pk}: yechgan {problem.solved_count}→{want_solved}, "
                f"urinish {problem.attempt_count}→{want_attempts}"
            )
            problem.solved_count = want_solved
            problem.attempt_count = want_attempts
            stale.append(problem)

        if options["dry_run"]:
            self.stdout.write(f"(dry-run) {len(stale)} ta masala tuzatilishi kerak")
            return

        Problem.objects.bulk_update(stale, ["solved_count", "attempt_count"], batch_size=500)
        self.stdout.write(self.style.SUCCESS(f"{len(stale)} ta masala sanog'i tuzatildi"))
