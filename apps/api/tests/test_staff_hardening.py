"""Adversarial review'dan chiqqan holatlar — regressiya qopqog'i.

Bir qismi HAQIQIY nuqson edi (PROTECT → 500, arena qayta to'lov, savol
variantlarini almashtirish arena javoblarini yo'q qilishi); qolgani esa
da'vo bo'lib, bu yerda ular ham qotirib qo'yiladi.
"""

from __future__ import annotations

from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from arena.models import ArenaAnswer, ArenaParticipation, ArenaQuestion, ArenaRound
from contests.models import ContestProblem
from core.models import User
from hackathons.models import Hackathon
from quizzes.models import Choice, Question


@pytest.fixture
def staff(db) -> User:
    return User.objects.create_user("staff_h", password="x", is_staff=True)


@pytest.fixture
def client(staff) -> APIClient:
    c = APIClient()
    c.force_authenticate(user=staff)
    return c


def _question(text: str = "Savol?") -> Question:
    q = Question.objects.create(text=text)
    Choice.objects.create(question=q, order=1, text="ha", is_correct=True)
    Choice.objects.create(question=q, order=2, text="yo'q")
    return q


@pytest.mark.django_db
class TestProtectedDelete:
    def test_musobaqada_ishlatilgan_masala_toza_409(self, client, contest, problem) -> None:
        """PROTECT ishlov berilmasa admin UI da 500 chiqardi."""
        ContestProblem.objects.get_or_create(
            contest=contest, problem=problem, defaults={"index_letter": "A"}
        )
        r = client.delete(reverse("staff-problem-detail", args=[problem.slug]))
        assert r.status_code == 409
        assert r.json()["error"]["code"] == "protected"
        assert r.json()["error"]["details"]["used_by"]

    def test_bogliqsiz_masala_ochiriladi(self, client, problem) -> None:
        assert (
            client.delete(reverse("staff-problem-detail", args=[problem.slug])).status_code == 204
        )


@pytest.mark.django_db
class TestQuestionChoicesGuard:
    def _arena_with_answer(self, question: Question, user: User) -> ArenaRound:
        arena = ArenaRound.objects.create(
            slug="a-h", title="A", start_at=timezone.now() - timedelta(seconds=5)
        )
        ArenaQuestion.objects.create(round=arena, question=question, order=1)
        part = ArenaParticipation.objects.create(round=arena, user=user, score=800, correct_count=1)
        ArenaAnswer.objects.create(
            participation=part,
            question=question,
            choice=question.choices.get(is_correct=True),
            is_correct=True,
            elapsed_ms=1000,
            points=800,
        )
        return arena

    def test_javob_berilgan_savol_variantlari_qulflangan(self, client, user) -> None:
        q = _question()
        self._arena_with_answer(q, user)
        r = client.patch(
            reverse("staff-question-detail", args=[q.pk]),
            {
                "choices": [
                    {"order": 1, "text": "boshqa", "is_correct": True},
                    {"order": 2, "text": "yana", "is_correct": False},
                ]
            },
            format="json",
        )
        assert r.status_code == 400
        # The API answers in English (`tools/check_api_english.py`); the source
        # of this string is `ANSWERED_MSG` in `quizzes/staff_serializers.py`.
        assert "arena answers" in str(r.json()).lower()
        # Jadval buzilmadi: javob ham, ball ham joyida
        assert ArenaAnswer.objects.count() == 1
        assert ArenaParticipation.objects.get().score == 800

    def test_javobsiz_savol_tahrirlanadi(self, client) -> None:
        q = _question()
        r = client.patch(
            reverse("staff-question-detail", args=[q.pk]),
            {
                "choices": [
                    {"order": 1, "text": "yangi", "is_correct": True},
                    {"order": 2, "text": "eski", "is_correct": False},
                ]
            },
            format="json",
        )
        assert r.status_code == 200
        assert q.choices.get(is_correct=True).text == "yangi"


@pytest.mark.django_db
class TestArenaReschedule:
    def _paid_round(self, user: User) -> ArenaRound:
        arena = ArenaRound.objects.create(
            slug="paid",
            title="P",
            start_at=timezone.now() - timedelta(hours=1),
            rewards_applied_at=timezone.now(),
        )
        ArenaParticipation.objects.create(round=arena, user=user, score=100, correct_count=1)
        return arena

    def test_mukofot_berilgan_raund_tozalashsiz_qayta_rejalanmaydi(self, client, user) -> None:
        """Aks holda `finalize` o'sha odamlarga ikkinchi marta Qvant berardi."""
        arena = self._paid_round(user)
        when = (timezone.now() + timedelta(hours=1)).isoformat()
        r = client.post(
            reverse("staff-arena-reschedule", args=[arena.slug]), {"start_at": when}, format="json"
        )
        assert r.status_code == 400
        assert r.json()["error"]["code"] == "already_paid"
        arena.refresh_from_db()
        assert arena.rewards_applied_at is not None

    def test_reset_bilan_qayta_rejalanadi(self, client, user) -> None:
        arena = self._paid_round(user)
        when = (timezone.now() + timedelta(hours=1)).isoformat()
        r = client.post(
            reverse("staff-arena-reschedule", args=[arena.slug]),
            {"start_at": when, "reset": True},
            format="json",
        )
        assert r.status_code == 200
        arena.refresh_from_db()
        assert arena.rewards_applied_at is None
        assert arena.participants.count() == 0

    def test_tolanmagan_raund_erkin_rejalanadi(self, client, user) -> None:
        arena = ArenaRound.objects.create(
            slug="free", title="F", start_at=timezone.now() + timedelta(hours=2)
        )
        ArenaParticipation.objects.create(round=arena, user=user)
        when = (timezone.now() + timedelta(hours=3)).isoformat()
        r = client.post(
            reverse("staff-arena-reschedule", args=[arena.slug]), {"start_at": when}, format="json"
        )
        assert r.status_code == 200


@pytest.mark.django_db
class TestValidationBounds:
    def test_qvant_miqdori_chegaralangan(self, client, user) -> None:
        """int32 dan oshgan qiymat Postgres'da 500 berardi."""
        r = client.post(
            reverse("staff-user-qvant", args=[user.username]),
            {"amount": 3_000_000_000, "note": "x"},
            format="json",
        )
        assert r.status_code == 400

    def test_hakaton_xronologiyasi(self, client) -> None:
        now = timezone.now()
        r = client.post(
            reverse("staff-hackathon-list"),
            {
                "slug": "teskari",
                "title": "T",
                "description": "d",
                "start_at": (now + timedelta(days=5)).isoformat(),
                "submission_deadline": now.isoformat(),
                "end_at": (now + timedelta(days=9)).isoformat(),
            },
            format="json",
        )
        assert r.status_code == 400
        assert not Hackathon.objects.filter(slug="teskari").exists()

    def test_nuqtali_username_ochiladi(self, client, db) -> None:
        """Router shabloni nuqtani kesardi — bunday hisob admin'da 404 edi."""
        User.objects.create_user("aziz.karimov", password="x")
        assert client.get(reverse("staff-user-detail", args=["aziz.karimov"])).status_code == 200


@pytest.mark.django_db
class TestNestedRowsReturn400:
    """Review «to'liq bo'lmagan qator KeyError → 500» deb da'vo qilgan edi.

    Bolalar serializer bilan tekshirilgani uchun aslida 400 keladi —
    shu holat qotirib qo'yiladi.
    """

    def test_savol_varianti_tartibsiz(self, client) -> None:
        q = _question()
        r = client.patch(
            reverse("staff-question-detail", args=[q.pk]),
            {"choices": [{"text": "tartibsiz", "is_correct": True}, {"order": 2, "text": "b"}]},
            format="json",
        )
        assert r.status_code == 400

    def test_roadmap_qadami_tartibsiz(self, client) -> None:
        r = client.post(
            reverse("staff-roadmap-list"),
            {
                "slug": "r-h",
                "title": "R",
                "description": "",
                "is_published": False,
                "order": 1,
                "steps": [{"title": "qadam", "problem": None, "article": None}],
            },
            format="json",
        )
        assert r.status_code == 400

    def test_chempionat_bosqichi_tartibsiz(self, client, contest) -> None:
        now = timezone.now()
        r = client.post(
            reverse("staff-tournament-list"),
            {
                "slug": "t-h",
                "title": "T",
                "description": "",
                "start_at": now.isoformat(),
                "end_at": (now + timedelta(days=1)).isoformat(),
                "stages": [{"title": "bosqich", "contest": contest.slug}],
            },
            format="json",
        )
        assert r.status_code == 400
