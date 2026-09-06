"""Submit oqimi — biznes logika VIEW da emas, shu yerda (ADR-0003)."""

from __future__ import annotations

import logging
from typing import Any

from django.db import transaction
from django.db.models import F
from django.utils import timezone

from judging.models import Attempt, AttemptTestResult, CustomRun
from judging.provider import JudgeJob, get_provider, new_job_id
from judging.verdicts import ALERTING, Verdict
from problems.models import Problem, TestCase

log = logging.getLogger(__name__)


def build_job(attempt: Attempt) -> JudgeJob:
    problem = attempt.problem
    language = attempt.language

    tests: list[dict[str, Any]] = [
        {"index": t.order, "input_ref": t.input_ref, "output_ref": t.output_ref}
        for t in TestCase.objects.filter(problem=problem).order_by("order")
    ]

    checker: dict[str, Any] = {"type": problem.checker_type}
    if problem.checker_type == Problem.Checker.INTERACTIVE and problem.interactor_language:
        checker["interactor"] = {
            "code": problem.interactor_language.code,
            "compile": problem.interactor_language.compile_cmd,
            "run": problem.interactor_language.run_cmd,
            "source": problem.interactor_source,
        }

    return JudgeJob(
        job_id=new_job_id(),
        attempt_id=attempt.pk,
        language={
            "code": language.code,
            "compile": language.compile_cmd,
            "run": language.run_cmd,
        },
        source=attempt.source_code,
        limits={
            "compile_time_ms": 10_000,
            "time_ms": problem.time_limit_ms,
            "memory_kb": problem.memory_limit_kb,
            "output_kb": 65_536,
            "processes": 1,
        },
        tests=tests,
        checker=checker,
        mode="acm",
    )


@transaction.atomic
def enqueue(attempt: Attempt) -> str:
    """Attempt ni navbatga qo'yadi.

    Attempt DB da ALLAQACHON saqlangan bo'lishi kerak: navbat yiqilsa ham
    submission yo'qolmasligi shart (10-operations § recovery).
    """
    Problem.objects.filter(pk=attempt.problem_id).update(attempt_count=F("attempt_count") + 1)
    job = build_job(attempt)
    get_provider().submit(job)
    return job.job_id


#: Custom test uchun cheklovlar — masala limitlari yo'q, shuning uchun
#: konservativ standart qiymatlar.
CUSTOM_LIMITS = {
    "compile_time_ms": 10_000,
    "time_ms": 5_000,
    "memory_kb": 262_144,
    "output_kb": 1_024,
    "processes": 1,
}


def enqueue_custom(run: CustomRun) -> str:
    """PRD P0-4 — stdin bilan bir marta ishga tushirish.

    `mode="custom"`: judge chiqishni kutilgan javob bilan SOLISHTIRMAYDI,
    shunchaki stdout ni qaytaradi.
    """
    job = JudgeJob(
        job_id=new_job_id(),
        attempt_id=0,
        custom_run_id=run.pk,
        language={
            "code": run.language.code,
            "compile": run.language.compile_cmd,
            "run": run.language.run_cmd,
        },
        source=run.source_code,
        limits=dict(CUSTOM_LIMITS),
        tests=[{"index": 1, "input": run.stdin, "expected": None}],
        checker={"type": "standard"},
        mode="custom",
    )
    get_provider().submit(job)
    return job.job_id


@transaction.atomic
def apply_custom_result(result: dict[str, Any]) -> CustomRun | None:
    run_id = result.get("custom_run_id")
    if not run_id:
        return None
    try:
        run = CustomRun.objects.select_for_update().get(pk=run_id)
    except CustomRun.DoesNotExist:
        log.warning("natija topilmagan custom run uchun keldi: %s", run_id)
        return None

    per_test = result.get("per_test") or []
    run.verdict = result.get("verdict", Verdict.IE)
    run.stdout = (per_test[0].get("stdout") if per_test else "") or result.get("stdout") or ""
    run.compile_output = result.get("compile_output") or ""
    run.time_ms = int(result.get("time_ms") or 0)
    run.memory_kb = int(result.get("memory_kb") or 0)
    run.judged_at = timezone.now()
    run.save()
    return run


@transaction.atomic
def apply_result(result: dict[str, Any]) -> Attempt | None:
    """Judge natijasini yozadi va reyting hisoblashni ishga tushiradi."""
    attempt_id = result.get("attempt_id")
    if not attempt_id:
        return None
    try:
        attempt = Attempt.objects.select_for_update().get(pk=attempt_id)
    except Attempt.DoesNotExist:
        log.warning("natija topilmagan attempt uchun keldi: %s", attempt_id)
        return None

    if attempt.verdict in {Verdict.AC} and result.get("verdict") != Verdict.AC:
        # Rejudge natijasi — yozamiz, lekin reyting qayta hisoblanadi
        log.info("attempt %s verdicti o'zgardi: AC → %s", attempt_id, result.get("verdict"))

    attempt.verdict = result.get("verdict", Verdict.IE)
    attempt.score = int(result.get("score") or 0)
    attempt.time_ms = int(result.get("time_ms") or 0)
    attempt.memory_kb = int(result.get("memory_kb") or 0)
    attempt.failed_test_index = result.get("failed_test_index")
    attempt.compile_output = result.get("compile_output") or ""
    attempt.judged_at = timezone.now()
    attempt.save()

    AttemptTestResult.objects.filter(attempt=attempt).delete()
    AttemptTestResult.objects.bulk_create(
        [
            AttemptTestResult(
                attempt=attempt,
                index=t["index"],
                verdict=t.get("verdict", Verdict.IE),
                time_ms=int(t.get("time_ms") or 0),
                memory_kb=int(t.get("memory_kb") or 0),
            )
            for t in (result.get("per_test") or [])
        ]
    )

    if attempt.verdict in ALERTING:
        # 10-operations: har bitta hodisa alert chiqaradi
        log.error(
            "XAVFSIZLIK: attempt %s da %s — potensial sandbox escape urinishi",
            attempt.pk,
            attempt.verdict,
        )

    from ratings.services import on_attempt_judged

    on_attempt_judged(attempt)
    return attempt
