"""Yakunlangan rasmiy musobaqalar uchun sertifikatlar — bir martalik to'ldirish.

Yangi musobaqada sertifikat `finalize` da o'zi beriladi; bu buyruq undan
oldin yakunlanganlar uchun. Takroriy ishga tushirish xavfsiz.
"""

from __future__ import annotations

from typing import Any

from django.core.management.base import BaseCommand

from contests.certificates import issue
from contests.models import Contest


class Command(BaseCommand):
    help = "Yakunlangan rasmiy musobaqalar uchun sertifikat beradi (takrorlash xavfsiz)."

    def handle(self, *args: Any, **options: Any) -> None:
        total = sum(
            issue(contest)
            for contest in Contest.objects.filter(
                ratings_applied_at__isnull=False, is_public=True, is_virtual=False
            )
        )
        self.stdout.write(self.style.SUCCESS(f"{total} ta ishtirokchi tekshirildi"))
