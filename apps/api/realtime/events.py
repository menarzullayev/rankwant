"""Hodisa turlari va yuklari — bitta joy (ADR-0029 §4).

⚠️ **Nega alohida modul.** `event:` nomi va yuk sxemasi — server bilan
mijoz o'rtasidagi **shartnoma**. U nashr joyida ham, obuna joyida ham
yozilsa, biri o'zgarib ikkinchisi jimgina eskirib qolardi: oqim ochiladi,
hodisa keladi, lekin mijoz noto'g'ri maydonni o'qiydi — va buni faqat
brauzerda sezish mumkin. Shu sababli nomlar va yuklar shu yerda.

⚠️ **Yukka shaxsiy ma'lumot solinmaydi.** `verdict` yuki faqat raqamlar va
kodlar; manba kod, kompilyatsiya chiqishi va bildirishnoma matni **hech
qachon** oqimga tushmaydi. Sabab ikki xil: (a) ular log va proksi
buferlarida qolishi mumkin, (b) mijoz baribir to'liq yozuvni REST dan
oladi (ADR-0029 §9: oqim — optimallashtirish, haqiqat manbasi emas).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from realtime import bus

if TYPE_CHECKING:  # pragma: no cover — faqat tip uchun, import sikli yo'q
    from judging.models import Attempt

#: Urinish verdikti tayyor bo'ldi. Yuk: raqamlar va kodlar.
EVENT_VERDICT = "verdict"
#: Urinish yakunlandi (shartnoma nomi) — yuk `verdict` bilan bir xil.
EVENT_ATTEMPT_FINISHED = "attempt_finished"
#: Urinish navbatga qo'yildi.
EVENT_ATTEMPT_QUEUED = "attempt_queued"
#: Test bosqichidagi oraliq holat (legacy nom — `test_started` bilan bir xil yuk).
EVENT_ATTEMPT_PROGRESS = "attempt_progress"
#: Test boshlandi (`attempt_progress` bilan bir xil yuk).
EVENT_TEST_STARTED = "test_started"
#: Kompilyatsiya bosqichi.
EVENT_COMPILATION_STARTED = "compilation_started"
EVENT_COMPILATION_FINISHED = "compilation_finished"
#: Bitta test yakunlandi — verdict/time/memory (maxfiy I/O yo'q).
EVENT_TEST_FINISHED = "test_finished"
#: Ommaviy jadval o'zgardi. Yuk: ⚠️ FAQAT versiya belgisi, jadval EMAS.
EVENT_STANDINGS = "standings"


def verdict_payload(attempt: Attempt) -> dict[str, Any]:
    """Verdikt hodisasining yuki — qatorning qisqa ko'rinishi."""
    return {
        "attempt_id": attempt.pk,
        "problem": attempt.problem.slug,
        "verdict": attempt.verdict,
        "score": attempt.score,
        "time_ms": attempt.time_ms,
        "memory_kb": attempt.memory_kb,
        "failed_test_index": attempt.failed_test_index,
        "running_test_index": attempt.running_test_index,
    }


def progress_payload(attempt: Attempt) -> dict[str, Any]:
    """Test bosqichidagi oraliq holat — faqat raqamlar."""
    meta = attempt.judge_meta or {}
    payload: dict[str, Any] = {
        "attempt_id": attempt.pk,
        "problem": attempt.problem.slug,
        "verdict": attempt.verdict,
        "running_test_index": attempt.running_test_index,
    }
    total = meta.get("total_tests")
    if total is not None:
        payload["total_tests"] = int(total)
    phase = meta.get("phase")
    if phase:
        payload["phase"] = phase
    return payload


def _attempt_channels(attempt: Attempt) -> tuple[str, str]:
    return bus.user_channel(attempt.user_id), bus.problem_channel(attempt.problem.slug)


def _publish_both(attempt: Attempt, event: str, payload: dict[str, Any]) -> None:
    user_ch, problem_ch = _attempt_channels(attempt)
    bus.publish(user_ch, event, payload)
    bus.publish(problem_ch, event, payload)


def standings_payload(contest_id: int, version: str) -> dict[str, Any]:
    """Jadval o'zgardi degan **belgi**.

    ⚠️ Jadvalning O'ZI bu yerga solinmaydi (ADR-0029 §3). Sabab
    `docs/10-operations` dagi o'lchov: 110 000 tomoshabin uchun 45 KB
    hujjatni oqim orqali tashish chekka kesh bergan narsani
    qimmatlashtiradi (7 300 so'rov/s, 330 MB/s origin'ga). Mijoz
    versiyani solishtiradi va **faqat farq bo'lsa** mavjud keshli
    endpointdan qayta oladi.
    """
    return {"contest_id": contest_id, "version": version}


def publish_verdict(attempt: Attempt) -> None:
    """Verdiktni egasiga yuboradi.

    ⚠️ Chaqiruvchi `apply_result` **qaytgandan keyin** chaqirishi shart:
    u `@transaction.atomic`, ya'ni shu paytda verdikt haqiqatan commit
    qilingan. Usiz obunachi hali ko'rinmaydigan qator haqida xabar olardi
    va REST dan qayta o'qisa eski holatni ko'rardi (ADR-0029 §6).
    """
    payload = verdict_payload(attempt)
    _publish_both(attempt, EVENT_VERDICT, payload)
    _publish_both(attempt, EVENT_ATTEMPT_FINISHED, payload)


def publish_attempt_progress(attempt: Attempt) -> None:
    """Test bosqichidagi holat — faqat egasiga."""
    payload = progress_payload(attempt)
    _publish_both(attempt, EVENT_ATTEMPT_PROGRESS, payload)
    _publish_both(attempt, EVENT_TEST_STARTED, payload)


def publish_attempt_queued(attempt: Attempt) -> None:
    _publish_both(
        attempt,
        EVENT_ATTEMPT_QUEUED,
        {
            "attempt_id": attempt.pk,
            "problem": attempt.problem.slug,
            "verdict": attempt.verdict,
            "phase": "queued",
        },
    )


def publish_compilation_started(attempt: Attempt, total_tests: int) -> None:
    _publish_both(
        attempt,
        EVENT_COMPILATION_STARTED,
        {
            "attempt_id": attempt.pk,
            "problem": attempt.problem.slug,
            "verdict": attempt.verdict,
            "total_tests": total_tests,
            "phase": "compiling",
        },
    )


def publish_compilation_finished(
    attempt: Attempt, *, ok: bool, compile_output: str = "", verdict: str | None = None
) -> None:
    payload: dict[str, Any] = {
        "attempt_id": attempt.pk,
        "problem": attempt.problem.slug,
        "ok": ok,
        "phase": "running" if ok else "failed",
    }
    if verdict:
        payload["verdict"] = verdict
    if compile_output and not ok:
        payload["compile_output"] = compile_output[:512]
    _publish_both(attempt, EVENT_COMPILATION_FINISHED, payload)


def publish_test_finished(
    attempt: Attempt,
    *,
    test_index: int,
    verdict: str,
    time_ms: int,
    memory_kb: int,
) -> None:
    _publish_both(
        attempt,
        EVENT_TEST_FINISHED,
        {
            "attempt_id": attempt.pk,
            "problem": attempt.problem.slug,
            "test_index": test_index,
            "verdict": verdict,
            "time_ms": time_ms,
            "memory_kb": memory_kb,
            "running_test_index": attempt.running_test_index,
        },
    )


def publish_standings(contest_id: int, version: str) -> None:
    bus.publish(
        bus.standings_channel(contest_id),
        EVENT_STANDINGS,
        standings_payload(contest_id, version),
    )
