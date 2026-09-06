"""Contest, ACM standings va Contests reytingi."""

from __future__ import annotations

from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from contests.models import Contest, ContestProblem, Standing
from contests.services import WRONG_ATTEMPT_PENALTY_MIN, finalize_contest, rebuild_standings
from core.models import User
from judging.models import Attempt
from judging.verdicts import Verdict
from ratings.models import RatingHistory


def submit(user, contest, problem, language, verdict, minutes_in):
    a = Attempt.objects.create(
        user=user,
        problem=problem,
        contest=contest,
        language=language,
        source_code="x",
        verdict=verdict,
    )
    Attempt.objects.filter(pk=a.pk).update(
        created_at=contest.start_at + timedelta(minutes=minutes_in)
    )
    a.refresh_from_db()
    return a


@pytest.mark.django_db
class TestStandings:
    def test_yechganlar_soni_ustun(self, contest, problem, language, user, other_user) -> None:
        third = User.objects.create_user(username="dilnoza", password="Parol!12345")
        p2 = type(problem).objects.create(
            slug="b", title="B", statement="…", difficulty=1200, is_public=True
        )
        ContestProblem.objects.create(contest=contest, problem=p2, index_letter="B")

        submit(user, contest, problem, language, Verdict.AC, 10)
        submit(user, contest, p2, language, Verdict.AC, 20)
        submit(other_user, contest, problem, language, Verdict.AC, 5)
        submit(third, contest, problem, language, Verdict.WA, 5)

        assert rebuild_standings(contest) == 3
        rows = list(Standing.objects.filter(contest=contest).order_by("rank"))
        assert rows[0].user_id == user.pk and rows[0].solved_count == 2
        assert rows[1].user_id == other_user.pk and rows[1].solved_count == 1
        assert rows[2].solved_count == 0

    def test_penalty_hisobi(self, contest, problem, language, user) -> None:
        """Penalty = AC vaqti + 20 × noto'g'ri urinishlar."""
        submit(user, contest, problem, language, Verdict.WA, 5)
        submit(user, contest, problem, language, Verdict.TLE, 8)
        submit(user, contest, problem, language, Verdict.AC, 30)
        rebuild_standings(contest)
        standing = Standing.objects.get(contest=contest, user=user)
        assert standing.penalty == 30 + 2 * WRONG_ATTEMPT_PENALTY_MIN

    def test_ce_penalty_bermaydi(self, contest, problem, language, user) -> None:
        submit(user, contest, problem, language, Verdict.CE, 3)
        submit(user, contest, problem, language, Verdict.AC, 10)
        rebuild_standings(contest)
        assert Standing.objects.get(contest=contest, user=user).penalty == 10

    def test_ac_dan_keyingi_urinish_penalty_bermaydi(
        self, contest, problem, language, user
    ) -> None:
        submit(user, contest, problem, language, Verdict.AC, 10)
        submit(user, contest, problem, language, Verdict.WA, 20)
        rebuild_standings(contest)
        assert Standing.objects.get(contest=contest, user=user).penalty == 10


@pytest.mark.django_db
class TestContestRating:
    def _ten_participants(self, contest, problem, language):
        users = []
        for i in range(10):
            u = User.objects.create_user(username=f"u{i}", password="Parol!12345")
            submit(u, contest, problem, language, Verdict.AC, 5 + i)
            users.append(u)
        return users

    def test_kam_ishtirokchi_reyting_bermaydi(self, contest, problem, language, user) -> None:
        """ADR-0006: >= 10 ishtirokchi sharti."""
        submit(user, contest, problem, language, Verdict.AC, 10)
        assert finalize_contest(contest) == 0
        user.refresh_from_db()
        assert user.rating_contest == 1400

    def test_reyting_hisoblanadi(self, contest, problem, language) -> None:
        users = self._ten_participants(contest, problem, language)
        assert finalize_contest(contest) == 10

        for u in users:
            u.refresh_from_db()
        # Birinchi o'rin yutadi, oxirgisi yo'qotadi
        assert users[0].rating_contest > 1400
        assert users[-1].rating_contest < 1400
        # Har birida audit yozuvi
        assert RatingHistory.objects.filter(rating_type="contest").count() == 10
        entry = RatingHistory.objects.filter(user=users[0], rating_type="contest").first()
        assert entry is not None and entry.rank == 1 and entry.seed is not None

    def test_ikki_marta_hisoblanmaydi(self, contest, problem, language) -> None:
        self._ten_participants(contest, problem, language)
        finalize_contest(contest)
        contest.refresh_from_db()
        assert finalize_contest(contest) == 0

    def test_unrated_contest(self, contest, problem, language) -> None:
        contest.is_rated = False
        contest.save()
        self._ten_participants(contest, problem, language)
        assert finalize_contest(contest) == 0

    def test_tugamagan_contest_yakunlanmaydi(self, problem, language) -> None:
        now = timezone.now()
        running = Contest.objects.create(
            slug="live",
            title="Live",
            start_at=now - timedelta(minutes=5),
            end_at=now + timedelta(hours=1),
            is_rated=True,
        )
        assert finalize_contest(running) == 0


@pytest.mark.django_db
class TestContestApi:
    def test_royxat_va_standings(self, contest, problem, language, user) -> None:
        submit(user, contest, problem, language, Verdict.AC, 10)
        rebuild_standings(contest)
        c = APIClient()
        assert c.get(reverse("contest-list")).status_code == 200
        body = c.get(reverse("contest-standings", args=[contest.slug])).json()
        assert body["results"][0]["username"] == user.username
        assert body["frozen"] is False

    def test_royxatdan_otish(self, problem, user) -> None:
        now = timezone.now()
        upcoming = Contest.objects.create(
            slug="kelasi",
            title="Kelasi",
            start_at=now + timedelta(hours=1),
            end_at=now + timedelta(hours=3),
        )
        c = APIClient()
        c.force_authenticate(user=user)
        assert c.post(reverse("contest-register", args=[upcoming.slug])).status_code == 201
        assert c.post(reverse("contest-register", args=[upcoming.slug])).status_code == 200

    def test_tugagan_contestga_royxatdan_otib_bolmaydi(self, contest, user) -> None:
        c = APIClient()
        c.force_authenticate(user=user)
        r = c.post(reverse("contest-register", args=[contest.slug]))
        assert r.status_code == 400
        assert r.json()["error"]["code"] == "contest_finished"

    def test_freeze_bayrogi(self, problem, language) -> None:
        now = timezone.now()
        frozen = Contest.objects.create(
            slug="muzlagan",
            title="Muzlagan",
            start_at=now - timedelta(hours=2),
            end_at=now + timedelta(minutes=10),
            freeze_minutes=30,
        )
        assert frozen.is_frozen is True


@pytest.mark.django_db
class TestVirtualContest:
    """PRD P1-1 — virtual ishtirok."""

    def test_tugagan_contestda_boshlash(self, contest, user) -> None:
        from contests.services import start_virtual, virtual_deadline

        reg = start_virtual(contest, user)
        assert reg.virtual_start_at is not None
        expected = contest.end_at - contest.start_at
        assert virtual_deadline(reg) - reg.virtual_start_at == expected

    def test_ketayotgan_contestda_boshlab_bolmaydi(self, problem, user) -> None:
        from contests.services import start_virtual

        now = timezone.now()
        running = Contest.objects.create(
            slug="live2",
            title="Live",
            start_at=now - timedelta(minutes=5),
            end_at=now + timedelta(hours=1),
        )
        with pytest.raises(ValueError):
            start_virtual(running, user)

    def test_ikki_marta_boshlanmaydi(self, contest, user) -> None:
        from contests.services import start_virtual

        first = start_virtual(contest, user).virtual_start_at
        assert start_virtual(contest, user).virtual_start_at == first

    def test_virtual_rasmiy_jadvalga_kirmaydi(
        self, contest, problem, language, user, other_user
    ) -> None:
        """Virtual ishtirokchi javoblarni bilib turib yechadi — uning
        natijasi rasmiy jadvalga va reytingga TUSHMASLIGI kerak."""
        from contests.services import rebuild_standings, start_virtual

        submit(other_user, contest, problem, language, Verdict.AC, 10)
        start_virtual(contest, user)
        submit(user, contest, problem, language, Verdict.AC, 5)

        rebuild_standings(contest)
        usernames = set(
            Standing.objects.filter(contest=contest).values_list("user__username", flat=True)
        )
        assert other_user.username in usernames
        assert user.username not in usernames

    def test_api_endpointi(self, contest, user) -> None:
        c = APIClient()
        c.force_authenticate(user=user)
        r = c.post(reverse("contest-virtual", args=[contest.slug]))
        assert r.status_code == 201
        assert r.json()["virtual_start_at"] is not None

    def test_ketayotgan_contestda_api_400(self, problem, user) -> None:
        now = timezone.now()
        running = Contest.objects.create(
            slug="live3",
            title="Live",
            start_at=now - timedelta(minutes=5),
            end_at=now + timedelta(hours=1),
        )
        c = APIClient()
        c.force_authenticate(user=user)
        r = c.post(reverse("contest-virtual", args=[running.slug]))
        assert r.status_code == 400
        assert r.json()["error"]["code"] == "not_finished"
