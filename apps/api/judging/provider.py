"""JudgeProvider — ADR-0004 shartnomasi.

API judge'ga HECH QACHON so'rov yubormaydi: worker navbatdan ish tortadi
(pull). Bu yerda faqat navbatga qo'yish va natijani o'qish bor.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from typing import Any, Protocol

from django.conf import settings


@dataclass(frozen=True)
class JudgeJob:
    job_id: str
    attempt_id: int
    language: dict[str, Any]
    source: str
    limits: dict[str, int]
    tests: list[dict[str, Any]]
    checker: dict[str, Any]
    #: IOI ballash uchun guruhlar: `{id, points, scoring}`. Bo'sh bo'lsa ACM.
    subtasks: list[dict[str, Any]] = field(default_factory=list)
    mode: str = "acm"
    #: Custom test bo'lsa — natija shu yozuvga yoziladi (attempt_id 0 bo'ladi)
    custom_run_id: int | None = None
    #: Kirish validatori (ADR-0020): `{code, compile, run, source}`.
    validator: dict[str, Any] | None = None
    #: Test kirishlari validatordan o'tkazilsinmi. Oddiy urinishda HAMISHA
    #: `False`: masalaning o'z testlarini muallif yozgan, ular ishonchli.
    #: `True` faqat job ishonchsiz kiritma olib kelganda — hack testi kabi.
    validate_input: bool = False
    #: Hack dvigateli (ADR-0020) uchun marshrut: judge bu ikki qiymatni
    #: natijada aynan qaytaradi va `drain_results` javobni to'g'ri hack
    #: va bosqichga bog'laydi.
    hack_id: int = 0
    hack_stage: str = ""

    def to_json(self) -> str:
        # ⚠️ Yangi maydon shu lug'atga ham QO'SHILISHI shart. Dataclass'ga
        # qo'shib, bu yerga qo'shmaslik — jim nuqson: maydon judge'ga
        # umuman yetib bormaydi va hech qanday xato chiqmaydi.
        return json.dumps(
            {
                "job_id": self.job_id,
                "attempt_id": self.attempt_id,
                "language": self.language,
                "source": self.source,
                "limits": self.limits,
                "tests": self.tests,
                "checker": self.checker,
                "subtasks": self.subtasks,
                "mode": self.mode,
                "custom_run_id": self.custom_run_id,
                "validator": self.validator,
                "validate_input": self.validate_input,
                "hack_id": self.hack_id,
                "hack_stage": self.hack_stage,
            }
        )


class JudgeProvider(Protocol):
    def submit(self, job: JudgeJob) -> str: ...
    def poll(self, timeout: int = 1) -> dict[str, Any] | None: ...
    #: Navbatda kutayotgan ishlar soni. Qotib qolgan urinishni
    #: yo'qolganidan ajratish uchun kerak: navbat bo'sh bo'lsa, hali
    #: javob kelmagan ish haqiqatan yo'qolgan.
    def pending_jobs(self) -> int: ...


class RedisJudgeProvider:
    """Navbat orqali — worker BRPOP qiladi."""

    def __init__(self, url: str | None = None) -> None:
        import redis

        # Judge navbati alohida Redis'da (ADR-0028: `judge-queue`): judge
        # `judge-net` (internal) tarmog'ida, sessiya/broker Redis'iga yo'q.
        # Bo'sh qiymat sessiya Redis'iga tushadi — bir tarmoqli eskirgan rejim.
        self._redis = redis.Redis.from_url(url or settings.JUDGE_QUEUE_URL)

    def submit(self, job: JudgeJob) -> str:
        self._redis.lpush(settings.JUDGE_JOBS_KEY, job.to_json())
        return job.job_id

    def pending_jobs(self) -> int:
        return int(self._redis.llen(settings.JUDGE_JOBS_KEY))  # type: ignore[arg-type]

    def poll(self, timeout: int = 1) -> dict[str, Any] | None:
        item = self._redis.brpop([settings.JUDGE_RESULTS_KEY], timeout=timeout)
        if not item:
            return None
        payload: dict[str, Any] = json.loads(item[1])  # type: ignore[index]
        return payload


class InMemoryJudgeProvider:
    """Testlar uchun — navbat o'rniga ro'yxat."""

    def __init__(self) -> None:
        self.jobs: list[JudgeJob] = []
        self.results: list[dict[str, Any]] = []

    def submit(self, job: JudgeJob) -> str:
        self.jobs.append(job)
        return job.job_id

    def pending_jobs(self) -> int:
        return len(self.jobs)

    def poll(self, timeout: int = 1) -> dict[str, Any] | None:
        return self.results.pop(0) if self.results else None


_provider: JudgeProvider | None = None


def get_provider() -> JudgeProvider:
    global _provider
    if _provider is None:
        _provider = (
            InMemoryJudgeProvider() if settings.JUDGE_PROVIDER == "memory" else RedisJudgeProvider()
        )
    return _provider


def set_provider(provider: JudgeProvider | None) -> None:
    """Testlar uchun."""
    global _provider
    _provider = provider


def new_job_id() -> str:
    return str(uuid.uuid4())
