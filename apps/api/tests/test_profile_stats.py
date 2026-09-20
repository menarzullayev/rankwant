"""Profil statistikasi — faollik xaritasi, tillar, verdiktlar, masalalar
xaritasi, reyting grafigi, qatnashgan musobaqalar va yechilganlar jadvali."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from contests.models import Contest, ContestRegistration, Standing
from core.models import User
from judging.models import Attempt
from judging.verdicts import Verdict
from problems.models import Language, Problem, Topic
from profiles import stats
from ratings.models import RatingHistory, UserSolvedProblem
from ratings.services import on_attempt_judged


def urinish(
    user: User,
    problem: Problem,
    language: Language,
    verdict: str = Verdict.AC,
    when: datetime | None = None,
    time_ms: int = 10,
    memory_kb: int = 100,
) -> Attempt:
    attempt = Attempt.objects.create(
        user=user,
        problem=problem,
        language=language,
        source_code="x",
        verdict=verdict,
        time_ms=time_ms,
        memory_kb=memory_kb,
    )
    if when is not None:
        Attempt.objects.filter(pk=attempt.pk).update(created_at=when)
        attempt.refresh_from_db()
    return attempt


def kun(year: int, month: int, day: int, hour: int = 12) -> datetime:
    return datetime(year, month, day, hour, tzinfo=timezone.get_current_timezone())


def get(name: str, username: str, **params: Any) -> Any:
    return APIClient().get(reverse(name, args=[username]), params)


@pytest.fixture
def python(db: None) -> Language:
    return Language.objects.create(
        code="py313", name="Python", version="3.13", compile_cmd=[], run_cmd=["python3", "{src}"]
    )


@pytest.mark.django_db
class TestFaollikXaritasi:
    def test_kunlik_urinish_va_yechim(
        self, user: User, problem: Problem, language: Language
    ) -> None:
        urinish(user, problem, language, Verdict.WA, kun(2026, 3, 20, 10))
        urinish(user, problem, language, Verdict.AC, kun(2026, 3, 20, 11))
        urinish(user, problem, language, Verdict.RATE_LIMITED, kun(2026, 3, 20, 12))
        UserSolvedProblem.objects.create(user=user, problem=problem, difficulty_at_solve=800)
        UserSolvedProblem.objects.filter(user=user).update(first_ac_at=kun(2026, 3, 20, 11))

        body = get("user-calendar", user.username, year=2026).data

        assert body["days"] == [{"date": "2026-03-20", "attempts": 2, "solved": 1}]
        assert (body["attempts"], body["solved"]) == (2, 1)
        assert 2026 in body["years"]

    def test_notogri_yil_rad(self, user: User) -> None:
        assert get("user-calendar", user.username, year=1999).status_code == 400
        assert get("user-calendar", user.username, year="abc").status_code == 400

    def test_eng_uzun_streak_ac_kunlaridan(
        self, user: User, problem: Problem, language: Language
    ) -> None:
        for day in (1, 2, 3, 10):
            urinish(user, problem, language, Verdict.AC, kun(2026, 2, day))
        urinish(user, problem, language, Verdict.WA, kun(2026, 2, 4))
        user.streak_count = 2
        user.last_active_date = timezone.localdate()
        user.save(update_fields=["streak_count", "last_active_date"])

        assert stats.streaks(user) == {"current": 2, "longest": 3}

    def test_uzilgan_streak_joriysi_nol(self, user: User) -> None:
        user.streak_count = 5
        user.last_active_date = timezone.localdate() - timedelta(days=3)
        user.save(update_fields=["streak_count", "last_active_date"])

        assert stats.streaks(user)["current"] == 0


@pytest.mark.django_db
class TestUmumiyStatistika:
    def test_tillar_va_verdiktlar(
        self, user: User, problem: Problem, language: Language, python: Language
    ) -> None:
        for verdict in (Verdict.AC, Verdict.WA, Verdict.WA):
            urinish(user, problem, language, verdict)
        urinish(user, problem, python, Verdict.AC)
        urinish(user, problem, language, Verdict.IE)
        urinish(user, problem, language, Verdict.PENDING)

        body = get("user-stats", user.username).data

        assert body["languages"][0] == {"code": "cpp23", "name": "C++", "accepted": 1, "errors": 2}
        assert body["languages"][1]["code"] == "py313"
        assert {row["verdict"]: row["count"] for row in body["verdicts"]} == {"AC": 2, "WA": 2}
        assert (body["attempts"], body["accepted"]) == (4, 2)

    def test_daraja_kesimi_faqat_ommaviy(
        self, user: User, problem: Problem, hard_problem: Problem
    ) -> None:
        Problem.objects.create(slug="yopiq", title="Yopiq", statement=".", difficulty=900)
        UserSolvedProblem.objects.create(user=user, problem=problem, difficulty_at_solve=800)

        body = get("user-stats", user.username).data

        assert (body["solved"], body["total"]) == (1, 2)
        levels = {row["code"]: (row["solved"], row["total"]) for row in body["levels"]}
        assert levels["beginner"] == (1, 1)
        assert levels["expert"] == (0, 1)

    def test_kesh_commitdan_keyin_yangilanadi(
        self,
        user: User,
        problem: Problem,
        language: Language,
        django_capture_on_commit_callbacks: Any,
    ) -> None:
        assert get("user-stats", user.username).data["attempts"] == 0
        attempt = urinish(user, problem, language, Verdict.WA)
        assert get("user-stats", user.username).data["attempts"] == 0, "hali keshdan"

        with django_capture_on_commit_callbacks() as callbacks:
            on_attempt_judged(attempt)
        assert get("user-stats", user.username).data["attempts"] == 0, "commitgacha eski"

        for callback in callbacks:
            callback()
        assert get("user-stats", user.username).data["attempts"] == 1


@pytest.mark.django_db
class TestMasalalarXaritasi:
    def test_holatlar(
        self, user: User, problem: Problem, hard_problem: Problem, language: Language
    ) -> None:
        Problem.objects.create(
            slug="uchinchi", title="Uchinchi", statement=".", difficulty=1300, is_public=True
        )
        Problem.objects.create(slug="yopiq", title="Yopiq", statement=".", difficulty=900)
        UserSolvedProblem.objects.create(user=user, problem=problem, difficulty_at_solve=800)
        urinish(user, hard_problem, language, Verdict.WA)

        rows = {row["slug"]: row for row in get("user-problem-map", user.username).data["problems"]}

        assert rows["a-plus-b"]["state"] == "solved"
        assert rows["hard-one"]["state"] == "attempted"
        assert rows["uchinchi"]["state"] == "untouched"
        assert rows["uchinchi"]["level"] == "intermediate"
        assert "yopiq" not in rows


@pytest.mark.django_db
class TestReytingGrafigi:
    def test_turlar_va_musobaqa_nomi(self, user: User, contest: Contest) -> None:
        RatingHistory.objects.create(
            user=user,
            rating_type="contest",
            value_before=1200,
            value_after=1480,
            delta=80,
            reason="contest",
            ref_type="contest",
            ref_id=contest.slug,
            rank=3,
        )
        RatingHistory.objects.create(
            user=user,
            rating_type="skills",
            value_before=0,
            value_after=90,
            delta=90,
            reason="problem_solved",
            ref_type="problem",
            ref_id="a-plus-b",
        )

        body = get("user-rating-series", user.username).data

        point = body["series"]["contest"][0]
        assert (point["title"], point["rank"], point["before"], point["after"]) == (
            "Round 1",
            3,
            1200,
            1480,
        )
        assert len(body["series"]["skills"]) == 1
        assert body["bands"][0]["code"] == "quark"

    def test_uzun_qator_siqiladi_cho_qqi_qoladi(self) -> None:
        points = [{"after": i} for i in range(1000)]
        points[517]["after"] = 5000

        thin = stats._thin(points, 100)

        assert len(thin) <= 103
        assert thin[-1] is points[-1]
        assert points[517] in thin


@pytest.mark.django_db
class TestMusobaqalar:
    def test_teng_orin_va_reyting_ozgarishi(
        self, user: User, other_user: User, contest: Contest
    ) -> None:
        third = User.objects.create_user(username="uchinchi")
        Standing.objects.create(contest=contest, user=third, rank=1, solved_count=4, penalty=50)
        Standing.objects.create(contest=contest, user=user, rank=2, solved_count=3, penalty=100)
        Standing.objects.create(
            contest=contest, user=other_user, rank=3, solved_count=3, penalty=100
        )
        RatingHistory.objects.create(
            user=user,
            rating_type="contest",
            value_before=1200,
            value_after=1450,
            delta=50,
            reason="contest",
            ref_type="contest",
            ref_id=contest.slug,
            rank=2,
        )

        row = get("user-contests", user.username).data["results"][0]

        assert (row["rank_from"], row["rank_to"]) == (2, 3)
        assert row["rating"] == {"before": 1200, "after": 1450, "delta": 50}
        assert (row["problems"], row["participants"]) == (1, 3)
        assert row["virtual"] is False

    def test_virtual_va_qidiruv(self, user: User, contest: Contest) -> None:
        Standing.objects.create(contest=contest, user=user, rank=1)
        ContestRegistration.objects.create(
            contest=contest, user=user, virtual_start_at=timezone.now()
        )

        assert get("user-contests", user.username).data["results"][0]["virtual"] is True
        assert get("user-contests", user.username, q="yo'q").data["results"] == []

    def test_yopiq_musobaqa_korinmaydi(self, user: User, contest: Contest) -> None:
        contest.is_public = False
        contest.save(update_fields=["is_public"])
        Standing.objects.create(contest=contest, user=user, rank=1)

        assert get("user-contests", user.username).data["results"] == []


@pytest.mark.django_db
class TestYechilganlarJadvali:
    def test_eng_yaxshi_vaqt_va_tillar(
        self, user: User, problem: Problem, language: Language, python: Language
    ) -> None:
        first = urinish(user, problem, language, Verdict.AC, time_ms=30, memory_kb=900)
        urinish(user, problem, python, Verdict.AC, time_ms=50, memory_kb=500)
        urinish(user, problem, language, Verdict.WA, time_ms=1, memory_kb=1)
        UserSolvedProblem.objects.create(
            user=user, problem=problem, first_ac_attempt=first, difficulty_at_solve=800
        )

        row = APIClient().get(reverse("solved-problems", args=[user.username])).data["results"][0]

        assert (row["best_time_ms"], row["best_memory_kb"]) == (30, 500)
        assert sorted(row["languages"]) == ["cpp23", "py313"]

    def test_qidiruv_va_saralash(self, user: User, problem: Problem, hard_problem: Problem) -> None:
        for solved in (problem, hard_problem):
            UserSolvedProblem.objects.create(
                user=user, problem=solved, difficulty_at_solve=solved.difficulty
            )
        url = reverse("solved-problems", args=[user.username])

        found = APIClient().get(url, {"q": "qiyin"}).data["results"]
        ordered = APIClient().get(url, {"ordering": "difficulty"}).data["results"]

        assert [row["slug"] for row in found] == ["hard-one"]
        assert [row["slug"] for row in ordered] == ["a-plus-b", "hard-one"]


@pytest.mark.django_db
class TestMavzuKuchi:
    def test_begona_profilda_ham_ochiq(self, user: User, problem: Problem) -> None:
        topic = Topic.objects.create(
            slug="math", name_uz="Matematika", name_ru="Математика", name_en="Math"
        )
        problem.topics.add(topic)
        UserSolvedProblem.objects.create(user=user, problem=problem, difficulty_at_solve=800)

        topics = get("user-topics", user.username).data["topics"]

        assert (topics[0]["slug"], topics[0]["solved"], topics[0]["name_en"]) == ("math", 1, "Math")
        assert topics[0]["rating"] > 0
