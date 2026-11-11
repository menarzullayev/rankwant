"""Which classrooms a user sits in or owns, for other apps (ADR-0042)."""

from __future__ import annotations

from typing import Any

from django.db.models import Q, QuerySet

from classroom.models import Classroom


def classes_of(user: Any) -> QuerySet[Classroom]:
    """Active classrooms the user owns or is a member of."""
    return Classroom.objects.filter(
        Q(owner=user) | Q(members__user=user), is_active=True
    ).distinct()
