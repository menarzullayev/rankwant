"""Import qilingan masalalar qiyinligini manba reytingidan qayta hisoblaydi.

Ishlatish:  python manage.py remap_difficulty

Xaritalash formulasi o'zgarganda kerak bo'ladi. Tarmoqqa CHIQMAYDI:
`source_rating` bazada saqlangani uchun arxivni qaytadan yuklash shart
emas.
"""

from __future__ import annotations

from argparse import ArgumentParser
from typing import Any

from django.core.management.base import BaseCommand

from core.models import User
from problems import kep
from problems.models import Problem
from ratings.models import RatingHistory, UserSolvedProblem
from ratings.services import recalc_skills


class Command(BaseCommand):
    help = "Qiyinlikni `source_rating` dan qayta hisoblaydi."

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--dry-run", action="store_true", help="Faqat ko'rsatadi")

    def handle(self, *args: Any, **options: Any) -> None:
        changed = []
        for problem in Problem.objects.exclude(source_rating=None).only(
            "pk", "difficulty", "source_rating"
        ):
            value = kep.map_difficulty(problem.source_rating)
            if value != problem.difficulty:
                problem.difficulty = value
                changed.append(problem)

        if options["dry_run"]:
            self.stdout.write(f"(dry-run) {len(changed)} masala qiyinligi o'zgarardi")
            return

        # `save()` EMAS: u e'lon qilingan masalaga raqam berish bilan
        # shug'ullanadi va bu yerda unga hojat yo'q.
        Problem.objects.bulk_update(changed, ["difficulty"], batch_size=500)
        self.stdout.write(self.style.SUCCESS(f"{len(changed)} masala qiyinligi qayta hisoblandi"))

        # ADR-0007: Skills JORIY qiyinlikdan hisoblanadi, ya'ni qiyinlik
        # o'zgarishi uni yechganlarning reytingini eskirtiradi. Masala
        # boshiga emas, FOYDALANUVCHI boshiga qayta hisoblanadi: bitta
        # odam yuzlab qayta baholangan masalani yechgan bo'lishi mumkin
        # va har biri uchun alohida hisoblash o'sha ishni takrorlardi.
        user_ids = set(
            UserSolvedProblem.objects.filter(problem_id__in=[p.pk for p in changed]).values_list(
                "user_id", flat=True
            )
        )
        for user in User.objects.filter(pk__in=user_ids).iterator(chunk_size=500):
            recalc_skills(user, reason=RatingHistory.Reason.PROBLEM_RERATED)
        self.stdout.write(self.style.SUCCESS(f"{len(user_ids)} foydalanuvchi Skills'i yangilandi"))
