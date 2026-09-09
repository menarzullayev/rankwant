"""Qoralama masalalarni ommaga chiqaradi.

Ishlatish:  python manage.py publish_problems --source KEP.uz

`update(is_public=True)` QILMAYDI: ommaviy raqam `Problem.save()` da
beriladi va to'g'ridan-to'g'ri UPDATE uni chetlab o'tib, raqamsiz
masalalar qoldirardi.
"""

from __future__ import annotations

from argparse import ArgumentParser
from typing import Any

from django.core.management.base import BaseCommand

from problems.models import Problem


class Command(BaseCommand):
    help = "Qoralama masalalarni e'lon qiladi va ularga ommaviy raqam beradi."

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--source", default="", help="Faqat shu manbadagilar")
        parser.add_argument(
            "--require-tests",
            action="store_true",
            help="Testsizlarini qoralama qoldiradi",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        drafts = Problem.objects.filter(is_public=False)
        if options["source"]:
            drafts = drafts.filter(source=options["source"])
        if options["require_tests"]:
            drafts = drafts.filter(tests__isnull=False).distinct()

        # Raqamlar YARATILISH tartibida beriladi. `source_url` bo'yicha
        # saralash noto'g'ri bo'lardi — u satr, ya'ni `.../10` `.../2` dan
        # oldin kelardi.
        published = 0
        for problem in drafts.order_by("pk"):
            problem.is_public = True
            problem.save()
            published += 1

        self.stdout.write(self.style.SUCCESS(f"{published} masala e'lon qilindi"))
