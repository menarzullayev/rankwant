"""`/studio/contests` backend (2026-11-10): what the organizer's page needs.

Measured before this change: `contests/mine/<slug>/participants/` answered
500, an end before the start was accepted, and only staff-ops could attach
problems to a contest.
"""

from __future__ import annotations

from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from contests import organizer_views
from contests.models import Contest, ContestRegistration
from core.models import User
from problems.models import Problem


def _client(user: User) -> APIClient:
    c = APIClient()
    c.force_authenticate(user=user)
    return c


def _payload(slug: str = "kubok", **extra) -> dict:
    start = timezone.now() + timedelta(days=7)
    return {
        "slug": slug,
        "title": "Kubok",
        "start_at": start.isoformat(),
        "end_at": (start + timedelta(hours=2)).isoformat(),
        **extra,
    }


def _contest(user: User, slug: str = "kubok") -> Contest:
    res = _client(user).post(reverse("mine-contest-list"), _payload(slug), format="json")
    assert res.status_code == 201, res.content
    return Contest.objects.get(slug=slug)


def _own_problem(user: User, slug: str, *, public: bool = False) -> Problem:
    problem = Problem.objects.create(
        slug=slug, title=slug.title(), statement="s", difficulty=800, is_public=public
    )
    problem.authors.add(user)
    return problem


@pytest.mark.django_db
class TestOrganizerContest:
    def test_end_before_start_is_refused(self, user) -> None:
        start = timezone.now() + timedelta(days=7)
        res = _client(user).post(
            reverse("mine-contest-list"),
            _payload(end_at=(start - timedelta(hours=1)).isoformat(), start_at=start.isoformat()),
            format="json",
        )
        assert res.status_code == 400
        assert "end_at" in res.json()["error"]["details"]

    def test_participants_answer(self, user, other_user) -> None:
        contest = _contest(user)
        ContestRegistration.objects.create(contest=contest, user=other_user)
        res = _client(user).get(reverse("mine-contest-participants", args=[contest.slug]))
        assert res.status_code == 200, res.content
        assert [row["username"] for row in res.json()] == [other_user.username]
        detail = _client(user).get(reverse("mine-contest-detail", args=[contest.slug])).json()
        assert detail["participant_count"] == 1

    def test_draft_cap(self, user, monkeypatch) -> None:
        monkeypatch.setattr(organizer_views, "MAX_DRAFTS", 1)
        _contest(user, "a1")
        res = _client(user).post(reverse("mine-contest-list"), _payload("a2"), format="json")
        assert res.status_code == 400
        assert res.json()["error"]["code"] == "contest_draft_limit"

    def test_staff_are_exempt_from_the_cap(self, monkeypatch) -> None:
        monkeypatch.setattr(organizer_views, "MAX_DRAFTS", 1)
        staff = User.objects.create_user("ops", password="x", is_staff=True)
        _contest(staff, "a1")
        _contest(staff, "a2")


@pytest.fixture
def gate_reports(settings):
    """Production runs with the readiness gate reporting, not refusing
    (`READINESS_ENFORCE=0`, 2026-11-10) — the attach tests run the same way."""
    settings.READINESS_ENFORCE = False


@pytest.mark.django_db
@pytest.mark.usefixtures("gate_reports")
class TestOrganizerProblems:
    def test_own_drafts_are_attached(self, user) -> None:
        contest = _contest(user)
        _own_problem(user, "birinchi")
        _own_problem(user, "ikkinchi")
        url = reverse("mine-contest-contest-problems", args=[contest.slug])
        res = _client(user).put(
            url,
            {
                "problems": [
                    {"problem": "birinchi", "index_letter": "A"},
                    {"problem": "ikkinchi", "index_letter": "B", "points": 200},
                ]
            },
            format="json",
        )
        assert res.status_code == 200, res.content
        assert [(r["problem"], r["index_letter"], r["points"]) for r in res.json()] == [
            ("birinchi", "A", 100),
            ("ikkinchi", "B", 200),
        ]
        detail = _client(user).get(reverse("mine-contest-detail", args=[contest.slug])).json()
        assert [row["problem"] for row in detail["problems"]] == ["birinchi", "ikkinchi"]

    def test_someone_elses_problem_is_refused(self, user, other_user) -> None:
        contest = _contest(user)
        _own_problem(other_user, "begona")
        res = _client(user).put(
            reverse("mine-contest-contest-problems", args=[contest.slug]),
            {"problems": [{"problem": "begona", "index_letter": "A"}]},
            format="json",
        )
        assert res.status_code == 400
        assert not contest.problems.exists()

    def test_published_problem_is_refused(self, user) -> None:
        # A published problem sits in the archive; a contest problem must not.
        contest = _contest(user)
        _own_problem(user, "ochiq", public=True)
        res = _client(user).put(
            reverse("mine-contest-contest-problems", args=[contest.slug]),
            {"problems": [{"problem": "ochiq", "index_letter": "A"}]},
            format="json",
        )
        assert res.status_code == 400

    def test_duplicate_letters_are_refused(self, user) -> None:
        contest = _contest(user)
        _own_problem(user, "p1")
        _own_problem(user, "p2")
        res = _client(user).put(
            reverse("mine-contest-contest-problems", args=[contest.slug]),
            {
                "problems": [
                    {"problem": "p1", "index_letter": "A"},
                    {"problem": "p2", "index_letter": "A"},
                ]
            },
            format="json",
        )
        assert res.status_code == 400

    def test_published_contest_is_locked(self, user) -> None:
        contest = _contest(user)
        _own_problem(user, "p1")
        Contest.objects.filter(pk=contest.pk).update(is_public=True)
        res = _client(user).put(
            reverse("mine-contest-contest-problems", args=[contest.slug]),
            {"problems": [{"problem": "p1", "index_letter": "A"}]},
            format="json",
        )
        assert res.status_code == 400
        assert res.json()["error"]["code"] == "contest_locked"

    def test_other_users_contest_is_not_found(self, user, other_user) -> None:
        contest = _contest(user)
        res = _client(other_user).get(reverse("mine-contest-contest-problems", args=[contest.slug]))
        assert res.status_code == 404


@pytest.mark.django_db
def test_enforced_readiness_gate_applies_here_too(user, settings) -> None:
    """Not a way around D8-F: with the gate on, a draft is refused here as on
    the staff surface."""
    settings.READINESS_ENFORCE = True
    contest = _contest(user)
    _own_problem(user, "p1")
    res = _client(user).put(
        reverse("mine-contest-contest-problems", args=[contest.slug]),
        {"problems": [{"problem": "p1", "index_letter": "A"}]},
        format="json",
    )
    assert res.status_code == 400
    assert "readiness" in str(res.json()["error"]["details"])


@pytest.mark.django_db
def test_staff_see_who_organized_a_draft(user) -> None:
    contest = _contest(user)
    ops = User.objects.create_user("ops", password="x", is_staff=True)
    rows = _client(ops).get(reverse("staff-contest-list")).json()["results"]
    row = next(row for row in rows if row["slug"] == contest.slug)
    assert row["organizers"] == [user.username]
