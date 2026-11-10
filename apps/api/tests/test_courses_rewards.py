"""Qvant unlock, module and course rewards, certificates (ADR-0056 part 6)."""

from __future__ import annotations

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from core.models import User
from courses import services
from courses.models import (
    Course,
    CourseCertificate,
    CourseTranslation,
    Enrollment,
    Lesson,
    LessonTranslation,
    Module,
    Section,
)
from quizzes.models import Choice, Question, Quiz, QuizQuestion
from quizzes.services import submit
from qvant import ledger
from qvant.models import QvantTransaction

pytestmark = pytest.mark.django_db


def _client(user: User) -> APIClient:
    c = APIClient()
    c.force_authenticate(user=user)
    return c


def _course(slug: str = "kurs", **kw) -> tuple[Course, list[Lesson]]:
    course = Course.objects.create(slug=slug, is_published=True, sequential=False, **kw)
    CourseTranslation.objects.create(course=course, locale="uz", title="Algoritmlar")
    lessons = []
    for m in range(2):
        module = Module.objects.create(course=course, order=m + 1, reward_qvant=10)
        section = Section.objects.create(module=module, order=1)
        lesson = Lesson.objects.create(section=section, order=1, kind=Lesson.Kind.TEXT)
        LessonTranslation.objects.create(lesson=lesson, locale="uz", title=f"Dars {m}", body="x")
        lessons.append(lesson)
    return course, lessons


def _quiz(questions: int = 4) -> Quiz:
    quiz = Quiz.objects.create(slug="yakuniy", title="Yakuniy", is_published=True)
    for i in range(questions):
        q = Question.objects.create(text=f"S{i}")
        Choice.objects.create(question=q, order=1, text="ha", is_correct=True)
        Choice.objects.create(question=q, order=2, text="yo'q")
        QuizQuestion.objects.create(quiz=quiz, question=q, order=i + 1)
    return quiz


def _answers(quiz: Quiz, right: int) -> dict[int, int]:
    items = list(quiz.items.select_related("question"))
    return {
        item.question_id: (
            item.question.choices.get(is_correct=True).pk
            if n < right
            else item.question.choices.get(is_correct=False).pk
        )
        for n, item in enumerate(items)
    }


def _credits(user: User, ref_type: str) -> list[int]:
    return list(
        QvantTransaction.objects.filter(user=user, ref_type=ref_type).values_list(
            "amount", flat=True
        )
    )


class TestQvantUnlock:
    def _url(self, course: Course) -> str:
        return reverse("course-enroll", args=[course.slug])

    def test_pays_once_and_enrols(self, user):
        course, _ = _course(access=Course.Access.QVANT, price_qvant=50)
        ledger.credit(user, 80, "admin", respect_cap=False)
        resp = _client(user).post(self._url(course), {"confirm_price": 50}, format="json")
        assert resp.status_code == 201
        assert Enrollment.objects.get().source == Enrollment.Source.QVANT
        assert ledger.get_wallet(user).balance == 30
        again = _client(user).post(self._url(course), {"confirm_price": 50}, format="json")
        assert again.status_code == 201
        assert ledger.get_wallet(user).balance == 30

    def test_a_changed_price_is_not_taken(self, user):
        course, _ = _course(access=Course.Access.QVANT, price_qvant=50)
        ledger.credit(user, 80, "admin", respect_cap=False)
        resp = _client(user).post(self._url(course), {"confirm_price": 40}, format="json")
        assert resp.status_code == 409
        assert resp.json()["error"]["code"] == "course_price_changed"
        assert ledger.get_wallet(user).balance == 80

    def test_not_enough_qvant(self, user):
        course, _ = _course(access=Course.Access.QVANT, price_qvant=50)
        resp = _client(user).post(self._url(course), {"confirm_price": 50}, format="json")
        assert resp.status_code == 402
        assert resp.json()["error"]["code"] == "course_qvant_insufficient"
        assert not Enrollment.objects.exists()


class TestRewards:
    def test_module_and_course_rewards_once(self, user):
        course, lessons = _course(reward_qvant=100)
        Enrollment.objects.create(user=user, course=course)
        services.complete(user, lessons[0])
        assert _credits(user, services.REF_MODULE) == [10]
        services.complete(user, lessons[1])
        services.complete(user, lessons[1])
        assert sorted(_credits(user, services.REF_MODULE)) == [10, 10]
        assert _credits(user, services.REF_COURSE) == [100]

    def test_rewards_ignore_the_daily_cap(self, user, settings):
        course, lessons = _course(reward_qvant=10_000)
        Enrollment.objects.create(user=user, course=course)
        for lesson in lessons:
            services.complete(user, lesson)
        assert _credits(user, services.REF_COURSE) == [10_000]


class TestCertificate:
    def test_without_a_final_quiz_the_lessons_are_enough(self, user):
        course, lessons = _course()
        Enrollment.objects.create(user=user, course=course)
        for lesson in lessons:
            services.complete(user, lesson)
        cert = CourseCertificate.objects.get()
        assert (cert.course_title, cert.name, cert.final_score) == ("Algoritmlar", "aziz", None)

    def test_the_final_quiz_must_reach_the_threshold(self, user):
        quiz = _quiz()
        course, lessons = _course(final_quiz=quiz)
        Enrollment.objects.create(user=user, course=course)
        for lesson in lessons:
            services.complete(user, lesson)
        assert not CourseCertificate.objects.exists()
        submit(user, quiz, _answers(quiz, 2))  # 50% < 70%
        assert not CourseCertificate.objects.exists()
        submit(user, quiz, _answers(quiz, 3))  # 75%
        assert CourseCertificate.objects.get().final_score == 75

    def test_quiz_first_then_lessons_also_issues(self, user):
        quiz = _quiz()
        course, lessons = _course(final_quiz=quiz)
        Enrollment.objects.create(user=user, course=course)
        submit(user, quiz, _answers(quiz, 4))
        assert not CourseCertificate.objects.exists()
        for lesson in lessons:
            services.complete(user, lesson)
        assert CourseCertificate.objects.get().final_score == 100

    def test_the_name_is_frozen(self, user):
        course, lessons = _course()
        Enrollment.objects.create(user=user, course=course)
        for lesson in lessons:
            services.complete(user, lesson)
        User.objects.filter(pk=user.pk).update(display_name="Boshqa")
        assert CourseCertificate.objects.get().name == "aziz"

    def test_public_check_and_pdf(self, user):
        course, lessons = _course()
        Enrollment.objects.create(user=user, course=course)
        for lesson in lessons:
            services.complete(user, lesson)
        cert = CourseCertificate.objects.get()
        body = APIClient().get(reverse("course-certificate", args=[cert.pk])).json()
        assert (body["course_title"], body["username"], body["course_slug"]) == (
            "Algoritmlar",
            "aziz",
            "kurs",
        )
        pdf = APIClient().get(reverse("course-certificate-pdf", args=[cert.pk]))
        assert pdf.status_code == 200
        assert pdf.content.startswith(b"%PDF")

    def test_course_page_links_the_certificate(self, user):
        course, lessons = _course()
        Enrollment.objects.create(user=user, course=course)
        for lesson in lessons:
            services.complete(user, lesson)
        body = _client(user).get(reverse("course-detail", args=[course.slug])).json()
        assert body["enrollment"]["certificate"] == str(CourseCertificate.objects.get().pk)


class TestCatchUp:
    def test_a_problem_solved_before_enrolling_counts(self, user, problem):
        from ratings.models import UserSolvedProblem

        course, _lessons = _course()
        module = Module.objects.create(course=course, order=3)
        section = Section.objects.create(module=module, order=1)
        lesson = Lesson.objects.create(
            section=section, order=1, kind=Lesson.Kind.PROBLEM, problem=problem
        )
        UserSolvedProblem.objects.create(user=user, problem=problem, difficulty_at_solve=800)
        services.enroll(user, course)
        assert lesson.progress.filter(user=user).exists()

    def test_a_quiz_passed_while_locked_counts_once_open(self, user):
        quiz = _quiz()
        course, lessons = _course()
        Course.objects.filter(pk=course.pk).update(sequential=True)
        course.refresh_from_db()
        module = Module.objects.create(course=course, order=3)
        section = Section.objects.create(module=module, order=1)
        quiz_lesson = Lesson.objects.create(
            section=section, order=1, kind=Lesson.Kind.QUIZ, quiz=quiz
        )
        Enrollment.objects.create(user=user, course=course)
        submit(user, quiz, _answers(quiz, 4))  # the lesson is still locked
        assert not quiz_lesson.progress.exists()
        for lesson in lessons:
            services.complete(user, lesson)
        assert quiz_lesson.progress.filter(user=user).exists()
        assert CourseCertificate.objects.filter(user=user, course=course).exists()
