"""Standings by region (decision 2026-11-10 ②: a school or regional olympiad
reads its own table).

A participant's region is shown only when their location is public: the
privacy key `country` hides the whole location on the profile
(`profiles/public.py`), and a filter that still found them by region would
tell the same thing. Such a row is left out of every regional view and
count.

The regional table stays one answer for everybody, so the edge can cache it
like the full one: one cache entry per region.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

from contests.models import Contest, Standing
from profiles.catalog import UZ_REGIONS

STANDINGS_CACHE_KEY = "standings:{contest_id}"


def cache_key(contest_id: int, region: str = "") -> str:
    base = STANDINGS_CACHE_KEY.format(contest_id=contest_id)
    return f"{base}:{region}" if region else base


def cache_keys(contest_id: int) -> list[str]:
    """Every cached table of a contest: the full one and one per region."""
    return [cache_key(contest_id), *(cache_key(contest_id, code) for code in UZ_REGIONS)]


def _location_public(row: Standing) -> bool:
    return "country" not in (row.user.hidden_fields or [])


def region_counts(contest: Contest) -> list[dict[str, Any]]:
    """Participants per region, for the filter; regions with none are left out."""
    counts: Counter[str] = Counter()
    rows = Standing.objects.filter(
        contest=contest, user__country="UZ", user__region__in=UZ_REGIONS
    ).values_list("user__region", "user__hidden_fields")
    for region, hidden in rows:
        if "country" not in (hidden or []):
            counts[region] += 1
    return [{"code": code, "count": counts[code]} for code in UZ_REGIONS if counts[code]]


def regional_rows(contest: Contest, region: str, limit: int) -> list[Standing]:
    """The region's rows in table order, each with its regional place.

    `region_rank` counts official rows only, like `rank`: an insider or a
    disqualified row has 0 there too.
    """
    rows = (
        Standing.objects.filter(contest=contest, user__country="UZ", user__region=region)
        .select_related("user")
        .order_by("position")
    )
    out: list[Standing] = []
    place = 0
    for row in rows.iterator(chunk_size=500):
        if not _location_public(row):
            continue
        if row.is_official:
            place += 1
            row.region_rank = place  # type: ignore[attr-defined]
        else:
            row.region_rank = 0  # type: ignore[attr-defined]
        out.append(row)
        if len(out) >= limit:
            break
    return out
