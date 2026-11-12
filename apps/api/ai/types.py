"""What goes into the AI tutor and what comes out (ADR-0065).

Plain dataclasses: the gateway knows nothing about the database, so the
caller (the `tutor` app) reads its rows and hands over these.
"""

from __future__ import annotations

from dataclasses import dataclass, field

#: What the student asked for. `HEAVY_KINDS` go to the stronger model.
KINDS = ("ask", "hint", "why_wrong")
#: Steps of the hint ladder (owner decision 2026-11-12: three).
HINT_LEVELS = (1, 2, 3)


@dataclass(frozen=True)
class Turn:
    """One earlier message of the same conversation."""

    role: str  # "student" | "tutor"
    text: str


@dataclass(frozen=True)
class Problem:
    title: str
    statement: str  # Markdown: legend, input, output, notes
    samples: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class Code:
    language: str  # the language's display name, e.g. "C++ 23 (GCC 14)"
    source: str


@dataclass(frozen=True)
class Verdict:
    code: str  # WA, TLE, RE, CE …
    test: int | None = None
    compile_output: str = ""


@dataclass(frozen=True)
class TutorRequest:
    kind: str
    locale: str
    problem: Problem
    question: str = ""
    hint_level: int | None = None
    code: Code | None = None
    verdict: Verdict | None = None
    history: tuple[Turn, ...] = ()


@dataclass(frozen=True)
class Usage:
    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_tokens: int = 0
    cache_write_tokens: int = 0
    #: What the call would cost on the API, as the provider reports it.
    cost_usd: float = 0.0
    latency_ms: int = 0


@dataclass(frozen=True)
class Answer:
    text: str
    model: str
    provider: str
    usage: Usage = field(default_factory=Usage)
    #: Fenced code blocks the guard took out of the answer.
    code_removed: int = 0


@dataclass(frozen=True)
class Config:
    """How to reach a model. Read from settings by the caller."""

    provider: str  # "" (off) | "claude-cli" | "anthropic"
    light_model: str
    heavy_model: str
    timeout_s: int = 120
    cli_path: str = ""
    #: `CLAUDE_CODE_OAUTH_TOKEN` from `claude setup-token`; empty = the
    #: CLI's own login (a developer machine).
    oauth_token: str = ""
    #: `ANTHROPIC_API_KEY` for the `anthropic` provider; empty = no API.
    api_key: str = ""


class AIError(RuntimeError):
    """The model gave no usable answer. `code` is shown to the student."""

    def __init__(self, code: str, detail: str = "") -> None:
        super().__init__(f"{code}: {detail}" if detail else code)
        self.code = code
        self.detail = detail
