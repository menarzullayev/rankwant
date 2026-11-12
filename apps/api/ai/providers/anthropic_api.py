"""The Claude API through the official SDK (decision ⑤, ADR-0065 § 2.2).

Off until there is an `ANTHROPIC_API_KEY` (owner choice 2026-11-12: «hozircha
kalitsiz»). With a key, `tutor.tasks.config()` picks this provider and falls
back to `claude -p` when the key is missing or the month's budget is spent
(decision ⑨). The answer is plain text: nothing here runs tools either, the
same prompt and the same guard apply.
"""

from __future__ import annotations

import time
from typing import Any

from ai.types import AIError, Config, Usage

NAME = "anthropic"

#: Long enough for a hint or an explanation; the guard trims code anyway.
MAX_TOKENS = 2048

#: US dollars per million tokens: (input, output). `claude-api` skill,
#: models.md (2026-11): Haiku 5.5 at $0.10 / $0.50 for prompts up to 100K
#: tokens, Sonnet 5.5 at $2 / $10. A model not listed costs as Sonnet — the
#: budget errs on the safe side.
PRICES: dict[str, tuple[float, float]] = {
    "claude-haiku-5-5": (0.10, 0.50),
    "claude-sonnet-5-5": (2.0, 10.0),
}
#: Cache reads cost a tenth of input, cache writes a quarter more (standard
#: prompt-caching multipliers). The tutor sends no cache breakpoints, so these
#: are near zero; they are counted so that a change there shows in the budget.
CACHE_READ = 0.1
CACHE_WRITE = 1.25


def cost_usd(model: str, usage: Any) -> float:
    price_in, price_out = PRICES.get(model, PRICES["claude-sonnet-5-5"])
    tokens_in = int(getattr(usage, "input_tokens", 0) or 0)
    tokens_out = int(getattr(usage, "output_tokens", 0) or 0)
    read = int(getattr(usage, "cache_read_input_tokens", 0) or 0)
    write = int(getattr(usage, "cache_creation_input_tokens", 0) or 0)
    total = (
        tokens_in * price_in
        + tokens_out * price_out
        + read * price_in * CACHE_READ
        + write * price_in * CACHE_WRITE
    )
    return total / 1_000_000


def failure_code(exc: Exception) -> str:
    """The student-facing code for an SDK error."""
    import anthropic

    if isinstance(exc, anthropic.RateLimitError):
        return "busy"
    if isinstance(exc, anthropic.APITimeoutError):
        return "timeout"
    if isinstance(exc, (anthropic.AuthenticationError, anthropic.PermissionDeniedError)):
        return "unavailable"
    if isinstance(exc, anthropic.APIConnectionError):
        return "unavailable"
    return "failed"


def complete(model: str, system: str, text: str, config: Config) -> tuple[str, Usage]:
    if not config.api_key:
        raise AIError("unavailable", "no ANTHROPIC_API_KEY")
    import anthropic

    client = anthropic.Anthropic(api_key=config.api_key, timeout=config.timeout_s, max_retries=1)
    started = time.monotonic()
    try:
        response = client.messages.create(
            model=model,
            max_tokens=MAX_TOKENS,
            system=system,
            messages=[{"role": "user", "content": text}],
        )
    except anthropic.APIError as exc:
        raise AIError(failure_code(exc), f"{model}: {type(exc).__name__}") from None
    latency = int((time.monotonic() - started) * 1000)
    raw = response.usage
    usage = Usage(
        input_tokens=int(raw.input_tokens or 0),
        output_tokens=int(raw.output_tokens or 0),
        cache_read_tokens=int(getattr(raw, "cache_read_input_tokens", 0) or 0),
        cache_write_tokens=int(getattr(raw, "cache_creation_input_tokens", 0) or 0),
        cost_usd=cost_usd(model, raw),
        latency_ms=latency,
    )
    if response.stop_reason == "refusal":
        raise AIError("refused", f"{model}: refusal")
    answer = "".join(block.text for block in response.content if block.type == "text").strip()
    if not answer:
        raise AIError("failed", f"{model}: empty answer ({response.stop_reason})")
    return answer, usage
