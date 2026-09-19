"""Rollar — staff guruhlari va obyekt mualliflari (ADR-0025, qaror 23).

Har guruh FAQAT o'z bo'lagini oladi: support — xabar, content — katalog
va blog, ops — Qvant/bloklash/testlar. Bare `is_staff` (guruhsiz) — faqat
O'QISH. Superuser bypass. Tashqi rollar: organizator (`contests/mine/`) va
muallif (`problems/mine/`) — nashr ikkalasida ham staff-ops qo'li.
"""

from __future__ import annotations

from datetime import timedelta

import pytest
from django.contrib.auth.models import Group
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from core.models import User
from problems.models import TestCase as ProblemTestCase


def _client(user: User) -> APIClient:
    c = APIClient()
    c.force_authenticate(user=user)
    return c


@pytest.fixture(autouse=True)
def _no_auto_staff_groups():
    """Bu modul guruh bo'linishini tekshiradi — avtomatik guruh berish
    (conftest signal) bu yerda O'CHIRILADI, guruhlar qo'lda biriktiriladi."""
    from django.db.models.signals import post_save

    from tests.conftest import _auto_grant_staff_groups

    post_save.disconnect(_auto_grant_staff_groups, sender=User)
    yield
    post_save.connect(_auto_grant_staff_groups, sender=User)


def _staff(name: str, *groups: str) -> User:
    user = User.objects.create_user(name, password="x", is_staff=True)
    for group in groups:
        user.groups.add(Group.objects.get(name=group))
    return user


@pytest.fixture
def target(db) -> User:
    """Guruh a'zolari ustida ishlaydigan oddiy foydalanuvchi."""
    return User.objects.create_user("nur", password="x")


@pytest.fixture
def fake_problem_s3(monkeypatch) -> dict[str, str]:
    """MinIO yo'q — test yuklashni xotiraga yozadigan soxta (storage)."""
    from problems import storage

    uploaded: dict[str, str] = {}

    def put(key: str, content: str) -> str:
        uploaded[key] = content
        return f"s3://rankwant/{key}"

    monkeypatch.setattr(storage, "ensure_bucket", lambda: None)
    monkeypatch.setattr(storage, "put_test_data", put)
    return uploaded


# ── Guruh bo'linishi: kim nimani oladi ──────────────────────────────────


@pytest.fixture
def bare_staff(db) -> User:
    return User.objects.create_user("bare1", password="x", is_staff=True)


@pytest.mark.django_db
class TestGuruhBohlinishi:
    def test_bare_staff_faqat_oqish(self, bare_staff, target) -> None:
        c = _client(bare_staff)
        assert c.get(reverse("staff-user-list")).status_code == 200
        # Yozish amallari — hammasi 403: bare is_staff monoliti qaytmasin.
        assert (
            c.patch(reverse("staff-user-detail", args=[target.username]), {"bio": "x"}).status_code
            == 403
        )
        assert (
            c.post(
                reverse("staff-user-qvant", args=[target.username]), {"amount": 10, "note": "t"}
            ).status_code
            == 403
        )
        assert (
            c.post(
                reverse("staff-user-notify", args=[target.username]), {"title": "t", "body": "b"}
            ).status_code
            == 403
        )
        assert c.post(reverse("staff-school-list"), {"name": "1-maktab"}).status_code == 403
        assert c.get(reverse("staff-analytics")).status_code == 403

    def test_support_xabar_yuboradi_boshqani_yoq(self, target) -> None:
        c = _client(_staff("sup1", "staff-support"))
        assert (
            c.post(
                reverse("staff-user-notify", args=[target.username]), {"title": "t", "body": "b"}
            ).status_code
            == 201
        )
        assert (
            c.post(reverse("staff-user-broadcast"), {"title": "t", "body": "b"}).status_code == 201
        )
        assert (
            c.post(
                reverse("staff-user-qvant", args=[target.username]), {"amount": 10, "note": "t"}
            ).status_code
            == 403
        )
        assert (
            c.patch(reverse("staff-user-detail", args=[target.username]), {"bio": "x"}).status_code
            == 403
        )
        assert c.post(reverse("staff-school-list"), {"name": "1-maktab"}).status_code == 403

    def test_content_katalog_blog_yozadi_usersni_yoq(self) -> None:
        c = _client(_staff("cont1", "staff-content"))
        assert c.post(reverse("staff-school-list"), {"name": "5-maktab"}).status_code == 201
        assert (
            c.post(
                reverse("staff-post-list"),
                {"slug": "xabar", "title": "Xabar", "body": "Matn", "kind": "news"},
                format="json",
            ).status_code
            == 201
        )
        assert c.get(reverse("staff-analytics")).status_code == 403

    def test_ops_qvant_bloklash_qiladi_blogni_yoq(self, target) -> None:
        c = _client(_staff("ops1", "staff-ops"))
        assert (
            c.post(
                reverse("staff-user-qvant", args=[target.username]),
                {"amount": 50, "note": "sovg'a"},
            ).status_code
            == 200
        )
        assert (
            c.patch(
                reverse("staff-user-detail", args=[target.username]), {"bio": "salom"}
            ).status_code
            == 200
        )
        assert (
            c.post(
                reverse("staff-user-notify", args=[target.username]), {"title": "t", "body": "b"}
            ).status_code
            == 201
        )
        assert c.get(reverse("staff-analytics")).status_code == 200
        # Blog/katalog — content guruhining ishi.
        assert c.post(reverse("staff-school-list"), {"name": "9-maktab"}).status_code == 403

    def test_superuser_bypass(self, target) -> None:
        boss = User.objects.create_user("boss", password="x", is_staff=True, is_superuser=True)
        c = _client(boss)
        assert (
            c.post(
                reverse("staff-user-qvant", args=[target.username]), {"amount": 10, "note": "t"}
            ).status_code
            == 200
        )
        assert c.post(reverse("staff-school-list"), {"name": "3-maktab"}).status_code == 201


# ── T-1: Organizator (`contests/mine/`) ─────────────────────────────────


@pytest.mark.django_db
class TestOrganizator:
    payload = {
        "slug": "maktab-kubogi",
        "title": "Maktab kubogi",
        "description": "Bahor kubogi",
        "start_at": (timezone.now() + timedelta(days=7)).isoformat(),
        "end_at": (timezone.now() + timedelta(days=7, hours=2)).isoformat(),
    }

    def test_draft_yaratiladi(self, user) -> None:
        c = _client(user)
        res = c.post(reverse("mine-contest-list"), self.payload, format="json")
        assert res.status_code == 201, res.content
        body = res.json()
        assert body["is_public"] is False
        assert body["is_rated"] is False
        contest = user.organized_contests.get(slug="maktab-kubogi")
        assert list(contest.organizers.all()) == [user]

    def test_faqat_o_zi(self, user, other_user) -> None:
        c = _client(user)
        c.post(reverse("mine-contest-list"), self.payload, format="json")
        other = _client(other_user)
        assert other.get(reverse("mine-contest-list")).json()["results"] == []
        assert other.get(reverse("mine-contest-detail", args=["maktab-kubogi"])).status_code == 404

    def test_nashr_ochirilmaydi(self, user) -> None:
        c = _client(user)
        c.post(reverse("mine-contest-list"), self.payload, format="json")
        # Nashr — staff-ops; organizator o'zi nashr qila olmaydi.
        ops = _client(_staff("ops2", "staff-ops"))
        assert (
            ops.patch(
                reverse("staff-contest-detail", args=["maktab-kubogi"]), {"is_public": True}
            ).status_code
            == 200
        )
        assert c.delete(reverse("mine-contest-detail", args=["maktab-kubogi"])).status_code == 403


# ── T-2: Masala muallifi (`problems/mine/`) ─────────────────────────────


@pytest.mark.django_db
class TestMuallif:
    def test_draft_yaratiladi(self, user) -> None:
        c = _client(user)
        body = c.post(
            reverse("mine-problem-list"),
            {"slug": "yigindi", "title": "Yig'indi", "statement": "a+b", "difficulty": 800},
            format="json",
        ).json()
        assert body["is_public"] is False
        problem = user.authored_problems.get(slug="yigindi")
        assert list(problem.authors.all()) == [user]

    def test_muallif_oz_editorialini_koradi(self, user, other_user) -> None:
        from problems.models import Problem

        problem = Problem.objects.create(
            slug="o-z-masalasi",
            title="O'z masalasi",
            statement="s",
            difficulty=800,
            editorial="maxfiy yechim",
            editorial_price=30,
            is_public=True,
        )
        problem.authors.add(user)
        mine = _client(user).get(reverse("problem-detail", args=[problem.slug])).json()
        other = _client(other_user).get(reverse("problem-detail", args=[problem.slug])).json()
        assert mine["editorial_state"]["access"] == "staff"
        assert mine["editorial"] == "maxfiy yechim"
        assert other["editorial_state"]["access"] == "locked"
        assert other["editorial"] == ""

    def test_muallif_draft_testini_yuklaydi(self, user, fake_problem_s3) -> None:
        c = _client(user)
        c.post(
            reverse("mine-problem-list"),
            {"slug": "draft-test", "title": "D", "statement": "s", "difficulty": 800},
            format="json",
        )
        url = reverse("staff-problem-tests", args=["draft-test"])
        res = c.post(url, {"order": 1, "input": "1 2", "expected": "3"}, format="json")
        assert res.status_code == 201
        assert ProblemTestCase.objects.get(problem__slug="draft-test", order=1)

    def test_muallif_nashr_masala_testiga_kirolmaydi(self, user, problem) -> None:
        # Nashr qilingan masala — xodim nazoratida (muallifga ham yo'q).
        c = _client(user)
        assert c.get(reverse("staff-problem-tests", args=[problem.slug])).status_code == 403
        ops = _client(_staff("ops3", "staff-ops"))
        assert ops.get(reverse("staff-problem-tests", args=[problem.slug])).status_code == 200
