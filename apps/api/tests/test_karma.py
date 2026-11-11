"""Karma: all-time vote sum, top lists, profile (decision 2026-11-11 ③)."""

from __future__ import annotations

from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from community.karma import karma_of
from community.models import Comment, Entry, Vote
from core.models import User


def _client(user: User | None = None) -> APIClient:
    client = APIClient()
    if user is not None:
        client.force_authenticate(user)
    return client


def _people(n: int) -> list[User]:
    return [User.objects.create_user(username=f"k{i}", password="Parol!12345") for i in range(n)]


def _vote(voter: User, kind: str, pk: int, value: int) -> None:
    url = reverse("comment-vote" if kind == "comment" else "entry-vote", args=[pk])
    res = _client(voter).post(url, {"value": value}, format="json")
    assert res.status_code == 200, res.content


@pytest.mark.django_db
class TestKarma:
    def test_sum_of_votes_on_entries_and_comments(self, user, problem) -> None:
        a, b, c = _people(3)
        entry = Entry.objects.create(author=user, title="Post", body="matn matn")
        comment = Comment.objects.create(
            target_type="problem", target_id=problem.pk, author=user, body="izoh"
        )
        _vote(a, "entry", entry.pk, 1)
        _vote(b, "entry", entry.pk, 1)
        _vote(c, "comment", comment.pk, -1)
        assert karma_of(user.pk) == 1
        _vote(c, "comment", comment.pk, 1)
        assert karma_of(user.pk) == 3
        _vote(c, "comment", comment.pk, 0)
        assert karma_of(user.pk) == 2

    def test_all_time_top_skips_non_positive(self, user, other_user) -> None:
        voters = _people(3)
        mine = Entry.objects.create(author=user, title="Post", body="matn matn")
        theirs = Entry.objects.create(author=other_user, title="Post 2", body="matn matn")
        for voter in voters:
            _vote(voter, "entry", mine.pk, 1)
        _vote(voters[0], "entry", theirs.pk, -1)
        rows = _client().get(reverse("karma-top")).json()
        assert [(r["user"]["username"], r["karma"], r["entries"]) for r in rows] == [
            (user.username, 3, 1)
        ]

    def test_thirty_days_counts_recent_votes_only(self, user, other_user) -> None:
        voters = _people(2)
        old = Entry.objects.create(author=user, title="Eski", body="matn matn")
        new = Entry.objects.create(author=other_user, title="Yangi", body="matn matn")
        for voter in voters:
            _vote(voter, "entry", old.pk, 1)
        Vote.objects.filter(object_id=old.pk).update(created_at=timezone.now() - timedelta(days=40))
        _vote(voters[0], "entry", new.pk, 1)
        rows = _client().get(reverse("karma-top"), {"period": "30d"}).json()
        assert [(r["user"]["username"], r["points"], r["karma"]) for r in rows] == [
            (other_user.username, 1, 1)
        ]
        everyone = _client().get(reverse("karma-top")).json()
        assert [r["user"]["username"] for r in everyone] == [user.username, other_user.username]

    def test_profile_shows_karma_and_entries(self, user) -> None:
        (voter,) = _people(1)
        entry = Entry.objects.create(author=user, title="Post", body="matn matn")
        _vote(voter, "entry", entry.pk, 1)
        profile = _client().get(reverse("user-profile", args=[user.username])).json()
        assert (profile["karma"], profile["blog_entries"]) == (1, 1)
