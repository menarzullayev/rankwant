"""Arena mexanikasi: qo'shilish, javob, ball, yakunlash."""

from __future__ import annotations

import logging

from django.db import transaction
from django.db.models import F, Q
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
    """Tezlikka bog'liq ball — MIN_POINTS bilan MAX_POINTS orasida.

    Yuqoridan ham qisiladi: manfiy `elapsed_ms` MAX_POINTS dan oshiq ball
    berardi (−100 ms → 1002). Server vaqtni o'zi hisoblagani uchun bunga
    yo'l yo'q, lekin formula ochiq e'lon qilingan (principle #2) va
    chegarasi kafolat bo'lishi kerak.
    """
    fraction_left = min(1.0, max(0.0, 1 - elapsed_ms / (limit_s * 1000)))
    return max(MIN_POINTS, round(MAX_POINTS * fraction_left))


def join(user: User, arena: ArenaRound) -> ArenaParticipation:
    if arena.is_finished:
        raise ArenaError("finished", "The round has finished")
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
        raise ArenaError("not_running", "The round is not running right now")
    item = arena.items.select_related("question").filter(order=index + 1).first()
    if item is None or item.question_id != question_id:
        raise ArenaError("wrong_question", "That question is not open right now")

    try:
        participation = ArenaParticipation.objects.select_for_update().get(round=arena, user=user)
    except ArenaParticipation.DoesNotExist as exc:
        raise ArenaError("not_joined", "Join the round first") from exc
    if ArenaAnswer.objects.filter(participation=participation, question_id=question_id).exists():
        raise ArenaError("already_answered", "This question has already been answered")

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


#: Jadvalning ko'rinadigan qismi — contests bilan bir xil chegara.
#: Cheklovsiz qoldirilganda 10 000 ishtirokchi 1.19 MB javob berardi va
#: SSE oqimi uni HAR 3 SONIYADA har bir tomoshabinga yuborardi.
TOP_LIMIT = 500


def standings(arena: ArenaRound, limit: int = TOP_LIMIT) -> list[dict[str, object]]:
    rows = ArenaParticipation.objects.filter(round=arena).select_related("user")[:limit]
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


def my_standing(arena: ArenaRound, user: User) -> dict[str, object] | None:
    """Foydalanuvchining O'Z qatori — `TOP_LIMIT` dan pastda bo'lsa ham.

    Ommaviy jadval chekkada keshlanadi, ya'ni unga shaxsiy qator qo'shib
    bo'lmaydi. O'rin `Meta.ordering` bilan BIR XIL mezon bo'yicha
    sanaladi (`-score, total_ms, joined_at`) — aks holda ikkita joyda
    ikki xil o'rin ko'rinardi.
    """
    row = ArenaParticipation.objects.filter(round=arena, user=user).select_related("user").first()
    if row is None:
        return None

    oldinda = (
        ArenaParticipation.objects.filter(round=arena)
        .filter(
            Q(score__gt=row.score)
            | Q(score=row.score, total_ms__lt=row.total_ms)
            | Q(score=row.score, total_ms=row.total_ms, joined_at__lt=row.joined_at)
        )
        .count()
    )
    return {
        "rank": oldinda + 1,
        "username": row.user.username,
        "display_name": row.user.display_name,
        "score": row.score,
        "correct_count": row.correct_count,
        "total_ms": row.total_ms,
    }


@transaction.atomic
def finalize(arena: ArenaRound) -> int:
    """Raund tugagach ishtirokchilarga Qvant. Bir marta — `rewards_applied_at`.

    «Bir marta» qulf bilan ta'minlanadi: `ledger.credit` hamyonni qulflaydi
    va kunlik shiftni hisobga oladi, lekin `(ref_type, ref_id)` bo'yicha
    takrorni tanimaydi — o'sha mukofot ikki marta kelsa ikkalasini ham
    yozadi. O'lchandi (preview, 6 ishtirokchi): parallel ikki chaqiruv
    12 tranzaksiya yozdi va har kimning balansi 15 o'rniga 30 bo'ldi.
    """
    arena = ArenaRound.objects.select_for_update().get(pk=arena.pk)
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
