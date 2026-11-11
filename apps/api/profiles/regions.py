"""Active members by region (decision 2026-11-11 ④: a region map on the home page).

"Active" is a day that counted for the streak (`User.last_active_date`): a
solved problem. Read from the user table alone, cached for ten minutes.
"""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from django.core.cache import cache
from django.db.models import Count
from django.utils import timezone

from core.models import User
from profiles.catalog import UZ_REGIONS

PERIODS = (7, 30, 90, 365)
CACHE_SECONDS = 10 * 60


def active_by_region(days: int) -> dict[str, Any]:
    days = days if days in PERIODS else 30
    key = f"regions:active:{days}"
    cached = cache.get(key)
    if cached is not None:
        return dict(cached)
    since = timezone.localdate() - timedelta(days=days - 1)
    counts = dict(
        User.objects.filter(
            is_active=True, country="UZ", region__in=UZ_REGIONS, last_active_date__gte=since
        )
        .values("region")
        .annotate(n=Count("pk"))
        .values_list("region", "n")
    )
    data = {
        "days": days,
        "total": sum(counts.values()),
        "regions": [{"code": code, "users": int(counts.get(code, 0))} for code in UZ_REGIONS],
    }
    cache.set(key, data, CACHE_SECONDS)
    return data
