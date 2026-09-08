"""Shartnoma: ../bakeoff/protocol.md

Bu tuzilmalar judge-go bilan BIR XIL bo'lishi shart — nomzodlar almashtiriladigan.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, NotRequired, TypedDict

# Verdict kodlari — 08-technical-spec dagi 20 talikning bake-off qismi
AC = "AC"
WA = "WA"
TLE = "TLE"
MLE = "MLE"
OLE = "OLE"
RE = "RE"
CE = "CE"
COMPILE_TIMEOUT = "COMPILE_TIMEOUT"
IDLENESS = "IDLENESS"
SECURITY_VIOLATION = "SECURITY_VIOLATION"
IE = "IE"


_TEST_KEYS = {"index", "input", "expected", "subtask", "points"}


@dataclass
class Limits:
    compile_time_ms: int = 10_000
    time_ms: int = 1_000
    memory_kb: int = 262_144
    output_kb: int = 65_536
    processes: int = 1


@dataclass
class Test:
    index: int
    input: str = ""
    expected: str = ""
    #: IOI ballash guruhi (0 = guruhsiz) va `sum` ballashda test bali.
    subtask: int = 0
    points: int = 0


@dataclass
class Subtask:
    id: int
    points: int = 0
    scoring: str = "min"


@dataclass
class Job:
    job_id: str
    language: dict[str, Any]
    source: str
    limits: Limits
    tests: list[Test]
    mode: str = "acm"
    checker: dict[str, Any] = field(default_factory=lambda: {"type": "standard"})
    subtasks: list[Subtask] = field(default_factory=list)
    attempt_id: int = 0

    @classmethod
    def from_json(cls, raw: dict[str, Any]) -> Job:
        return cls(
            job_id=raw["job_id"],
            language=raw["language"],
            source=raw["source"],
            limits=Limits(**raw["limits"]),
            # API test HAVOLASINI ham yuboradi (`input_ref`) — bu nomzod
            # inline ma'lumot bilan ishlaydi, shuning uchun notanish
            # kalitlar tashlanadi, TypeError bermaydi.
            tests=[Test(**{k: v for k, v in t.items() if k in _TEST_KEYS}) for t in raw["tests"]],
            mode=raw.get("mode", "acm"),
            checker=raw.get("checker") or {"type": "standard"},
            subtasks=[Subtask(**st) for st in raw.get("subtasks") or []],
            attempt_id=raw.get("attempt_id", 0),
        )


@dataclass
class RunOutcome:
    """Bitta sandbox ishga tushirishning natijasi."""

    stdout: str = ""
    stderr: str = ""
    exit_code: int = 0
    cpu_ms: int = 0  # CPU vaqti — TLE shu bo'yicha, wall clock bo'yicha EMAS
    wall_ms: int = 0  # IDLENESS aniqlash uchun
    peak_kb: int = 0
    oom_kill: bool = False
    timeout: bool = False
    output_exceeded: bool = False
    killed_by_sandbox: bool = False


class TestResultDict(TypedDict):
    index: int
    verdict: str
    time_ms: int
    memory_kb: int
    stdout: NotRequired[str]


class JudgeMetaDict(TypedDict):
    worker: str
    sandbox: str
    queue_wait_ms: int
    sandbox_setup_ms: int
    total_ms: int


class ResultDict(TypedDict):
    """Natija shakli — judge-go/protocol.go dagi `Result` bilan bir xil."""

    job_id: str
    verdict: str
    score: int
    time_ms: int
    memory_kb: int
    failed_test_index: int | None
    compile_output: str
    per_test: list[TestResultDict]
    judge_meta: JudgeMetaDict
