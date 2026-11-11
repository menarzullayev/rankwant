"""The `real` checker: numbers compared by the judge itself (ADR-0060)."""

from __future__ import annotations

import json

import pytest
from django.core.exceptions import ValidationError
from rest_framework.test import APIClient

from core.models import User
from judging.models import Attempt
from judging.services import build_job
from problems.evaluation import checker_spec, task_kind_error
from problems.models import Problem
from problems.readiness import checker_ready

pytestmark = pytest.mark.django_db


def _real(problem: Problem, **fields: object) -> Problem:
    problem.checker_type = Problem.Checker.REAL
    for name, value in fields.items():
        setattr(problem, name, value)
    problem.save()
    return problem


class TestJob:
    def test_the_job_carries_the_tolerance_and_asks_for_protocol_2(
        self, problem, user, language
    ) -> None:
        _real(problem, real_tolerance=1e-4)
        attempt = Attempt.objects.create(
            user=user, problem=problem, language=language, source_code="x", verdict="PENDING"
        )
        job = json.loads(build_job(attempt).to_json())
        assert job["checker"] == {"type": "real", "epsilon": 1e-4}
        assert job["protocol_version"] == 2

    def test_a_standard_job_is_unchanged(self, problem, user, language) -> None:
        attempt = Attempt.objects.create(
            user=user, problem=problem, language=language, source_code="x", verdict="PENDING"
        )
        job = json.loads(build_job(attempt).to_json())
        assert job["checker"] == {"type": "standard"}
        assert job["protocol_version"] == 1

    def test_the_default_tolerance_is_the_robocontest_one(self, problem) -> None:
        assert checker_spec(_real(problem)) == {"type": "real", "epsilon": 1e-6}


class TestWhereItFits:
    def test_needs_no_checker_program(self, problem) -> None:
        assert checker_ready(_real(problem))

    def test_file_io_is_allowed(self, problem) -> None:
        _real(problem, io_mode=Problem.IoMode.BOTH)
        problem.clean()

    def test_two_pass_may_compare_its_second_run(self) -> None:
        assert task_kind_error("two_pass", "stdio", "real") is None

    @pytest.mark.parametrize("kind", ["answer", "sql"])
    def test_kinds_that_never_compare_numbers_refuse_it(self, kind: str) -> None:
        assert task_kind_error(kind, "stdio", "real") is not None

    @pytest.mark.parametrize("tolerance", [0.0, 1e-13, 0.5])
    def test_a_tolerance_outside_the_range_is_refused(self, problem, tolerance: float) -> None:
        _real(problem, real_tolerance=tolerance)
        with pytest.raises(ValidationError):
            problem.full_clean()


def test_staff_can_choose_it(problem) -> None:
    client = APIClient()
    client.force_authenticate(User.objects.create_user("staff1", password="x", is_staff=True))
    response = client.patch(
        f"/api/v1/staff/problems/{problem.slug}/",
        {"checker_type": "real", "real_tolerance": 1e-5},
        format="json",
    )
    assert response.status_code == 200, response.content
    problem.refresh_from_db()
    assert (problem.checker_type, problem.real_tolerance) == ("real", 1e-5)


def test_the_problem_page_says_how_close_is_close_enough(problem) -> None:
    _real(problem, real_tolerance=1e-6)
    body = APIClient().get(f"/api/v1/problems/{problem.slug}/").json()
    assert (body["checker_type"], body["real_tolerance"]) == ("real", 1e-6)
