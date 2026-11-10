"""Fair play: editor signals, the jury's report, disqualification (ADR-0055, part 4).

Owner decisions, 2026-11-10: solving with an AI assistant is now the larger
risk than copying from another participant, so the report reads how a
solution was written, not what it resembles:

- during a contest the editor tells, with each attempt, how much was pasted,
  how often the page was left and how long it was open (`AttemptSignal`);
- AI assistants are forbidden in a contest and the page says so — also that
  these signals are recorded;
- after the contest the jury sees the participants whose signals stand out;
  nothing is decided automatically;
- the jury (or staff-ops) disqualifies: every contest attempt is SKIPPED,
  the row shows «DQ» with no place, the certificate goes, the participant is
  told why, and when the rating was already applied the whole contest is
  re-rated.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from django.db import transaction
from django.utils import timezone

from contests.models import AttemptSignal, Certificate, Contest, ContestRegistration
from core.permissions import STAFF_GROUP_OPS, has_staff_group

#: A single paste this long is a whole solution, not a snippet.
LARGE_PASTE = 200
#: Share of the source that came from pastes.
PASTED_SHARE = 0.6
#: Characters per minute no one types for long.
FAST_CPM = 400
#: Leaving the page this often.
MANY_BLURS = 10
#: Below this a solution is too short to read anything from.
MIN_SOURCE = 100

#: Each signal is clamped; a page cannot claim more than this.
LIMIT = 10_000_000


@dataclass
class FairPlayError(Exception):
    code: str
    message: str
    status: int = 400


def can_judge(contest: Contest, user: Any) -> bool:
    """The jury and staff-ops read the report and disqualify."""
    if user is None or not getattr(user, "is_authenticated", False):
        return False
    if has_staff_group(user, STAFF_GROUP_OPS):
        return True
    return contest.jury.filter(pk=user.pk).exists()


def _count(data: dict[str, Any], key: str) -> int:
    try:
        value = int(data.get(key) or 0)
    except (TypeError, ValueError):
        return 0
    return max(0, min(value, LIMIT))


def record(attempt: Any, data: dict[str, Any] | None) -> AttemptSignal | None:
    """Keep what the editor told about a contest attempt."""
    if not data or not attempt.contest_id:
        return None
    return AttemptSignal.objects.create(
        attempt=attempt,
        contest_id=attempt.contest_id,
        user_id=attempt.user_id,
        source_chars=len(attempt.source_code or ""),
        pasted_chars=_count(data, "pasted_chars"),
        largest_paste=_count(data, "largest_paste"),
        paste_count=_count(data, "paste_count"),
        blur_count=_count(data, "blur_count"),
        active_ms=_count(data, "active_ms"),
    )


def flags(signal: AttemptSignal) -> list[str]:
    """What stands out in one attempt's signals."""
    found: list[str] = []
    if signal.source_chars >= MIN_SOURCE and (
        signal.largest_paste >= LARGE_PASTE
        or signal.pasted_chars >= PASTED_SHARE * signal.source_chars
    ):
        found.append("pasted")
    minutes = signal.active_ms / 60_000
    typed = max(0, signal.source_chars - signal.pasted_chars)
    if typed >= MIN_SOURCE * 3 and minutes > 0 and typed / minutes > FAST_CPM:
        found.append("fast")
    if signal.blur_count >= MANY_BLURS:
        found.append("away")
    return found


def report(contest: Contest) -> list[dict[str, Any]]:
    """Attempts whose signals stand out, the most flags first."""
    rows: list[dict[str, Any]] = []
    signals = (
        # The official run only: a virtual attempt comes after the end.
        AttemptSignal.objects.filter(contest=contest, attempt__created_at__lt=contest.end_at)
        .select_related("user", "attempt", "attempt__problem")
        .order_by("attempt__created_at")
    )
    letters = dict(contest.problems.values_list("problem_id", "index_letter"))
    for signal in signals:
        found = flags(signal)
        if not found:
            continue
        rows.append(
            {
                "attempt": signal.attempt_id,
                "username": signal.user.username,
                "problem": letters.get(signal.attempt.problem_id, ""),
                "verdict": signal.attempt.verdict,
                "created_at": signal.attempt.created_at,
                "flags": found,
                "source_chars": signal.source_chars,
                "pasted_chars": signal.pasted_chars,
                "largest_paste": signal.largest_paste,
                "paste_count": signal.paste_count,
                "blur_count": signal.blur_count,
                "active_ms": signal.active_ms,
            }
        )
    rows.sort(key=lambda row: -len(row["flags"]))
    return rows


def disqualify(contest: Contest, user: Any, judge: Any, reason: str) -> ContestRegistration:
    from contests.services import rebuild_standings
    from judging.services import skip_attempts

    reason = (reason or "").strip()
    if not reason:
        raise FairPlayError("reason_required", "Write the reason")
    if timezone.now() < contest.start_at:
        raise FairPlayError("contest_not_started", "The contest has not started")
    with transaction.atomic():
        registration, _ = ContestRegistration.objects.select_for_update().get_or_create(
            contest=contest, user=user
        )
        if registration.disqualified_at is not None:
            raise FairPlayError("already_disqualified", "Already disqualified")
        registration.disqualified_at = timezone.now()
        registration.disqualified_reason = reason
        registration.disqualified_by = judge
        registration.save(
            update_fields=["disqualified_at", "disqualified_reason", "disqualified_by"]
        )
        # Through the reverse relation: an app does not import another's models.
        skip_attempts(contest.attempts.filter(user=user))
        Certificate.objects.filter(contest=contest, user=user).delete()
        if contest.ratings_applied_at is not None and contest.is_rated:
            from ratings.services import rerate_contest

            rerate_contest(contest)
        else:
            rebuild_standings(contest)
        if contest.ratings_applied_at is not None:
            from contests.certificates import issue

            issue(contest)
    _tell(contest, user, reason)
    return registration


def _tell(contest: Contest, user: Any, reason: str) -> None:
    from notifications.services import notify

    notify(
        user,
        # `Notification.Kind.SYSTEM` by value (`tools/check_architecture.py`).
        "system",
        code="contest_disqualified",
        params={"contest": contest.title, "reason": reason[:300]},
        ref_type="contest",
        ref_id=contest.slug,
    )
