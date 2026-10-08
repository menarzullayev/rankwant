"""Who may open a problem that belongs to a contest (ADR-0055).

A problem written for a contest is not in the archive (`is_public=False`)
and stays that way until the contest is finalized. In between it has three
states, all read from the contest it is attached to:

    before the start   closed to everybody but its authors and staff
    from the start     open by address — the statement is for everybody,
                       sending a solution is for registered participants
    after finalizing   `is_public=True`: an archive problem like any other

"Open by address" is narrower than "public": the problem is in no list, no
search, no sitemap and no count. Everything that lists problems keeps
filtering on `is_public`; only the places that open ONE problem use
`openable()`.

The contest is reached through the reverse relation (`contest_entries`), so
this module imports nothing from `contests`.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from django.db.models import Q, QuerySet
from django.utils import timezone

from problems.models import Problem


def _held_and_started(now: datetime) -> QuerySet[Problem]:
    return Problem.objects.filter(
        is_public=False,
        contest_entries__contest__is_public=True,
        contest_entries__contest__start_at__lte=now,
    )


def openable_q(now: datetime | None = None) -> Q:
    """Problems that may be opened by address.

    A subquery, not a join: the callers annotate aggregates on the same
    queryset, and a join to the contest rows would multiply them.
    """
    held = _held_and_started(now or timezone.now()).values("pk")
    return Q(is_public=True) | Q(pk__in=held)


def openable(slug: str, now: datetime | None = None) -> Problem | None:
    return Problem.objects.filter(openable_q(now), slug=slug).first()


def holding_entry(problem: Problem, now: datetime | None = None) -> Any | None:
    """The contest entry that keeps this problem out of the archive.

    `None` for an archive problem. When a problem is in several contests the
    earliest started one answers — that is the contest it was written for.
    """
    if problem.is_public:
        return None
    return (
        problem.contest_entries.select_related("contest")
        .filter(contest__is_public=True, contest__start_at__lte=now or timezone.now())
        .order_by("contest__start_at", "pk")
        .first()
    )


def frozen_since(problem: Problem, now: datetime | None = None) -> datetime | None:
    """From when other people's attempts on this problem are not shown.

    The scoreboard freezes for the last minutes of a contest; a problem's
    statistics and its list of solvers must freeze with it, or they give
    away what the scoreboard hides. Like the scoreboard's, the freeze ends
    with the contest.
    """
    now = now or timezone.now()
    entry = holding_entry(problem, now)
    if entry is None:
        return None
    contest = entry.contest
    freeze_at: datetime | None = contest.freeze_at
    if freeze_at is None or not (freeze_at <= now < contest.end_at):
        return None
    return freeze_at
