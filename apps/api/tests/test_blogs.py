"""Member blogs: anyone writes, feed tabs, votes, reports, followers (decision 2026-11-11)."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from community.blog import NEW_DAILY_ENTRIES, clean_tags
from community.models import Comment, Entry
from community.services import AUTO_HIDE_REPORTS, CommunityError
from core.models import User
from notifications.models import Notification
from profiles.models import Follow


def _client(user: User | None = None) -> APIClient:
    client = APIClient()
    if user is not None:
        client.force_authenticate(user)
    return client


def _old(user: User) -> User:
    User.objects.filter(pk=user.pk).update(
        date_joined=timezone.now() - timedelta(days=30), email_verified_at=timezone.now()
    )
    user.refresh_from_db()
    return user


def _write(user: User, **data: Any) -> Any:
    body = {"title": "Segment daraxti", "body": "Lazy propagation haqida qisqa yozuv.", **data}
    return _client(user).post(reverse("entry-list"), body, format="json")


@pytest.fixture
def writer(user) -> User:
    return _old(user)


@pytest.fixture
def reader(other_user) -> User:
    return _old(other_user)


@pytest.mark.django_db
class TestWriting:
    def test_anyone_signed_in_writes(self, user) -> None:
        res = _write(user, tags=["DP", "#graph", "dp"])
        assert res.status_code == 201, res.content
        assert res.json()["tags"] == ["dp", "graph"]
        assert res.json()["author"]["username"] == user.username

    def test_guest_reads_but_does_not_write(self, writer) -> None:
        _write(writer)
        assert _client().get(reverse("entry-list")).json()["count"] == 1
        res = _client().post(reverse("entry-list"), {"title": "x", "body": "y"}, format="json")
        assert res.status_code in (401, 403)

    def test_new_account_one_a_day(self, user) -> None:
        for _ in range(NEW_DAILY_ENTRIES):
            assert _write(user).status_code == 201
        assert _write(user).json()["error"]["code"] == "entry_daily_limit"

    def test_link_needs_confirmed_email(self, user) -> None:
        res = _write(user, body="Qarang: https://example.com bu yerda")
        assert res.json()["error"]["code"] == "comment_link_unverified"

    def test_tags_are_checked(self) -> None:
        assert clean_tags("Segment Tree, dp") == ",segment-tree,dp,"
        with pytest.raises(CommunityError):
            clean_tags(["a", "b", "c", "d", "e", "f"])
        with pytest.raises(CommunityError):
            clean_tags(["bad tag!"])

    def test_only_the_author_edits_and_deletes(self, writer, reader) -> None:
        eid = _write(writer).json()["id"]
        url = reverse("entry-detail", args=[eid])
        edit = {"title": "Yangi sarlavha", "body": "Yangilangan matn shu yerda.", "tags": []}
        assert _client(reader).patch(url, edit, format="json").status_code == 403
        assert _client(writer).patch(url, edit, format="json").json()["title"] == "Yangi sarlavha"
        assert _client(writer).delete(url).status_code == 204
        assert _client().get(url).status_code == 404


@pytest.mark.django_db
class TestFeed:
    def test_tabs_and_filters(self, writer, reader) -> None:
        a = _write(writer, title="Birinchi post", tags=["dp"]).json()["id"]
        Entry.objects.create(author=reader, title="Ikkinchi", body="matn matn matn", tags=",graph,")
        everyone = _client().get(reverse("entry-list")).json()["results"]
        assert [e["title"] for e in everyone] == ["Ikkinchi", "Birinchi post"]
        dp = _client().get(reverse("entry-list"), {"tag": "dp"}).json()["results"]
        assert [e["id"] for e in dp] == [a]
        mine = _client().get(reverse("entry-list"), {"author": writer.username}).json()
        assert mine["count"] == 1

        _client(reader).post(reverse("entry-vote", args=[a]), {"value": 1}, format="json")
        top = _client().get(reverse("entry-list"), {"tab": "top"}).json()["results"]
        assert [e["id"] for e in top] == [a]

        Follow.objects.create(follower=reader, following=writer)
        following = _client(reader).get(reverse("entry-list"), {"tab": "following"}).json()
        assert [e["id"] for e in following["results"]] == [a]
        assert _client().get(reverse("entry-list"), {"tab": "following"}).json()["count"] == 0

    def test_views_count_once_and_not_the_author(self, writer, reader) -> None:
        eid = _write(writer).json()["id"]
        url = reverse("entry-detail", args=[eid])
        _client(writer).get(url)
        _client(reader).get(url)
        _client(reader).get(url)
        assert Entry.objects.get(pk=eid).view_count == 1

    def test_comment_count_and_discussion(self, writer, reader) -> None:
        eid = _write(writer).json()["id"]
        url = reverse("entry-discussion", args=[eid])
        res = _client(reader).post(url, {"body": "```\nkod\n```"}, format="json")
        assert res.status_code == 201
        # No problem behind an entry: code is open to everyone.
        assert "kod" in _client().get(url).json()["comments"][0]["body"]
        assert _client().get(reverse("entry-detail", args=[eid])).json()["comment_count"] == 1
        assert Comment.objects.get().target_type == "entry"


@pytest.mark.django_db
class TestVotesAndModeration:
    def test_plus_and_minus_for_everyone(self, writer, user) -> None:
        eid = _write(writer).json()["id"]
        newcomer = User.objects.create_user(username="yangi", password="Parol!12345")
        res = _client(newcomer).post(
            reverse("entry-vote", args=[eid]), {"value": -1}, format="json"
        )
        assert res.json() == {"score": -1, "my_vote": -1}

    def test_reports_hide_and_staff_restores(self, writer) -> None:
        eid = _write(writer).json()["id"]
        for i in range(AUTO_HIDE_REPORTS):
            person = _old(User.objects.create_user(username=f"rp{i}", password="Parol!12345"))
            _client(person).post(
                reverse("entry-report", args=[eid]), {"reason": "spam"}, format="json"
            )
        assert Entry.objects.get(pk=eid).is_hidden is True
        assert _client().get(reverse("entry-detail", args=[eid])).status_code == 404
        assert _client().get(reverse("entry-list")).json()["count"] == 0
        staff = User.objects.create_user(username="mod", password="Parol!12345", is_staff=True)
        res = _client(staff).post(reverse("staff-entry-unhide", args=[eid]))
        assert res.json()["is_hidden"] is False and res.json()["link"] == f"/blogs/{eid}"


@pytest.mark.django_db
class TestFollowers:
    def test_followers_hear_about_a_new_entry(
        self, writer, reader, django_capture_on_commit_callbacks
    ) -> None:
        Follow.objects.create(follower=reader, following=writer)
        with django_capture_on_commit_callbacks(execute=True):
            eid = _write(writer).json()["id"]
        note = Notification.objects.get(user=reader)
        assert note.code == "blog_entry"
        assert note.params == {
            "user": writer.username,
            "title": "Segment daraxti",
            "entry": str(eid),
        }
