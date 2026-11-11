"""Streak page, region map, "my content" (decision 2026-11-11 ④)."""

from __future__ import annotations

from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from community.models import Comment, Entry, Report
from core.models import User
from problems.models import ProblemReport
from qvant.models import ShopItem


def _client(user: User | None = None) -> APIClient:
    client = APIClient()
    if user is not None:
        client.force_authenticate(user)
    return client


@pytest.mark.django_db
class TestStreak:
    def test_alive_streak_and_milestones(self, user) -> None:
        today = timezone.localdate()
        User.objects.filter(pk=user.pk).update(
            streak_count=8,
            streak_max=12,
            last_active_date=today,
            streak_freeze_until=today + timedelta(days=1),
        )
        ShopItem.objects.create(
            code="freeze", category="streak_freeze", title_uz="Muzlatgich", price=50
        )
        body = _client(user).get(reverse("qvant-streak")).json()
        assert (body["current"], body["longest"], body["active_today"]) == (8, 12, True)
        assert body["milestones"] == [3, 7, 14, 30, 100, 365]
        assert body["freeze"] == {"code": "freeze", "price": 50}
        assert body["freeze_until"] == str(today + timedelta(days=1))

    def test_broken_streak_reads_zero(self, user) -> None:
        User.objects.filter(pk=user.pk).update(
            streak_count=5, streak_max=5, last_active_date=timezone.localdate() - timedelta(days=3)
        )
        body = _client(user).get(reverse("qvant-streak")).json()
        assert (body["current"], body["longest"], body["active_today"]) == (0, 5, False)
        assert body["freeze_until"] is None and body["freeze"] is None

    def test_needs_a_session(self) -> None:
        assert _client().get(reverse("qvant-streak")).status_code in (401, 403)


@pytest.mark.django_db
class TestRegions:
    def test_counts_active_members_per_region(self, user, other_user) -> None:
        today = timezone.localdate()
        User.objects.filter(pk=user.pk).update(
            country="UZ", region="samarqand", last_active_date=today
        )
        User.objects.filter(pk=other_user.pk).update(
            country="UZ", region="samarqand", last_active_date=today - timedelta(days=20)
        )
        week = _client().get(reverse("region-activity"), {"days": 7}).json()
        month = _client().get(reverse("region-activity"), {"days": 30}).json()
        assert (week["days"], week["total"]) == (7, 1)
        assert next(r for r in month["regions"] if r["code"] == "samarqand")["users"] == 2
        assert len(month["regions"]) == 14

    def test_unknown_period_falls_back(self) -> None:
        assert _client().get(reverse("region-activity"), {"days": 5}).json()["days"] == 30


@pytest.mark.django_db
class TestMyContent:
    def test_reports_about_my_problems_entries_and_comments(
        self, user, other_user, problem
    ) -> None:
        problem.authors.add(user)
        ProblemReport.objects.create(
            problem=problem, user=other_user, reason="tests", comment="3-test xato"
        )
        entry = Entry.objects.create(author=user, title="Post", body="matn matn")
        comment = Comment.objects.create(
            target_type="problem", target_id=problem.pk, author=user, body="izoh matni"
        )
        Report.objects.create(reporter=other_user, kind="entry", object_id=entry.pk, reason="spam")
        Report.objects.create(
            reporter=other_user, kind="comment", object_id=comment.pk, reason="rude"
        )
        rows = _client(user).get(reverse("my-content-reports")).json()
        assert sorted(r["kind"] for r in rows) == ["comment", "entry", "problem"]
        links = {r["kind"]: r["link"] for r in rows}
        assert links["entry"] == f"/blogs/{entry.pk}"
        assert links["comment"] == f"/problems/{problem.slug}?tab=discussion#c{comment.pk}"
        assert all("reporter" not in r and other_user.username not in str(r) for r in rows)

    def test_others_see_nothing_of_mine(self, user, other_user, problem) -> None:
        entry = Entry.objects.create(author=user, title="Post", body="matn matn")
        Report.objects.create(reporter=other_user, kind="entry", object_id=entry.pk, reason="spam")
        assert _client(other_user).get(reverse("my-content-reports")).json() == []
