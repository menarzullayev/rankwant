"""Fair play: editor signals, the jury's report and disqualification (ADR-0055, part 4)."""

from __future__ import annotations

from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from contests.integrity import flags
from contests.models import AttemptSignal, Contest, ContestProblem, ContestRegistration, Standing
from contests.services import finalize_contest, rebuild_standings
from core.models import User
from judging.models import Attempt
from judging.verdicts import Verdict
from notifications.models import Notification
from problems.models import Problem, TestCase
from ratings.models import RatingHistory, UserSolvedProblem

SOURCE = "int main(){" + "x" * 400 + "}"


def make_contest(*, starts_in: int = -10, lasts: int = 120) -> Contest:
    start = timezone.now() + timedelta(minutes=starts_in)
    contest = Contest.objects.create(
        slug="halol-raund",
        title="Halol raund",
        start_at=start,
        end_at=start + timedelta(minutes=lasts),
        is_rated=True,
    )
    problem = Problem.objects.create(
        slug="halol-masala", title="Halol", statement="…", difficulty=1200, is_public=False
    )
    TestCase.objects.create(
        problem=problem, order=1, input_ref="s3://x/1.in", output_ref="s3://x/1.out"
    )
    ContestProblem.objects.create(contest=contest, problem=problem, index_letter="A")
    return contest


def person(name: str) -> User:
    return User.objects.create_user(username=name, password="Parol!12345")


def as_user(user: User) -> APIClient:
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def submit(user: User, contest: Contest, language, editor=None):
    ContestRegistration.objects.get_or_create(contest=contest, user=user)
    payload = {
        "problem": "halol-masala",
        "language": language.code,
        "source_code": SOURCE,
        "contest": contest.slug,
    }
    if editor is not None:
        payload["editor"] = editor
    return as_user(user).post("/api/v1/attempts/", payload, format="json")


@pytest.mark.django_db
class TestSignals:
    def test_a_contest_attempt_keeps_its_signals(self, language) -> None:
        contest = make_contest()
        user = person("yozuvchi")
        response = submit(
            user,
            contest,
            language,
            {"pasted_chars": 410, "largest_paste": 410, "paste_count": 1, "blur_count": 2},
        )
        assert response.status_code == 201, response.content
        signal = AttemptSignal.objects.get(attempt_id=response.json()["id"])
        assert signal.largest_paste == 410 and signal.source_chars == len(SOURCE)
        assert flags(signal) == ["pasted"]

    def test_an_archive_attempt_keeps_nothing(self, language, problem) -> None:
        response = as_user(person("arxiv")).post(
            "/api/v1/attempts/",
            {
                "problem": problem.slug,
                "language": language.code,
                "source_code": SOURCE,
                "editor": {"pasted_chars": 999},
            },
            format="json",
        )
        assert response.status_code == 201
        assert not AttemptSignal.objects.exists()

    def test_typing_too_fast_and_leaving_often(self, language) -> None:
        contest = make_contest()
        user = person("tez")
        attempt_id = submit(
            user, contest, language, {"active_ms": 30_000, "blur_count": 12}
        ).json()["id"]
        assert set(flags(AttemptSignal.objects.get(attempt_id=attempt_id))) == {"fast", "away"}


@pytest.mark.django_db
class TestReport:
    def test_only_the_jury_after_the_end(self, language) -> None:
        contest = make_contest()
        judge, user = person("hakam"), person("ishtirokchi")
        contest.jury.add(judge)
        submit(user, contest, language, {"largest_paste": 401})
        url = f"/api/v1/contests/{contest.slug}/integrity/"
        assert as_user(judge).get(url).status_code == 400  # still running
        Contest.objects.filter(pk=contest.pk).update(end_at=timezone.now() - timedelta(minutes=1))
        Attempt.objects.filter(contest=contest).update(
            created_at=timezone.now() - timedelta(minutes=5)
        )
        assert as_user(user).get(url).status_code == 403
        rows = as_user(judge).get(url).json()["results"]
        assert rows[0]["username"] == "ishtirokchi" and rows[0]["flags"] == ["pasted"]


@pytest.mark.django_db
class TestDisqualify:
    def _finished(self, language, n: int = 11):
        contest = make_contest(starts_in=-180, lasts=120)
        people = [person(f"q{i}") for i in range(n)]
        for i, user in enumerate(people):
            ContestRegistration.objects.create(contest=contest, user=user)
            row = Attempt.objects.create(
                user=user,
                problem=contest.problems.get().problem,
                contest=contest,
                language=language,
                source_code=SOURCE,
                verdict=Verdict.AC,
            )
            Attempt.objects.filter(pk=row.pk).update(
                created_at=contest.start_at + timedelta(minutes=1 + i)
            )
            UserSolvedProblem.objects.create(
                user=user, problem=row.problem, first_ac_attempt=row, difficulty_at_solve=1200
            )
        rebuild_standings(contest)
        return contest, people

    def test_dq_before_finalizing(self, language) -> None:
        contest, people = self._finished(language)
        judge = person("hakam")
        contest.jury.add(judge)
        cheat = people[0]
        response = as_user(judge).post(
            f"/api/v1/contests/{contest.slug}/disqualify/",
            {"username": cheat.username, "reason": "AI bilan yozilgan"},
            format="json",
        )
        assert response.status_code == 200, response.content
        assert not Attempt.objects.filter(user=cheat).exclude(verdict=Verdict.SKIPPED).exists()
        assert not UserSolvedProblem.objects.filter(user=cheat).exists()
        row = Standing.objects.get(contest=contest, user=cheat)
        assert row.is_disqualified and row.rank == 0
        assert Standing.objects.get(contest=contest, user=people[1]).rank == 1
        note = Notification.objects.get(user=cheat)
        assert note.code == "contest_disqualified"

    def test_dq_after_finalizing_rerates_the_contest(self, language) -> None:
        contest, people = self._finished(language)
        finalize_contest(contest)
        cheat, second = people[0], people[1]
        cheat.refresh_from_db()
        assert cheat.rated_contest_count == 1
        before_second = RatingHistory.objects.get(user=second, ref_id=contest.slug).value_after
        ops = User.objects.create_user(username="ops", password="Parol!12345", is_staff=True)
        from django.contrib.auth.models import Group

        ops.groups.add(Group.objects.get_or_create(name="staff-ops")[0])
        response = as_user(ops).post(
            f"/api/v1/contests/{contest.slug}/disqualify/",
            {"username": cheat.username, "reason": "Ko'chirma"},
            format="json",
        )
        assert response.status_code == 200, response.content
        cheat.refresh_from_db()
        assert cheat.rated_contest_count == 0
        assert not RatingHistory.objects.filter(user=cheat, ref_id=contest.slug).exists()
        assert not cheat.certificates.exists()
        # The second moved up to first: their rating change is computed again.
        second_row = RatingHistory.objects.get(user=second, ref_id=contest.slug)
        assert second_row.rank == 1 and second_row.value_after > before_second
        assert second.certificates.get().place == 1

    def test_only_the_jury_disqualifies(self, language) -> None:
        contest, people = self._finished(language, n=2)
        organizer = person("tashkilotchi")
        contest.organizers.add(organizer)
        response = as_user(organizer).post(
            f"/api/v1/contests/{contest.slug}/disqualify/",
            {"username": people[0].username, "reason": "?"},
            format="json",
        )
        assert response.status_code == 403
        assert ContestRegistration.objects.get(user=people[0]).disqualified_at is None

    def test_a_reason_is_required(self, language) -> None:
        contest, people = self._finished(language, n=2)
        judge = person("hakam")
        contest.jury.add(judge)
        response = as_user(judge).post(
            f"/api/v1/contests/{contest.slug}/disqualify/",
            {"username": people[0].username, "reason": " "},
            format="json",
        )
        assert response.status_code == 400
