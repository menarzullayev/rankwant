"""Test foydalanuvchilarini bazadan olib tashlaydi.

Ishlatish:
    python manage.py prune_test_users --prefix e2e --dry-run
    python manage.py prune_test_users --prefix e2e

Nega buyruq: stress sinovi minglab hisob yaratadi va ularni har safar
qo'lda o'chirish xavfli. Bu yerda chegara ANIQ — faqat berilgan
prefiksdagi, xodim bo'lmagan hisoblar.
"""

from __future__ import annotations

from argparse import ArgumentParser
from typing import Any

from django.core.management.base import BaseCommand, CommandError
from django.db import router
from django.db.models.deletion import Collector

from core.models import User


class Command(BaseCommand):
    help = "Berilgan prefiksdagi test hisoblarini o'chiradi."

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--prefix", required=True, help="Username boshlanishi, masalan `e2e`")
        parser.add_argument("--dry-run", action="store_true", help="Faqat sanaydi")

    def handle(self, *args: Any, **options: Any) -> None:
        prefix: str = options["prefix"].strip()
        if len(prefix) < 3:
            # Qisqa prefiks tasodifan haqiqiy hisobni ham qamrab olardi.
            raise CommandError("Prefiks kamida 3 belgidan iborat bo'lishi kerak")

        # Xodim va superuser HECH QACHON o'chirilmaydi: nomi mos kelib
        # qolgan admin bilan birga kirish huquqi ham yo'qolardi.
        victims = (
            User.objects.filter(username__startswith=prefix)
            .exclude(is_staff=True)
            .exclude(is_superuser=True)
        )
        if not victims.exists():
            self.stdout.write("Mos hisob topilmadi")
            return

        collector = Collector(using=router.db_for_write(User))
        collector.collect(list(victims))
        for model, objects in sorted(collector.data.items(), key=lambda kv: kv[0].__name__):
            self.stdout.write(f"  {model._meta.label:34} {len(objects)}")

        if options["dry_run"]:
            self.stdout.write("(dry-run — hech narsa o'chirilmadi)")
            return

        removed = victims.count()
        victims.delete()
        self.stdout.write(self.style.SUCCESS(f"{removed} test hisobi o'chirildi"))
