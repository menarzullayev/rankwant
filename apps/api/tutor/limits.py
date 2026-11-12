"""How many tutor replies a student gets a day (decision ③).

The same numbers as Robocontest's RoboAI, the owner's choice of 2026-11-11.
A day is the site's day (Asia/Tashkent). A reply that failed is not counted:
the student did not get anything for it.
"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta
from typing import Any

from django.db.models import F
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


def local_day(moment: datetime | None = None) -> date:
    return timezone.localtime(moment or timezone.now()).date()


def used_today(user: Any, now: datetime | None = None) -> int:
    from tutor.models import DailyUse

    row = DailyUse.objects.filter(user=user, day=local_day(now)).first()
    return row.count if row else 0


def take(user: Any) -> None:
    """Count one reply. Called inside the asking transaction, with the user row locked."""
    from tutor.models import DailyUse

    row, _ = DailyUse.objects.get_or_create(user=user, day=local_day())
    DailyUse.objects.filter(pk=row.pk).update(count=F("count") + 1)


def give_back(user_id: int, asked_at: datetime) -> None:
    """A reply that failed is not counted: the student got nothing for it."""
    from tutor.models import DailyUse

    DailyUse.objects.filter(user_id=user_id, day=local_day(asked_at), count__gt=0).update(
        count=F("count") - 1
    )
