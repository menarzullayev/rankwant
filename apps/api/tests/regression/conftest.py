"""Fixtures for the readiness regression suite (WP1 · D8).

The harness talks to a `JudgeProvider`, so the judge is swapped here instead
of being stubbed deep inside `problems.readiness`: the probe, the job it
builds and the state machine all run for real — only the sandbox is fake.
"""

from __future__ import annotations

from typing import Any

import pytest

from judging.provider import JudgeJob, set_provider
from judging.verdicts import Verdict
from problems.models import Problem, ReferenceSolution, TestCase


class ScriptedJudge:
    """Answers `submit()` immediately — no sandbox, no queue.

    `InMemoryJudgeProvider` only records jobs, so a harness polling it would
    never see a result. This one decides the verdict from the source it was
    handed, which is exactly the axis S3/S4 vary along:

        ScriptedJudge({"ref": Verdict.AC, "echo": Verdict.AC})
    """

    def __init__(self, verdicts: dict[str, str]) -> None:
        self.verdicts = verdicts
        self.jobs: list[JudgeJob] = []
        self.results: list[dict[str, Any]] = []

    def submit(self, job: JudgeJob) -> str:
        self.jobs.append(job)
        self.results.append(
            {
                "job_id": job.job_id,
                "attempt_id": job.attempt_id,
                "verdict": self.verdicts.get(job.source, Verdict.IE),
            }
        )
        return job.job_id

    def pending_jobs(self) -> int:
        return 0

    def poll(self, timeout: int = 1) -> dict[str, Any] | None:
        return self.results.pop(0) if self.results else None


@pytest.fixture
def scripted_judge():
    """Installs a `ScriptedJudge`; usage: `scripted_judge({"ref": "AC"})`."""

    def build(verdicts: dict[str, str]) -> ScriptedJudge:
        provider = ScriptedJudge(verdicts)
        set_provider(provider)
        return provider

    yield build
    set_provider(None)


@pytest.fixture
def ready_problem(db, problem: Problem, language) -> Problem:
    """A problem that satisfies S1 and S2 and owns a reference solution.

    Starts at `checker_validated` — the harness is what moves it forward.
    The reference solution source is the literal `"ref"` and the echo
    program's is `"echo"`, so a `ScriptedJudge` can tell them apart.
    """
    TestCase.objects.create(
        problem=problem,
        order=1,
        input_ref="s3://x/1.in",
        output_ref="s3://x/1.out",
        is_sample=True,
    )
    TestCase.objects.create(
        problem=problem,
        order=11,
        input_ref="s3://x/11.in",
        output_ref="s3://x/11.out",
        is_sample=False,
    )
    ReferenceSolution.objects.create(problem=problem, language=language, source="ref")
    problem.readiness = Problem.Readiness.CHECKER_VALIDATED
    problem.save(update_fields=["readiness"])
    return problem
