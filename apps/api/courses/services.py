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
from courses.access import plan_covers_courses
from courses.models import Course, CourseCertificate, Enrollment, Lesson, LessonProgress, Module
from quizzes import services as quizzes
from qvant import ledger

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


#: Ledger references: one per user and course (or module), so a reward or a
#: price is never taken twice.
REF_UNLOCK = "course_unlock"
REF_COURSE = "course"
REF_MODULE = "course_module"


def enroll(user: User, course: Course, *, confirm_price: int | None = None) -> Enrollment:
    existing = Enrollment.objects.filter(user=user, course=course).first()
    if existing is not None and (
        existing.source != Enrollment.Source.PLAN
        or course.access != Course.Access.PAID
        or plan_covers_courses(user)
    ):
        return existing
    if course.access == Course.Access.QVANT:
        return _enroll_with_qvant(user, course, confirm_price)
    if course.access == Course.Access.PAID:
        # Bought courses are enrolled by `grant_purchase`; here only a plan
        # that opens paid courses lets the reader in (ADR-0057).
        if not plan_covers_courses(user):
            raise course_error(
                "course_payment_required", "This course is paid.", status.HTTP_402_PAYMENT_REQUIRED
            )
        enrollment, _ = Enrollment.objects.get_or_create(
            user=user, course=course, defaults={"source": Enrollment.Source.PLAN}
        )
        refresh_completion(user, course)
        return enrollment
    enrollment, _ = Enrollment.objects.get_or_create(
        user=user, course=course, defaults={"source": Enrollment.Source.FREE}
    )
    refresh_completion(user, course)
    return enrollment


@transaction.atomic
def _enroll_with_qvant(user: User, course: Course, confirm_price: int | None) -> Enrollment:
    """Pay the course's Qvant price once and enrol (no refund — owner decision).

    The reader confirms the price they saw: a price staff changed in the
    meantime is not taken silently.
    """
    if confirm_price != course.price_qvant:
        raise course_error(
            "course_price_changed",
            "Confirm the course's current Qvant price.",
            status.HTTP_409_CONFLICT,
        )
    ledger.lock_wallet(user)
    existing = Enrollment.objects.filter(user=user, course=course).first()
    if existing is not None:
        return existing
    try:
        ledger.debit(
            user,
            course.price_qvant,
            ledger_reason(),
            ref_type=REF_UNLOCK,
            ref_id=course.slug,
        )
    except ledger.InsufficientBalance as error:
        raise course_error(
            "course_qvant_insufficient",
            "Not enough Qvant for this course.",
            status.HTTP_402_PAYMENT_REQUIRED,
        ) from error
    enrollment = Enrollment.objects.create(user=user, course=course, source=Enrollment.Source.QVANT)
    refresh_completion(user, course)
    return enrollment


def grant_purchase(user: User, course: Course) -> Enrollment:
    """A paid course was bought: it stays open for good (ADR-0057)."""
    enrollment, created = Enrollment.objects.get_or_create(
        user=user, course=course, defaults={"source": Enrollment.Source.PURCHASE}
    )
    if not created and enrollment.source != Enrollment.Source.PURCHASE:
        enrollment.source = Enrollment.Source.PURCHASE
        enrollment.save(update_fields=["source"])
    refresh_completion(user, course)
    return enrollment


def revoke_purchase(user: User, course: Course) -> None:
    """The purchase was refunded: the course closes at once (owner decision
    2026-11-10). Lesson progress and a certificate already issued stay; a
    plan that opens paid courses keeps the course open."""
    enrollment = Enrollment.objects.filter(
        user=user, course=course, source=Enrollment.Source.PURCHASE
    ).first()
    if enrollment is None:
        return
    if plan_covers_courses(user):
        enrollment.source = Enrollment.Source.PLAN
        enrollment.save(update_fields=["source"])
    else:
        enrollment.delete()


def ledger_reason() -> str:
    # `qvant.models` is another app's model module: take the value by name.
    return "course"


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
    reward_module(user, lesson.section.module)
    return refresh_completion(user, course)


def _already_met(user: User, lesson: Lesson) -> bool:
    """A problem solved, or a quiz passed, before the lesson was open."""
    if lesson.kind == Lesson.Kind.PROBLEM and lesson.problem is not None:
        return bool(lesson.problem.solvers.filter(user=user).exists())
    if lesson.kind == Lesson.Kind.QUIZ and lesson.quiz is not None:
        best = quizzes.best_percent(user, lesson.quiz)
        return best is not None and best >= lesson.quiz_pass_percent
    return False


def catch_up(user: User, course: Course) -> None:
    """Complete open problem and quiz lessons whose condition is already met.

    Their own events fire once: a problem solved in the archive before
    enrolling, or a quiz passed while its lesson was still locked, would
    otherwise leave the lesson undone for good. Completing one may open the
    next in a sequential course, hence the loop.
    """
    while True:
        state = progress.state(course, user)
        if state.enrollment is None:
            return
        pending = Lesson.objects.filter(
            id__in=state.unlocked - state.completed,
            kind__in=(Lesson.Kind.PROBLEM, Lesson.Kind.QUIZ),
        ).select_related("problem", "quiz", "section__module")
        met = [lesson for lesson in pending if _already_met(user, lesson)]
        if not met:
            return
        for lesson in met:
            LessonProgress.objects.get_or_create(user=user, lesson=lesson)
            reward_module(user, lesson.section.module)


def refresh_completion(user: User, course: Course) -> progress.CourseState:
    """Mark the enrolment complete once every required lesson is done; pay
    the course reward and issue the certificate when they are due."""
    catch_up(user, course)
    state = progress.state(course, user)
    enrollment = state.enrollment
    if enrollment is not None and state.is_complete:
        if enrollment.completed_at is None:
            enrollment.completed_at = timezone.now()
            enrollment.save(update_fields=["completed_at"])
            ledger.credit_once(
                user, course.reward_qvant, ledger_reason(), ref_type=REF_COURSE, ref_id=course.slug
            )
        issue_certificate(user, course)
    return state


def reward_module(user: User, module: Module) -> None:
    """The module's Qvant reward, once, when its last required lesson is done."""
    if not module.reward_qvant:
        return
    required = set(
        Lesson.objects.filter(section__module=module, is_required=True).values_list("id", flat=True)
    )
    if not required:
        return
    done = set(
        LessonProgress.objects.filter(user=user, lesson_id__in=required).values_list(
            "lesson_id", flat=True
        )
    )
    if required <= done:
        ledger.credit_once(
            user, module.reward_qvant, ledger_reason(), ref_type=REF_MODULE, ref_id=str(module.pk)
        )


def issue_certificate(user: User, course: Course) -> CourseCertificate | None:
    """Owner decision 2026-11-10: every required lesson, and the final quiz
    at or above the course threshold when the course has one."""
    existing = CourseCertificate.objects.filter(user=user, course=course).first()
    if existing is not None:
        return existing
    score = None
    if course.final_quiz is not None:
        score = quizzes.best_percent(user, course.final_quiz)
        if score is None or score < course.certificate_threshold:
            return None
    title_row = next((t for t in course.translations.all() if t.locale == course.base_locale), None)
    certificate, _ = CourseCertificate.objects.get_or_create(
        user=user,
        course=course,
        defaults={
            "name": (user.display_name or user.username)[:150],
            "course_title": (title_row.title if title_row else course.slug)[:200],
            "final_score": score,
        },
    )
    return certificate


def _record(user: User, lessons: list[Lesson]) -> None:
    courses: dict[int, Course] = {}
    for lesson in lessons:
        course = lesson.section.module.course
        state = progress.state(course, user)
        if state.enrollment is None or lesson.id not in state.unlocked:
            continue
        LessonProgress.objects.get_or_create(user=user, lesson=lesson)
        reward_module(user, lesson.section.module)
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
    # A final quiz passed after the lessons were done issues the certificate.
    finished = Course.objects.filter(
        final_quiz_id=quiz_id, enrollments__user=user, enrollments__completed_at__isnull=False
    )
    for course in finished:
        issue_certificate(user, course)


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

    from courses import teaching

    post_save.connect(
        teaching._on_member, sender="classroom.ClassroomMember", dispatch_uid="courses-class-member"
    )
