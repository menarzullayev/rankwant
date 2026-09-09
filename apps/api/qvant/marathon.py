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


def week_start(when: date | None = None) -> date:
    year, week, _ = (when or timezone.localdate()).isocalendar()
    return date.fromisocalendar(year, week, 1)


def week_seed(user: User, when: date | None = None) -> int:
    """Hafta va foydalanuvchidan barqaror urug'.

    `hash()` ishlatilmaydi: u jarayonlar orasida turlicha bo'ladi
    (PYTHONHASHSEED), ya'ni ikki server ikki xil to'plam ko'rsatardi.
    """
    key = f"{quests.week_key(when)}:{user.pk}"
    return int(hashlib.sha256(key.encode()).hexdigest()[:8], 16)


def marathon_problems(user: User, when: date | None = None) -> list[Problem]:
    """Foydalanuvchining shu haftalik marafoni.

    To'plam HAFTA BOSHIGA mahkamlangan: tanlov «hafta boshida yechilmagan
    edi» sharti bo'yicha qilinadi, «hozir yechilmagan» bo'yicha emas.
    Aks holda foydalanuvchi masalani yechishi bilan u to'plamdan chiqib
    ketardi va marafon hech qachon tugamasdi.

    To'plam har kimga alohida: umumiy to'plamda oldin yechilgan bitta
    masala butun haftani qulflab qo'yardi — o'lchandi, 700 ta masala
    yechgan foydalanuvchining marafonni yakunlash imkoni 1.7 % edi.
    """
    from ratings.models import UserSolvedProblem

    start = week_start(when)
    already = UserSolvedProblem.objects.filter(user=user, first_ac_at__date__lt=start).values(
        "problem_id"
    )
    ids = list(
        Problem.objects.filter(is_public=True)
        .exclude(pk__in=already)
        .order_by("pk")
        .values_list("pk", flat=True)
    )
    # Yechilmagan masala MARATHON_SIZE dan kam bo'lsa marafon YO'Q: aks
    # holda "10 masalali marafon" bittasini yechish bilan yakunlanib,
    # +100 Qvant tekinga berilardi.
    if len(ids) < MARATHON_SIZE:
        return []

    rng = random.Random(week_seed(user, when))
    chosen = rng.sample(ids, MARATHON_SIZE)
    return list(Problem.objects.filter(pk__in=chosen).order_by("difficulty"))


def solved_this_week(user: User, when: date | None = None) -> set[int]:
    """Marafon masalalaridan shu hafta yechilganlari."""
    from ratings.models import UserSolvedProblem

    problem_ids = [p.pk for p in marathon_problems(user, when)]
    return set(
        UserSolvedProblem.objects.filter(
            user=user, problem_id__in=problem_ids, first_ac_at__date__gte=week_start(when)
        ).values_list("problem_id", flat=True)
    )


def check_completion(user: User) -> int:
    """Marafon yakunlangan bo'lsa mukofot beradi. Qaytaradi: Qvant."""
    problems = marathon_problems(user)
    if not problems:
        return 0
    if len(solved_this_week(user)) < len(problems):
        return 0
    return quests.award(user, MARATHON_QUEST, quests.week_key(), ref_id="marathon")
