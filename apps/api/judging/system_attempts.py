"""Submissions the platform makes itself, through the path users take.

The Abramyan verification (ADR-0060 § 2.6) sends each reference solution and
an empty program as a system account: attempt → queue → judge → result. It
lives here so the problems app does not reach into `judging.models`.
"""

from __future__ import annotations

from typing import Any

from judging.models import Attempt
from judging.services import enqueue
from judging.verdicts import TERMINAL, Verdict

#: Verdicts that are not an answer yet.
UNFINISHED = frozenset({Verdict.PENDING, Verdict.RUNNING})


def submit(user: Any, problem: Any, language: Any, source: str) -> int:
    """Save and queue one attempt; returns its id."""
    attempt = Attempt.objects.create(
        user=user, problem=problem, language=language, source_code=source
    )
    enqueue(attempt)
    return attempt.pk


def finished(ids: set[int]) -> set[int]:
    """The ids among these whose verdict is final."""
    return set(
        Attempt.objects.filter(pk__in=ids, verdict__in=TERMINAL).values_list("pk", flat=True)
    )


def results(ids: list[int]) -> dict[int, dict[str, Any]]:
    """Verdict, failed test, time and memory of each attempt."""
    return {
        row["pk"]: dict(row)
        for row in Attempt.objects.filter(pk__in=ids).values(
            "pk", "verdict", "failed_test_index", "time_ms", "memory_kb"
        )
    }


def last_verdicts(problem: Any, username: str, source: str) -> tuple[str | None, str | None]:
    """The account's last verdict on this problem for `source`, and for any
    other source: (other, this). `None` when there is none."""
    attempts = Attempt.objects.filter(problem=problem, user__username=username).order_by("-pk")
    this = attempts.filter(source_code=source).values_list("verdict", flat=True).first()
    other = attempts.exclude(source_code=source).values_list("verdict", flat=True).first()
    return other, this
