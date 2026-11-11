"""Whether a coach may open a student's solution code (ADR-0061 § 4).

Other apps ask here instead of reading `coaching.models` (ADR-0042).
"""

from __future__ import annotations

from typing import Any

from coaching.models import CoachLink


def coach_may_read(viewer: Any, student_id: int) -> bool:
    """An ACTIVE coach of this student, with the student's consent for them."""
    if viewer is None or not getattr(viewer, "is_authenticated", False):
        return False
    return CoachLink.objects.filter(
        coach_id=viewer.pk,
        student_id=student_id,
        status=CoachLink.Status.ACTIVE,
        can_view_attempts=True,
    ).exists()


def coaches_of(student_id: int) -> list[Any]:
    """The student's active coaches, for the profile."""
    from core.models import User

    return list(
        User.objects.filter(
            coached_links__student_id=student_id,
            coached_links__status=CoachLink.Status.ACTIVE,
            is_active=True,
        ).order_by("username")
    )
