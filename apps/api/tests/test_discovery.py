"""Taqvim, qidiruv va Algoritmlar (Article.kind)."""

from __future__ import annotations

from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from arena.models import ArenaRound
from content.models import Article
from duels.models import Duel
from hackathons.models import Hackathon
from tournaments.models import Tournament


@pytest.mark.django_db
class TestCalendar:
    def test_barcha_turlar_yigiladi(self, user, other_user, contest) -> None:
        now = timezone.now()
        soon = now + timedelta(days=2)
        ArenaRound.objects.create(slug="a", title="Arena", start_at=soon)
        Tournament.objects.create(slug="t", title="Chempionat", start_at=soon, end_at=soon)
        Hackathon.objects.create(
            slug="h", title="Hakaton", start_at=soon, submission_deadline=soon, end_at=soon
        )
        Duel.objects.create(
            challenger=user,
            opponent=other_user,
            status=Duel.Status.ACCEPTED,
            title="Duel",
            start_at=soon,
        )
        kinds = {e["kind"] for e in APIClient().get(reverse("calendar")).json()["results"]}
        assert kinds == {"contest", "arena", "tournament", "hackathon"}  # duel yo'q — mehmon

        c = APIClient()
        c.force_authenticate(user=user)
        kinds = {e["kind"] for e in c.get(reverse("calendar")).json()["results"]}
        assert "duel" in kinds

    def test_oraliq_filtri(self, contest) -> None:
        far = (timezone.now() + timedelta(days=200)).isoformat()
        body = APIClient().get(reverse("calendar"), {"from": far, "to": far}).json()
        assert body["results"] == []


@pytest.mark.django_db
class TestSearch:
    def test_qisqa_sorov_bosh(self) -> None:
        assert APIClient().get(reverse("search"), {"q": "a"}).json()["problems"] == []

    def test_har_turdan(self, user, problem, contest) -> None:
        Article.objects.create(slug="dp", title="Dinamik dasturlash", body="x", is_published=True)
        body = APIClient().get(reverse("search"), {"q": "a+b"}).json()
        assert [p["slug"] for p in body["problems"]] == ["a-plus-b"]
        assert (
            APIClient().get(reverse("search"), {"q": "round"}).json()["contests"][0]["slug"]
            == contest.slug
        )
        assert (
            APIClient().get(reverse("search"), {"q": "dinamik"}).json()["articles"][0]["slug"]
            == "dp"
        )
        users = APIClient().get(reverse("search"), {"q": user.username[:4]}).json()["users"]
        assert users[0]["username"] == user.username


@pytest.mark.django_db
class TestAlgorithms:
    def test_kind_filtri(self) -> None:
        Article.objects.create(slug="m", title="Maqola", body="x", is_published=True)
        Article.objects.create(
            slug="bfs", title="BFS", body="x", is_published=True, kind=Article.Kind.ALGORITHM
        )
        body = APIClient().get(reverse("article-list"), {"kind": "algorithm"}).json()
        assert [a["slug"] for a in body["results"]] == ["bfs"]
        assert body["results"][0]["kind"] == "algorithm"
