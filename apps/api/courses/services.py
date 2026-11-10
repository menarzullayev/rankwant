"""Enrolment and progress (ADR-0056 § 3.3, § 3.4).

Access to lessons goes through an `Enrollment`: free courses enrol on a click,
Qvant and paid courses enrol through their own flows (later parts) and a
classroom enrols its students. A preview lesson opens to any signed-in
visitor; a guest sees the course page and its programme, not the lessons
(ADR-0054).

Problem and quiz lessons complete on their own: a first accepted attempt
(`ratings.UserSolvedProblem`) or a quiz attempt at or above the lesson's pass
mark. Text and video lessons are completed by the learner.
"""

from __future__ import annotations

import logging
from typing import Any

from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import APIException

from core.models import User
from courses import progress
from courses.models import Course, Enrollment, Lesson, LessonProgress

log = logging.getLogger(__name__)

SELF_COMPLETED = (Lesson.Kind.TEXT, Lesson.Kind.VIDEO)


class CourseError(APIException):
    status_code: int = status.HTTP_403_FORBIDDEN
    default_code = "course_forbidden"
    default_detail = "This lesson is not open to you."


def course_error(
    code: str, detail: str, status_code: int = status.HTTP_403_FORBIDDEN
) -> CourseError:
    # `core.errors` reads the code from `default_code`, so set it per error.
    err = CourseError(detail=detail, code=code)
    err.status_code = status_code
    err.default_code = code
    return err


def enroll(user: User, course: Course) -> Enrollment:
    if course.access == Course.Access.QVANT:
        raise course_error(
            "course_qvant_required",
            "This course opens with Qvant.",
            status.HTTP_402_PAYMENT_REQUIRED,
        )
    if course.access == Course.Access.PAID:
        raise course_error(
            "course_payment_required", "This course is paid.", status.HTTP_402_PAYMENT_REQUIRED
        )
    enrollment, _ = Enrollment.objects.get_or_create(
        user=user, course=course, defaults={"source": Enrollment.Source.FREE}
    )
    return enrollment


def check_open(user: Any, lesson: Lesson, state: progress.CourseState) -> None:
    """Raise unless `user` may read `lesson` now."""
    if not getattr(user, "is_authenticated", False):
        raise course_error(
            "course_sign_in", "Sign in to open lessons.", status.HTTP_401_UNAUTHORIZED
        )
    if state.enrollment is None:
        if lesson.is_preview:
            return
        raise course_error("course_not_enrolled", "Enrol in the course to open this lesson.")
    if lesson.id not in state.unlocked:
        raise course_error("course_locked", "Finish the previous lessons first.")


def complete(user: User, lesson: Lesson) -> progress.CourseState:
    course = lesson.section.module.course
    state = progress.state(course, user)
    check_open(user, lesson, state)
    if state.enrollment is None:
        raise course_error("course_not_enrolled", "Enrol in the course to keep your progress.")
    if lesson.kind not in SELF_COMPLETED:
        raise course_error(
            "course_not_self_completed",
            "Problem and quiz lessons complete when you solve or pass them.",
            status.HTTP_400_BAD_REQUEST,
        )
    LessonProgress.objects.get_or_create(user=user, lesson=lesson)
    return refresh_completion(user, course)


def refresh_completion(user: User, course: Course) -> progress.CourseState:
    """Mark the enrolment complete once every required lesson is done."""
    state = progress.state(course, user)
    enrollment = state.enrollment
    if enrollment is not None and state.is_complete and enrollment.completed_at is None:
        enrollment.completed_at = timezone.now()
        enrollment.save(update_fields=["completed_at"])
    return state


def _record(user: User, lessons: list[Lesson]) -> None:
    courses: dict[int, Course] = {}
    for lesson in lessons:
        course = lesson.section.module.course
        state = progress.state(course, user)
        if state.enrollment is None or lesson.id not in state.unlocked:
            continue
        LessonProgress.objects.get_or_create(user=user, lesson=lesson)
        courses[course.id] = course
    for course in courses.values():
        refresh_completion(user, course)


def on_problem_solved(user: User, problem_id: int) -> None:
    lessons = list(
        Lesson.objects.filter(kind=Lesson.Kind.PROBLEM, problem_id=problem_id).select_related(
            "section__module__course"
        )
    )
    if lessons:
        _record(user, lessons)


def on_quiz_attempt(user: User, quiz_id: int, score: int, total: int) -> None:
    if total <= 0:
        return
    lessons = [
        lesson
        for lesson in Lesson.objects.filter(kind=Lesson.Kind.QUIZ, quiz_id=quiz_id).select_related(
            "section__module__course"
        )
        if score * 100 >= lesson.quiz_pass_percent * total
    ]
    if lessons:
        _record(user, lessons)


# Signals are connected by sender name: `courses` never imports other apps'
# models (tools/check_architecture.py). A failure here must not undo the
# accepted attempt or the quiz result, so it is logged and swallowed.


def _on_solved(sender: object, instance: object, created: bool, **kwargs: object) -> None:
    if not created:
        return
    try:
        with transaction.atomic():
            on_problem_solved(instance.user, instance.problem_id)  # type: ignore[attr-defined]
    except Exception:
        log.exception("courses: problem progress not recorded")


def _on_quiz(sender: object, instance: object, created: bool, **kwargs: object) -> None:
    if not created:
        return
    try:
        with transaction.atomic():
            on_quiz_attempt(
                instance.user,  # type: ignore[attr-defined]
                instance.quiz_id,  # type: ignore[attr-defined]
                instance.score,  # type: ignore[attr-defined]
                instance.total,  # type: ignore[attr-defined]
            )
    except Exception:
        log.exception("courses: quiz progress not recorded")


def connect() -> None:
    from django.db.models.signals import post_save

    post_save.connect(_on_solved, sender="ratings.UserSolvedProblem", dispatch_uid="courses-solved")
    post_save.connect(_on_quiz, sender="quizzes.QuizAttempt", dispatch_uid="courses-quiz")
