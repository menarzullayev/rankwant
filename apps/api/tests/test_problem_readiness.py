"""Content readiness — R1 … R10 (WP1 · D8 · D8-F · ADR-0037).

The suite is the acceptance evidence for two frozen decisions:

  D8    the criterion is semantic, never a count ("at least five hidden
        tests" is forbidden) — R1..R7
  D8-F  a `legacy_unverified` problem stays PUBLIC but cannot enter a graded
        contest — R8, R9

R10 guards the state machine itself: a jump such as `draft -> validated`
must never be accepted, wherever it is attempted from.
"""

from __future__ import annotations

from typing import Any

import pytest
from django.core.exceptions import ValidationError
from django.urls import reverse
from rest_framework.test import APIClient

from contests.models import Contest, ContestProblem
from core.models import User
from problems.models import Problem, TestCase


@pytest.fixture
def staff_user(db) -> User:
    return User.objects.create_user("staff1", password="Parol!12345", is_staff=True)


@pytest.fixture
def staff(staff_user) -> APIClient:
    client = APIClient()
    client.force_authenticate(user=staff_user)
    return client


@pytest.fixture
def draft(db) -> Problem:
    """A brand new problem — no tests, not public."""
    return Problem.objects.create(
        slug="draft-one", title="Draft", statement="…", difficulty=800, is_public=False
    )


@pytest.fixture
def empty_contest(db) -> Contest:
    """A contest with no problems attached yet."""
    from datetime import timedelta

    from django.utils import timezone

    now = timezone.now()
    return Contest.objects.create(
        slug="round-empty",
        title="Round empty",
        start_at=now - timedelta(hours=2),
        end_at=now - timedelta(minutes=1),
        is_rated=True,
    )


def publish(staff: APIClient, problem: Problem) -> Any:
    """`PATCH staff/problems/<slug>/` with `is_public=True`.

    `Any` on purpose: `APIClient` returns the DRF `Response`, whose stub does
    not declare `.json()` even though the runtime object has it.
    """
    """`PATCH staff/problems/<slug>/` with `is_public=True`."""
    return staff.patch(
        reverse("staff-problem-detail", args=[problem.slug]),
        {"is_public": True},
        format="json",
    )


@pytest.mark.django_db
class TestDefaultAndPublish:
    def test_default_readiness_is_draft(self, draft) -> None:
        """R1 — a new problem starts as a draft and is not public."""
        assert draft.readiness == Problem.Readiness.DRAFT
        assert draft.is_public is False

    def test_publish_without_tests_is_400(self, staff, draft) -> None:
        """R2 — publishing with no test at all is refused (existing gate)."""
        response = publish(staff, draft)
        assert response.status_code == 400, response.json()
        draft.refresh_from_db()
        assert draft.is_public is False

    def test_publish_without_hidden_test_is_400(self, staff, draft) -> None:
        """R3 — only a sample test: copying the sample would be accepted."""
        TestCase.objects.create(
            problem=draft,
            order=1,
            input_ref="s3://x/1.in",
            output_ref="s3://x/1.out",
            is_sample=True,
        )
        response = publish(staff, draft)
        assert response.status_code == 400, response.json()
        draft.refresh_from_db()
        assert draft.is_public is False


@pytest.mark.django_db
class TestStateMachine:
    def test_transition_forward_step_ok(self, draft) -> None:
        """R4 — one step forward is accepted once the condition is met."""
        draft.readiness = Problem.Readiness.NEEDS_TESTS
        draft.save(update_fields=["readiness"])
        TestCase.objects.create(
            problem=draft,
            order=1,
            input_ref="s3://x/1.in",
            output_ref="s3://x/1.out",
            is_sample=False,
        )
        draft.readiness = Problem.Readiness.HAS_HIDDEN_TESTS
        draft.full_clean()  # S1 holds — the hidden test exists
        draft.save(update_fields=["readiness"])
        assert draft.readiness == Problem.Readiness.HAS_HIDDEN_TESTS

    def test_hidden_test_required_for_the_step(self, draft) -> None:
        """R4 (negative half) — the same step without a hidden test is refused."""
        draft.readiness = Problem.Readiness.NEEDS_TESTS
        draft.save(update_fields=["readiness"])
        TestCase.objects.create(
            problem=draft,
            order=1,
            input_ref="s3://x/1.in",
            output_ref="s3://x/1.out",
            is_sample=True,
        )
        draft.readiness = Problem.Readiness.HAS_HIDDEN_TESTS
        with pytest.raises(ValidationError) as exc:
            draft.full_clean()
        assert "S1" in str(exc.value)

    def test_checker_type_required(self, draft) -> None:
        """R5 — `special` without a checker program cannot advance (S2)."""
        TestCase.objects.create(
            problem=draft,
            order=1,
            input_ref="s3://x/1.in",
            output_ref="s3://x/1.out",
            is_sample=False,
        )
        draft.readiness = Problem.Readiness.HAS_HIDDEN_TESTS
        draft.save(update_fields=["readiness"])
        draft.checker_type = Problem.Checker.SPECIAL
        draft.checker_source = ""
        draft.readiness = Problem.Readiness.CHECKER_VALIDATED
        with pytest.raises(ValidationError) as exc:
            draft.full_clean()
        assert "S2" in str(exc.value)

    def test_draft_to_validated_jump_rejected(self, draft) -> None:
        """R10 — a jump is refused even when every condition looks met."""
        TestCase.objects.create(
            problem=draft,
            order=1,
            input_ref="s3://x/1.in",
            output_ref="s3://x/1.out",
            is_sample=False,
        )
        draft.readiness = Problem.Readiness.VALIDATED
        with pytest.raises(ValidationError) as exc:
            draft.full_clean()
        assert "is not allowed" in str(exc.value)


@pytest.mark.django_db
class TestBackfill:
    def test_backfill_audit_numbers(self) -> None:
        """M1 — A/B/C groups and criterion ③ (no public row left NULL)."""
        from io import StringIO

        from django.core.management import call_command

        legacy = Problem.objects.create(
            slug="archive-a", title="Archive A", statement="…", difficulty=800, is_public=True
        )
        with_hidden = Problem.objects.create(
            slug="archive-b", title="Archive B", statement="…", difficulty=800, is_public=True
        )
        TestCase.objects.create(
            problem=with_hidden,
            order=1,
            input_ref="s3://x/1.in",
            output_ref="s3://x/1.out",
            is_sample=False,
        )
        private = Problem.objects.create(
            slug="archive-c", title="Archive C", statement="…", difficulty=800, is_public=False
        )

        out = StringIO()
        call_command("backfill_readiness", "--apply", stdout=out)
        printed = out.getvalue()

        legacy.refresh_from_db()
        with_hidden.refresh_from_db()
        private.refresh_from_db()
        assert legacy.readiness == Problem.Readiness.LEGACY_UNVERIFIED
        assert with_hidden.readiness == Problem.Readiness.NEEDS_REVIEW
        assert private.readiness == Problem.Readiness.DRAFT
        # D8-F — the backfill never touches visibility.
        assert legacy.is_public is True
        # Criterion ③.
        assert Problem.objects.filter(is_public=True, readiness__isnull=True).count() == 0
        assert "A legacy_unverified=1" in printed
        assert "B needs_review=1" in printed


@pytest.mark.django_db
class TestGradedGate:
    def test_graded_requires_validated(self, staff, draft, empty_contest) -> None:
        """R8 — a draft problem cannot be attached to a graded contest."""
        response = staff.put(
            reverse("staff-contest-problems", args=[empty_contest.slug]),
            [{"problem": draft.slug, "index_letter": "A"}],
            format="json",
        )
        assert response.status_code == 400, response.json()
        assert not ContestProblem.objects.filter(contest=empty_contest).exists()

    def test_validated_problem_is_accepted(self, staff, draft, empty_contest) -> None:
        """R8 (positive half) — `validated` content does enter a contest."""
        draft.readiness = Problem.Readiness.VALIDATED
        draft.save(update_fields=["readiness"])
        response = staff.put(
            reverse("staff-contest-problems", args=[empty_contest.slug]),
            [{"problem": draft.slug, "index_letter": "A"}],
            format="json",
        )
        assert response.status_code == 200, response.json()
        assert ContestProblem.objects.filter(contest=empty_contest).count() == 1

    def test_legacy_unverified_public_but_not_in_contest(self, staff, empty_contest) -> None:
        """R9 — D8-F: visible in the archive, refused by a graded contest."""
        legacy = Problem.objects.create(
            slug="archive-one",
            title="Archive",
            statement="…",
            difficulty=800,
            is_public=True,
            readiness=Problem.Readiness.LEGACY_UNVERIFIED,
        )
        # Public: the archive stays readable.
        assert legacy.is_public is True
        listed = APIClient().get(reverse("problem-list")).json()
        assert "archive-one" in [row["slug"] for row in listed["results"]]
        # ...but not graded-eligible.
        response = staff.put(
            reverse("staff-contest-problems", args=[empty_contest.slug]),
            [{"problem": legacy.slug, "index_letter": "A"}],
            format="json",
        )
        assert response.status_code == 400, response.json()
        assert not ContestProblem.objects.filter(contest=empty_contest).exists()
        legacy.refresh_from_db()
        assert legacy.is_public is True  # the gate never touches visibility
