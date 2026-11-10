"""Public courses API (ADR-0056, part 2): catalogue, enrolment, lessons, progress."""

from __future__ import annotations

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from courses import progress
from courses.models import (
    Course,
    CourseTranslation,
    Enrollment,
    Lesson,
    LessonProgress,
    LessonTranslation,
    Module,
    ModuleTranslation,
    Section,
    SectionTranslation,
)
from quizzes.models import Choice, Question, Quiz, QuizQuestion
from quizzes.services import submit
from ratings.models import UserSolvedProblem

pytestmark = pytest.mark.django_db


def _client(user=None) -> APIClient:
    c = APIClient()
    if user is not None:
        c.force_authenticate(user=user)
    return c


def _course(slug="cpp", access=Course.Access.FREE, sequential=True, published=True, **kw) -> Course:
    course = Course.objects.create(
        slug=slug, access=access, sequential=sequential, is_published=published, **kw
    )
    CourseTranslation.objects.create(
        course=course, locale="uz", title="C++ asoslari", summary="Qisqa"
    )
    CourseTranslation.objects.create(
        course=course, locale="en", title="C++ basics", summary="Short"
    )
    return course


def _lessons(course: Course, kinds: list[str], **kw) -> list[Lesson]:
    module = Module.objects.create(course=course, order=1)
    ModuleTranslation.objects.create(module=module, locale="uz", title="1-modul")
    section = Section.objects.create(module=module, order=1)
    SectionTranslation.objects.create(section=section, locale="uz", title="Kirish")
    out = []
    for i, kind in enumerate(kinds, start=1):
        lesson = Lesson.objects.create(section=section, order=i, kind=kind, **kw)
        LessonTranslation.objects.create(
            lesson=lesson, locale="uz", title=f"Dars {i}", body=f"Matn {i}"
        )
        out.append(lesson)
    return out


def _lesson_url(course: Course, lesson: Lesson) -> str:
    return reverse("course-lesson", args=[course.slug, lesson.pk])


def _complete_url(course: Course, lesson: Lesson) -> str:
    return reverse("course-lesson-complete", args=[course.slug, lesson.pk])


class TestCatalogue:
    def test_lists_only_published_courses(self):
        _course("live")
        _course("draft", published=False)
        body = _client().get(reverse("course-list")).json()
        assert [row["slug"] for row in body["results"]] == ["live"]

    def test_draft_course_page_is_404(self):
        _course("draft", published=False)
        assert _client().get(reverse("course-detail", args=["draft"])).status_code == 404

    def test_title_follows_the_reader_language_with_base_fallback(self):
        course = _course()
        en = _client().get(reverse("course-detail", args=[course.slug]), {"lang": "en"}).json()
        assert (en["title"], en["locale"]) == ("C++ basics", "en")
        ru = _client().get(reverse("course-detail", args=[course.slug]), {"lang": "ru"}).json()
        assert (ru["title"], ru["locale"]) == ("C++ asoslari", "uz")
        assert ru["locales"] == ["en", "uz"]

    def test_partial_translation_falls_back_field_by_field(self):
        course = _course()
        CourseTranslation.objects.filter(course=course, locale="uz").update(description="Uzun matn")
        body = _client().get(reverse("course-detail", args=[course.slug]), {"lang": "en"}).json()
        assert (body["title"], body["description"]) == ("C++ basics", "Uzun matn")

    def test_filters_by_level_and_access(self):
        _course("a", level=Course.Level.ADVANCED)
        _course("b", access=Course.Access.QVANT, price_qvant=50)
        rows = _client().get(reverse("course-list"), {"level": "advanced"}).json()["results"]
        assert [r["slug"] for r in rows] == ["a"]
        rows = _client().get(reverse("course-list"), {"access": "qvant"}).json()["results"]
        assert [r["slug"] for r in rows] == ["b"]

    def test_card_shows_my_progress(self, user):
        course = _course()
        first, _second = _lessons(course, [Lesson.Kind.TEXT, Lesson.Kind.TEXT])
        Enrollment.objects.create(user=user, course=course)
        LessonProgress.objects.create(user=user, lesson=first)
        row = _client(user).get(reverse("course-list")).json()["results"][0]
        assert (row["enrolled"], row["percent"], row["lesson_count"]) == (True, 50, 2)
        guest = _client().get(reverse("course-list")).json()["results"][0]
        assert (guest["enrolled"], guest["percent"]) == (False, None)


class TestCoursePage:
    def test_guest_sees_the_programme_with_lessons_locked(self):
        course = _course()
        preview, _locked = _lessons(course, [Lesson.Kind.TEXT, Lesson.Kind.TEXT])
        Lesson.objects.filter(pk=preview.pk).update(is_preview=True)
        body = _client().get(reverse("course-detail", args=[course.slug])).json()
        lessons = body["modules"][0]["sections"][0]["lessons"]
        assert [(row["title"], row["state"]) for row in lessons] == [
            ("Dars 1", "open"),
            ("Dars 2", "locked"),
        ]
        assert body["enrollment"] is None
        assert body["progress"]["total"] == 2

    def test_sequential_course_opens_one_lesson_at_a_time(self, user):
        course = _course()
        a, _b, _c = _lessons(course, [Lesson.Kind.TEXT] * 3)
        Enrollment.objects.create(user=user, course=course)
        LessonProgress.objects.create(user=user, lesson=a)
        body = _client(user).get(reverse("course-detail", args=[course.slug])).json()
        states = [row["state"] for row in body["modules"][0]["sections"][0]["lessons"]]
        assert states == ["done", "open", "locked"]
        assert body["progress"] == {"done": 1, "total": 3, "percent": 33, "completed": False}

    def test_optional_lesson_does_not_block(self, user):
        course = _course()
        a, b, c = _lessons(course, [Lesson.Kind.TEXT] * 3)
        Lesson.objects.filter(pk=a.pk).update(is_required=False)
        Enrollment.objects.create(user=user, course=course)
        state = progress.state(course, user)
        assert {a.pk, b.pk} <= state.unlocked
        assert c.pk not in state.unlocked

    def test_free_course_without_sequence_opens_everything(self, user):
        course = _course(sequential=False)
        lessons = _lessons(course, [Lesson.Kind.TEXT] * 3)
        Enrollment.objects.create(user=user, course=course)
        assert progress.state(course, user).unlocked == {lesson.pk for lesson in lessons}


class TestEnrol:
    def test_free_course_enrols_once(self, user):
        course = _course()
        url = reverse("course-enroll", args=[course.slug])
        assert _client(user).post(url).status_code == 201
        assert _client(user).post(url).status_code == 201
        assert Enrollment.objects.filter(user=user, course=course).count() == 1
        assert Enrollment.objects.get().source == Enrollment.Source.FREE

    def test_guest_cannot_enrol(self):
        course = _course()
        assert _client().post(reverse("course-enroll", args=[course.slug])).status_code in (
            401,
            403,
        )

    @pytest.mark.parametrize(
        ("access", "price", "status", "code"),
        [
            # A Qvant course asks the reader to confirm the price first.
            (Course.Access.QVANT, {"price_qvant": 50}, 409, "course_price_changed"),
            (Course.Access.PAID, {"price_uzs": 99_000}, 402, "course_payment_required"),
        ],
    )
    def test_priced_course_is_not_free_to_join(self, user, access, price, status, code):
        course = _course(access=access, **price)
        resp = _client(user).post(reverse("course-enroll", args=[course.slug]))
        assert resp.status_code == status
        assert resp.json()["error"]["code"] == code
        assert not Enrollment.objects.exists()


class TestLesson:
    def test_guest_gets_401(self):
        course = _course()
        (lesson,) = _lessons(course, [Lesson.Kind.TEXT])
        resp = _client().get(_lesson_url(course, lesson))
        assert resp.status_code == 401
        assert resp.json()["error"]["code"] == "course_sign_in"

    def test_preview_opens_without_enrolment(self, user):
        course = _course()
        preview, other = _lessons(course, [Lesson.Kind.TEXT, Lesson.Kind.TEXT])
        Lesson.objects.filter(pk=preview.pk).update(is_preview=True)
        assert _client(user).get(_lesson_url(course, preview)).status_code == 200
        assert _client(user).get(_lesson_url(course, other)).status_code == 403

    def test_locked_lesson_is_refused(self, user):
        course = _course()
        _a, b = _lessons(course, [Lesson.Kind.TEXT] * 2)
        Enrollment.objects.create(user=user, course=course)
        resp = _client(user).get(_lesson_url(course, b))
        assert resp.status_code == 403
        assert resp.json()["error"]["code"] == "course_locked"

    def test_lesson_body_and_neighbours(self, user):
        course = _course()
        a, b = _lessons(course, [Lesson.Kind.TEXT] * 2)
        Enrollment.objects.create(user=user, course=course)
        body = _client(user).get(_lesson_url(course, a)).json()
        assert (body["title"], body["body"], body["previous"]) == ("Dars 1", "Matn 1", None)
        assert body["next"] == {"id": b.pk, "title": "Dars 2", "state": "locked"}

    def test_lesson_of_another_course_is_404(self, user):
        course = _course("one")
        other = _course("two")
        (lesson,) = _lessons(other, [Lesson.Kind.TEXT])
        assert _client(user).get(_lesson_url(course, lesson)).status_code == 404

    def test_hls_video_never_exposes_the_storage_key(self, user):
        course = _course(sequential=False)
        (lesson,) = _lessons(
            course,
            [Lesson.Kind.VIDEO],
            video_provider=Lesson.VideoProvider.HLS,
            video_ref="videos/secret/master.m3u8",
        )
        Enrollment.objects.create(user=user, course=course)
        body = _client(user).get(_lesson_url(course, lesson)).json()
        assert body["video"]["provider"] == "hls"
        assert body["video"]["ref"] is None
        assert "secret" not in str(body)

    def test_youtube_video_returns_its_id(self, user):
        course = _course(sequential=False)
        (lesson,) = _lessons(
            course,
            [Lesson.Kind.VIDEO],
            video_provider=Lesson.VideoProvider.YOUTUBE,
            video_ref="dQw4w9WgXcQ",
        )
        Enrollment.objects.create(user=user, course=course)
        body = _client(user).get(_lesson_url(course, lesson)).json()
        assert body["video"]["ref"] == "dQw4w9WgXcQ"

    def test_hidden_problem_is_not_linked(self, user, problem):
        course = _course(sequential=False)
        (lesson,) = _lessons(course, [Lesson.Kind.PROBLEM], problem=problem)
        Enrollment.objects.create(user=user, course=course)
        body = _client(user).get(_lesson_url(course, lesson)).json()
        assert body["problem"]["slug"] == problem.slug
        problem.is_public = False
        problem.save(update_fields=["is_public"])
        assert _client(user).get(_lesson_url(course, lesson)).json()["problem"] is None


class TestComplete:
    def test_text_lessons_complete_the_course(self, user):
        course = _course()
        a, b = _lessons(course, [Lesson.Kind.TEXT] * 2)
        Enrollment.objects.create(user=user, course=course)
        first = _client(user).post(_complete_url(course, a)).json()
        assert (first["percent"], first["completed"]) == (50, False)
        second = _client(user).post(_complete_url(course, b)).json()
        assert (second["percent"], second["completed"]) == (100, True)
        assert Enrollment.objects.get().completed_at is not None

    def test_completing_twice_counts_once(self, user):
        course = _course()
        (a,) = _lessons(course, [Lesson.Kind.TEXT])
        Enrollment.objects.create(user=user, course=course)
        _client(user).post(_complete_url(course, a))
        _client(user).post(_complete_url(course, a))
        assert LessonProgress.objects.count() == 1

    def test_cannot_skip_ahead(self, user):
        course = _course()
        _a, b = _lessons(course, [Lesson.Kind.TEXT] * 2)
        Enrollment.objects.create(user=user, course=course)
        assert _client(user).post(_complete_url(course, b)).status_code == 403
        assert not LessonProgress.objects.exists()

    def test_preview_progress_needs_enrolment(self, user):
        course = _course()
        (a,) = _lessons(course, [Lesson.Kind.TEXT], is_preview=True)
        assert _client(user).post(_complete_url(course, a)).status_code == 403

    def test_problem_lesson_is_not_self_completed(self, user, problem):
        course = _course()
        (lesson,) = _lessons(course, [Lesson.Kind.PROBLEM], problem=problem)
        Enrollment.objects.create(user=user, course=course)
        assert _client(user).post(_complete_url(course, lesson)).status_code == 400


class TestAutomaticProgress:
    def test_solving_the_problem_completes_the_lesson(self, user, problem):
        course = _course()
        (lesson,) = _lessons(course, [Lesson.Kind.PROBLEM], problem=problem)
        Enrollment.objects.create(user=user, course=course)
        UserSolvedProblem.objects.create(user=user, problem=problem, difficulty_at_solve=800)
        assert LessonProgress.objects.filter(user=user, lesson=lesson).exists()
        assert Enrollment.objects.get().completed_at is not None

    def test_solving_without_enrolment_records_nothing(self, user, problem):
        course = _course()
        _lessons(course, [Lesson.Kind.PROBLEM], problem=problem)
        UserSolvedProblem.objects.create(user=user, problem=problem, difficulty_at_solve=800)
        assert not LessonProgress.objects.exists()

    def test_solving_a_locked_lesson_records_nothing(self, user, problem):
        course = _course()
        _text, _locked = _lessons(course, [Lesson.Kind.TEXT, Lesson.Kind.PROBLEM], problem=None)
        Lesson.objects.filter(pk=_locked.pk).update(problem=problem)
        Enrollment.objects.create(user=user, course=course)
        UserSolvedProblem.objects.create(user=user, problem=problem, difficulty_at_solve=800)
        assert not LessonProgress.objects.exists()

    def test_quiz_pass_mark_decides(self, user, other_user):
        quiz = Quiz.objects.create(slug="q", title="Q", is_published=True)
        for i in range(4):
            question = Question.objects.create(text=f"S{i}")
            Choice.objects.create(question=question, order=1, text="ha", is_correct=True)
            Choice.objects.create(question=question, order=2, text="yo'q")
            QuizQuestion.objects.create(quiz=quiz, question=question, order=i + 1)
        course = _course()
        (lesson,) = _lessons(course, [Lesson.Kind.QUIZ], quiz=quiz)
        right = {
            item.question_id: item.question.choices.get(is_correct=True).pk
            for item in quiz.items.select_related("question")
        }
        for u in (user, other_user):
            Enrollment.objects.create(user=u, course=course)
        two = dict(list(right.items())[:2])
        three = dict(list(right.items())[:3])
        submit(user, quiz, two)  # 50% < 70%
        submit(other_user, quiz, three)  # 75% >= 70%
        assert not LessonProgress.objects.filter(user=user, lesson=lesson).exists()
        assert LessonProgress.objects.filter(user=other_user, lesson=lesson).exists()


class TestMyCourses:
    def test_lists_enrolled_courses_with_progress(self, user):
        course = _course()
        a, _b = _lessons(course, [Lesson.Kind.TEXT] * 2)
        _course("other")
        Enrollment.objects.create(user=user, course=course)
        LessonProgress.objects.create(user=user, lesson=a)
        body = _client(user).get(reverse("my-courses")).json()
        assert [row["course"]["slug"] for row in body["results"]] == ["cpp"]
        assert body["results"][0]["progress"]["percent"] == 50

    def test_guest_is_refused(self):
        assert _client().get(reverse("my-courses")).status_code in (401, 403)
