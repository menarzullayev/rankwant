"""Staff API — chempionat boshqaruvi (admin UI)."""

from __future__ import annotations

from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from contests.models import Contest, Standing
from core.models import User
from tournaments.models import Tournament, TournamentStage, TournamentStanding


def _contest(slug: str) -> Contest:
    now = timezone.now()
    return Contest.objects.create(
        slug=slug, title=slug, start_at=now - timedelta(hours=3), end_at=now - timedelta(hours=1)
    )


def _payload(**extra) -> dict:
    now = timezone.now()
    body = {
        "slug": "mavsum-1",
        "title": "Mavsum 1",
        "description": "**Chempionat**",
        "start_at": now.isoformat(),
        "end_at": (now + timedelta(days=30)).isoformat(),
        "is_public": False,
    }
    body.update(extra)
    return body


@pytest.fixture
def staff_client(db) -> APIClient:
    staff = User.objects.create_user("staff1", password="x", is_staff=True)
    c = APIClient()
    c.force_authenticate(user=staff)
    return c


@pytest.fixture
def tournament(db) -> Tournament:
    return Tournament.objects.create(
        slug="mavsum-1",
        title="Mavsum 1",
        start_at=timezone.now() - timedelta(days=1),
        end_at=timezone.now() + timedelta(days=30),
    )


@pytest.mark.django_db
class TestStaffTournamentAccess:
    def test_anonim_kira_olmaydi(self, tournament) -> None:
        anon = APIClient()
        assert anon.get(reverse("staff-tournament-list")).status_code in (401, 403)
        assert anon.post(
            reverse("staff-tournament-list"), _payload(), format="json"
        ).status_code in (
            401,
            403,
        )
        assert anon.post(
            reverse("staff-tournament-rebuild", args=[tournament.slug])
        ).status_code in (401, 403)

    def test_oddiy_foydalanuvchi_403(self, user, tournament) -> None:
        c = APIClient()
        c.force_authenticate(user=user)
        assert c.get(reverse("staff-tournament-list")).status_code == 403
        assert (
            c.post(reverse("staff-tournament-list"), _payload(), format="json").status_code == 403
        )
        assert (
            c.patch(
                reverse("staff-tournament-detail", args=[tournament.slug]), {"title": "X"}
            ).status_code
            == 403
        )
        assert (
            c.delete(reverse("staff-tournament-detail", args=[tournament.slug])).status_code == 403
        )
        assert (
            c.post(reverse("staff-tournament-rebuild", args=[tournament.slug])).status_code == 403
        )

    def test_ommaviy_api_ozgarmaydi(self, tournament) -> None:
        """Yopiq chempionat ommaviy ro'yxatda ko'rinmaydi; staff esa ko'radi."""
        tournament.is_public = False
        tournament.save()
        assert APIClient().get(reverse("tournament-list")).json()["count"] == 0


@pytest.mark.django_db
class TestStaffTournamentCrud:
    def test_yaratish_bosqichlar_bilan(self, staff_client) -> None:
        c1, c2 = _contest("bosqich-1"), _contest("final")
        r = staff_client.post(
            reverse("staff-tournament-list"),
            _payload(
                stages=[
                    {"order": 2, "title": "Final", "contest": "final", "weight": 2},
                    {"order": 1, "title": "1-bosqich", "contest": "bosqich-1"},
                ]
            ),
            format="json",
        )
        assert r.status_code == 201, r.json()
        body = r.json()
        assert body["slug"] == "mavsum-1"
        assert body["is_public"] is False
        assert body["stage_count"] == 2
        assert [s["contest"] for s in body["stages"]] == ["bosqich-1", "final"]
        assert body["stages"][1]["weight"] == 2
        assert body["stages"][0]["weight"] == 1  # default
        assert c1.tournament_stage.tournament.slug == "mavsum-1"
        assert c2.tournament_stage.order == 2

    def test_royxat_va_qidiruv(self, staff_client, tournament) -> None:
        Tournament.objects.create(
            slug="boshqa", title="Boshqa", start_at=timezone.now(), end_at=timezone.now()
        )
        assert staff_client.get(reverse("staff-tournament-list")).json()["count"] == 2
        r = staff_client.get(reverse("staff-tournament-list"), {"search": "mavsum"})
        assert [x["slug"] for x in r.json()["results"]] == ["mavsum-1"]

    def test_korish(self, staff_client, tournament) -> None:
        TournamentStage.objects.create(
            tournament=tournament, order=1, title="A", contest=_contest("c-a")
        )
        body = staff_client.get(reverse("staff-tournament-detail", args=["mavsum-1"])).json()
        assert body["stages"] == [
            {"order": 1, "title": "A", "contest": "c-a", "contest_title": "c-a", "weight": 1}
        ]

    def test_tahrirlash_bosqichlarga_tegmaydi(self, staff_client, tournament) -> None:
        TournamentStage.objects.create(
            tournament=tournament, order=1, title="A", contest=_contest("c-a")
        )
        r = staff_client.patch(
            reverse("staff-tournament-detail", args=["mavsum-1"]),
            {"title": "Yangi nom", "is_public": False},
            format="json",
        )
        assert r.status_code == 200, r.json()
        tournament.refresh_from_db()
        assert tournament.title == "Yangi nom"
        assert tournament.is_public is False
        assert tournament.stages.count() == 1

    def test_bosqichlarni_almashtirish(self, staff_client, tournament) -> None:
        old = _contest("eski")
        TournamentStage.objects.create(tournament=tournament, order=1, title="Eski", contest=old)
        _contest("yangi-1"), _contest("yangi-2")
        r = staff_client.patch(
            reverse("staff-tournament-detail", args=["mavsum-1"]),
            {
                "stages": [
                    {"order": 1, "title": "Y1", "contest": "yangi-1", "weight": 1},
                    {"order": 2, "title": "Y2", "contest": "yangi-2", "weight": 3},
                ]
            },
            format="json",
        )
        assert r.status_code == 200, r.json()
        assert list(tournament.stages.values_list("contest__slug", "weight")) == [
            ("yangi-1", 1),
            ("yangi-2", 3),
        ]
        assert not TournamentStage.objects.filter(contest=old).exists()
        assert Contest.objects.filter(pk=old.pk).exists()  # PROTECT: contest o'chmaydi

    def test_bosqichlarni_boshatish(self, staff_client, tournament) -> None:
        TournamentStage.objects.create(
            tournament=tournament, order=1, title="A", contest=_contest("c-a")
        )
        r = staff_client.patch(
            reverse("staff-tournament-detail", args=["mavsum-1"]), {"stages": []}, format="json"
        )
        assert r.status_code == 200
        assert tournament.stages.count() == 0

    def test_ozining_bosqichini_qayta_tartiblash(self, staff_client, tournament) -> None:
        """O'z contestini qayta yuborish OneToOne xatosi bermasligi kerak."""
        _contest("c-a")
        TournamentStage.objects.create(
            tournament=tournament, order=1, title="A", contest=Contest.objects.get(slug="c-a")
        )
        r = staff_client.patch(
            reverse("staff-tournament-detail", args=["mavsum-1"]),
            {"stages": [{"order": 5, "title": "A5", "contest": "c-a", "weight": 2}]},
            format="json",
        )
        assert r.status_code == 200, r.json()
        stage = tournament.stages.get()
        assert (stage.order, stage.title, stage.weight) == (5, "A5", 2)

    def test_boshqa_chempionat_bosqichi_rad_etiladi(self, staff_client, tournament) -> None:
        busy = _contest("band")
        other = Tournament.objects.create(
            slug="boshqa", title="Boshqa", start_at=timezone.now(), end_at=timezone.now()
        )
        TournamentStage.objects.create(tournament=other, order=1, title="X", contest=busy)
        r = staff_client.patch(
            reverse("staff-tournament-detail", args=["mavsum-1"]),
            {"stages": [{"order": 1, "title": "A", "contest": "band"}]},
            format="json",
        )
        assert r.status_code == 400
        err = r.json()["error"]
        assert err["code"] == "invalid"
        assert "band → boshqa" in err["details"]["stages"][0]
        assert tournament.stages.count() == 0

    def test_takror_tartib_va_contest_rad_etiladi(self, staff_client, tournament) -> None:
        _contest("c-a"), _contest("c-b")
        url = reverse("staff-tournament-detail", args=["mavsum-1"])
        r = staff_client.patch(
            url,
            {
                "stages": [
                    {"order": 1, "title": "A", "contest": "c-a"},
                    {"order": 1, "title": "B", "contest": "c-b"},
                ]
            },
            format="json",
        )
        assert r.status_code == 400 and "stages" in r.json()["error"]["details"]
        r = staff_client.patch(
            url,
            {
                "stages": [
                    {"order": 1, "title": "A", "contest": "c-a"},
                    {"order": 2, "title": "B", "contest": "c-a"},
                ]
            },
            format="json",
        )
        assert r.status_code == 400 and "stages" in r.json()["error"]["details"]

    def test_notogri_contest_slug(self, staff_client) -> None:
        r = staff_client.post(
            reverse("staff-tournament-list"),
            _payload(stages=[{"order": 1, "title": "A", "contest": "yoq"}]),
            format="json",
        )
        assert r.status_code == 400
        assert not Tournament.objects.filter(slug="mavsum-1").exists()  # atomic

    def test_vaqt_tekshiruvi(self, staff_client) -> None:
        now = timezone.now()
        r = staff_client.post(
            reverse("staff-tournament-list"),
            _payload(start_at=now.isoformat(), end_at=(now - timedelta(days=1)).isoformat()),
            format="json",
        )
        assert r.status_code == 400
        assert "end_at" in r.json()["error"]["details"]

    def test_ochirish(self, staff_client, tournament) -> None:
        contest = _contest("c-a")
        TournamentStage.objects.create(tournament=tournament, order=1, title="A", contest=contest)
        r = staff_client.delete(reverse("staff-tournament-detail", args=["mavsum-1"]))
        assert r.status_code == 204
        assert not Tournament.objects.filter(slug="mavsum-1").exists()
        assert not TournamentStage.objects.exists()
        assert Contest.objects.filter(pk=contest.pk).exists()


@pytest.mark.django_db
class TestStaffTournamentRebuild:
    def test_rebuild(self, staff_client, tournament, user, other_user) -> None:
        c1 = _contest("bosqich-1")
        TournamentStage.objects.create(tournament=tournament, order=1, title="1", contest=c1)
        Standing.objects.create(contest=c1, user=user, rank=1, solved_count=3)
        Standing.objects.create(contest=c1, user=other_user, rank=2, solved_count=1)

        r = staff_client.post(reverse("staff-tournament-rebuild", args=["mavsum-1"]))
        assert r.status_code == 200
        assert r.json() == {"participants": 2}
        assert TournamentStanding.objects.get(tournament=tournament, user=user).rank == 1

    def test_rebuild_bosh(self, staff_client, tournament) -> None:
        r = staff_client.post(reverse("staff-tournament-rebuild", args=["mavsum-1"]))
        assert r.status_code == 200
        assert r.json() == {"participants": 0}

    def test_rebuild_yoq_chempionat_404(self, staff_client) -> None:
        assert (
            staff_client.post(reverse("staff-tournament-rebuild", args=["yoq"])).status_code == 404
        )
