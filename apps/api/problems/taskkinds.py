"""What a solver submits, and how it becomes a program the judge can run.

`Problem.task_kind` is the third axis next to `io_mode` (where the answer
travels) and `checker_type` (who grades it) — ADR-0053.

`function`
    The solver writes a function, not a program. The author supplies, per
    language, a *harness*: a complete program that reads the test, calls the
    function and prints the result, with one line holding `SOLUTION_MARKER`
    where the submission goes. The two are joined here, before the job is
    built, so the judge compiles one ordinary source file and needs to know
    nothing about the kind.

    Joining text rather than linking two files is what makes ten languages
    cost the same as one: no language needs a second compile unit, a module
    path or a build file.
"""

from __future__ import annotations

import re

#: Stands alone on a line of the harness; that line is replaced.
SOLUTION_MARKER = "{{SOLUTION}}"

#: The languages a function problem can be offered in (ADR-0053): chosen by
#: how widely they are used, since production attempts were test traffic.
#: A family covers every version of the language (`cpp23`, `cpp26`, …).
FUNCTION_FAMILIES = (
    "cpp",
    "c",
    "py",
    "pypy",
    "java",
    "kotlin",
    "csharp",
    "js",
    "ts",
    "go",
    "rust",
)

_FAMILY = re.compile(r"^([a-z]+?)\d+$")


def family(language_code: str) -> str:
    """`cpp23` → `cpp`. A code without a version is its own family."""
    match = _FAMILY.match(language_code)
    return match.group(1) if match else language_code


def supports_function(language_code: str) -> bool:
    return family(language_code) in FUNCTION_FAMILIES


def harness_error(harness: str) -> str | None:
    """Why this harness cannot take a submission, or `None`."""
    if not harness.strip():
        return "the harness is empty"
    lines = [line for line in harness.splitlines() if line.strip() == SOLUTION_MARKER]
    if len(lines) != 1 or harness.count(SOLUTION_MARKER) != 1:
        return f"the harness must contain {SOLUTION_MARKER} exactly once, alone on a line"
    return None


def compose(harness: str, solution: str) -> str:
    """The program the judge compiles: the harness with the solution in place.

    The marker is found in the harness only — a submission that contains
    the marker text is inserted as it is, not expanded again.
    """
    out: list[str] = []
    for line in harness.splitlines():
        if line.strip() == SOLUTION_MARKER:
            out.append(solution.rstrip("\n"))
        else:
            out.append(line)
    return "\n".join(out) + "\n"
