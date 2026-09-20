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
#:
#: Measured against Codeforces (2026-09-20). The two means answer two
#: different questions, which is why they sit further apart than the sigma
#: suggests:
#:
#:   general rated population   974,498 users   mean 1,015  (min -53, max 3,810)
#:   contest participants        35,538 users   mean 1,332  (p25 1,065, p75 1,564)
#:
#: `CONTEST_MEAN` models the second group — people who actually turn up to a
#: contest, who are measurably stronger than the population at large. Pulling
#: it down to the 1,015 population mean would understate contest load and
#: flatten the leaderboard spread the load test depends on. `SKILLS_MEAN` is
#: the softer, wider axis and keeps a round 1,200.
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
        parser.add_argument(
            "--attempts",
            type=int,
            default=0,
            help="Har foydalanuvchiga o'rtacha urinish. 0 — faqat hisob yaratiladi.",
        )

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

        if options["attempts"]:
            self.seed_attempts(rng, options["attempts"])

    def seed_attempts(self, rng: random.Random, per_user: int) -> None:
        """Urinish va yechilgan masalalar.

        Hisobning o'zi arxiv, statistika va yechganlar bo'limini
        sinamaydi — ular URINISHGA tayanadi. Masala mashhurligi
        ataylab notekis: haqiqiy arxivda bir nechta masala minglab
        urinish oladi, qolganlari bir nechtadan, va aynan o'sha
        gavjum masala cho'kish nuqtasi bo'ladi.
        """
        from django.db.models import Count, Q

        from judging.models import Attempt
        from problems.models import Language, Problem
        from ratings.models import UserSolvedProblem

        languages = list(Language.objects.filter(is_active=True))
        problems = list(
            Problem.objects.filter(is_public=True, tests__isnull=False)
            .distinct()
            .values_list("pk", flat=True)
        )
        users = list(
            User.objects.filter(username__startswith=f"{PREFIX}_").values_list("pk", flat=True)
        )
        if not (languages and problems and users):
            raise CommandError("Til, testli masala yoki foydalanuvchi topilmadi")

        # Zipf: birinchi masalalar eng gavjum bo'ladi.
        weights = [1 / (i + 1) ** 0.8 for i in range(len(problems))]
        source = "int main(){return 0;}\n"

        attempts: list[Attempt] = []
        solved: set[tuple[int, int]] = set()
        for user_id in users:
            for _ in range(max(0, int(rng.gauss(per_user, per_user / 2)))):
                problem_id = rng.choices(problems, weights=weights, k=1)[0]
                verdict = rng.choices(
                    ["AC", "WA", "TLE", "RE", "CE"], weights=[30, 40, 15, 10, 5], k=1
                )[0]
                attempts.append(
                    Attempt(
                        user_id=user_id,
                        problem_id=problem_id,
                        language=rng.choice(languages),
                        source_code=source,
                        # `bulk_create` `save()` ni chetlab o'tadi — hisoblab
                        # qo'yamiz, aks holda ustun nolda qolardi.
                        source_size=len(source.encode()),
                        verdict=verdict,
                        time_ms=rng.randint(1, 900),
                        memory_kb=rng.randint(1024, 65536),
                    )
                )
                if verdict == "AC":
                    solved.add((user_id, problem_id))

        Attempt.objects.bulk_create(attempts, batch_size=2000)
        UserSolvedProblem.objects.bulk_create(
            [
                UserSolvedProblem(user_id=u, problem_id=p, difficulty_at_solve=800)
                for u, p in solved
            ],
            batch_size=2000,
            ignore_conflicts=True,
        )

        # Denormallashtirilgan sanoqlar — aks holda arxivda hamma joyda
        # nol turardi va ro'yxat soxta ko'rinardi.
        # `solved_count` — YECHGAN ODAMLAR soni, AC urinishlar soni emas
        # (jonli kodda u birinchi AC da bir marta oshadi). Shu sababli
        # `attempts__user` bo'yicha distinct.
        counts = Problem.objects.filter(is_public=True).annotate(
            n=Count("attempts", distinct=True),
            ac=Count("attempts__user", filter=Q(attempts__verdict="AC"), distinct=True),
        )
        updates = []
        for problem in counts:
            problem.attempt_count = problem.n
            problem.solved_count = problem.ac
            updates.append(problem)
        Problem.objects.bulk_update(updates, ["attempt_count", "solved_count"], batch_size=500)

        self.stdout.write(
            self.style.SUCCESS(f"{len(attempts)} urinish, {len(solved)} yechilgan masala yozildi")
        )
