"""Staff API — testlar (`staff/quizzes/`) va savol qidiruvi (`staff/questions/`)."""

from __future__ import annotations

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from core.models import User
from quizzes.models import Question, Quiz, QuizQuestion


@pytest.fixture
def staff(db) -> User:
    return User.objects.create_user("staff1", password="x", is_staff=True)


@pytest.fixture
def staff_client(staff) -> APIClient:
    c = APIClient()
    c.force_authenticate(user=staff)
    return c


@pytest.fixture
def questions(db) -> list[Question]:
    return [Question.objects.create(text=f"Savol {i}") for i in range(3)]


@pytest.fixture
def quiz(db, questions) -> Quiz:
    q = Quiz.objects.create(slug="asoslar", title="Asoslar", reward_qvant=10)
    QuizQuestion.objects.create(quiz=q, question=questions[0], order=1)
    QuizQuestion.objects.create(quiz=q, question=questions[1], order=2)
    return q


def _orders(quiz: Quiz) -> list[tuple[int, int]]:
    return list(quiz.items.order_by("order").values_list("question_id", "order"))


@pytest.mark.django_db
class TestStaffQuizAccess:
    def test_anonim_kirolmaydi(self, quiz) -> None:
        r = APIClient().get(reverse("staff-quiz-list"))
        assert r.status_code in (401, 403)

    def test_oddiy_foydalanuvchi_403(self, user, quiz) -> None:
        c = APIClient()
        c.force_authenticate(user=user)
        assert c.get(reverse("staff-quiz-list")).status_code == 403
        assert c.get(reverse("staff-quiz-detail", args=[quiz.slug])).status_code == 403
        r = c.post(reverse("staff-quiz-list"), {"slug": "x", "title": "X"}, format="json")
        assert r.status_code == 403
        assert c.get(reverse("staff-question-list")).status_code == 403

    def test_ommaviy_api_nashr_qilinmaganini_kormaydi(self, quiz) -> None:
        """Staff yuzasi ommaviy o'qishni o'zgartirmaydi."""
        assert APIClient().get(reverse("quiz-list")).json()["count"] == 0


@pytest.mark.django_db
class TestStaffQuizCrud:
    def test_royxat_va_tartib(self, staff_client, quiz, questions) -> None:
        body = staff_client.get(reverse("staff-quiz-list")).json()
        assert body["count"] == 1
        item = body["results"][0]
        assert item["slug"] == "asoslar"
        assert item["questions"] == [questions[0].pk, questions[1].pk]
        assert item["is_published"] is False

    def test_qidiruv(self, staff_client, quiz) -> None:
        Quiz.objects.create(slug="graflar", title="Graflar")
        body = staff_client.get(reverse("staff-quiz-list"), {"search": "graf"}).json()
        assert [q["slug"] for q in body["results"]] == ["graflar"]

    def test_yaratish_savollar_bilan(self, staff_client, questions) -> None:
        r = staff_client.post(
            reverse("staff-quiz-list"),
            {
                "slug": "yangi",
                "title": "Yangi",
                "description": "tavsif",
                "reward_qvant": 25,
                "is_published": True,
                "questions": [questions[2].pk, questions[0].pk],
            },
            format="json",
        )
        assert r.status_code == 201, r.json()
        assert r.json()["questions"] == [questions[2].pk, questions[0].pk]
        quiz = Quiz.objects.get(slug="yangi")
        assert quiz.reward_qvant == 25 and quiz.is_published
        assert _orders(quiz) == [(questions[2].pk, 1), (questions[0].pk, 2)]

    def test_yaratish_savolsiz(self, staff_client) -> None:
        r = staff_client.post(
            reverse("staff-quiz-list"), {"slug": "bosh", "title": "Bo'sh"}, format="json"
        )
        assert r.status_code == 201
        assert r.json()["questions"] == []

    def test_olish(self, staff_client, quiz, questions) -> None:
        body = staff_client.get(reverse("staff-quiz-detail", args=[quiz.slug])).json()
        assert body["title"] == "Asoslar"
        assert body["questions"] == [questions[0].pk, questions[1].pk]

    def test_tahrirlash_savollarni_almashtiradi(self, staff_client, quiz, questions) -> None:
        """Yangi ro'yxat eski qatorlarni to'liq almashtiradi, order = pozitsiya + 1."""
        new = [questions[1].pk, questions[2].pk, questions[0].pk]
        r = staff_client.patch(
            reverse("staff-quiz-detail", args=[quiz.slug]),
            {"title": "Asoslar 2", "questions": new},
            format="json",
        )
        assert r.status_code == 200, r.json()
        assert r.json()["questions"] == new
        assert r.json()["title"] == "Asoslar 2"
        assert _orders(quiz) == [(new[0], 1), (new[1], 2), (new[2], 3)]

    def test_savollarsiz_patch_tartibni_saqlaydi(self, staff_client, quiz, questions) -> None:
        r = staff_client.patch(
            reverse("staff-quiz-detail", args=[quiz.slug]), {"is_published": True}, format="json"
        )
        assert r.status_code == 200
        assert r.json()["questions"] == [questions[0].pk, questions[1].pk]
        assert Quiz.objects.get(pk=quiz.pk).is_published

    def test_bosh_royxat_savollarni_tozalaydi(self, staff_client, quiz) -> None:
        r = staff_client.patch(
            reverse("staff-quiz-detail", args=[quiz.slug]), {"questions": []}, format="json"
        )
        assert r.status_code == 200
        assert r.json()["questions"] == []
        assert quiz.items.count() == 0

    def test_mavjud_bolmagan_savol_400(self, staff_client, quiz, questions) -> None:
        r = staff_client.patch(
            reverse("staff-quiz-detail", args=[quiz.slug]),
            {"questions": [questions[0].pk, 999_999]},
            format="json",
        )
        assert r.status_code == 400
        assert "questions" in r.json()["error"]["details"]
        # noto'g'ri so'rov eski tartibni buzmaydi
        assert _orders(quiz) == [(questions[0].pk, 1), (questions[1].pk, 2)]

    def test_takror_savol_400(self, staff_client, quiz, questions) -> None:
        r = staff_client.patch(
            reverse("staff-quiz-detail", args=[quiz.slug]),
            {"questions": [questions[0].pk, questions[0].pk]},
            format="json",
        )
        assert r.status_code == 400
        assert "questions" in r.json()["error"]["details"]

    def test_slug_takror_400(self, staff_client, quiz) -> None:
        r = staff_client.post(
            reverse("staff-quiz-list"), {"slug": quiz.slug, "title": "T"}, format="json"
        )
        assert r.status_code == 400
        assert "slug" in r.json()["error"]["details"]

    def test_ochirish(self, staff_client, quiz) -> None:
        r = staff_client.delete(reverse("staff-quiz-detail", args=[quiz.slug]))
        assert r.status_code == 204
        assert not Quiz.objects.filter(pk=quiz.pk).exists()
        assert QuizQuestion.objects.filter(quiz_id=quiz.pk).count() == 0
