"""Savol banki — staff CRUD (`staff/questions/`)."""

from __future__ import annotations

from typing import Any

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from core.models import User
from problems.models import Topic
from quizzes.models import Choice, Question

LIST = reverse("staff-question-list")


def detail(pk: int) -> str:
    return reverse("staff-question-detail", args=[pk])


def payload(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "text": "2+2 nechaga teng?",
        "explanation": "Arifmetika",
        "difficulty": 900,
        "topics": [],
        "is_active": True,
        "choices": [
            {"order": 1, "text": "3", "is_correct": False},
            {"order": 2, "text": "4", "is_correct": True},
            {"order": 3, "text": "5", "is_correct": False},
        ],
    }
    base.update(overrides)
    return base


@pytest.fixture
def staff_client(db) -> APIClient:
    staff = User.objects.create_user("staff1", password="x", is_staff=True)
    client = APIClient()
    client.force_authenticate(staff)
    return client


@pytest.fixture
def question(db) -> Question:
    q = Question.objects.create(text="Eski savol", difficulty=800)
    Choice.objects.create(question=q, order=1, text="a", is_correct=True)
    Choice.objects.create(question=q, order=2, text="b")
    return q


@pytest.mark.django_db
class TestAccess:
    def test_anonim(self, question) -> None:
        client = APIClient()
        assert client.get(LIST).status_code in (401, 403)
        assert client.post(LIST, payload(), format="json").status_code in (401, 403)
        assert client.delete(detail(question.pk)).status_code in (401, 403)

    def test_oddiy_foydalanuvchi(self, user, question) -> None:
        client = APIClient()
        client.force_authenticate(user)
        assert client.get(LIST).status_code == 403
        assert client.post(LIST, payload(), format="json").status_code == 403
        assert client.patch(detail(question.pk), {"text": "x"}, format="json").status_code == 403
        assert client.delete(detail(question.pk)).status_code == 403


@pytest.mark.django_db
class TestCrud:
    def test_yaratish(self, staff_client) -> None:
        Topic.objects.create(slug="math", name_uz="Matematika")
        res = staff_client.post(LIST, payload(topics=["math"]), format="json")
        assert res.status_code == 201, res.json()
        body = res.json()
        assert body["topics"] == ["math"]
        assert [c["order"] for c in body["choices"]] == [1, 2, 3]
        assert [c["is_correct"] for c in body["choices"]] == [False, True, False]
        q = Question.objects.get(pk=body["id"])
        assert q.correct_choice_id == q.choices.get(order=2).pk

    def test_royxat_va_qidiruv(self, staff_client, question) -> None:
        Question.objects.create(text="Boshqa mavzu")
        body = staff_client.get(LIST).json()
        assert body["count"] == 2
        # Staff serializer to'g'ri javobni ko'rsatadi
        assert any(c["is_correct"] for c in body["results"][1]["choices"])
        found = staff_client.get(LIST, {"search": "Eski"}).json()
        assert found["count"] == 1
        assert found["results"][0]["id"] == question.pk

    def test_olish(self, staff_client, question) -> None:
        body = staff_client.get(detail(question.pk)).json()
        assert body["text"] == "Eski savol"
        assert len(body["choices"]) == 2

    def test_yangilash_variantlarni_almashtiradi(self, staff_client, question) -> None:
        old_ids = set(question.choices.values_list("pk", flat=True))
        res = staff_client.patch(
            detail(question.pk),
            {
                "text": "Yangilangan",
                "choices": [
                    {"order": 1, "text": "x", "is_correct": False},
                    {"order": 2, "text": "y", "is_correct": False},
                    {"order": 3, "text": "z", "is_correct": True},
                ],
            },
            format="json",
        )
        assert res.status_code == 200, res.json()
        question.refresh_from_db()
        assert question.text == "Yangilangan"
        assert question.choices.count() == 3
        assert not old_ids & set(question.choices.values_list("pk", flat=True))
        assert question.choices.get(is_correct=True).text == "z"

    def test_patch_variantlarsiz_eskilarini_saqlaydi(self, staff_client, question) -> None:
        res = staff_client.patch(detail(question.pk), {"difficulty": 1500}, format="json")
        assert res.status_code == 200
        question.refresh_from_db()
        assert question.difficulty == 1500
        assert question.choices.count() == 2

    def test_put(self, staff_client, question) -> None:
        res = staff_client.put(detail(question.pk), payload(text="PUT"), format="json")
        assert res.status_code == 200, res.json()
        assert question.choices.count() == 3

    def test_ochirish(self, staff_client, question) -> None:
        assert staff_client.delete(detail(question.pk)).status_code == 204
        assert not Question.objects.filter(pk=question.pk).exists()
        assert not Choice.objects.filter(question_id=question.pk).exists()


@pytest.mark.django_db
class TestValidation:
    def test_kam_variant(self, staff_client) -> None:
        res = staff_client.post(
            LIST, payload(choices=[{"order": 1, "text": "a", "is_correct": True}]), format="json"
        )
        assert res.status_code == 400
        assert "choices" in res.json()["error"]["details"]

    def test_togri_javob_yoq(self, staff_client) -> None:
        choices = [
            {"order": 1, "text": "a", "is_correct": False},
            {"order": 2, "text": "b", "is_correct": False},
        ]
        res = staff_client.post(LIST, payload(choices=choices), format="json")
        assert res.status_code == 400
        assert "choices" in res.json()["error"]["details"]

    def test_ikki_togri_javob(self, staff_client) -> None:
        choices = [
            {"order": 1, "text": "a", "is_correct": True},
            {"order": 2, "text": "b", "is_correct": True},
        ]
        res = staff_client.post(LIST, payload(choices=choices), format="json")
        assert res.status_code == 400

    def test_takror_tartib(self, staff_client) -> None:
        choices = [
            {"order": 1, "text": "a", "is_correct": True},
            {"order": 1, "text": "b", "is_correct": False},
        ]
        res = staff_client.post(LIST, payload(choices=choices), format="json")
        assert res.status_code == 400
        assert Question.objects.count() == 0

    def test_notogri_mavzu(self, staff_client) -> None:
        res = staff_client.post(LIST, payload(topics=["yoq"]), format="json")
        assert res.status_code == 400
        assert "topics" in res.json()["error"]["details"]

    def test_xato_yaratishda_savol_qolmaydi(self, staff_client) -> None:
        """Variant validatsiyasi savol yozilishidan OLDIN — yarim yozuv yo'q."""
        staff_client.post(LIST, payload(choices=[]), format="json")
        assert Question.objects.count() == 0
