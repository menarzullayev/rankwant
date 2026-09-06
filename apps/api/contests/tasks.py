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
