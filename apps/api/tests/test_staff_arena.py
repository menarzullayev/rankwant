"""Staff API — Arena raundlari (`staff/arena/`)."""

from __future__ import annotations

from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from arena.models import ArenaAnswer, ArenaParticipation, ArenaQuestion, ArenaRound
from core.models import User
from quizzes.models import Choice, Question
from qvant import ledger


def _question(text: str) -> Question:
    q = Question.objects.create(text=text)
    Choice.objects.create(question=q, order=1, text="ha", is_correct=True)
    Choice.objects.create(question=q, order=2, text="yo'q")
    return q


@pytest.fixture
def staff_client(db) -> APIClient:
    staff = User.objects.create_user("staff1", password="x", is_staff=True)
    client = APIClient()
    client.force_authenticate(staff)
    return client


@pytest.fixture
def arena(db) -> ArenaRound:
    arena = ArenaRound.objects.create(
        slug="demo",
        title="Demo",
        start_at=timezone.now() + timedelta(hours=1),
        seconds_per_question=30,
        reward_qvant=15,
    )
    for i in range(2):
        ArenaQuestion.objects.create(round=arena, question=_question(f"S{i}"), order=i + 1)
    return arena


@pytest.mark.django_db
class TestStaffArenaAccess:
    def test_anonim_kirolmaydi(self, arena) -> None:
        res = APIClient().get(reverse("staff-arena-list"))
        assert res.status_code in (401, 403)

    def test_oddiy_foydalanuvchi_403(self, user, arena) -> None:
        client = APIClient()
        client.force_authenticate(user)
        assert client.get(reverse("staff-arena-list")).status_code == 403
        assert client.post(reverse("staff-arena-reset", args=[arena.slug])).status_code == 403

    def test_ommaviy_api_ozgarmagan(self, arena) -> None:
        """Ommaviy ro'yxatda staff maydonlari (is_public, questions) chiqmasin."""
        item = APIClient().get(reverse("arena-list")).json()["results"][0]
        assert "is_public" not in item
        assert "questions" not in item


@pytest.mark.django_db
class TestStaffArenaCrud:
    def test_royxat_va_qidiruv(self, staff_client, arena) -> None:
        body = staff_client.get(reverse("staff-arena-list"), {"search": "demo"}).json()
        assert body["count"] == 1
        item = body["results"][0]
        assert item["questions"] == list(arena.items.values_list("question_id", flat=True))
        assert item["question_count"] == 2
        assert item["participant_count"] == 0
        assert staff_client.get(reverse("staff-arena-list"), {"search": "zzz"}).json()["count"] == 0

    def test_yaratish_savollar_bilan(self, staff_client) -> None:
        q1, q2 = _question("a"), _question("b")
        res = staff_client.post(
            reverse("staff-arena-list"),
            {
                "slug": "yangi",
                "title": "Yangi",
                "start_at": (timezone.now() + timedelta(days=1)).isoformat(),
                "seconds_per_question": 45,
                "reward_qvant": 20,
                "is_public": False,
                "questions": [q2.pk, q1.pk],
            },
            format="json",
        )
        assert res.status_code == 201, res.json()
        assert res.json()["questions"] == [q2.pk, q1.pk]
        assert res.json()["question_count"] == 2
        arena = ArenaRound.objects.get(slug="yangi")
        assert not arena.is_public
        assert list(arena.items.values_list("question_id", "order")) == [(q2.pk, 1), (q1.pk, 2)]

    def test_savollar_almashtiriladi_va_tartiblanadi(self, staff_client, arena) -> None:
        old = list(arena.items.values_list("question_id", flat=True))
        q3 = _question("c")
        res = staff_client.patch(
            reverse("staff-arena-detail", args=[arena.slug]),
            {"questions": [q3.pk, old[0]]},
            format="json",
        )
        assert res.status_code == 200, res.json()
        assert res.json()["questions"] == [q3.pk, old[0]]
        assert list(arena.items.values_list("question_id", "order")) == [(q3.pk, 1), (old[0], 2)]

    def test_tahrir_savollarsiz_royxatni_saqlaydi(self, staff_client, arena) -> None:
        res = staff_client.patch(
            reverse("staff-arena-detail", args=[arena.slug]), {"title": "Boshqa"}, format="json"
        )
        assert res.status_code == 200
        assert res.json()["title"] == "Boshqa"
        assert arena.items.count() == 2

    def test_notogri_savol_id(self, staff_client, arena) -> None:
        res = staff_client.patch(
            reverse("staff-arena-detail", args=[arena.slug]),
            {"questions": [999_999]},
            format="json",
        )
        assert res.status_code == 400
        assert "questions" in res.json()["error"]["details"]

    def test_takror_savol_id(self, staff_client, arena) -> None:
        qid = arena.items.first().question_id
        res = staff_client.patch(
            reverse("staff-arena-detail", args=[arena.slug]),
            {"questions": [qid, qid]},
            format="json",
        )
        assert res.status_code == 400

    def test_ochirish(self, staff_client, arena) -> None:
        res = staff_client.delete(reverse("staff-arena-detail", args=[arena.slug]))
        assert res.status_code == 204
        assert not ArenaRound.objects.filter(slug=arena.slug).exists()


@pytest.mark.django_db
class TestStaffArenaActions:
    def test_reschedule(self, staff_client, arena) -> None:
        arena.rewards_applied_at = timezone.now()
        arena.save(update_fields=["rewards_applied_at"])
        new_start = timezone.now() + timedelta(days=2)
        res = staff_client.post(
            reverse("staff-arena-reschedule", args=[arena.slug]),
            {"start_at": new_start.isoformat()},
            format="json",
        )
        assert res.status_code == 200, res.json()
        arena.refresh_from_db()
        assert arena.start_at == new_start
        assert arena.rewards_applied_at is None
        assert res.json()["rewards_applied_at"] is None

    def test_reschedule_start_at_shart(self, staff_client, arena) -> None:
        res = staff_client.post(
            reverse("staff-arena-reschedule", args=[arena.slug]), {}, format="json"
        )
        assert res.status_code == 400

    def test_reset(self, staff_client, arena, user) -> None:
        participation = ArenaParticipation.objects.create(round=arena, user=user, correct_count=1)
        q = arena.items.first().question
        ArenaAnswer.objects.create(
            participation=participation,
            question=q,
            choice=q.choices.first(),
            is_correct=True,
            elapsed_ms=10,
            points=900,
        )
        arena.rewards_applied_at = timezone.now()
        arena.save(update_fields=["rewards_applied_at"])

        res = staff_client.post(reverse("staff-arena-reset", args=[arena.slug]))
        assert res.status_code == 200
        assert res.json()["participant_count"] == 0
        assert not ArenaParticipation.objects.filter(round=arena).exists()
        assert not ArenaAnswer.objects.filter(participation__round=arena).exists()
        arena.refresh_from_db()
        assert arena.rewards_applied_at is None

    def test_finalize_tugamagan_raund(self, staff_client, arena) -> None:
        res = staff_client.post(reverse("staff-arena-finalize", args=[arena.slug]))
        assert res.status_code == 400
        assert res.json()["error"]["code"] == "not_finished"

    def test_finalize(self, staff_client, arena, user, other_user) -> None:
        arena.start_at = timezone.now() - timedelta(hours=1)
        arena.save(update_fields=["start_at"])
        ArenaParticipation.objects.create(round=arena, user=user, correct_count=1, score=500)
        ArenaParticipation.objects.create(round=arena, user=other_user, correct_count=0)

        res = staff_client.post(reverse("staff-arena-finalize", args=[arena.slug]))
        assert res.status_code == 200, res.json()
        assert res.json()["awarded"] == 1
        arena.refresh_from_db()
        assert arena.rewards_applied_at is not None
        assert ledger.get_wallet(user).balance == 15
        assert ledger.get_wallet(other_user).balance == 0

        again = staff_client.post(reverse("staff-arena-finalize", args=[arena.slug]))
        assert again.status_code == 400
        assert again.json()["error"]["code"] == "already_finalized"
