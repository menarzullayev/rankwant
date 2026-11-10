"""A course given to a classroom and the teacher's report (ADR-0056 part 8)."""

from __future__ import annotations

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from classroom.models import Assignment, Classroom, ClassroomMember
from classroom.services import join, pending_assignments
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
    ModuleTranslation,
    Section,
)
from quizzes.models import Choice, Question, Quiz, QuizQuestion
from quizzes.services import submit

pytestmark = pytest.mark.django_db


def _client(user: User) -> APIClient:
    c = APIClient()
    c.force_authenticate(user=user)
    return c


def _user(name: str) -> User:
    return User.objects.create_user(username=name, password="x-pass-12345")


def _course(slug: str = "kurs", **kw) -> tuple[Course, list[Lesson]]:
    kw.setdefault("is_published", True)
    course = Course.objects.create(slug=slug, sequential=False, **kw)
    CourseTranslation.objects.create(course=course, locale="uz", title="Algoritmlar")
    lessons = []
    for m in range(2):
        module = Module.objects.create(course=course, order=m + 1)
        ModuleTranslation.objects.create(module=module, locale="uz", title=f"Modul {m}")
        section = Section.objects.create(module=module, order=1)
        lesson = Lesson.objects.create(section=section, order=1, kind=Lesson.Kind.TEXT)
        LessonTranslation.objects.create(lesson=lesson, locale="uz", title=f"Dars {m}", body="x")
        lessons.append(lesson)
    return course, lessons


@pytest.fixture
def room(user) -> Classroom:
    return Classroom.objects.create(owner=user, name="9-A", slug="9-a", join_code="J00001")


@pytest.fixture
def students(room) -> list[User]:
    people = [_user("talaba1"), _user("talaba2")]
    for person in people:
        ClassroomMember.objects.create(classroom=room, user=person)
    return people


def _assign(owner: User, room: Classroom, **body):
    body.setdefault("title", "Kurs")
    return _client(owner).post(
        reverse("classroom-assignments", args=[room.slug]), body, format="json"
    )


class TestAssign:
    def test_a_free_course_enrols_every_student(self, user, room, students):
        course, _ = _course()
        helper = _user("yordamchi")
        ClassroomMember.objects.create(
            classroom=room, user=helper, role=ClassroomMember.Role.ASSISTANT
        )
        resp = _assign(user, room, course=course.slug)
        assert resp.status_code == 201
        assert resp.json()["course"] == {
            "slug": "kurs",
            "title": "Algoritmlar",
            "locale": "uz",
            "access": "free",
            "price_qvant": 0,
        }
        enrolled = Enrollment.objects.filter(course=course)
        assert sorted(enrolled.values_list("user__username", flat=True)) == [
            "talaba1",
            "talaba2",
        ]
        assert set(enrolled.values_list("source", flat=True)) == {Enrollment.Source.CLASSROOM}

    def test_a_student_who_joins_later_is_enrolled(self, user, room, students):
        course, _ = _course()
        _assign(user, room, course=course.slug)
        late = _user("kechikkan")
        join(late, room.join_code)
        assert Enrollment.objects.filter(user=late, course=course).exists()

    def test_an_existing_enrolment_is_kept(self, user, room, students):
        course, _ = _course()
        Enrollment.objects.create(user=students[0], course=course)
        _assign(user, room, course=course.slug)
        assert Enrollment.objects.get(user=students[0]).source == Enrollment.Source.FREE

    def test_a_priced_course_is_not_opened(self, user, room, students):
        course, _ = _course(access=Course.Access.QVANT, price_qvant=50)
        resp = _assign(user, room, course=course.slug)
        assert resp.status_code == 201
        assert not Enrollment.objects.exists()
        join(_user("kechikkan"), room.join_code)
        assert not Enrollment.objects.exists()
        # The student still pays the price themselves.
        enrol = _client(students[0]).post(reverse("course-enroll", args=[course.slug]), {})
        assert enrol.status_code == 409

    def test_an_unpublished_course_is_refused(self, user, room, students):
        course, _ = _course(is_published=False)
        resp = _assign(user, room, course=course.slug)
        assert resp.status_code == 400
        assert resp.json()["error"]["code"] == "classroom_course_unavailable"
        assert not Assignment.objects.exists()

    def test_only_the_owner_assigns(self, room, students):
        course, _ = _course()
        resp = _assign(students[0], room, course=course.slug)
        assert resp.status_code == 403
        assert not Enrollment.objects.exists()

    def test_problems_or_a_course_is_needed(self, user, room):
        resp = _assign(user, room)
        assert resp.status_code == 400

    def test_problems_alone_still_work(self, user, room, problem):
        resp = _assign(user, room, problems=[problem.slug])
        assert resp.status_code == 201
        assert resp.json()["course"] is None

    def test_students_see_the_course_in_the_list(self, user, room, students):
        course, _ = _course()
        _assign(user, room, course=course.slug)
        rows = _client(students[0]).get(reverse("classroom-assignments", args=[room.slug])).json()
        assert rows[0]["course"]["slug"] == "kurs"


class TestReport:
    def _url(self, room: Classroom, assignment: Assignment) -> str:
        return reverse("classroom-course-report", args=[room.slug, assignment.pk])

    def test_the_teacher_sees_each_students_standing(self, user, room, students):
        quiz = Quiz.objects.create(slug="yakuniy", title="Yakuniy", is_published=True)
        question = Question.objects.create(text="S")
        right = Choice.objects.create(question=question, order=1, text="ha", is_correct=True)
        Choice.objects.create(question=question, order=2, text="yo'q")
        QuizQuestion.objects.create(quiz=quiz, question=question, order=1)
        course, lessons = _course(final_quiz=quiz)
        _assign(user, room, course=course.slug)
        assignment = Assignment.objects.get()
        first, second = students
        services.complete(first, lessons[0])
        services.complete(first, lessons[1])
        submit(first, quiz, {question.pk: right.pk})
        services.complete(second, lessons[1])

        body = _client(user).get(self._url(room, assignment)).json()
        assert body["has_final_quiz"] is True
        assert [m["title"] for m in body["modules"]] == ["Modul 0", "Modul 1"]
        assert body["modules"][0]["lessons"][0]["title"] == "Dars 0"
        rows = {row["username"]: row for row in body["students"]}
        assert rows["talaba1"]["percent"] == 100
        assert rows["talaba1"]["final_score"] == 100
        assert rows["talaba1"]["certificate"] == str(CourseCertificate.objects.get().pk)
        assert rows["talaba1"]["completed_at"] is not None
        assert (rows["talaba2"]["done"], rows["talaba2"]["total"]) == (1, 2)
        assert rows["talaba2"]["percent"] == 50
        assert rows["talaba2"]["lessons"] == [lessons[1].pk]
        assert rows["talaba2"]["final_score"] is None
        assert rows["talaba2"]["last_activity"] is not None

    def test_the_numbers_match_the_course_page(self, user, room, students):
        course, lessons = _course()
        _assign(user, room, course=course.slug)
        services.complete(students[0], lessons[0])
        report = _client(user).get(self._url(room, Assignment.objects.get())).json()
        page = _client(students[0]).get(reverse("course-detail", args=[course.slug])).json()
        row = next(r for r in report["students"] if r["username"] == "talaba1")
        assert row["percent"] == page["progress"]["percent"]

    def test_a_student_cannot_read_it(self, user, room, students):
        course, _ = _course()
        _assign(user, room, course=course.slug)
        resp = _client(students[0]).get(self._url(room, Assignment.objects.get()))
        assert resp.status_code == 403

    def test_a_problem_assignment_has_no_course_report(self, user, room, problem):
        _assign(user, room, problems=[problem.slug])
        resp = _client(user).get(self._url(room, Assignment.objects.get()))
        assert resp.status_code == 404

    def test_a_missing_assignment_progress_is_404(self, user, room):
        resp = _client(user).get(reverse("classroom-progress", args=[room.slug, 999]))
        assert resp.status_code == 404


class TestPending:
    def test_a_course_is_pending_until_completed(self, user, room, students):
        course, lessons = _course()
        _assign(user, room, course=course.slug)
        student = students[0]
        assert pending_assignments(student) == 1
        services.complete(student, lessons[0])
        assert pending_assignments(student) == 1
        services.complete(student, lessons[1])
        assert pending_assignments(student) == 0

    def test_a_priced_course_not_yet_unlocked_is_pending(self, user, room, students):
        course, _ = _course(access=Course.Access.QVANT, price_qvant=50)
        _assign(user, room, course=course.slug)
        assert pending_assignments(students[0]) == 1
