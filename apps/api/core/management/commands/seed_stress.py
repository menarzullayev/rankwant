"""Stress sinovi uchun sun'iy foydalanuvchilar — «neytron»lar.

Ishlatish:
    python manage.py seed_stress --users 10000
    python manage.py seed_stress --users 500 --password 'Sinov!12345'
    python manage.py prune_test_users --prefix neytron

Nega kerak: sakkizta hisob bilan reyting jadvali, profil o'rni va
sahifalash haqiqiy yuk ostida qanday ishlashini bilib bo'lmaydi.

Nomi ataylab: `Qvant` valyutasi bilan bitta olamdan, va prefiks
`neytron_` bo'lgani uchun ularni bir buyruq bilan yo'q qilish mumkin.
"""

from __future__ import annotations

import random
from argparse import ArgumentParser
from typing import Any

from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand, CommandError

from core.models import User

PREFIX = "neytron"

#: Reyting taqsimoti haqiqiyga yaqin bo'lishi kerak: hammasi bir xil
#: bo'lsa saralash va o'rin hisoblash yuki soxta bo'lardi.
SKILLS_MEAN, SKILLS_SIGMA = 1200, 700
CONTEST_MEAN, CONTEST_SIGMA = 1400, 250


class Command(BaseCommand):
    help = "Stress sinovi uchun `neytron` foydalanuvchilarini yaratadi."

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--users", type=int, default=10_000)
        parser.add_argument(
            "--password",
            default="",
            help="Berilsa hammasi shu parol bilan kira oladi. Berilmasa — kira olmaydi.",
        )
        parser.add_argument("--seed", type=int, default=0, help="Takrorlanadigan tasodif")

    def handle(self, *args: Any, **options: Any) -> None:
        count: int = options["users"]
        if count < 1:
            raise CommandError("--users musbat bo'lishi kerak")

        rng = random.Random(options["seed"])
        # Parol BIR MARTA heshlanadi: 10 000 marta PBKDF2 soatlab
        # ishlagan bo'lardi. `make_password(None)` — Django ning
        # «kirib bo'lmaydi» shakli; bo'sh satr YARAMAYDI, chunki
        # `has_usable_password()` uni yaroqli deb hisoblaydi.
        password = make_password(options["password"] or None)

        existing = set(
            User.objects.filter(username__startswith=f"{PREFIX}_").values_list(
                "username", flat=True
            )
        )
        rows = []
        for index in range(1, count + 1):
            username = f"{PREFIX}_{index:06d}"
            if username in existing:
                continue
            rows.append(
                User(
                    username=username,
                    password=password,
                    display_name=f"Neytron {index}",
                    rating_skills=max(0, int(rng.gauss(SKILLS_MEAN, SKILLS_SIGMA))),
                    rating_contest=max(0, int(rng.gauss(CONTEST_MEAN, CONTEST_SIGMA))),
                    rating_activity=rng.randint(0, 100),
                    rating_challenges=max(0, int(rng.gauss(CONTEST_MEAN, CONTEST_SIGMA))),
                    streak_count=rng.randint(0, 60),
                )
            )

        User.objects.bulk_create(rows, batch_size=1000)
        note = "parol bilan" if options["password"] else "parolsiz (kira olmaydi)"
        self.stdout.write(self.style.SUCCESS(f"{len(rows)} ta {PREFIX} yaratildi — {note}"))
        if len(rows) < count:
            self.stdout.write(f"({count - len(rows)} tasi allaqachon bor edi)")
