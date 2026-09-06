"""Duel mexanikasi: chaqiriq, qabul, masala tanlash, yakunlash."""

from __future__ import annotations

import logging
import random
from datetime import datetime, timedelta

from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from core.models import User
from duels.models import Duel, DuelProblem
from judging.models import Attempt
from judging.verdicts import Verdict
from problems.models import Problem
from ratings.models import UserSolvedProblem

log = logging.getLogger(__name__)

DIFFICULTY_WINDOW = 200
#: Chaqiriq boshlanish vaqti kamida shuncha keyin — raqib topilishi kerak
MIN_LEAD_MINUTES = 5
MAX_OPEN_PER_USER = 3


class DuelError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def create(
    challenger: User,
    *,
    title: str,
    problem_count: int,
    difficulty: int,
    duration_minutes: int,
    start_at: datetime,
) -> Duel:
    if start_at < timezone.now() + timedelta(minutes=MIN_LEAD_MINUTES):
        raise DuelError("too_soon", f"Boshlanish kamida {MIN_LEAD_MINUTES} daqiqadan keyin")
    open_count = Duel.objects.filter(challenger=challenger, status=Duel.Status.OPEN).count()
    if open_count >= MAX_OPEN_PER_USER:
        raise DuelError("too_many", f"Bir vaqtda ko'pi bilan {MAX_OPEN_PER_USER} ta ochiq chaqiriq")
    return Duel.objects.create(
        challenger=challenger,
        title=title,
        problem_count=problem_count,
        difficulty=difficulty,
        duration_minutes=duration_minutes,
        start_at=start_at,
    )


def pick_problems(duel: Duel) -> list[Problem]:
    """Ikkalasi ham yechmagan masalalar, qiyinlik oynasi ichidan tasodifiy.

    Oyna yetmasa kengaytiriladi — bo'sh duel yaratishdan ko'ra qiyinroq
    masala yaxshi. Tasodif `random.Random(duel.pk)` bilan: yakunlash
    qayta chaqirilsa ham to'plam o'zgarmaydi.
    """
    solved_by_either = UserSolvedProblem.objects.filter(user__in=duel.participants()).values_list(
        "problem_id", flat=True
    )
    window = DIFFICULTY_WINDOW
    while True:
        pool = list(
            Problem.objects.filter(
                is_public=True,
                difficulty__gte=duel.difficulty - window,
                difficulty__lte=duel.difficulty + window,
            )
            .exclude(pk__in=solved_by_either)
            .order_by("pk")
        )
        if len(pool) >= duel.problem_count or window >= 3000:
            break
        window += DIFFICULTY_WINDOW
    if not pool:
        raise DuelError("no_problems", "Mos masala topilmadi")
    rng = random.Random(duel.pk)
    return rng.sample(pool, min(duel.problem_count, len(pool)))


@transaction.atomic
def accept(opponent: User, duel: Duel) -> Duel:
    duel = Duel.objects.select_for_update().get(pk=duel.pk)
    if duel.status != Duel.Status.OPEN:
        raise DuelError("not_open", "Chaqiriq endi ochiq emas")
    if duel.challenger_id == opponent.pk:
        raise DuelError("self", "O'z chaqirig'ingizni qabul qila olmaysiz")
    if duel.start_at <= timezone.now():
        raise DuelError("expired", "Boshlanish vaqti o'tib ketgan")

    duel.opponent = opponent
    duel.status = Duel.Status.ACCEPTED
    duel.save(update_fields=["opponent", "status"])
    for i, problem in enumerate(pick_problems(duel), start=1):
        DuelProblem.objects.create(duel=duel, problem=problem, order=i)

    from notifications.models import Notification
    from notifications.services import notify

    notify(
        duel.challenger,
        Notification.Kind.DUEL,
        f"{opponent.username} chaqirig'ingizni qabul qildi",
        body=f"«{duel.title}» {timezone.localtime(duel.start_at):%d.%m %H:%M} da boshlanadi.",
        ref_type="duel",
        ref_id=duel.slug,
    )
    return duel


def cancel(user: User, duel: Duel) -> Duel:
    if duel.challenger_id != user.pk:
        raise DuelError("forbidden", "Faqat chaqiruvchi bekor qila oladi")
    if duel.status != Duel.Status.OPEN:
        raise DuelError("not_open", "Faqat ochiq chaqiriqni bekor qilish mumkin")
    duel.status = Duel.Status.CANCELLED
    duel.save(update_fields=["status"])
    return duel


def solved_in_window(duel: Duel, user: User) -> tuple[int, datetime | None]:
    """Nechta masala yechildi va oxirgi AC qachon (teng bo'lsa tezroq yutadi)."""
    accepted = (
        Attempt.objects.filter(
            user=user,
            problem__in=duel.problems.all(),
            verdict=Verdict.AC,
            created_at__gte=duel.start_at,
            created_at__lt=duel.end_at,
        )
        .values("problem_id")
        .order_by("problem_id")
    )
    problem_ids = {row["problem_id"] for row in accepted}
    last = (
        Attempt.objects.filter(
            user=user,
            problem_id__in=problem_ids,
            verdict=Verdict.AC,
            created_at__gte=duel.start_at,
            created_at__lt=duel.end_at,
        )
        .order_by("-created_at")
        .values_list("created_at", flat=True)
        .first()
    )
    return len(problem_ids), last


@transaction.atomic
def finalize(duel: Duel) -> bool:
    """Tugagan duelni yakunlaydi: natija, Elo, bildirishnoma, Qvant."""
    duel = Duel.objects.select_for_update().get(pk=duel.pk)
    if not duel.is_due or duel.opponent is None:
        return False

    a, b = duel.challenger, duel.opponent
    a_solved, a_last = solved_in_window(duel, a)
    b_solved, b_last = solved_in_window(duel, b)

    if a_solved != b_solved:
        winner = a if a_solved > b_solved else b
    elif a_solved == 0:
        winner = None  # ikkalasi hech narsa yechmadi — durang
    elif a_last and b_last and a_last != b_last:
        winner = a if a_last < b_last else b  # teng, lekin tezroq
    else:
        winner = None

    duel.challenger_solved = a_solved
    duel.opponent_solved = b_solved
    duel.winner = winner
    duel.is_draw = winner is None
    duel.status = Duel.Status.FINISHED
    duel.save()

    from ratings.services import apply_duel_ratings

    apply_duel_ratings(duel)

    from notifications.models import Notification
    from notifications.services import notify
    from qvant import ledger
    from qvant.models import QvantTransaction

    for user in (a, b):
        outcome = "durang" if winner is None else ("g'alaba" if winner == user else "mag'lubiyat")
        notify(
            user,
            Notification.Kind.DUEL,
            f"Duel tugadi: {outcome}",
            body=f"«{duel.title}» — {a.username} {a_solved} : {b_solved} {b.username}",
            ref_type="duel",
            ref_id=duel.slug,
        )
    if winner is not None:
        ledger.credit(
            winner, DUEL_WIN_QVANT, QvantTransaction.Reason.DUEL, ref_type="duel", ref_id=duel.slug
        )

    duel.ratings_applied_at = timezone.now()
    duel.save(update_fields=["ratings_applied_at"])
    return True


DUEL_WIN_QVANT = 20


def record(user: User) -> dict[str, int]:
    """W/D/L — KEP'dagi kabi profil ko'rsatkichi."""
    finished = Duel.objects.filter(status=Duel.Status.FINISHED).filter(
        Q(challenger=user) | Q(opponent=user)
    )
    wins = finished.filter(winner=user).count()
    draws = finished.filter(is_draw=True).count()
    return {"wins": wins, "draws": draws, "losses": finished.count() - wins - draws}
