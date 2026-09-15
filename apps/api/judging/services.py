"""Submit oqimi — biznes logika VIEW da emas, shu yerda (ADR-0003)."""

from __future__ import annotations

import logging
from typing import Any

from django.core.cache import cache
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from judging.models import Attempt, AttemptTestResult, CustomRun
from judging.provider import JudgeJob, get_provider, new_job_id
from judging.verdicts import ALERTING, Verdict
from problems.models import Language, Problem, ProblemLanguage, TestCase, Validator

log = logging.getLogger(__name__)


def build_job(attempt: Attempt, *, validate_input: bool = False) -> JudgeJob:
    """Urinish uchun judge ishini quradi.

    `validate_input` — test kirishlari masalaning validatoridan o'tsinmi
    (ADR-0020). Oddiy yuborishda `False`: masalaning o'z testlarini muallif
    yozgan, ya'ni ular ishonchli, va ularni har submissionda qayta tekshirish
    sof isrof bo'lardi. `True` faqat kiritma ISHONCHSIZ bo'lganda — hack
    testi kabi.
    """
    problem = attempt.problem
    language = attempt.language

    tests: list[dict[str, Any]] = [
        {
            "index": t.order,
            "input_ref": t.input_ref,
            "output_ref": t.output_ref,
            "subtask": t.subtask_id or 0,
            "points": t.points,
        }
        for t in TestCase.objects.filter(problem=problem).order_by("order")
    ]

    subtasks = [
        {"id": st.pk, "points": st.points, "scoring": st.scoring}
        for st in problem.subtasks.order_by("order")
    ]

    def _program(lang: Language | None, source: str) -> dict[str, Any] | None:
        if lang is None or not source:
            return None
        return {
            "code": lang.code,
            "compile": lang.compile_cmd,
            "run": lang.run_cmd,
            "source": source,
        }

    checker: dict[str, Any] = {"type": problem.checker_type}
    if problem.checker_type == Problem.Checker.INTERACTIVE:
        interactor = _program(problem.interactor_language, problem.interactor_source)
        if interactor:
            checker["interactor"] = interactor
    elif problem.checker_type in (Problem.Checker.SPECIAL, Problem.Checker.SCORER):
        # Judge `special` va `scorer` da checker dasturini KUTADI; berilmasa
        # har yuborish IE bo'ladi. Model tomonida bu maydonlar yo'q edi.
        program = _program(problem.checker_language, problem.checker_source)
        if program:
            checker["program"] = program

    # Kirish validatori faqat SO'RALGANDA biriktiriladi.
    #
    # ⚠️ `problem.validator` — OneToOne, ya'ni yo'q bo'lsa unga murojaat
    # `RelatedObjectDoesNotExist` otadi va uni `getattr(..., None)` ham
    # to'smaydi. Shuning uchun so'rov bilan olinadi.
    #
    # Validator topilmasa `None` qoladi va `validate_input` baribir `True`
    # ketadi: judge uni YOPIQ yiqilish bilan rad etadi (protocol.md
    # § «Kirish validatori»). Bu ataylab — jimgina tekshiruvsiz davom
    # etishdan ko'ra ochiq xato yaxshi.
    validator: dict[str, Any] | None = None
    if validate_input:
        row = Validator.objects.filter(problem=problem).first()
        if row is not None:
            validator = _program(row.language, row.source)

    # Til ustma-ust limiti — Python C++ dan sekinroq, shu bois masala
    # limiti unga adolatsiz bo'lishi mumkin (KEP ham shunday qiladi).
    override = ProblemLanguage.objects.filter(problem=problem, language=language).first()
    time_ms = (override.time_limit_ms if override else None) or problem.time_limit_ms
    memory_kb = (override.memory_limit_kb if override else None) or problem.memory_limit_kb

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
            "time_ms": time_ms,
            "memory_kb": memory_kb,
            "output_kb": 65_536,
            "processes": language.process_limit,
        },
        tests=tests,
        checker=checker,
        subtasks=subtasks,
        # Subtask bo'lsa IOI: guruh to'liq o'tsagina ball beriladi.
        # `scorer` da checker sonni o'zi qaytaradi.
        mode="ioi" if subtasks else "acm",
        validator=validator,
        validate_input=validate_input,
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
        limits={**CUSTOM_LIMITS, "processes": run.language.process_limit},
        tests=[{"index": 1, "input": run.stdin, "expected": None}],
        checker={"type": "standard"},
        mode="custom",
    )
    get_provider().submit(job)
    return job.job_id


def _verdict_of(result: dict[str, Any]) -> str:
    """Judge bergan verdictni katalogga qarshi tekshiradi.

    Ustun `choices` bilan e'lon qilingan, lekin Postgres uni majburlamaydi:
    judge yuborgan istalgan satr shundayligicha yozilardi — o'lchandi,
    `"HACKED"` bazaga tushdi va u yerdan statistika, jadval va UI ga
    oqib ketardi. Tanilmagan verdict IE bo'ladi: bu aynan shu holat —
    ichki xato.
    """
    given = result.get("verdict")
    if given in Verdict.values:
        return str(given)
    log.error("judge tanilmagan verdict yubordi: %r (job %s)", given, result.get("job_id"))
    return Verdict.IE


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
    run.verdict = _verdict_of(result)
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

    verdict = _verdict_of(result)
    accept_revoked = attempt.verdict == Verdict.AC and verdict != Verdict.AC
    if accept_revoked:
        log.info("attempt %s verdicti o'zgardi: AC → %s", attempt_id, verdict)

    attempt.verdict = verdict
    attempt.score = int(result.get("score") or 0)
    attempt.time_ms = int(result.get("time_ms") or 0)
    attempt.memory_kb = int(result.get("memory_kb") or 0)
    attempt.failed_test_index = result.get("failed_test_index")
    attempt.compile_output = result.get("compile_output") or ""
    attempt.judge_meta = result.get("judge_meta") or {}
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

    from ratings.services import on_accept_revoked, on_attempt_judged

    if accept_revoked:
        on_accept_revoked(attempt)
    else:
        on_attempt_judged(attempt)

    if attempt.contest_id:
        _schedule_standings_rebuild(attempt.contest_id)
    return attempt


#: Contest spike'da 500 submit/10s bo'ladi. Har verdictda to'liq qayta
#: hisoblash — barcha urinishlarni skanerlash — ma'nosiz qimmat, mijoz
#: esa standings'ni har 10 s da yangilaydi (SSE_INTERVAL_S).
STANDINGS_DEBOUNCE_S = 5


def _schedule_standings_rebuild(contest_id: int) -> None:
    key = f"standings-rebuild:{contest_id}"
    if not cache.add(key, "1", STANDINGS_DEBOUNCE_S):
        return
    from contests.tasks import rebuild_standings_task

    rebuild_standings_task.apply_async((contest_id,), countdown=STANDINGS_DEBOUNCE_S)
