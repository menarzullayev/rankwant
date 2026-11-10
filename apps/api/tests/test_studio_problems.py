"""`/studio/problems` backend (2026-11-10): draft cap, review request, tests.

Measured before this change: an author could add a test to a draft but not
remove one (DELETE 403), had no way to tell staff a draft was ready, and
nothing capped how many drafts one account could create.
"""

from __future__ import annotations

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from core.models import User
from notifications.models import Notification
from problems import author_views
from problems.models import Problem, TestCase


def _client(user: User) -> APIClient:
    c = APIClient()
    c.force_authenticate(user=user)
    return c


@pytest.fixture
def fake_problem_s3(monkeypatch) -> dict[str, str]:
    from problems import storage

    uploaded: dict[str, str] = {}

    def put(key: str, content: str) -> str:
        uploaded[key] = content
        return f"s3://rankwant/{key}"

    monkeypatch.setattr(storage, "ensure_bucket", lambda: None)
    monkeypatch.setattr(storage, "put_test_data", put)
    return uploaded


def _draft(user: User, slug: str = "yigindi", statement: str = "a+b") -> Problem:
    res = _client(user).post(
        reverse("mine-problem-list"),
        {"slug": slug, "title": "Yig'indi", "statement": statement, "difficulty": 800},
        format="json",
    )
    assert res.status_code == 201, res.content
    return Problem.objects.get(slug=slug)


def _test(problem: Problem, order: int, *, sample: bool) -> None:
    TestCase.objects.create(
        problem=problem,
        order=order,
        input_ref=f"s3://rankwant/t/{order}.in",
        output_ref=f"s3://rankwant/t/{order}.out",
        is_sample=sample,
        group="sample" if sample else "unclassified",
    )


@pytest.mark.django_db
class TestDraftFields:
    def test_sections_are_writable_limits_are_not(self, user) -> None:
        problem = _draft(user)
        res = _client(user).patch(
            reverse("mine-problem-detail", args=[problem.slug]),
            {
                "input_format": "n",
                "output_format": "son",
                "note": "izoh",
                "time_limit_ms": 99999,
                "review_requested_at": "2026-01-01T00:00:00Z",
            },
            format="json",
        )
        assert res.status_code == 200, res.content
        body = res.json()
        assert (body["input_format"], body["output_format"], body["note"]) == ("n", "son", "izoh")
        assert body["time_limit_ms"] == 1000
        assert body["review_requested_at"] is None

    def test_list_counts_samples_and_hidden(self, user) -> None:
        problem = _draft(user)
        _test(problem, 1, sample=True)
        _test(problem, 2, sample=False)
        _test(problem, 3, sample=False)
        row = _client(user).get(reverse("mine-problem-list")).json()["results"][0]
        assert (row["sample_count"], row["hidden_count"]) == (1, 2)


@pytest.mark.django_db
class TestDraftLimit:
    def test_cap_refuses_the_next_draft(self, user, monkeypatch) -> None:
        monkeypatch.setattr(author_views, "MAX_DRAFTS", 2)
        _draft(user, "a1")
        _draft(user, "a2")
        res = _client(user).post(
            reverse("mine-problem-list"),
            {"slug": "a3", "title": "T", "statement": "s", "difficulty": 800},
            format="json",
        )
        assert res.status_code == 400
        assert res.json()["error"]["code"] == "draft_limit"
        assert not Problem.objects.filter(slug="a3").exists()

    def test_published_problems_do_not_count(self, user, monkeypatch) -> None:
        monkeypatch.setattr(author_views, "MAX_DRAFTS", 1)
        Problem.objects.filter(pk=_draft(user, "a1").pk).update(is_public=True)
        _draft(user, "a2")

    def test_staff_are_exempt(self, monkeypatch) -> None:
        monkeypatch.setattr(author_views, "MAX_DRAFTS", 1)
        staff = User.objects.create_user("ops", password="x", is_staff=True)
        _draft(staff, "a1")
        _draft(staff, "a2")


@pytest.mark.django_db
class TestReview:
    def test_gaps_are_named(self, user) -> None:
        # The API refuses a blank statement; a draft can still hold one
        # (created in the admin, imported), so the review checks it too.
        problem = _draft(user)
        Problem.objects.filter(pk=problem.pk).update(statement="  ")
        res = _client(user).post(reverse("mine-problem-review", args=[problem.slug]))
        assert res.status_code == 400
        error = res.json()["error"]
        assert error["code"] == "review_not_ready"
        assert error["details"]["missing"] == ["statement", "sample_test", "hidden_test"]
        problem.refresh_from_db()
        assert problem.review_requested_at is None

    def test_hidden_test_is_required(self, user) -> None:
        problem = _draft(user)
        _test(problem, 1, sample=True)
        res = _client(user).post(reverse("mine-problem-review", args=[problem.slug]))
        assert res.json()["error"]["details"]["missing"] == ["hidden_test"]

    def test_ready_draft_reaches_staff_ops_once(self, user) -> None:
        ops = User.objects.create_user("ops", password="x", is_staff=True)
        support_only = User.objects.create_user("sup", password="x", is_staff=True)
        support_only.groups.clear()
        problem = _draft(user)
        _test(problem, 1, sample=True)
        _test(problem, 2, sample=False)

        first = _client(user).post(reverse("mine-problem-review", args=[problem.slug]))
        assert first.status_code == 200, first.content
        assert first.json()["review_requested_at"]
        second = _client(user).post(reverse("mine-problem-review", args=[problem.slug]))
        assert second.json()["review_requested_at"] == first.json()["review_requested_at"]

        rows = Notification.objects.filter(code="problem_review_requested")
        assert [row.user for row in rows] == [ops]
        row = rows.get()
        assert row.kind == Notification.Kind.SYSTEM
        assert (row.ref_type, row.ref_id) == ("problem_review", problem.slug)
        assert row.params == {"problem": "Yig'indi", "user": user.username}

    def test_other_users_draft_is_not_found(self, user, other_user) -> None:
        problem = _draft(user)
        res = _client(other_user).post(reverse("mine-problem-review", args=[problem.slug]))
        assert res.status_code == 404

    def test_published_problem_is_refused(self, user) -> None:
        problem = _draft(user)
        Problem.objects.filter(pk=problem.pk).update(is_public=True)
        res = _client(user).post(reverse("mine-problem-review", args=[problem.slug]))
        assert res.json()["error"]["code"] == "already_public"

    def test_editing_keeps_the_request(self, user) -> None:
        problem = _draft(user)
        _test(problem, 1, sample=True)
        _test(problem, 2, sample=False)
        _client(user).post(reverse("mine-problem-review", args=[problem.slug]))
        body = (
            _client(user)
            .patch(reverse("mine-problem-detail", args=[problem.slug]), {"title": "Yangi"})
            .json()
        )
        assert body["review_requested_at"]


@pytest.mark.django_db
class TestAuthorTests:
    def test_author_deletes_a_draft_test(self, user, fake_problem_s3) -> None:
        problem = _draft(user)
        c = _client(user)
        url = reverse("staff-problem-tests", args=[problem.slug])
        assert c.post(url, {"order": 1, "input": "1 2", "expected": "3"}).status_code == 201
        delete = reverse("staff-problem-delete-test", args=[problem.slug, 1])
        assert c.delete(delete).status_code == 204
        assert not problem.tests.exists()

    def test_other_user_cannot_delete(self, user, other_user) -> None:
        problem = _draft(user)
        _test(problem, 1, sample=False)
        delete = reverse("staff-problem-delete-test", args=[problem.slug, 1])
        assert _client(other_user).delete(delete).status_code == 403
        assert problem.tests.exists()

    def test_published_problem_tests_stay_with_staff(self, user) -> None:
        problem = _draft(user)
        _test(problem, 1, sample=False)
        Problem.objects.filter(pk=problem.pk).update(is_public=True)
        delete = reverse("staff-problem-delete-test", args=[problem.slug, 1])
        assert _client(user).delete(delete).status_code == 403

    def test_author_still_cannot_edit_the_problem_as_staff(self, user) -> None:
        problem = _draft(user)
        res = _client(user).patch(
            reverse("staff-problem-detail", args=[problem.slug]), {"is_public": True}
        )
        assert res.status_code == 403


@pytest.mark.django_db
class TestStaffQueue:
    def test_queue_lists_requested_drafts_with_authors(self, user) -> None:
        ops = User.objects.create_user("ops", password="x", is_staff=True)
        waiting = _draft(user, "kutyapti")
        _draft(user, "jim")
        Problem.objects.filter(pk=waiting.pk).update(review_requested_at="2026-11-10T10:00:00Z")
        published = _draft(user, "chiqqan")
        Problem.objects.filter(pk=published.pk).update(
            review_requested_at="2026-11-10T10:00:00Z", is_public=True
        )

        rows = _client(ops).get(reverse("staff-problem-list"), {"review": "1"}).json()["results"]
        assert [row["slug"] for row in rows] == ["kutyapti"]
        assert rows[0]["authors"] == [user.username]
        assert rows[0]["review_requested_at"]

        everything = _client(ops).get(reverse("staff-problem-list")).json()["count"]
        assert everything == 3


@pytest.mark.django_db
def test_published_problem_is_not_edited_by_its_author(user) -> None:
    problem = _draft(user)
    Problem.objects.filter(pk=problem.pk).update(is_public=True)
    res = _client(user).patch(
        reverse("mine-problem-detail", args=[problem.slug]), {"statement": "boshqa"}
    )
    assert res.status_code == 403
    problem.refresh_from_db()
    assert problem.statement == "a+b"
