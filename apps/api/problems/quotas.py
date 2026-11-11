"""Problems a user owns count against the plan (ADR-0061 § 2)."""

from __future__ import annotations

from typing import Any

from core import quotas


def _problems(user: Any) -> int:
    return int(user.authored_problems.count())


quotas.register("problems", _problems)
