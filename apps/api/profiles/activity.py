"""Activity events — one row per thing that happened to a user.

Written when the thing happens (HITL 2026-10-05), not composed on read: the
signed-in home page reads one indexed query instead of merging four tables.

The writers are not touched. Each source model announces its own rows through
`post_save`, so a new writer of `QvantTransaction` is covered without knowing
this module exists. The one exception is `bulk_create`, which sends no
signal: contest rating changes are written in bulk and call `record_ratings`
themselves.

An event is a log line, not a source of truth. A failure to write one must
not undo the solve, the payment or the rating change it describes, so every
write is wrapped and logged.
"""

from __future__ import annotations

import logging
from collections.abc import Iterable
from typing import Any

from django.db import transaction
from django.db.models.signals import post_save

from profiles.models import ActivityEvent

log = logging.getLogger(__name__)

Kind = ActivityEvent.Kind


def _rating_event(row: Any) -> ActivityEvent | None:
    """A rating change worth a line of its own.

    A solve already has its `solved` event, and the activity rating moves a
    little every day — both would bury the rest of the feed.
    """
    if row.reason == "problem_solved" or row.rating_type == "activity":
        return None
    return ActivityEvent(
        user_id=row.user_id,
        kind=Kind.RATING,
        ref_type=row.ref_type,
        ref_id=row.ref_id,
        data={
            "type": row.rating_type,
            "before": row.value_before,
            "after": row.value_after,
            "delta": row.delta,
            "reason": row.reason,
            "rank": row.rank,
        },
    )


def _write(events: Iterable[ActivityEvent | None]) -> None:
    rows = [event for event in events if event is not None]
    if not rows:
        return
    try:
        # A savepoint: a failed insert must not poison the caller's transaction.
        with transaction.atomic():
            ActivityEvent.objects.bulk_create(rows, batch_size=500)
    except Exception:
        log.exception("activity events were not written (%s rows)", len(rows))


def record_ratings(histories: Iterable[Any]) -> None:
    """For rating rows written with `bulk_create`, which sends no signal."""
    _write(_rating_event(row) for row in histories)


def _on_rating(sender: Any, instance: Any, created: bool, **kwargs: Any) -> None:
    if created:
        _write([_rating_event(instance)])


def _on_solved(sender: Any, instance: Any, created: bool, **kwargs: Any) -> None:
    if not created:
        return
    problem = instance.problem
    _write(
        [
            ActivityEvent(
                user_id=instance.user_id,
                kind=Kind.SOLVED,
                ref_type="problem",
                ref_id=problem.slug,
                data={"title": problem.title, "difficulty": instance.difficulty_at_solve},
            )
        ]
    )


def _on_qvant(sender: Any, instance: Any, created: bool, **kwargs: Any) -> None:
    if not created:
        return
    _write(
        [
            ActivityEvent(
                user_id=instance.user_id,
                kind=Kind.QVANT,
                ref_type=instance.ref_type,
                ref_id=instance.ref_id,
                data={
                    "amount": instance.amount,
                    "reason": instance.reason,
                    "balance_after": instance.balance_after,
                },
            )
        ]
    )


def _on_contest(sender: Any, instance: Any, created: bool, **kwargs: Any) -> None:
    if not created:
        return
    contest = instance.contest
    _write(
        [
            ActivityEvent(
                user_id=instance.user_id,
                kind=Kind.CONTEST,
                ref_type="contest",
                ref_id=contest.slug,
                data={"title": contest.title},
            )
        ]
    )


def connect() -> None:
    """Called once from `ProfilesConfig.ready`.

    The senders are named, not imported: this app listens to the others
    without depending on their modules (`tools/check_architecture.py`).
    """
    for model, receiver, uid in (
        ("ratings.RatingHistory", _on_rating, "activity-rating"),
        ("ratings.UserSolvedProblem", _on_solved, "activity-solved"),
        ("qvant.QvantTransaction", _on_qvant, "activity-qvant"),
        ("contests.ContestRegistration", _on_contest, "activity-contest"),
    ):
        post_save.connect(receiver, sender=model, dispatch_uid=uid)
