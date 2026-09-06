"""Chempionat — bosqichlar yig'indisi, formula ochiq."""

from __future__ import annotations

from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from contests.models import Contest, Standing
from tournaments.models import Tournament, TournamentStage, TournamentStanding
from tournaments.services import rebuild, stage_points


def _contest(slug: str, hours_ago: int) -> Contest:
    now = timezone.now()
    return Contest.objects.create(
        slug=slug,
        title=slug,
        start_at=now - timedelta(hours=hours_ago + 2),
        end_at=now - timedelta(hours=hours_ago),
    )


@pytest.fixture
def championship(db, user, other_user) -> Tournament:
    t = Tournament.objects.create(
        slug="mavsum-1",
        title="Mavsum 1",
        start_at=timezone.now() - timedelta(days=1),
        end_at=timezone.now() + timedelta(days=30),
    )
    c1, c2 = _contest("bosqich-1", 10), _contest("final", 5)
    TournamentStage.objects.create(tournament=t, order=1, title="1-bosqich", contest=c1)
    TournamentStage.objects.create(tournament=t, order=2, title="Final", contest=c2, weight=2)
    # 1-bosqich: user 1-o'rin, other 2-o'rin (2 ishtirokchi)
    Standing.objects.create(contest=c1, user=user, rank=1, solved_count=3, penalty=10)
    Standing.objects.create(contest=c1, user=other_user, rank=2, solved_count=2, penalty=20)
    # Final: other 1-o'rin, user 2-o'rin
    Standing.objects.create(contest=c2, user=other_user, rank=1, solved_count=4, penalty=10)
    Standing.objects.create(contest=c2, user=user, rank=2, solved_count=3, penalty=30)
    return t


@pytest.mark.django_db
class TestTournament:
    def test_formula(self) -> None:
        assert stage_points(weight=1, participants=10, rank=1) == 10
        assert stage_points(weight=1, participants=10, rank=10) == 1
        assert stage_points(weight=2, participants=10, rank=1) == 20

    def test_yigma_jadval(self, championship, user, other_user) -> None:
        assert rebuild(championship) == 2
        rows = list(TournamentStanding.objects.filter(tournament=championship))
        # user: 1×2 + 2×1 = 4;  other: 1×1 + 2×2 = 5 → final og'irroq, other yutadi
        by_user = {r.user_id: r for r in rows}
        assert by_user[other_user.pk].points == 5 and by_user[other_user.pk].rank == 1
        assert by_user[user.pk].points == 4 and by_user[user.pk].rank == 2
        assert by_user[user.pk].solved_total == 6

    def test_contest_yakunlanganda_jadval_yangilanadi(self, championship) -> None:
        from contests.services import finalize_contest

        c = championship.stages.get(order=2).contest
        finalize_contest(c)
        assert TournamentStanding.objects.filter(tournament=championship).count() == 2

    def test_api(self, championship) -> None:
        rebuild(championship)
        c = APIClient()
        assert c.get(reverse("tournament-list")).json()["results"][0]["stage_count"] == 2
        detail = c.get(reverse("tournament-detail", args=[championship.slug])).json()
        assert [s["title"] for s in detail["stages"]] == ["1-bosqich", "Final"]
        rows = c.get(reverse("tournament-standings", args=[championship.slug])).json()["results"]
        assert rows[0]["rank"] == 1 and rows[0]["points"] == 5
