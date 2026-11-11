"""Plan quotas (ADR-0061 § 2): how much an author may own.

`limit()` answers for one user and one kind of thing. What the user already
owns is counted by the app that owns the rows: it registers a counter in its
own `quotas.py` (`core` must not import a feature app's models — see
`tools/check_architecture.py`) and `CoreConfig.ready()` discovers them, as it
does for `nav_badges.py`. `enforce()` counts and refuses one more; `usage()`
is what `/me/quotas/` shows. The numbers live in `core.PlanQuota` (admin);
`DEFAULTS` is used until a row exists.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from django.utils import timezone

KEYS = ("problems", "contests", "quizzes", "classrooms", "class_members", "storage_mb")

_FREE = {
    "problems": 20,
    "contests": 5,
    "quizzes": 3,
    "classrooms": 3,
    "class_members": 40,
    "storage_mb": 200,
}
#: Owner decision 2026-11-11 (plan contents, teacher tools round 4).
DEFAULTS: dict[str, dict[str, int]] = {
    "free": _FREE,
    "plus": _FREE,
    "pro": _FREE,
    "judge": {
        "problems": 2000,
        "contests": 100,
        "quizzes": 50,
        "classrooms": 50,
        "class_members": 50,
        "storage_mb": 4096,
    },
}


class QuotaExceeded(Exception):
    """The user already owns as many as the plan allows."""

    def __init__(self, key: str, limit: int) -> None:
        super().__init__(f"Your plan allows {limit} ({key})")
        self.key = key
        self.limit = limit

    def as_error(self) -> dict[str, Any]:
        """The API error body, one shape for every app."""
        return {
            "error": {
                "code": "quota_exceeded",
                "message": str(self),
                "details": {"quota": self.key, "limit": self.limit},
            }
        }


def plan_of(user: Any) -> str:
    """The plan in force: an expired one counts as free."""
    plan = getattr(user, "plan", "free") or "free"
    expires = getattr(user, "plan_expires_at", None)
    if plan != "free" and expires is not None and expires <= timezone.now():
        return "free"
    return str(plan)


def limit(user: Any, key: str) -> int | None:
    """How many `key` the user may own; `None` — no limit (staff)."""
    if key not in KEYS:
        raise KeyError(key)
    if getattr(user, "is_staff", False):
        return None
    from core.models import PlanQuota

    plan = plan_of(user)
    row = PlanQuota.objects.filter(plan=plan).values(key).first()
    if row is not None:
        return int(row[key])
    return DEFAULTS.get(plan, _FREE)[key]


def check(user: Any, key: str, owned: int) -> None:
    """Refuse one more when `owned` already reaches the limit."""
    allowed = limit(user, key)
    if allowed is not None and owned >= allowed:
        raise QuotaExceeded(key, allowed)


#: key → counts what the user owns now. Every owned row counts, published or
#: not (owner decision 2026-11-11: counting drafts only would empty the plan).
_COUNTERS: dict[str, Callable[[Any], int]] = {}


def register(key: str, count: Callable[[Any], int]) -> None:
    if key not in KEYS:
        raise KeyError(key)
    if key in _COUNTERS:
        raise ValueError(f"quota counter registered twice: {key}")
    _COUNTERS[key] = count


def owned(user: Any, key: str) -> int:
    return _COUNTERS[key](user)


def enforce(user: Any, key: str) -> None:
    """Refuse a new one past the plan. Staff are not counted at all."""
    if limit(user, key) is None:
        return
    check(user, key, owned(user, key))


def usage(user: Any) -> list[dict[str, Any]]:
    """Each counted kind: `limit` (`None` — none) and how many are `used`."""
    return [
        {"key": key, "limit": limit(user, key), "used": owned(user, key)}
        for key in KEYS
        if key in _COUNTERS
    ]
