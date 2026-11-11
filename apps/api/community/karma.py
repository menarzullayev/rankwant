"""Karma (decision 2026-11-11 ③): the sum of the votes a person's entries and
comments received, all time.

Read from `Vote.author` (copied at vote time), not stored on the user:
`User` is a locked entity (`docs/05-domain-model`), and the vote table is
small next to the user table.
"""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from django.db.models import Count, Q, Sum
from django.utils import timezone

from community.models import Entry, Vote
from core.models import User

#: "Active authors" look at this window (owner decision ③: so a newcomer is seen).
ACTIVE_WINDOW = timedelta(days=30)
PERIODS = ("all", "30d")


def karma_of(user_id: int) -> int:
    total = Vote.objects.filter(author_id=user_id).aggregate(n=Sum("value"))["n"]
    return int(total or 0)


def entries_of(user_id: int) -> int:
    return Entry.objects.filter(author_id=user_id, is_deleted=False, is_hidden=False).count()


def top(period: str = "all", limit: int = 50) -> list[dict[str, Any]]:
    """People by karma: all time, or by the votes of the last 30 days.

    Only positive totals: a list of "top" people should not end with the
    ones the community voted down.
    """
    votes = Vote.objects.filter(author__isnull=False, author__is_active=True)
    if period == "30d":
        votes = votes.filter(created_at__gte=timezone.now() - ACTIVE_WINDOW)
    rows = list(
        votes.values("author_id")
        .annotate(total=Sum("value"))
        .filter(total__gt=0)
        .order_by("-total", "author_id")[:limit]
    )
    ids = [row["author_id"] for row in rows]
    people = {u.pk: u for u in User.objects.filter(pk__in=ids)}
    alltime: dict[int, int] = {}
    if period != "all":
        alltime = {
            row["author_id"]: int(row["n"])
            for row in Vote.objects.filter(author_id__in=ids)
            .values("author_id")
            .annotate(n=Sum("value"))
        }
    entries = dict(
        User.objects.filter(pk__in=ids)
        .annotate(
            n=Count(
                "blog_entries",
                filter=Q(blog_entries__is_deleted=False, blog_entries__is_hidden=False),
            )
        )
        .values_list("pk", "n")
    )
    return [
        {
            "user": people[row["author_id"]],
            "points": int(row["total"]),
            "karma": alltime.get(row["author_id"], int(row["total"])),
            "entries": entries.get(row["author_id"], 0),
        }
        for row in rows
        if row["author_id"] in people
    ]
