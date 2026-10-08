"""A contest's problems: closed before it, open by address during it,
in the archive after it (ADR-0055).

The first class is the list of places a problem could show through before
its contest starts. Each is asked the way a visitor would ask it.
"""

from __future__ import annotations

from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from contests.models import Contest, ContestProblem, ContestRegistration
from contests.services import finalize_contest, frozen_windows, release_problems
from core.models import User
from judging.models import Attempt
from judging.verdicts import Verdict
from problems.models import Problem, TestCase

SECRET = "Yashirin shartnoma"


def make_contest(
    *, starts_in: int, lasts: int = 120, freeze: int = 0, slug: str = "kuz-raundi"
) -> Contest:
    """A public contest that starts `starts_in` minutes from now."""
    start = timezone.now() + timedelta(minutes=starts_in)
    return Contest.objects.create(
        slug=slug,
        title="Kuz raundi",
        start_at=start,
        end_at=start + timedelta(minutes=lasts),
        freeze_minutes=freeze,
        is_rated=True,
    )


def held_problem(contest: Contest, slug: str = "maxfiy-masala", letter: str = "A") -> Problem:
    """A problem written for the contest: tested, and not in the archive."""
    problem = Problem.objects.create(
        slug=slug,
        title=SECRET,
        statement="Faqat musobaqada ochiladi.",
        editorial="Yechim: saralang.",
        difficulty=1500,
        is_public=False,
    )
    TestCase.objects.create(
        problem=problem, order=1, input_ref="s3://x/1.in", output_ref="s3://x/1.out"
    )
    ContestProblem.objects.create(contest=contest, problem=problem, index_letter=letter)
    return problem


def attempt(user: User, problem: Problem, contest: Contest, language, verdict: str, at) -> Attempt:
    row = Attempt.objects.create(
        user=user,
        problem=problem,
        contest=contest,
        language=language,
        source_code="x",
        verdict=verdict,
    )
    Attempt.objects.filter(pk=row.pk).update(created_at=at)
    row.refresh_from_db()
    return row


def text_of(response) -> str:
    return str(response.content.decode())


@pytest.mark.django_db
class TestBeforeTheStart:
    """Nothing about the problem leaves the server — not its title, not its slug."""

    @pytest.fixture
    def problem_(self) -> Problem:
        return held_problem(make_contest(starts_in=60))

    def test_the_problem_does_not_open(self, client: APIClient, problem_: Problem) -> None:
        assert client.get(reverse("problem-detail", args=[problem_.slug])).status_code == 404

    def test_a_signed_in_visitor_is_no_different(
        self, client: APIClient, user, problem_: Problem
    ) -> None:
        client.force_login(user)
        assert client.get(reverse("problem-detail", args=[problem_.slug])).status_code == 404

    def test_the_archive_list(self, client: APIClient, problem, problem_: Problem) -> None:
        body = text_of(client.get(reverse("problem-list")))
        assert problem.slug in body  # the control: the archive itself answers
        assert problem_.slug not in body and SECRET not in body

    def test_the_archive_search(self, client: APIClient, problem_: Problem) -> None:
        body = text_of(client.get(reverse("problem-list"), {"search": "Yashirin"}))
        assert problem_.slug not in body and SECRET not in body

    def test_the_site_search(self, client: APIClient, problem_: Problem) -> None:
        body = text_of(client.get("/api/v1/search/", {"q": "Yashirin"}))
        assert problem_.slug not in body and SECRET not in body

    def test_statistics_and_solvers(self, client: APIClient, problem_: Problem) -> None:
        assert client.get(reverse("problem-stats", args=[problem_.slug])).status_code == 404
        assert client.get(reverse("problem-solvers", args=[problem_.slug])).status_code == 404

    def test_the_contest_page_tells_the_count_only(
        self, client: APIClient, problem_: Problem
    ) -> None:
        response = client.get(reverse("contest-detail", args=["kuz-raundi"]))
        assert response.status_code == 200
        body = response.json()
        assert body["problems"] == [] and body["problem_count"] == 1
        assert problem_.slug not in text_of(response) and SECRET not in text_of(response)

    def test_a_solution_is_refused(
        self, client: APIClient, user, language, problem_: Problem
    ) -> None:
        client.force_login(user)
        ContestRegistration.objects.create(
            contest=problem_.contest_entries.get().contest, user=user
        )
        for extra in ({}, {"contest": "kuz-raundi"}):
            response = client.post(
                reverse("attempt-list"),
                {"problem": problem_.slug, "language": language.code, "source_code": "x", **extra},
                format="json",
            )
            assert response.status_code == 400, response.content
        assert not Attempt.objects.filter(problem=problem_).exists()

    def test_the_platform_counts_do_not_move(
        self, client: APIClient, problem, problem_: Problem
    ) -> None:
        assert Problem.objects.filter(is_public=True).count() == 1
        body = text_of(client.get(reverse("platform-stats")))
        assert problem_.slug not in body and SECRET not in body

    # A draft contest (`is_public=False`) opens nothing, even when it has started.
    def test_a_draft_contest_opens_nothing(self, client: APIClient) -> None:
        contest = make_contest(starts_in=-10, slug="qoralama")
        contest.is_public = False
        contest.save()
        problem = held_problem(contest, slug="qoralama-masala")
        assert client.get(reverse("problem-detail", args=[problem.slug])).status_code == 404


@pytest.mark.django_db
class TestDuringTheContest:
    @pytest.fixture
    def contest_(self) -> Contest:
        return make_contest(starts_in=-30)

    @pytest.fixture
    def problem_(self, contest_: Contest) -> Problem:
        return held_problem(contest_)

    def test_the_statement_is_for_everybody(self, client: APIClient, problem_: Problem) -> None:
        response = client.get(reverse("problem-detail", args=[problem_.slug]))
        assert response.status_code == 200
        body = response.json()
        assert body["statement"] == "Faqat musobaqada ochiladi."
        assert body["contest"] == {
            "slug": "kuz-raundi",
            "title": "Kuz raundi",
            "index_letter": "A",
            "is_running": True,
            "is_frozen": False,
            "registered": False,
        }

    def test_it_is_still_in_no_list(self, client: APIClient, problem_: Problem) -> None:
        for response in (
            client.get(reverse("problem-list")),
            client.get(reverse("problem-list"), {"search": "Yashirin"}),
            client.get("/api/v1/search/", {"q": "Yashirin"}),
        ):
            assert problem_.slug not in text_of(response) and SECRET not in text_of(response)
        # No public number until it reaches the archive.
        assert problem_.code is None

    def test_the_contest_page_lists_it(self, client: APIClient, problem_: Problem) -> None:
        body = client.get(reverse("contest-detail", args=["kuz-raundi"])).json()
        assert [row["slug"] for row in body["problems"]] == [problem_.slug]

    def test_the_editorial_stays_closed(self, client: APIClient, user, problem_: Problem) -> None:
        client.force_login(user)
        body = client.get(reverse("problem-detail", args=[problem_.slug])).json()
        assert body["editorial_state"]["available"] is False
        assert "saralang" not in str(body)
        assert client.post(reverse("problem-editorial", args=[problem_.slug])).status_code == 404

    def test_only_the_registered_send_solutions(
        self, client: APIClient, user, language, contest_: Contest, problem_: Problem
    ) -> None:
        client.force_login(user)
        payload = {"problem": problem_.slug, "language": language.code, "source_code": "print(1)"}

        # Outside the contest: a free check of the answer from another account.
        outside = client.post(reverse("attempt-list"), payload, format="json")
        assert outside.status_code == 400 and "contest" in outside.json()["error"]["details"]

        # In the contest, but not registered.
        unregistered = client.post(
            reverse("attempt-list"), {**payload, "contest": contest_.slug}, format="json"
        )
        assert unregistered.status_code == 400
        assert not Attempt.objects.filter(problem=problem_).exists()

        # Registering after the start is allowed.
        assert client.post(reverse("contest-register", args=[contest_.slug])).status_code in (
            200,
            201,
        )
        accepted = client.post(
            reverse("attempt-list"), {**payload, "contest": contest_.slug}, format="json"
        )
        assert accepted.status_code == 201, accepted.content
        assert Attempt.objects.get(problem=problem_).contest == contest_
        assert (
            client.get(reverse("problem-detail", args=[problem_.slug])).json()["contest"][
                "registered"
            ]
            is True
        )


@pytest.mark.django_db
class TestTheFreeze:
    """After the freeze, what other people sent is theirs until the end."""

    @pytest.fixture
    def setting(self, user, other_user, language):
        contest = make_contest(starts_in=-100, lasts=120, freeze=30)  # frozen for 10 minutes now
        problem = held_problem(contest)
        freeze_at = contest.freeze_at
        assert freeze_at is not None and contest.is_frozen
        before = attempt(
            other_user, problem, contest, language, Verdict.AC, freeze_at - timedelta(minutes=20)
        )
        after = attempt(
            other_user, problem, contest, language, Verdict.WA, freeze_at + timedelta(minutes=2)
        )
        mine = attempt(
            user, problem, contest, language, Verdict.AC, freeze_at + timedelta(minutes=3)
        )
        return contest, problem, before, after, mine

    def ids(self, client: APIClient, **params) -> set[int]:
        return {row["id"] for row in client.get(reverse("attempt-list"), params).json()["results"]}

    def test_a_guest_sees_what_came_before(self, client: APIClient, setting) -> None:
        _, _, before, after, mine = setting
        assert self.ids(client) == {before.pk}
        assert client.get(reverse("attempt-detail", args=[after.pk])).status_code == 404
        assert client.get(reverse("attempt-detail", args=[mine.pk])).status_code == 404

    def test_a_participant_also_sees_their_own(self, client: APIClient, user, setting) -> None:
        _, problem, before, _, mine = setting
        client.force_login(user)
        assert self.ids(client) == {before.pk, mine.pk}
        assert self.ids(client, problem=problem.slug) == {before.pk, mine.pk}

    def test_staff_see_everything(self, client: APIClient, setting) -> None:
        _, _, before, after, mine = setting
        client.force_login(
            User.objects.create_user(username="hakam", password="Parol!12345", is_staff=True)
        )
        assert self.ids(client) == {before.pk, after.pk, mine.pk}

    def test_the_numbers_stop_with_the_scoreboard(self, client: APIClient, setting) -> None:
        _, problem, before, _, _ = setting
        body = client.get(reverse("problem-detail", args=[problem.slug])).json()
        assert (body["attempt_count"], body["solved_count"]) == (1, 1)
        assert body["contest"]["is_frozen"] is True
        assert client.get(reverse("problem-stats", args=[problem.slug])).json()["total"] == 1
        solvers = client.get(reverse("problem-solvers", args=[problem.slug])).json()
        # Only the solution that came before the freeze; the later one is not told.
        assert [row["username"] for row in solvers["results"]] == [before.user.username]

    # The scoreboard unfreezes when the contest ends; so does everything else.
    # A hack phase may follow, and it needs those attempts in the open.
    def test_it_ends_with_the_contest(self, client: APIClient, setting) -> None:
        contest, problem, before, after, mine = setting
        Contest.objects.filter(pk=contest.pk).update(
            start_at=timezone.now() - timedelta(hours=3),
            end_at=timezone.now() - timedelta(minutes=5),
        )
        assert frozen_windows() == []
        assert self.ids(client) == {before.pk, after.pk, mine.pk}
        assert (
            client.get(reverse("problem-detail", args=[problem.slug])).json()["attempt_count"] == 0
        )

    def test_a_contest_without_a_freeze_hides_nothing(
        self, client: APIClient, user, language
    ) -> None:
        contest = make_contest(starts_in=-100, lasts=120, freeze=0, slug="muzlatishsiz")
        problem = held_problem(contest, slug="ochiq-masala")
        row = attempt(
            user, problem, contest, language, Verdict.WA, timezone.now() - timedelta(minutes=1)
        )
        assert frozen_windows() == []
        assert self.ids(client) == {row.pk}


@pytest.mark.django_db
class TestAfterTheContest:
    @pytest.fixture
    def ended(self) -> Contest:
        return make_contest(starts_in=-180, lasts=120)

    def test_finalizing_moves_the_problems_to_the_archive(
        self, client: APIClient, ended: Contest
    ) -> None:
        problem = held_problem(ended)
        assert problem.code is None

        finalize_contest(ended)

        problem.refresh_from_db()
        assert problem.is_public and problem.code is not None
        assert problem.slug in text_of(client.get(reverse("problem-list")))
        body = client.get(reverse("problem-detail", args=[problem.slug])).json()
        assert body["contest"] is None and body["editorial_state"]["available"] is True

    def test_archive_solutions_are_accepted_afterwards(
        self, client: APIClient, user, language, ended: Contest
    ) -> None:
        problem = held_problem(ended)
        finalize_contest(ended)
        client.force_login(user)
        response = client.post(
            reverse("attempt-list"),
            {"problem": problem.slug, "language": language.code, "source_code": "print(1)"},
            format="json",
        )
        assert response.status_code == 201, response.content

    # Between the last second and finalizing (a hack phase can last days)
    # the problem is open to read and closed to send.
    def test_ended_but_not_finalized(
        self, client: APIClient, user, language, ended: Contest
    ) -> None:
        problem = held_problem(ended)
        client.force_login(user)
        ContestRegistration.objects.create(contest=ended, user=user)
        assert client.get(reverse("problem-detail", args=[problem.slug])).status_code == 200
        for extra in ({}, {"contest": ended.slug}):
            response = client.post(
                reverse("attempt-list"),
                {"problem": problem.slug, "language": language.code, "source_code": "x", **extra},
                format="json",
            )
            assert response.status_code == 400

    def test_a_problem_without_tests_stays_held(self, ended: Contest) -> None:
        problem = held_problem(ended)
        problem.tests.all().delete()
        assert release_problems(ended) == []
        problem.refresh_from_db()
        assert not problem.is_public

    def test_a_problem_shared_with_an_unfinished_contest_stays_held(self, ended: Contest) -> None:
        problem = held_problem(ended)
        later = make_contest(starts_in=600, slug="keyingi-raund")
        ContestProblem.objects.create(contest=later, problem=problem, index_letter="A")
        assert release_problems(ended) == []
        problem.refresh_from_db()
        assert not problem.is_public

    def test_an_archive_problem_in_a_contest_is_left_alone(self, problem, contest) -> None:
        # `contest` holds the public `problem` fixture: nothing to release.
        code = problem.code
        finalize_contest(contest)
        problem.refresh_from_db()
        assert problem.is_public and problem.code == code
