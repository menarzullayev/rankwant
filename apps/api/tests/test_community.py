"""Problem discussion: tree, hidden code, votes, reports, limits (decision 2026-11-11)."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

import pytest
from django.contrib.auth.models import Group
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from community.models import Comment, Report, Vote
from community.services import AUTO_HIDE_REPORTS, HIDDEN_CODE, NEW_DAILY_COMMENTS, hide_code
from core.models import User
from core.permissions import STAFF_GROUP_CONTENT
from notifications.models import Notification
from problems.models import Problem
from ratings.models import UserSolvedProblem

CODE = "Mana:\n```cpp\nint main() { return 0; }\n```\nshunday."


def _client(user: User | None = None) -> APIClient:
    client = APIClient()
    if user is not None:
        client.force_authenticate(user)
    return client


def _old(user: User) -> User:
    """An account past its first week, with a confirmed e-mail."""
    User.objects.filter(pk=user.pk).update(
        date_joined=timezone.now() - timedelta(days=30), email_verified_at=timezone.now()
    )
    user.refresh_from_db()
    return user


def _url(problem: Problem) -> str:
    return reverse("problem-discussion", args=[problem.slug])


def _post(user: User, problem: Problem, body: str, parent: int | None = None) -> Any:
    data: dict[str, Any] = {"body": body}
    if parent is not None:
        data["reply_to"] = parent
    return _client(user).post(_url(problem), data, format="json")


@pytest.fixture
def writer(user) -> User:
    return _old(user)


@pytest.fixture
def reader(other_user) -> User:
    return _old(other_user)


@pytest.mark.django_db
class TestThread:
    def test_replies_form_a_tree(self, writer, reader, problem) -> None:
        root = _post(writer, problem, "Birinchi savol").json()
        reply = _post(reader, problem, "Javob", root["id"]).json()
        deeper = _post(writer, problem, "Javobga javob", reply["id"]).json()
        assert (reply["depth"], deeper["depth"]) == (1, 2)
        row = Comment.objects.get(pk=deeper["id"])
        assert row.root_id == root["id"] and row.parent_id == reply["id"]

        page = _client().get(_url(problem)).json()
        assert page["count"] == 3
        assert [c["id"] for c in page["comments"]] == [root["id"], reply["id"], deeper["id"]]

    def test_threads_page_newest_first(self, writer, problem) -> None:
        for i in range(22):
            Comment.objects.create(
                target_type="problem", target_id=problem.pk, author=writer, body=f"m {i}"
            )
        first = _client().get(_url(problem)).json()
        assert len(first["comments"]) == 20 and first["next"] is not None
        second = _client().get(_url(problem), {"before": first["next"]}).json()
        assert len(second["comments"]) == 2 and second["next"] is None

    def test_no_discussion_off_the_archive(self, writer, problem) -> None:
        Problem.objects.filter(pk=problem.pk).update(is_public=False)
        assert _client().get(_url(problem)).status_code == 404
        res = _post(writer, problem, "Salom")
        assert res.status_code == 404
        assert res.json()["error"]["code"] == "discussion_closed"

    def test_guest_reads_but_does_not_write(self, problem) -> None:
        assert _client().get(_url(problem)).status_code == 200
        assert _client().post(_url(problem), {"body": "x y"}, format="json").status_code in (
            401,
            403,
        )


@pytest.mark.django_db
class TestHiddenCode:
    def test_hide_code_swaps_fences(self) -> None:
        text, count = hide_code(CODE + "\n~~~\nprint(1)\n~~~")
        assert count == 2
        assert "int main" not in text and "print(1)" not in text
        assert text.count(HIDDEN_CODE) == 2

    def test_indented_and_long_inline_code_are_hidden(self) -> None:
        one_line = "`print(sum(map(int, open(0).read().split())))`"
        body = "Gap:\n\n    a = 1\n    print(a)\n\nva " + one_line + ", `n` qisqa"
        text, count = hide_code(body)
        assert count == 2
        assert "print(a)" not in text and "open(0)" not in text
        assert "`n`" in text

    def test_unclosed_fence_is_hidden_too(self) -> None:
        text, count = hide_code("a\n```\nsecret")
        assert count == 1 and "secret" not in text

    def test_code_is_closed_until_solved(self, writer, reader, problem) -> None:
        _post(writer, problem, CODE)
        guest = _client().get(_url(problem)).json()
        assert guest["code_open"] is False
        assert "int main" not in guest["comments"][0]["body"]
        assert guest["comments"][0]["hidden_code"] == 1

        UserSolvedProblem.objects.create(
            user=reader, problem=problem, difficulty_at_solve=problem.difficulty
        )
        seen = _client(reader).get(_url(problem)).json()
        assert seen["code_open"] is True
        assert "int main" in seen["comments"][0]["body"]

    def test_author_sees_own_code_and_badges(self, writer, reader, problem) -> None:
        problem.authors.add(reader)
        UserSolvedProblem.objects.create(
            user=writer, problem=problem, difficulty_at_solve=problem.difficulty
        )
        _post(writer, problem, CODE)
        _post(reader, problem, "Muallif javobi")
        rows = _client(writer).get(_url(problem)).json()["comments"]
        mine = next(c for c in rows if c["mine"])
        assert "int main" in mine["body"]
        assert mine["author_solved"] is True
        assert next(c for c in rows if not c["mine"])["author_owner"] is True


@pytest.mark.django_db
class TestVotes:
    def test_vote_change_and_take_back(self, writer, reader, problem) -> None:
        cid = _post(writer, problem, "Foydali izoh").json()["id"]
        url = reverse("comment-vote", args=[cid])
        assert _client(reader).post(url, {"value": 1}, format="json").json() == {
            "score": 1,
            "my_vote": 1,
        }
        assert _client(reader).post(url, {"value": -1}, format="json").json()["score"] == -1
        assert _client(reader).post(url, {"value": 0}, format="json").json()["score"] == 0
        assert not Vote.objects.exists()

    def test_vote_remembers_the_author_for_karma(self, writer, reader, problem) -> None:
        cid = _post(writer, problem, "Izoh").json()["id"]
        _client(reader).post(reverse("comment-vote", args=[cid]), {"value": 1}, format="json")
        assert Vote.objects.get().author_id == writer.pk

    def test_no_self_vote(self, writer, problem) -> None:
        cid = _post(writer, problem, "Izoh").json()["id"]
        res = _client(writer).post(reverse("comment-vote", args=[cid]), {"value": 1}, format="json")
        assert res.json()["error"]["code"] == "vote_self"


@pytest.mark.django_db
class TestModeration:
    def test_three_reports_hide_at_once(self, writer, problem) -> None:
        cid = _post(writer, problem, "Reklama!!!").json()["id"]
        url = reverse("comment-report", args=[cid])
        for i in range(AUTO_HIDE_REPORTS):
            person = _old(User.objects.create_user(username=f"r{i}", password="Parol!12345"))
            assert _client(person).post(url, {"reason": "spam"}, format="json").status_code == 201
            hidden = Comment.objects.get(pk=cid).is_hidden
            assert hidden is (i + 1 >= AUTO_HIDE_REPORTS)
        row = _client().get(_url(problem)).json()["comments"][0]
        assert row["is_hidden"] is True and row["body"] == ""

    def test_one_report_per_person(self, writer, reader, problem) -> None:
        cid = _post(writer, problem, "Izoh").json()["id"]
        url = reverse("comment-report", args=[cid])
        _client(reader).post(url, {"reason": "rude"}, format="json")
        again = _client(reader).post(url, {"reason": "rude"}, format="json")
        assert again.json()["error"]["code"] == "report_already"

    def test_staff_restores_and_rejects_reports(self, writer, reader, problem) -> None:
        cid = _post(writer, problem, "Izoh").json()["id"]
        _client(reader).post(
            reverse("comment-report", args=[cid]), {"reason": "spam"}, format="json"
        )
        Comment.objects.filter(pk=cid).update(is_hidden=True)
        staff = User.objects.create_user(username="mod", password="Parol!12345", is_staff=True)
        res = _client(staff).post(reverse("staff-comment-unhide", args=[cid]))
        assert res.status_code == 200 and res.json()["is_hidden"] is False
        assert Report.objects.get().status == "rejected"
        listed = _client(staff).get(reverse("staff-comment-list"), {"reported": "1"}).json()
        assert listed["results"][0]["link"].startswith(f"/problems/{problem.slug}?tab=discussion")

    def test_author_deletes_but_thread_stays(self, writer, reader, problem) -> None:
        root = _post(writer, problem, "Savol").json()
        _post(reader, problem, "Javob", root["id"])
        assert (
            _client(writer).delete(reverse("comment-detail", args=[root["id"]])).status_code == 204
        )
        rows = _client().get(_url(problem)).json()["comments"]
        assert rows[0]["is_deleted"] is True and rows[0]["body"] == "" and rows[0]["author"] is None
        assert rows[1]["body"] == "Javob"

    def test_only_the_author_edits(self, writer, reader, problem) -> None:
        cid = _post(writer, problem, "Savol").json()["id"]
        url = reverse("comment-detail", args=[cid])
        assert _client(reader).patch(url, {"body": "Buzish"}, format="json").status_code == 403
        res = _client(writer).patch(url, {"body": "Tahrir"}, format="json")
        assert res.json()["body"] == "Tahrir" and res.json()["edited_at"] is not None

    def test_moderator_sees_hidden_text(self, writer, problem) -> None:
        cid = _post(writer, problem, "Yashirin matn").json()["id"]
        Comment.objects.filter(pk=cid).update(is_hidden=True)
        moderator = User.objects.create_user(username="cm", password="Parol!12345", is_staff=True)
        moderator.groups.add(Group.objects.get_or_create(name=STAFF_GROUP_CONTENT)[0])
        row = _client(moderator).get(_url(problem)).json()["comments"][0]
        assert row["body"] == "Yashirin matn"


@pytest.mark.django_db
class TestLimits:
    def test_new_account_writes_five_a_day(self, user, problem) -> None:
        for i in range(NEW_DAILY_COMMENTS):
            assert _post(user, problem, f"Izoh {i}").status_code == 201
        res = _post(user, problem, "Yana bitta")
        assert res.json()["error"]["code"] == "comment_daily_limit"

    def test_link_needs_a_confirmed_email(self, user, problem) -> None:
        res = _post(user, problem, "Qarang: https://example.com")
        assert res.json()["error"]["code"] == "comment_link_unverified"
        _old(user)
        assert _post(user, problem, "Qarang: https://example.com").status_code == 201

    def test_too_short_and_reply_to_removed(self, writer, reader, problem) -> None:
        assert _post(writer, problem, "x").json()["error"]["code"] == "comment_short"
        cid = _post(writer, problem, "Savol").json()["id"]
        Comment.objects.filter(pk=cid).update(is_deleted=True)
        assert _post(reader, problem, "Javob", cid).json()["error"]["code"] == "comment_removed"


@pytest.mark.django_db
class TestNotifications:
    def test_reply_and_mention_notify_once(self, writer, reader, problem) -> None:
        third = _old(User.objects.create_user(username="sardor", password="Parol!12345"))
        root = _post(writer, problem, "Savol").json()
        _post(reader, problem, f"@{writer.username} @sardor @nobody javob", root["id"])
        codes = sorted(Notification.objects.values_list("user__username", "code"))
        assert codes == [(writer.username, "comment_reply"), (third.username, "comment_mention")]
        params = Notification.objects.get(code="comment_reply").params
        assert params["problem"] == problem.slug and params["user"] == reader.username

    def test_mention_in_code_does_not_notify(self, writer, reader, problem) -> None:
        _post(writer, problem, f"```\n@{reader.username}\n```")
        assert not Notification.objects.exists()
