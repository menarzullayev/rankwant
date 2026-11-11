"""Reports about problems a person wrote, for "My content" (decision 2026-11-11 ④)."""

from __future__ import annotations

from typing import Any

from problems.models import ProblemReport


def for_author(user_id: int, limit: int = 200) -> list[dict[str, Any]]:
    """Reports on the author's problems, newest first. The reporter is not
    named: the author fixes the problem, not the person."""
    rows = (
        ProblemReport.objects.filter(problem__authors__id=user_id)
        .select_related("problem")
        .order_by("-created_at")[:limit]
    )
    return [
        {
            "kind": "problem",
            "title": row.problem.title,
            "link": f"/problems/{row.problem.slug}",
            "reason": row.reason,
            "note": row.comment,
            "status": row.status,
            "created_at": row.created_at,
        }
        for row in rows
    ]
