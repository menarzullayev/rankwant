"""Testsiz masalalarni arxivdan qoralamaga qaytaradi.

Ishlatish:
    python manage.py unpublish_testless --dry-run
    python manage.py unpublish_testless

Testsiz masala ochiladi, yechim yuboriladi va `WRONG_TEST` qaytadi —
foydalanuvchi buni platforma nosozligi deb qabul qiladi, holbuki masala
shunchaki tayyor emas. O'lchandi: import qilingan arxivda 2 096 ommaviy
masaladan 870 tasi (41%) shu holatda edi.

Qaytarish xavfsiz: `Problem.code` faqat e'lon qilinganda beriladi va
hech qachon tozalanmaydi, ya'ni test qo'shilib qayta e'lon qilinganda
masala O'SHA raqamini oladi va tarqalgan havolalar buzilmaydi.

Teskarisi — `publish_problems`, u endi testsizlarni o'zi o'tkazib
yuboradi.
"""

from __future__ import annotations

from argparse import ArgumentParser
from typing import Any

from django.core.management.base import BaseCommand
from django.db.models import Count

from problems.models import Problem


class Command(BaseCommand):
    help = "Testi yo'q ommaviy masalalarni qoralamaga qaytaradi."

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args: Any, **options: Any) -> None:
        rows = Problem.objects.annotate(n=Count("tests")).filter(n=0, is_public=True)
        jami = rows.count()
        ommaviy = Problem.objects.filter(is_public=True).count()
        self.stdout.write(f"Testsiz ommaviy masala: {jami} / {ommaviy}")
        if not jami:
            return

        yechilgan = rows.filter(solved_count__gt=0).count()
        if yechilgan:
            # Bu yozuvlar seed'dan: judge nol testni AC deb emas, WRONG_TEST
            # deb qaytaradi, ya'ni ularni haqiqiy odam yecha olmagan.
            self.stdout.write(
                self.style.WARNING(f"  ulardan {yechilgan} tasida yechuvchi ko'rinadi")
            )

        for problem in rows.order_by("pk")[:5]:
            self.stdout.write(f"  masalan: {problem.slug} (#{problem.code})")
        if jami > 5:
            self.stdout.write(f"  … va yana {jami - 5} ta")

        if options["dry_run"]:
            self.stdout.write(self.style.WARNING("(dry-run) hech narsa o'zgarmadi"))
            return

        # `update()` yetarli: raqam allaqachon berilgan, `save()` esa faqat
        # e'lon qilishda kerak.
        n = Problem.objects.filter(pk__in=list(rows.values_list("pk", flat=True))).update(
            is_public=False
        )
        self.stdout.write(
            self.style.SUCCESS(f"{n} masala qoralamaga qaytarildi — arxivda {ommaviy - n} ta qoldi")
        )
