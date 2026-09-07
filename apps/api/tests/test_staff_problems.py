"""Staff API — masala/mavzu CRUD va test yuklash (admin UI yuzasi)."""

from __future__ import annotations

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from core.models import User
from problems import storage
from problems.models import Problem, Topic
from problems.models import TestCase as ProblemTestCase


@pytest.fixture
def staff_user(db) -> User:
    return User.objects.create_user("staff1", password="x", is_staff=True)


@pytest.fixture
def staff_client(staff_user) -> APIClient:
    client = APIClient()
    client.force_authenticate(staff_user)
    return client


@pytest.fixture
def fake_s3(monkeypatch) -> dict[str, str]:
    """MinIO unit testda yo'q — yuklashni yozib boradigan soxta bilan almashtiramiz."""
    uploaded: dict[str, str] = {}

    def put(key: str, content: str) -> str:
        uploaded[key] = content
        return f"s3://rankwant/{key}"

    monkeypatch.setattr(storage, "ensure_bucket", lambda: None)
    monkeypatch.setattr(storage, "put_test_data", put)
    return uploaded


PAYLOAD = {
    "slug": "yangi-masala",
    "title": "Yangi masala",
    "statement": "## Matn\n\nMarkdown",
    "difficulty": 1200,
    "topics": [],
    "time_limit_ms": 2000,
    "memory_limit_kb": 131072,
    "checker_type": "standard",
    "is_public": False,
}


@pytest.mark.django_db
class TestRuxsat:
    def test_anonim_kirolmaydi(self, problem) -> None:
        client = APIClient()
        assert client.get(reverse("staff-problem-list")).status_code in (401, 403)
        assert client.get(reverse("staff-topic-list")).status_code in (401, 403)
        assert client.get(reverse("staff-problem-tests", args=[problem.slug])).status_code in (
            401,
            403,
        )

    def test_oddiy_foydalanuvchi_403(self, user, problem) -> None:
        client = APIClient()
        client.force_authenticate(user)
        assert client.get(reverse("staff-problem-list")).status_code == 403
        assert client.post(reverse("staff-problem-list"), PAYLOAD, format="json").status_code == 403
        assert client.get(reverse("staff-topic-list")).status_code == 403
        assert (
            client.post(
                reverse("staff-problem-tests", args=[problem.slug]),
                {"order": 1, "input": "1\n", "expected": "1\n"},
                format="json",
            ).status_code
            == 403
        )

    def test_ommaviy_api_ozgarmagan(self, problem) -> None:
        """Ommaviy masala API si yashirin masala va staff maydonlarini ko'rsatmaydi."""
        Problem.objects.create(slug="yashirin", title="Y", statement="…", difficulty=800)
        body = APIClient().get(reverse("problem-list")).json()
        assert [p["slug"] for p in body["results"]] == [problem.slug]
        detail = APIClient().get(reverse("problem-detail", args=[problem.slug])).json()
        assert "interactor_source" not in detail
        assert "is_public" not in detail


@pytest.mark.django_db
class TestProblemCrud:
    def test_royxat_yashirinni_ham_koradi(self, staff_client, problem) -> None:
        Problem.objects.create(slug="yashirin", title="Y", statement="…", difficulty=800)
        body = staff_client.get(reverse("staff-problem-list")).json()
        assert body["count"] == 2
        assert {"test_count", "is_public", "interactor_source"} <= set(body["results"][0])

    def test_qidiruv(self, staff_client, problem, hard_problem) -> None:
        body = staff_client.get(reverse("staff-problem-list"), {"search": "hard"}).json()
        assert [p["slug"] for p in body["results"]] == [hard_problem.slug]

    def test_yaratish_mavzu_va_til_bilan(self, staff_client, language) -> None:
        Topic.objects.create(slug="dp", name_uz="DP")
        payload = {
            **PAYLOAD,
            "topics": ["dp"],
            "checker_type": "interactive",
            "interactor_source": "int main(){}",
            "interactor_language": language.code,
        }
        res = staff_client.post(reverse("staff-problem-list"), payload, format="json")
        assert res.status_code == 201, res.json()
        body = res.json()
        assert body["topics"] == ["dp"]
        assert body["interactor_language"] == language.code
        assert body["test_count"] == 0
        problem = Problem.objects.get(slug="yangi-masala")
        assert problem.interactor_language == language
        assert list(problem.topics.values_list("slug", flat=True)) == ["dp"]

    def test_notogri_mavzu_400(self, staff_client) -> None:
        res = staff_client.post(
            reverse("staff-problem-list"), {**PAYLOAD, "topics": ["yoq"]}, format="json"
        )
        assert res.status_code == 400
        assert "topics" in res.json()["error"]["details"]

    def test_qiyinlik_qadam_va_chegara(self, staff_client) -> None:
        for bad in (1250, 700, 3600):
            res = staff_client.post(
                reverse("staff-problem-list"), {**PAYLOAD, "difficulty": bad}, format="json"
            )
            assert res.status_code == 400, bad
            assert "difficulty" in res.json()["error"]["details"]

    def test_tahrirlash(self, staff_client, problem) -> None:
        res = staff_client.patch(
            reverse("staff-problem-detail", args=[problem.slug]),
            {"title": "A + B", "is_public": False, "interactor_language": None},
            format="json",
        )
        assert res.status_code == 200, res.json()
        problem.refresh_from_db()
        assert problem.title == "A + B"
        assert problem.is_public is False
        assert problem.interactor_language is None

    def test_ochirish(self, staff_client, problem) -> None:
        res = staff_client.delete(reverse("staff-problem-detail", args=[problem.slug]))
        assert res.status_code == 204
        assert not Problem.objects.filter(pk=problem.pk).exists()


@pytest.mark.django_db
class TestTopicCrud:
    def test_crud(self, staff_client) -> None:
        url = reverse("staff-topic-list")
        res = staff_client.post(url, {"slug": "graflar", "name_uz": "Graflar"}, format="json")
        assert res.status_code == 201, res.json()
        res = staff_client.post(
            url, {"slug": "dfs", "name_uz": "DFS", "parent": "graflar"}, format="json"
        )
        assert res.status_code == 201, res.json()
        assert res.json()["parent"] == "graflar"
        assert Topic.objects.get(slug="dfs").parent == Topic.objects.get(slug="graflar")

        assert staff_client.get(url).json()["count"] == 2
        res = staff_client.patch(
            reverse("staff-topic-detail", args=["dfs"]), {"name_ru": "Поиск"}, format="json"
        )
        assert res.status_code == 200
        assert Topic.objects.get(slug="dfs").name_ru == "Поиск"

        assert staff_client.delete(reverse("staff-topic-detail", args=["dfs"])).status_code == 204
        assert not Topic.objects.filter(slug="dfs").exists()


@pytest.mark.django_db
class TestTestCases:
    """Bu slice'ning yadrosi — avval masala tuzuvchilar test yuklay olmasdi."""

    def test_yuklash_s3_va_db(self, staff_client, problem, fake_s3) -> None:
        url = reverse("staff-problem-tests", args=[problem.slug])
        res = staff_client.post(
            url,
            {"order": 1, "input": "1 2\n", "expected": "3\n", "is_sample": True, "points": 10},
            format="json",
        )
        assert res.status_code == 201, res.json()
        body = res.json()
        assert body["order"] == 1
        assert body["is_sample"] is True
        assert body["points"] == 10
        assert body["input_ref"] == "s3://rankwant/tests/a-plus-b/1.in"
        assert body["output_ref"] == "s3://rankwant/tests/a-plus-b/1.out"

        # Matn aynan yuborilgandek yozilishi shart — oxirgi \n judge uchun muhim.
        assert fake_s3["tests/a-plus-b/1.in"] == "1 2\n"
        assert fake_s3["tests/a-plus-b/1.out"] == "3\n"
        assert ProblemTestCase.objects.get(problem=problem, order=1).input_ref.startswith("s3://")

    def test_qayta_yuklash_yangilaydi(self, staff_client, problem, fake_s3) -> None:
        url = reverse("staff-problem-tests", args=[problem.slug])
        staff_client.post(url, {"order": 2, "input": "a", "expected": "b"}, format="json")
        res = staff_client.post(
            url, {"order": 2, "input": "x", "expected": "y", "points": 5}, format="json"
        )
        assert res.status_code == 200
        assert ProblemTestCase.objects.filter(problem=problem, order=2).count() == 1
        assert ProblemTestCase.objects.get(problem=problem, order=2).points == 5
        assert fake_s3["tests/a-plus-b/2.in"] == "x"

    def test_royxat_tartibda(self, staff_client, problem, fake_s3) -> None:
        url = reverse("staff-problem-tests", args=[problem.slug])
        staff_client.post(url, {"order": 3, "input": "", "expected": ""}, format="json")
        staff_client.post(url, {"order": 1, "input": "", "expected": ""}, format="json")
        body = staff_client.get(url).json()
        assert [t["order"] for t in body] == [1, 3]
        assert {"order", "is_sample", "points", "input_ref", "output_ref"} <= set(body[0])

        detail = staff_client.get(reverse("staff-problem-detail", args=[problem.slug])).json()
        assert detail["test_count"] == 2

    def test_notogri_kiritish_400(self, staff_client, problem, fake_s3) -> None:
        url = reverse("staff-problem-tests", args=[problem.slug])
        res = staff_client.post(url, {"order": 0, "input": "a", "expected": "b"}, format="json")
        assert res.status_code == 400
        assert "order" in res.json()["error"]["details"]
        res = staff_client.post(url, {"order": 1, "input": "a"}, format="json")
        assert res.status_code == 400
        assert "expected" in res.json()["error"]["details"]
        assert not fake_s3

    def test_ochirish(self, staff_client, problem, fake_s3) -> None:
        url = reverse("staff-problem-tests", args=[problem.slug])
        staff_client.post(url, {"order": 1, "input": "a", "expected": "b"}, format="json")
        del_url = reverse("staff-problem-delete-test", args=[problem.slug, 1])
        assert staff_client.delete(del_url).status_code == 204
        assert not ProblemTestCase.objects.filter(problem=problem).exists()
        assert staff_client.delete(del_url).status_code == 404

    def test_yoq_masala_404(self, staff_client, fake_s3) -> None:
        res = staff_client.post(
            reverse("staff-problem-tests", args=["yoq"]),
            {"order": 1, "input": "a", "expected": "b"},
            format="json",
        )
        assert res.status_code == 404
        assert not fake_s3
