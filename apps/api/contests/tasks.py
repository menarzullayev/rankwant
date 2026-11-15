from __future__ import annotations

import logging

from celery import shared_task
from django.utils import timezone

from contests.models import Contest
from contests.services import finalize_contest, rebuild_standings

log = logging.getLogger(__name__)


@shared_task(name="contests.rebuild_standings")
def rebuild_standings_task(contest_id: int) -> int:
    return rebuild_standings(Contest.objects.get(pk=contest_id))


@shared_task(name="contests.finalize_due")
def finalize_due_contests() -> int:
    """Tugagan, lekin reytingi hisoblanmagan musobaqalarni yakunlaydi."""
    due = Contest.objects.filter(end_at__lte=timezone.now(), ratings_applied_at__isnull=True)
    total = 0
    for contest in due:
        try:
            total += finalize_contest(contest)
        except Exception:
            log.exception("contest %s yakunlanmadi", contest.slug)
    return total


@shared_task(name="contests.announce_new")
def announce_new(contest_id: int) -> int:
    """A contest was just published: tell the people active lately, once."""
    from notifications.reminders import announce_to_active

    contest = Contest.objects.filter(pk=contest_id, is_public=True).first()
    if contest is None:
        return 0
    return announce_to_active(
        "contest_new", f"contest:{contest.pk}", "contest", contest.slug, contest=contest.title
    )


@shared_task(name="contests.run_reminders")
def run_reminders() -> dict[str, int]:
    """A day / an hour before a contest, and its end, for hosts (beat, every 5 minutes)."""
    from contests import reminders

    return reminders.run()
