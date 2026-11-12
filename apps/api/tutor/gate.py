"""Where the tutor is off (decision ④, ADR-0065 § 2.5).

A problem of a contest that is not finalized is still a contest problem
(`is_public=False`, ADR-0055): the tutor is off for it before the start,
during the contest and until it reaches the archive. An archive problem
reused in a contest that is running now is off too — otherwise a
participant would ask the tutor during the round.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from django.utils import timezone

CONTEST = "ai_off_in_contest"


def closed_reason(problem: Any, now: datetime | None = None) -> str | None:
    if not problem.is_public:
        return CONTEST
    now = now or timezone.now()
    running = problem.contest_entries.filter(
        contest__is_public=True, contest__start_at__lte=now, contest__end_at__gt=now
    ).exists()
    return CONTEST if running else None
