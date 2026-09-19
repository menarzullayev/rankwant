"""Sinf a'zoligi va progress."""

from __future__ import annotations

from django.db import transaction

from classroom.models import Assignment, Classroom, ClassroomMember
from core.models import User


class ClassroomError(Exception):
    """Sinf amali bajarilmadi."""


@transaction.atomic
def join(user: User, join_code: str) -> ClassroomMember:
    try:
        classroom = Classroom.objects.select_for_update().get(join_code=join_code, is_active=True)
    except Classroom.DoesNotExist:
        raise ClassroomError("Classroom not found or inactive") from None

    if classroom.owner_id == user.pk:
        raise ClassroomError("You already own this classroom")
    if classroom.members.count() >= Classroom.MAX_MEMBERS:
        raise ClassroomError(f"Classroom is full (max {Classroom.MAX_MEMBERS})")

    member, _ = ClassroomMember.objects.get_or_create(classroom=classroom, user=user)
    return member


def assignment_progress(assignment: Assignment) -> list[dict[str, object]]:
    """Har o'quvchi bo'yicha nechta masala yechilgan.

    `UserSolvedProblem` dan o'qiydi: uy vazifasi uchun ALOHIDA yechilganlik
    hisobi yuritilmaydi — bir masalani ikki marta yechib bo'lmaydi va
    ikkita haqiqat manbai bo'lishi kerak emas.
    """
    from django.db.models import Count

    from ratings.models import UserSolvedProblem

    problem_ids = list(assignment.problems.values_list("pk", flat=True))
    total = len(problem_ids)
    members = list(assignment.classroom.members.select_related("user"))
    if not problem_ids or not members:
        return [{"username": m.user.username, "solved": 0, "total": total} for m in members]

    counts = dict(
        UserSolvedProblem.objects.filter(
            user_id__in=[m.user_id for m in members], problem_id__in=problem_ids
        )
        .values_list("user_id")
        .annotate(n=Count("pk"))
        .values_list("user_id", "n")
    )

    return [
        {
            "username": m.user.username,
            "solved": counts.get(m.user_id, 0),
            "total": total,
        }
        for m in members
    ]
