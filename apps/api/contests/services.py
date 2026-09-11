"""Standings hisoblash — ACM penalty va reyting yakunlash."""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from django.db import transaction
from django.utils import timezone

from contests.models import Contest, ContestProblem, ContestRegistration, Standing
from judging.models import Attempt
from judging.verdicts import Verdict

log = logging.getLogger(__name__)

#: ACM: har noto'g'ri urinish uchun jarima (daqiqa)
WRONG_ATTEMPT_PENALTY_MIN = 20

#: IOI: masalaning to'liq bali (judge shu shkalada qaytaradi).
MAX_PROBLEM_SCORE = 100


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
    #: IOI bali. ACM da ishlatilmaydi — u yerda tartibni `solved` belgilaydi.
    total: int = 0


@transaction.atomic
def rebuild_standings(contest: Contest) -> int:
    """Contest standings ni qayta quradi.

    ACM: yechilgan masalalar soni ↓, keyin penalty ↑.
    Penalty = (birinchi AC vaqti daqiqada) + 20 × (AC gacha noto'g'ri urinishlar).

    IOI: BALL ↓, keyin oxirgi ball olingan vaqt ↑. Jarima yo'q — IOI da
    noto'g'ri urinish jazolanmaydi, har masaladan eng yaxshi natija
    olinadi.
    """
    problem_ids = list(
        ContestProblem.objects.filter(contest=contest).values_list("problem_id", flat=True)
    )
    if not problem_ids:
        return 0

    # Rasmiy jadvalga FAQAT musobaqa oynasida yuborilgan urinishlar
    # kiradi. Shu bilan virtual ishtirok ham chetda qoladi: `start_virtual`
    # faqat TUGAGAN musobaqada ishlaydi, ya'ni virtual urinish har doim
    # `end_at` dan keyin turadi.
    #
    # Ilgari bu yerda foydalanuvchi bo'yicha chiqarib tashlash turardi va
    # musobaqada haqiqatan qatnashgan odam keyin uni virtual takrorlasa,
    # RASMIY natijasi jadvaldan o'chib ketardi (o'lchandi).
    #
    # Pastki chegara ataylab ochiq: rejudge yoki keyin o'zgartirilgan
    # `start_at` tufayli urinish musobaqa boshidan oldin turishi mumkin —
    # bunday urinishning jarimasi quyida nolga qisiladi.
    attempts = (
        Attempt.objects.filter(
            contest=contest, problem_id__in=problem_ids, created_at__lt=contest.end_at
        )
        .order_by("created_at")
        .values("user_id", "problem_id", "verdict", "created_at", "score")
    )
    # ICPC muzlatishi: oxirgi daqiqalarda jadval freeze paytidagi holatda
    # qotadi. Kesish URINISHLAR bo'yicha, rebuild'ni butunlay o'tkazib
    # yuborish bo'yicha emas — aks holda freeze'dan sal oldin kelgan AC
    # debounce tufayli navbatga tushib, jadvalga umuman kirmay qolardi.
    # Contest tugagach `is_frozen` False bo'ladi va `finalize_contest`
    # to'liq, haqiqiy jadvalni quradi.
    if contest.is_frozen:
        attempts = attempts.filter(created_at__lt=contest.freeze_at)

    if contest.scoring_type == Contest.Scoring.IOI:
        return _rebuild_ioi(contest, attempts)

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
            # Manfiy daqiqa `PositiveIntegerField` cheklovini buzadi va
            # BUTUN jadval qurilishini to'xtatadi — bitta qator emas.
            # Urinish start'dan oldin turishi mumkin: rejudge yoki
            # `start_at` keyin o'zgartirilgan bo'lsa.
            minutes = max(0, int((state.solved_at - contest.start_at).total_seconds() // 60))
            penalty += minutes + WRONG_ATTEMPT_PENALTY_MIN * state.wrong
            if last_ac is None or state.solved_at > last_ac:
                last_ac = state.solved_at
        rows.append(_Row(user_id, solved, penalty, last_ac))

    rows.sort(key=lambda r: (-r.solved, r.penalty))
    return _write(contest, rows, score=lambda r: r.solved)


def _write(contest: Contest, rows: list[_Row], score: Callable[[_Row], int]) -> int:
    """Saralangan qatorlarni jadvalga yozadi — tartib ALLAQACHON berilgan."""
    Standing.objects.filter(contest=contest).delete()
    Standing.objects.bulk_create(
        [
            Standing(
                contest=contest,
                user_id=row.user_id,
                rank=i + 1,
                solved_count=row.solved,
                penalty=row.penalty,
                total_score=score(row),
                last_ac_at=row.last_ac,
            )
            for i, row in enumerate(rows)
        ]
    )
    return len(rows)


def _rebuild_ioi(contest: Contest, attempts: Any) -> int:
    """IOI jadvali — ball bo'yicha.

    O'lchandi: `scoring_type` tanlanardi, judge qisman ballarni to'g'ri
    hisoblardi, jadval esa uni UMUMAN o'qimasdi va hammani ACM qoidasi
    bilan saralardi — 270 ballik ishtirokchi 200 ballikdan pastda turardi.

    Har masaladan ENG YAXSHI urinish olinadi (IOI shunday), jarima yo'q.
    Tenglikda oxirgi ball olingan vaqt erta bo'lgani yuqori turadi.
    """
    best: dict[int, dict[int, tuple[int, datetime]]] = {}
    for a in attempts:
        got = int(a["score"] or 0)
        rows = best.setdefault(a["user_id"], {})
        current = rows.get(a["problem_id"])
        if current is None or got > current[0]:
            rows[a["problem_id"]] = (got, a["created_at"])

    rows_out: list[_Row] = []
    for user_id, per_problem in best.items():
        total = sum(score for score, _ in per_problem.values())
        scoring = [when for score, when in per_problem.values() if score > 0]
        rows_out.append(
            _Row(
                user_id=user_id,
                # `solved` — TO'LIQ yechilganlar soni; jadvalda ko'rsatiladi,
                # lekin IOI da tartibni BALL belgilaydi.
                solved=sum(1 for score, _ in per_problem.values() if score >= MAX_PROBLEM_SCORE),
                penalty=0,
                last_ac=max(scoring) if scoring else None,
            )
        )
        rows_out[-1].total = total

    rows_out.sort(key=lambda r: (-r.total, r.last_ac or contest.end_at))
    return _write(contest, rows_out, score=lambda r: r.total)


@transaction.atomic
def create_mirror(source: Contest, slug: str, start_at, title: str = "") -> Contest:  # type: ignore[no-untyped-def]
    """PRD P2-1 — rasmiy olimpiadaning ko'zgu nusxasi.

    Masalalar va scoring asl musobaqadan ko'chiriladi, vaqt esa yangi.
    Mirror **reytingsiz** yaratiladi: asl musobaqa ishtirokchilari
    javoblarni bilishadi, ya'ni reytingga qo'shish adolatsiz bo'lardi.
    Kerak bo'lsa admin uni qo'lda `is_rated` qilishi mumkin.
    """
    duration = source.end_at - source.start_at
    mirror = Contest.objects.create(
        slug=slug,
        title=title or f"{source.title} (mirror)",
        description=source.description,
        start_at=start_at,
        end_at=start_at + duration,
        freeze_minutes=source.freeze_minutes,
        scoring_type=source.scoring_type,
        is_rated=False,
        is_public=source.is_public,
        mirror_of=source,
    )
    ContestProblem.objects.bulk_create(
        [
            ContestProblem(
                contest=mirror,
                problem=cp.problem,
                index_letter=cp.index_letter,
                points=cp.points,
            )
            for cp in ContestProblem.objects.filter(contest=source)
        ]
    )
    log.info("mirror yaratildi: %s ← %s", mirror.slug, source.slug)
    return mirror


@transaction.atomic
def start_virtual(contest: Contest, user) -> ContestRegistration:  # type: ignore[no-untyped-def]
    """PRD P1-1 — arxivdagi musobaqani o'z vaqtingizda boshlash.

    Virtual ishtirok **reytingga ta'sir qilmaydi**: `apply_contest_ratings`
    faqat `Standing` jadvalidan o'qiydi, virtual urinishlar esa u yerga
    tushmaydi (`rebuild_standings` `virtual_start_at is null` bo'yicha
    filtrlaydi). Aks holda kimdir javoblarni bilib turib reyting yig'ardi.
    """
    if not contest.is_finished:
        raise ValueError("Virtual ishtirok faqat tugagan musobaqada mumkin")

    reg, _ = ContestRegistration.objects.get_or_create(contest=contest, user=user)
    if reg.virtual_start_at is None:
        reg.virtual_start_at = timezone.now()
        reg.save(update_fields=["virtual_start_at"])
    return reg


def virtual_deadline(reg: ContestRegistration) -> datetime:
    """Virtual ishtirokchi uchun tugash vaqti — asl musobaqa davomiyligi."""
    duration = reg.contest.end_at - reg.contest.start_at
    assert reg.virtual_start_at is not None
    return reg.virtual_start_at + duration


@transaction.atomic
def finalize_contest(contest: Contest) -> int:
    """Musobaqa tugagach: standings + Contests reytingi.

    Qulf `duels.finalize` dagi kabi: `ratings_applied_at` ni o'qish va
    yozish orasi ochiq qolsa, ikkinchi ishchi shu oraliqda kirib oladi.
    Beat `finalize_due` ni har 60 soniyada yuboradi, worker esa ikkita
    jarayonda ishlaydi — 10 ming ishtirokchili musobaqa 60 soniyadan
    uzoq yakunlansa ikki chaqiruv ustma-ust tushadi.

    O'lchandi (preview, 12 ishtirokchi): reyting to'g'ri qoldi —
    `bulk_update` mutlaq qiymat yozadi — lekin `RatingHistory` 24 qator
    va bildirishnoma ham 24 ta bo'ldi. Reyting tarixi principle #2 ning
    tushuntirish yuzasi, ya'ni ikkilangan qator uni buzadi.
    """
    contest = Contest.objects.select_for_update().get(pk=contest.pk)
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
        try:
            from profiles.achievements import on_rated_contest

            for standing in Standing.objects.filter(contest=contest).select_related("user"):
                with transaction.atomic():
                    on_rated_contest(standing.user)
        except Exception:
            log.exception("contest %s uchun yutuqlar tekshirilmadi", contest.slug)
    contest.ratings_applied_at = timezone.now()
    contest.save(update_fields=["ratings_applied_at"])

    # Bu contest chempionat bosqichi bo'lsa — yig'ma jadval yangilanadi.
    # Import ichkarida: tournaments contests'ga bog'liq, teskarisi emas.
    from tournaments.services import rebuild_for_contest

    rebuild_for_contest(contest.pk)
    log.info("contest %s yakunlandi — %s ishtirokchi reytingi yangilandi", contest.slug, affected)
    return affected
