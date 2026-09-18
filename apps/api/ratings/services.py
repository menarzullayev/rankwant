"""Reyting hisoblash — formulalar `ratings.formulas` da, DB mantiqi shu yerda."""

from __future__ import annotations

import logging
from functools import partial

from django.db import models, transaction
from django.utils import timezone

from core.models import User
from judging.models import Attempt
from judging.verdicts import Verdict
from ratings import formulas
from ratings.models import RatingHistory, UserSolvedProblem

log = logging.getLogger(__name__)


def bump_max_rating(user: User, rating_type: str, value: int) -> None:
    """Raise the stored maximum for `rating_type` to `value` if it is higher.

    Call it wherever a `RatingHistory` row is written: the column mirrors
    `MAX(value_after)`. The update is a single SQL expression, so concurrent
    writers cannot lower it.
    """
    from django.db.models import F, Value
    from django.db.models.functions import Coalesce, Greatest

    from core.user_stats import MAX_RATING_FIELDS

    field = MAX_RATING_FIELDS[rating_type]
    User.objects.filter(pk=user.pk).update(
        **{field: Greatest(Coalesce(F(field), Value(value)), Value(value))}
    )
    current = getattr(user, field)
    setattr(user, field, value if current is None else max(current, value))


def _record(
    user: User,
    rating_type: str,
    before: int,
    after: int,
    reason: str,
    *,
    ref_type: str = "",
    ref_id: str = "",
    seed: float | None = None,
    rank: int | None = None,
) -> None:
    if before == after:
        return
    RatingHistory.objects.create(
        user=user,
        rating_type=rating_type,
        value_before=before,
        value_after=after,
        delta=after - before,
        reason=reason,
        ref_type=ref_type,
        ref_id=str(ref_id),
        seed=seed,
        rank=rank,
    )
    bump_max_rating(user, rating_type, after)


@transaction.atomic
def recalc_skills(
    user: User, reason: str = RatingHistory.Reason.PROBLEM_SOLVED, ref_id: str = ""
) -> int:
    """Skills ni JORIY qiyinliklardan qayta hisoblaydi (ADR-0007)."""
    difficulties = list(
        UserSolvedProblem.objects.filter(user=user)
        .select_related("problem")
        .values_list("problem__difficulty", flat=True)
    )
    new_value = formulas.skills_rating(difficulties)
    before = user.rating_skills
    if new_value != before:
        user.rating_skills = new_value
        user.save(update_fields=["rating_skills"])
        _record(
            user,
            RatingHistory.Type.SKILLS,
            before,
            new_value,
            reason,
            ref_type="problem",
            ref_id=ref_id,
        )
        if reason == RatingHistory.Reason.PROBLEM_RERATED:
            # ADR-0007 sharti: reyting foydalanuvchi HARAKATISIZ o'zgardi —
            # sababini ko'rsatmasak principle #2 buziladi.
            from notifications.models import Notification
            from notifications.services import notify

            notify(
                user,
                Notification.Kind.PROBLEM_RERATED,
                f"Skills reytingingiz {new_value - before:+d} ga o'zgardi",
                body=(
                    f"Siz yechgan masala qayta baholandi. "
                    f"Skills: {before} → {new_value}. Bu sizning harakatingiz "
                    f"emas — masala qiyinligi statistika asosida yangilandi."
                ),
                ref_type="problem",
                ref_id=ref_id,
            )
    return new_value


def _profile_stats_changed(user_id: int) -> None:
    """Profil statistikasi keshini commitdan KEYIN eskirtiradi.

    Tranzaksiya ichida eskirtirilsa, parallel so'rov hali commit bo'lmagan
    eski ma'lumotni yangi versiya ostida keshlab qo'yardi. `robust` — kesh
    xatosi verdiktni to'xtatmaydi.
    """
    from profiles.stats import bump

    transaction.on_commit(partial(bump, user_id), robust=True)


@transaction.atomic
def on_attempt_judged(attempt: Attempt) -> None:
    """Verdict yozilgandan keyin chaqiriladi."""
    _profile_stats_changed(attempt.user_id)
    if attempt.verdict != Verdict.AC:
        return

    _, created = UserSolvedProblem.objects.get_or_create(
        user=attempt.user,
        problem=attempt.problem,
        defaults={
            "first_ac_attempt": attempt,
            "difficulty_at_solve": attempt.problem.difficulty,
        },
    )
    if not created:
        return  # faqat birinchi AC

    from django.db.models import F

    type(attempt.problem).objects.filter(pk=attempt.problem_id).update(
        solved_count=F("solved_count") + 1
    )
    # Public problems only, the same rule as the profile's solved figures:
    # a hidden contest problem must not show up in a public count.
    if attempt.problem.is_public:
        User.objects.filter(pk=attempt.user_id).update(solved_count=F("solved_count") + 1)
    recalc_skills(attempt.user, ref_id=attempt.problem.slug)

    # Phase 1 — Qvant va Activity. Qvant hodisasi Skills dan KEYIN:
    # reyting yozuvi Qvant xatosidan qat'i nazar saqlanishi kerak.
    try:
        from qvant.services import on_first_accepted

        on_first_accepted(attempt.user)
    except Exception:
        # Qvant retention mexanizmi; u yiqilsa ham verdict va Skills
        # to'g'ri qolishi shart.
        log.exception("Qvant hodisasi bajarilmadi: attempt %s", attempt.pk)


@transaction.atomic
def on_accept_revoked(attempt: Attempt) -> None:
    """Rejudge AC ni bekor qildi — ADR-0002 qaytarish qoidasi.

    Yechilgan masala yozuvi olib tashlanadi, Skills qayta hisoblanadi va
    shu urinish uchun berilgan Qvant qaytariladi.
    """
    _profile_stats_changed(attempt.user_id)
    row = UserSolvedProblem.objects.filter(
        user=attempt.user, problem=attempt.problem, first_ac_attempt=attempt
    ).first()
    if row is None:
        return

    # Bir masalaga bir necha AC odatiy — odam yechimini optimallashtiradi.
    # Rejudge faqat birinchisini yiqitsa (masalan checker qattiqlashdi),
    # keyingisi hali AC: masala YECHILGANICHA qoladi va yozuv o'sha
    # urinishga ko'chadi. Aks holda foydalanuvchida ishlaydigan yechim
    # bo'la turib masala «yechilmagan» ko'rinardi va yechuvchilar sanog'i
    # ham asossiz kamayardi.
    keyingi = (
        Attempt.objects.filter(user=attempt.user, problem=attempt.problem, verdict=Verdict.AC)
        .exclude(pk=attempt.pk)
        .order_by("created_at", "pk")
        .first()
    )
    if keyingi is not None:
        row.first_ac_attempt = keyingi
        row.first_ac_at = keyingi.created_at
        row.save(update_fields=["first_ac_attempt", "first_ac_at"])
        return

    row.delete()

    from django.db.models import F, Value
    from django.db.models.functions import Greatest

    # Nol ostiga TUSHMAYDI. `solved_count` — musbat maydon, ya'ni sanoq
    # qatorlardan past bo'lib qolgan holatda bu `update` CHECK xatosi
    # berib BUTUN tranzaksiyani yiqitardi (o'lchandi: `sqlite3.
    # IntegrityError: CHECK constraint failed: solved_count`). Bekor
    # qilish yolg'iz ishlamaydi: uni hack dvigateli ham chaqiradi
    # (`hacks.services._finish`), demak begona sabab hackni abadiy
    # `TESTING` da qoldirardi.
    #
    # Sanoq qatorlardan qanday ajralib ketadi: `UserSolvedProblem` kodni
    # chetlab yo'qolganda — foydalanuvchi o'chirilishi (kaskad), import
    # yoki qo'lda tuzatish. Haqiqatga tenglashtirish uchun alohida vosita
    # bor: `python manage.py recount_problems`.
    type(attempt.problem).objects.filter(pk=attempt.problem_id).update(
        solved_count=Greatest(F("solved_count") - 1, Value(0))
    )
    # Same floor as above: the counter may already be behind the rows.
    if attempt.problem.is_public:
        User.objects.filter(pk=attempt.user_id).update(
            solved_count=Greatest(F("solved_count") - 1, Value(0))
        )
    recalc_skills(
        attempt.user,
        reason=RatingHistory.Reason.RECALCULATION,
        ref_id=attempt.problem.slug,
    )
    try:
        from qvant.services import revoke_for_attempt

        revoke_for_attempt(attempt.user, timezone.localtime(attempt.created_at).date())
    except Exception:
        log.exception("Qvant qaytarilmadi: attempt %s", attempt.pk)
    try:
        from profiles.achievements import on_unsolved

        with transaction.atomic():
            on_unsolved(attempt.user)
    except Exception:
        log.exception("yutuq qaytarilmadi: attempt %s", attempt.pk)


def on_problem_visibility_changed(problem_id: int, is_public: bool) -> None:
    """Move every solver of the problem by one when it is published or hidden.

    `User.solved_count` counts public problems only (ADR-0024). A queryset
    `update(is_public=...)` bypasses this; `recount_user_stats` repairs that.
    """
    from django.db.models import F, Value
    from django.db.models.functions import Greatest

    solvers = User.objects.filter(solved__problem_id=problem_id)
    if is_public:
        solvers.update(solved_count=F("solved_count") + 1)
    else:
        solvers.update(solved_count=Greatest(F("solved_count") - 1, Value(0)))


@transaction.atomic
def recalc_skills_for_problem(problem_id: int) -> int:
    """Masala qayta baholanganda — ADR-0007.

    Bu ARZON OPERATSIYA EMAS: mashhur masalada minglab foydalanuvchi
    qayta hisoblanadi. Partiyada va e'lon bilan bajarilishi kerak.
    """
    user_ids = UserSolvedProblem.objects.filter(problem_id=problem_id).values_list(
        "user_id", flat=True
    )
    count = 0
    for user in User.objects.filter(pk__in=list(user_ids)):
        recalc_skills(user, reason=RatingHistory.Reason.PROBLEM_RERATED, ref_id=str(problem_id))
        count += 1
    log.info("masala %s qayta baholandi — %s foydalanuvchi yangilandi", problem_id, count)
    return count


@transaction.atomic
def apply_contest_ratings(contest) -> int:  # type: ignore[no-untyped-def]
    """Musobaqa yakunlangach Contests reytingini yangilaydi.

    Faqat `is_rated` va >= MIN_RATED_PARTICIPANTS ishtirokchi bo'lganda.
    """
    from contests.models import Standing

    if not contest.is_rated:
        return 0

    standings = list(
        Standing.objects.filter(contest=contest).select_related("user").order_by("rank")
    )
    if len(standings) < formulas.MIN_RATED_PARTICIPANTS:
        log.info("contest %s: %s ishtirokchi — reyting hisoblanmadi", contest.pk, len(standings))
        return 0

    users = [s.user for s in standings]
    ratings = [u.rating_contest for u in users]
    ranks = [s.rank for s in standings]
    counts = [u.rated_contest_count for u in users]

    deltas = formulas.contest_deltas(ratings, ranks, counts)
    # Har bir yozuv uchun alohida `seed()` chaqirish yana O(n²) berardi.
    seeds = formulas.contest_seeds(ratings)

    from notifications.models import Notification

    # 10 000 ishtirokchida qatorma-qator yozish 30 000 so'rov beradi va
    # ularning hammasi BITTA tranzaksiyada 10 000 user qatorini qulflab
    # turadi (o'lchandi: 3 so'rov/kishi). Partiyada yoziladi.
    histories: list[RatingHistory] = []
    notes: list[Notification] = []

    for i, (user, standing, delta) in enumerate(zip(users, standings, deltas, strict=True)):
        before = user.rating_contest
        after = formulas.apply_floor(before + delta)
        user.rating_contest = after
        user.rated_contest_count += 1

        if before != after:
            # Mirrors `bump_max_rating`, which this batch path cannot call per row.
            if user.max_rating_contest is None or after > user.max_rating_contest:
                user.max_rating_contest = after
            histories.append(
                RatingHistory(
                    user=user,
                    rating_type=RatingHistory.Type.CONTEST,
                    value_before=before,
                    value_after=after,
                    delta=after - before,
                    reason=RatingHistory.Reason.CONTEST,
                    ref_type="contest",
                    ref_id=contest.slug,
                    # Faqat O'ZINI chiqarib tashlaydi. Ilgari bu yerda
                    # `r != before` turardi va teng reytingdagilarning
                    # HAMMASI tashlab yuborilardi — 1200 da turgan yuzta
                    # yangi foydalanuvchi bir-birining seed'ini buzardi.
                    seed=seeds[i],
                    rank=standing.rank,
                )
            )
        notes.append(
            Notification(
                user=user,
                kind=Notification.Kind.CONTEST_RESULT,
                title=f"{contest.title}: {standing.rank}-o'rin, reyting {after - before:+d}",
                body=f"Contests reytingi: {before} → {after}",
                ref_type="contest",
                ref_id=contest.slug,
            )
        )

    User.objects.bulk_update(
        users, ["rating_contest", "rated_contest_count", "max_rating_contest"], batch_size=500
    )
    RatingHistory.objects.bulk_create(histories, batch_size=500)
    try:
        Notification.objects.bulk_create(notes, batch_size=500)
    except Exception:
        # Bildirishnoma reytingni ushlab qolmasligi kerak (notifications.notify).
        log.exception("contest %s natijalari e'lon qilinmadi", contest.slug)
    return len(standings)


@transaction.atomic
def apply_duel_ratings(duel) -> None:  # type: ignore[no-untyped-def]
    """Duel yakunlangach Challenges reytingi — klassik 1v1 Elo (ADR-0006).

    K yangi o'yinchi uchun katta (32), 10 dueldan keyin 16: dastlab tez
    joylashadi, keyin barqarorlashadi.
    """
    from duels.models import Duel

    a, b = duel.challenger, duel.opponent
    if duel.is_draw:
        score_a = score_b = 0.5
    else:
        score_a = 1.0 if duel.winner_id == a.pk else 0.0
        score_b = 1.0 - score_a

    def played(user) -> int:  # type: ignore[no-untyped-def]
        return (
            Duel.objects.filter(status=Duel.Status.FINISHED, ratings_applied_at__isnull=False)
            .filter(models.Q(challenger=user) | models.Q(opponent=user))
            .count()
        )

    ra, rb = a.rating_challenges, b.rating_challenges
    delta_a = formulas.duel_delta(ra, rb, score_a, played(a))
    delta_b = formulas.duel_delta(rb, ra, score_b, played(b))

    for user, before, delta in ((a, ra, delta_a), (b, rb, delta_b)):
        after = formulas.apply_floor(before + delta)
        user.rating_challenges = after
        user.save(update_fields=["rating_challenges"])
        _record(
            user,
            RatingHistory.Type.CHALLENGES,
            before,
            after,
            RatingHistory.Reason.DUEL,
            ref_type="duel",
            ref_id=duel.slug,
        )
