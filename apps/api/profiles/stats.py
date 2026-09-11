"""Profil statistikasi — faollik xaritasi, tillar, verdiktlar, masalalar xaritasi.

Hisob og'ir: 2 000 urinishli foydalanuvchida bir necha agregat so'rov,
masalalar xaritasi esa arxivdagi 1 200 dan ortiq masalani qamraydi.
Natija foydalanuvchi bo'yicha keshlanadi. Yangi urinish baholanganda
versiya oshadi (`bump`): eski yozuv o'chirilmaydi, shunchaki o'qilmay
qoladi va muddati bilan o'zi ketadi.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable
from datetime import date, datetime, timedelta
from typing import Any

from django.core.cache import cache
from django.db.models import Count, Max, Min, Q
from django.db.models.functions import TruncDate
from django.utils import timezone

from contests.models import Contest, ContestProblem, ContestRegistration, Standing
from core.cache import cache_get, cache_set
from core.models import User
from judging.models import Attempt
from judging.verdicts import Verdict
from problems.models import DIFFICULTY_LEVELS, Problem, difficulty_level
from profiles import titles
from ratings.models import RatingHistory, UserSolvedProblem

TTL = 60 * 60
#: Masalalar ro'yxati hamma uchun bir xil — alohida va qisqaroq keshda.
CATALOG_TTL = 10 * 60
#: Grafikda bir qatorga shuncha nuqta yetadi; ko'pi faqat sahifani og'irlashtiradi.
SERIES_LIMIT = 400

#: Statistikaga kirmaydi: hali tekshirilmagan, shiftga urilgan yoki infra va
#: muallif aybi (checker, test) — bular foydalanuvchining xatosi emas.
NOT_COUNTED = frozenset(
    {
        Verdict.PENDING,
        Verdict.RUNNING,
        Verdict.RATE_LIMITED,
        Verdict.TESTING_ABORTED,
        Verdict.IE,
        Verdict.WRONG_TEST,
        Verdict.CHECKER_ERROR,
        Verdict.DENIAL_OF_JUDGEMENT,
    }
)


def _version_key(user_id: int) -> str:
    return f"pstats:v:{user_id}"


def bump(user_id: int) -> None:
    """Foydalanuvchi statistikasini eskirtiradi."""
    try:
        cache.incr(_version_key(user_id))
    except ValueError:
        cache_set(_version_key(user_id), 1, None)
    except Exception:
        # Kesh yiqilgan — u holda o'qish ham ishlamaydi, eskirgan qiymat yo'q.
        pass


def cached(user_id: int, name: str, build: Callable[[], Any]) -> Any:
    version = cache_get(_version_key(user_id), 0)
    key = f"pstats:{user_id}:{version}:{name}"
    value = cache_get(key)
    if value is None:
        value = build()
        cache_set(key, value, TTL)
    return value


def _tz() -> Any:
    return timezone.get_current_timezone()


# ── Faollik xaritasi ─────────────────────────────────────────────────


def streaks(user: User) -> dict[str, int]:
    """Joriy va eng uzun streak — AC olingan kunlar (`qvant.streak` bilan bir qoida).

    Joriy qiymat `User.streak_count` dan: unda muzlatgich (freeze) ham
    hisobga olingan. Oxirgi faol kun kechadan oldin bo'lsa, streak uzilgan.
    """
    days = sorted(
        set(
            Attempt.objects.filter(user=user, verdict=Verdict.AC)
            .annotate(day=TruncDate("created_at", tzinfo=_tz()))
            .values_list("day", flat=True)
        )
    )
    longest = run = 0
    previous: date | None = None
    for day in days:
        run = run + 1 if previous is not None and day - previous == timedelta(days=1) else 1
        longest = max(longest, run)
        previous = day
    today = timezone.localdate()
    alive = user.last_active_date is not None and user.last_active_date >= today - timedelta(days=1)
    current = user.streak_count if alive else 0
    return {"current": current, "longest": max(longest, current)}


def calendar(user: User, year: int) -> dict[str, Any]:
    """Kunlik urinishlar va yechilgan (birinchi AC) masalalar soni."""
    tz = _tz()
    start = datetime(year, 1, 1, tzinfo=tz)
    end = datetime(year + 1, 1, 1, tzinfo=tz)
    days: dict[date, dict[str, int]] = {}
    for row in (
        Attempt.objects.filter(user=user, created_at__gte=start, created_at__lt=end)
        .exclude(verdict=Verdict.RATE_LIMITED)
        .annotate(day=TruncDate("created_at", tzinfo=tz))
        .values("day")
        .annotate(n=Count("id"))
    ):
        days.setdefault(row["day"], {"attempts": 0, "solved": 0})["attempts"] = row["n"]
    for row in (
        UserSolvedProblem.objects.filter(user=user, first_ac_at__gte=start, first_ac_at__lt=end)
        .annotate(day=TruncDate("first_ac_at", tzinfo=tz))
        .values("day")
        .annotate(n=Count("id"))
    ):
        days.setdefault(row["day"], {"attempts": 0, "solved": 0})["solved"] = row["n"]

    first = Attempt.objects.filter(user=user).aggregate(first=Min("created_at"))["first"]
    this_year = timezone.localdate().year
    first_year = timezone.localtime(first).year if first else this_year
    return {
        "year": year,
        "years": list(range(this_year, first_year - 1, -1)),
        "days": [{"date": day.isoformat(), **counts} for day, counts in sorted(days.items())],
        "attempts": sum(counts["attempts"] for counts in days.values()),
        "solved": sum(counts["solved"] for counts in days.values()),
        "streak": streaks(user),
    }


# ── Umumiy raqamlar ──────────────────────────────────────────────────


def _level_totals() -> dict[str, int]:
    value: dict[str, int] | None = cache_get("pstats:levels")
    if value is None:
        value = dict(
            Counter(
                difficulty_level(difficulty)[0]
                for difficulty in Problem.objects.filter(is_public=True).values_list(
                    "difficulty", flat=True
                )
            )
        )
        cache_set("pstats:levels", value, CATALOG_TTL)
    return value


def overview(user: User) -> dict[str, Any]:
    """Yechilgan/jami, daraja kesimi, tillar va verdiktlar ulushi."""
    counted = Attempt.objects.filter(user=user).exclude(verdict__in=NOT_COUNTED)
    languages = [
        {
            "code": row["language__code"],
            "name": row["language__name"],
            "accepted": row["accepted"],
            "errors": row["total"] - row["accepted"],
        }
        for row in counted.values("language__code", "language__name")
        .annotate(total=Count("id"), accepted=Count("id", filter=Q(verdict=Verdict.AC)))
        .order_by("-total", "language__code")
    ]
    verdicts = [
        {"verdict": row["verdict"], "count": row["n"]}
        for row in counted.values("verdict").annotate(n=Count("id")).order_by("-n", "verdict")
    ]
    solved = Counter(
        difficulty_level(value)[0]
        for value in UserSolvedProblem.objects.filter(
            user=user, problem__is_public=True
        ).values_list("problem__difficulty", flat=True)
    )
    totals = _level_totals()
    return {
        "solved": sum(solved.values()),
        "total": sum(totals.values()),
        "levels": [
            {"code": code, "label": label, "solved": solved[code], "total": totals.get(code, 0)}
            for _, code, label in DIFFICULTY_LEVELS
        ],
        "attempts": sum(row["count"] for row in verdicts),
        "accepted": next((row["count"] for row in verdicts if row["verdict"] == Verdict.AC), 0),
        "languages": languages,
        "verdicts": verdicts,
    }


# ── Masalalar xaritasi ───────────────────────────────────────────────


def _catalog() -> list[dict[str, Any]]:
    """Ommaviy masalalar — raqam tartibida, yechilish foizi bilan."""
    value: list[dict[str, Any]] | None = cache_get("pstats:catalog")
    if value is None:
        value = [
            {
                "id": pk,
                "code": code,
                "slug": slug,
                "title": title,
                "level": difficulty_level(difficulty)[0],
                # Masala ro'yxatidagi `success_rate` bilan bir xil hisob.
                "rate": round(solved / attempts * 100) if attempts else None,
            }
            for pk, code, slug, title, difficulty, solved, attempts in Problem.objects.filter(
                is_public=True
            )
            .order_by("code", "pk")
            .values_list(
                "pk", "code", "slug", "title", "difficulty", "solved_count", "attempt_count"
            )
        ]
        cache_set("pstats:catalog", value, CATALOG_TTL)
    return value


def problem_sets(user: User) -> tuple[set[int], set[int]]:
    """(yechilgan, urinilgan) masala ID'lari — keshda."""

    def build() -> dict[str, list[int]]:
        return {
            "solved": list(
                UserSolvedProblem.objects.filter(user=user).values_list("problem_id", flat=True)
            ),
            "attempted": list(
                Attempt.objects.filter(user=user).values_list("problem_id", flat=True).distinct()
            ),
        }

    sets: dict[str, list[int]] = cached(user.pk, "sets", build)
    return set(sets["solved"]), set(sets["attempted"])


def problem_map(user: User) -> dict[str, Any]:
    solved, attempted = problem_sets(user)
    rows = [
        {
            "code": row["code"],
            "slug": row["slug"],
            "title": row["title"],
            "level": row["level"],
            "rate": row["rate"],
            "state": (
                "solved"
                if row["id"] in solved
                else "attempted"
                if row["id"] in attempted
                else "untouched"
            ),
        }
        for row in _catalog()
    ]
    return {"problems": rows}


# ── Reyting grafigi ──────────────────────────────────────────────────


def _thin(points: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    """Nuqtalarni siqadi, lekin birinchi, oxirgi va eng yuqorisini saqlaydi."""
    if len(points) <= limit:
        return points
    step = len(points) / limit
    keep = {int(i * step) for i in range(limit)} | {0, len(points) - 1}
    keep.add(max(range(len(points)), key=lambda i: points[i]["after"]))
    return [points[i] for i in sorted(keep)]


def rating_series(user: User) -> dict[str, Any]:
    """To'rt reyting tarixi va unvon chegaralari."""
    rows = list(
        RatingHistory.objects.filter(user=user)
        .order_by("created_at", "pk")
        .values(
            "rating_type",
            "value_before",
            "value_after",
            "delta",
            "reason",
            "ref_type",
            "ref_id",
            "rank",
            "created_at",
        )
    )
    contest_titles = dict(
        Contest.objects.filter(
            slug__in={row["ref_id"] for row in rows if row["ref_type"] == "contest"}
        ).values_list("slug", "title")
    )
    series: dict[str, list[dict[str, Any]]] = {kind: [] for kind in RatingHistory.Type.values}
    for row in rows:
        series.setdefault(row["rating_type"], []).append(
            {
                "at": row["created_at"],
                "before": row["value_before"],
                "after": row["value_after"],
                "delta": row["delta"],
                "reason": row["reason"],
                "ref": row["ref_id"],
                "title": contest_titles.get(row["ref_id"], "")
                if row["ref_type"] == "contest"
                else "",
                "rank": row["rank"],
            }
        )
    return {
        "series": {kind: _thin(points, SERIES_LIMIT) for kind, points in series.items()},
        "bands": titles.bands(),
        "title": titles.user_title(user),
    }


# ── Qatnashgan musobaqalar ───────────────────────────────────────────


def contest_rows(user: User, standings: list[Standing]) -> list[dict[str, Any]]:
    """Musobaqa jadvali: teng o'rinlar oralig'i, reyting o'zgarishi, hajm.

    `Standing.rank` ketma-ket raqam (1, 2, 3…) — teng natija alohida
    belgilanmaydi. Shuning uchun oraliq natijaning o'zidan olinadi:
    ACM'da yechilganlar va jarima, IOI'da ball bir xil bo'lganlar.
    """
    if not standings:
        return []
    ids = [row.contest_id for row in standings]
    participants = dict(
        Standing.objects.filter(contest_id__in=ids)
        .values_list("contest_id")
        .annotate(n=Count("id"))
    )
    problems = dict(
        ContestProblem.objects.filter(contest_id__in=ids)
        .values_list("contest_id")
        .annotate(n=Count("id"))
    )
    virtual = set(
        ContestRegistration.objects.filter(
            user=user, contest_id__in=ids, virtual_start_at__isnull=False
        ).values_list("contest_id", flat=True)
    )
    history = {
        row.ref_id: row
        for row in RatingHistory.objects.filter(
            user=user,
            rating_type=RatingHistory.Type.CONTEST,
            reason=RatingHistory.Reason.CONTEST,
            ref_id__in=[row.contest.slug for row in standings],
        )
    }
    out: list[dict[str, Any]] = []
    for standing in standings:
        contest = standing.contest
        same = Standing.objects.filter(contest_id=standing.contest_id)
        same = (
            same.filter(total_score=standing.total_score)
            if contest.scoring_type == Contest.Scoring.IOI
            else same.filter(solved_count=standing.solved_count, penalty=standing.penalty)
        )
        tie = same.aggregate(lo=Min("rank"), hi=Max("rank"))
        change = history.get(contest.slug)
        rating: dict[str, Any] | None = None
        if change is not None:
            rating = {
                "before": change.value_before,
                "after": change.value_after,
                "delta": change.delta,
            }
        elif contest.is_rated and contest.ratings_applied_at and contest.pk not in virtual:
            # O'zgarishsiz natija tarixga yozilmaydi (`apply_contest_ratings`).
            rating = {"before": None, "after": None, "delta": 0}
        out.append(
            {
                "slug": contest.slug,
                "title": contest.title,
                "rank": standing.rank,
                "rank_from": tie["lo"] or standing.rank,
                "rank_to": tie["hi"] or standing.rank,
                "solved": standing.solved_count,
                "score": standing.total_score,
                "rating": rating,
                "problems": problems.get(contest.pk, 0),
                "participants": participants.get(contest.pk, 0),
                "start_at": contest.start_at,
                "duration_min": int((contest.end_at - contest.start_at).total_seconds() // 60),
                "is_rated": contest.is_rated,
                "virtual": contest.pk in virtual,
            }
        )
    return out
