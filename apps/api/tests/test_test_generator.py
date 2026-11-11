"""The test generator: generator → validator → reference → storage (ADR-0061 § 6)."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from core.models import User
from judging.tasks import drain_results
from problems.models import (
    GenerationRun,
    Language,
    Problem,
    ReferenceSolution,
    TestCase,
    TestGenerator,
    Validator,
)
from tests.quota_utils import set_free_quota


def _client(user: User) -> APIClient:
    client = APIClient()
    client.force_authenticate(user)
    return client


@pytest.fixture
def py(db) -> Language:
    return Language.objects.create(
        code="py313", name="Python", version="3.13", compile_cmd=[], run_cmd=["python3", "{src}"]
    )


@pytest.fixture
def draft(user, py) -> Problem:
    problem = Problem.objects.create(
        slug="gen-draft", title="G", statement="s", difficulty=800, is_public=False
    )
    problem.authors.add(user)
    TestGenerator.objects.create(problem=problem, language=py, source="print(input())")
    ReferenceSolution.objects.create(problem=problem, language=py, source="print(int(input())*2)")
    return problem


def _url(problem: Problem, action: str) -> str:
    return reverse(f"staff-problem-{action}", args=[problem.slug])


def _answer(memory_judge, verdict: str, stdout: str = "") -> None:
    """The judge's answer to the last job, as `drain_results` reads it."""
    job = memory_judge.jobs[-1]
    memory_judge.results.append(
        {
            "job_id": job.job_id,
            "attempt_id": 0,
            "hack_stage": job.hack_stage,
            "verdict": verdict,
            "compile_output": "",
            "per_test": [{"index": 1, "verdict": verdict, "stdout": stdout}],
        }
    )


@pytest.mark.django_db
class TestChain:
    def _start(self, user, problem, captured, lines="3\n5\n") -> dict[str, Any]:
        with captured(execute=True):
            res = _client(user).post(_url(problem, "generate"), {"lines": lines}, format="json")
        assert res.status_code == 202, res.content
        body: dict[str, Any] = res.json()
        return body

    def test_two_tests_made_one_at_a_time(
        self, user, draft, memory_judge, fake_hack_storage, django_capture_on_commit_callbacks
    ) -> None:
        run = self._start(user, draft, django_capture_on_commit_callbacks)
        assert run["total"] == 2
        assert len(memory_judge.jobs) == 1
        first = memory_judge.jobs[0]
        assert first.hack_stage == f"testgen:{run['id']}:0:gen"
        assert first.tests[0]["input"] == "3\n"
        assert first.mode == "custom"
        assert first.attempt_id == 0 and first.hack_id == 0

        with django_capture_on_commit_callbacks(execute=True):
            _answer(memory_judge, "AC", "3\n")
            drain_results()
        assert len(memory_judge.jobs) == 2
        reference = memory_judge.jobs[1]
        assert reference.hack_stage == f"testgen:{run['id']}:0:ref"
        assert reference.source == "print(int(input())*2)"
        assert reference.validate_input is False  # no validator on this problem

        with django_capture_on_commit_callbacks(execute=True):
            _answer(memory_judge, "AC", "6\n")
            drain_results()
        test = TestCase.objects.get(problem=draft)
        assert (test.origin, test.group, test.order) == ("gen", "random", 1)
        assert fake_hack_storage[test.output_ref.removeprefix("s3://test/")] == "6\n"
        # Only now the second line is queued: never two jobs at once.
        assert len(memory_judge.jobs) == 3
        assert memory_judge.jobs[2].hack_stage == f"testgen:{run['id']}:1:gen"

        with django_capture_on_commit_callbacks(execute=True):
            _answer(memory_judge, "AC", "5\n")
            drain_results()
        with django_capture_on_commit_callbacks(execute=True):
            _answer(memory_judge, "AC", "10\n")
            drain_results()
        done = GenerationRun.objects.get()
        assert (done.status, done.made) == ("done", 2)
        assert done.bytes_written == len("3\n6\n5\n10\n")
        assert TestCase.objects.filter(problem=draft).count() == 2

    def test_validator_checks_and_can_stop_the_run(
        self, user, draft, py, memory_judge, fake_hack_storage, django_capture_on_commit_callbacks
    ) -> None:
        Validator.objects.create(problem=draft, language=py, source="assert int(input())<4")
        self._start(user, draft, django_capture_on_commit_callbacks, lines="9\n")
        with django_capture_on_commit_callbacks(execute=True):
            _answer(memory_judge, "AC", "9\n")
            drain_results()
        assert memory_judge.jobs[-1].validate_input is True
        assert memory_judge.jobs[-1].validator is not None
        with django_capture_on_commit_callbacks(execute=True):
            _answer(memory_judge, "WRONG_TEST")
            drain_results()
        run = GenerationRun.objects.get()
        assert run.status == "failed"
        assert "validator" in run.error
        assert not TestCase.objects.filter(problem=draft).exists()

    def test_generator_crash_stops_the_run(
        self, user, draft, memory_judge, fake_hack_storage, django_capture_on_commit_callbacks
    ) -> None:
        self._start(user, draft, django_capture_on_commit_callbacks)
        with django_capture_on_commit_callbacks(execute=True):
            _answer(memory_judge, "RE_EXIT")
            drain_results()
        run = GenerationRun.objects.get()
        assert run.status == "failed"
        assert len(memory_judge.jobs) == 1

    def test_published_meanwhile_keeps_its_tests(
        self, user, draft, memory_judge, fake_hack_storage, django_capture_on_commit_callbacks
    ) -> None:
        self._start(user, draft, django_capture_on_commit_callbacks)
        Problem.objects.filter(pk=draft.pk).update(is_public=True)
        with django_capture_on_commit_callbacks(execute=True):
            _answer(memory_judge, "AC", "3\n")
            drain_results()
        run = GenerationRun.objects.get()
        assert run.status == "failed"
        assert "published" in run.error
        assert len(memory_judge.jobs) == 1
        assert not TestCase.objects.filter(problem=draft).exists()

    def test_a_hand_upload_taking_the_number_is_skipped(
        self, user, draft, memory_judge, fake_hack_storage, django_capture_on_commit_callbacks
    ) -> None:
        from problems.generation import _add_test

        run = self._start(user, draft, django_capture_on_commit_callbacks, lines="1\n")
        row = GenerationRun.objects.get(pk=run["id"])
        TestCase.objects.create(problem=draft, order=1, input_ref="a", output_ref="b")
        real = TestCase.objects.filter

        calls = {"n": 0}

        def stale_filter(*args, **kwargs):
            # The first count misses the hand-made test, as a race would.
            calls["n"] += 1
            if calls["n"] == 1:
                return real(problem_id=-1)
            return real(*args, **kwargs)

        import unittest.mock as mock

        with mock.patch.object(TestCase.objects, "filter", side_effect=stale_filter):
            test = _add_test(row, "s3://test/x.out")
        assert test.order == 2
        assert TestCase.objects.filter(problem=draft).count() == 2

    def test_a_late_answer_does_not_move_the_run(
        self, user, draft, memory_judge, fake_hack_storage, django_capture_on_commit_callbacks
    ) -> None:
        run = self._start(user, draft, django_capture_on_commit_callbacks)
        memory_judge.results.append(
            {
                "job_id": "old",
                "attempt_id": 0,
                "hack_stage": f"testgen:{run['id']}:0:ref",
                "verdict": "AC",
                "per_test": [{"index": 1, "verdict": "AC", "stdout": "x"}],
            }
        )
        drain_results()
        fresh = GenerationRun.objects.get()
        assert (fresh.stage, fresh.made) == ("gen", 0)
        assert not TestCase.objects.exists()


@pytest.mark.django_db
class TestGuards:
    def test_author_of_a_draft_only(self, user, other_user, draft) -> None:
        assert _client(other_user).get(_url(draft, "generate")).status_code == 403
        Problem.objects.filter(pk=draft.pk).update(is_public=True)
        assert _client(user).get(_url(draft, "generate")).status_code == 403

    def test_author_uploads_the_programs(self, user, py) -> None:
        problem = Problem.objects.create(slug="p2", title="P", statement="s", difficulty=800)
        problem.authors.add(user)
        body = {"language": py.code, "source": "print(1)"}
        for action in ("generator", "reference-solution", "validator"):
            res = _client(user).put(
                reverse(f"staff-problem-{action}", args=[problem.slug]),
                body,
                format="json",
            )
            assert res.status_code == 201, (action, res.content)

    def test_needs_generator_and_reference(self, user, py) -> None:
        problem = Problem.objects.create(slug="p3", title="P", statement="s", difficulty=800)
        problem.authors.add(user)
        res = _client(user).post(_url(problem, "generate"), {"lines": "1"}, format="json")
        assert res.json()["error"]["code"] == "generation_no_generator"
        TestGenerator.objects.create(problem=problem, language=py, source="x")
        res = _client(user).post(_url(problem, "generate"), {"lines": "1"}, format="json")
        assert res.json()["error"]["code"] == "generation_no_reference"

    def test_at_most_100_tests(self, user, draft) -> None:
        lines = "\n".join(str(i) for i in range(101))
        res = _client(user).post(_url(draft, "generate"), {"lines": lines}, format="json")
        assert res.json()["error"]["code"] == "generation_too_many"

    def test_one_run_at_a_time(self, user, draft, django_capture_on_commit_callbacks) -> None:
        with django_capture_on_commit_callbacks(execute=True):
            _client(user).post(_url(draft, "generate"), {"lines": "1"}, format="json")
        res = _client(user).post(_url(draft, "generate"), {"lines": "1"}, format="json")
        assert res.json()["error"]["code"] == "generation_running"
        # A run with no answer for half an hour gives way.
        GenerationRun.objects.update(updated_at=timezone.now() - timedelta(hours=1))
        with django_capture_on_commit_callbacks(execute=True):
            again = _client(user).post(_url(draft, "generate"), {"lines": "1"}, format="json")
        assert again.status_code == 202
        assert GenerationRun.objects.filter(status="failed").count() == 1

    def test_storage_quota(
        self, user, draft, memory_judge, fake_hack_storage, django_capture_on_commit_callbacks
    ) -> None:
        set_free_quota(storage_mb=0)
        res = _client(user).post(_url(draft, "generate"), {"lines": "1"}, format="json")
        assert res.json()["error"]["code"] == "quota_exceeded"
        quotas = _client(user).get(reverse("me-quotas")).json()["quotas"]
        assert {row["key"] for row in quotas} >= {"storage_mb"}

    def test_queue_down_fails_the_run_at_once(
        self, user, draft, memory_judge, monkeypatch, django_capture_on_commit_callbacks
    ) -> None:
        def down(job):
            raise ConnectionError("redis is down")

        monkeypatch.setattr(memory_judge, "submit", down)
        with django_capture_on_commit_callbacks(execute=True):
            res = _client(user).post(_url(draft, "generate"), {"lines": "1"}, format="json")
        assert res.status_code == 202
        run = GenerationRun.objects.get()
        assert run.status == "failed"
        assert "queue" in run.error
        # Nothing holds the problem: the next run may start straight away.
        with django_capture_on_commit_callbacks(execute=True):
            again = _client(user).post(_url(draft, "generate"), {"lines": "1"}, format="json")
        assert again.status_code == 202

    def test_unknown_group(self, user, draft) -> None:
        res = _client(user).post(
            _url(draft, "generate"), {"lines": "1", "group": "unclassified"}, format="json"
        )
        assert res.status_code == 400
