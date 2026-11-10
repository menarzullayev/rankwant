from __future__ import annotations

from datetime import timedelta

from celery import shared_task
from django.db.models import F, Q
from django.utils import timezone

from profiles import external
from profiles.models import ExternalProfile


@shared_task(name="profiles.refresh_external")
def refresh_external(profile_id: int) -> bool:
    """Tashqi reytingni yangilaydi — so'rov ichida emas, navbatda."""
    profile = ExternalProfile.objects.filter(pk=profile_id).first()
    return external.refresh(profile) if profile is not None else False


#: A profile refreshed more recently than this is skipped (audit Q-07.4).
STALE_AFTER = timedelta(hours=20)
#: Upper bound per run; the rest waits for tomorrow rather than hammering
#: the platforms' public APIs.
DAILY_BATCH = 500
#: Seconds between two queued refreshes, so the fetches do not burst.
SPACING_S = 2


@shared_task(name="profiles.refresh_stale_externals")
def refresh_stale_externals() -> int:
    """Re-read linked external ratings once a day (audit Q-07.4, 2026-11-10).

    A rating used to change only when its owner pressed Refresh, so a
    profile that improved elsewhere stayed stale. Only active accounts with
    a platform that has a rating are read; the ~974 thousand imported
    accounts are refreshed by the manual bulk import, not here (2026-09-19
    decision: that import stays manual).
    """
    cutoff = timezone.now() - STALE_AFTER
    ids = list(
        ExternalProfile.objects.filter(user__is_active=True, kind__in=list(external.FETCHERS))
        .filter(Q(fetched_at__isnull=True) | Q(fetched_at__lt=cutoff))
        .order_by(F("fetched_at").asc(nulls_first=True), "pk")
        .values_list("pk", flat=True)[:DAILY_BATCH]
    )
    for index, profile_id in enumerate(ids):
        refresh_external.apply_async((profile_id,), countdown=index * SPACING_S)
    return len(ids)
