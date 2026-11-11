"""Active classrooms a user owns count against the plan (ADR-0061 § 3).

An archived classroom does not: archiving is how a teacher frees a place.
"""

from __future__ import annotations

from typing import Any

from classroom.models import Classroom
from core import quotas


def _classrooms(user: Any) -> int:
    return Classroom.objects.filter(owner=user, is_active=True).count()


quotas.register("classrooms", _classrooms)
