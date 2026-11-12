"""Asking the tutor: every check, then a pending reply for the `ai` worker.

The model call takes seconds (measured 6–9 s), so it never runs in a web
request: the API stores the question and a pending reply and returns 202;
the `ai` worker answers and the reply reaches the page over the user's
event stream (ADR-0029) or the next read.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from judging.verdicts import Verdict
from tutor import gate, limits
from tutor.models import Conversation, Message

MAX_QUESTION = 1_500
MAX_CODE = 20_000

#: Verdicts that are the student's to fix. A judge fault (IE, CHECKER_ERROR,
#: DENIAL_OF_JUDGEMENT …) has nothing in the code to explain.
EXPLAINABLE = frozenset(
    {
        Verdict.WA, Verdict.TLE, Verdict.MLE, Verdict.OLE, Verdict.RE, Verdict.RE_SIGNAL,
        Verdict.RE_EXIT, Verdict.CE, Verdict.PE, Verdict.HACKED, Verdict.PARTIAL,
        Verdict.COMPILE_TIMEOUT, Verdict.IDLENESS,
    }
)  # fmt: skip


@dataclass
class TutorError(Exception):
    code: str
    message: str
    http: int = 400
    details: dict[str, Any] = field(default_factory=dict)


def enabled() -> bool:
    return bool(settings.AI_PROVIDER)


def usage(user: Any) -> dict[str, Any]:
    return {
        "used": limits.used_today(user),
        "limit": limits.daily_limit(user),
        "resets_at": limits.resets_at(),
    }


def _check_attempt(user: Any, problem: Any, attempt_id: Any) -> Any:
    # Through the problem's reverse relation: `tutor` imports no other app's models.
    attempt = (
        problem.attempts.select_related("language").filter(pk=attempt_id, user=user).first()
        if attempt_id
        else None
    )
    if attempt is None:
        raise TutorError("attempt_not_found", "Attempt not found", 404)
    if attempt.verdict not in EXPLAINABLE:
        raise TutorError("attempt_not_explainable", "This verdict has nothing to explain", 400)
    return attempt


def ask(
    user: Any,
    problem: Any,
    *,
    kind: str,
    locale: str,
    question: str = "",
    hint_level: int | None = None,
    attempt_id: int | None = None,
    code: str = "",
    code_language: str = "",
) -> Message:
    """Store the question and a pending reply; raise `TutorError` on any refusal."""
    if not enabled():
        raise TutorError("ai_unavailable", "The AI tutor is not available", 503)
    if gate.closed_reason(problem) is not None:
        raise TutorError(gate.CONTEST, "The AI tutor is off for contest problems", 403)
    question = question.strip()
    if kind == Message.Kind.ASK and not question:
        raise TutorError("question_required", "The question is empty", 400)
    if len(question) > MAX_QUESTION or len(code) > MAX_CODE:
        raise TutorError("too_long", "The question or the code is too long", 400)
    attempt = _check_attempt(user, problem, attempt_id) if kind == Message.Kind.WHY_WRONG else None

    with transaction.atomic():
        # One request at a time per student: the daily count and the
        # one-pending rule must not be raced by two tabs.
        get_user_model().objects.select_for_update().filter(pk=user.pk).first()
        conversation, _ = Conversation.objects.get_or_create(user=user, problem=problem)
        if conversation.messages.filter(status=Message.Status.PENDING).exists():
            raise TutorError("tutor_busy", "The previous question is still being answered", 409)
        if kind == Message.Kind.HINT:
            if hint_level is None or not 1 <= hint_level <= 3:
                raise TutorError("hint_level", "The hint step is 1 to 3", 400)
            if hint_level > conversation.hint_level + 1:
                raise TutorError(
                    "hint_step", "Hints open one step at a time", 400,
                    {"next": conversation.hint_level + 1},
                )  # fmt: skip
        limit = limits.daily_limit(user)
        used = limits.used_today(user)
        if limit is not None and used >= limit:
            raise TutorError(
                "tutor_limit", "Today's AI tutor requests are used up", 429,
                {"limit": limit, "used": used, "resets_at": limits.resets_at().isoformat()},
            )  # fmt: skip
        asked = Message.objects.create(
            conversation=conversation,
            user=user,
            role=Message.Role.STUDENT,
            kind=kind,
            text=question if kind == Message.Kind.ASK else "",
            hint_level=hint_level if kind == Message.Kind.HINT else None,
            attempt=attempt,
            code=code if kind == Message.Kind.ASK else "",
            code_language=code_language[:64] if code and kind == Message.Kind.ASK else "",
            locale=locale,
        )
        reply = Message.objects.create(
            conversation=conversation,
            user=user,
            role=Message.Role.TUTOR,
            kind=kind,
            reply_to=asked,
            hint_level=asked.hint_level,
            # «Nega xato?» on the attempt page finds its reply by the attempt.
            attempt=attempt,
            locale=locale,
            status=Message.Status.PENDING,
        )
        conversation.save(update_fields=["updated_at"])

        from tutor.tasks import answer

        transaction.on_commit(lambda: answer.delay(reply.pk))
    return reply


def expired_before() -> datetime:
    """A reply still pending after this moment will not come: the worker is
    down or the call hung past its own timeout."""
    return timezone.now() - timedelta(seconds=settings.AI_TIMEOUT_S + 120)
