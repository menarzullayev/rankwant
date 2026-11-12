"""One entry point: `ask(request, config) -> Answer` (ADR-0065).

The caller reads the rows and the settings; this module chooses the model,
builds the prompt, calls the provider and filters the answer. It never
touches the database, so it can move into a service of its own later (D6).
"""

from __future__ import annotations

from ai import guard, prompts
from ai.providers import anthropic_api, claude_cli
from ai.types import HINT_LEVELS, KINDS, AIError, Answer, Config, TutorRequest

PROVIDERS = {claude_cli.NAME: claude_cli.complete, anthropic_api.NAME: anthropic_api.complete}


def model_for(request: TutorRequest, config: Config) -> str:
    """The stronger model reads code: «Nega xato?» and a question with code
    attached (decision ⑥, owner choice 2026-11-12). Everything else — the
    statement, the hint ladder — goes to the light one."""
    if request.kind == "why_wrong" or request.code is not None:
        return config.heavy_model
    return config.light_model


def validate(request: TutorRequest) -> None:
    if request.kind not in KINDS:
        raise AIError("invalid", f"unknown kind {request.kind!r}")
    if request.kind == "hint" and request.hint_level not in HINT_LEVELS:
        raise AIError("invalid", f"hint level {request.hint_level!r}")
    if request.kind == "why_wrong" and (request.verdict is None or request.code is None):
        raise AIError("invalid", "why_wrong needs the attempt's code and verdict")
    if request.kind == "ask" and not request.question.strip():
        raise AIError("invalid", "empty question")


def ask(request: TutorRequest, config: Config) -> Answer:
    validate(request)
    complete = PROVIDERS.get(config.provider)
    if complete is None:
        raise AIError("unavailable", f"provider {config.provider!r} is off")
    model = model_for(request, config)
    text, usage = complete(
        model, prompts.system_prompt(request), prompts.user_message(request), config
    )
    text, removed = guard.strip_solution_code(text)
    return Answer(
        text=text, model=model, provider=config.provider, usage=usage, code_removed=removed
    )
