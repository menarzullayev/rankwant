"""Staff API — musobaqalar (admin UI)."""

from __future__ import annotations

from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from contests.models import Contest, ContestProblem, Standing
from core.models import User
from judging.models import Attempt
from judging.verdicts import Verdict


@pytest.fixture
def staff_user(db) -> User:
    return User.objects.create_user("staff1", password="x", is_staff=True)


@pytest.fixture
def staff(staff_user) -> APIClient:
    c = APIClient()
    c.force_authenticate(user=staff_user)
    return c


def _payload(**overrides):
    now = timezone.now()
    base = {
        "slug": "round-2",
        "title": "Round 2",
        "description": "tavsif",
        "start_at": (now + timedelta(days=1)).isoformat(),
        "end_at": (now + timedelta(days=1, hours=2)).isoformat(),
        "freeze_minutes": 30,
        "scoring_type": "acm",
        "is_rated": True,
        "is_virtual": False,
        "is_public": False,
        "mirror_of": None,
    }
    base.update(overrides)
    return base


@pytest.mark.django_db
class TestStaffContestAccess:
    def test_anonim_kira_olmaydi(self, contest) -> None:
        r = APIClient().get(reverse("staff-contest-list"))
        assert r.status_code in (401, 403)

    def test_oddiy_foydalanuvchi_403(self, user, contest) -> None:
        c = APIClient()
        c.force_authenticate(user=user)
        assert c.get(reverse("staff-contest-list")).status_code == 403
        assert c.post(reverse("staff-contest-list"), _payload(), format="json").status_code == 403
        assert c.post(reverse("staff-contest-finalize", args=[contest.slug])).status_code == 403
        assert (
            c.post(reverse("staff-contest-rebuild-standings", args=[contest.slug])).status_code
            == 403
        )
        assert (
            c.put(
                reverse("staff-contest-problems", args=[contest.slug]), [], format="json"
            ).status_code
            == 403
        )

    def test_ommaviy_api_ozgarmaydi(self, contest) -> None:
        """Public serializer maxfiy maydonlarni oshkor qilmaydi."""
        body = APIClient().get(reverse("contest-detail", args=[contest.slug])).json()
        assert "is_public" not in body
        assert "mirror_of" not in body
        assert "ratings_applied_at" not in body


@pytest.mark.django_db
class TestStaffContestCrud:
    def test_royxat_yopiq_musobaqani_ham_koradi(self, staff, contest) -> None:
        contest.is_public = False
        contest.save(update_fields=["is_public"])
        body = staff.get(reverse("staff-contest-list")).json()
        assert body["count"] == 1
        row = body["results"][0]
        assert row["slug"] == contest.slug
        assert row["is_public"] is False
        assert row["problems"][0]["problem"] == "a-plus-b"
        assert row["problems"][0]["index_letter"] == "A"

    def test_qidiruv(self, staff, contest) -> None:
        assert staff.get(reverse("staff-contest-list"), {"search": "round"}).json()["count"] == 1
        assert staff.get(reverse("staff-contest-list"), {"search": "yoq"}).json()["count"] == 0

    def test_yaratish(self, staff, contest) -> None:
        r = staff.post(
            reverse("staff-contest-list"), _payload(mirror_of=contest.slug), format="json"
        )
        assert r.status_code == 201, r.json()
        body = r.json()
        assert body["mirror_of"] == contest.slug
        assert body["freeze_minutes"] == 30
        assert body["is_public"] is False
        created = Contest.objects.get(slug="round-2")
        assert created.mirror_of == contest
        assert created.is_rated is True

    def test_tugash_boshlanishdan_oldin_rad(self, staff) -> None:
        now = timezone.now()
        r = staff.post(
            reverse("staff-contest-list"),
            _payload(start_at=now.isoformat(), end_at=(now - timedelta(hours=1)).isoformat()),
            format="json",
        )
        assert r.status_code == 400
        assert "end_at" in r.json()["error"]["details"]

    def test_ozini_kozgusi_rad(self, staff, contest) -> None:
        r = staff.patch(
            reverse("staff-contest-detail", args=[contest.slug]),
            {"mirror_of": contest.slug},
            format="json",
        )
        assert r.status_code == 400
        assert "mirror_of" in r.json()["error"]["details"]

    def test_korish(self, staff, contest) -> None:
        body = staff.get(reverse("staff-contest-detail", args=[contest.slug])).json()
        assert body["title"] == "Round 1"
        assert body["is_finished"] is True
        assert body["ratings_applied_at"] is None

    def test_tahrirlash(self, staff, contest) -> None:
        r = staff.patch(
            reverse("staff-contest-detail", args=[contest.slug]),
            {"title": "Round 1 (yangi)", "scoring_type": "ioi", "is_public": False},
            format="json",
        )
        assert r.status_code == 200, r.json()
        contest.refresh_from_db()
        assert contest.title == "Round 1 (yangi)"
        assert contest.scoring_type == "ioi"
        assert contest.is_public is False

    def test_ochirish(self, staff, contest) -> None:
        r = staff.delete(reverse("staff-contest-detail", args=[contest.slug]))
        assert r.status_code == 204
        assert not Contest.objects.filter(slug=contest.slug).exists()


@pytest.mark.django_db
class TestStaffContestProblems:
    def test_get_joriy_royxat(self, staff, contest) -> None:
        body = staff.get(reverse("staff-contest-problems", args=[contest.slug])).json()
        assert body == [{"problem": "a-plus-b", "index_letter": "A", "points": 100, "title": "A+B"}]

    def test_put_toliq_almashtiradi(self, staff, contest, hard_problem) -> None:
        r = staff.put(
            reverse("staff-contest-problems", args=[contest.slug]),
            [{"problem": hard_problem.slug, "index_letter": "B", "points": 200}],
            format="json",
        )
        assert r.status_code == 200, r.json()
        assert [(p["problem"], p["index_letter"], p["points"]) for p in r.json()] == [
            ("hard-one", "B", 200)
        ]
        # Eski "A" qatori o'chdi — bu qisman yangilash emas, to'liq almashtirish
        assert list(
            ContestProblem.objects.filter(contest=contest).values_list("index_letter", flat=True)
        ) == ["B"]

    def test_post_va_obyekt_korinishi(self, staff, contest, problem, hard_problem) -> None:
        r = staff.post(
            reverse("staff-contest-problems", args=[contest.slug]),
            {
                "problems": [
                    {"problem": problem.slug, "index_letter": "A"},
                    {"problem": hard_problem.slug, "index_letter": "B"},
                ]
            },
            format="json",
        )
        assert r.status_code == 200, r.json()
        assert [p["index_letter"] for p in r.json()] == ["A", "B"]
        assert r.json()[0]["points"] == 100  # standart ball

    def test_bosh_royxat_hammasini_ochiradi(self, staff, contest) -> None:
        r = staff.put(reverse("staff-contest-problems", args=[contest.slug]), [], format="json")
        assert r.status_code == 200
        assert r.json() == []
        assert not ContestProblem.objects.filter(contest=contest).exists()

    def test_notogri_slug_rad(self, staff, contest) -> None:
        r = staff.put(
            reverse("staff-contest-problems", args=[contest.slug]),
            [{"problem": "yoq-masala", "index_letter": "A"}],
            format="json",
        )
        assert r.status_code == 400
        assert ContestProblem.objects.filter(contest=contest).count() == 1  # o'zgarmadi

    def test_takror_harf_rad(self, staff, contest, problem, hard_problem) -> None:
        r = staff.put(
            reverse("staff-contest-problems", args=[contest.slug]),
            [
                {"problem": problem.slug, "index_letter": "A"},
                {"problem": hard_problem.slug, "index_letter": "A"},
            ],
            format="json",
        )
        assert r.status_code == 400
        assert "problems" in r.json()["error"]["details"]

    def test_takror_masala_rad(self, staff, contest, problem) -> None:
        r = staff.put(
            reverse("staff-contest-problems", args=[contest.slug]),
            [
                {"problem": problem.slug, "index_letter": "A"},
                {"problem": problem.slug, "index_letter": "B"},
            ],
            format="json",
        )
        assert r.status_code == 400


@pytest.mark.django_db
class TestStaffContestActions:
    def test_rebuild_standings(self, staff, contest, problem, user, language) -> None:
        attempt = Attempt.objects.create(
            user=user,
            problem=problem,
            language=language,
            source_code="x",
            contest=contest,
            verdict=Verdict.AC,
        )
        Attempt.objects.filter(pk=attempt.pk).update(
            created_at=contest.start_at + timedelta(minutes=10)
        )

        r = staff.post(reverse("staff-contest-rebuild-standings", args=[contest.slug]))
        assert r.status_code == 200
        assert r.json() == {"rows": 1}
        row = Standing.objects.get(contest=contest, user=user)
        assert row.solved_count == 1
        assert row.penalty == 10

    def test_rebuild_bosh_musobaqa(self, staff, contest) -> None:
        ContestProblem.objects.filter(contest=contest).delete()
        r = staff.post(reverse("staff-contest-rebuild-standings", args=[contest.slug]))
        assert r.status_code == 200
        assert r.json() == {"rows": 0}

    def test_finalize_tugagan_musobaqa(self, staff, contest) -> None:
        r = staff.post(reverse("staff-contest-finalize", args=[contest.slug]))
        assert r.status_code == 200
        # Ishtirokchi kam — reyting hisoblanmadi, lekin musobaqa yakunlangan deb belgilandi
        assert r.json()["affected"] == 0
        assert r.json()["ratings_applied_at"] is not None
        contest.refresh_from_db()
        assert contest.ratings_applied_at is not None

    def test_finalize_ikki_marta_zararsiz(self, staff, contest) -> None:
        staff.post(reverse("staff-contest-finalize", args=[contest.slug]))
        contest.refresh_from_db()
        first = contest.ratings_applied_at
        r = staff.post(reverse("staff-contest-finalize", args=[contest.slug]))
        assert r.json()["affected"] == 0
        contest.refresh_from_db()
        assert contest.ratings_applied_at == first

    def test_finalize_tugamagan_musobaqa(self, staff, contest) -> None:
        contest.end_at = timezone.now() + timedelta(hours=1)
        contest.save(update_fields=["end_at"])
        r = staff.post(reverse("staff-contest-finalize", args=[contest.slug]))
        assert r.status_code == 200
        assert r.json() == {"affected": 0, "ratings_applied_at": None}
