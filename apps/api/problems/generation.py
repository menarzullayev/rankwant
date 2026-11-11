"""The test generator (ADR-0061 § 6, owner decision ⑬).

One line of parameters → the generator's stdin → its stdout is the test's
input → the validator (if the problem has one) checks it → the reference
solution answers it → both go to storage and a `TestCase` with
`origin=GENERATED` is added.

The judge protocol does not change: every step is a `custom` job, and the
result finds its way back through `hack_stage`, which the judge copies
from the job unread. A value starting with `testgen:` routes here
(`judging.tasks.drain_results`), so a generated test is never dropped as a
result with nobody to own it.

Tests are made one at a time: the next job is queued only after the last
one answered. A run therefore never holds more than one place in the
queue that submissions share.
"""

from __future__ import annotations

import logging
import math
from datetime import timedelta
from typing import Any

from django.db import transaction
from django.db.models import Max, Sum
from django.utils import timezone

from core import quotas
from core.models import User
from judging.provider import JudgeJob, get_provider, new_job_id
from judging.verdicts import Verdict
from problems import limits, storage
from problems.models import (
    GenerationRun,
    Problem,
    ProblemLanguage,
    ReferenceSolution,
    TestCase,
    TestGenerator,
    Validator,
)

log = logging.getLogger(__name__)

#: Owner decision ⑬: at most 100 tests a run, each file at most 8 MiB.
MAX_LINES = 100
MAX_LINE_CHARS = 1000
MAX_TEST_KB = storage.MAX_TEST_BYTES // 1024
#: A run that has not moved for this long lost its job (a judge restart):
#: a new run may replace it.
STALE_AFTER = timedelta(minutes=30)
ROUTE = "testgen"

#: The generator is untrusted code: a submission's limits.
GENERATOR_LIMITS = {"compile_time_ms": 10_000, "time_ms": 10_000, "memory_kb": 262_144}


class GenerationError(Exception):
    def __init__(self, message: str, error: str) -> None:
        super().__init__(message)
        #: The API error code (`error.<code>` on the site).
        self.code = error


def storage_used(user: User) -> int:
    """Bytes of generated test data the user's runs have written."""
    total = GenerationRun.objects.filter(started_by=user).aggregate(n=Sum("bytes_written"))["n"]
    return int(total or 0)


def storage_used_mb(user: User) -> int:
    return math.ceil(storage_used(user) / (1024 * 1024))


def _room_left(user: User) -> int | None:
    """Bytes the plan still allows; `None` — no limit (staff)."""
    allowed = quotas.limit(user, "storage_mb")
    if allowed is None:
        return None
    return allowed * 1024 * 1024 - storage_used(user)


def _key(run: GenerationRun) -> str:
    return f"{ROUTE}:{run.pk}:{run.current}:{run.stage}"


def _program(language: Any, source: str) -> dict[str, Any]:
    return {**language.judge_spec(), "source": source}


def _enqueue(run: GenerationRun, job: JudgeJob) -> None:
    """Queue one step. A queue that is down fails the run at once: left
    RUNNING it would hold the problem's next run back until it went stale."""
    try:
        get_provider().submit(job)
    except Exception:
        log.exception("test generator: run %s could not be queued", run.pk)
        _fail(run, "The judge queue is unavailable; start the run again")


def _queue_generator(run: GenerationRun, generator: TestGenerator) -> None:
    line = run.lines[run.current]
    _enqueue(
        run,
        JudgeJob(
            job_id=new_job_id(),
            attempt_id=0,
            hack_stage=_key(run),
            language=generator.language.judge_spec(),
            source=generator.source,
            limits={
                **GENERATOR_LIMITS,
                "compile_time_ms": generator.language.compile_time_ms,
                "processes": generator.language.process_limit,
                "output_kb": MAX_TEST_KB,
            },
            tests=[{"index": 1, "input": f"{line}\n", "expected": None}],
            checker={"type": "standard"},
            mode="custom",
        ),
    )


def _queue_reference(run: GenerationRun, test_input: str) -> None:
    problem = run.problem
    reference = ReferenceSolution.objects.select_related("language").filter(problem=problem).first()
    if reference is None:
        _fail(run, "The reference solution was removed")
        return
    validator = Validator.objects.select_related("language").filter(problem=problem).first()
    override = ProblemLanguage.objects.filter(problem=problem, language=reference.language).first()
    _enqueue(
        run,
        JudgeJob(
            job_id=new_job_id(),
            attempt_id=0,
            hack_stage=_key(run),
            language=reference.language.judge_spec(),
            source=reference.source,
            limits={
                "compile_time_ms": reference.language.compile_time_ms,
                "time_ms": (override.time_limit_ms if override else None) or problem.time_limit_ms,
                "memory_kb": limits.memory_limit_kb(problem, reference.language, override),
                "output_kb": MAX_TEST_KB,
                "processes": reference.language.process_limit,
            },
            tests=[{"index": 1, "input": test_input, "expected": None}],
            checker={"type": "standard"},
            mode="custom",
            # A generated input is not trusted until the validator says so
            # (`protocol.md` § input validator): a bad one → WRONG_TEST.
            validator=_program(validator.language, validator.source) if validator else None,
            validate_input=validator is not None,
        ),
    )


def parse_lines(text: str) -> list[str]:
    return [line.rstrip() for line in text.splitlines() if line.strip()]


@transaction.atomic
def start(user: User, problem: Problem, lines: list[str], group: str) -> GenerationRun:
    if not lines:
        raise GenerationError("Write at least one line", error="generation_empty")
    if len(lines) > MAX_LINES:
        raise GenerationError(f"At most {MAX_LINES} tests a run", error="generation_too_many")
    if any(len(line) > MAX_LINE_CHARS for line in lines):
        raise GenerationError(
            f"A line is longer than {MAX_LINE_CHARS}", error="generation_line_long"
        )
    if group not in TestCase.Group.values or group == TestCase.Group.UNCLASSIFIED:
        raise GenerationError("Unknown test group", error="generation_group")
    generator = TestGenerator.objects.select_related("language").filter(problem=problem).first()
    if generator is None:
        raise GenerationError("Upload a generator first", error="generation_no_generator")
    if not ReferenceSolution.objects.filter(problem=problem).exists():
        raise GenerationError("Upload a reference solution first", error="generation_no_reference")
    left = _room_left(user)
    if left is not None and left <= 0:
        raise GenerationError("Your plan's test storage is full", error="quota_exceeded")
    # One run at a time per problem; one left behind by a lost job gives way.
    running = (
        GenerationRun.objects.select_for_update()
        .filter(problem=problem, status=GenerationRun.Status.RUNNING)
        .first()
    )
    if running is not None:
        if timezone.now() - running.updated_at < STALE_AFTER:
            raise GenerationError("A run is in progress", error="generation_running")
        _fail(running, "No answer from the judge; replaced by a new run")
    run = GenerationRun.objects.create(problem=problem, started_by=user, lines=lines, group=group)
    transaction.on_commit(lambda: _queue_generator(run, generator))
    return run


def _fail(run: GenerationRun, error: str) -> GenerationRun:
    run.status = GenerationRun.Status.FAILED
    run.error = error
    run.finished_at = timezone.now()
    run.save(update_fields=["status", "error", "finished_at", "updated_at"])
    return run


def _stdout(result: dict[str, Any]) -> str:
    per_test = result.get("per_test") or []
    return str(per_test[0].get("stdout") or "") if per_test else ""


@transaction.atomic
def apply_result(result: dict[str, Any]) -> GenerationRun | None:
    """A generator or reference answer, routed here by `hack_stage`."""
    parts = str(result.get("hack_stage") or "").split(":")
    if len(parts) != 4 or parts[0] != ROUTE or not parts[1].isdigit() or not parts[2].isdigit():
        return None
    run = (
        GenerationRun.objects.select_for_update()
        .select_related("problem", "started_by")
        .filter(pk=int(parts[1]))
        .first()
    )
    if run is None:
        log.warning("generation result for a missing run: %s", parts[1])
        return None
    # A late or repeated answer must not move a run that went on.
    if (
        run.status != GenerationRun.Status.RUNNING
        or int(parts[2]) != run.current
        or parts[3] != run.stage
    ):
        return run

    verdict = str(result.get("verdict") or Verdict.IE)
    detail = str(result.get("compile_output") or "")[:2000]
    number = run.current + 1
    out = _stdout(result)

    if run.stage == GenerationRun.Stage.GENERATE:
        if verdict != Verdict.AC or not out.strip():
            return _fail(run, f"Test {number}: the generator returned {verdict}. {detail}".strip())
        size = len(out.encode())
        if size > storage.MAX_TEST_BYTES:
            return _fail(run, f"Test {number}: the input is larger than 8 MiB")
        storage.ensure_bucket()
        run.input_ref = storage.put_test_data(
            f"tests/{run.problem.slug}/gen/{run.pk}/{number}.in", out
        )
        run.input_size = size
        run.stage = GenerationRun.Stage.ANSWER
        run.save(update_fields=["input_ref", "input_size", "stage", "updated_at"])
        # After commit: the answer must find this step saved.
        transaction.on_commit(lambda: _queue_reference(run, out))
        return run

    if verdict == Verdict.WRONG_TEST:
        return _fail(run, f"Test {number}: the validator rejected the input. {detail}".strip())
    if verdict != Verdict.AC:
        return _fail(
            run, f"Test {number}: the reference solution returned {verdict}. {detail}".strip()
        )
    size = len(out.encode())
    if size > storage.MAX_TEST_BYTES:
        return _fail(run, f"Test {number}: the answer is larger than 8 MiB")
    if run.started_by is not None:
        left = _room_left(run.started_by)
        if left is not None and run.input_size + size > left:
            return _fail(run, f"Test {number}: your plan's test storage is full")
    output_ref = storage.put_test_data(f"tests/{run.problem.slug}/gen/{run.pk}/{number}.out", out)
    last = TestCase.objects.filter(problem=run.problem).aggregate(m=Max("order"))["m"] or 0
    TestCase.objects.create(
        problem=run.problem,
        order=last + 1,
        input_ref=run.input_ref,
        output_ref=output_ref,
        origin=TestCase.Origin.GENERATED,
        group=run.group,
    )
    run.made += 1
    run.bytes_written += run.input_size + size
    run.input_ref = ""
    run.input_size = 0
    if run.current + 1 >= len(run.lines):
        run.status = GenerationRun.Status.DONE
        run.finished_at = timezone.now()
        run.save()
        return run
    run.current += 1
    run.stage = GenerationRun.Stage.GENERATE
    run.save()
    generator = TestGenerator.objects.select_related("language").filter(problem=run.problem).first()
    if generator is None:
        return _fail(run, "The generator was removed")
    transaction.on_commit(lambda: _queue_generator(run, generator))
    return run


def is_generation_result(result: dict[str, Any]) -> bool:
    return str(result.get("hack_stage") or "").startswith(f"{ROUTE}:")
