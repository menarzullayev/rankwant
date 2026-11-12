"""How many tutor replies a student gets a day (decision ③).

The same numbers as Robocontest's RoboAI, the owner's choice of 2026-11-11.
A day is the site's day (Asia/Tashkent). A reply that failed is not counted:
the student did not get anything for it.
"""

from __future__ import annotations

from datetime import datetime, time, timedelta
from typing import Any

from django.utils import timezone

from core.quotas import plan_of

DAILY = {"free": 5, "plus": 100, "pro": 250, "judge": 500}


def daily_limit(user: Any) -> int | None:
    """`None` — no limit (staff)."""
    if getattr(user, "is_staff", False):
        return None
    return DAILY.get(plan_of(user), DAILY["free"])


def day_start(now: datetime | None = None) -> datetime:
    local = timezone.localtime(now or timezone.now())
    return timezone.make_aware(datetime.combine(local.date(), time.min))


def resets_at(now: datetime | None = None) -> datetime:
    return day_start(now) + timedelta(days=1)


def used_today(user: Any, now: datetime | None = None) -> int:
    from tutor.models import Message

    return (
        Message.objects.filter(user=user, role=Message.Role.TUTOR, created_at__gte=day_start(now))
        .exclude(status=Message.Status.FAILED)
        .count()
    )
