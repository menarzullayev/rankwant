"""Standings hisoblash — ACM penalty va reyting yakunlash."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime

from django.db import transaction
from django.utils import timezone

from contests.models import Contest, ContestProblem, Standing
from judging.models import Attempt
from judging.verdicts import Verdict

log = logging.getLogger(__name__)

#: ACM: har noto'g'ri urinish uchun jarima (daqiqa)
WRONG_ATTEMPT_PENALTY_MIN = 20


@dataclass
class _ProblemState:
    """Bitta foydalanuvchining bitta masaladagi holati."""

    solved_at: datetime | None = None
    wrong: int = 0


@dataclass
class _Row:
    user_id: int
    solved: int
    penalty: int
    last_ac: datetime | None


@transaction.atomic
def rebuild_standings(contest: Contest) -> int:
    """Contest standings ni qayta quradi.

    ACM: yechilgan masalalar soni ↓, keyin penalty ↑.
    Penalty = (birinchi AC vaqti daqiqada) + 20 × (AC gacha noto'g'ri urinishlar).
    """
    problem_ids = list(
        ContestProblem.objects.filter(contest=contest).values_list("problem_id", flat=True)
    )
    if not problem_ids:
        return 0

    attempts = (
        Attempt.objects.filter(contest=contest, problem_id__in=problem_ids)
        .order_by("created_at")
        .values("user_id", "problem_id", "verdict", "created_at")
    )

    per_user: dict[int, dict[int, _ProblemState]] = {}
    for a in attempts:
        state = per_user.setdefault(a["user_id"], {}).setdefault(a["problem_id"], _ProblemState())
        if state.solved_at is not None:
            continue
        if a["verdict"] == Verdict.AC:
            state.solved_at = a["created_at"]
        elif a["verdict"] in {Verdict.PENDING, Verdict.RUNNING, Verdict.CE}:
            # Kompilyatsiya xatosi va tekshirilmagan urinish jarima bermaydi
            continue
        else:
            state.wrong += 1

    rows: list[_Row] = []
    for user_id, problems in per_user.items():
        solved = 0
        penalty = 0
        last_ac: datetime | None = None
        for state in problems.values():
            if state.solved_at is None:
                continue
            solved += 1
            minutes = int((state.solved_at - contest.start_at).total_seconds() // 60)
            penalty += minutes + WRONG_ATTEMPT_PENALTY_MIN * state.wrong
            if last_ac is None or state.solved_at > last_ac:
                last_ac = state.solved_at
        rows.append(_Row(user_id, solved, penalty, last_ac))

    rows.sort(key=lambda r: (-r.solved, r.penalty))

    Standing.objects.filter(contest=contest).delete()
    Standing.objects.bulk_create(
        [
            Standing(
                contest=contest,
                user_id=row.user_id,
                rank=i + 1,
                solved_count=row.solved,
                penalty=row.penalty,
                total_score=row.solved,
                last_ac_at=row.last_ac,
            )
            for i, row in enumerate(rows)
        ]
    )
    return len(rows)


@transaction.atomic
def finalize_contest(contest: Contest) -> int:
    """Musobaqa tugagach: standings + Contests reytingi."""
    if contest.ratings_applied_at is not None:
        return 0
    if not contest.is_finished:
        return 0

    rebuild_standings(contest)

    from ratings.services import apply_contest_ratings

    affected = apply_contest_ratings(contest)

    # Phase 1 — contest yakunlash questi (ADR-0002: +30, contest boshiga)
    if contest.is_rated:
        try:
            from qvant.services import on_contest_finished

            for standing in Standing.objects.filter(contest=contest).select_related("user"):
                on_contest_finished(standing.user, contest.slug)
        except Exception:
            log.exception("contest %s uchun Qvant berilmadi", contest.slug)
    contest.ratings_applied_at = timezone.now()
    contest.save(update_fields=["ratings_applied_at"])
    log.info("contest %s yakunlandi — %s ishtirokchi reytingi yangilandi", contest.slug, affected)
    return affected
