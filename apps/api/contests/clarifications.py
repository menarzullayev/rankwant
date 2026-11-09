"""Questions during a contest, the jury's answers and announcements (ADR-0055, part 3).

Owner decisions, 2026-11-10:

- any signed-in user asks, until the contest ends; a question about a
  problem only once the problems are open (from the start);
- the jury, the organizers and staff-ops answer and announce;
- a question is private — its author and the moderators see it; an answer
  goes to the author, or to everybody when the jury publishes it;
- the answer and the announcement reach people as a notification and on
  the contest page; a new question notifies the jury;
- quick answers (yes / no / read the statement / no comment) are stored
  as codes, so each reader sees them in their own language;
- at most `MAX_QUESTIONS` questions of `MAX_LENGTH` characters per person
  per contest, one per `INTERVAL`;
- once the contest is finalized every answered question is public. The
  author's name never is.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import Any

from django.db.models import Q, QuerySet
from django.utils import timezone

from contests.models import Clarification, Contest, ContestProblem, ContestRegistration
from core.permissions import STAFF_GROUP_OPS, has_staff_group

MAX_QUESTIONS = 20
MAX_LENGTH = 1000
INTERVAL = timedelta(seconds=60)
#: How much of a question or an announcement a notification carries.
EXCERPT = 200
#: Rows one list returns, newest first.
LIST_LIMIT = 300


@dataclass
class ClarificationError(Exception):
    code: str
    message: str
    status: int = 400
    retry_after: int | None = None


def can_moderate(contest: Contest, user: Any) -> bool:
    """The jury, the organizers and staff-ops answer and announce."""
    if user is None or not getattr(user, "is_authenticated", False):
        return False
    if has_staff_group(user, STAFF_GROUP_OPS):
        return True
    return (
        contest.jury.filter(pk=user.pk).exists() or contest.organizers.filter(pk=user.pk).exists()
    )


def visible(contest: Contest, user: Any) -> QuerySet[Clarification]:
    """What this viewer may read."""
    rows = Clarification.objects.filter(contest=contest).select_related(
        "problem", "author", "answered_by"
    )
    if can_moderate(contest, user):
        return rows
    shown = Q(is_public=True, answered_at__isnull=False)
    if contest.ratings_applied_at is not None:
        # Finalized: every answered question is the archive's.
        shown = Q(answered_at__isnull=False)
    if user is not None and getattr(user, "is_authenticated", False):
        shown |= Q(author=user)
    return rows.filter(shown)


def _excerpt(text: str) -> str:
    text = " ".join(text.split())
    return text if len(text) <= EXCERPT else text[: EXCERPT - 1] + "…"


def _entry(contest: Contest, letter: str | None) -> ContestProblem | None:
    if not letter:
        return None
    if timezone.now() < contest.start_at:
        # Before the start the problems are closed; a letter would ask about
        # something nobody may see yet.
        raise ClarificationError("problems_closed", "The problems open when the contest starts")
    entry = ContestProblem.objects.filter(contest=contest, index_letter=letter).first()
    if entry is None:
        raise ClarificationError("problem_not_found", "This problem is not in the contest")
    return entry


def _clean(text: str) -> str:
    text = (text or "").strip()
    if not text:
        raise ClarificationError("text_empty", "Write the text first")
    if len(text) > MAX_LENGTH:
        raise ClarificationError("text_too_long", f"At most {MAX_LENGTH} characters")
    return text


def ask(contest: Contest, user: Any, letter: str | None, text: str) -> Clarification:
    now = timezone.now()
    if now >= contest.end_at:
        raise ClarificationError("contest_finished", "The contest has finished")
    question = _clean(text)
    entry = _entry(contest, letter)
    mine = Clarification.objects.filter(contest=contest, author=user)
    if mine.count() >= MAX_QUESTIONS:
        raise ClarificationError(
            "too_many_questions", f"At most {MAX_QUESTIONS} questions per contest", status=429
        )
    last = mine.order_by("-created_at").values_list("created_at", flat=True).first()
    if last is not None and now - last < INTERVAL:
        wait = int((INTERVAL - (now - last)).total_seconds()) + 1
        raise ClarificationError(
            "question_too_soon", "One question a minute", status=429, retry_after=wait
        )
    row = Clarification.objects.create(
        contest=contest, author=user, problem=entry, question=question
    )
    _tell_moderators(contest, row)
    return row


def answer(row: Clarification, moderator: Any, text: str, code: str, public: bool) -> Clarification:
    text = (text or "").strip()
    if code and code not in Clarification.QuickAnswer.values:
        raise ClarificationError("unknown_answer", "Unknown quick answer")
    if not code:
        text = _clean(text)
    elif len(text) > MAX_LENGTH:
        raise ClarificationError("text_too_long", f"At most {MAX_LENGTH} characters")
    was_public = row.is_public
    row.answer = text
    row.answer_code = code
    row.answered_by = moderator
    row.answered_at = timezone.now()
    row.is_public = public
    row.save(update_fields=["answer", "answer_code", "answered_by", "answered_at", "is_public"])
    _tell_author(row)
    if public and not was_public:
        _tell_everybody(row.contest, row, row.question)
    return row


def announce(contest: Contest, moderator: Any, letter: str | None, text: str) -> Clarification:
    body = _clean(text)
    entry = _entry(contest, letter)
    row = Clarification.objects.create(
        contest=contest,
        problem=entry,
        answer=body,
        answered_by=moderator,
        answered_at=timezone.now(),
        is_public=True,
    )
    _tell_everybody(contest, row, body)
    return row


# ── Notifications ────────────────────────────────────────────────────
# `Notification.Kind.SYSTEM` is named by value: an app does not import
# another app's models (`tools/check_architecture.py`).


def _tell_moderators(contest: Contest, row: Clarification) -> None:
    from core.models import User
    from notifications.services import notify_many

    ids = set(contest.jury.values_list("pk", flat=True))
    ids |= set(contest.organizers.values_list("pk", flat=True))
    if not ids:
        # A contest with no jury yet: staff-ops answer it.
        ids = set(
            User.objects.filter(is_staff=True, groups__name=STAFF_GROUP_OPS).values_list(
                "pk", flat=True
            )
        )
    if row.author_id:
        ids.discard(row.author_id)
    notify_many(
        User.objects.filter(pk__in=ids, is_active=True),
        "system",
        code="contest_question",
        params={"contest": contest.title, "text": _excerpt(row.question)},
        ref_type="contest_qa",
        ref_id=contest.slug,
    )


def _tell_author(row: Clarification) -> None:
    from notifications.services import notify

    if row.author is None:
        return
    notify(
        row.author,
        "system",
        code="contest_answer",
        params={"contest": row.contest.title, "question": _excerpt(row.question)},
        ref_type="contest_qa",
        ref_id=row.contest.slug,
    )


def _tell_everybody(contest: Contest, row: Clarification, text: str) -> None:
    """Every registered participant, but the author already told."""
    from core.models import User
    from notifications.services import notify_many

    ids = set(ContestRegistration.objects.filter(contest=contest).values_list("user_id", flat=True))
    if row.author_id:
        ids.discard(row.author_id)
    notify_many(
        User.objects.filter(pk__in=ids, is_active=True),
        "system",
        code="contest_announcement",
        params={"contest": contest.title, "text": _excerpt(row.answer or text)},
        ref_type="contest_qa",
        ref_id=contest.slug,
    )
