"""A user's latest attempts as plain rows, for other apps' dashboards."""

from __future__ import annotations

from typing import Any

from judging.models import Attempt


def recent_attempts(user_id: int, limit: int = 5) -> list[dict[str, Any]]:
    rows = (
        Attempt.objects.filter(user_id=user_id)
        .select_related("problem", "language")
        .order_by("-created_at")[:limit]
    )
    return [
        {
            "id": row.pk,
            "problem": row.problem.slug,
            "problem_title": row.problem.title,
            "language": row.language.name,
            "verdict": row.verdict,
            "in_contest": row.contest_id is not None,
            "created_at": row.created_at,
        }
        for row in rows
    ]
