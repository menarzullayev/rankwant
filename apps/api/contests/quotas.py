"""Contests a user organizes count against the plan (ADR-0061 § 2)."""

from __future__ import annotations

from typing import Any

from core import quotas


def _contests(user: Any) -> int:
    return int(user.organized_contests.count())


quotas.register("contests", _contests)
