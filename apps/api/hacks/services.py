"""Hack dvigateli — ADR-0020 (siyosatlar) va ADR-0021 (etalon yechim).

Bitta hack uchta judge ishidan o'tadi va har biri navbatdan alohida
qaytadi:

    1. `generate`  — generator dasturi kiritmani yasaydi (ixtiyoriy)
    2. `reference` — kiritma VALIDATORdan o'tadi, so'ng etalon yechim
                     to'g'ri javobni hisoblaydi
    3. `defend`    — himoyachining kodi o'sha test bilan ishlaydi

Bosqichlar ketma-ket: har javob keyingisini navbatga qo'yadi. Ular bitta
ishga birlashtirilmadi — judge hack mantig'ini bilmasligi kerak, aks
holda «bitta dvigatel» qoidasi judge ichiga ham ko'chib ketardi.
"""

from __future__ import annotations

import logging
from typing import Any

from django.conf import settings
from django.db import IntegrityError, transaction
from django.utils import timezone

from contests.models import Contest, ContestProblem, ContestRegistration
from core.models import User
from hacks import policies
from hacks.models import Hack, HackLock, HackRoom, HackRoomMember
from hacks.policies import AddsTest, Policy
from judging.models import Attempt
from judging.provider import JudgeJob, get_provider, new_job_id
from judging.verdicts import Verdict
from problems import storage
from problems.models import (
    Language,
    Problem,
    ProblemLanguage,
    ReferenceSolution,
    TestCase,
    Validator,
)
from ratings.models import UserSolvedProblem

log = logging.getLogger(__name__)


class HackError(Exception):
    """Foydalanuvchiga ko'rsatiladigan rad etish sababi."""


#: Generator ishonchsiz kod — submission bilan bir xil qattiq chegarada.
GENERATOR_LIMITS = {
    "compile_time_ms": 10_000,
    "time_ms": 10_000,
    "memory_kb": 262_144,
    "processes": 1,
}


# ── Siyosat ──────────────────────────────────────────────────────────


def open_policy(attempt: Attempt, now: Any = None) -> Policy | None:
    """Shu urinishga HOZIR qaysi siyosat oynasi ochiq.

    Tartib muhim: musobaqa urinishida xona → ochiq faza → uphack ketma
    ketligi vaqt bo'yicha ajraladi, ya'ni bir paytda faqat bittasi ochiq.
    Musobaqadan tashqarida esa har doim amaliyot.
    """
    now = now or timezone.now()
    contest = attempt.contest
    if contest is None:
        return policies.PRACTICE

    if contest.hack_room and contest.start_at <= now < contest.end_at:
        return policies.CONTEST_ROOM
    until = contest.hack_open_until
    if until and contest.end_at <= now < until:
        return policies.OPEN_PHASE
    uphack_until = contest.uphack_until
    if uphack_until and now < uphack_until:
        return policies.UPHACK
    # Musobaqa urinishi, lekin hamma oyna yopilgan. Amaliyotga TUSHMAYDI:
    # aks holda yopilgan oyna «doim ochiq» bo'lib qolardi.
    return None


def is_trusted(user: User) -> bool:
    """Uphack uchun «ishonchli foydalanuvchi».

    Ta'rif ochiq va tekshiriladigan (principle #2): reyting chegarasi yoki
    admin. Yashirin ro'yxat emas.
    """
    return bool(user.is_staff or user.rating_contest >= settings.HACK_UPHACK_MIN_RATING)


def room_of(contest: Contest, user: User) -> HackRoom | None:
    """Foydalanuvchining xonasi; ro'yxatdan o'tmagan bo'lsa `None`.

    Xonalar birinchi so'rovda taqsimlanadi: musobaqa boshlanishida
    alohida vazifa yo'q va ro'yxatdan kech o'tganlar ham joy oladi.
    """
    member = (
        HackRoomMember.objects.filter(contest=contest, user=user).select_related("room").first()
    )
    if member is not None:
        return member.room
    if not ContestRegistration.objects.filter(contest=contest, user=user).exists():
        return None
    return _assign_room(contest, user)


@transaction.atomic
def _assign_room(contest: Contest, user: User) -> HackRoom:
    """Eng bo'sh xonaga qo'shadi, kerak bo'lsa yangisini ochadi."""
    locked = Contest.objects.select_for_update().get(pk=contest.pk)
    existing = (
        HackRoomMember.objects.filter(contest=locked, user=user).select_related("room").first()
    )
    if existing is not None:
        return existing.room

    room = None
    for candidate in HackRoom.objects.filter(contest=locked).order_by("number"):
        if candidate.members.count() < settings.HACK_ROOM_SIZE:
            room = candidate
            break
    if room is None:
        last = HackRoom.objects.filter(contest=locked).order_by("-number").first()
        room = HackRoom.objects.create(contest=locked, number=(last.number + 1) if last else 1)
    HackRoomMember.objects.create(room=room, contest=locked, user=user)
    return room


def eligibility(user: User, attempt: Attempt, policy: Policy) -> str:
    """Bu foydalanuvchi shu urinishni hack qila oladimi.

    Qaytaradi: bo'sh satr — ha; aks holda sabab (foydalanuvchiga
    ko'rsatiladi). Sababni AYTAMIZ: jimgina yashirilgan tugma
    foydalanuvchini «nega ishlamadi?» degan savol bilan qoldiradi.
    """
    if attempt.user_id == user.pk:
        return "O'z yechimingizni hack qilib bo'lmaydi"
    if attempt.verdict != Verdict.AC:
        return "Faqat qabul qilingan yechim hack qilinadi"

    # ADR-0020, 2-tamoyil: manba ko'rinishi uchun IKKI shart birga —
    # hacker masalani o'zi yechgan bo'lishi va oyna ochiq bo'lishi.
    if not UserSolvedProblem.objects.filter(user=user, problem_id=attempt.problem_id).exists():
        return "Avval shu masalani o'zingiz yeching"

    if policy.trusted_only and not is_trusted(user):
        return f"Uphack uchun {settings.HACK_UPHACK_MIN_RATING}+ musobaqa reytingi kerak"

    if policy.room_only:
        contest = attempt.contest
        if contest is None:
            return "Musobaqa topilmadi"
        mine = room_of(contest, user)
        theirs = room_of(contest, attempt.user)
        if mine is None:
            return "Musobaqaga ro'yxatdan o'ting"
        if theirs is None or mine.pk != theirs.pk:
            return "Faqat o'z xonangizdagi yechimlar"
        if (
            policy.needs_lock
            and not HackLock.objects.filter(
                contest=contest, problem_id=attempt.problem_id, user=user
            ).exists()
        ):
            return "Avval masalani lock qiling"
    return ""


@transaction.atomic
def lock(user: User, contest: Contest, problem: Problem) -> HackLock:
    """Masalani lock qiladi. QAYTARIB BO'LMAYDI.

    Codeforces qoidasi: lock qilgandan keyin o'sha masalaga qayta yuborib
    bo'lmaydi, evaziga xonadagi yechimlar ochiladi. Ya'ni hack huquqi
    tekin emas — o'z balli xatarga qo'yiladi. Shuning uchun ochish yo'li
    ham yo'q.

    `AC` sharti shundan kelib chiqadi: yechilmagan masalada xatarga
    qo'yiladigan ball yo'q va lock faqat tekin ruxsatnomaga aylanardi.
    """
    if not contest.hack_room:
        raise HackError("Bu musobaqada xona hackingi yoqilmagan")
    if not contest.is_running:
        raise HackError("Musobaqa faol emas")
    if not ContestRegistration.objects.filter(contest=contest, user=user).exists():
        raise HackError("Musobaqaga ro'yxatdan o'ting")
    if not ContestProblem.objects.filter(contest=contest, problem=problem).exists():
        raise HackError("Masala bu musobaqada yo'q")
    if not Attempt.objects.filter(
        contest=contest, user=user, problem=problem, verdict=Verdict.AC
    ).exists():
        raise HackError("Avval shu masalani musobaqada yeching")

    row, _ = HackLock.objects.get_or_create(contest=contest, problem=problem, user=user)
    # Xona aynan shu yerda taqsimlansin: hack oynasi ochilganda ro'yxat
    # tayyor bo'ladi va birinchi hack so'rovi taqsimotni kutmaydi.
    room_of(contest, user)
    return row


def can_view_source(user: User, attempt: Attempt) -> bool:
    """Hack uchun manba ko'rinadimi (ADR-0020, 2-tamoyil).

    Bu urinish detalidagi umumiy yopiqlikni ALMASHTIRMAYDI — uning
    ustiga nuqtali istisno qo'shadi: hack oynasi ochiq va hacker
    huquqli bo'lsa, aynan o'sha yechim ko'rinadi.
    """
    if not user.is_authenticated:
        return False
    policy = open_policy(attempt)
    if policy is None:
        return False
    return not eligibility(user, attempt, policy)


# ── Yuborish ─────────────────────────────────────────────────────────


def _program(language: Language, source: str) -> dict[str, Any]:
    return {
        "code": language.code,
        "compile": language.compile_cmd,
        "run": language.run_cmd,
        "source": source,
    }


def _problem_limits(problem: Problem, language: Language) -> dict[str, int]:
    override = ProblemLanguage.objects.filter(problem=problem, language=language).first()
    return {
        "compile_time_ms": 10_000,
        "time_ms": (override.time_limit_ms if override else None) or problem.time_limit_ms,
        "memory_kb": (override.memory_limit_kb if override else None) or problem.memory_limit_kb,
        "output_kb": settings.HACK_GENERATOR_OUTPUT_KB,
        "processes": language.process_limit,
    }


@transaction.atomic
def submit(
    hacker: User,
    attempt: Attempt,
    *,
    raw_input: str = "",
    generator_language: Language | None = None,
    generator_source: str = "",
) -> Hack:
    """Hack urinishini qabul qiladi va birinchi bosqichni navbatga qo'yadi."""
    policy = open_policy(attempt)
    if policy is None:
        raise HackError("Bu yechim uchun hack oynasi yopiq")
    reason = eligibility(hacker, attempt, policy)
    if reason:
        raise HackError(reason)

    problem = attempt.problem
    # ADR-0020 3-qaror va ADR-0021: ikkala darvoza ham majburiy.
    # Ularsiz hack ochilsa, buzuq kiritma yoki noto'g'ri javob bilan
    # istalgan to'g'ri yechimni «sindirish» mumkin bo'lardi.
    if not Validator.objects.filter(problem=problem).exists():
        raise HackError("Bu masalada kirish validatori yo'q — hack yopiq")
    if not ReferenceSolution.objects.filter(problem=problem).exists():
        raise HackError("Bu masalada etalon yechim yo'q — hack yopiq")

    if generator_language is not None:
        if not generator_source.strip():
            raise HackError("Generator manbasi bo'sh")
        stage = Hack.Stage.GENERATE
    else:
        if not raw_input.strip():
            raise HackError("Test kiritmasi bo'sh")
        if len(raw_input.encode()) > settings.HACK_INPUT_MAX_BYTES:
            raise HackError(
                f"Kiritma {settings.HACK_INPUT_MAX_BYTES // 1024} KB dan oshmasligi kerak — "
                "kattasini generator bilan yuboring"
            )
        stage = Hack.Stage.REFERENCE

    try:
        hack = Hack.objects.create(
            hacker=hacker,
            defender_attempt=attempt,
            problem=problem,
            contest=attempt.contest,
            policy=policy.code,
            stage=stage,
            generator_language=generator_language,
            generator_source=generator_source,
            input_size=len(raw_input.encode()),
        )
    except IntegrityError as exc:  # uniq_hack_in_flight
        raise HackError("Bu yechim uchun hack allaqachon tekshirilmoqda") from exc

    if stage == Hack.Stage.REFERENCE:
        storage.ensure_bucket()
        hack.input_ref = storage.put_test_data(f"hacks/{hack.pk}.in", raw_input)
        hack.save(update_fields=["input_ref", "updated_at"])
        _enqueue_reference(hack, raw_input)
    else:
        _enqueue_generator(hack)
    return hack


def _enqueue(job: JudgeJob) -> None:
    get_provider().submit(job)


def _enqueue_generator(hack: Hack) -> None:
    """Generator — ISHONCHSIZ kod, `custom` rejimda chiqishi olinadi."""
    assert hack.generator_language is not None
    _enqueue(
        JudgeJob(
            job_id=new_job_id(),
            attempt_id=0,
            hack_id=hack.pk,
            hack_stage=Hack.Stage.GENERATE,
            language={
                "code": hack.generator_language.code,
                "compile": hack.generator_language.compile_cmd,
                "run": hack.generator_language.run_cmd,
            },
            source=hack.generator_source,
            limits={**GENERATOR_LIMITS, "output_kb": settings.HACK_GENERATOR_OUTPUT_KB},
            tests=[{"index": 1, "input": "", "expected": None}],
            checker={"type": "standard"},
            mode="custom",
        )
    )


def _enqueue_reference(hack: Hack, test_input: str) -> None:
    """Etalon yechim: avval VALIDATOR, keyin to'g'ri javob.

    `validate_input=True` — shu bosqichda kiritma tekshiriladi va
    yaroqsiz bo'lsa judge `WRONG_TEST` qaytaradi (protocol.md § «Kirish
    validatori»). Ya'ni tekshiruv etalon yechim ishga tushishidan ham
    oldin bo'ladi.
    """
    reference = (
        ReferenceSolution.objects.select_related("language").filter(problem=hack.problem).first()
    )
    validator = Validator.objects.select_related("language").filter(problem=hack.problem).first()
    if reference is None or validator is None:
        # `submit` ikkalasini ham tekshirgan, lekin generator bosqichi
        # bilan bu bosqich orasida xodim ularni olib tashlashi mumkin.
        # Yiqilish o'rniga hack yopiladi: aks holda istisno `drain_results`
        # da qolib, hack abadiy `TESTING` bo'lib turardi.
        _finish(
            hack,
            Hack.Status.IGNORED,
            detail="masalaning validatori yoki etalon yechimi olib tashlandi",
        )
        return
    limits = _problem_limits(hack.problem, reference.language)
    _enqueue(
        JudgeJob(
            job_id=new_job_id(),
            attempt_id=0,
            hack_id=hack.pk,
            hack_stage=Hack.Stage.REFERENCE,
            language={
                "code": reference.language.code,
                "compile": reference.language.compile_cmd,
                "run": reference.language.run_cmd,
            },
            source=reference.source,
            limits=limits,
            tests=[{"index": 1, "input": test_input, "expected": None}],
            checker={"type": "standard"},
            mode="custom",
            validator=_program(validator.language, validator.source),
            validate_input=True,
        )
    )


def _enqueue_defender(hack: Hack) -> None:
    """Himoyachining kodi hack testida — endi javob ham bor.

    Kiritma allaqachon validatordan o'tgan va S3 da yotibdi, shuning
    uchun bu bosqichda qayta tekshirilmaydi: ikkinchi tekshiruv har hack
    uchun bitta ortiqcha sandbox ishga tushirish bo'lardi.
    """
    attempt = hack.defender_attempt
    problem = hack.problem
    checker: dict[str, Any] = {"type": problem.checker_type}
    if problem.checker_type in (Problem.Checker.SPECIAL, Problem.Checker.SCORER):
        if problem.checker_language and problem.checker_source:
            checker["program"] = _program(problem.checker_language, problem.checker_source)
    _enqueue(
        JudgeJob(
            job_id=new_job_id(),
            attempt_id=0,
            hack_id=hack.pk,
            hack_stage=Hack.Stage.DEFEND,
            language={
                "code": attempt.language.code,
                "compile": attempt.language.compile_cmd,
                "run": attempt.language.run_cmd,
            },
            source=attempt.source_code,
            limits=_problem_limits(problem, attempt.language),
            tests=[{"index": 1, "input_ref": hack.input_ref, "output_ref": hack.output_ref}],
            checker=checker,
            mode="acm",
        )
    )


# ── Oyna yopilishi ───────────────────────────────────────────────────


def hack_phase_pending(contest: Contest) -> bool:
    """Reyting hack fazasi tufayli KUTISHI kerakmi (ADR-0020, 7-tamoyil).

    Ikki sabab bilan kutiladi: oyna hali yopilmagan, yoki yopilgan-u
    qayta tekshiruv natijalari hali kelmagan. Ikkinchisi ham muhim —
    bekor qilinadigan `AC` reytingga kirib ketsa, uni keyin qaytarish
    reyting tarixini buzardi (principle #2 ning tushuntirish yuzasi).

    Qayta tekshiruv abadiy kutmaydi: `judging.reap_stuck` javobsiz
    urinishni besh daqiqadan keyin `DENIAL_OF_JUDGEMENT` ga o'giradi.
    """
    if not (contest.hack_room or contest.hack_open_minutes):
        return False
    if contest.hack_phase_closed_at is None:
        return True
    return Attempt.objects.filter(
        contest=contest,
        verdict__in=(Verdict.PENDING, Verdict.RUNNING, Verdict.TESTING_ABORTED),
    ).exists()


@transaction.atomic
def close_hack_phase(contest: Contest) -> int:
    """Oyna yopildi: testlar to'plamga qo'shiladi, `AC` lar qayta navbatga.

    Tartib SHART: avval testlar, keyin qayta tekshiruv, keyin reyting.
    Aks holda hack qilingan yechim reytingga to'g'ri deb kirib ketardi.

    Qulf `finalize_contest` dagi kabi: beat har daqiqada chaqiradi va
    ikki chaqiruv ustma-ust tushsa testlar ikki marta qo'shilardi.
    """
    locked = Contest.objects.select_for_update().get(pk=contest.pk)
    if locked.hack_phase_closed_at is not None:
        return 0

    added = 0
    problem_ids: set[int] = set()
    for hack in Hack.objects.filter(
        contest=locked, status=Hack.Status.SUCCESSFUL, added_test__isnull=True
    ).select_related("problem"):
        policy = policies.get(hack.policy)
        if policy is None or policy.adds_test != AddsTest.ON_CLOSE:
            continue
        _add_test(hack)
        if hack.added_test_id is None:
            continue
        hack.save(update_fields=["added_test", "updated_at"])
        added += 1
        if policy.rejudge_on_close:
            problem_ids.add(hack.problem_id)

    requeued = _rejudge_accepted(locked, problem_ids) if problem_ids else 0
    now = timezone.now()
    locked.hack_tests_added_at = now
    locked.hack_phase_closed_at = now
    locked.save(update_fields=["hack_tests_added_at", "hack_phase_closed_at"])
    log.info(
        "contest %s: hack fazasi yopildi — %s test, %s qayta tekshiruv",
        locked.slug,
        added,
        requeued,
    )
    return added


def _rejudge_accepted(contest: Contest, problem_ids: set[int]) -> int:
    """Yangi testlar bilan o'sha masalalardagi `AC` larni qayta tekshiradi.

    `judging.enqueue` ATAYIN ishlatilmaydi — u masalaning urinishlar
    sonini oshirardi, qayta tekshirish esa yangi urinish emas. Verdikt
    `TESTING_ABORTED`: foydalanuvchi eski natija bekor qilinganini
    ko'radi, `PENDING` esa yangi yuborishdan farq qilmasdi. Ikkalasi ham
    `rejudge` buyrug'idagi bilan bir xil.

    Chegara yo'q: yarim qoldirilgan qayta tekshiruv reytingni noto'g'ri
    ma'lumot ustida hisoblagan bo'lardi.
    """
    from judging.services import build_job

    provider = get_provider()
    sent = 0
    rows = Attempt.objects.filter(
        contest=contest, problem_id__in=problem_ids, verdict=Verdict.AC
    ).select_related("problem", "language")
    for attempt in rows.order_by("pk").iterator(chunk_size=200):
        try:
            provider.submit(build_job(attempt))
        except Exception:
            log.exception("hack qayta tekshiruvi yiqildi: urinish %s", attempt.pk)
            continue
        Attempt.objects.filter(pk=attempt.pk).update(
            verdict=Verdict.TESTING_ABORTED, judged_at=None, requeued_at=None
        )
        sent += 1
    return sent


@transaction.atomic
def abandon(hack: Hack, reason: str) -> Hack:
    """Javobi kelmagan hackni yopadi — ball ham, jarima ham yo'q.

    Judge ishni olib yiqilsa hack abadiy `TESTING` bo'lib qolardi:
    hacker natija ko'rmas, musobaqa esa yakunlanmasdi — `close_due`
    aynan shunday hackni kutadi.
    """
    return _finish(hack, Hack.Status.IGNORED, detail=reason)


# ── Judge javobi ─────────────────────────────────────────────────────


@transaction.atomic
def apply_hack_result(result: dict[str, Any]) -> Hack | None:
    """Judge natijasini hack bosqichiga qo'llaydi.

    `judging.tasks.drain_results` shu funksiyaga `hack_id` bo'yicha
    yo'naltiradi. Natija kechikib kelishi yoki takrorlanishi mumkin,
    shuning uchun bosqich SOLISHTIRILADI: eski bosqichning javobi
    keyingisini buzib yubormaydi.
    """
    hack_id = result.get("hack_id")
    if not hack_id:
        return None
    hack = Hack.objects.select_for_update().filter(pk=hack_id).first()
    if hack is None:
        log.warning("natija topilmagan hack uchun keldi: %s", hack_id)
        return None
    if hack.status != Hack.Status.TESTING:
        return hack
    if result.get("hack_stage") != hack.stage:
        log.info("hack %s: eski bosqich javobi tashlandi (%s)", hack.pk, result.get("hack_stage"))
        return hack

    verdict = str(result.get("verdict") or Verdict.IE)
    stdout = ""
    per_test = result.get("per_test") or []
    if per_test:
        stdout = str(per_test[0].get("stdout") or "")
    detail = str(result.get("compile_output") or "")

    if hack.stage == Hack.Stage.GENERATE:
        return _after_generator(hack, verdict, stdout, detail)
    if hack.stage == Hack.Stage.REFERENCE:
        return _after_reference(hack, verdict, stdout, detail)
    return _after_defender(hack, verdict, detail)


def _after_generator(hack: Hack, verdict: str, stdout: str, detail: str) -> Hack:
    if verdict != Verdict.AC or not stdout.strip():
        return _finish(
            hack,
            Hack.Status.GENERATOR_CRASHED,
            detail=detail or f"generator {verdict} berdi",
        )
    if len(stdout.encode()) > settings.HACK_GENERATOR_OUTPUT_KB * 1024:
        return _finish(hack, Hack.Status.GENERATOR_CRASHED, detail="generator chiqishi juda katta")

    storage.ensure_bucket()
    hack.input_ref = storage.put_test_data(f"hacks/{hack.pk}.in", stdout)
    hack.input_size = len(stdout.encode())
    hack.stage = Hack.Stage.REFERENCE
    hack.save(update_fields=["input_ref", "input_size", "stage", "updated_at"])
    _enqueue_reference(hack, stdout)
    return hack


def _after_reference(hack: Hack, verdict: str, stdout: str, detail: str) -> Hack:
    # Validator kiritmani rad etdi — JAZO YO'Q (ADR-0020, 3-qaror).
    if verdict == Verdict.WRONG_TEST:
        return _finish(
            hack, Hack.Status.INVALID_INPUT, detail=detail or "kiritma cheklovga mos emas"
        )
    if verdict != Verdict.AC:
        # Etalon yechimning o'zi yiqildi: masala sozlamasi nuqsoni,
        # hackerning aybi emas (ADR-0021).
        log.error("hack %s: etalon yechim %s berdi (masala %s)", hack.pk, verdict, hack.problem_id)
        return _finish(hack, Hack.Status.IGNORED, detail=f"etalon yechim {verdict} berdi")

    storage.ensure_bucket()
    hack.output_ref = storage.put_test_data(f"hacks/{hack.pk}.out", stdout)
    hack.stage = Hack.Stage.DEFEND
    hack.save(update_fields=["output_ref", "stage", "updated_at"])
    _enqueue_defender(hack)
    return hack


def _after_defender(hack: Hack, verdict: str, detail: str) -> Hack:
    hack.defender_verdict = verdict
    if verdict in (Verdict.IE, Verdict.CHECKER_ERROR, Verdict.DENIAL_OF_JUDGEMENT):
        return _finish(hack, Hack.Status.IGNORED, detail=detail or f"judge {verdict} berdi")
    if verdict == Verdict.AC:
        return _finish(hack, Hack.Status.UNSUCCESSFUL, verdict=verdict)
    return _finish(hack, Hack.Status.SUCCESSFUL, verdict=verdict, detail=detail)


def _finish(hack: Hack, status: str, *, verdict: str = "", detail: str = "") -> Hack:
    """Yakuniy holatni yozadi va oqibatlarini qo'llaydi."""
    hack.status = status
    hack.stage = Hack.Stage.DONE
    hack.judged_at = timezone.now()
    if verdict:
        hack.defender_verdict = verdict
    if detail:
        hack.detail = detail[:2000]
    policy = policies.get(hack.policy)

    if status == Hack.Status.SUCCESSFUL and policy is not None:
        hack.points = policy.success_points
        _mark_defender_hacked(hack)
        if policy.adds_test == AddsTest.IMMEDIATE:
            _add_test(hack)
        if policy.qvant_reward:
            _reward(hack, policy.qvant_reward)
    elif status == Hack.Status.UNSUCCESSFUL and policy is not None:
        hack.points = policy.failure_points

    hack.save()
    _notify(hack)
    if policy is not None and policy.affects_standings and hack.contest_id:
        from contests.tasks import rebuild_standings_task
        from core.tasks import queue

        queue(rebuild_standings_task, hack.contest_id)
    return hack


def _mark_defender_hacked(hack: Hack) -> None:
    """Himoyachining urinishi `HACKED` bo'ladi va `AC` bekor qilinadi.

    Quyi oqim odatdagidek: yechilgan masala yozuvi, Skills reytingi va
    Qvant `judging.services.apply_result` dagi rejudge yo'li bilan bir
    xil tarzda qaytariladi.
    """
    attempt = hack.defender_attempt
    if attempt.verdict != Verdict.AC:
        return
    attempt.verdict = Verdict.HACKED
    attempt.judged_at = timezone.now()
    attempt.save(update_fields=["verdict", "judged_at"])

    from ratings.services import on_accept_revoked

    on_accept_revoked(attempt)


def _add_test(hack: Hack) -> None:
    """Muvaffaqiyatli hack testini masalaning asosiy to'plamiga qo'shadi."""
    if hack.added_test_id or not (hack.input_ref and hack.output_ref):
        return
    last = TestCase.objects.filter(problem=hack.problem).order_by("-order").first()
    test = TestCase.objects.create(
        problem=hack.problem,
        order=(last.order + 1) if last else 1,
        input_ref=hack.input_ref,
        output_ref=hack.output_ref,
        origin=TestCase.Origin.HACK,
    )
    hack.added_test = test


def _reward(hack: Hack, amount: int) -> None:
    """Amaliyot mukofoti — faqat ledger orqali (ADR-0002).

    Kunlik shift ledgerning o'zida: farm qilmoqchi bo'lgan foydalanuvchi
    100 Qvant dan keyin hech narsa olmaydi.
    """
    from qvant.ledger import credit
    from qvant.models import QvantTransaction

    try:
        credit(
            hack.hacker,
            amount,
            QvantTransaction.Reason.HACK,
            ref_type="hack",
            ref_id=str(hack.pk),
        )
    except Exception:
        log.exception("hack %s uchun Qvant berilmadi", hack.pk)


def _notify(hack: Hack) -> None:
    """Ikkala tomonga ham xabar: hacker natijani, himoyachi sababini biladi."""
    from notifications.models import Notification
    from notifications.services import notify

    slug = hack.problem.slug
    labels: dict[str, str] = {
        Hack.Status.SUCCESSFUL: f"Hack muvaffaqiyatli — {slug}",
        Hack.Status.UNSUCCESSFUL: f"Hack ishlamadi — {slug}",
        Hack.Status.INVALID_INPUT: f"Hack testi yaroqsiz — {slug}",
        Hack.Status.GENERATOR_CRASHED: f"Generator yiqildi — {slug}",
        Hack.Status.IGNORED: f"Hack hisobga olinmadi — {slug}",
    }
    title = labels.get(hack.status)
    if title:
        notify(
            hack.hacker,
            Notification.Kind.HACK,
            title,
            body=hack.detail,
            ref_type="hack",
            ref_id=str(hack.pk),
        )
    if hack.status == Hack.Status.SUCCESSFUL:
        notify(
            hack.defender_attempt.user,
            Notification.Kind.HACK,
            f"Yechimingiz hack qilindi — {slug}",
            body=f"Yangi testda {hack.defender_verdict}",
            ref_type="attempt",
            ref_id=str(hack.defender_attempt_id),
        )
