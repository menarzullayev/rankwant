"""A teacher's question bank and quiz, given to a class (ADR-0061 § 5)."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from classroom.models import Assignment, Classroom, ClassroomMember
from core.models import User
from quizzes.models import Choice, Question, Quiz, QuizAttempt, QuizQuestion
from qvant.models import QvantTransaction
from tests.quota_utils import set_free_quota


def _client(user: User) -> APIClient:
    client = APIClient()
    client.force_authenticate(user)
    return client


def _user(name: str, **extra: Any) -> User:
    return User.objects.create_user(username=name, password="x", **extra)


def _question(owner: User | None, kind: str = "single", **extra: Any) -> Question:
    question = Question.objects.create(owner=owner, kind=kind, text=f"Q {kind}", **extra)
    if kind in ("single", "multiple"):
        for order, (text, right) in enumerate(
            [("a", True), ("b", kind == "multiple"), ("c", False)], start=1
        ):
            Choice.objects.create(question=question, order=order, text=text, is_correct=right)
    return question


def _quiz(owner: User | None, questions: list[Question], **extra: Any) -> Quiz:
    quiz = Quiz.objects.create(
        owner=owner,
        slug=extra.pop("slug", "t1"),
        title="Test",
        reward_qvant=extra.pop("reward_qvant", 0),
        is_published=owner is None,
        **extra,
    )
    for order, question in enumerate(questions, start=1):
        QuizQuestion.objects.create(quiz=quiz, question=question, order=order)
    return quiz


def _given(teacher: User, student: User, quiz: Quiz) -> Classroom:
    room = Classroom.objects.create(owner=teacher, name="9-A", slug="9a")
    ClassroomMember.objects.create(classroom=room, user=student)
    Assignment.objects.create(classroom=room, title="Test", quiz=quiz)
    return room


def _submit(user: User, quiz: Quiz, answers: dict[int, Any]):
    return _client(user).post(
        reverse("quiz-submit", args=[quiz.slug]), {"answers": answers}, format="json"
    )


@pytest.mark.django_db
class TestKinds:
    def test_each_kind_grades(self, user, other_user) -> None:
        single = _question(user)
        multiple = _question(user, "multiple")
        number = _question(user, "number", answer_number=3.14, tolerance=0.01)
        text = _question(user, "text", answer_text="Toshkent\nTashkent")
        quiz = _quiz(user, [single, multiple, number, text])
        _given(user, other_user, quiz)
        right_single = single.choices.get(is_correct=True).pk
        right_multi = sorted(multiple.choices.filter(is_correct=True).values_list("pk", flat=True))
        res = _submit(
            other_user,
            quiz,
            {
                single.pk: right_single,
                multiple.pk: right_multi,
                number.pk: "3,145",
                text.pk: "  tashkent ",
            },
        )
        assert res.status_code == 201, res.content
        assert (res.json()["score"], res.json()["total"]) == (4, 4)

    def test_multiple_needs_the_exact_set(self, user, other_user) -> None:
        multiple = _question(user, "multiple")
        quiz = _quiz(user, [multiple])
        _given(user, other_user, quiz)
        first = multiple.choices.filter(is_correct=True).first()
        assert first is not None
        assert _submit(other_user, quiz, {multiple.pk: [first.pk]}).json()["score"] == 0

    def test_number_outside_tolerance(self, user, other_user) -> None:
        number = _question(user, "number", answer_number=10, tolerance=0.5)
        quiz = _quiz(user, [number])
        _given(user, other_user, quiz)
        assert _submit(other_user, quiz, {number.pk: 10.6}).json()["score"] == 0

    def test_public_single_choice_answers_still_work(self, user) -> None:
        question = _question(None)
        quiz = _quiz(None, [question], reward_qvant=10)
        right = question.choices.get(is_correct=True).pk
        res = _submit(user, quiz, {question.pk: right})
        body = res.json()
        assert body["score"] == 1
        assert body["review"][0]["chosen"] == right
        assert body["review"][0]["correct"] == right
        assert body["qvant_awarded"] == 10


@pytest.mark.django_db
class TestTeacherQuiz:
    def test_no_qvant(self, user, other_user) -> None:
        question = _question(user)
        quiz = _quiz(user, [question], reward_qvant=50)
        _given(user, other_user, quiz)
        res = _submit(other_user, quiz, {question.pk: question.choices.get(is_correct=True).pk})
        assert res.json()["qvant_awarded"] == 0
        assert not QvantTransaction.objects.filter(user=other_user).exists()

    def test_only_its_class_sees_it(self, user, other_user) -> None:
        quiz = _quiz(user, [_question(user)])
        stranger = _user("x")
        url = reverse("quiz-detail", args=[quiz.slug])
        assert _client(stranger).get(url).status_code == 404
        assert APIClient().get(url).status_code == 404
        _given(user, other_user, quiz)
        assert _client(other_user).get(url).status_code == 200
        assert _client(user).get(url).status_code == 200
        catalogue = APIClient().get(reverse("quiz-list")).json()
        rows = catalogue["results"] if isinstance(catalogue, dict) else catalogue
        assert quiz.slug not in [row["slug"] for row in rows]

    def test_one_attempt(self, user, other_user) -> None:
        question = _question(user)
        quiz = _quiz(user, [question], one_attempt=True)
        _given(user, other_user, quiz)
        assert _submit(other_user, quiz, {}).status_code == 201
        again = _submit(other_user, quiz, {})
        assert again.json()["error"]["code"] == "quiz_taken"
        state = _client(other_user).get(reverse("quiz-detail", args=[quiz.slug])).json()["state"]
        assert state["taken"] is True

    def test_answers_wait_for_the_moment(self, user, other_user) -> None:
        question = _question(user)
        quiz = _quiz(user, [question], answers_after=timezone.now() + timedelta(days=1))
        _given(user, other_user, quiz)
        body = _submit(
            other_user, quiz, {question.pk: question.choices.get(is_correct=False, order=3).pk}
        ).json()
        assert body["answers_hidden"] is True
        assert body["review"][0]["correct_value"] is None
        assert body["review"][0]["is_correct"] is False
        Quiz.objects.filter(pk=quiz.pk).update(answers_after=timezone.now() - timedelta(minutes=1))
        later = _client(other_user).get(reverse("quiz-result", args=[quiz.slug])).json()
        assert later["answers_hidden"] is False
        assert later["review"][0]["correct_value"] == question.choices.get(is_correct=True).pk


@pytest.mark.django_db
class TestTimeLimit:
    def test_questions_only_after_start(self, user, other_user) -> None:
        quiz = _quiz(user, [_question(user)], time_limit_minutes=10)
        _given(user, other_user, quiz)
        url = reverse("quiz-detail", args=[quiz.slug])
        assert _client(other_user).get(url).json()["questions"] == []
        assert _submit(other_user, quiz, {}).json()["error"]["code"] == "quiz_not_started"
        started = _client(other_user).post(reverse("quiz-start", args=[quiz.slug]))
        assert started.status_code == 201
        assert started.json()["deadline"] is not None
        assert len(_client(other_user).get(url).json()["questions"]) == 1

    def test_late_submit_counts_nothing(self, user, other_user) -> None:
        question = _question(user)
        quiz = _quiz(user, [question], time_limit_minutes=5)
        _given(user, other_user, quiz)
        _client(other_user).post(reverse("quiz-start", args=[quiz.slug]))
        QuizAttempt.objects.filter(user=other_user).update(
            started_at=timezone.now() - timedelta(minutes=10)
        )
        right = question.choices.get(is_correct=True).pk
        assert _submit(other_user, quiz, {question.pk: right}).json()["score"] == 0

    def test_in_time_counts(self, user, other_user) -> None:
        question = _question(user)
        quiz = _quiz(user, [question], time_limit_minutes=5)
        _given(user, other_user, quiz)
        _client(other_user).post(reverse("quiz-start", args=[quiz.slug]))
        right = question.choices.get(is_correct=True).pk
        assert _submit(other_user, quiz, {question.pk: right}).json()["score"] == 1


@pytest.mark.django_db
class TestAuthoring:
    def _q(self, client: APIClient, **body: Any):
        return client.post(reverse("mine-question-list"), body, format="json")

    def test_question_kinds_validate(self, user) -> None:
        client = _client(user)
        ok = self._q(
            client,
            kind="multiple",
            text="T",
            choices=[
                {"order": 1, "text": "a", "is_correct": True},
                {"order": 2, "text": "b", "is_correct": True},
            ],
        )
        assert ok.status_code == 201, ok.content
        assert self._q(client, kind="number", text="T").status_code == 400
        assert self._q(client, kind="number", text="T", answer_number=2).status_code == 201
        assert self._q(client, kind="text", text="T", answer_text=" ").status_code == 400
        assert (
            self._q(
                client,
                kind="single",
                text="T",
                choices=[
                    {"order": 1, "text": "a", "is_correct": True},
                    {"order": 2, "text": "b", "is_correct": True},
                ],
            ).status_code
            == 400
        )

    def test_bank_is_private(self, user, other_user) -> None:
        mine = _question(user)
        rows = _client(other_user).get(reverse("mine-question-list")).json()["results"]
        assert rows == []
        res = _client(other_user).patch(
            reverse("mine-question-detail", args=[mine.pk]), {"text": "x"}, format="json"
        )
        assert res.status_code == 404

    def test_quiz_takes_only_own_questions(self, user, other_user) -> None:
        theirs = _question(other_user)
        res = _client(user).post(
            reverse("mine-quiz-list"),
            {"slug": "q1", "title": "Q", "question_ids": [theirs.pk]},
            format="json",
        )
        assert res.status_code == 400

    def test_quiz_quota(self, user) -> None:
        set_free_quota(quizzes=1)
        client = _client(user)
        first = client.post(reverse("mine-quiz-list"), {"slug": "q1", "title": "Q"}, format="json")
        assert first.status_code == 201
        assert Quiz.objects.get(slug="q1").reward_qvant == 0
        second = client.post(reverse("mine-quiz-list"), {"slug": "q2", "title": "Q"}, format="json")
        assert second.json()["error"]["code"] == "quota_exceeded"

    def test_reserved_slug(self, user) -> None:
        res = _client(user).post(
            reverse("mine-quiz-list"), {"slug": "mine", "title": "Q"}, format="json"
        )
        assert res.status_code == 400

    def test_questions_fixed_after_students_answered(self, user, other_user) -> None:
        question = _question(user)
        quiz = _quiz(user, [question])
        _given(user, other_user, quiz)
        _submit(other_user, quiz, {})
        res = _client(user).patch(
            reverse("mine-quiz-detail", args=[quiz.slug]), {"question_ids": []}, format="json"
        )
        assert res.status_code == 400
        res = _client(user).patch(
            reverse("mine-question-detail", args=[question.pk]),
            {
                "kind": "single",
                "choices": [
                    {"order": 1, "text": "z", "is_correct": True},
                    {"order": 2, "text": "y"},
                ],
            },
            format="json",
        )
        assert res.status_code == 400

    def test_given_quiz_is_not_deleted(self, user, other_user) -> None:
        quiz = _quiz(user, [_question(user)])
        _given(user, other_user, quiz)
        res = _client(user).delete(reverse("mine-quiz-detail", args=[quiz.slug]))
        assert res.json()["error"]["code"] == "quiz_in_use"

    def test_folders(self, user) -> None:
        client = _client(user)
        folder = client.post(reverse("question-folder-list"), {"name": "Graflar"}).json()
        made = self._q(client, kind="number", text="T", answer_number=1, folder=folder["id"])
        assert made.status_code == 201
        rows = client.get(reverse("mine-question-list"), {"folder": folder["id"]}).json()
        assert len(rows["results"]) == 1


@pytest.mark.django_db
class TestClassReport:
    def test_assign_and_report(self, user, other_user) -> None:
        question = _question(user)
        other = _question(user, "number", answer_number=1)
        quiz = _quiz(user, [question, other])
        room = Classroom.objects.create(owner=user, name="9-A", slug="9a")
        ClassroomMember.objects.create(classroom=room, user=other_user)
        res = _client(user).post(
            reverse("classroom-assignments", args=[room.slug]),
            {"title": "Test", "quiz": quiz.slug},
            format="json",
        )
        assert res.status_code == 201, res.content
        assert res.json()["quiz"]["slug"] == quiz.slug
        _submit(other_user, quiz, {question.pk: question.choices.get(is_correct=True).pk})
        assignment = Assignment.objects.get()
        url = reverse("classroom-quiz-report", args=[room.slug, assignment.pk])
        body = _client(user).get(url).json()
        assert body["students"][0]["score"] == 1
        wrong = {row["id"]: row["wrong"] for row in body["questions"]}
        assert wrong == {question.pk: 0, other.pk: 1}
        assert _client(other_user).get(url).status_code == 403

    def test_another_teachers_quiz_is_refused(self, user, other_user) -> None:
        theirs = _quiz(other_user, [_question(other_user)])
        room = Classroom.objects.create(owner=user, name="9-A", slug="9a")
        res = _client(user).post(
            reverse("classroom-assignments", args=[room.slug]),
            {"title": "Test", "quiz": theirs.slug},
            format="json",
        )
        assert res.json()["error"]["code"] == "classroom_quiz_unavailable"


@pytest.mark.django_db
class TestStaffBankStaysApart:
    def test_staff_bank_hides_teacher_questions(self, user) -> None:
        staff = _user("ops", is_staff=True)
        _question(user)
        public = _question(None)
        rows = _client(staff).get(reverse("staff-question-list")).json()
        ids = [row["id"] for row in (rows["results"] if isinstance(rows, dict) else rows)]
        assert ids == [public.pk]

    def test_staff_quiz_cannot_take_a_teacher_question(self, user) -> None:
        staff = _user("ops", is_staff=True)
        theirs = _question(user)
        res = _client(staff).post(
            reverse("staff-quiz-list"),
            {"slug": "s1", "title": "S", "questions": [theirs.pk]},
            format="json",
        )
        assert res.status_code == 400

    def test_answered_number_cannot_change(self, user, other_user) -> None:
        number = _question(user, "number", answer_number=5)
        quiz = _quiz(user, [number])
        _given(user, other_user, quiz)
        _submit(other_user, quiz, {number.pk: 5})
        res = _client(user).patch(
            reverse("mine-question-detail", args=[number.pk]), {"answer_number": 6}, format="json"
        )
        assert res.status_code == 400
        ok = _client(user).patch(
            reverse("mine-question-detail", args=[number.pk]), {"text": "New text"}, format="json"
        )
        assert ok.status_code == 200
