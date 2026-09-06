"""Masala tavsiyasi — PRD P1-2.

Yondashuv ataylab sodda va TUSHUNTIRILADIGAN: foydalanuvchi darajasiga
yaqin, hali yechmagan masalalari. Murakkab tavsiya modeli (collaborative
filtering) bu bosqichda asossiz — 0 foydalanuvchida o'rgatadigan
ma'lumot yo'q, va «nega bu masala?» savoliga javob berish qiyinlashadi.
"""

from __future__ import annotations

from django.db.models import QuerySet

from core.models import User
from problems.models import DIFFICULTY_MAX, DIFFICULTY_MIN, Problem

#: Skills reyting → maqsad qiyinlik. Skills yig'indi bo'lgani uchun
#: to'g'ridan-to'g'ri qiyinlik emas — eng qiyin yechilgan masaladan
#: boshlaymiz, u foydalanuvchi darajasini aniqroq ko'rsatadi.
STEP_UP = 100
WINDOW = 300


def target_difficulty(user: User) -> int:
    """Foydalanuvchining keyingi qadami."""
    from ratings.models import UserSolvedProblem

    hardest = (
        UserSolvedProblem.objects.filter(user=user)
        .order_by("-problem__difficulty")
        .values_list("problem__difficulty", flat=True)
        .first()
    )
    if hardest is None:
        return DIFFICULTY_MIN
    return min(DIFFICULTY_MAX, hardest + STEP_UP)


def recommend(user: User, limit: int = 10) -> QuerySet[Problem]:
    """Yechilmagan, darajaga yaqin masalalar.

    Tartib: maqsad qiyinlikka yaqinligi, keyin ommaboplik.
    """
    from ratings.models import UserSolvedProblem

    target = target_difficulty(user)
    solved = UserSolvedProblem.objects.filter(user=user).values_list("problem_id", flat=True)

    return (
        Problem.objects.filter(
            is_public=True,
            difficulty__gte=max(DIFFICULTY_MIN, target - WINDOW),
            difficulty__lte=min(DIFFICULTY_MAX, target + WINDOW),
        )
        .exclude(pk__in=solved)
        .order_by("-solved_count", "difficulty")[:limit]
    )
