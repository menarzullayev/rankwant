"""Hisobni o'chirish (anonimlashtirish) va ma'lumot eksporti."""

from __future__ import annotations

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from contests.models import Contest, ContestRegistration, Standing
from core import account
from core.models import ApiToken, User
from judging.models import Attempt, CustomRun
from notifications.models import Notification
from problems.models import Favourite
from qvant import ledger
from qvant.models import QvantTransaction
from ratings.models import RatingHistory


@pytest.fixture
def full_user(db, problem, language) -> User:
    """Ma'lumoti bor foydalanuvchi — bo'sh hisobda o'chirish hech narsani isbotlamaydi."""
    u = User.objects.create_user(
        username="Aziz",
        password="Parol!12345",
        email="aziz@example.com",
        display_name="Aziz Karimov",
        bio="Toshkentdanman",
        avatar_url="https://example.com/a.png",
        telegram_id=555,
    )
    Attempt.objects.create(
        user=u, problem=problem, language=language, source_code="int main(){}", verdict="AC"
    )
    RatingHistory.objects.create(
        user=u, rating_type="skills", value_before=0, value_after=10, delta=10, reason="solve"
    )
    ledger.credit(u, 30, QvantTransaction.Reason.QUEST)
    Notification.objects.create(user=u, kind="system", title="Salom", body="…")
    CustomRun.objects.create(user=u, language=language, source_code="print(1)", stdin="")
    Favourite.objects.create(user=u, problem=problem)
    ApiToken.issue(u, "Laptop", ["read"], timezone.now() + timezone.timedelta(days=1))
    return u


@pytest.mark.django_db
class TestAnonimlashtirish:
    def test_shaxsiy_malumot_ochadi(self, full_user) -> None:
        account.anonymize(full_user)

        full_user.refresh_from_db()
        assert full_user.username == f"neytrino_{full_user.pk:05d}"
        assert full_user.display_name == f"Neytrino {full_user.pk}"
        assert full_user.email == ""
        assert full_user.bio == ""
        assert full_user.avatar_url == ""
        assert full_user.telegram_id is None
        assert full_user.is_active is False
        assert full_user.has_usable_password() is False

    def test_natijalar_joyida_qoladi(self, full_user) -> None:
        """Bu — qarorning butun mag'zi: yechim va reyting tarixi o'chmaydi."""
        account.anonymize(full_user)

        assert Attempt.objects.filter(user=full_user).count() == 1
        assert Attempt.objects.get(user=full_user).source_code == "int main(){}"
        assert RatingHistory.objects.filter(user=full_user).count() == 1
        assert QvantTransaction.objects.filter(user=full_user).exists()

    def test_ommaviy_yozuvda_orni_yoq_narsalar_ochadi(self, full_user) -> None:
        account.anonymize(full_user)

        assert not Notification.objects.filter(user=full_user).exists()
        assert not CustomRun.objects.filter(user=full_user).exists()
        assert not Favourite.objects.filter(user=full_user).exists()
        assert not ApiToken.objects.filter(user=full_user).exists()

    def test_jadval_orinlari_siljimaydi(self, full_user, other_user) -> None:
        """O'chirish o'rniga anonimlashtirishning SABABI.

        Qatorni o'chirish qolganlarning o'rnini surar va tugagan
        musobaqa tarixini yolg'onlashtirardi.
        """
        contest = Contest.objects.create(
            slug="c1",
            title="C1",
            start_at=timezone.now() - timezone.timedelta(hours=3),
            end_at=timezone.now() - timezone.timedelta(hours=1),
        )
        Standing.objects.create(contest=contest, user=full_user, rank=1, solved_count=3)
        Standing.objects.create(contest=contest, user=other_user, rank=2, solved_count=2)

        account.anonymize(full_user)

        rows = list(Standing.objects.filter(contest=contest).order_by("rank"))
        assert [r.rank for r in rows] == [1, 2]
        assert rows[0].user.username == f"neytrino_{full_user.pk:05d}"

    def test_nom_neytron_bilan_toqnashmaydi(self, full_user) -> None:
        """`prune_test_users --prefix neytron` anonimni olib ketmasligi kerak."""
        account.anonymize(full_user)

        full_user.refresh_from_db()
        assert not full_user.username.startswith("neytron_")
        assert not User.objects.filter(username__startswith="neytron_").exists()

    def test_ochirilgandan_keyin_kira_olmaydi(self, full_user) -> None:
        account.anonymize(full_user)

        c = APIClient()
        r = c.post(
            reverse("login"), {"username": "Aziz", "password": "Parol!12345"}, format="json"
        )
        assert r.status_code == 401


@pytest.mark.django_db
class TestDeleteEndpoint:
    def test_anonim_ochira_olmaydi(self, full_user) -> None:
        assert APIClient().delete(reverse("me")).status_code in (401, 403)

    def test_notogri_parol(self, full_user) -> None:
        c = APIClient()
        c.force_authenticate(user=full_user)

        r = c.delete(reverse("me"), {"password": "boshqa"}, format="json")

        assert r.status_code == 400
        full_user.refresh_from_db()
        assert full_user.username == "Aziz"

    def test_ochirish(self, full_user) -> None:
        c = APIClient()
        c.force_authenticate(user=full_user)

        r = c.delete(reverse("me"), {"password": "Parol!12345"}, format="json")

        assert r.status_code == 204
        full_user.refresh_from_db()
        assert account.is_anonymized(full_user)

    def test_profil_sahifasi_yopiladi(self, full_user) -> None:
        c = APIClient()
        c.force_authenticate(user=full_user)
        c.delete(reverse("me"), {"password": "Parol!12345"}, format="json")

        full_user.refresh_from_db()
        r = APIClient().get(reverse("user-detail", args=[full_user.username]))
        assert r.status_code == 404


@pytest.mark.django_db
class TestExport:
    def test_ozining_malumoti(self, full_user) -> None:
        c = APIClient()
        c.force_authenticate(user=full_user)

        r = c.get(reverse("me-export"))

        assert r.status_code == 200
        assert r["Content-Disposition"].startswith("attachment")
        assert r.data["profile"]["email"] == "aziz@example.com"
        assert len(r.data["attempts"]) == 1
        # Kod ham chiqadi: eksportning maqsadi shu — o'chirishdan oldin
        # hamma narsani olib qolish.
        assert r.data["attempts"][0]["source_code"] == "int main(){}"
        assert len(r.data["rating_history"]) == 1
        assert r.data["qvant"][0]["amount"] == 30

    def test_anonim_olmaydi(self, full_user) -> None:
        assert APIClient().get(reverse("me-export")).status_code in (401, 403)

    def test_boshqaning_malumoti_chiqmaydi(self, full_user, other_user, problem, language) -> None:
        Attempt.objects.create(
            user=other_user, problem=problem, language=language, source_code="SIR", verdict="AC"
        )
        c = APIClient()
        c.force_authenticate(user=full_user)

        r = c.get(reverse("me-export"))

        assert all(a["source_code"] != "SIR" for a in r.data["attempts"])
