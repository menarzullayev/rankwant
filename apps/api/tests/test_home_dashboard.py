"""The signed-in home page's endpoints (HITL 2026-10-05).

Activity events, the 14-day statistics, today's presence, the Qvant top
list, and the three fields the dashboard reads from existing lists.
"""

from __future__ import annotations

from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from blog.models import Post
from content.models import Roadmap, RoadmapStep
from contests.models import Contest, ContestRegistration
from core.models import User, UserSession
from judging.models import Attempt
from profiles.models import ActivityEvent
from qvant import ledger
from qvant.models import QvantTransaction
from ratings.models import RatingHistory, UserSolvedProblem


def _login(user: User) -> APIClient:
    client = APIClient()
    client.force_authenticate(user)
    return client


def _contest() -> Contest:
    now = timezone.now()
    return Contest.objects.create(
        slug="r1", title="Raund 1", start_at=now, end_at=now + timedelta(hours=2)
    )


@pytest.mark.django_db
class TestActivityEvents:
    def test_qvant_yozuvi_hodisa_qoldiradi(self, user) -> None:
        ledger.credit(user, 25, QvantTransaction.Reason.ADMIN, respect_cap=False)
        event = ActivityEvent.objects.get(user=user)
        assert event.kind == "qvant"
        assert event.data["amount"] == 25
        assert event.data["balance_after"] == 25

    def test_yechilgan_masala_hodisa_qoldiradi(self, user, problem) -> None:
        UserSolvedProblem.objects.create(user=user, problem=problem, difficulty_at_solve=900)
        event = ActivityEvent.objects.get(user=user, kind="solved")
        assert event.ref_id == problem.slug
        assert event.data == {"title": problem.title, "difficulty": 900}

    def test_musobaqaga_yozilish_hodisa_qoldiradi(self, user) -> None:
        ContestRegistration.objects.create(contest=_contest(), user=user)
        event = ActivityEvent.objects.get(user=user, kind="contest")
        assert event.data == {"title": "Raund 1"}

    def _history(self, user: User, rating_type: str, reason: str) -> None:
        RatingHistory.objects.create(
            user=user,
            rating_type=rating_type,
            value_before=1400,
            value_after=1450,
            delta=50,
            reason=reason,
        )

    def test_musobaqa_reytingi_hodisa(self, user) -> None:
        self._history(user, "contest", "contest")
        event = ActivityEvent.objects.get(user=user, kind="rating")
        assert event.data["delta"] == 50

    def test_yechim_reytingi_alohida_hodisa_emas(self, user) -> None:
        """The solve already has its own event; its rating change would double it."""
        self._history(user, "skills", "problem_solved")
        assert not ActivityEvent.objects.filter(user=user).exists()

    def test_activity_reytingi_hodisa_emas(self, user) -> None:
        self._history(user, "activity", "recalculation")
        assert not ActivityEvent.objects.filter(user=user).exists()

    def test_bulk_yozilgan_reyting_ham_hodisa(self, user) -> None:
        """`bulk_create` sends no signal — the bulk writer reports itself."""
        from profiles import activity

        row = RatingHistory(
            user=user,
            rating_type="contest",
            value_before=1400,
            value_after=1380,
            delta=-20,
            reason="contest",
            ref_type="contest",
            ref_id="r1",
        )
        RatingHistory.objects.bulk_create([row])
        assert not ActivityEvent.objects.exists()
        activity.record_ratings([row])
        assert ActivityEvent.objects.get().data["delta"] == -20

    def test_lenta_faqat_oziniki(self, user) -> None:
        other = User.objects.create_user(username="vali", password="Parol!12345")
        ledger.credit(user, 5, QvantTransaction.Reason.ADMIN, respect_cap=False)
        ledger.credit(other, 7, QvantTransaction.Reason.ADMIN, respect_cap=False)
        rows = _login(user).get(reverse("me-activity")).json()
        assert [row["data"]["amount"] for row in rows] == [5]

    def test_lenta_mehmonga_yopiq(self) -> None:
        assert APIClient().get(reverse("me-activity")).status_code in (401, 403)


@pytest.mark.django_db
class TestDailyStats:
    def test_on_tort_kun_va_import_sanalmaydi(self, user, problem, language) -> None:
        User.objects.create_user(username="cf1", password="x", origin=User.Origin.IMPORTED)
        Attempt.objects.create(user=user, problem=problem, language=language, source_code="x")
        Attempt.objects.create(user=user, problem=problem, language=language, source_code="y")
        rows = APIClient().get(reverse("platform-stats-daily")).json()
        assert len(rows) == 14
        assert rows[-1]["date"] == timezone.localdate().isoformat()
        real = User.objects.exclude(origin=User.Origin.IMPORTED).count()
        assert rows[-1]["new_users"] == real
        assert rows[-1]["attempts"] == 2
        assert rows[-1]["active_users"] == 1
        assert rows[0] == {
            "date": (timezone.localdate() - timedelta(days=13)).isoformat(),
            "new_users": 0,
            "active_users": 0,
            "attempts": 0,
        }


@pytest.mark.django_db
class TestPresence:
    def _session(self, user: User, key: str, ago: timedelta) -> None:
        UserSession.objects.create(user=user, session_key=key, last_seen=timezone.now() - ago)

    def test_bugun_faol_va_hozir_onlayn(self, user) -> None:
        other = User.objects.create_user(username="vali", password="Parol!12345")
        self._session(user, "a", timedelta(seconds=1))
        self._session(other, "b", timedelta(seconds=1))
        body = APIClient().get(reverse("presence")).json()
        assert body["today"] == 2
        assert body["online"] == 2
        assert {row["username"] for row in body["results"]} == {"aziz", "vali"}
        assert all(row["online"] for row in body["results"])

    def test_yashirgan_foydalanuvchi_chiqmaydi(self, user) -> None:
        user.hidden_fields = ["email", "online"]
        user.save(update_fields=["hidden_fields"])
        self._session(user, "a", timedelta(seconds=1))
        body = APIClient().get(reverse("presence")).json()
        assert body == {"today": 0, "online": 0, "results": []}

    def test_codeforces_tashrifi_sanalmaydi(self, user) -> None:
        """`last_seen_at` is written by the Codeforces sync too — only a
        session on this site counts."""
        User.objects.filter(pk=user.pk).update(last_seen_at=timezone.now())
        assert APIClient().get(reverse("presence")).json()["today"] == 0

    def test_kechagi_sessiya_chiqmaydi(self, user) -> None:
        self._session(user, "a", timedelta(days=2))
        assert APIClient().get(reverse("presence")).json()["today"] == 0


@pytest.mark.django_db
class TestTopLists:
    def test_qvant_top_balans_boyicha(self, user) -> None:
        other = User.objects.create_user(username="vali", password="Parol!12345")
        ledger.credit(user, 10, QvantTransaction.Reason.ADMIN, respect_cap=False)
        ledger.credit(other, 40, QvantTransaction.Reason.ADMIN, respect_cap=False)
        rows = APIClient().get(reverse("qvant-top")).json()
        assert [(row["username"], row["balance"]) for row in rows] == [("vali", 40), ("aziz", 10)]

    @pytest.mark.parametrize("field", ["streak_count", "rating_activity"])
    def test_yangi_saralash_maydonlari(self, user, field: str) -> None:
        other = User.objects.create_user(username="vali", password="Parol!12345")
        User.objects.filter(pk=other.pk).update(**{field: 99999})
        rows = APIClient().get(reverse("user-list"), {"ordering": f"-{field}"}).json()["results"]
        assert rows[0]["username"] == "vali"


@pytest.mark.django_db
class TestListFields:
    def test_yol_xaritasi_keyingi_qadam(self, user, problem) -> None:
        roadmap = Roadmap.objects.create(slug="boshlash", title="Boshlash", is_published=True)
        RoadmapStep.objects.create(roadmap=roadmap, order=1, title="Birinchi", problem=problem)
        RoadmapStep.objects.create(roadmap=roadmap, order=2, title="Ikkinchi")
        row = APIClient().get(reverse("roadmap-list")).json()[0]
        assert row["next_step"]["order"] == 1
        assert row["next_step"]["problem"] == problem.slug

        UserSolvedProblem.objects.create(user=user, problem=problem, difficulty_at_solve=800)
        row = _login(user).get(reverse("roadmap-list")).json()[0]
        assert row["solved_steps"] == 1
        assert row["next_step"]["order"] == 2

    def test_sarlavhasiz_qadam_masala_nomini_oladi(self, problem) -> None:
        roadmap = Roadmap.objects.create(slug="boshlash", title="Boshlash", is_published=True)
        RoadmapStep.objects.create(roadmap=roadmap, order=1, problem=problem)
        row = APIClient().get(reverse("roadmap-list")).json()[0]
        assert row["next_step"]["title"] == problem.title

    def test_urinishlar_soni_sahifaga_bogliq_emas(self, user, problem, language) -> None:
        """Thirty attempts are thirty, though the list returns 25 a page."""
        other = User.objects.create_user(username="vali", password="Parol!12345")
        for author, n in ((user, 30), (other, 2)):
            Attempt.objects.bulk_create(
                Attempt(user=author, problem=problem, language=language, source_code="x")
                for _ in range(n)
            )
        url = reverse("attempt-counts")
        query = {"username": user.username, "problems": f"{problem.slug},yoq"}
        assert APIClient().get(url, query).json() == {problem.slug: 30}
        assert APIClient().get(url, {"username": user.username}).json() == {}

    def test_hammasi_yechilgan_yolda_keyingi_qadam_yoq(self, user, problem) -> None:
        roadmap = Roadmap.objects.create(slug="boshlash", title="Boshlash", is_published=True)
        RoadmapStep.objects.create(roadmap=roadmap, order=1, problem=problem)
        UserSolvedProblem.objects.create(user=user, problem=problem, difficulty_at_solve=800)
        assert _login(user).get(reverse("roadmap-list")).json()[0]["next_step"] is None

    def test_musobaqa_qatnashchilari_soni(self, user) -> None:
        ContestRegistration.objects.create(contest=_contest(), user=user)
        row = APIClient().get(reverse("contest-list")).json()["results"][0]
        assert row["participant_count"] == 1

    def test_post_muqova_rasmi(self) -> None:
        Post.objects.create(
            slug="yangilik",
            title="Yangilik",
            body="matn",
            cover_url="https://example.com/a.png",
            is_published=True,
        )
        row = APIClient().get(reverse("post-list")).json()["results"][0]
        assert row["cover_url"] == "https://example.com/a.png"
