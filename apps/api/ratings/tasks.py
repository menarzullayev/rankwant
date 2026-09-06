from __future__ import annotations

from celery import shared_task

from ratings.services import recalc_skills_for_problem


@shared_task(name="ratings.recalc_skills_for_problem")
def recalc_skills_for_problem_task(problem_id: int) -> int:
    """Masala qiyinligi o'zgarganda — ADR-0007.

    Partiyada ishlaydi; `UserSolvedProblem(problem_id)` indeksi shart.
    """
    return recalc_skills_for_problem(problem_id)
