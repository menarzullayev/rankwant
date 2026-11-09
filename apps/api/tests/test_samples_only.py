"""Audit Q-05 (2026-11-10): samples-only problems earn neither Skills nor Qvant.

1 225 of 1 236 public problems had no hidden test, so a program printing
the sample answers was accepted. They stay in the archive, flagged as
`has_hidden_tests: false`; a solve there stays on the profile but adds
nothing to Skills and pays no Qvant (streak, daily quest, marathon).
"""

from __future__ import annotations

from datetime import date

import pytest
from django.db.models import Max
from rest_framework.test import APIClient

from judging.models import Attempt
from problems.models import Problem, TestCase
from problems.serializers import ProblemListSerializer
from ratings import formulas
from ratings.models import UserSolvedProblem
from ratings.services import on_attempt_judged

pytestmark = pytest.mark.django_db


def _problem(slug: str, difficulty: int, *, hidden: bool, sample: bool = True) -> Problem:
    code = (Problem.objects.aggregate(m=Max("code"))["m"] or 0) + 1
    problem = Problem.objects.create(
        slug=slug,
        title=slug,
        statement="…",
        difficulty=difficulty,
        is_public=True,
        code=code,
        readiness=Problem.Readiness.LEGACY_UNVERIFIED,
    )
    if sample:
        TestCase.objects.create(
            problem=problem,
            order=1,
            input_ref="s3://x/1.in",
            output_ref="s3://x/1.out",
            is_sample=True,
        )
    if hidden:
        TestCase.objects.create(
            problem=problem, order=2, input_ref="s3://x/2.in", output_ref="s3://x/2.out"
        )
    return problem


def _accept(user, problem, language) -> Attempt:
    attempt = Attempt.objects.create(
        user=user, problem=problem, language=language, source_code="x", verdict="AC"
    )
    on_attempt_judged(attempt)
    return attempt


class TestFlag:
    def test_list_and_detail_say_whether_hidden_tests_exist(self, language) -> None:
        _problem("judged", 900, hidden=True)
        _problem("samples", 900, hidden=False)
        client = APIClient()
        rows = {r["slug"]: r for r in client.get("/api/v1/problems/").json()["results"]}
        assert rows["judged"]["has_hidden_tests"] is True
        assert rows["samples"]["has_hidden_tests"] is False
        assert rows["samples"]["has_tests"] is True
        detail = client.get("/api/v1/problems/samples/").json()
        assert detail["has_hidden_tests"] is False

    def test_plain_problem_rows_keep_both_flags(self) -> None:
        """Marathon and recommendations serialize unannotated rows.

        A read-only `BooleanField` on a missing attribute was dropped by DRF,
        so the web read `undefined` there as "no tests".
        """
        plain = Problem.objects.get(pk=_problem("plain", 900, hidden=True).pk)
        data = ProblemListSerializer(plain).data
        assert data["has_tests"] is True
        assert data["has_hidden_tests"] is True


class TestSkills:
    def test_samples_only_solve_adds_nothing(self, user, language) -> None:
        samples = _problem("samples", 1500, hidden=False)
        _accept(user, samples, language)
        user.refresh_from_db()
        assert UserSolvedProblem.objects.filter(user=user, problem=samples).exists()
        assert user.rating_skills == 0

    def test_judged_solve_counts(self, user, language) -> None:
        judged = _problem("judged", 1500, hidden=True)
        _problem("samples", 2500, hidden=False)
        _accept(user, judged, language)
        _accept(user, Problem.objects.get(slug="samples"), language)
        user.refresh_from_db()
        assert user.rating_skills == formulas.skills_rating([1500])

    def test_first_hidden_test_recounts_the_solvers(
        self, user, language, django_capture_on_commit_callbacks
    ) -> None:
        samples = _problem("samples", 1500, hidden=False)
        _accept(user, samples, language)
        with django_capture_on_commit_callbacks(execute=True):
            TestCase.objects.create(
                problem=samples, order=2, input_ref="s3://x/2.in", output_ref="s3://x/2.out"
            )
        user.refresh_from_db()
        assert user.rating_skills == formulas.skills_rating([1500])

    def test_losing_the_last_hidden_test_recounts_the_solvers(
        self, user, language, django_capture_on_commit_callbacks
    ) -> None:
        judged = _problem("judged", 1500, hidden=True)
        _accept(user, judged, language)
        user.refresh_from_db()
        assert user.rating_skills > 0
        with django_capture_on_commit_callbacks(execute=True):
            TestCase.objects.filter(problem=judged, is_sample=False).delete()
        user.refresh_from_db()
        assert user.rating_skills == 0


class TestQvant:
    def test_samples_only_solve_starts_no_streak(self, user, language) -> None:
        _accept(user, _problem("samples", 900, hidden=False), language)
        user.refresh_from_db()
        assert user.streak_count == 0

    def test_judged_solve_starts_the_streak(self, user, language) -> None:
        _accept(user, _problem("judged", 900, hidden=True), language)
        user.refresh_from_db()
        assert user.streak_count == 1

    def test_daily_count_skips_samples_only(self, user, language) -> None:
        from qvant.services import _distinct_ac_count

        _accept(user, _problem("judged", 900, hidden=True), language)
        _accept(user, _problem("samples", 900, hidden=False), language)
        assert _distinct_ac_count(user, date.today()) == 1

    def test_marathon_draws_only_judged_problems(self, user) -> None:
        from qvant.marathon import MARATHON_SIZE, marathon_problems

        for i in range(MARATHON_SIZE):
            _problem(f"judged-{i}", 900, hidden=True)
            _problem(f"samples-{i}", 900, hidden=False)
        drawn = marathon_problems(user)
        assert len(drawn) == MARATHON_SIZE
        assert all(p.slug.startswith("judged-") for p in drawn)
