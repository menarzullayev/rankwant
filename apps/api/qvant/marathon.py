"""Haftalik marafon — PRD P1-9, ADR-0002 (+100 Qvant, haftada bir marta).

Marafon = har hafta avtomatik tanlanadigan masalalar to'plami. Alohida
model kerak emas: to'plam determinlashgan tarzda hafta kalitidan
hosil qilinadi, ya'ni bir haftada hamma bir xil masalalarni oladi va
tarixni qayta hisoblash mumkin.
"""

from __future__ import annotations

import hashlib
import random
from datetime import date

from django.utils import timezone

from core.models import User
from problems.models import Problem
from qvant import quests

MARATHON_SIZE = 10
MARATHON_QUEST = "weekly_marathon"
MARATHON_REWARD = 100


def week_seed(when: date | None = None) -> int:
    """Hafta kalitidan barqaror urug'.

    `hash()` ishlatilmaydi: u jarayonlar orasida turlicha bo'ladi
    (PYTHONHASHSEED), ya'ni ikki server ikki xil to'plam ko'rsatardi.
    """
    key = quests.week_key(when)
    return int(hashlib.sha256(key.encode()).hexdigest()[:8], 16)


def marathon_problems(when: date | None = None) -> list[Problem]:
    """Shu haftaning masalalari — barcha foydalanuvchi uchun bir xil."""
    ids = list(Problem.objects.filter(is_public=True).order_by("pk").values_list("pk", flat=True))
    # Arxivda MARATHON_SIZE dan kam masala bo'lsa marafon YO'Q: aks holda
    # "10 masalali marafon" bitta masalani yechish bilan yakunlanib,
    # +100 Qvant tekinga berilardi.
    if len(ids) < MARATHON_SIZE:
        return []

    # Determinlashgan aralashtirish: bir haftada hamma bir xil to'plamni
    # ko'radi va tarixni qayta hisoblash mumkin. `random.Random(seed)`
    # ishlatiladi, `hash()` emas — u jarayonlar orasida turlicha.
    rng = random.Random(week_seed(when))
    chosen = rng.sample(ids, MARATHON_SIZE)
    return list(Problem.objects.filter(pk__in=chosen).order_by("difficulty"))


def solved_this_week(user: User, when: date | None = None) -> set[int]:
    """Shu hafta marafon masalalaridan nechtasi yechilgan."""
    from ratings.models import UserSolvedProblem

    target = when or timezone.localdate()
    year, week, _ = target.isocalendar()
    week_start = date.fromisocalendar(year, week, 1)

    problem_ids = [p.pk for p in marathon_problems(target)]
    return set(
        UserSolvedProblem.objects.filter(
            user=user, problem_id__in=problem_ids, first_ac_at__date__gte=week_start
        ).values_list("problem_id", flat=True)
    )


def check_completion(user: User) -> int:
    """Marafon yakunlangan bo'lsa mukofot beradi. Qaytaradi: Qvant."""
    problems = marathon_problems()
    if not problems:
        return 0
    if len(solved_this_week(user)) < len(problems):
        return 0
    return quests.award(user, MARATHON_QUEST, quests.week_key(), ref_id="marathon")
