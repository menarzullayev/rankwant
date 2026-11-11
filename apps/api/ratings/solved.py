"""Which problems a user has solved, for other apps (they may not read `ratings.models`)."""

from __future__ import annotations

from collections.abc import Iterable

from ratings.models import UserSolvedProblem


def solved_ids(user_id: int, problem_ids: Iterable[int]) -> set[int]:
    ids = list(problem_ids)
    if not ids:
        return set()
    return set(
        UserSolvedProblem.objects.filter(user_id=user_id, problem_id__in=ids).values_list(
            "problem_id", flat=True
        )
    )
