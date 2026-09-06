"""Arena mexanikasi: qo'shilish, javob, ball, yakunlash."""

from __future__ import annotations

import logging

from django.db import transaction
from django.db.models import F
from django.utils import timezone

from arena.models import ArenaAnswer, ArenaParticipation, ArenaRound
from core.models import User
from quizzes.models import Choice
from qvant import ledger
from qvant.models import QvantTransaction

log = logging.getLogger(__name__)

#: To'g'ri javob uchun maksimal ball; qolgan vaqtga proporsional kamayadi,
#: lekin oxirgi soniyada ham MIN_POINTS beriladi — to'g'ri javob nol emas.
MAX_POINTS = 1000
MIN_POINTS = 100


class ArenaError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def points_for(elapsed_ms: int, limit_s: int) -> int:
    fraction_left = max(0.0, 1 - elapsed_ms / (limit_s * 1000))
    return max(MIN_POINTS, round(MAX_POINTS * fraction_left))


def join(user: User, arena: ArenaRound) -> ArenaParticipation:
    if arena.is_finished:
        raise ArenaError("finished", "Raund tugagan")
    participation, _ = ArenaParticipation.objects.get_or_create(round=arena, user=user)
    return participation


@transaction.atomic
def answer(user: User, arena: ArenaRound, question_id: int, choice_id: int) -> ArenaAnswer:
    """Faqat JORIY savolga, faqat bir marta.

    Joriy savol server vaqtidan olinadi: mijoz eski savolga kech javob
    yubora olmaydi va kelgusi savolni oldindan ko'ra olmaydi.
    """
    index = arena.current_index
    if index is None:
        raise ArenaError("not_running", "Raund hozir yurmayapti")
    item = arena.items.select_related("question").filter(order=index + 1).first()
    if item is None or item.question_id != question_id:
        raise ArenaError("wrong_question", "Bu savol hozir ochiq emas")

    try:
        participation = ArenaParticipation.objects.select_for_update().get(round=arena, user=user)
    except ArenaParticipation.DoesNotExist as exc:
        raise ArenaError("not_joined", "Avval raundga qo'shiling") from exc
    if ArenaAnswer.objects.filter(participation=participation, question_id=question_id).exists():
        raise ArenaError("already_answered", "Bu savolga javob berilgan")

    choice = Choice.objects.filter(pk=choice_id, question_id=question_id).first()
    if choice is None:
        raise ArenaError("bad_choice", "Variant bu savolga tegishli emas")

    opened_at = arena.question_deadline(index - 1) if index else arena.start_at
    elapsed_ms = int((timezone.now() - opened_at).total_seconds() * 1000)
    points = points_for(elapsed_ms, arena.seconds_per_question) if choice.is_correct else 0

    record = ArenaAnswer.objects.create(
        participation=participation,
        question_id=question_id,
        choice=choice,
        is_correct=choice.is_correct,
        elapsed_ms=elapsed_ms,
        points=points,
    )
    ArenaParticipation.objects.filter(pk=participation.pk).update(
        score=F("score") + points,
        correct_count=F("correct_count") + (1 if choice.is_correct else 0),
        total_ms=F("total_ms") + elapsed_ms,
    )
    return record


def standings(arena: ArenaRound) -> list[dict[str, object]]:
    rows = ArenaParticipation.objects.filter(round=arena).select_related("user")
    return [
        {
            "rank": i + 1,
            "username": row.user.username,
            "display_name": row.user.display_name,
            "score": row.score,
            "correct_count": row.correct_count,
            "total_ms": row.total_ms,
        }
        for i, row in enumerate(rows)
    ]


@transaction.atomic
def finalize(arena: ArenaRound) -> int:
    """Raund tugagach ishtirokchilarga Qvant. Bir marta — `rewards_applied_at`."""
    if arena.rewards_applied_at is not None or not arena.is_finished:
        return 0
    awarded = 0
    for participation in ArenaParticipation.objects.filter(round=arena).select_related("user"):
        if participation.correct_count == 0:
            continue  # kirib hech narsa qilmagan — mukofot yo'q (anti-farm)
        tx = ledger.credit(
            participation.user,
            arena.reward_qvant,
            QvantTransaction.Reason.ARENA,
            ref_type="arena",
            ref_id=arena.slug,
        )
        if tx:
            awarded += 1
    arena.rewards_applied_at = timezone.now()
    arena.save(update_fields=["rewards_applied_at"])
    log.info("arena %s yakunlandi — %s ishtirokchiga Qvant", arena.slug, awarded)
    return awarded
