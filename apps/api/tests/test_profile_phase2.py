"""Profil 2-bosqichi — unvon, rollar, onlayn holat va yutuqlar (ADR-0018)."""

from __future__ import annotations

import importlib
import io
from datetime import datetime, timedelta
from typing import Any

import pytest
from django.apps import apps
from django.core.management import call_command
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from contests.models import Contest, ContestRegistration, Standing
from core.models import User, UserSession
from judging.models import Attempt
from judging.verdicts import Verdict
from problems.models import Language, Problem
from profiles import achievements, public
from profiles.models import Follow, UserAchievement
from profiles.titles import title_for
from qvant import ledger
from qvant.models import QvantQuest, QvantTransaction, UserQuestCompletion
from ratings.models import UserSolvedProblem
from ratings.services import on_attempt_judged


def kirgan(user: User) -> APIClient:
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def reytingli(user: User, rating: int, contests: int = 1) -> User:
    user.rating_contest = rating
    user.rated_contest_count = contests
    user.save(update_fields=["rating_contest", "rated_contest_count"])
    return user


def profil(user: User, viewer: User | None = None) -> Any:
    client = kirgan(viewer) if viewer else APIClient()
    return client.get(reverse("user-profile", args=[user.username])).data


def test_unvon_chegaralari() -> None:
    assert title_for(0, 1) == {"code": "kvark", "level": 1}
    assert title_for(1399, 1) == {"code": "foton", "level": 2}
    assert title_for(1400, 1) == {"code": "elektron", "level": 3}
    assert title_for(2699, 3) == {"code": "yulduz", "level": 8}
    assert title_for(2700, 3) == {"code": "galaktika", "level": 9}
    # Reytingli musobaqasiz — boshlang'ich 1400 hali hech narsa aytmaydi.
    assert title_for(3000, 0) is None


@pytest.mark.django_db
class TestUnvonHammaJoyda:
    def test_foydalanuvchi_royxatlari(self, user: User, other_user: User) -> None:
        reytingli(user, 1850)
        Follow.objects.create(follower=user, following=other_user)

        leaders = {
            row["username"]: row["title"]
            for row in APIClient().get(reverse("user-list")).data["results"]
        }
        followers = APIClient().get(reverse("user-followers", args=[other_user.username])).data

        assert leaders == {"aziz": {"code": "atom", "level": 5}, "bekzod": None}
        assert followers["results"][0]["title"] == {"code": "atom", "level": 5}
        assert profil(user)["title"] == {"code": "atom", "level": 5}
        assert profil(other_user)["title"] is None

    def test_urinish_standings_jamoa(
        self, user: User, problem: Problem, language: Language, contest: Contest
    ) -> None:
        reytingli(user, 2450)
        Attempt.objects.create(
            user=user, problem=problem, language=language, source_code="x", verdict=Verdict.AC
        )
        Standing.objects.create(contest=contest, user=user, rank=1, solved_count=1, penalty=5)
        team = kirgan(user).post(reverse("me-teams"), {"name": "Alfa"}, format="json")

        attempts = APIClient().get(reverse("attempt-list"), {"username": user.username}).data
        standings = APIClient().get(reverse("contest-standings", args=[contest.slug])).data

        yulduz = {"code": "yulduz", "level": 8}
        assert attempts["results"][0]["user_title"] == yulduz
        assert standings["results"][0]["user_title"] == yulduz
        assert team.status_code == 201
        assert team.data["members"][0]["title"] == yulduz


@pytest.mark.django_db
class TestRollar:
    def test_hamma_rollar(
        self, user: User, other_user: User, problem: Problem, contest: Contest
    ) -> None:
        user.is_staff = True
        user.save(update_fields=["is_staff"])
        problem.author = user
        problem.save(update_fields=["author"])
        contest.jury.add(user)
        Standing.objects.create(contest=contest, user=user, rank=1, solved_count=2, penalty=30)
        Standing.objects.create(contest=contest, user=other_user, rank=2, solved_count=1, penalty=9)

        roles = {row["code"]: row for row in profil(user)["roles"]}

        assert set(roles) == {"staff", "author", "jury", "champion"}
        assert roles["champion"]["contest"] == "round-1"
        assert profil(other_user)["roles"] == []

    def test_chempion_qoidalari(self, user: User, other_user: User, contest: Contest) -> None:
        Standing.objects.create(contest=contest, user=user, rank=1, solved_count=2, penalty=30)
        teng = Standing.objects.create(
            contest=contest, user=other_user, rank=2, solved_count=2, penalty=30
        )
        assert public.champion_of(other_user) == contest, "teng natija ham g'olib"

        teng.solved_count = 1
        teng.save(update_fields=["solved_count"])
        assert public.champion_of(other_user) is None

        ContestRegistration.objects.create(
            user=user, contest=contest, virtual_start_at=timezone.now()
        )
        assert public.champion_of(user) is None, "virtual ishtirok rasmiy emas"

        ContestRegistration.objects.filter(user=user).delete()
        Contest.objects.filter(pk=contest.pk).update(end_at=timezone.now() - timedelta(days=400))
        assert public.champion_of(user) is None, "365 kundan eski"

    def test_hech_narsa_yechmagan_birinchi_chempion_emas(
        self, user: User, contest: Contest
    ) -> None:
        Standing.objects.create(contest=contest, user=user, rank=1, solved_count=0, penalty=0)

        assert public.champion_of(user) is None


@pytest.mark.django_db
class TestOnlayn:
    @staticmethod
    def seen(user: User, when: datetime) -> None:
        # What `core.sessions.record` writes: the session row and the user column (ADR-0024).
        UserSession.objects.update_or_create(
            user=user, session_key="a" * 40, defaults={"last_seen": when}
        )
        User.objects.filter(pk=user.pk).update(last_seen_at=when)

    def test_onlayn_va_oxirgi_faollik(self, user: User) -> None:
        self.seen(user, timezone.now() - timedelta(minutes=2))
        body = profil(user)
        assert body["online"] is True
        assert body["last_seen"] is not None

        self.seen(user, timezone.now() - timedelta(hours=3))
        body = profil(user)
        assert body["online"] is False
        assert body["last_seen"] is not None

    def test_chiqib_ketsa_ham_oxirgi_faollik_qoladi(self, user: User) -> None:
        # Signing out deletes the session; the visit it recorded stays (ADR-0024).
        self.seen(user, timezone.now() - timedelta(hours=3))
        UserSession.objects.filter(user=user).delete()

        body = profil(user)

        assert (body["online"], body["last_seen"] is not None) == (False, True)

    def test_yashirilsa_faqat_egasi_koradi(self, user: User, other_user: User) -> None:
        self.seen(user, timezone.now())
        saved = kirgan(user).patch(reverse("me"), {"hidden_fields": ["online"]}, format="json")

        begona = profil(user, other_user)
        egasi = profil(user, user)

        assert saved.status_code == 200
        assert (begona["online"], begona["last_seen"]) == (False, None)
        assert egasi["online"] is True


@pytest.mark.django_db
class TestYutuqlar:
    def test_yangi_yutuq_bir_marta_qvant_beradi(self, user: User, problem: Problem) -> None:
        UserSolvedProblem.objects.create(user=user, problem=problem, difficulty_at_solve=800)

        assert achievements.on_solved(user, streak=0) == ["solve-1"]
        assert achievements.on_solved(user, streak=0) == []

        tx = QvantTransaction.objects.get(user=user)
        assert (tx.reason, tx.ref_type, tx.ref_id, tx.amount) == (
            "achievement",
            "achievement",
            "solve-1",
            10,
        )
        assert UserAchievement.objects.get(user=user, code="solve-1").awarded == 10
        out = io.StringIO()
        call_command("qvant_audit", stdout=out)
        assert "hammasi mos" in out.getvalue()

    def test_quest_tolagan_yutuq_qvantsiz(self, user: User) -> None:
        assert achievements.on_solved(user, streak=8) == ["streak-7"]

        assert UserAchievement.objects.get(user=user, code="streak-7").awarded == 0
        assert not QvantTransaction.objects.filter(user=user).exists()

    def test_rejudge_yutuqni_va_qvantni_qaytaradi(self, user: User, problem: Problem) -> None:
        solved = UserSolvedProblem.objects.create(
            user=user, problem=problem, difficulty_at_solve=800
        )
        achievements.on_solved(user, streak=0)
        solved.delete()

        assert achievements.on_unsolved(user) == ["solve-1"]
        assert ledger.get_wallet(user).balance == 0
        assert not UserAchievement.objects.filter(user=user).exists()

    def test_kunlik_shiftga_boysunadi(self, user: User) -> None:
        ledger.credit(user, 95, QvantTransaction.Reason.QUEST)

        granted = achievements.grant(user, "solve-1")

        assert granted == min(10, 5)
        assert UserAchievement.objects.filter(user=user, code="solve-1").exists()

    def test_musobaqa_bosqichi_faqat_tenglikda(self, user: User) -> None:
        reytingli(user, 1500, contests=1)
        assert achievements.on_rated_contest(user) == ["contest-1"]

        reytingli(user, 1500, contests=2)
        assert achievements.on_rated_contest(user) == []

    def test_birinchi_ac_hook(
        self,
        user: User,
        problem: Problem,
        language: Language,
        django_capture_on_commit_callbacks: Any,
    ) -> None:
        attempt = Attempt.objects.create(
            user=user, problem=problem, language=language, source_code="x", verdict=Verdict.AC
        )

        with django_capture_on_commit_callbacks(execute=True):
            on_attempt_judged(attempt)

        assert UserAchievement.objects.filter(user=user, code="solve-1").exists()

    def test_royxat_noyoblik_bilan(self, user: User, other_user: User) -> None:
        achievements.grant(user, "solve-1")

        rows = {
            row["code"]: row
            for row in APIClient().get(reverse("user-achievements", args=[user.username])).data
        }

        assert rows["solve-1"]["done"] is True
        assert rows["solve-1"]["achieved_at"] is not None
        assert rows["solve-1"]["rarity"] == 50.0, "ikki faol foydalanuvchidan biri"
        assert rows["solve-10"]["tier"] == "bronze"
        assert rows["contest-50"]["tier"] == "gold"

    def test_uchtasini_tanlash(self, user: User) -> None:
        for code in ("solve-1", "contest-1", "profile-1", "streak-7"):
            UserAchievement.objects.create(user=user, code=code)
        client = kirgan(user)

        def pin(codes: list[str]) -> int:
            return client.patch(
                reverse("me"), {"pinned_achievements": codes}, format="json"
            ).status_code

        assert pin(["solve-1", "contest-1", "streak-7", "profile-1"]) == 400, "ko'pi bilan uchta"
        assert pin(["solve-1", "solve-1"]) == 400
        assert pin(["solve-100"]) == 400, "olinmagan yutuq"
        assert pin(["streak-7", "solve-1", "contest-1"]) == 200

        pinned = profil(user)["pinned"]
        assert [row["code"] for row in pinned] == ["streak-7", "solve-1", "contest-1"]
        assert pinned[0]["tier"] == "bronze"

    def test_migratsiya_tarixiylarni_qvantsiz_tiklaydi(
        self, user: User, other_user: User, problem: Problem
    ) -> None:
        solved = UserSolvedProblem.objects.create(
            user=user, problem=problem, difficulty_at_solve=800
        )
        reytingli(user, 1500, contests=1)
        quest = QvantQuest.objects.create(
            code="profile_complete", type=QvantQuest.Type.ACHIEVEMENT, title_uz="P", reward=50
        )
        UserQuestCompletion.objects.create(
            user=other_user, quest=quest, period_key="once", awarded=50
        )
        migration = importlib.import_module("profiles.migrations.0004_backfill_achievements")

        migration.backfill(apps, None)
        migration.backfill(apps, None)

        rows = {(row.user_id, row.code): row for row in UserAchievement.objects.all()}
        assert set(rows) == {
            (user.pk, "solve-1"),
            (user.pk, "contest-1"),
            (other_user.pk, "profile-1"),
        }
        assert rows[(user.pk, "solve-1")].achieved_at == solved.first_ac_at
        assert all(row.awarded == 0 for row in rows.values())
        assert not QvantTransaction.objects.exists()
