from __future__ import annotations

import logging

from celery import shared_task

from duels.models import Duel
from duels.services import finalize

log = logging.getLogger(__name__)


@shared_task(name="duels.finalize_due")
def finalize_due_duels() -> int:
    total = 0
    for duel in Duel.objects.filter(status=Duel.Status.ACCEPTED, ratings_applied_at__isnull=True):
        if not duel.is_due:
            continue
        try:
            total += int(finalize(duel))
        except Exception:
            log.exception("duel %s yakunlanmadi", duel.slug)
    return total
