"""The unofficial tier (ADR-0060 § 2.3): the Abramyan book and Judge-made problems.

The owner's rule: the solve marks the problem solved and keeps the streak
and the heatmap; it moves no rating, pays no Qvant and is not in the solved
count. The problem has no public number and is outside the archive's
default list.
"""

from __future__ import annotations

import pytest
from rest_framework.test import APIClient

from core.models import User
from judging.models import Attempt
from judging.services import apply_result
from problems.models import Problem, TestCase
from qvant import ledger, quests
from ratings.models import UserSolvedProblem
from ratings.services import recalc_skills

pytestmark = pytest.mark.django_db


@pytest.fixture
def book(db) -> Problem:
    """An unofficial public problem with a hidden test."""
    problem = Problem.objects.create(
        slug="begin1",
        title="Begin1. Kvadrat perimetri",
        statement="…",
        difficulty=800,
        is_public=True,
        is_official=False,
    )
    TestCase.objects.create(
        problem=problem, order=1, input_ref="s3://x/1.in", output_ref="s3://x/1.out"
    )
    return problem


def _solve(user: User, problem: Problem, language) -> None:  # type: ignore[no-untyped-def]
    attempt = Attempt.objects.create(user=user, problem=problem, language=language, source_code="x")
    apply_result({"attempt_id": attempt.pk, "verdict": "AC"})


class TestNoNumber:
    def test_an_unofficial_problem_gets_no_number(self, book) -> None:
        assert book.code is None

    def test_promotion_gives_it_the_next_number(self, book, problem) -> None:
        book.is_official = True
        book.save()
        assert book.code is not None and book.code > problem.code


class TestTheSolve:
    def test_counts_for_the_mark_the_streak_and_the_heatmap(self, user, book, language) -> None:
        quests.sync_catalogue()
        _solve(user, book, language)
        user.refresh_from_db()
        assert UserSolvedProblem.objects.filter(user=user, problem=book).exists()
        assert user.streak_count == 1
        book.refresh_from_db()
        assert book.solved_count == 1
        heatmap = APIClient().get(f"/api/v1/users/{user.username}/calendar/").json()
        assert any(day.get("solved") for day in heatmap.get("days", heatmap.get("results", [])))

    def test_moves_no_rating_and_pays_no_qvant(self, user, book, language) -> None:
        quests.sync_catalogue()
        skills, activity = user.rating_skills, user.rating_activity
        _solve(user, book, language)
        user.refresh_from_db()
        assert user.solved_count == 0
        assert user.rating_skills == recalc_skills(user) == skills
        assert user.rating_activity == activity
        assert ledger.get_wallet(user).balance == 0

    def test_an_official_solve_the_same_day_still_pays(self, user, book, problem, language) -> None:
        quests.sync_catalogue()
        TestCase.objects.create(
            problem=problem, order=99, input_ref="s3://x/99.in", output_ref="s3://x/99.out"
        )
        _solve(user, book, language)
        _solve(user, problem, language)
        user.refresh_from_db()
        assert user.solved_count == 1
        assert ledger.get_wallet(user).balance > 0
        # Only the official solve made a quest's day.
        assert user.streak_count == 1


class TestStreakMilestone:
    def test_an_unofficial_solve_pays_no_milestone_and_a_later_official_one_does(
        self, user
    ) -> None:
        from datetime import timedelta

        from django.utils import timezone

        from qvant import streak

        quests.sync_catalogue()
        today = timezone.localdate()
        user.streak_count = 6
        user.last_active_date = today - timedelta(days=1)
        user.save()
        assert streak.touch(user, today, reward=False) == (7, [])
        assert ledger.get_wallet(user).balance == 0
        _, granted = streak.touch(user, today)
        assert granted == [quests.STREAK_7]


class TestLists:
    def test_the_archive_lists_the_official_tier(self, problem, book) -> None:
        client = APIClient()
        slugs = {row["slug"] for row in client.get("/api/v1/problems/").json()["results"]}
        assert slugs == {problem.slug}
        unofficial = client.get("/api/v1/problems/?tier=unofficial").json()["results"]
        assert [row["slug"] for row in unofficial] == [book.slug]
        assert unofficial[0]["is_official"] is False and unofficial[0]["code"] is None
        both = {row["slug"] for row in client.get("/api/v1/problems/?tier=all").json()["results"]}
        assert both == {problem.slug, book.slug}

    def test_it_opens_by_its_address(self, book) -> None:
        response = APIClient().get(f"/api/v1/problems/{book.slug}/")
        assert response.status_code == 200
        assert response.json()["is_official"] is False

    def test_platform_counts_are_the_official_archive(self, problem, book) -> None:
        from django.core.cache import cache

        cache.clear()
        assert APIClient().get("/api/v1/stats/").json()["problems"] == 1


class TestTierChanges:
    def test_demotion_takes_the_solve_out_of_the_count(self, user, problem, language) -> None:
        TestCase.objects.create(
            problem=problem, order=99, input_ref="s3://x/99.in", output_ref="s3://x/99.out"
        )
        _solve(user, problem, language)
        user.refresh_from_db()
        assert user.solved_count == 1
        problem.is_official = False
        problem.save()
        user.refresh_from_db()
        assert user.solved_count == 0

    def test_promotion_puts_it_back(self, user, book, language) -> None:
        _solve(user, book, language)
        book.is_official = True
        book.save()
        user.refresh_from_db()
        assert user.solved_count == 1
