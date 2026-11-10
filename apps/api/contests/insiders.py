"""People who know a contest's problems before it starts (ADR-0055, part 2).

The problem authors, the testers, the jury and the organizers. They may
take part in the contest, but unrated: their row in the table carries a
star and no place, and everything that ranks people — ratings, places,
certificates, Qvant, the champion badge, a championship — skips it.

A tester also opens the problems before the start and sends solutions to
them. Such an attempt (made before the contest's start) is a *testing*
attempt: it is judged, and it counts nowhere — not in the table, not as a
solved problem, not in the problem's numbers — and until the contest ends
only its author sees it.

The problems are reached through `ContestProblem`, so this module imports
nothing from `problems`.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from django.db.models import Q
from django.utils import timezone

from contests.models import Contest, ContestProblem, Standing

#: The order a role is told in when a person holds several: the one that
#: says the most about what they know comes first.
ROLES: tuple[str, ...] = (
    Standing.InsiderRole.AUTHOR,
    Standing.InsiderRole.TESTER,
    Standing.InsiderRole.JURY,
    Standing.InsiderRole.ORGANIZER,
)


def _author_ids(contest: Contest) -> set[int]:
    entries = ContestProblem.objects.filter(contest=contest)
    ids = set(entries.exclude(problem__authors=None).values_list("problem__authors", flat=True))
    ids |= set(entries.exclude(problem__author=None).values_list("problem__author", flat=True))
    return ids


def insiders(contest: Contest) -> dict[int, str]:
    """User id → insider role, for every insider of the contest."""
    found: dict[int, str] = {}
    groups: dict[str, Any] = {
        Standing.InsiderRole.AUTHOR: _author_ids(contest),
        Standing.InsiderRole.TESTER: contest.testers.values_list("pk", flat=True),
        Standing.InsiderRole.JURY: contest.jury.values_list("pk", flat=True),
        Standing.InsiderRole.ORGANIZER: contest.organizers.values_list("pk", flat=True),
    }
    for role in ROLES:
        for user_id in groups[role]:
            found.setdefault(user_id, role)
    return found


def role_of(contest: Contest, user: Any) -> str:
    """The user's insider role in the contest, or "" for a participant."""
    if user is None or not getattr(user, "is_authenticated", False):
        return ""
    return insiders(contest).get(user.pk, "")


def testing_contests(user: Any, now: datetime | None = None) -> Any:
    """Public contests not started yet in which the user is an insider.

    These are the contests whose problems the user may open and send to
    before the start.
    """
    if user is None or not getattr(user, "is_authenticated", False):
        return Contest.objects.none()
    now = now or timezone.now()
    return Contest.objects.filter(
        Q(testers=user)
        | Q(jury=user)
        | Q(organizers=user)
        | Q(problems__problem__authors=user)
        | Q(problems__problem__author=user),
        is_public=True,
        start_at__gt=now,
    ).distinct()


def is_testing(attempt: Any) -> bool:
    """A testing attempt: sent to a contest before the contest started."""
    contest = attempt.contest if attempt.contest_id else None
    return bool(contest is not None and attempt.created_at < contest.start_at)


def crew(contest: Contest) -> dict[str, list[dict[str, Any]]]:
    """The people who prepared the contest, for its public page.

    Inactive accounts are left out: imported authors are shadow accounts
    whose profile would 404.
    """
    from core.models import User
    from profiles.titles import user_title

    def people(ids: Any) -> list[dict[str, Any]]:
        rows = User.objects.filter(pk__in=list(ids), is_active=True).order_by("username")
        return [{"username": u.username, "user_title": user_title(u)} for u in rows]

    return {
        "authors": people(_author_ids(contest)),
        "testers": people(contest.testers.values_list("pk", flat=True)),
        "jury": people(contest.jury.values_list("pk", flat=True)),
    }


def notify_new_testers(contest: Contest, before: set[int]) -> int:
    """Tell the people just made testers of the contest.

    They have nowhere else to learn it from: the problems open to them
    quietly, on pages they have no reason to visit.
    """
    from core.models import User
    from notifications.services import notify

    added = set(contest.testers.values_list("pk", flat=True)) - before
    for user in User.objects.filter(pk__in=added, is_active=True):
        notify(
            user,
            # `Notification.Kind.SYSTEM` — named by value: an app does not
            # import another app's models (`tools/check_architecture.py`).
            "system",
            code="contest_tester",
            params={"contest": contest.title},
            ref_type="contest",
            ref_id=contest.slug,
        )
    return len(added)
