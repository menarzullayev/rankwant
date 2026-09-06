"""O'z o'qish kontenti (P2-5) va o'qituvchi sinfi (P2-2)."""

from __future__ import annotations

from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from classroom.models import Assignment, Classroom, ClassroomMember
from classroom.services import ClassroomError, assignment_progress, join
from content.models import Article, ArticleProblemLink, Roadmap, RoadmapStep
from judging.models import Attempt
from judging.services import apply_result


@pytest.mark.django_db
class TestArticle:
    def test_nashr_qilinmagan_korinmaydi(self) -> None:
        Article.objects.create(slug="qoralama", title="Q", body="x")
        assert APIClient().get(reverse("article-list")).json()["count"] == 0

    def test_oqish_vaqti_hisoblanadi(self) -> None:
        article = Article.objects.create(
            slug="uzun", title="Uzun", body=" ".join(["so'z"] * 600), is_published=True
        )
        assert article.reading_minutes == 3

    def test_masala_bogliqligi(self, problem) -> None:
        """Differensiatorning yadrosi: maqola ↔ masala."""
        article = Article.objects.create(
            slug="dp", title="Dinamik dasturlash", body="matn", is_published=True
        )
        ArticleProblemLink.objects.create(
            article=article, problem=problem, role=ArticleProblemLink.Role.PRACTICE
        )
        body = APIClient().get(reverse("article-detail", args=["dp"])).json()
        assert body["problems"][0]["slug"] == problem.slug
        assert body["problems"][0]["role"] == "practice"

    def test_royxatda_matn_yoq(self) -> None:
        Article.objects.create(slug="a", title="A", body="uzun", is_published=True)
        item = APIClient().get(reverse("article-list")).json()["results"][0]
        assert "body" not in item
        assert item["problem_count"] == 0


@pytest.mark.django_db
class TestRoadmap:
    def test_qadamlar_tartibda(self, problem) -> None:
        roadmap = Roadmap.objects.create(slug="boshlash", title="Boshlash", is_published=True)
        article = Article.objects.create(slug="kirish", title="Kirish", body="x", is_published=True)
        RoadmapStep.objects.create(roadmap=roadmap, order=2, problem=problem)
        RoadmapStep.objects.create(roadmap=roadmap, order=1, article=article)

        body = APIClient().get(reverse("roadmap-detail", args=["boshlash"])).json()
        assert [s["order"] for s in body["steps"]] == [1, 2]
        assert body["steps"][0]["article"] == "kirish"
        assert body["steps"][1]["problem"] == problem.slug

    def test_bosh_qadam_rad_etiladi(self) -> None:
        from django.core.exceptions import ValidationError

        roadmap = Roadmap.objects.create(slug="r", title="R")
        step = RoadmapStep(roadmap=roadmap, order=1)
        with pytest.raises(ValidationError):
            step.clean()


@pytest.mark.django_db
class TestClassroom:
    def test_join_code_avtomatik(self, user) -> None:
        c = Classroom.objects.create(name="9-A", slug="9a", owner=user)
        assert len(c.join_code) > 0

    def test_qoshilish(self, user, other_user) -> None:
        c = Classroom.objects.create(name="9-A", slug="9a", owner=user)
        member = join(other_user, c.join_code)
        assert member.classroom == c

    def test_egasi_qoshila_olmaydi(self, user) -> None:
        c = Classroom.objects.create(name="9-A", slug="9a", owner=user)
        with pytest.raises(ClassroomError):
            join(user, c.join_code)

    def test_notogri_kod(self, user) -> None:
        with pytest.raises(ClassroomError):
            join(user, "yoq")

    def test_ikki_marta_qoshilmaydi(self, user, other_user) -> None:
        c = Classroom.objects.create(name="9-A", slug="9a", owner=user)
        join(other_user, c.join_code)
        join(other_user, c.join_code)
        assert ClassroomMember.objects.filter(classroom=c).count() == 1

    def test_progress(self, user, other_user, problem, hard_problem, language) -> None:
        c = Classroom.objects.create(name="9-A", slug="9a", owner=user)
        join(other_user, c.join_code)
        assignment = Assignment.objects.create(classroom=c, title="Uy vazifasi")
        assignment.problems.set([problem, hard_problem])

        attempt = Attempt.objects.create(
            user=other_user, problem=problem, language=language, source_code="x"
        )
        apply_result({"attempt_id": attempt.pk, "verdict": "AC"})

        rows = assignment_progress(assignment)
        assert rows == [{"username": other_user.username, "solved": 1, "total": 2}]

    def test_bosh_vazifa_progressi(self, user, other_user) -> None:
        c = Classroom.objects.create(name="9-A", slug="9a", owner=user)
        join(other_user, c.join_code)
        assignment = Assignment.objects.create(classroom=c, title="Bo'sh")
        assert assignment_progress(assignment) == [
            {"username": other_user.username, "solved": 0, "total": 0}
        ]


@pytest.mark.django_db
class TestClassroomApi:
    def _client(self, user) -> APIClient:
        c = APIClient()
        c.force_authenticate(user=user)
        return c

    def test_yaratish_va_korish(self, user) -> None:
        c = self._client(user)
        r = c.post(reverse("classroom-list"), {"name": "9-A", "slug": "9a"})
        assert r.status_code == 201
        detail = c.get(reverse("classroom-detail", args=["9a"])).json()
        assert detail["join_code"]  # egasi kodni ko'radi

    def test_begona_sinf_korinmaydi(self, user, other_user) -> None:
        Classroom.objects.create(name="9-A", slug="9a", owner=user)
        assert self._client(other_user).get(reverse("classroom-list")).json() == []

    def test_qoshilish_endpointi(self, user, other_user) -> None:
        room = Classroom.objects.create(name="9-A", slug="9a", owner=user)
        r = self._client(other_user).post(reverse("classroom-join"), {"join_code": room.join_code})
        assert r.status_code == 201

    def test_faqat_egasi_vazifa_beradi(self, user, other_user, problem) -> None:
        room = Classroom.objects.create(name="9-A", slug="9a", owner=user)
        join(other_user, room.join_code)
        r = self._client(other_user).post(
            reverse("classroom-assignments", args=["9a"]),
            {"title": "Vazifa", "problems": [problem.slug]},
            format="json",
        )
        assert r.status_code == 403
        assert r.json()["error"]["code"] == "not_owner"

    def test_egasi_vazifa_beradi(self, user, problem) -> None:
        Classroom.objects.create(name="9-A", slug="9a", owner=user)
        r = self._client(user).post(
            reverse("classroom-assignments", args=["9a"]),
            {
                "title": "Vazifa",
                "problems": [problem.slug],
                "due_at": (timezone.now() + timedelta(days=7)).isoformat(),
            },
            format="json",
        )
        assert r.status_code == 201
        assert r.json()["problems"] == [problem.slug]


@pytest.mark.django_db
class TestMirrorContest:
    def test_mirror_masalalarni_kochiradi(self, contest, problem) -> None:
        from contests.services import create_mirror

        mirror = create_mirror(contest, "mirror-1", timezone.now() + timedelta(days=1))
        assert mirror.mirror_of == contest
        assert mirror.problems.count() == contest.problems.count()
        assert mirror.end_at - mirror.start_at == contest.end_at - contest.start_at

    def test_mirror_reytingsiz(self, contest) -> None:
        """Asl ishtirokchilar javoblarni bilishadi — reyting adolatsiz."""
        from contests.services import create_mirror

        assert contest.is_rated is True
        mirror = create_mirror(contest, "mirror-2", timezone.now() + timedelta(days=1))
        assert mirror.is_rated is False
