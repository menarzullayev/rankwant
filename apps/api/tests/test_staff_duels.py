"""Staff API: duel nazorati (`staff/duels/`)."""

from __future__ import annotations

from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from core.models import User
from duels.models import Duel
from duels.services import accept, create
from judging.models import Attempt
from judging.verdicts import Verdict
from notifications.models import Notification
from problems.models import Language, Problem


@pytest.fixture
def staff(db) -> User:
    return User.objects.create_user("staff1", password="x", is_staff=True)


@pytest.fixture
def staff_client(staff) -> APIClient:
    c = APIClient()
    c.force_authenticate(user=staff)
    return c


@pytest.fixture
def pool(db, problem, hard_problem) -> list[Problem]:
    extra = [
        Problem.objects.create(slug=f"p{i}", title=f"P{i}", difficulty=1200, is_public=True)
        for i in range(4)
    ]
    return [problem, hard_problem, *extra]


def _open(challenger: User, title: str = "Div 2") -> Duel:
    return create(
        challenger,
        title=title,
        problem_count=3,
        difficulty=1200,
        duration_minutes=60,
        start_at=timezone.now() + timedelta(minutes=10),
    )


def _accepted(user: User, other_user: User, *, minutes_ago: int = 0) -> Duel:
    """Qabul qilingan duel; `minutes_ago` bilan boshlanishni orqaga suramiz."""
    duel = _open(user)
    accept(other_user, duel)
    if minutes_ago:
        Duel.objects.filter(pk=duel.pk).update(
            start_at=timezone.now() - timedelta(minutes=minutes_ago)
        )
    duel.refresh_from_db()
    return duel


def _ac(user: User, problem: Problem, when) -> None:
    lang = Language.objects.get_or_create(code="cpp23", defaults={"name": "C++", "version": "23"})[
        0
    ]
    a = Attempt.objects.create(
        user=user, problem=problem, language=lang, source_code="x", verdict=Verdict.AC
    )
    Attempt.objects.filter(pk=a.pk).update(created_at=when)


@pytest.mark.django_db
class TestStaffDuelAccess:
    def test_anonim(self) -> None:
        r = APIClient().get(reverse("staff-duel-list"))
        assert r.status_code in (401, 403)

    def test_oddiy_foydalanuvchi(self, user, pool) -> None:
        duel = _open(user)
        c = APIClient()
        c.force_authenticate(user=user)
        assert c.get(reverse("staff-duel-list")).status_code == 403
        assert c.post(reverse("staff-duel-cancel", args=[duel.slug])).status_code == 403
        assert c.post(reverse("staff-duel-finalize", args=[duel.slug])).status_code == 403
        duel.refresh_from_db()
        assert duel.status == Duel.Status.OPEN


@pytest.mark.django_db
class TestStaffDuelRead:
    def test_barcha_holatlar_royxatda(self, staff_client, user, other_user, pool) -> None:
        _open(user, "Ochiq")
        _accepted(user, other_user)
        cancelled = _open(user, "Bekor")
        Duel.objects.filter(pk=cancelled.pk).update(status=Duel.Status.CANCELLED)

        body = staff_client.get(reverse("staff-duel-list")).json()
        assert body["count"] == 3
        assert {d["status"] for d in body["results"]} == {"open", "accepted", "cancelled"}
        # Ommaviy ro'yxat esa faqat ochiqlarni ko'rsatadi — o'zgarmagan
        assert APIClient().get(reverse("duel-list")).json()["count"] == 1

    def test_qidiruv_va_tartib(self, staff_client, user, other_user, pool) -> None:
        first = _open(user, "Birinchi")
        second = _open(other_user, "Ikkinchi")

        url = reverse("staff-duel-list")
        by_user = staff_client.get(url, {"search": "bekzod"}).json()["results"]
        assert [d["slug"] for d in by_user] == [second.slug]
        by_title = staff_client.get(url, {"search": "Birin"}).json()["results"]
        assert [d["slug"] for d in by_title] == [first.slug]
        ordered = staff_client.get(url, {"ordering": "created_at"}).json()["results"]
        assert [d["slug"] for d in ordered] == [first.slug, second.slug]
        default = staff_client.get(url).json()["results"]
        assert [d["slug"] for d in default] == [second.slug, first.slug]

    def test_retrieve_masalalar_bilan(self, staff_client, user, other_user, pool) -> None:
        duel = _accepted(user, other_user)
        body = staff_client.get(reverse("staff-duel-detail", args=[duel.slug])).json()
        assert body["challenger"] == "aziz" and body["opponent"] == "bekzod"
        assert len(body["problems"]) == 3
        assert body["is_due"] is False

    def test_yozish_yoq(self, staff_client, user, pool) -> None:
        duel = _open(user)
        assert staff_client.post(reverse("staff-duel-list"), {"title": "x"}).status_code == 405
        detail = reverse("staff-duel-detail", args=[duel.slug])
        assert staff_client.patch(detail, {"title": "x"}).status_code == 405
        assert staff_client.delete(detail).status_code == 405
        assert Duel.objects.filter(pk=duel.pk).exists()


@pytest.mark.django_db
class TestStaffDuelCancel:
    def test_ochiq_bekor_bildirishnomasiz(self, staff_client, user, pool) -> None:
        duel = _open(user)
        r = staff_client.post(reverse("staff-duel-cancel", args=[duel.slug]))
        assert r.status_code == 200
        assert r.json()["status"] == "cancelled"
        assert not Notification.objects.filter(kind=Notification.Kind.DUEL).exists()

    def test_qabul_qilingan_bekor_ikkalasiga_xabar(
        self, staff_client, user, other_user, pool
    ) -> None:
        duel = _accepted(user, other_user)
        Notification.objects.all().delete()  # qabul qilish bildirishnomasini tozalaymiz
        r = staff_client.post(reverse("staff-duel-cancel", args=[duel.slug]))
        assert r.status_code == 200
        duel.refresh_from_db()
        assert duel.status == Duel.Status.CANCELLED
        notified = set(
            Notification.objects.filter(kind=Notification.Kind.DUEL, ref_id=duel.slug).values_list(
                "user__username", flat=True
            )
        )
        assert notified == {"aziz", "bekzod"}

    def test_tugagan_bekor_qilinmaydi(self, staff_client, user, other_user, pool) -> None:
        duel = _accepted(user, other_user, minutes_ago=120)
        staff_client.post(reverse("staff-duel-finalize", args=[duel.slug]))
        r = staff_client.post(reverse("staff-duel-cancel", args=[duel.slug]))
        assert r.status_code == 400
        assert r.json()["error"]["code"] == "not_cancellable"


@pytest.mark.django_db
class TestStaffDuelFinalize:
    def test_ochiq_yakunlanmaydi(self, staff_client, user, pool) -> None:
        duel = _open(user)
        r = staff_client.post(reverse("staff-duel-finalize", args=[duel.slug]))
        assert r.status_code == 400
        assert r.json()["error"]["code"] == "not_accepted"

    def test_muddati_otgan_yakunlanadi(self, staff_client, user, other_user, pool) -> None:
        duel = _accepted(user, other_user, minutes_ago=120)
        _ac(user, duel.problems.first(), duel.start_at + timedelta(minutes=5))
        r = staff_client.post(reverse("staff-duel-finalize", args=[duel.slug]))
        assert r.status_code == 200
        body = r.json()
        assert body["status"] == "finished"
        assert body["winner"] == "aziz"
        assert (body["challenger_solved"], body["opponent_solved"]) == (1, 0)

    def test_muddati_otmagan_force_siz_rad(self, staff_client, user, other_user, pool) -> None:
        duel = _accepted(user, other_user, minutes_ago=10)
        r = staff_client.post(reverse("staff-duel-finalize", args=[duel.slug]))
        assert r.status_code == 400
        assert r.json()["error"]["code"] == "not_due"
        duel.refresh_from_db()
        assert duel.status == Duel.Status.ACCEPTED

    def test_force_yakunlaydi_va_aclar_saqlanadi(
        self, staff_client, user, other_user, pool
    ) -> None:
        """Davom etayotgan duel majburan yakunlanganda o'ynalgan AC'lar sanaladi."""
        duel = _accepted(user, other_user, minutes_ago=10)
        _ac(other_user, duel.problems.first(), duel.start_at + timedelta(minutes=5))
        r = staff_client.post(
            reverse("staff-duel-finalize", args=[duel.slug]), {"force": True}, format="json"
        )
        assert r.status_code == 200
        body = r.json()
        assert body["status"] == "finished"
        assert body["winner"] == "bekzod"
        assert (body["challenger_solved"], body["opponent_solved"]) == (0, 1)
        duel.refresh_from_db()
        assert duel.end_at <= timezone.now()
        assert duel.ratings_applied_at is not None
        assert (
            Notification.objects.filter(kind=Notification.Kind.DUEL, ref_id=duel.slug).count() >= 2
        )

    def test_ikki_marta_yakunlanmaydi(self, staff_client, user, other_user, pool) -> None:
        duel = _accepted(user, other_user, minutes_ago=120)
        url = reverse("staff-duel-finalize", args=[duel.slug])
        assert staff_client.post(url).status_code == 200
        r = staff_client.post(url, {"force": True}, format="json")
        assert r.status_code == 400
        assert r.json()["error"]["code"] == "not_accepted"
