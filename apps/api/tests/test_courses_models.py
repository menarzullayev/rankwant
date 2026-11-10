"""Courses data model (ADR-0056): structure, access rules, translations."""

from __future__ import annotations

import pytest
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from core.permissions import STAFF_GROUP_CONTENT
from courses import i18n
from courses.models import (
    Course,
    CourseTranslation,
    Enrollment,
    Lesson,
    LessonProgress,
    LessonTranslation,
    Module,
    Section,
)

pytestmark = pytest.mark.django_db


def _tree(access: str = Course.Access.FREE, **course_kw) -> tuple[Course, Section]:
    course = Course.objects.create(slug="cpp-basics", access=access, **course_kw)
    module = Module.objects.create(course=course, order=1)
    section = Section.objects.create(module=module, order=1)
    return course, section


class TestStructure:
    def test_four_levels_hang_together(self):
        course, section = _tree()
        lesson = Lesson.objects.create(section=section, order=1, kind=Lesson.Kind.TEXT)
        assert lesson.section.module.course == course
        assert list(course.modules.get().sections.get().lessons.all()) == [lesson]

    def test_deleting_a_course_removes_its_tree(self):
        course, section = _tree()
        Lesson.objects.create(section=section, order=1)
        course.delete()
        assert not Lesson.objects.exists()
        assert not Section.objects.exists()


class TestAccessRules:
    def test_qvant_course_needs_a_qvant_price(self):
        with pytest.raises(ValidationError) as err:
            Course(slug="q", access=Course.Access.QVANT).clean()
        assert "price_qvant" in err.value.message_dict

    def test_paid_course_needs_a_price_in_som(self):
        with pytest.raises(ValidationError) as err:
            Course(slug="p", access=Course.Access.PAID).clean()
        assert "price_uzs" in err.value.message_dict

    def test_priced_courses_are_valid(self):
        Course(slug="q", access=Course.Access.QVANT, price_qvant=50).clean()
        Course(slug="p", access=Course.Access.PAID, price_uzs=97_000).clean()
        Course(slug="f").clean()


class TestLessonKinds:
    def test_problem_lesson_needs_a_problem(self):
        _, section = _tree()
        with pytest.raises(ValidationError) as err:
            Lesson(section=section, kind=Lesson.Kind.PROBLEM).clean()
        assert "problem" in err.value.message_dict

    def test_quiz_lesson_needs_a_quiz(self):
        _, section = _tree()
        with pytest.raises(ValidationError) as err:
            Lesson(section=section, kind=Lesson.Kind.QUIZ).clean()
        assert "quiz" in err.value.message_dict

    def test_video_lesson_needs_provider_and_video(self):
        _, section = _tree()
        with pytest.raises(ValidationError) as err:
            Lesson(section=section, kind=Lesson.Kind.VIDEO).clean()
        assert "video_ref" in err.value.message_dict

    def test_free_course_may_use_youtube_or_vimeo(self):
        _, section = _tree()
        for provider in (
            Lesson.VideoProvider.YOUTUBE,
            Lesson.VideoProvider.VIMEO,
            Lesson.VideoProvider.HLS,
        ):
            Lesson(
                section=section, kind=Lesson.Kind.VIDEO, video_provider=provider, video_ref="abc"
            ).clean()

    def test_paid_course_serves_video_only_from_r2(self):
        # A YouTube or Vimeo link can be shared, so a paid lesson would leak.
        _, section = _tree(access=Course.Access.PAID, price_uzs=97_000)
        with pytest.raises(ValidationError) as err:
            Lesson(
                section=section, kind=Lesson.Kind.VIDEO, video_provider="youtube", video_ref="abc"
            ).clean()
        assert "video_provider" in err.value.message_dict
        Lesson(
            section=section, kind=Lesson.Kind.VIDEO, video_provider="hls", video_ref="courses/1/v1"
        ).clean()


class TestOncePerUser:
    def test_one_enrollment_per_user_and_course(self, user):
        course, _ = _tree()
        Enrollment.objects.create(user=user, course=course)
        with pytest.raises(IntegrityError), transaction.atomic():
            Enrollment.objects.create(user=user, course=course)

    def test_one_progress_row_per_lesson(self, user):
        _, section = _tree()
        lesson = Lesson.objects.create(section=section, order=1)
        LessonProgress.objects.create(user=user, lesson=lesson)
        with pytest.raises(IntegrityError), transaction.atomic():
            LessonProgress.objects.create(user=user, lesson=lesson)

    def test_one_translation_per_locale(self):
        course, _ = _tree()
        CourseTranslation.objects.create(course=course, locale="uz", title="C++ asoslari")
        with pytest.raises(IntegrityError), transaction.atomic():
            CourseTranslation.objects.create(course=course, locale="uz", title="Takror")


class TestTranslationPick:
    def _lesson_with(self, *locales: str) -> Lesson:
        _, section = _tree()
        lesson = Lesson.objects.create(section=section, order=1)
        for code in locales:
            LessonTranslation.objects.create(lesson=lesson, locale=code, title=f"t-{code}")
        return lesson

    def test_reader_locale_wins(self):
        rows = self._lesson_with("uz", "ru").translations.all()
        assert i18n.pick(rows, "ru", "uz").locale == "ru"

    def test_falls_back_to_base_locale(self):
        rows = self._lesson_with("uz", "ru").translations.all()
        assert i18n.pick(rows, "en", "uz").locale == "uz"

    def test_falls_back_to_any_when_base_is_missing(self):
        rows = self._lesson_with("ru").translations.all()
        assert i18n.pick(rows, "en", "uz").locale == "ru"

    def test_nothing_to_pick(self):
        assert i18n.pick([], "uz", "uz") is None


def test_staff_content_manages_courses():
    from core.groups import sync_staff_groups

    sync_staff_groups()
    codes = set(
        Group.objects.get(name=STAFF_GROUP_CONTENT).permissions.values_list("codename", flat=True)
    )
    for model in ("course", "module", "section", "lesson"):
        for action in ("view", "add", "change", "delete"):
            assert f"{action}_{model}" in codes
