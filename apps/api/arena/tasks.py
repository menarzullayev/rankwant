from __future__ import annotations

import logging

from celery import shared_task
from django.utils import timezone

from arena.models import ArenaRound
from arena.services import finalize

log = logging.getLogger(__name__)


@shared_task(name="arena.finalize_due")
def finalize_due_rounds() -> int:
    """Tugagan, lekin mukofoti berilmagan raundlarni yakunlaydi."""
    total = 0
    for arena in ArenaRound.objects.filter(rewards_applied_at__isnull=True):
        if arena.end_at > timezone.now():
            continue
        try:
            total += finalize(arena)
        except Exception:
            log.exception("arena %s yakunlanmadi", arena.slug)
    return total
