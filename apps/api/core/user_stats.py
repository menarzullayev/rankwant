"""Stored user counters (ADR-0024): where they come from and how to rebuild them.

`User.solved_count`, `max_rating_*`, `streak_max` and `last_seen_at` cache values
that other tables already hold. The services keep them current as events
happen. This module derives them again from the source tables, for the
migration that fills them and for `manage.py recount_user_stats`.

Every function takes an app registry, so a migration can pass its historical
models. The default is the live registry.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta
from typing import Any

from django.db.models import Count, F, Max, Value
from django.db.models.functions import Coalesce, Greatest, TruncDate
from django.utils import timezone

#: `RatingHistory.rating_type` -> the `User` column that stores its maximum.
MAX_RATING_FIELDS: dict[str, str] = {
    "skills": "max_rating_skills",
    "contest": "max_rating_contest",
    "activity": "max_rating_activity",
    "challenges": "max_rating_challenges",
}

#: The columns this module owns, in report order.
FIELDS: tuple[str, ...] = (
    "solved_count",
    *MAX_RATING_FIELDS.values(),
    "streak_max",
    "last_seen_at",
)

#: Columns that may legitimately run ahead of their source, so a rebuild only
#: raises them. A streak kept alive by a freeze has no accepted attempt on the
#: frozen day, and deleting a session does not undo the visit it recorded.
RAISE_ONLY: frozenset[str] = frozenset({"streak_max", "last_seen_at"})


def _registry(registry: Any) -> Any:
    if registry is not None:
        return registry
    from django.apps import apps

    return apps


def longest_run(days: list[date]) -> int:
    """Longest run of consecutive days in a sorted list.

    The same rule as `profiles.stats.streaks`: one accepted attempt makes a day
    count, and a missing day breaks the run.
    """
    longest = run = 0
    previous: date | None = None
    for day in days:
        run = run + 1 if previous is not None and day - previous == timedelta(days=1) else 1
        longest = max(longest, run)
        previous = day
    return longest


def expected(registry: Any = None) -> dict[int, dict[str, Any]]:
    """Each user's counters as derived from the source tables."""
    get = _registry(registry).get_model
    User = get("core", "User")
    UserSession = get("core", "UserSession")
    RatingHistory = get("ratings", "RatingHistory")
    UserSolvedProblem = get("ratings", "UserSolvedProblem")
    Attempt = get("judging", "Attempt")

    empty = {field: None for field in MAX_RATING_FIELDS.values()}
    out: dict[int, dict[str, Any]] = {
        pk: {"solved_count": 0, **empty, "streak_max": streak, "last_seen_at": None}
        for pk, streak in User.objects.values_list("pk", "streak_count").iterator(chunk_size=5000)
    }

    def row_for(user_id: int) -> dict[str, Any] | None:
        # A user created after the first query simply waits for the next run.
        return out.get(user_id)

    # Public problems only, like the profile's solved figures.
    for user_id, solved in (
        UserSolvedProblem.objects.filter(problem__is_public=True)
        .values_list("user_id")
        .annotate(n=Count("pk"))
    ):
        if (row := row_for(user_id)) is not None:
            row["solved_count"] = solved

    for user_id, rating_type, top in RatingHistory.objects.values_list(
        "user_id", "rating_type"
    ).annotate(top=Max("value_after")):
        field = MAX_RATING_FIELDS.get(rating_type)
        if field and (row := row_for(user_id)) is not None:
            row[field] = top

    days: dict[int, list[date]] = defaultdict(list)
    ac_days = (
        # "AC" is `judging.verdicts.Verdict.AC`; a migration may not import it.
        Attempt.objects.filter(verdict="AC")
        .annotate(day=TruncDate("created_at", tzinfo=timezone.get_current_timezone()))
        .values_list("user_id", "day")
        .distinct()
        .order_by("user_id", "day")
    )
    for user_id, day in ac_days.iterator(chunk_size=5000):
        days[user_id].append(day)
    for user_id, user_days in days.items():
        if (row := row_for(user_id)) is not None:
            row["streak_max"] = max(row["streak_max"], longest_run(user_days))

    for user_id, seen in UserSession.objects.values_list("user_id").annotate(last=Max("last_seen")):
        if (row := row_for(user_id)) is not None:
            row["last_seen_at"] = seen
    return out


def _differs(field: str, stored: Any, wanted: Any) -> bool:
    if field in RAISE_ONLY:
        return wanted is not None and (stored is None or stored < wanted)
    return bool(stored != wanted)


def reconcile(
    *, fix: bool, registry: Any = None, bulk: bool = False
) -> list[tuple[int, str, Any, Any]]:
    """Compare the stored columns with `expected()` and optionally repair them.

    Returns `(user_id, field, stored, expected)` for every difference found.

    `bulk=True` writes whole rows with `bulk_update`. Use it only where no other
    writer can touch these columns, as in the migration that adds them. The
    default writes one guarded `UPDATE` per difference, which is safe while the
    site is live: a raise-only column is never lowered, and an exact column is
    set to the value derived moments ago.
    """
    User = _registry(registry).get_model("core", "User")
    wanted_by_user = expected(registry)
    diffs: list[tuple[int, str, Any, Any]] = []
    rows: list[Any] = []
    for stored in User.objects.values("pk", *FIELDS).iterator(chunk_size=5000):
        wanted = wanted_by_user.get(stored["pk"])
        if wanted is None:
            continue
        changed = False
        for field in FIELDS:
            if _differs(field, stored[field], wanted[field]):
                diffs.append((stored["pk"], field, stored[field], wanted[field]))
                changed = True
        if fix and bulk and changed:
            values = {
                field: wanted[field]
                if _differs(field, stored[field], wanted[field])
                else stored[field]
                for field in FIELDS
            }
            rows.append(User(pk=stored["pk"], **values))

    if fix and bulk and rows:
        User.objects.bulk_update(rows, list(FIELDS), batch_size=2000)
    elif fix:
        for user_id, field, _stored, value in diffs:
            if field in RAISE_ONLY:
                update = {field: Greatest(Coalesce(F(field), Value(value)), Value(value))}
            else:
                update = {field: value}
            User.objects.filter(pk=user_id).update(**update)
    return diffs
