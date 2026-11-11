"""Problems a user owns count against the plan (ADR-0061 § 2)."""

from __future__ import annotations

from typing import Any

from core import quotas


def _problems(user: Any) -> int:
    return int(user.authored_problems.count())


quotas.register("problems", _problems)


def _storage_mb(user: Any) -> int:
    from problems.generation import storage_used_mb

    return storage_used_mb(user)


# Generated test data counts against the plan (ADR-0061 § 6).
quotas.register("storage_mb", _storage_mb)
