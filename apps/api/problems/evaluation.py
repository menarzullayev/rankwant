"""Which ways of grading a problem the judge can actually carry out.

Two fields decide how a submission is graded: `Problem.io_mode` (where the
data travels) and `Problem.checker_type` (who says whether the answer is
right). Not every pair of them is something the judge does. Before this
module a problem could be saved in a shape that looked configured and was
graded wrongly or not at all — nothing failed until a submission arrived.

Every rule here is read off the judge (`services/judge-go`), not assumed:

  `both` + `special` / `scorer`
      In `both` mode the judge accepts the answer from stdout OR from
      `output.txt` (`classifyAnswer`). The checker program, however, is
      handed stdout only (`runChecker(..., out.Stdout, ...)`). A solution
      that writes the file gives the checker an empty answer.

  `both` + `interactive`
      The interactive branch (`runInteractive`) returns before any test is
      resolved: `input.txt` is never written and `output.txt` is never read.
      The file half of `both` does not exist for such a problem.

  `interactive` / `scorer` + subtasks
      An interactive run is one dialogue scored 0 or 100; a scorer's result
      is the mean of the per-test scores. Neither path reads the subtasks,
      so the points configured on them would silently never be awarded.

  `function` task kind
      The submission is a function; `judging.services` inserts it into the
      author's harness for the chosen language and the judge runs the
      result as an ordinary program. So: the harness does the I/O (stdio
      only — a harness that also had to honour `output.txt` would be two
      programs), a dialogue with an interactor belongs to a whole program,
      and a language without a harness has nothing to be inserted into.

The rules are checked where a problem is edited (staff API, `clean()`),
where its readiness advances (S2) and where it is released — the earliest
points at which each can be known.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from problems.models import Problem

#: Stable code for API clients and the release report.
EVALUATION_MODE_INVALID = "EVALUATION_MODE_INVALID"

_FILE_IO = "both"
_STANDARD = "standard"
_NO_SUBTASKS = frozenset({"interactive", "scorer"})


def combination_error(io_mode: str, checker_type: str) -> str | None:
    """Why this `io_mode` / `checker_type` pair cannot be graded, or `None`."""
    if io_mode != _FILE_IO or checker_type == _STANDARD:
        return None
    if checker_type == "interactive":
        return (
            "io_mode 'both' cannot be combined with an interactive checker: an "
            "interactive run talks to the interactor over stdin/stdout only, "
            "input.txt is never written and output.txt is never read"
        )
    return (
        f"io_mode 'both' cannot be combined with a '{checker_type}' checker: the "
        "checker program receives stdout only, so an answer written to "
        "output.txt would reach it empty"
    )


def subtask_error(checker_type: str, has_subtasks: bool) -> str | None:
    """Why subtasks cannot be used with this checker, or `None`."""
    if not has_subtasks or checker_type not in _NO_SUBTASKS:
        return None
    return (
        f"a '{checker_type}' problem cannot have subtasks: its score does not "
        "come from them, so their points would never be awarded"
    )


def task_kind_error(task_kind: str, io_mode: str, checker_type: str) -> str | None:
    """Why this task kind cannot be combined with the other two axes, or `None`."""
    if task_kind != "function":
        return None
    if io_mode == _FILE_IO:
        return (
            "a 'function' problem cannot use io_mode 'both': its harness reads "
            "stdin and writes stdout"
        )
    if checker_type == "interactive":
        return (
            "a 'function' problem cannot be interactive: the dialogue is held "
            "by a whole program, not by a function inside a harness"
        )
    return None


def harnesses_error(problem: Problem) -> str | None:
    """A function problem needs a usable harness for every language it lists."""
    if problem.task_kind != "function":
        return None
    from problems.taskkinds import harness_error, supports_function

    rows = list(problem.languages.select_related("language"))
    if not rows:
        return "a 'function' problem lists no languages: add a harness for at least one"
    for row in rows:
        code = row.language.code
        if not supports_function(code):
            return f"language '{code}' is not offered for 'function' problems"
        error = harness_error(row.harness)
        if error:
            return f"language '{code}': {error}"
    return None


def evaluation_error(problem: Problem) -> str | None:
    """The first rule a saved problem breaks, or `None` when it can be graded."""
    return (
        combination_error(problem.io_mode, problem.checker_type)
        or subtask_error(problem.checker_type, problem.subtasks.exists())
        or task_kind_error(problem.task_kind, problem.io_mode, problem.checker_type)
        or harnesses_error(problem)
    )
