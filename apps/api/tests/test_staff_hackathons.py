"""Staff API: `staff/hackathons/` — CRUD, barcha loyihalar, baholash."""

from __future__ import annotations

from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from core.models import User
from hackathons.models import Hackathon, HackathonSubmission
from hackathons.services import submit

ENTRY = {"title": "Bot", "description": "Telegram bot", "repo_url": "https://github.com/x/y"}


def _iso(delta: timedelta) -> str:
    return (timezone.now() + delta).isoformat()


def _payload(slug: str = "yangi") -> dict[str, object]:
    return {
        "slug": slug,
        "title": "Yangi hakaton",
        "description": "# Shartlar",
        "start_at": _iso(timedelta(days=1)),
        "submission_deadline": _iso(timedelta(days=3)),
        "end_at": _iso(timedelta(days=5)),
        "is_public": False,
    }


def _open_hackathon(slug: str = "ochiq") -> Hackathon:
    now = timezone.now()
    return Hackathon.objects.create(
        slug=slug,
        title="Ochiq",
        start_at=now - timedelta(days=1),
        submission_deadline=now + timedelta(days=1),
        end_at=now + timedelta(days=3),
    )


@pytest.fixture
def staff(db) -> User:
    return User.objects.create_user("staff1", password="x", is_staff=True)


@pytest.fixture
def staff_client(staff) -> APIClient:
    c = APIClient()
    c.force_authenticate(user=staff)
    return c


@pytest.mark.django_db
class TestStaffHackathonAccess:
    def test_anonim_401(self) -> None:
        _open_hackathon()
        c = APIClient()
        assert c.get(reverse("staff-hackathon-list")).status_code == 401
        assert c.post(reverse("staff-hackathon-list"), _payload(), format="json").status_code == 401
        assert c.get(reverse("staff-hackathon-submissions", args=["ochiq"])).status_code == 401

    def test_oddiy_foydalanuvchi_403(self, user) -> None:
        h = _open_hackathon()
        entry = submit(user, h, **ENTRY)
        c = APIClient()
        c.force_authenticate(user=user)
        assert c.get(reverse("staff-hackathon-list")).status_code == 403
        assert c.post(reverse("staff-hackathon-list"), _payload(), format="json").status_code == 403
        assert c.get(reverse("staff-hackathon-submissions", args=[h.slug])).status_code == 403
        url = reverse("staff-hackathon-score-entry", args=[h.slug, entry.pk])
        assert c.post(url, {"score": 50}, format="json").status_code == 403

    def test_yashirin_hakaton_ommaviy_royxatda_yoq(self, staff_client) -> None:
        """Staff yuzasi ommaviy API'ga ta'sir qilmaydi: is_public=False ko'rinmaydi."""
        staff_client.post(reverse("staff-hackathon-list"), _payload(), format="json")
        assert APIClient().get(reverse("hackathon-list")).json()["count"] == 0
        assert staff_client.get(reverse("staff-hackathon-list")).json()["count"] == 1


@pytest.mark.django_db
class TestStaffHackathonCrud:
    def test_yaratish(self, staff_client) -> None:
        res = staff_client.post(reverse("staff-hackathon-list"), _payload(), format="json")
        assert res.status_code == 201, res.json()
        body = res.json()
        assert body["slug"] == "yangi"
        assert body["is_public"] is False
        assert body["submission_count"] == 0
        assert body["accepts_submissions"] is False
        assert Hackathon.objects.filter(slug="yangi").exists()

    def test_slug_takrorlanmaydi(self, staff_client) -> None:
        _open_hackathon("ochiq")
        res = staff_client.post(reverse("staff-hackathon-list"), _payload("ochiq"), format="json")
        assert res.status_code == 400

    def test_royxat_va_qidiruv(self, staff_client) -> None:
        _open_hackathon("alpha")
        _open_hackathon("beta")
        body = staff_client.get(reverse("staff-hackathon-list"), {"search": "beta"}).json()
        assert [h["slug"] for h in body["results"]] == ["beta"]

    def test_olish_va_tahrirlash(self, staff_client, user) -> None:
        h = _open_hackathon()
        submit(user, h, **ENTRY)
        url = reverse("staff-hackathon-detail", args=[h.slug])
        body = staff_client.get(url).json()
        assert body["submission_count"] == 1
        assert body["accepts_submissions"] is True

        res = staff_client.patch(url, {"title": "Yangilandi", "is_public": False}, format="json")
        assert res.status_code == 200
        h.refresh_from_db()
        assert h.title == "Yangilandi"
        assert h.is_public is False

    def test_ochirish(self, staff_client) -> None:
        h = _open_hackathon()
        url = reverse("staff-hackathon-detail", args=[h.slug])
        assert staff_client.delete(url).status_code == 204
        assert not Hackathon.objects.filter(pk=h.pk).exists()


@pytest.mark.django_db
class TestStaffSubmissions:
    def test_muddatgacha_ham_hammasi_korinadi(self, staff_client, user, other_user) -> None:
        """Ommaviy API muddatgacha faqat o'zinikini beradi; staff — hammasini."""
        h = _open_hackathon()
        submit(user, h, **ENTRY)
        submit(other_user, h, **{**ENTRY, "title": "Boshqa"})
        assert h.accepts_submissions
        body = staff_client.get(reverse("staff-hackathon-submissions", args=[h.slug])).json()
        assert sorted(e["username"] for e in body["results"]) == ["aziz", "bekzod"]
        assert body["results"][0]["scored_by"] is None

    def test_baholash(self, staff_client, staff, user) -> None:
        h = _open_hackathon()
        entry = submit(user, h, **ENTRY)
        url = reverse("staff-hackathon-score-entry", args=[h.slug, entry.pk])
        res = staff_client.post(url, {"score": 88, "feedback": "zo'r"}, format="json")
        assert res.status_code == 200, res.json()
        assert res.json()["score"] == 88
        assert res.json()["scored_by"] == staff.username
        entry.refresh_from_db()
        assert entry.score == 88 and entry.feedback == "zo'r" and entry.scored_by == staff

    def test_baho_oraligi(self, staff_client, user) -> None:
        h = _open_hackathon()
        entry = submit(user, h, **ENTRY)
        url = reverse("staff-hackathon-score-entry", args=[h.slug, entry.pk])
        assert staff_client.post(url, {"score": 101}, format="json").status_code == 400
        assert staff_client.post(url, {"score": -1}, format="json").status_code == 400

    def test_begona_hakaton_loyihasi_404(self, staff_client, user) -> None:
        """Entry boshqa hakatonga tegishli bo'lsa, slug orqali topilmaydi."""
        h1 = _open_hackathon("h1")
        h2 = _open_hackathon("h2")
        entry = submit(user, h1, **ENTRY)
        url = reverse("staff-hackathon-score-entry", args=[h2.slug, entry.pk])
        assert staff_client.post(url, {"score": 10}, format="json").status_code == 404
        assert HackathonSubmission.objects.get(pk=entry.pk).score is None
