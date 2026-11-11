"""Each language's runtime memory is added to the problem's limit (ADR-0060 § 2.2)."""

from __future__ import annotations

import json

import pytest
from rest_framework.test import APIClient

from judging.models import Attempt
from judging.services import build_job
from problems.languages import LANGUAGES, row_values
from problems.limits import memory_limit_kb
from problems.models import Language, ProblemLanguage

pytestmark = pytest.mark.django_db


@pytest.fixture
def jvm(db) -> Language:
    return Language.objects.create(
        code="jvm-test", name="JVM", run_cmd=["java", "Main"], memory_overhead_kb=21_504
    )


def _job_memory(problem, user, language) -> int:
    attempt = Attempt.objects.create(
        user=user, problem=problem, language=language, source_code="x", verdict="PENDING"
    )
    return int(json.loads(build_job(attempt).to_json())["limits"]["memory_kb"])


def test_the_runtime_is_added_to_the_problem_limit(problem, user, jvm) -> None:
    problem.memory_limit_kb = 65_536
    problem.save()
    assert _job_memory(problem, user, jvm) == 65_536 + 21_504


def test_a_limit_the_author_set_for_the_language_is_used_as_written(problem, user, jvm) -> None:
    problem.memory_limit_kb = 65_536
    problem.save()
    ProblemLanguage.objects.create(problem=problem, language=jvm, memory_limit_kb=100_000)
    assert _job_memory(problem, user, jvm) == 100_000


def test_a_time_only_override_keeps_the_overhead(problem, jvm) -> None:
    row = ProblemLanguage.objects.create(problem=problem, language=jvm, time_limit_ms=3000)
    assert memory_limit_kb(problem, jvm, row) == problem.memory_limit_kb + 21_504


def test_the_submit_panel_shows_the_limit_the_language_gets(problem, jvm) -> None:
    problem.memory_limit_kb = 65_536
    problem.save()
    body = APIClient().get(f"/api/v1/problems/{problem.slug}/").json()
    row = next(lang for lang in body["languages"] if lang["code"] == "jvm-test")
    assert row["memory_limit_kb"] == 65_536 + 21_504
    # The header keeps the problem's own limit: what the solution may use.
    assert body["memory_limit_kb"] == 65_536


def test_every_catalog_language_has_a_measured_overhead() -> None:
    """A language added without measuring would run with no allowance for
    its runtime: a JVM would lose 20 MB of every problem's limit."""
    for spec in LANGUAGES:
        assert row_values(spec)["memory_overhead_kb"] >= 1024, spec["code"]


def test_the_migration_wrote_the_measured_values() -> None:
    assert Language.objects.get(code="julia113").memory_overhead_kb == 119_808
    assert Language.objects.get(code="r45").memory_overhead_kb == 45_056
