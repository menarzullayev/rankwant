"""Grading, the time limit and the single attempt, and the Qvant reward."""

from __future__ import annotations

import re
from collections.abc import Iterable
from datetime import datetime, timedelta
from typing import Any, TypedDict

from django.db import transaction
from django.db.models import Q, QuerySet
from django.utils import timezone

from core.models import User
from quizzes.models import Question, Quiz, QuizAttempt
from qvant import ledger
from qvant.models import QvantTransaction

#: A submit this long after the deadline still counts: the page sends the
#: answers itself at zero, and the request may take a moment to arrive.
GRACE = timedelta(seconds=60)


class QuizError(Exception):
    def __init__(self, message: str, error: str) -> None:
        super().__init__(message)
        #: The API error code (`error.<code>` on the site).
        self.code = error


class ReviewItem(TypedDict):
    question_id: int
    #: Single choice only (as before 2026-11-11); `None` for other kinds.
    chosen: int | None
    correct: int | None
    #: Any kind: a choice id, a list of them, a number or a text.
    chosen_value: Any
    correct_value: Any
    is_correct: bool
    explanation: str


def _fold(text: str) -> str:
    """Case and spaces do not count in a short text answer."""
    return re.sub(r"\s+", " ", str(text)).strip().casefold()


def accepted_texts(question: Question) -> list[str]:
    return [line.strip() for line in question.answer_text.splitlines() if line.strip()]


def _number(value: Any) -> float | None:
    try:
        return float(str(value).replace(",", ".").strip())
    except (TypeError, ValueError):
        return None


def check(question: Question, answer: Any) -> tuple[bool, Any]:
    """Whether `answer` is right, and the right answer to show for it."""
    kind = question.kind
    if kind == Question.Kind.SINGLE:
        correct = question.correct_choice_id
        return answer is not None and answer == correct, correct
    if kind == Question.Kind.MULTIPLE:
        right = sorted(c.pk for c in question.choices.all() if c.is_correct)
        given = sorted(answer) if isinstance(answer, list) else None
        return given is not None and given == right, right
    if kind == Question.Kind.NUMBER:
        value = _number(answer)
        target = question.answer_number
        ok = value is not None and target is not None and abs(value - target) <= question.tolerance
        return ok, target
    accepted = accepted_texts(question)
    ok = isinstance(answer, str) and _fold(answer) in {_fold(a) for a in accepted}
    return ok, accepted[0] if accepted else ""


def grade(quiz: Quiz, answers: dict[int, Any]) -> tuple[int, int, list[ReviewItem]]:
    """Answers against the right ones, on the server.

    The right answer is never sent before grading (the serializer has no
    `is_correct`), otherwise the quiz would mean nothing.
    """
    review: list[ReviewItem] = []
    score = 0
    items = quiz.items.select_related("question").prefetch_related("question__choices")
    for item in items:
        question = item.question
        given = answers.get(question.pk)
        ok, correct = check(question, given)
        if ok:
            score += 1
        single = question.kind == Question.Kind.SINGLE
        review.append(
            {
                "question_id": question.pk,
                "chosen": given if single and isinstance(given, int) else None,
                "correct": correct if single else None,
                "chosen_value": given,
                "correct_value": correct,
                "is_correct": ok,
                "explanation": question.explanation,
            }
        )
    return score, len(review), review


def deadline(quiz: Quiz, attempt: QuizAttempt) -> datetime | None:
    if quiz.time_limit_minutes is None or attempt.started_at is None:
        return None
    return attempt.started_at + timedelta(minutes=quiz.time_limit_minutes)


def answers_shown(quiz: Quiz) -> bool:
    """The right answers may be shown once an attempt is finished."""
    return quiz.answers_after is None or quiz.answers_after <= timezone.now()


def hidden(review: list[ReviewItem]) -> list[ReviewItem]:
    """Before `answers_after`: no right answers, no marks, no explanations."""
    return [
        {
            "question_id": item["question_id"],
            "chosen": item["chosen"],
            "correct": None,
            "chosen_value": item["chosen_value"],
            "correct_value": None,
            "is_correct": False,
            "explanation": "",
        }
        for item in review
    ]


def open_attempt(user: User, quiz: Quiz) -> QuizAttempt | None:
    return QuizAttempt.objects.filter(user=user, quiz=quiz, finished_at=None).first()


def _refuse_second(user: User, quiz: Quiz) -> None:
    if (
        quiz.one_attempt
        and QuizAttempt.objects.filter(user=user, quiz=quiz, finished_at__isnull=False).exists()
    ):
        raise QuizError("This quiz allows one attempt", error="quiz_taken")


@transaction.atomic
def start(user: User, quiz: Quiz) -> QuizAttempt:
    """Open an attempt and start the clock; a second call returns the same one."""
    ledger.lock_wallet(user)  # one row per user to serialize on
    current = open_attempt(user, quiz)
    if current is not None:
        return current
    _refuse_second(user, quiz)
    now = timezone.now()
    return QuizAttempt.objects.create(user=user, quiz=quiz, started_at=now)


@transaction.atomic
def submit(user: User, quiz: Quiz, answers: dict[int, Any]) -> tuple[QuizAttempt, list[ReviewItem]]:
    # The wallet lock also serializes the first-attempt check below: without
    # it 6 parallel submits paid 100 Qvant instead of 25 (measured).
    ledger.lock_wallet(user)
    attempt = open_attempt(user, quiz)
    if attempt is None:
        if quiz.time_limit_minutes is not None:
            raise QuizError("Start the quiz first", error="quiz_not_started")
        _refuse_second(user, quiz)
    else:
        ends = deadline(quiz, attempt)
        if ends is not None and timezone.now() > ends + GRACE:
            # Too late: the attempt closes with nothing counted.
            answers = {}

    score, total, review = grade(quiz, answers)

    # Qvant only on the FIRST finish, and never for a teacher's quiz: a
    # teacher could otherwise write a quiz and pay themselves (ADR-0002,
    # owner decision ⑪ of 2026-11-11).
    first_time = not QuizAttempt.objects.filter(
        user=user, quiz=quiz, finished_at__isnull=False
    ).exists()
    awarded = 0
    if first_time and quiz.owner_id is None and quiz.reward_qvant and total:
        tx = ledger.credit(
            user,
            quiz.reward_qvant,
            QvantTransaction.Reason.QUIZ,
            ref_type="quiz",
            ref_id=quiz.slug,
        )
        awarded = tx.amount if tx else 0

    now = timezone.now()
    stored = {str(k): v for k, v in answers.items()}
    if attempt is None:
        attempt = QuizAttempt.objects.create(
            user=user,
            quiz=quiz,
            answers=stored,
            score=score,
            total=total,
            qvant_awarded=awarded,
            started_at=now,
            finished_at=now,
        )
    else:
        attempt.answers = stored
        attempt.score = score
        attempt.total = total
        attempt.qvant_awarded = awarded
        attempt.finished_at = now
        attempt.save(update_fields=["answers", "score", "total", "qvant_awarded", "finished_at"])
    return attempt, review


def last_result(user: User, quiz: Quiz) -> tuple[QuizAttempt, list[ReviewItem]] | None:
    """The user's latest finished attempt, graded again for its review."""
    attempt = (
        QuizAttempt.objects.filter(user=user, quiz=quiz, finished_at__isnull=False)
        .order_by("-finished_at")
        .first()
    )
    if attempt is None:
        return None
    answers = {int(k): v for k, v in (attempt.answers or {}).items()}
    _, _, review = grade(quiz, answers)
    return attempt, review


def visible_to(user: User | None) -> QuerySet[Quiz]:
    """Quizzes a reader may open: public ones, plus a teacher's quiz for its
    owner and for members of a class it is given to."""
    public = Q(owner=None, is_published=True)
    if user is None or not user.is_authenticated:
        return Quiz.objects.filter(public)
    from classroom.access import classes_of

    given = Q(classroom_assignments__classroom__in=classes_of(user))
    return Quiz.objects.filter(public | Q(owner=user) | given).distinct()


def assignable(user: User, slug: str) -> Quiz | None:
    """A quiz a teacher may give a class: their own, or a public one."""
    return (
        Quiz.objects.filter(slug=slug)
        .filter(Q(owner=user) | Q(owner=None, is_published=True))
        .first()
    )


def best_percent(user: User, quiz: Quiz) -> int | None:
    """The user's best score on `quiz` in percent, or None if never taken."""
    return best_percents([user.pk], quiz).get(user.pk)


def best_percents(user_ids: Iterable[int], quiz: Quiz) -> dict[int, int]:
    """Best score in percent per user; users who never took `quiz` are absent."""
    best: dict[int, int] = {}
    for user_id, score, total in QuizAttempt.objects.filter(
        user_id__in=list(user_ids), quiz=quiz, finished_at__isnull=False
    ).values_list("user_id", "score", "total"):
        if total:
            percent = (100 * score) // total
            best[user_id] = max(best.get(user_id, percent), percent)
    return best


def class_report(quiz: Quiz, users: list[User]) -> dict[str, Any]:
    """Each student's best result, and how many got each question wrong."""
    attempts = list(
        QuizAttempt.objects.filter(quiz=quiz, user__in=users, finished_at__isnull=False)
    )
    items = list(quiz.items.select_related("question").prefetch_related("question__choices"))
    wrong = {item.question_id: 0 for item in items}
    answered = {item.question_id: 0 for item in items}
    per_user: dict[int, dict[str, Any]] = {}
    for attempt in attempts:
        row = per_user.setdefault(attempt.user_id, {"attempts": 0, "best": None})
        row["attempts"] += 1
        if row["best"] is None or attempt.score > row["best"].score:
            row["best"] = attempt
    # Wrong answers are counted on each student's best attempt.
    for row in per_user.values():
        given = {int(k): v for k, v in (row["best"].answers or {}).items()}
        for item in items:
            answered[item.question_id] += 1
            ok, _ = check(item.question, given.get(item.question_id))
            if not ok:
                wrong[item.question_id] += 1
    students = []
    for user in users:
        mine = per_user.get(user.pk)
        best = mine["best"] if mine else None
        students.append(
            {
                "username": user.username,
                "attempts": mine["attempts"] if mine else 0,
                "score": best.score if best else None,
                "total": best.total if best else len(items),
                "finished_at": best.finished_at if best else None,
            }
        )
    return {
        "quiz": quiz.slug,
        "title": quiz.title,
        "students": students,
        "questions": [
            {
                "id": item.question_id,
                "order": item.order,
                "text": item.question.text[:200],
                "wrong": wrong[item.question_id],
                "answered": answered[item.question_id],
            }
            for item in items
        ],
    }
