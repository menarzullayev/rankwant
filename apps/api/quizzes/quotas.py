"""A teacher's quizzes count against the plan (ADR-0061 § 2, § 5)."""

from __future__ import annotations

from typing import Any

from core import quotas
from quizzes.models import Quiz


def _quizzes(user: Any) -> int:
    return Quiz.objects.filter(owner=user).count()


quotas.register("quizzes", _quizzes)
