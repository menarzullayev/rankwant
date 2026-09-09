"""Arena — jonli raund. Vaqt `start_at` orqali boshqariladi (freezegun'siz)."""

from __future__ import annotations

from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from arena.models import ArenaParticipation, ArenaQuestion, ArenaRound
from arena.services import ArenaError, answer, finalize, join, points_for
from quizzes.models import Choice, Question
from qvant import ledger


def _round(start_offset_s: int, seconds: int = 60, n: int = 2) -> ArenaRound:
    arena = ArenaRound.objects.create(
        slug=f"r{start_offset_s}",
        title="Sinov",
        start_at=timezone.now() + timedelta(seconds=start_offset_s),
        seconds_per_question=seconds,
        reward_qvant=15,
    )
    for i in range(n):
        q = Question.objects.create(text=f"Savol {i}")
        Choice.objects.create(question=q, order=1, text="ha", is_correct=True)
        Choice.objects.create(question=q, order=2, text="yo'q")
        ArenaQuestion.objects.create(round=arena, question=q, order=i + 1)
    return arena


def _correct(arena: ArenaRound, index: int) -> tuple[int, int]:
    q = arena.items.get(order=index + 1).question
    return q.pk, q.choices.get(is_correct=True).pk


@pytest.fixture
def running(db) -> ArenaRound:
    return _round(start_offset_s=-5)  # 5 s oldin boshlangan → 0-savol ochiq


@pytest.mark.django_db
class TestArenaMechanics:
    def test_joriy_savol_server_vaqtidan(self, running) -> None:
        assert running.current_index == 0
        later = _round(start_offset_s=-65)  # 65 s → 1-savol
        assert later.current_index == 1
        assert _round(start_offset_s=30).current_index is None  # hali boshlanmagan
        assert _round(start_offset_s=-500).current_index is None  # tugagan

    def test_togri_javob_ball_tezlikka_bogliq(self) -> None:
        assert points_for(0, 60) == 1000
        assert points_for(30_000, 60) == 500
        assert points_for(60_000, 60) == 100  # oxirgi soniyada ham nol emas

    def test_ball_chegaradan_chiqmaydi(self) -> None:
        """Manfiy `elapsed_ms` MAX dan oshiq ball berardi: −100 ms → 1002."""
        for elapsed in (-10_000, -100, -1, 0, 1, 59_999, 60_000, 10**9):
            assert 100 <= points_for(elapsed, 60) <= 1000

    def test_javob_faqat_joriy_savolga(self, user, running) -> None:
        join(user, running)
        next_q, next_choice = _correct(running, 1)
        with pytest.raises(ArenaError) as exc:
            answer(user, running, next_q, next_choice)
        assert exc.value.code == "wrong_question"

    def test_ikki_marta_javob_berib_bolmaydi(self, user, running) -> None:
        join(user, running)
        q, choice = _correct(running, 0)
        first = answer(user, running, q, choice)
        assert first.is_correct and first.points > 0
        with pytest.raises(ArenaError) as exc:
            answer(user, running, q, choice)
        assert exc.value.code == "already_answered"

    def test_qoshilmasdan_javob_yoq(self, user, running) -> None:
        q, choice = _correct(running, 0)
        with pytest.raises(ArenaError) as exc:
            answer(user, running, q, choice)
        assert exc.value.code == "not_joined"

    def test_tugagan_raundga_qoshilib_bolmaydi(self, user) -> None:
        with pytest.raises(ArenaError) as exc:
            join(user, _round(start_offset_s=-500))
        assert exc.value.code == "finished"

    def test_yakunlash_qvant_bir_marta_va_faqat_javob_berganlarga(
        self, user, other_user, running
    ) -> None:
        join(user, running)
        join(other_user, running)  # kirdi, hech narsa qilmadi
        q, choice = _correct(running, 0)
        answer(user, running, q, choice)

        running.start_at = timezone.now() - timedelta(seconds=500)
        running.save()
        assert finalize(running) == 1
        assert ledger.get_wallet(user).balance == 15
        assert ledger.get_wallet(other_user).balance == 0
        assert finalize(running) == 0  # ikkinchi marta hech narsa


@pytest.mark.django_db
class TestArenaApi:
    def test_joriy_savol_togri_javobni_oshkor_qilmaydi(self, user, running) -> None:
        c = APIClient()
        c.force_authenticate(user=user)
        c.post(reverse("arena-join", args=[running.slug]))
        body = c.get(reverse("arena-current", args=[running.slug])).json()
        assert body["index"] == 0
        assert body["answered"] is False
        assert all("is_correct" not in ch for ch in body["question"]["choices"])

    def test_javob_va_standings(self, user, other_user, running) -> None:
        for u in (user, other_user):
            c = APIClient()
            c.force_authenticate(user=u)
            c.post(reverse("arena-join", args=[running.slug]))
        q, choice = _correct(running, 0)
        wrong = running.items.get(order=1).question.choices.get(is_correct=False).pk

        c = APIClient()
        c.force_authenticate(user=user)
        r = c.post(
            reverse("arena-answer", args=[running.slug]),
            {"question_id": q, "choice_id": choice},
            format="json",
        )
        assert r.status_code == 201 and r.json()["is_correct"] is True

        c2 = APIClient()
        c2.force_authenticate(user=other_user)
        r2 = c2.post(
            reverse("arena-answer", args=[running.slug]),
            {"question_id": q, "choice_id": wrong},
            format="json",
        )
        assert r2.json()["is_correct"] is False and r2.json()["points"] == 0

        rows = APIClient().get(reverse("arena-standings", args=[running.slug])).json()["results"]
        assert [row["username"] for row in rows][:2] == [user.username, other_user.username]
        assert rows[0]["rank"] == 1

    def test_royxat_ochiq(self, running) -> None:
        body = APIClient().get(reverse("arena-list")).json()
        assert body["count"] == 1
        assert body["results"][0]["question_count"] == 2
        assert body["results"][0]["is_running"] is True
        assert ArenaParticipation.objects.count() == 0


def test_standings_chegaralangan(running) -> None:
    """Cheklovsiz jadval SSE oqimida har 3 soniyada megabaytlab yuborilardi."""
    from arena.models import ArenaParticipation
    from arena.services import TOP_LIMIT, standings
    from core.models import User

    ArenaParticipation.objects.bulk_create(
        [
            ArenaParticipation(
                round=running,
                user=User.objects.create_user(f"neytron_{i:05d}"),
                score=i,
            )
            for i in range(TOP_LIMIT + 20)
        ]
    )

    rows = standings(running)

    assert len(rows) == TOP_LIMIT
    # Kesish saralashdan KEYIN bo'lishi kerak — eng yuqori ball birinchi.
    scores = [int(row["score"]) for row in rows]  # type: ignore[call-overload]
    assert scores == sorted(scores, reverse=True)
