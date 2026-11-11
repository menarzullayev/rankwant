"""The limits a submission actually runs under."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from problems.models import Language, Problem, ProblemLanguage


def memory_limit_kb(
    problem: Problem, language: Language, override: ProblemLanguage | None = None
) -> int:
    """The memory a submission in `language` gets (ADR-0060 § 2.2).

    The problem's limit is what the solution may use; the language's
    measured runtime overhead is added on top, so a JVM's 20 MB is not taken
    out of a 64 MB problem. An author who set this language's limit on the
    problem (`ProblemLanguage.memory_limit_kb`) named the exact number, and
    it is used as written.
    """
    if override is not None and override.memory_limit_kb:
        return override.memory_limit_kb
    return problem.memory_limit_kb + language.memory_overhead_kb
