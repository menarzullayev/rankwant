"""Whether a user's paid plan opens paid courses (ADR-0057).

Read from `User.plan` / `plan_expires_at`, which `billing` keeps in step
with the user's subscriptions. Courses never import `billing`: the plan on
the user record is the one fact they need, and an expiry time is checked
here at read time, so a lapsed plan closes its courses without waiting for
the periodic sync.
"""

from __future__ import annotations

from typing import Any

from django.utils import timezone

#: Owner decision 2026-11-10: Pro opens every paid course; Judge includes Pro.
PLANS_WITH_COURSES = frozenset({"pro", "judge"})


def plan_covers_courses(user: Any) -> bool:
    if not getattr(user, "is_authenticated", False):
        return False
    expires = getattr(user, "plan_expires_at", None)
    return (
        getattr(user, "plan", "free") in PLANS_WITH_COURSES
        and expires is not None
        and expires > timezone.now()
    )
