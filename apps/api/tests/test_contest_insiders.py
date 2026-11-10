"""Insiders: testers before the start, and unrated participation (ADR-0055, part 2).

The problem authors, the testers, the jury and the organizers know the
problems before the start. A tester opens and sends to them early; the
attempt counts nowhere and only its author sees it. Any insider may take
part, but unrated: a star in the table, no place, no rating, no
certificate, no Qvant, no championship points.
"""

from __future__ import annotations

from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from contests.insiders import insiders
from contests.models import Contest, ContestProblem, ContestRegistration, Standing
from contests.services import finalize_contest, rebuild_standings
from core.models import User
from judging.models import Attempt
from judging.services import apply_result
from judging.verdicts import Verdict
from notifications.models import Notification
from problems.models import Problem, TestCase
from ratings.models import RatingHistory, UserSolvedProblem

SECRET = "Maxfiy sinov masalasi"


def make_contest(*, starts_in: int, lasts: int = 120, slug: str = "qish-raundi") -> Contest:
    start = timezone.now() + timedelta(minutes=starts_in)
    return Contest.objects.create(
        slug=slug,
        title="Qish raundi",
        start_at=start,
        end_at=start + timedelta(minutes=lasts),
        is_rated=True,
    )


def held_problem(contest: Contest, slug: str = "sinov-masala", letter: str = "A") -> Problem:
    problem = Problem.objects.create(
        slug=slug, title=SECRET, statement="…", difficulty=1500, is_public=False
    )
    TestCase.objects.create(
        problem=problem, order=1, input_ref="s3://x/1.in", output_ref="s3://x/1.out"
    )
    ContestProblem.objects.create(contest=contest, problem=problem, index_letter=letter)
    return problem


def people(n: int, prefix: str = "p") -> list[User]:
    return [
        User.objects.create_user(username=f"{prefix}{i}", password="Parol!12345") for i in range(n)
    ]


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


def submit(client: APIClient, problem: Problem, language, contest: Contest):
    return client.post(
        reverse("attempt-list"),
        {
            "problem": problem.slug,
            "language": language.code,
            "source_code": "int main(){}",
            "contest": contest.slug,
        },
        format="json",
    )


@pytest.mark.django_db
class TestWhoIsAnInsider:
    def test_the_four_roles(self, language) -> None:
        contest = make_contest(starts_in=60)
        problem = held_problem(contest)
        author, tester, judge, organizer, stranger = people(5)
        problem.authors.add(author)
        contest.testers.add(tester)
        contest.jury.add(judge)
        contest.organizers.add(organizer)
        found = insiders(contest)
        assert found == {
            author.pk: "author",
            tester.pk: "tester",
            judge.pk: "jury",
            organizer.pk: "organizer",
        }
        assert stranger.pk not in found

    def test_the_single_author_field_counts_too(self) -> None:
        contest = make_contest(starts_in=60)
        (author,) = people(1)
        problem = held_problem(contest)
        Problem.objects.filter(pk=problem.pk).update(author=author)
        assert insiders(contest) == {author.pk: "author"}

    def test_an_author_who_also_tests_is_told_as_an_author(self) -> None:
        contest = make_contest(starts_in=60)
        problem = held_problem(contest)
        (both,) = people(1)
        problem.authors.add(both)
        contest.testers.add(both)
        assert insiders(contest) == {both.pk: "author"}


@pytest.mark.django_db
class TestTesterBeforeTheStart:
    @pytest.fixture
    def setup(self, language):
        contest = make_contest(starts_in=60)
        problem = held_problem(contest)
        tester, stranger = people(2, "t")
        contest.testers.add(tester)
        return contest, problem, tester, stranger

    def test_the_tester_opens_the_problem(self, client: APIClient, setup) -> None:
        contest, problem, tester, _stranger = setup
        client.force_login(tester)
        response = client.get(reverse("problem-detail", args=[problem.slug]))
        assert response.status_code == 200
        held = response.json()["contest"]
        assert held["slug"] == contest.slug and held["testing"] is True

    def test_anybody_else_still_gets_404(self, client: APIClient, setup) -> None:
        _, problem, _, stranger = setup
        assert client.get(reverse("problem-detail", args=[problem.slug])).status_code == 404
        client.force_login(stranger)
        assert client.get(reverse("problem-detail", args=[problem.slug])).status_code == 404

    def test_the_viewer_lists_the_problems_for_the_tester_only(
        self, client: APIClient, setup
    ) -> None:
        contest, problem, tester, stranger = setup
        client.force_login(tester)
        mine = client.get(reverse("contest-viewer", args=[contest.slug])).json()
        assert mine["role"] == "tester" and mine["testing"] is True
        assert [p["slug"] for p in mine["problems"]] == [problem.slug]
        # The public contest page still tells the count only.
        public = client.get(reverse("contest-detail", args=[contest.slug])).json()
        assert public["problems"] == []
        client.force_login(stranger)
        theirs = client.get(reverse("contest-viewer", args=[contest.slug])).json()
        assert theirs == {
            "role": "",
            "registered": False,
            "testing": False,
            "problems": [],
            "disqualified_reason": None,
            "judge": False,
        }

    def test_the_tester_sends_without_registering(self, client: APIClient, setup, language) -> None:
        contest, problem, tester, _ = setup
        client.force_login(tester)
        response = submit(client, problem, language, contest)
        assert response.status_code == 201, response.content

    def test_a_stranger_cannot_send(self, client: APIClient, setup, language) -> None:
        contest, problem, _, stranger = setup
        ContestRegistration.objects.create(contest=contest, user=stranger)
        client.force_login(stranger)
        assert submit(client, problem, language, contest).status_code == 400
        assert not Attempt.objects.filter(problem=problem).exists()

    def test_a_testing_attempt_counts_nowhere(self, client: APIClient, setup, language) -> None:
        contest, problem, tester, _ = setup
        client.force_login(tester)
        attempt_id = submit(client, problem, language, contest).json()["id"]
        apply_result({"attempt_id": attempt_id, "verdict": "AC", "score": 100})
        problem.refresh_from_db()
        assert problem.attempt_count == 0 and problem.solved_count == 0
        assert not UserSolvedProblem.objects.filter(user=tester).exists()
        assert not RatingHistory.objects.filter(user=tester).exists()
        # Nor in the contest table.
        assert not Standing.objects.filter(contest=contest).exists()

    def test_only_its_author_sees_a_testing_attempt(
        self, client: APIClient, setup, language
    ) -> None:
        contest, problem, tester, stranger = setup
        client.force_login(tester)
        attempt_id = submit(client, problem, language, contest).json()["id"]
        ids = {row["id"] for row in client.get(reverse("attempt-list")).json()["results"]}
        assert attempt_id in ids
        client.force_login(stranger)
        ids = {row["id"] for row in client.get(reverse("attempt-list")).json()["results"]}
        assert attempt_id not in ids
        assert client.get(reverse("attempt-detail", args=[attempt_id])).status_code == 404
        client.logout()
        body = client.get(reverse("attempt-list")).content.decode()
        assert problem.slug not in body

    def test_after_the_start_the_tester_needs_to_register_like_anybody(
        self, client: APIClient, setup, language
    ) -> None:
        contest, problem, tester, _ = setup
        Contest.objects.filter(pk=contest.pk).update(start_at=timezone.now() - timedelta(minutes=1))
        client.force_login(tester)
        assert submit(client, problem, language, contest).status_code == 400
        ContestRegistration.objects.create(contest=contest, user=tester)
        assert submit(client, problem, language, contest).status_code == 201


@pytest.mark.django_db
class TestUnratedInTheTable:
    def _finished(self, language, officials: int = 10):
        now = timezone.now()
        contest = make_contest(starts_in=-180, lasts=120)
        problem = held_problem(contest)
        tester = User.objects.create_user(username="sinovchi", password="Parol!12345")
        contest.testers.add(tester)
        crowd = people(officials)
        # The tester tested before the start and then won the contest.
        attempt(
            tester, problem, contest, language, Verdict.AC, contest.start_at - timedelta(hours=5)
        )
        attempt(
            tester, problem, contest, language, Verdict.AC, contest.start_at + timedelta(minutes=1)
        )
        for i, user in enumerate(crowd):
            attempt(
                user,
                problem,
                contest,
                language,
                Verdict.AC,
                contest.start_at + timedelta(minutes=5 + i),
            )
        for user in [tester, *crowd]:
            ContestRegistration.objects.get_or_create(contest=contest, user=user)
        assert contest.end_at < now
        return contest, tester, crowd

    def test_the_insider_has_a_star_and_no_place(self, language) -> None:
        contest, tester, crowd = self._finished(language)
        rebuild_standings(contest)
        row = Standing.objects.get(contest=contest, user=tester)
        assert row.insider_role == "tester" and row.rank == 0 and row.position == 1
        first = Standing.objects.get(contest=contest, user=crowd[0])
        # The insider above does not push the first official participant down.
        assert first.rank == 1 and first.position == 2

    def test_the_testing_attempt_is_not_in_the_table(self, language) -> None:
        contest, tester, _ = self._finished(language)
        rebuild_standings(contest)
        # Solved at minute 1 of the contest, not at minute 0 from the test run.
        assert Standing.objects.get(contest=contest, user=tester).penalty == 1

    def test_the_public_table_follows_position(self, client: APIClient, language) -> None:
        contest, tester, _crowd = self._finished(language)
        rebuild_standings(contest)
        rows = client.get(reverse("contest-standings", args=[contest.slug])).json()["results"]
        assert rows[0]["username"] == tester.username and rows[0]["insider_role"] == "tester"
        assert rows[1]["rank"] == 1 and rows[1]["insider_role"] == ""

    def test_finalizing_skips_the_insider(self, language) -> None:
        contest, tester, crowd = self._finished(language)
        finalize_contest(contest)
        tester.refresh_from_db()
        assert tester.rated_contest_count == 0
        assert not RatingHistory.objects.filter(user=tester, ref_id=contest.slug).exists()
        assert not tester.certificates.exists()
        winner = crowd[0]
        winner.refresh_from_db()
        assert winner.rated_contest_count == 1
        assert winner.certificates.get().place == 1

    def test_insiders_do_not_make_up_the_rated_minimum(self, language) -> None:
        contest, _tester, _crowd = self._finished(language, officials=9)
        finalize_contest(contest)
        # Nine official participants and one tester: below the minimum of ten.
        assert not RatingHistory.objects.filter(ref_id=contest.slug).exists()

    def test_the_profile_tells_no_place(self, client: APIClient, language) -> None:
        contest, tester, _ = self._finished(language)
        finalize_contest(contest)
        rows = client.get(f"/api/v1/users/{tester.username}/contests/").json()["results"]
        assert rows[0]["insider_role"] == "tester" and rows[0]["rank"] == 0
        assert rows[0]["participants"] == 10


@pytest.mark.django_db
class TestCrewAndAppointment:
    def test_the_contest_page_tells_the_crew(self, client: APIClient) -> None:
        contest = make_contest(starts_in=60)
        problem = held_problem(contest)
        author, tester, judge = people(3, "c")
        problem.authors.add(author)
        contest.testers.add(tester)
        contest.jury.add(judge)
        crew = client.get(reverse("contest-detail", args=[contest.slug])).json()["crew"]
        assert [p["username"] for p in crew["authors"]] == [author.username]
        assert [p["username"] for p in crew["testers"]] == [tester.username]
        assert [p["username"] for p in crew["jury"]] == [judge.username]

    def test_an_inactive_author_is_left_out(self, client: APIClient) -> None:
        contest = make_contest(starts_in=60)
        problem = held_problem(contest)
        (shadow,) = people(1, "kep")
        User.objects.filter(pk=shadow.pk).update(is_active=False)
        problem.authors.add(shadow)
        crew = client.get(reverse("contest-detail", args=[contest.slug])).json()["crew"]
        assert crew["authors"] == []

    def test_an_organizer_appoints_testers_and_they_are_told(self) -> None:
        client = APIClient()
        organizer, tester = people(2, "o")
        contest = make_contest(starts_in=60)
        contest.organizers.add(organizer)
        client.force_login(organizer)
        response = client.patch(
            f"/api/v1/contests/mine/{contest.slug}/", {"testers": [tester.username]}, format="json"
        )
        assert response.status_code == 200, response.content
        assert list(contest.testers.values_list("username", flat=True)) == [tester.username]
        note = Notification.objects.get(user=tester)
        assert note.code == "contest_tester" and note.ref_id == contest.slug
        # Saving again tells nobody twice.
        client.patch(
            f"/api/v1/contests/mine/{contest.slug}/", {"testers": [tester.username]}, format="json"
        )
        assert Notification.objects.filter(user=tester).count() == 1

    def test_a_tester_badge_on_the_profile(self, client: APIClient) -> None:
        contest = make_contest(starts_in=60)
        (tester,) = people(1, "b")
        contest.testers.add(tester)
        body = client.get(reverse("user-profile", args=[tester.username])).json()
        assert {"code": "tester"} in body["roles"]


@pytest.mark.django_db
def test_an_organizer_cannot_add_testers_after_the_start() -> None:
    """A tester added mid-contest would lose a participant's place retroactively."""
    client = APIClient()
    organizer, late = people(2, "late")
    contest = make_contest(starts_in=-10)
    contest.organizers.add(organizer)
    client.force_login(organizer)
    response = client.patch(
        f"/api/v1/contests/mine/{contest.slug}/", {"testers": [late.username]}, format="json"
    )
    assert response.status_code == 400
    assert not contest.testers.exists()
