"""Side-menu badges: `/me/nav-badges/` (see `core.nav_badges`)."""

from __future__ import annotations

from datetime import timedelta

import pytest
from django.core.cache import cache
from django.utils import timezone
from rest_framework.test import APIClient

from blog.models import Post
from classroom.models import Assignment, Classroom, ClassroomMember
from contests.models import Contest
from core import nav_badges
from core.models import NavSeen, User
from duels.models import Duel
from problems.models import Problem
from ratings.models import UserSolvedProblem

URL = "/api/v1/me/nav-badges/"
SEEN = "/api/v1/me/nav-badges/seen/"

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def _fresh_cache(monkeypatch: pytest.MonkeyPatch) -> None:
    cache.clear()
    # The real epoch is a calendar date; the tests must not depend on
    # which side of it they run.
    monkeypatch.setattr(nav_badges, "EPOCH", timezone.now() - timedelta(days=10))


@pytest.fixture
def user() -> User:
    # Joined after the feature's epoch, so the join date is the floor.
    account = User.objects.create_user(username="reader", password="x-pass-12345")
    User.objects.filter(pk=account.pk).update(date_joined=timezone.now() - timedelta(days=1))
    account.refresh_from_db()
    return account


@pytest.fixture
def client(user: User) -> APIClient:
    api = APIClient()
    api.force_authenticate(user)
    return api


def badges(api: APIClient) -> dict[str, tuple[str, int]]:
    response = api.get(URL)
    assert response.status_code == 200, response.content
    return {row["section"]: (row["kind"], row["count"]) for row in response.json()["badges"]}


def post(published_at, **extra) -> Post:  # type: ignore[no-untyped-def]
    return Post.objects.create(
        slug=f"post-{Post.objects.count()}",
        title="News",
        body="text",
        is_published=True,
        published_at=published_at,
        **extra,
    )


class TestAccess:
    def test_guest_is_refused(self) -> None:
        assert APIClient().get(URL).status_code in (401, 403)

    def test_nothing_to_show_is_an_empty_list(self, client: APIClient) -> None:
        assert badges(client) == {}

    def test_every_planned_section_is_registered(self) -> None:
        assert nav_badges.sections("todo") == ["classroom", "duels"]
        assert nav_badges.sections("live") == ["arena", "contests", "hackathons", "tournaments"]
        assert nav_badges.sections("unread") == ["blog"]
        assert nav_badges.sections("new") == ["algorithms", "learn", "problems", "quizzes"]


class TestUnread:
    def test_a_post_published_since_the_floor_is_unread(self, client: APIClient) -> None:
        post(timezone.now())
        assert badges(client)["blog"] == ("unread", 1)

    def test_a_post_older_than_the_account_is_not(self, client: APIClient) -> None:
        post(timezone.now() - timedelta(days=30))
        assert "blog" not in badges(client)

    def test_an_unpublished_post_is_not(self, client: APIClient) -> None:
        Post.objects.create(slug="draft", title="Draft", body="x", published_at=timezone.now())
        assert "blog" not in badges(client)

    def test_nothing_before_the_epoch_counts_for_an_old_account(self, user: User) -> None:
        # An account from last year must not open the site to every post
        # ever published.
        User.objects.filter(pk=user.pk).update(date_joined=nav_badges.EPOCH - timedelta(days=400))
        user.refresh_from_db()
        post(nav_badges.EPOCH - timedelta(days=1))
        api = APIClient()
        api.force_authenticate(user)
        assert "blog" not in badges(api)

    def test_opening_the_section_clears_it(self, client: APIClient, user: User) -> None:
        post(timezone.now())
        response = client.post(SEEN, {"section": "blog"}, format="json")
        assert response.status_code == 200
        assert response.json()["badges"] == []
        assert NavSeen.objects.filter(user=user, section="blog").count() == 1
        # The cached answer went with it.
        assert "blog" not in badges(client)

    def test_what_is_published_afterwards_counts_again(self, client: APIClient) -> None:
        post(timezone.now())
        client.post(SEEN, {"section": "blog"}, format="json")
        post(timezone.now() + timedelta(seconds=5))
        cache.clear()
        assert badges(client)["blog"] == ("unread", 1)

    def test_one_users_visit_does_not_clear_anothers(self, client: APIClient) -> None:
        post(timezone.now())
        other = User.objects.create_user(username="other", password="x-pass-12345")
        User.objects.filter(pk=other.pk).update(date_joined=timezone.now() - timedelta(days=1))
        api = APIClient()
        api.force_authenticate(User.objects.get(pk=other.pk))
        api.post(SEEN, {"section": "blog"}, format="json")
        assert badges(client)["blog"] == ("unread", 1)


class TestSeenRefusals:
    def test_a_todo_section_is_not_cleared_by_looking(self, client: APIClient) -> None:
        assert client.post(SEEN, {"section": "duels"}, format="json").status_code == 400

    def test_a_live_section_is_not_cleared_by_looking(self, client: APIClient) -> None:
        assert client.post(SEEN, {"section": "contests"}, format="json").status_code == 400

    def test_an_unknown_section_is_refused(self, client: APIClient, user: User) -> None:
        assert client.post(SEEN, {"section": "nope"}, format="json").status_code == 400
        assert not NavSeen.objects.filter(user=user).exists()


class TestTodo:
    def test_an_open_invitation_waits_for_the_opponent(self, client: APIClient, user: User) -> None:
        rival = User.objects.create_user(username="rival", password="x-pass-12345")
        Duel.objects.create(
            slug="d1", title="Duel", challenger=rival, opponent=user, start_at=timezone.now()
        )
        assert badges(client)["duels"] == ("todo", 1)

    def test_the_challengers_own_duel_is_not_their_todo(
        self, client: APIClient, user: User
    ) -> None:
        rival = User.objects.create_user(username="rival", password="x-pass-12345")
        Duel.objects.create(
            slug="d2", title="Duel", challenger=user, opponent=rival, start_at=timezone.now()
        )
        assert "duels" not in badges(client)

    def test_an_answered_invitation_is_gone(self, client: APIClient, user: User) -> None:
        rival = User.objects.create_user(username="rival", password="x-pass-12345")
        Duel.objects.create(
            slug="d3",
            title="Duel",
            challenger=rival,
            opponent=user,
            start_at=timezone.now(),
            status=Duel.Status.ACCEPTED,
        )
        assert "duels" not in badges(client)

    def _assignment(
        self, user: User, *, due_in: timedelta | None = None
    ) -> tuple[Assignment, Problem]:
        teacher = User.objects.create_user(
            username=f"t{Classroom.objects.count()}", password="x-pass-12345"
        )
        room = Classroom.objects.create(
            name="Class",
            slug=f"c{Classroom.objects.count()}",
            owner=teacher,
            join_code=f"J{Classroom.objects.count():05d}",
        )
        ClassroomMember.objects.create(classroom=room, user=user)
        problem = Problem.objects.create(
            slug=f"p{Problem.objects.count()}", title="Sum", statement="x", difficulty=800
        )
        work = Assignment.objects.create(
            classroom=room,
            title="Homework",
            due_at=None if due_in is None else timezone.now() + due_in,
        )
        work.problems.add(problem)
        return work, problem

    def test_an_unfinished_assignment_waits(self, client: APIClient, user: User) -> None:
        self._assignment(user)
        assert badges(client)["classroom"] == ("todo", 1)

    def test_a_solved_assignment_does_not(self, client: APIClient, user: User) -> None:
        _, problem = self._assignment(user)
        UserSolvedProblem.objects.create(user=user, problem=problem, difficulty_at_solve=800)
        assert "classroom" not in badges(client)

    def test_one_past_its_due_date_does_not(self, client: APIClient, user: User) -> None:
        self._assignment(user, due_in=timedelta(days=-1))
        assert "classroom" not in badges(client)


class TestLive:
    def _contest(self, start: timedelta, end: timedelta, **extra) -> Contest:  # type: ignore[no-untyped-def]
        now = timezone.now()
        return Contest.objects.create(
            slug=f"c{Contest.objects.count()}",
            title="Round",
            start_at=now + start,
            end_at=now + end,
            **extra,
        )

    def test_a_running_contest_is_live(self, client: APIClient) -> None:
        self._contest(timedelta(hours=-1), timedelta(hours=1))
        assert badges(client)["contests"] == ("live", 1)

    def test_a_finished_or_future_one_is_not(self, client: APIClient) -> None:
        self._contest(timedelta(hours=-3), timedelta(hours=-1))
        self._contest(timedelta(hours=1), timedelta(hours=3))
        assert "contests" not in badges(client)

    def test_a_hidden_contest_is_not(self, client: APIClient) -> None:
        self._contest(timedelta(hours=-1), timedelta(hours=1), is_public=False)
        assert "contests" not in badges(client)


class TestResilience:
    def test_one_failing_section_leaves_the_rest(
        self, client: APIClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        post(timezone.now())

        def boom(user: User) -> int:
            raise RuntimeError("down")

        broken = nav_badges.Badge(section="duels", kind="todo", count=boom)
        monkeypatch.setitem(nav_badges._REGISTRY, "duels", broken)
        assert badges(client) == {"blog": ("unread", 1)}

    def test_registering_a_section_twice_is_an_error(self) -> None:
        with pytest.raises(ValueError, match="twice"):
            nav_badges.register(nav_badges.Badge(section="blog", kind="unread", count=lambda s: 0))
