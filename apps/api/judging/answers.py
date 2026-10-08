"""Answer-file submissions — task kind `answer` (ADR-0053).

The solver sends the answers, not a program: one text file per test, picked
one by one or packed in a zip. Nothing of theirs is executed; the judge
runs the author's checker over each file.

The rules a solver meets are all here:

- a file belongs to the test whose number is the first number in its name
  (`3.out`, `03.txt`, `test3.out`);
- at most `MAX_FILES` files and `MAX_BYTES` in total, zipped or not —
  counted on the unpacked size, so a small archive cannot expand past it;
- a test with no file keeps the answer the solver last sent for it. An
  answer task is solved one test at a time, often by hand; having to send
  every finished file again with each new one would punish exactly the
  work the task asks for.
"""

from __future__ import annotations

import io
import re
import zipfile
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import TYPE_CHECKING, Any

from problems import storage
from problems.answertasks import (
    ANSWER_LANGUAGE,
    answer_language,
    inputs_archive,
    judged_orders,
)

if TYPE_CHECKING:
    from collections.abc import Iterable

    from judging.models import Attempt

#: ADR-0053: 10 MB and 50 files.
MAX_BYTES = 10 * 1024 * 1024
MAX_FILES = 50

__all__ = [
    "ANSWER_LANGUAGE",
    "MAX_BYTES",
    "MAX_FILES",
    "AnswerError",
    "answer_language",
    "inputs_archive",
    "judged_orders",
    "read_upload",
    "submit",
    "test_order",
]

_NUMBER = re.compile(r"\d+")


class AnswerError(ValueError):
    """The upload cannot be accepted; the message is shown to the solver."""


@dataclass(frozen=True)
class Stored:
    order: int
    ref: str
    size: int
    #: Taken from an earlier attempt, not sent with this one.
    carried: bool


def test_order(filename: str) -> int | None:
    """`03.out` → 3. `None` when the name carries no number."""
    match = _NUMBER.search(PurePosixPath(filename.replace("\\", "/")).stem)
    return int(match.group()) if match else None


def _decode(name: str, raw: bytes) -> str:
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        raise AnswerError(f"{name}: an answer file must be UTF-8 text") from None


def _unzip(archive: bytes) -> Iterable[tuple[str, bytes]]:
    try:
        bundle = zipfile.ZipFile(io.BytesIO(archive))
    except zipfile.BadZipFile:
        raise AnswerError("The archive is not a zip file") from None
    with bundle:
        entries = [info for info in bundle.infolist() if not info.is_dir()]
        if len(entries) > MAX_FILES:
            raise AnswerError(f"The archive holds more than {MAX_FILES} files")
        # The declared sizes are checked before a byte is unpacked.
        if sum(info.file_size for info in entries) > MAX_BYTES:
            raise AnswerError(f"The archive unpacks to more than {MAX_BYTES // 1024 // 1024} MB")
        for info in entries:
            with bundle.open(info) as handle:
                data = handle.read(MAX_BYTES + 1)
            if len(data) > MAX_BYTES:
                raise AnswerError(
                    f"The archive unpacks to more than {MAX_BYTES // 1024 // 1024} MB"
                )
            yield info.filename, data


def read_upload(
    orders: list[int], archive: bytes | None, files: Iterable[tuple[str, bytes]]
) -> dict[int, str]:
    """The answers of one submission, by test order.

    `files` are `(name, content)` pairs sent on their own; `archive` is a
    zip of such files. Both may be given: a file sent on its own wins over
    the archive's file for the same test.
    """
    named: list[tuple[str, bytes]] = list(_unzip(archive)) if archive else []
    packed = len(named)
    named += list(files)
    if len(named) > MAX_FILES:
        raise AnswerError(f"More than {MAX_FILES} files were sent")
    if sum(len(raw) for _name, raw in named) > MAX_BYTES:
        raise AnswerError(f"The files exceed {MAX_BYTES // 1024 // 1024} MB in total")

    known = set(orders)
    answers: dict[int, str] = {}
    origin: dict[int, bool] = {}
    for position, (name, raw) in enumerate(named):
        order = test_order(name)
        if order is None:
            raise AnswerError(f"{name}: the file name must contain the test number, like 3.out")
        if order not in known:
            raise AnswerError(f"{name}: this problem has no test {order}")
        from_archive = position < packed
        if order in answers and origin[order] == from_archive:
            raise AnswerError(f"{name}: test {order} was sent twice")
        answers[order] = _decode(name, raw)
        origin[order] = from_archive
    if not answers:
        raise AnswerError("No answer file was sent")
    return answers


def store(attempt: Attempt, answers: dict[int, str]) -> list[Stored]:
    """Write this attempt's answers and carry the rest over.

    Returns one entry per test that has an answer, sent now or earlier.
    """
    from judging.models import AttemptAnswer

    orders = judged_orders(attempt.problem)
    earlier: dict[int, AttemptAnswer] = {}
    missing = [order for order in orders if order not in answers]
    if missing:
        # The newest earlier answer of this solver, per test.
        rows = AttemptAnswer.objects.filter(
            attempt__user_id=attempt.user_id,
            attempt__problem_id=attempt.problem_id,
            order__in=missing,
        ).order_by("order", "-attempt_id")
        for row in rows:
            earlier.setdefault(row.order, row)

    stored: list[Stored] = []
    for order in orders:
        if order in answers:
            text = answers[order]
            ref = storage.put_test_data(f"answers/{attempt.pk}/{order}.out", text)
            stored.append(Stored(order, ref, len(text.encode()), carried=False))
        elif order in earlier:
            row = earlier[order]
            stored.append(Stored(order, row.ref, row.size, carried=True))
    AttemptAnswer.objects.bulk_create(
        AttemptAnswer(
            attempt=attempt, order=item.order, ref=item.ref, size=item.size, carried=item.carried
        )
        for item in stored
    )
    return stored


def manifest(orders: list[int], stored: list[Stored]) -> str:
    """What the attempt page shows in place of source code."""
    by_order = {item.order: item for item in stored}
    lines = []
    for order in orders:
        item = by_order.get(order)
        if item is None:
            lines.append(f"{order:02d}  -")
        elif item.carried:
            lines.append(f"{order:02d}  {item.size} B  (earlier attempt)")
        else:
            lines.append(f"{order:02d}  {item.size} B")
    return "\n".join(lines) + "\n"


def job_answers(attempt_id: int) -> dict[int, str]:
    """Test order → storage reference, for the judge job."""
    from judging.models import AttemptAnswer

    return dict(AttemptAnswer.objects.filter(attempt_id=attempt_id).values_list("order", "ref"))


def submit(user: Any, problem: Any, answers: dict[int, str], **fields: Any) -> Attempt:
    """Create the attempt with its files; the caller enqueues it."""
    from judging.models import Attempt
    from judging.verdicts import Verdict

    attempt = Attempt.objects.create(
        user=user,
        problem=problem,
        language=answer_language(),
        source_code="-",
        verdict=Verdict.PENDING,
        **fields,
    )
    stored = store(attempt, answers)
    attempt.source_code = manifest(judged_orders(problem), stored)
    attempt.save(update_fields=["source_code", "source_size"])
    return attempt
