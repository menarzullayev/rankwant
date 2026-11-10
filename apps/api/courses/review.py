"""Who may change what in a course, and what stops it from going to review.

Owner decisions (2026-11-10, ADR-0056 part 4):

* any signed-in user writes courses, at most `MAX_DRAFTS` unpublished ones;
  staff are exempt;
* an author edits **text** at any time — it goes live at once, so a typo
  does not wait for a reviewer;
* the **structure** (modules, sections, lessons, their kinds, the course
  settings) is the author's only while the course is unpublished; after
  that it is staff-content's, because it changes the progress of everyone
  enrolled;
* access and price are staff's: an author's course is free until staff
  price it at publishing (the author's share is an open question).
"""

from __future__ import annotations

from typing import Any

from django.db.models import Q, QuerySet

from core.models import User
from core.permissions import STAFF_GROUP_CONTENT, has_staff_group
from courses.models import Course, Lesson

#: Unpublished courses one author may hold. Nobody has written a course yet,
#: so this guards the open surface against a flood rather than fitting use.
MAX_DRAFTS = 3


def is_course_staff(user: Any) -> bool:
    return has_staff_group(user, STAFF_GROUP_CONTENT)


def editable_courses(user: User) -> QuerySet[Course]:
    """Courses `user` may open in the studio: their own, or all for staff."""
    if is_course_staff(user):
        return Course.objects.all()
    return Course.objects.filter(authors=user)


def structure_open(user: Any, course: Course) -> bool:
    """May `user` change the course's structure and settings now?"""
    return not course.is_published or is_course_staff(user)


def reviewers() -> QuerySet[User]:
    """Who is told about a review request: active staff-content and superusers."""
    return (
        User.objects.filter(is_active=True, is_staff=True)
        .filter(Q(is_superuser=True) | Q(groups__name=STAFF_GROUP_CONTENT))
        .distinct()
    )


def _base_text(obj: Any, base: str) -> Any:
    return next((t for t in obj.translations.all() if t.locale == base), None)


def review_gaps(course: Course) -> list[str]:
    """Stable codes for what a reviewer would send back; empty when ready.

    Only what can be checked: a reviewer still reads the course.
    """
    base = course.base_locale
    gaps: list[str] = []
    text = _base_text(course, base)
    if text is None or not text.title.strip():
        gaps.append("title")
    if text is None or not text.summary.strip():
        gaps.append("summary")
    lessons = list(
        Lesson.objects.filter(section__module__course=course)
        .select_related("problem", "quiz")
        .prefetch_related("translations")
    )
    if not lessons:
        gaps.append("lessons")
    for lesson in lessons:
        row = _base_text(lesson, base)
        if row is None or not row.title.strip():
            gaps.append("lesson_title")
        if lesson.kind == Lesson.Kind.TEXT and (row is None or not row.body.strip()):
            gaps.append("lesson_text")
        if lesson.kind == Lesson.Kind.PROBLEM and (
            lesson.problem is None or not lesson.problem.is_public
        ):
            gaps.append("lesson_problem")
        if lesson.kind == Lesson.Kind.QUIZ and (
            lesson.quiz is None or not lesson.quiz.is_published
        ):
            gaps.append("lesson_quiz")
        if lesson.kind == Lesson.Kind.VIDEO and not lesson.video_ref.strip():
            gaps.append("lesson_video")
    return list(dict.fromkeys(gaps))
