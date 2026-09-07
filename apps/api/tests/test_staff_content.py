"""Staff kontent API — `staff/articles/`, `staff/roadmaps/` (admin UI)."""

from __future__ import annotations

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from content.models import Article, ArticleProblemLink, Roadmap, RoadmapStep
from core.models import User
from problems.models import Topic


@pytest.fixture
def staff(db) -> User:
    return User.objects.create_user("staff1", password="x", is_staff=True)


@pytest.fixture
def staff_client(staff) -> APIClient:
    c = APIClient()
    c.force_authenticate(user=staff)
    return c


@pytest.fixture
def article(db) -> Article:
    return Article.objects.create(slug="dp", title="Dinamik dasturlash", body="matn")


@pytest.mark.django_db
class TestStaffAccess:
    @pytest.mark.parametrize("name", ["staff-article-list", "staff-roadmap-list"])
    def test_anonim_kira_olmaydi(self, name) -> None:
        assert APIClient().get(reverse(name)).status_code in (401, 403)

    @pytest.mark.parametrize("name", ["staff-article-list", "staff-roadmap-list"])
    def test_oddiy_foydalanuvchi_kira_olmaydi(self, user, name) -> None:
        c = APIClient()
        c.force_authenticate(user=user)
        assert c.get(reverse(name)).status_code == 403
        assert c.post(reverse(name), {"slug": "x", "title": "X"}, format="json").status_code == 403

    def test_ommaviy_api_ozgarmaydi(self, article) -> None:
        """Nashr qilinmagan maqola ommaviy ro'yxatda hali ham ko'rinmaydi."""
        assert APIClient().get(reverse("article-list")).json()["count"] == 0


@pytest.mark.django_db
class TestStaffArticle:
    def test_royxat_nashr_qilinmaganini_ham_koradi(self, staff_client, article) -> None:
        body = staff_client.get(reverse("staff-article-list")).json()
        assert body["count"] == 1
        assert body["results"][0]["slug"] == "dp"
        assert body["results"][0]["is_published"] is False

    def test_yaratish(self, staff_client, staff, problem) -> None:
        Topic.objects.create(slug="dp", name_uz="DP")
        r = staff_client.post(
            reverse("staff-article-list"),
            {
                "slug": "yangi",
                "kind": "algorithm",
                "title": "Yangi",
                "summary": "qisqa",
                "body": "# Matn",
                "locale": "uz",
                "difficulty": 1200,
                "topics": ["dp"],
                "is_published": True,
                "problems": [{"problem": problem.slug, "role": "practice", "order": 1}],
            },
            format="json",
        )
        assert r.status_code == 201, r.json()
        data = r.json()
        assert data["kind"] == "algorithm"
        assert data["topics"] == ["dp"]
        assert data["author"] == staff.username
        assert data["published_at"] is not None
        assert data["reading_minutes"] >= 1  # model avtomatik hisoblaydi
        assert data["problems"] == [{"problem": problem.slug, "role": "practice", "order": 1}]

    def test_yaratish_notogri_topic(self, staff_client) -> None:
        r = staff_client.post(
            reverse("staff-article-list"),
            {"slug": "x", "title": "X", "body": "x", "topics": ["yoq"]},
            format="json",
        )
        assert r.status_code == 400
        assert "topics" in r.json()["error"]["details"]

    def test_tahrirlash(self, staff_client, article) -> None:
        r = staff_client.patch(
            reverse("staff-article-detail", args=["dp"]),
            {"title": "Yangi nom", "is_published": True},
            format="json",
        )
        assert r.status_code == 200
        article.refresh_from_db()
        assert article.title == "Yangi nom"
        assert article.is_published is True
        assert article.published_at is not None

    def test_masala_boglanishlari_almashtiriladi(
        self, staff_client, article, problem, hard_problem
    ) -> None:
        ArticleProblemLink.objects.create(article=article, problem=problem, role="practice")
        url = reverse("staff-article-detail", args=["dp"])
        r = staff_client.patch(
            url,
            {
                "problems": [
                    {"problem": hard_problem.slug, "role": "editorial", "order": 2},
                    {"problem": problem.slug, "role": "example", "order": 1},
                ]
            },
            format="json",
        )
        assert r.status_code == 200, r.json()
        assert [(p["problem"], p["role"]) for p in r.json()["problems"]] == [
            (problem.slug, "example"),
            (hard_problem.slug, "editorial"),
        ]
        assert article.problem_links.count() == 2

        # Bo'sh ro'yxat — hammasi o'chadi; ro'yxat yuborilmasa — tegilmaydi
        assert staff_client.patch(url, {"problems": []}, format="json").status_code == 200
        assert article.problem_links.count() == 0
        staff_client.patch(url, {"summary": "s"}, format="json")
        assert article.problem_links.count() == 0

    def test_takror_boglanish_rad_etiladi(self, staff_client, article, problem) -> None:
        r = staff_client.patch(
            reverse("staff-article-detail", args=["dp"]),
            {
                "problems": [
                    {"problem": problem.slug, "role": "practice", "order": 1},
                    {"problem": problem.slug, "role": "practice", "order": 2},
                ]
            },
            format="json",
        )
        assert r.status_code == 400
        assert "problems" in r.json()["error"]["details"]

    def test_notogri_masala_slugi(self, staff_client, article) -> None:
        r = staff_client.patch(
            reverse("staff-article-detail", args=["dp"]),
            {"problems": [{"problem": "yoq", "role": "practice", "order": 1}]},
            format="json",
        )
        assert r.status_code == 400

    def test_ochirish(self, staff_client, article) -> None:
        r = staff_client.delete(reverse("staff-article-detail", args=["dp"]))
        assert r.status_code == 204
        assert not Article.objects.filter(slug="dp").exists()

    def test_qidiruv(self, staff_client, article) -> None:
        Article.objects.create(slug="graf", title="Graflar", body="x")
        body = staff_client.get(reverse("staff-article-list"), {"search": "graf"}).json()
        assert [a["slug"] for a in body["results"]] == ["graf"]


@pytest.mark.django_db
class TestStaffRoadmap:
    def test_yaratish_qadamlar_bilan(self, staff_client, article, problem) -> None:
        r = staff_client.post(
            reverse("staff-roadmap-list"),
            {
                "slug": "boshlash",
                "title": "Boshlash",
                "description": "d",
                "is_published": True,
                "order": 1,
                "steps": [
                    {"order": 2, "title": "Mashq", "problem": problem.slug},
                    {"order": 1, "title": "O'qish", "article": "dp", "is_optional": True},
                ],
            },
            format="json",
        )
        assert r.status_code == 201, r.json()
        steps = r.json()["steps"]
        assert [s["order"] for s in steps] == [1, 2]
        assert steps[0]["article"] == "dp"
        assert steps[0]["problem"] is None
        assert steps[0]["is_optional"] is True
        assert steps[1]["problem"] == problem.slug
        assert r.json()["step_count"] == 0  # annotatsiya faqat ro'yxat/detail'da

        detail = staff_client.get(reverse("staff-roadmap-detail", args=["boshlash"])).json()
        assert detail["step_count"] == 2

    def test_bosh_qadam_rad_etiladi(self, staff_client) -> None:
        r = staff_client.post(
            reverse("staff-roadmap-list"),
            {"slug": "r", "title": "R", "steps": [{"order": 1, "title": "Bo'sh"}]},
            format="json",
        )
        assert r.status_code == 400
        assert "steps" in r.json()["error"]["details"]
        assert not Roadmap.objects.filter(slug="r").exists()

    def test_takror_tartib_rad_etiladi(self, staff_client, article) -> None:
        r = staff_client.post(
            reverse("staff-roadmap-list"),
            {
                "slug": "r",
                "title": "R",
                "steps": [
                    {"order": 1, "article": "dp"},
                    {"order": 1, "article": "dp"},
                ],
            },
            format="json",
        )
        assert r.status_code == 400
        assert "steps" in r.json()["error"]["details"]

    def test_qadamlar_almashtiriladi(self, staff_client, article, problem) -> None:
        roadmap = Roadmap.objects.create(slug="r", title="R")
        RoadmapStep.objects.create(roadmap=roadmap, order=1, article=article)
        url = reverse("staff-roadmap-detail", args=["r"])

        r = staff_client.patch(
            url, {"steps": [{"order": 5, "problem": problem.slug}]}, format="json"
        )
        assert r.status_code == 200, r.json()
        assert [(s["order"], s["problem"]) for s in r.json()["steps"]] == [(5, problem.slug)]

        # Qadamlarsiz PATCH — qadamlar saqlanib qoladi
        r = staff_client.patch(url, {"title": "Yangi"}, format="json")
        assert r.status_code == 200
        assert roadmap.steps.count() == 1

    def test_tahrirlash_va_ochirish(self, staff_client) -> None:
        Roadmap.objects.create(slug="r", title="R")
        url = reverse("staff-roadmap-detail", args=["r"])
        r = staff_client.patch(url, {"is_published": True, "order": 3}, format="json")
        assert r.status_code == 200
        assert r.json()["is_published"] is True
        assert staff_client.delete(url).status_code == 204
        assert not Roadmap.objects.filter(slug="r").exists()

    def test_nashr_qilinmagan_royxatda_koradi(self, staff_client) -> None:
        Roadmap.objects.create(slug="q", title="Q")
        body = staff_client.get(reverse("staff-roadmap-list")).json()
        assert body["count"] == 1
        assert APIClient().get(reverse("roadmap-list")).json() == []
