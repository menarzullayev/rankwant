"""O'z o'qish kontenti (P2-5) va o'qituvchi sinfi (P2-2)."""

from __future__ import annotations

from datetime import timedelta

import pytest
from django.core.management import call_command
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from classroom.models import Assignment, Classroom, ClassroomMember
from classroom.services import ClassroomError, assignment_progress, join
from content.models import Article, ArticleProblemLink, Roadmap, RoadmapStep
from judging.models import Attempt
from judging.services import apply_result
from problems import storage
from problems.models import TestCase as ProblemTestCase


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


@pytest.mark.django_db
class TestClassroomAuthorization:
    """Fon xavfsizlik tekshiruvi topgan ikkita nuqson uchun regressiya.

    Ikkalasi ham `get_queryset` a'zolarni ham qaytargani, ruxsat esa
    alohida tekshirilmagani sababli yuzaga kelgan edi.
    """

    def _client(self, user) -> APIClient:
        c = APIClient()
        c.force_authenticate(user=user)
        return c

    def test_oquvchi_sinfni_ochira_olmaydi(self, user, other_user) -> None:
        room = Classroom.objects.create(name="9-A", slug="9a", owner=user)
        join(other_user, room.join_code)
        r = self._client(other_user).delete(reverse("classroom-detail", args=["9a"]))
        assert r.status_code == 404
        assert Classroom.objects.filter(slug="9a").exists()

    def test_oquvchi_sinfni_ozgartira_olmaydi(self, user, other_user) -> None:
        room = Classroom.objects.create(name="9-A", slug="9a", owner=user)
        join(other_user, room.join_code)
        r = self._client(other_user).patch(
            reverse("classroom-detail", args=["9a"]), {"name": "Meniki"}
        )
        assert r.status_code == 404
        room.refresh_from_db()
        assert room.name == "9-A"

    def test_egasi_ozgartira_oladi(self, user) -> None:
        Classroom.objects.create(name="9-A", slug="9a", owner=user)
        r = self._client(user).patch(reverse("classroom-detail", args=["9a"]), {"name": "9-B"})
        assert r.status_code == 200

    def test_oquvchi_join_code_ni_kormaydi(self, user, other_user) -> None:
        """Kod bilan istalgan odam sinfga qo'shila oladi."""
        room = Classroom.objects.create(name="9-A", slug="9a", owner=user)
        join(other_user, room.join_code)
        body = self._client(other_user).get(reverse("classroom-detail", args=["9a"])).json()
        assert "join_code" not in body
        assert "members" not in body

    def test_egasi_join_code_ni_koradi(self, user, other_user) -> None:
        room = Classroom.objects.create(name="9-A", slug="9a", owner=user)
        join(other_user, room.join_code)
        body = self._client(user).get(reverse("classroom-detail", args=["9a"])).json()
        assert body["join_code"] == room.join_code
        assert len(body["members"]) == 1

    def test_begona_sinfga_kira_olmaydi(self, user, other_user) -> None:
        Classroom.objects.create(name="9-A", slug="9a", owner=user)
        assert (
            self._client(other_user).get(reverse("classroom-detail", args=["9a"])).status_code
            == 404
        )


@pytest.mark.django_db
class TestSeedDemo:
    """seed_demo — local ishga tushirishning birinchi qadami.

    Sinaladi, chunki buzilgan seed yangi ishlab chiquvchi uchun bo'sh
    `/learn` va `/classroom` degani, va buni faqat qo'lda ochib ko'rish
    orqali bilib bo'lardi.
    """

    @pytest.fixture(autouse=True)
    def _fake_s3(self, monkeypatch):
        """MinIO unit testda yo'q — yuklashni yozib boradigan soxta bilan almashtiramiz."""
        self.uploaded: dict[str, str] = {}

        def put(key: str, content: str) -> str:
            self.uploaded[key] = content
            return f"s3://rankwant/{key}"

        monkeypatch.setattr(storage, "ensure_bucket", lambda: None)
        monkeypatch.setattr(storage, "put_test_data", put)

    def test_seed_ishlaydi_va_takrorlanadi(self) -> None:
        call_command("seed_demo", verbosity=0)
        call_command("seed_demo", verbosity=0)  # idempotent

        assert Article.objects.filter(is_published=True, kind=Article.Kind.ARTICLE).count() == 3
        assert RoadmapStep.objects.count() == 5
        classroom = Classroom.objects.get(slug="11-a-sinf")
        assert classroom.members.count() == 3
        assert classroom.assignments.get().problems.count() == 3

        from arena.models import ArenaRound
        from duels.models import Duel
        from hackathons.models import Hackathon
        from quizzes.models import Quiz
        from tournaments.models import Tournament

        assert Quiz.objects.get(slug="algoritm-asoslari").items.count() == 4
        assert ArenaRound.objects.get(slug="demo-arena").items.count() == 4
        assert Tournament.objects.get(slug="demo-mavsum").stages.count() == 2
        assert Hackathon.objects.get(slug="demo-hakaton").accepts_submissions
        assert Duel.objects.filter(status=Duel.Status.OPEN).count() == 1  # idempotent
        assert Article.objects.filter(kind=Article.Kind.ALGORITHM).count() == 1

    def test_standart_holatda_jonli_oyna_yoq(self) -> None:
        """Standart seed jonli contest/arena yaratmaydi.

        ⚠️ Regressiya (2026-09-24). `deploy.yml` ning `Demo data` qadami
        bu buyruqni HAR deploy'da yurgizadi. Oyna jonli bo'lsa
        `tools/check_deploy_window.py` uni «faol contest» deb ko'radi
        (`core/mixins.py`: `start_at <= now < end_at`) va KEYINGI
        deploy'ni qoida №1 bo'yicha to'xtatadi — ya'ni har deploy o'zidan
        keyingisini bloklaydi. O'lchandi:

            run 35966889156 — deploy to'xtadi:
            ✗ contest «demo-round-1» — 2026-09-24T13:52:30+05:00 gacha
        """
        from arena.models import ArenaRound
        from contests.models import Contest

        call_command("seed_demo", verbosity=0)

        contest = Contest.objects.get(slug="demo-round-1")
        assert not contest.is_running, "demo contest jonli — keyingi deploy bloklanadi"
        assert contest.is_finished

        arena = ArenaRound.objects.get(slug="demo-arena")
        assert not arena.is_running, "demo arena jonli — keyingi deploy bloklanadi"
        assert arena.is_finished

    def test_live_bayrog_i_jonli_oyna_beradi(self) -> None:
        """`--live` — demo ko'rsatish uchun ataylab yoqiladigan jonli oyna."""
        from arena.models import ArenaRound
        from contests.models import Contest

        call_command("seed_demo", verbosity=0, live=True)

        assert Contest.objects.get(slug="demo-round-1").is_running

        # ⚠️ Arena `now + 3 daqiqa` da boshlanadi (izoh: «jonli sinab
        # ko'rish uchun»), ya'ni hozir YURMAYDI — lekin tugagan ham emas.
        # `is_running` `start_at <= now < end_at` (`core/mixins.py`).
        arena = ArenaRound.objects.get(slug="demo-arena")
        assert not arena.is_running
        assert not arena.is_finished

    def test_testlar_haqiqiy_S3_ga_yuklanadi(self) -> None:
        """Test ma'lumoti mavjud bo'lmasa to'g'ri yechim ham WA oladi."""
        call_command("seed_demo", verbosity=0)

        assert self.uploaded["tests/a-plus-b/1.in"] == "1 2\n"
        assert self.uploaded["tests/a-plus-b/1.out"] == "3\n"
        first = ProblemTestCase.objects.get(problem__slug="a-plus-b", order=1)
        assert first.input_ref.startswith("s3://")

    def test_testsiz_masalada_soxta_ref_yoq(self) -> None:
        """Yozilmagan masalaga soxta test qo'yilsa, u har doim WA berardi."""
        call_command("seed_demo", verbosity=0)
        assert not ProblemTestCase.objects.filter(problem__slug="ryukzak").exists()

    def test_roadmap_qadamlari_toliq(self) -> None:
        """Har qadamda maqola ham, masala ham bo'lishi kerak."""
        call_command("seed_demo", verbosity=0)
        for step in RoadmapStep.objects.all():
            assert step.article is not None
            assert step.problem is not None


def test_traektoriya_progressi_yechilgan_masalalardan(db, user, problem) -> None:
    """Alohida progress modeli yo'q — qadam masalasi yechilganmi, shundan."""
    from content.models import Roadmap, RoadmapStep
    from ratings.models import UserSolvedProblem

    roadmap = Roadmap.objects.create(slug="yol", title="Yo'l", is_published=True)
    RoadmapStep.objects.create(roadmap=roadmap, order=1, problem=problem)
    RoadmapStep.objects.create(roadmap=roadmap, order=2, title="Faqat maqola")

    client = APIClient()
    assert client.get(reverse("roadmap-list")).data[0]["solved_steps"] == 0

    client.force_authenticate(user)
    assert client.get(reverse("roadmap-list")).data[0]["solved_steps"] == 0

    UserSolvedProblem.objects.create(
        user=user, problem=problem, difficulty_at_solve=problem.difficulty
    )
    assert client.get(reverse("roadmap-list")).data[0]["solved_steps"] == 1
