"""Timed notifications about contests (decision 2026-11-16).

Participants hear a day and an hour before a contest they registered for;
hosts hear an hour before and when it ends. "At most once" is
`notifications.reminders.send_once` (the `ReminderSent` table), so the beat
task may look as often as it likes. This lives in `contests` because a
notifications module may not import `contests` (`tools/check_architecture.py`).
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta

from django.utils import timezone

from contests.models import Contest, ContestRegistration
from notifications.reminders import SLACK, send_once

log = logging.getLogger(__name__)


def contest_starts(now: datetime | None = None) -> int:
    """Participants: a day and an hour before the start. Hosts: an hour before."""
    now = now or timezone.now()
    sent = 0
    for code, host_code, ahead in (
        ("contest_starts_in_day", None, timedelta(hours=24)),
        ("contest_starts_in_hour", "host_contest_starts_in_hour", timedelta(hours=1)),
    ):
        due = Contest.objects.filter(
            is_virtual=False, is_public=True, start_at__gt=now, start_at__lte=now + ahead + SLACK
        ).filter(start_at__gte=now + ahead - SLACK * 3)
        for contest in due:
            ref = f"contest:{contest.pk}"
            registrations = ContestRegistration.objects.filter(contest=contest).select_related(
                "user"
            )
            for row in registrations.iterator():
                sent += send_once(
                    row.user, code, ref, "contest", contest.slug, contest=contest.title
                )
            if host_code:
                for host in contest.organizers.all():
                    sent += send_once(
                        host, host_code, ref, "contest", contest.slug, contest=contest.title
                    )
    return sent


def contest_ended(now: datetime | None = None) -> int:
    """Hosts: the contest they organise is over."""
    now = now or timezone.now()
    sent = 0
    ended = Contest.objects.filter(
        is_virtual=False, is_public=True, end_at__lte=now, end_at__gte=now - timedelta(hours=6)
    )
    for contest in ended:
        for host in contest.organizers.all():
            sent += send_once(
                host,
                "host_contest_ended",
                f"contest:{contest.pk}",
                "contest",
                contest.slug,
                contest=contest.title,
            )
    return sent


def plagiarism_found(now: datetime | None = None) -> int:
    """Hosts: the contest is over and the editor signals flagged attempts."""
    from contests import integrity

    now = now or timezone.now()
    sent = 0
    ended = Contest.objects.filter(
        is_virtual=False, is_public=True, end_at__lte=now, end_at__gte=now - timedelta(hours=6)
    )
    for contest in ended:
        flagged = len({row["username"] for row in integrity.report(contest)})
        if not flagged:
            continue
        for host in contest.organizers.all():
            sent += send_once(
                host,
                "host_plagiarism_found",
                f"contest:{contest.pk}",
                "contest",
                contest.slug,
                contest=contest.title,
                count=str(flagged),
            )
    return sent


def run(now: datetime | None = None) -> dict[str, int]:
    result: dict[str, int] = {}
    for name, part in (
        ("contest_starts", contest_starts),
        ("contest_ended", contest_ended),
        ("plagiarism_found", plagiarism_found),
    ):
        try:
            result[name] = part(now)
        except Exception:
            log.exception("musobaqa eslatmasi yiqildi: %s", name)
            result[name] = -1
    return result
