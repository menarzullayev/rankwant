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

Before the start the contest's insiders — problem authors, testers, jury,
organizers — open its problems too, when the viewer is passed in (part 2).

The contest is reached through the reverse relation (`contest_entries`);
the one thing taken from `contests` is the insider rule, imported lazily.
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


def _testing(user: Any, now: datetime) -> QuerySet[Problem] | None:
    """Held problems of the contests this user tests before their start."""
    if user is None or not getattr(user, "is_authenticated", False):
        return None
    from contests.insiders import testing_contests

    return Problem.objects.filter(
        is_public=False, contest_entries__contest__in=testing_contests(user, now)
    )


def openable_q(now: datetime | None = None, user: Any = None) -> Q:
    """Problems that may be opened by address.

    A subquery, not a join: the callers annotate aggregates on the same
    queryset, and a join to the contest rows would multiply them.
    """
    now = now or timezone.now()
    held = _held_and_started(now).values("pk")
    scope = Q(is_public=True) | Q(pk__in=held)
    tested = _testing(user, now)
    if tested is not None:
        scope |= Q(pk__in=tested.values("pk"))
    return scope


def openable(slug: str, now: datetime | None = None, user: Any = None) -> Problem | None:
    return Problem.objects.filter(openable_q(now, user), slug=slug).first()


def holding_entry(problem: Problem, now: datetime | None = None, user: Any = None) -> Any | None:
    """The contest entry that keeps this problem out of the archive.

    `None` for an archive problem. When a problem is in several contests the
    earliest started one answers — that is the contest it was written for.
    Before any has started, an insider passed as `user` gets the entry of
    the contest they test (ADR-0055, part 2).
    """
    if problem.is_public:
        return None
    now = now or timezone.now()
    entries = problem.contest_entries.select_related("contest")
    started = (
        entries.filter(contest__is_public=True, contest__start_at__lte=now)
        .order_by("contest__start_at", "pk")
        .first()
    )
    if started is not None or user is None or not getattr(user, "is_authenticated", False):
        return started
    from contests.insiders import testing_contests

    return (
        entries.filter(contest__in=testing_contests(user, now))
        .order_by("contest__start_at", "pk")
        .first()
    )


def without_testing(attempts: QuerySet[Any], problem: Problem) -> QuerySet[Any]:
    """Drop the testing attempts on this problem (ADR-0055, part 2).

    An attempt sent to a contest before its start was a tester's: it is in
    no count and no list of solvers.
    """
    for contest_id, start_at in problem.contest_entries.values_list(
        "contest_id", "contest__start_at"
    ):
        attempts = attempts.exclude(contest_id=contest_id, created_at__lt=start_at)
    return attempts


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
