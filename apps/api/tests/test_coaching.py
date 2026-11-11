"""Coach and student (ADR-0061 § 4)."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from classroom.models import Classroom, ClassroomMember
from coaching.models import CoachLink, Recommendation
from contests.models import Contest
from core.models import User
from judging.models import Attempt
from notifications.models import Notification
from problems.models import Problem
from ratings.models import UserSolvedProblem


def _client(user: User) -> APIClient:
    client = APIClient()
    client.force_authenticate(user)
    return client


def _user(name: str, **extra: Any) -> User:
    return User.objects.create_user(username=name, password="x", **extra)


def _ask(student: User, coach: User):
    return _client(student).post(reverse("coaching-list"), {"coach": coach.username})


def _active(student: User, coach: User, *, consent: bool = False) -> CoachLink:
    return CoachLink.objects.create(
        student=student, coach=coach, status=CoachLink.Status.ACTIVE, can_view_attempts=consent
    )


@pytest.mark.django_db
class TestAsking:
    def test_ask_notifies_the_coach(self, user, other_user) -> None:
        res = _ask(user, other_user)
        assert res.status_code == 201
        assert res.json()["status"] == "pending"
        note = Notification.objects.get(user=other_user)
        assert note.code == "coach_requested"
        assert note.params == {"user": user.username}

    def test_consent_starts_from_the_users_default(self, user, other_user) -> None:
        User.objects.filter(pk=user.pk).update(coach_can_view_attempts=True)
        user.refresh_from_db()
        assert _ask(user, other_user).json()["can_view_attempts"] is True
        assert _ask(user, _user("c2")).json()["can_view_attempts"] is True

    def test_not_yourself_and_not_twice(self, user, other_user) -> None:
        assert _client(user).post(reverse("coaching-list"), {"coach": user.username}).json()[
            "error"
        ]["code"] == ("coach_self")
        _ask(user, other_user)
        assert _ask(user, other_user).json()["error"]["code"] == "coach_already"

    def test_at_most_three(self, user) -> None:
        for i in range(3):
            assert _ask(user, _user(f"c{i}")).status_code == 201
        res = _ask(user, _user("c3"))
        assert res.json()["error"]["code"] == "coach_limit"

    def test_ending_frees_a_place(self, user) -> None:
        links = [_ask(user, _user(f"c{i}")).json()["id"] for i in range(3)]
        _client(user).post(reverse("coaching-end", args=[links[0]]))
        assert _ask(user, _user("c3")).status_code == 201

    def test_withdraw_then_ask_again_waits(self, user, other_user) -> None:
        link = _ask(user, other_user).json()["id"]
        _client(user).post(reverse("coaching-end", args=[link]))
        assert _ask(user, other_user).json()["error"]["code"] == "request_answered"
        assert Notification.objects.filter(user=other_user).count() == 1

    def test_unknown_coach(self, user) -> None:
        res = _client(user).post(reverse("coaching-list"), {"coach": "yoq"})
        assert res.json()["error"]["code"] == "coach_not_found"


@pytest.mark.django_db
class TestAnswering:
    def test_accept(self, user, other_user) -> None:
        link = _ask(user, other_user).json()["id"]
        res = _client(other_user).post(reverse("coaching-accept", args=[link]))
        assert res.json()["status"] == "active"
        assert Notification.objects.get(user=user).code == "coach_accepted"
        listed = _client(user).get(reverse("coaching-list")).json()
        assert [row["coach"]["username"] for row in listed["coaches"]] == [other_user.username]

    def test_only_the_coach_answers(self, user, other_user) -> None:
        link = _ask(user, other_user).json()["id"]
        res = _client(user).post(reverse("coaching-accept", args=[link]))
        assert res.json()["error"]["code"] == "request_not_found"
        res = _client(_user("x")).post(reverse("coaching-accept", args=[link]))
        assert res.json()["error"]["code"] == "request_not_found"

    def test_decline_pauses_asking_again(self, user, other_user) -> None:
        link = _ask(user, other_user).json()["id"]
        _client(other_user).post(reverse("coaching-decline", args=[link]))
        assert Notification.objects.get(user=user).code == "coach_declined"
        assert _ask(user, other_user).json()["error"]["code"] == "request_answered"
        CoachLink.objects.filter(pk=link).update(decided_at=timezone.now() - timedelta(days=2))
        assert _ask(user, other_user).status_code == 201

    def test_requests_list_for_the_coach(self, user, other_user) -> None:
        _ask(user, other_user)
        rows = _client(other_user).get(reverse("coaching-list")).json()["requests"]
        assert [row["student"]["username"] for row in rows] == [user.username]


@pytest.mark.django_db
class TestCode:
    def _attempt(self, student: User, problem: Problem, language, **extra: Any) -> Attempt:
        return Attempt.objects.create(
            user=student, problem=problem, language=language, source_code="print(1)", **extra
        )

    def _source(self, viewer: User, attempt: Attempt) -> str | None:
        body = _client(viewer).get(reverse("attempt-detail", args=[attempt.pk])).json()
        source = body.get("source_code")
        return None if source is None else str(source)

    def test_coach_with_consent_reads_code(self, user, other_user, problem, language) -> None:
        attempt = self._attempt(user, problem, language)
        assert self._source(other_user, attempt) is None
        link = _active(user, other_user)
        assert self._source(other_user, attempt) is None, "no consent"
        _client(user).patch(
            reverse("coaching-detail", args=[link.pk]), {"can_view_attempts": True}, format="json"
        )
        assert self._source(other_user, attempt) == "print(1)"

    def test_consent_is_per_coach(self, user, other_user, problem, language) -> None:
        attempt = self._attempt(user, problem, language)
        _active(user, other_user, consent=True)
        third = _user("c3")
        _active(user, third, consent=False)
        assert self._source(other_user, attempt) == "print(1)"
        assert self._source(third, attempt) is None

    def test_ended_coach_reads_nothing(self, user, other_user, problem, language) -> None:
        attempt = self._attempt(user, problem, language)
        link = _active(user, other_user, consent=True)
        _client(user).post(reverse("coaching-end", args=[link.pk]))
        assert self._source(other_user, attempt) is None

    def test_coach_cannot_change_consent(self, user, other_user) -> None:
        link = _active(user, other_user)
        res = _client(other_user).patch(
            reverse("coaching-detail", args=[link.pk]), {"can_view_attempts": True}, format="json"
        )
        assert res.status_code == 400
        link.refresh_from_db()
        assert link.can_view_attempts is False

    def test_not_while_the_contest_runs(self, user, other_user, problem, language) -> None:
        now = timezone.now()
        contest = Contest.objects.create(
            slug="live",
            title="Live",
            start_at=now - timedelta(hours=1),
            end_at=now + timedelta(hours=1),
            is_public=True,
        )
        attempt = self._attempt(user, problem, language, contest=contest)
        _active(user, other_user, consent=True)
        assert self._source(other_user, attempt) is None
        Contest.objects.filter(pk=contest.pk).update(
            start_at=now - timedelta(hours=3), end_at=now - timedelta(hours=1)
        )
        assert self._source(other_user, attempt) == "print(1)"


@pytest.mark.django_db
class TestPanelAndRecommendations:
    def test_recommend_and_see_it_in_tasks(self, user, other_user, problem) -> None:
        link = _active(user, other_user)
        res = _client(other_user).post(
            reverse("coaching-recommend", args=[link.pk]),
            {"problem": f"#{problem.code}", "note": "DP mashqi"},
            format="json",
        )
        assert res.status_code == 201, res.content
        assert Notification.objects.get(user=user).code == "coach_recommended"
        rows = _client(user).get(reverse("coaching-recommendations")).json()
        assert [(r["problem"], r["note"], r["solved"]) for r in rows] == [
            (problem.slug, "DP mashqi", False)
        ]
        UserSolvedProblem.objects.create(user=user, problem=problem, difficulty_at_solve=800)
        assert _client(user).get(reverse("coaching-recommendations")).json()[0]["solved"] is True

    def test_recommend_twice_notifies_once(self, user, other_user, problem) -> None:
        link = _active(user, other_user)
        for _ in range(2):
            _client(other_user).post(
                reverse("coaching-recommend", args=[link.pk]), {"problem": problem.slug}
            )
        assert Recommendation.objects.count() == 1
        assert Notification.objects.filter(user=user).count() == 1

    def test_only_an_active_coach_recommends(self, user, other_user, problem) -> None:
        link = CoachLink.objects.create(student=user, coach=other_user)
        res = _client(other_user).post(
            reverse("coaching-recommend", args=[link.pk]), {"problem": problem.slug}
        )
        assert res.json()["error"]["code"] == "request_not_found"
        res = _client(user).post(reverse("coaching-recommend", args=[link.pk]), {"problem": "x"})
        assert res.json()["error"]["code"] == "request_not_found"

    def test_hidden_problem_is_refused(self, user, other_user) -> None:
        Problem.objects.create(slug="draft", title="D", statement="s", difficulty=800)
        link = _active(user, other_user)
        res = _client(other_user).post(
            reverse("coaching-recommend", args=[link.pk]), {"problem": "draft"}
        )
        assert res.json()["error"]["code"] == "coach_problem_missing"

    def test_panel(self, user, other_user, problem, language) -> None:
        _active(user, other_user, consent=True)
        Attempt.objects.create(user=user, problem=problem, language=language, source_code="x")
        rows = _client(other_user).get(reverse("coaching-students")).json()
        assert [row["username"] for row in rows] == [user.username]
        assert rows[0]["can_view_attempts"] is True
        assert [a["problem"] for a in rows[0]["recent"]] == [problem.slug]
        # A student has no students.
        assert _client(user).get(reverse("coaching-students")).json() == []

    def test_ended_coachs_recommendations_leave_the_tasks(self, user, other_user, problem) -> None:
        link = _active(user, other_user)
        Recommendation.objects.create(link=link, problem=problem)
        _client(user).post(reverse("coaching-end", args=[link.pk]))
        assert _client(user).get(reverse("coaching-recommendations")).json() == []


@pytest.mark.django_db
class TestProfile:
    def test_coach_and_teacher_apart(self, user, other_user) -> None:
        teacher = _user("ustoz")
        room = Classroom.objects.create(name="A", slug="a", owner=teacher)
        ClassroomMember.objects.create(classroom=room, user=user)
        _active(user, other_user)
        body = APIClient().get(reverse("user-profile", args=[user.username])).json()
        assert [row["username"] for row in body["coach"]] == [other_user.username]
        assert [row["username"] for row in body["teacher"]] == ["ustoz"]

    def test_pending_coach_is_not_shown(self, user, other_user) -> None:
        _ask(user, other_user)
        body = APIClient().get(reverse("user-profile", args=[user.username])).json()
        assert body["coach"] == []


@pytest.mark.django_db
def test_hidden_coach_hides_the_teacher_too() -> None:
    from importlib import import_module
    from types import SimpleNamespace

    from django.apps import apps as global_apps
    from django.db import connection

    migration = import_module("coaching.migrations.0002_hide_teacher_too")
    hid = _user("hid", hidden_fields=["email", "coach"])
    shown = _user("shown", hidden_fields=["email"])
    # The step only reads `schema_editor.connection` (to pick the query).
    editor = SimpleNamespace(connection=connection)
    migration.forwards(global_apps, editor)
    hid.refresh_from_db()
    shown.refresh_from_db()
    assert hid.hidden_fields == ["email", "coach", "teacher"]
    assert shown.hidden_fields == ["email"]
