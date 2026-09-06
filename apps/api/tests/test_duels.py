"""Duel — 1v1, Challenges Elo (PRD Phase 3)."""

from __future__ import annotations

from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from duels.models import Duel
from duels.services import DuelError, accept, cancel, create, finalize
from judging.models import Attempt
from judging.verdicts import Verdict
from notifications.models import Notification
from problems.models import Problem
from qvant import ledger
from ratings.models import RatingHistory


@pytest.fixture
def pool(db, problem, hard_problem) -> list[Problem]:
    extra = [
        Problem.objects.create(slug=f"p{i}", title=f"P{i}", difficulty=1200, is_public=True)
        for i in range(4)
    ]
    return [problem, hard_problem, *extra]


def _duel(challenger, **kw) -> Duel:
    return create(
        challenger,
        title=kw.get("title", "Div 2"),
        problem_count=kw.get("problem_count", 3),
        difficulty=kw.get("difficulty", 1200),
        duration_minutes=kw.get("duration_minutes", 60),
        start_at=kw.get("start_at", timezone.now() + timedelta(minutes=10)),
    )


def _ac(user, problem, when) -> None:
    from problems.models import Language

    lang = Language.objects.get_or_create(code="cpp23", defaults={"name": "C++", "version": "23"})[
        0
    ]
    a = Attempt.objects.create(
        user=user, problem=problem, language=lang, source_code="x", verdict=Verdict.AC
    )
    Attempt.objects.filter(pk=a.pk).update(created_at=when)


@pytest.mark.django_db
class TestDuelFlow:
    def test_chaqiriq_va_qabul(self, user, other_user, pool) -> None:
        duel = _duel(user)
        assert duel.status == Duel.Status.OPEN
        accept(other_user, duel)
        duel.refresh_from_db()
        assert duel.status == Duel.Status.ACCEPTED
        assert duel.items.count() == 3
        assert Notification.objects.filter(user=user, kind=Notification.Kind.DUEL).exists()

    def test_ozini_qabul_qila_olmaydi(self, user, pool) -> None:
        with pytest.raises(DuelError) as exc:
            accept(user, _duel(user))
        assert exc.value.code == "self"

    def test_juda_erta_va_juda_kop(self, user, pool) -> None:
        with pytest.raises(DuelError) as exc:
            _duel(user, start_at=timezone.now() + timedelta(minutes=1))
        assert exc.value.code == "too_soon"
        for i in range(3):
            _duel(user, title=f"d{i}")
        with pytest.raises(DuelError) as exc:
            _duel(user, title="d4")
        assert exc.value.code == "too_many"

    def test_bekor_faqat_chaqiruvchi(self, user, other_user, pool) -> None:
        duel = _duel(user)
        with pytest.raises(DuelError):
            cancel(other_user, duel)
        assert cancel(user, duel).status == Duel.Status.CANCELLED

    def test_yechilgan_masala_tanlanmaydi(self, user, other_user, pool) -> None:
        from ratings.models import UserSolvedProblem

        UserSolvedProblem.objects.create(user=user, problem=pool[2], difficulty_at_solve=1200)
        duel = _duel(user, problem_count=5)
        accept(other_user, duel)
        assert pool[2] not in duel.problems.all()


@pytest.mark.django_db
class TestDuelFinalize:
    def _finished_duel(self, user, other_user) -> Duel:
        duel = _duel(user, start_at=timezone.now() + timedelta(minutes=10))
        accept(other_user, duel)
        # Vaqtni orqaga suramiz: duel 2 soat oldin boshlangan va tugagan
        Duel.objects.filter(pk=duel.pk).update(start_at=timezone.now() - timedelta(hours=2))
        duel.refresh_from_db()
        return duel

    def test_galaba_elo_qvant_bildirishnoma(self, user, other_user, pool) -> None:
        duel = self._finished_duel(user, other_user)
        problems = list(duel.problems.all())
        inside = duel.start_at + timedelta(minutes=10)
        _ac(user, problems[0], inside)
        _ac(user, problems[1], inside)
        _ac(other_user, problems[0], inside)

        assert finalize(duel) is True
        duel.refresh_from_db()
        assert duel.winner == user and (duel.challenger_solved, duel.opponent_solved) == (2, 1)

        user.refresh_from_db()
        other_user.refresh_from_db()
        assert user.rating_challenges > 1400 > other_user.rating_challenges
        # Klassik Elo nol-yig'indi
        assert user.rating_challenges + other_user.rating_challenges == 2800
        assert (
            RatingHistory.objects.filter(
                rating_type="challenges", reason=RatingHistory.Reason.DUEL
            ).count()
            == 2
        )
        assert ledger.get_wallet(user).balance == 20
        assert ledger.get_wallet(other_user).balance == 0
        assert Notification.objects.filter(kind=Notification.Kind.DUEL, user=other_user).exists()

    def test_oynadan_tashqari_ac_hisoblanmaydi(self, user, other_user, pool) -> None:
        duel = self._finished_duel(user, other_user)
        problems = list(duel.problems.all())
        _ac(user, problems[0], duel.start_at - timedelta(minutes=1))  # oldin
        _ac(other_user, problems[0], duel.end_at + timedelta(minutes=1))  # keyin
        finalize(duel)
        duel.refresh_from_db()
        assert duel.is_draw and (duel.challenger_solved, duel.opponent_solved) == (0, 0)

    def test_teng_hisobda_tezroq_yutadi(self, user, other_user, pool) -> None:
        duel = self._finished_duel(user, other_user)
        p = duel.problems.first()
        _ac(user, p, duel.start_at + timedelta(minutes=30))
        _ac(other_user, p, duel.start_at + timedelta(minutes=5))
        finalize(duel)
        duel.refresh_from_db()
        assert duel.winner == other_user

    def test_ikki_marta_yakunlanmaydi(self, user, other_user, pool) -> None:
        duel = self._finished_duel(user, other_user)
        assert finalize(duel) is True
        assert finalize(duel) is False


@pytest.mark.django_db
class TestDuelApi:
    def test_masalalar_boshlangunicha_yashirin(self, user, other_user, pool) -> None:
        duel = _duel(user)
        accept(other_user, duel)
        c = APIClient()
        c.force_authenticate(user=user)
        assert c.get(reverse("duel-detail", args=[duel.slug])).json()["problems"] == []

        Duel.objects.filter(pk=duel.pk).update(start_at=timezone.now() - timedelta(minutes=1))
        body = c.get(reverse("duel-detail", args=[duel.slug])).json()
        assert body["is_running"] and len(body["problems"]) == 3

        # Begona odam yurayotgan duelning masalalarini ham ko'rmaydi
        assert APIClient().get(reverse("duel-detail", args=[duel.slug])).json()["problems"] == []

    def test_kutish_xonasi_va_mine(self, user, other_user, pool) -> None:
        _duel(user)
        assert APIClient().get(reverse("duel-list")).json()["count"] == 1
        c = APIClient()
        c.force_authenticate(user=user)
        body = c.get(reverse("duel-mine")).json()
        assert body["record"] == {"wins": 0, "draws": 0, "losses": 0}
        assert len(body["results"]) == 1

    def test_api_orqali_yaratish_va_qabul(self, user, other_user, pool) -> None:
        c = APIClient()
        c.force_authenticate(user=user)
        r = c.post(
            reverse("duel-list"),
            {"title": "Blitz", "start_at": (timezone.now() + timedelta(minutes=15)).isoformat()},
            format="json",
        )
        assert r.status_code == 201
        slug = r.json()["slug"]
        c2 = APIClient()
        c2.force_authenticate(user=other_user)
        assert c2.post(reverse("duel-accept", args=[slug])).json()["status"] == "accepted"
