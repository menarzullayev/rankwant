"""What the model reads, built from the rows (ADR-0065 § 2.3).

The statement goes in the student's language when a translation exists
(ADR-0058). The editorial never goes: it is the solution, and the tutor
must lead the student to it, not hand it over.
"""

from __future__ import annotations

from typing import Any

from ai import types
from problems import storage, translations
from tutor.models import Message

#: Statement fields sent to the model — `editorial` is left out on purpose.
STATEMENT_FIELDS = ("title", "statement", "input_format", "output_format", "note")
MAX_SAMPLE = 2_000
#: Turns of the same conversation the model sees.
HISTORY = 6


def problem(row: Any, locale: str) -> types.Problem:
    data = {field: getattr(row, field) or "" for field in STATEMENT_FIELDS}
    translations.apply(data, row, locale)
    parts = [data["statement"]]
    for heading, field in (
        ("Input", "input_format"),
        ("Output", "output_format"),
        ("Notes", "note"),
    ):
        if data[field]:
            parts.append(f"## {heading}\n{data[field]}")
    parts.append(
        f"Time limit: {row.time_limit_ms} ms. Memory limit: {row.memory_limit_kb // 1024} MB."
    )
    samples = tuple(
        (s["input"][:MAX_SAMPLE], s["expected"][:MAX_SAMPLE]) for s in storage.sample_tests(row)[:3]
    )
    return types.Problem(title=data["title"], statement="\n\n".join(parts), samples=samples)


def _said(message: Message) -> str:
    """A student message as a line of history."""
    if message.kind == Message.Kind.HINT:
        return f"(asked for hint {message.hint_level})"
    if message.kind == Message.Kind.WHY_WRONG:
        return "(asked why the attempt failed)"
    return message.text


def history(reply: Message) -> tuple[types.Turn, ...]:
    earlier = (
        Message.objects.filter(
            conversation_id=reply.conversation_id, created_at__lte=reply.created_at
        )
        .exclude(pk__in=[reply.pk, reply.reply_to_id or 0])
        .exclude(status__in=[Message.Status.PENDING, Message.Status.FAILED])
        .order_by("-created_at", "-pk")[: HISTORY * 2]
    )
    turns = [
        types.Turn(
            "student" if m.role == Message.Role.STUDENT else "tutor",
            _said(m) if m.role == Message.Role.STUDENT else m.text,
        )
        for m in reversed(list(earlier))
    ]
    return tuple(turns[-HISTORY:])


def request(reply: Message) -> types.TutorRequest:
    """The request for a pending tutor reply."""
    asked = reply.reply_to
    assert asked is not None
    code = verdict = None
    if asked.kind == Message.Kind.WHY_WRONG and asked.attempt is not None:
        attempt = asked.attempt
        code = types.Code(language=attempt.language.name, source=attempt.source_code)
        verdict = types.Verdict(
            code=attempt.verdict,
            test=attempt.failed_test_index,
            compile_output=attempt.compile_output,
        )
    elif asked.code:
        code = types.Code(language=asked.code_language or "unknown", source=asked.code)
    return types.TutorRequest(
        kind=asked.kind,
        locale=asked.locale,
        problem=problem(reply.conversation.problem, asked.locale),
        question=asked.text if asked.kind == Message.Kind.ASK else "",
        hint_level=asked.hint_level,
        code=code,
        verdict=verdict,
        history=history(reply),
    )
