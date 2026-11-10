"""Where a learner stands in a course: done, open and locked lessons.

Lessons are read in curriculum order (module, section, lesson; ties by id).
Without `sequential` every lesson is open. With it, a lesson opens once every
required lesson before it is done; optional lessons never block anything.
The percentage counts required lessons only, so optional extras cannot keep
a course from completing.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from django.db.models import QuerySet

from core.models import User
from courses.access import plan_covers_courses
from courses.models import Course, Enrollment, Lesson, LessonProgress

CURRICULUM_ORDER = (
    "section__module__order",
    "section__module__id",
    "section__order",
    "section__id",
    "order",
    "id",
)


def ordered_lessons(course: Course) -> QuerySet[Lesson]:
    return Lesson.objects.filter(section__module__course=course).order_by(*CURRICULUM_ORDER)


@dataclass
class CourseState:
    enrollment: Enrollment | None
    order: list[int]
    required: set[int]
    completed: set[int] = field(default_factory=set)
    unlocked: set[int] = field(default_factory=set)

    @property
    def required_done(self) -> int:
        return len(self.required & self.completed)

    @property
    def percent(self) -> int:
        if not self.required:
            return 0
        return round(100 * self.required_done / len(self.required))

    @property
    def is_complete(self) -> bool:
        return bool(self.required) and self.required <= self.completed

    def neighbours(self, lesson_id: int) -> tuple[int | None, int | None]:
        i = self.order.index(lesson_id)
        prev_id = self.order[i - 1] if i > 0 else None
        next_id = self.order[i + 1] if i + 1 < len(self.order) else None
        return prev_id, next_id


def state(course: Course, user: Any) -> CourseState:
    """`user` may be a guest (`AnonymousUser` or `None`): nothing is enrolled or done."""
    rows = list(ordered_lessons(course).values_list("id", "is_required"))
    order = [lesson_id for lesson_id, _ in rows]
    required = {lesson_id for lesson_id, is_required in rows if is_required}
    enrollment = None
    completed: set[int] = set()
    if isinstance(user, User):
        enrollment = Enrollment.objects.filter(user=user, course=course).first()
        # A paid course opened by a plan closes when the plan lapses; the
        # progress stays and comes back with a new plan or a purchase.
        if (
            enrollment is not None
            and enrollment.source == Enrollment.Source.PLAN
            and course.access == Course.Access.PAID
            and not plan_covers_courses(user)
        ):
            enrollment = None
        completed = set(
            LessonProgress.objects.filter(user=user, lesson_id__in=order).values_list(
                "lesson_id", flat=True
            )
        )
    result = CourseState(enrollment=enrollment, order=order, required=required, completed=completed)
    if not course.sequential:
        result.unlocked = set(order)
        return result
    blocked = False
    for lesson_id, is_required in rows:
        if not blocked:
            result.unlocked.add(lesson_id)
        if is_required and lesson_id not in completed:
            blocked = True
    return result
