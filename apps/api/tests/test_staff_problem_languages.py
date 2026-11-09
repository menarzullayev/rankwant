"""Audit Q-12 (2026-11-10): language rows and harnesses are edited through the staff API.

`ProblemLanguage.harness` could be edited only in the Django admin, which
production does not route, so no new `function` problem could be authored.
"""

from __future__ import annotations

import pytest
from rest_framework.test import APIClient

from core.models import User
from problems.models import Language, Problem, ProblemLanguage

pytestmark = pytest.mark.django_db

HARNESS = '#include <cstdio>\n{{SOLUTION}}\nint main() { std::printf("%d", add(1, 2)); }\n'


@pytest.fixture
def staff_client(db) -> APIClient:
    client = APIClient()
    client.force_authenticate(User.objects.create_user("staff-q12", password="x", is_staff=True))
    return client


@pytest.fixture
def function_problem(problem: Problem) -> Problem:
    problem.task_kind = Problem.TaskKind.FUNCTION
    problem.save(update_fields=["task_kind"])
    return problem


def url(problem: Problem, code: str = "") -> str:
    base = f"/api/v1/staff/problems/{problem.slug}/languages/"
    return f"{base}{code}/" if code else base


def test_create_then_replace_a_harness(staff_client, function_problem, language) -> None:
    body = {
        "harness": HARNESS,
        "code_template": "int add(int a, int b) {\n}\n",
        "time_limit_ms": 2000,
    }
    first = staff_client.put(url(function_problem, "cpp23"), body, format="json")
    assert first.status_code == 201, first.json()
    assert first.json()["language"] == "cpp23"
    second = staff_client.put(
        url(function_problem, "cpp23"), {**body, "time_limit_ms": 3000}, format="json"
    )
    assert second.status_code == 200
    row = ProblemLanguage.objects.get(problem=function_problem, language=language)
    assert row.time_limit_ms == 3000
    assert row.harness == HARNESS
    listed = staff_client.get(url(function_problem)).json()
    assert [r["language"] for r in listed] == ["cpp23"]


def test_harness_without_the_marker_is_refused(staff_client, function_problem, language) -> None:
    res = staff_client.put(
        url(function_problem, "cpp23"), {"harness": "int main() {}"}, format="json"
    )
    assert res.status_code == 400
    assert "harness" in str(res.json())
    assert not ProblemLanguage.objects.exists()


def test_a_language_without_function_support_is_refused(staff_client, function_problem) -> None:
    Language.objects.create(
        code="haskell9", name="Haskell", version="9", compile_cmd=[], run_cmd=[]
    )
    res = staff_client.put(url(function_problem, "haskell9"), {"harness": HARNESS}, format="json")
    assert res.status_code == 400
    assert "language" in str(res.json())


def test_a_harness_on_a_whole_program_problem_is_refused(staff_client, problem, language) -> None:
    res = staff_client.put(url(problem, "cpp23"), {"harness": HARNESS}, format="json")
    assert res.status_code == 400
    ok = staff_client.put(url(problem, "cpp23"), {"memory_limit_kb": 524288}, format="json")
    assert ok.status_code == 201


def test_delete_and_unknown_language(staff_client, function_problem, language) -> None:
    staff_client.put(url(function_problem, "cpp23"), {"harness": HARNESS}, format="json")
    assert staff_client.delete(url(function_problem, "cpp23")).status_code == 204
    assert staff_client.delete(url(function_problem, "cpp23")).status_code == 404
    assert staff_client.put(url(function_problem, "nope1"), {}, format="json").status_code == 404


def test_not_open_to_a_regular_user(function_problem, language) -> None:
    client = APIClient()
    client.force_authenticate(User.objects.create_user("plain-q12", password="x"))
    assert client.get(url(function_problem)).status_code == 403
    assert (
        client.put(url(function_problem, "cpp23"), {"harness": HARNESS}, format="json").status_code
        == 403
    )
