"""The problem side of an `answer` task (ADR-0053): which tests are answered,
the public inputs, and the stand-in language an answer attempt is filed under.

Kept in this app so that `judging` reads tests through it instead of
through the models (`tools/check_architecture.py`).
"""

from __future__ import annotations

import io
import zipfile

from problems import storage, testgroups
from problems.models import Language, Problem, TestCase

#: Attempts need a language row; an answer attempt has no language. This
#: inactive row stands in, so it is offered nowhere and filters skip it.
ANSWER_LANGUAGE = "answer"


def answer_language() -> Language:
    row, _ = Language.objects.get_or_create(
        code=ANSWER_LANGUAGE,
        defaults={
            "name": "Answer files",
            "version": "",
            "source_file": "answers.txt",
            "compile_cmd": [],
            "run_cmd": ["true"],
            "is_active": False,
        },
    )
    return row


def judged_orders(problem: Problem) -> list[int]:
    """The tests a solver answers, in order."""
    return list(
        TestCase.objects.filter(problem=problem)
        .exclude(group__in=testgroups.NON_JUDGED_GROUPS)
        .order_by("order")
        .values_list("order", flat=True)
    )


def inputs_archive(problem: Problem) -> bytes:
    """The public half of an answer task: every test input, zipped."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as bundle:
        tests = (
            TestCase.objects.filter(problem=problem)
            .exclude(group__in=testgroups.NON_JUDGED_GROUPS)
            .order_by("order")
        )
        for test in tests:
            bundle.writestr(f"{test.order:02d}.in", storage.get_test_data(test.input_ref))
    return buffer.getvalue()
