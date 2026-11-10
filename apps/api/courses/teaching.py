"""A course given to a classroom (ADR-0056 part 8).

The teacher gives a published course to a class. A free course enrols every
student at once, and every student who joins later; a Qvant or paid course
is unlocked by each student. Anyone can create a class and share its join
code, so a class must never open a priced course (owner decision
2026-11-10).

The teacher's report lives here, not in `classroom`: it is course logic
(required lessons, the final quiz, certificates) and must show the same
numbers the student sees on the course page.
"""

from __future__ import annotations

import logging
from collections.abc import Iterable
from datetime import datetime
from typing import Any

from django.db import transaction

from core.models import User
from courses import progress, services
from courses.models import Course, CourseCertificate, Enrollment, LessonProgress
from courses.serializers import _text
from quizzes import services as quizzes

log = logging.getLogger(__name__)


def assignable(slug: str) -> Course | None:
    """A course a teacher may give to a class: any published one."""
    return Course.objects.filter(slug=slug, is_published=True).first()


def opens_for_class(course: Course) -> bool:
    """Whether giving `course` to a class enrols its students."""
    return course.is_published and course.access == Course.Access.FREE


def enroll_members(course: Course, users: Iterable[User]) -> int:
    """Enrol `users` in a free course; returns how many enrolments are new.

    An existing enrolment (free, Qvant, a purchase) is left as it is.
    """
    if not opens_for_class(course):
        return 0
    new = 0
    for user in users:
        _, created = Enrollment.objects.get_or_create(
            user=user, course=course, defaults={"source": Enrollment.Source.CLASSROOM}
        )
        if created:
            new += 1
            services.refresh_completion(user, course)
    return new


def _on_member(sender: Any, instance: Any, created: bool, **kwargs: Any) -> None:
    """A student who joins later gets the class's free courses too.

    A failure here must not undo the join: the student can still enrol from
    the course page.
    """
    if not created or instance.role != "student":
        return
    courses = Course.objects.filter(
        classroom_assignments__classroom_id=instance.classroom_id,
        access=Course.Access.FREE,
        is_published=True,
    ).distinct()
    for course in courses:
        try:
            with transaction.atomic():
                enroll_members(course, [instance.user])
        except Exception:
            log.exception("class course enrolment failed: course=%s", course.pk)


def brief(course: Course, locale: str) -> dict[str, Any]:
    row = _text(course, locale, course.base_locale)
    return {
        "slug": course.slug,
        "title": row.title if row else course.slug,
        # The title's language (ADR-0059: Uzbek follows the reader's alphabet).
        "locale": row.locale if row else course.base_locale,
        "access": course.access,
        "price_qvant": course.price_qvant,
    }


def report(course: Course, users: list[User], locale: str) -> dict[str, Any]:
    """Every student's standing in `course`, plus the curriculum to read it by."""
    lessons = list(
        progress.ordered_lessons(course)
        .select_related("section__module")
        .prefetch_related("translations", "section__module__translations")
    )
    modules: list[dict[str, Any]] = []
    for lesson in lessons:
        module = lesson.section.module
        if not modules or modules[-1]["id"] != module.pk:
            row = _text(module, locale, course.base_locale)
            modules.append({"id": module.pk, "title": row.title if row else "", "lessons": []})
        row = _text(lesson, locale, course.base_locale)
        modules[-1]["lessons"].append(
            {
                "id": lesson.pk,
                "title": row.title if row else "",
                "kind": lesson.kind,
                "is_required": lesson.is_required,
            }
        )

    order = [lesson.pk for lesson in lessons]
    required = {lesson.pk for lesson in lessons if lesson.is_required}
    ids = [user.pk for user in users]
    done: dict[int, set[int]] = {}
    last: dict[int, datetime] = {}
    for user_id, lesson_id, at in LessonProgress.objects.filter(
        user_id__in=ids, lesson_id__in=order
    ).values_list("user_id", "lesson_id", "completed_at"):
        done.setdefault(user_id, set()).add(lesson_id)
        if user_id not in last or at > last[user_id]:
            last[user_id] = at
    enrolments = {e.user_id: e for e in Enrollment.objects.filter(course=course, user_id__in=ids)}
    certificates = dict(
        CourseCertificate.objects.filter(course=course, user_id__in=ids).values_list(
            "user_id", "pk"
        )
    )
    quiz = course.final_quiz
    scores = quizzes.best_percents(ids, quiz) if quiz is not None else {}

    rows = []
    for user in users:
        finished = done.get(user.pk, set())
        enrolment = enrolments.get(user.pk)
        required_done = len(required & finished)
        certificate = certificates.get(user.pk)
        rows.append(
            {
                "username": user.username,
                "display_name": user.display_name,
                "enrolled": enrolment is not None,
                "done": required_done,
                "total": len(required),
                # The same formula as the course page (`CourseState.percent`).
                "percent": round(100 * required_done / len(required)) if required else 0,
                "completed_at": enrolment.completed_at if enrolment else None,
                "final_score": scores.get(user.pk),
                "certificate": str(certificate) if certificate else None,
                "last_activity": last.get(user.pk),
                "lessons": [lesson_id for lesson_id in order if lesson_id in finished],
            }
        )
    return {
        "course": brief(course, locale),
        "has_final_quiz": bool(course.final_quiz_id),
        "certificate_threshold": course.certificate_threshold,
        "modules": modules,
        "students": rows,
    }
