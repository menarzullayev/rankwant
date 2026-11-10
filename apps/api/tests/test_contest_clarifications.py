"""Questions, answers and announcements during a contest (ADR-0055, part 3)."""

from __future__ import annotations

from datetime import timedelta

import pytest
from django.contrib.auth.models import Group
from django.utils import timezone
from rest_framework.test import APIClient

from contests import clarifications as qa
from contests.models import Clarification, Contest, ContestProblem, ContestRegistration
from core.models import User
from notifications.models import Notification
from problems.models import Problem, TestCase


def make_contest(*, starts_in: int = -10, lasts: int = 120) -> Contest:
    start = timezone.now() + timedelta(minutes=starts_in)
    contest = Contest.objects.create(
        slug="savol-raundi",
        title="Savol raundi",
        start_at=start,
        end_at=start + timedelta(minutes=lasts),
        is_rated=True,
    )
    problem = Problem.objects.create(
        slug="savol-masala", title="Savol masala", statement="…", difficulty=1200, is_public=False
    )
    TestCase.objects.create(
        problem=problem, order=1, input_ref="s3://x/1.in", output_ref="s3://x/1.out"
    )
    ContestProblem.objects.create(contest=contest, problem=problem, index_letter="A")
    return contest


def person(name: str) -> User:
    return User.objects.create_user(username=name, password="Parol!12345")


def client_for(user: User | None) -> APIClient:
    client = APIClient()
    if user is not None:
        client.force_authenticate(user=user)
    return client


def url(contest: Contest, tail: str = "clarifications/") -> str:
    return f"/api/v1/contests/{contest.slug}/{tail}"


def ask(user: User, contest: Contest, text: str = "a manfiy bo'lishi mumkinmi?", problem="A"):
    return client_for(user).post(
        url(contest), {"problem": problem, "question": text}, format="json"
    )


@pytest.mark.django_db
class TestAsking:
    def test_any_signed_in_user_asks(self) -> None:
        contest = make_contest()
        response = ask(person("tomoshabin"), contest)
        assert response.status_code == 201, response.content
        assert response.json()["problem"] == "A" and response.json()["mine"] is True

    def test_a_guest_cannot(self) -> None:
        contest = make_contest()
        response = client_for(None).post(url(contest), {"question": "?"}, format="json")
        assert response.status_code == 401
        assert not Clarification.objects.exists()

    def test_not_after_the_end(self) -> None:
        contest = make_contest(starts_in=-200, lasts=60)
        assert ask(person("kech"), contest).status_code == 400

    def test_before_the_start_only_about_the_contest(self) -> None:
        contest = make_contest(starts_in=60)
        user = person("erta")
        assert ask(user, contest).json()["error"]["code"] == "problems_closed"
        assert ask(user, contest, problem=None).status_code == 201

    def test_one_a_minute(self) -> None:
        contest = make_contest()
        user = person("shoshqaloq")
        assert ask(user, contest).status_code == 201
        second = ask(user, contest)
        assert second.status_code == 429 and int(second["Retry-After"]) > 0

    def test_at_most_twenty(self) -> None:
        contest = make_contest()
        user = person("savolchi")
        old = timezone.now() - timedelta(hours=1)
        for i in range(qa.MAX_QUESTIONS):
            Clarification.objects.create(contest=contest, author=user, question=f"q{i}")
        Clarification.objects.filter(author=user).update(created_at=old)
        response = ask(user, contest)
        assert response.status_code == 429
        assert response.json()["error"]["code"] == "too_many_questions"

    def test_a_long_question_is_refused(self) -> None:
        contest = make_contest()
        response = ask(person("uzun"), contest, text="x" * (qa.MAX_LENGTH + 1))
        assert response.status_code == 400

    def test_the_jury_is_told(self) -> None:
        contest = make_contest()
        judge = person("hakam")
        contest.jury.add(judge)
        ask(person("savol"), contest)
        note = Notification.objects.get(user=judge)
        assert note.code == "contest_question" and note.ref_type == "contest_qa"

    def test_without_a_jury_staff_ops_is_told(self) -> None:
        contest = make_contest()
        ops = User.objects.create_user(username="ops", password="Parol!12345", is_staff=True)
        ops.groups.add(Group.objects.get_or_create(name="staff-ops")[0])
        ask(person("savol2"), contest)
        assert Notification.objects.filter(user=ops, code="contest_question").exists()


@pytest.mark.django_db
class TestPrivacy:
    def test_a_question_is_its_authors(self) -> None:
        contest = make_contest()
        author, other = person("muallif"), person("boshqa")
        ask(author, contest)
        assert len(client_for(author).get(url(contest)).json()["results"]) == 1
        assert client_for(other).get(url(contest)).json()["results"] == []
        assert client_for(None).get(url(contest)).json()["results"] == []

    def test_the_moderator_sees_everything_with_names(self) -> None:
        contest = make_contest()
        judge = person("hakam")
        contest.jury.add(judge)
        ask(person("muallif"), contest)
        body = client_for(judge).get(url(contest)).json()
        assert body["moderator"] is True
        assert body["results"][0]["author"] == "muallif"

    def test_nobody_else_learns_whose_it_was(self) -> None:
        contest = make_contest()
        judge = person("hakam")
        contest.jury.add(judge)
        row_id = ask(person("muallif"), contest).json()["id"]
        client_for(judge).post(
            url(contest, f"clarifications/{row_id}/answer/"),
            {"answer": "Ha, manfiy bo'ladi.", "public": True},
            format="json",
        )
        rows = client_for(None).get(url(contest)).json()["results"]
        assert rows[0]["answer"] == "Ha, manfiy bo'ladi." and rows[0]["author"] is None

    def test_after_finalizing_every_answer_is_public(self) -> None:
        contest = make_contest()
        judge = person("hakam")
        contest.jury.add(judge)
        row_id = ask(person("muallif"), contest).json()["id"]
        client_for(judge).post(
            url(contest, f"clarifications/{row_id}/answer/"), {"answer_code": "no"}, format="json"
        )
        unanswered = Clarification.objects.create(contest=contest, author=person("x"), question="?")
        assert client_for(None).get(url(contest)).json()["results"] == []
        Contest.objects.filter(pk=contest.pk).update(ratings_applied_at=timezone.now())
        ids = [r["id"] for r in client_for(None).get(url(contest)).json()["results"]]
        assert ids == [row_id] and unanswered.pk not in ids


@pytest.mark.django_db
class TestAnswering:
    def test_only_a_moderator_answers(self) -> None:
        contest = make_contest()
        row_id = ask(person("muallif"), contest).json()["id"]
        response = client_for(person("begona")).post(
            url(contest, f"clarifications/{row_id}/answer/"), {"answer": "Ha"}, format="json"
        )
        assert response.status_code == 403
        assert not Clarification.objects.get(pk=row_id).is_answered

    def test_an_organizer_answers(self) -> None:
        contest = make_contest()
        organizer = person("tashkilotchi")
        contest.organizers.add(organizer)
        row_id = ask(person("muallif"), contest).json()["id"]
        response = client_for(organizer).post(
            url(contest, f"clarifications/{row_id}/answer/"),
            {"answer_code": "read_statement"},
            format="json",
        )
        assert response.status_code == 200, response.content
        assert response.json()["answer_code"] == "read_statement"

    def test_the_author_is_told(self) -> None:
        contest = make_contest()
        judge, author = person("hakam"), person("muallif")
        contest.jury.add(judge)
        row_id = ask(author, contest).json()["id"]
        client_for(judge).post(
            url(contest, f"clarifications/{row_id}/answer/"), {"answer_code": "yes"}, format="json"
        )
        assert Notification.objects.get(user=author).code == "contest_answer"

    def test_a_public_answer_tells_the_participants(self) -> None:
        contest = make_contest()
        judge, author, participant = person("hakam"), person("muallif"), person("qatnashchi")
        contest.jury.add(judge)
        ContestRegistration.objects.create(contest=contest, user=participant)
        ContestRegistration.objects.create(contest=contest, user=author)
        row_id = ask(author, contest).json()["id"]
        client_for(judge).post(
            url(contest, f"clarifications/{row_id}/answer/"),
            {"answer": "n ≤ 10^5", "public": True},
            format="json",
        )
        assert Notification.objects.get(user=participant).code == "contest_announcement"
        # The author is told once, as the author.
        assert list(Notification.objects.filter(user=author).values_list("code", flat=True)) == [
            "contest_answer"
        ]

    def test_an_unknown_quick_answer_is_refused(self) -> None:
        contest = make_contest()
        judge = person("hakam")
        contest.jury.add(judge)
        row_id = ask(person("muallif"), contest).json()["id"]
        response = client_for(judge).post(
            url(contest, f"clarifications/{row_id}/answer/"),
            {"answer_code": "maybe"},
            format="json",
        )
        assert response.status_code == 400


@pytest.mark.django_db
class TestAnnouncements:
    def test_the_jury_announces_to_everybody(self) -> None:
        contest = make_contest()
        judge, participant = person("hakam"), person("qatnashchi")
        contest.jury.add(judge)
        ContestRegistration.objects.create(contest=contest, user=participant)
        response = client_for(judge).post(
            url(contest, "announcements/"),
            {"problem": "A", "text": "Testlar tuzatildi."},
            format="json",
        )
        assert response.status_code == 201, response.content
        rows = client_for(None).get(url(contest)).json()["results"]
        assert rows[0]["is_announcement"] is True and rows[0]["problem"] == "A"
        assert Notification.objects.get(user=participant).code == "contest_announcement"

    def test_a_participant_cannot_announce(self) -> None:
        contest = make_contest()
        response = client_for(person("qatnashchi")).post(
            url(contest, "announcements/"), {"text": "Hammaga salom"}, format="json"
        )
        assert response.status_code == 403
        assert not Clarification.objects.exists()
