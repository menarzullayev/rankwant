"""Timed notifications — nobody clicked anything, the clock did (decision 2026-11-16).

`run()` is what the beat task calls every five minutes. It looks at the
moments below and sends each notification at most once to each person, however
many times it looks again. The contest reminders live in `contests.reminders`
(a notifications module may not import `contests`) and use `send_once` from here:

* their streak is alive but today has no solved problem and it is past 20:00
  in Tashkent (`STREAK_WARN_HOUR`);
* their streak ended, noticed on the day after the missed one.

"At most once" lives in `ReminderSent`, not in the notification row: the site
channel may be switched off, or the row deleted, and a reminder must not come
back every five minutes because of that.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from datetime import date, datetime, timedelta

from django.core.cache import cache
from django.db import IntegrityError, transaction
from django.utils import timezone

from core.models import User
from notifications.models import Notification, ReminderSent
from notifications.services import notify, notify_many

log = logging.getLogger(__name__)

#: Local (Asia/Tashkent) hour from which "your streak is about to break" is sent.
STREAK_WARN_HOUR = 20
#: Streaks shorter than this are not worth a warning.
STREAK_MIN_DAYS = 2
#: A reminder window is a little wider than its step, so a beat that was late
#: still catches it; `ReminderSent` stops the second send.
SLACK = timedelta(minutes=10)
#: Rows older than this are of no use to the dedupe any more.
KEEP_DAYS = 60


def once(user: User, code: str, ref: str) -> bool:
    """True exactly once per `(user, code, ref)`."""
    try:
        with transaction.atomic():
            ReminderSent.objects.create(user=user, code=code, ref=ref)
    except IntegrityError:
        return False
    return True


def send_once(
    user: User, code: str, ref: str, ref_type: str, ref_id: str | int, **params: str
) -> int:
    if not once(user, code, ref):
        return 0
    notify(
        user,
        Notification.Kind.SYSTEM,
        code=code,
        params=params,
        ref_type=ref_type,
        ref_id=ref_id,
    )
    return 1


def streak_at_risk(now: datetime | None = None) -> int:
    """After 20:00 local: a living streak with nothing solved today."""
    now = timezone.localtime(now or timezone.now())
    if now.hour < STREAK_WARN_HOUR:
        return 0
    today = now.date()
    users = User.objects.filter(
        is_active=True,
        last_active_date=today - timedelta(days=1),
        streak_count__gte=STREAK_MIN_DAYS,
    )
    sent = 0
    for user in users.iterator():
        if user.streak_freeze_until and user.streak_freeze_until >= today:
            continue
        sent += send_once(
            user,
            "streak_at_risk",
            f"day:{today.isoformat()}",
            "streak",
            user.pk,
            days=str(user.streak_count),
        )
    return sent


def streak_broken(now: datetime | None = None) -> int:
    """The day after the missed one: the streak that was alive is gone."""
    today = timezone.localtime(now or timezone.now()).date()
    users = User.objects.filter(
        is_active=True,
        last_active_date__lte=today - timedelta(days=2),
        last_active_date__gte=today - timedelta(days=4),
        streak_count__gte=STREAK_MIN_DAYS,
    )
    sent = 0
    for user in users.iterator():
        gap: date = user.last_active_date  # type: ignore[assignment]
        if user.streak_freeze_until and user.streak_freeze_until >= today - timedelta(days=1):
            continue
        # One notice per streak: the last solved day names it.
        sent += send_once(
            user,
            "streak_broken",
            f"last:{gap.isoformat()}",
            "streak",
            user.pk,
            days=str(user.streak_count),
        )
    return sent


#: Someone who has not opened the site for this long is not told about a new contest.
ACTIVE_DAYS = 60


def announce_to_active(code: str, ref: str, ref_type: str, ref_id: str, **params: str) -> int:
    """One notice to everybody active lately, once per `(code, ref)` however often it is asked.

    Site channel only (`notify_many`): a contest announced to every account
    would be ~974k rows, so it goes to people seen in the last `ACTIVE_DAYS`.
    """
    since = timezone.now() - timedelta(days=ACTIVE_DAYS)
    already = set(ReminderSent.objects.filter(code=code, ref=ref).values_list("user_id", flat=True))
    people = [
        user
        for user in User.objects.filter(is_active=True, last_seen_at__gte=since).iterator()
        if user.pk not in already
    ]
    if not people:
        return 0
    ReminderSent.objects.bulk_create(
        [ReminderSent(user=u, code=code, ref=ref) for u in people], ignore_conflicts=True
    )
    return notify_many(
        people, Notification.Kind.SYSTEM, code=code, params=params, ref_type=ref_type, ref_id=ref_id
    )


def prune(now: datetime | None = None) -> int:
    cutoff = (now or timezone.now()) - timedelta(days=KEEP_DAYS)
    deleted, _ = ReminderSent.objects.filter(created_at__lt=cutoff).delete()
    return deleted


def run(now: datetime | None = None) -> dict[str, int]:
    """The streak notices the clock owes, once per day each.

    Both look at every user with a living streak, so the scan itself runs once
    a day (a cache key), not every five minutes; `ReminderSent` still makes the
    notices exactly-once if the cache is lost. Each part is isolated: one
    failing must not stop the other. The contest reminders are
    `contests.reminders.run`.
    """
    local = timezone.localtime(now or timezone.now())
    day = local.date().isoformat()
    parts: list[tuple[str, Callable[[datetime | None], int], str]] = [
        ("streak_broken", streak_broken, f"notif:streak_broken:{day}"),
    ]
    if local.hour >= STREAK_WARN_HOUR:
        parts.append(("streak_at_risk", streak_at_risk, f"notif:streak_at_risk:{day}"))
    result: dict[str, int] = {}
    for name, part, key in parts:
        if not cache.add(key, 1, 20 * 3600):
            continue
        try:
            result[name] = part(now)
        except Exception:
            log.exception("vaqt xabari yiqildi: %s", name)
            cache.delete(key)
            result[name] = -1
    return result
