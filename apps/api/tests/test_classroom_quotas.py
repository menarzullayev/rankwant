"""Plan quotas and the classroom's join requests, roles and management (ADR-0061 § 2–3)."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from classroom.models import Assignment, Classroom, ClassroomJoinRequest, ClassroomMember
from core import quotas
from core.models import PlanQuota, User
from notifications.models import Notification
from problems.models import Problem
from tests.quota_utils import set_free_quota


def _client(user: User) -> APIClient:
    client = APIClient()
    client.force_authenticate(user)
    return client


def _user(name: str, **extra: Any) -> User:
    return User.objects.create_user(username=name, password="x", **extra)


def _room(owner: User, slug: str = "9a", **extra: object) -> Classroom:
    return Classroom.objects.create(owner=owner, name="9-A", slug=slug, **extra)


def _detail(room: Classroom) -> str:
    return reverse("classroom-detail", args=[room.slug])


@pytest.mark.django_db
class TestQuotaService:
    def test_free_defaults(self, user) -> None:
        assert quotas.limit(user, "classrooms") == 3
        assert quotas.limit(user, "class_members") == 40
        assert quotas.limit(user, "problems") == 20

    def test_admin_row_wins(self, user) -> None:
        set_free_quota(classrooms=7)
        assert quotas.limit(user, "classrooms") == 7

    def test_judge_plan(self, user) -> None:
        User.objects.filter(pk=user.pk).update(plan="judge")
        user.refresh_from_db()
        assert quotas.limit(user, "classrooms") == 50

    def test_expired_plan_is_free(self, user) -> None:
        User.objects.filter(pk=user.pk).update(
            plan="judge", plan_expires_at=timezone.now() - timedelta(days=1)
        )
        user.refresh_from_db()
        assert quotas.plan_of(user) == "free"
        assert quotas.limit(user, "classrooms") == 3

    def test_staff_have_no_limit(self) -> None:
        staff = _user("ops", is_staff=True)
        assert quotas.limit(staff, "classrooms") is None
        quotas.enforce(staff, "classrooms")

    def test_unknown_key_is_an_error(self, user) -> None:
        with pytest.raises(KeyError):
            quotas.limit(user, "videos")

    def test_seeded_rows(self) -> None:
        # Migration `core.0038` writes one row per plan.
        assert set(PlanQuota.objects.values_list("plan", flat=True)) >= {"free", "judge"}

    def test_me_quotas(self, user, problem) -> None:
        problem.authors.add(user)
        _room(user)
        _room(user, "9b", is_active=False)
        body = _client(user).get(reverse("me-quotas")).json()
        rows = {row["key"]: row for row in body["quotas"]}
        assert body["plan"] == "free"
        assert rows["problems"] == {"key": "problems", "limit": 20, "used": 1}
        # An archived classroom frees its place.
        assert rows["classrooms"]["used"] == 1
        assert rows["contests"]["used"] == 0

    def test_me_quotas_needs_a_session(self) -> None:
        assert APIClient().get(reverse("me-quotas")).status_code in (401, 403)


@pytest.mark.django_db
class TestClassroomQuota:
    def test_fourth_classroom_is_refused(self, user) -> None:
        client = _client(user)
        for i in range(3):
            res = client.post(reverse("classroom-list"), {"slug": f"s{i}", "name": "S"})
            assert res.status_code == 201, res.content
        res = client.post(reverse("classroom-list"), {"slug": "s3", "name": "S"})
        assert res.status_code == 400
        assert res.json()["error"]["code"] == "quota_exceeded"
        assert res.json()["error"]["details"] == {"quota": "classrooms", "limit": 3}

    def test_archiving_frees_a_place(self, user) -> None:
        set_free_quota(classrooms=1)
        client = _client(user)
        assert client.post(reverse("classroom-list"), {"slug": "a", "name": "A"}).status_code == 201
        assert client.delete(_detail(Classroom.objects.get(slug="a"))).status_code == 204
        assert client.post(reverse("classroom-list"), {"slug": "b", "name": "B"}).status_code == 201

    def test_archive_keeps_the_rows(self, user, other_user, problem) -> None:
        room = _room(user)
        ClassroomMember.objects.create(classroom=room, user=other_user)
        Assignment.objects.create(classroom=room, title="T")
        assert _client(user).delete(_detail(room)).status_code == 204
        room.refresh_from_db()
        assert room.is_active is False
        assert room.members.count() == 1
        assert room.assignments.count() == 1

    def test_reserved_slug(self, user) -> None:
        res = _client(user).post(reverse("classroom-list"), {"slug": "join", "name": "J"})
        assert res.status_code == 400

    def test_new_classroom_asks_for_approval(self, user) -> None:
        _client(user).post(reverse("classroom-list"), {"slug": "a", "name": "A"})
        assert Classroom.objects.get(slug="a").join_mode == Classroom.JoinMode.APPROVAL


@pytest.mark.django_db
class TestJoinRequests:
    def test_request_waits_and_notifies(self, user, other_user) -> None:
        room = _room(user)
        res = _client(other_user).post(reverse("classroom-join"), {"join_code": room.join_code})
        assert res.status_code == 202
        assert res.json()["status"] == "pending"
        assert res.json()["slug"] == room.slug
        assert not room.members.exists()
        note = Notification.objects.get(user=user)
        assert note.code == "classroom_join_requested"
        assert note.params == {"classroom": "9-A", "user": other_user.username}
        assert (note.ref_type, note.ref_id) == ("classroom", room.slug)

    def test_asking_twice_notifies_once(self, user, other_user) -> None:
        room = _room(user)
        for _ in range(2):
            _client(other_user).post(reverse("classroom-join"), {"join_code": room.join_code})
        assert Notification.objects.filter(user=user).count() == 1

    def test_approve(self, user, other_user) -> None:
        room = _room(user)
        _client(other_user).post(reverse("classroom-join"), {"join_code": room.join_code})
        req = ClassroomJoinRequest.objects.get()
        url = reverse("classroom-approve", args=[room.slug, req.pk])
        assert _client(user).post(url).status_code == 200
        assert room.members.filter(user=other_user).exists()
        note = Notification.objects.get(user=other_user)
        assert note.code == "classroom_join_approved"
        assert note.ref_type == "classroom"
        # Answered once: a second answer is refused.
        assert _client(user).post(url).json()["error"]["code"] == "request_answered"

    def test_reject_has_no_link_and_can_be_asked_again(self, user, other_user) -> None:
        room = _room(user)
        client = _client(other_user)
        client.post(reverse("classroom-join"), {"join_code": room.join_code})
        req = ClassroomJoinRequest.objects.get()
        assert (
            _client(user).post(reverse("classroom-reject", args=[room.slug, req.pk])).status_code
            == 200
        )
        assert not room.members.exists()
        note = Notification.objects.get(user=other_user)
        assert note.code == "classroom_join_rejected"
        # The student cannot open the classroom, so the notice links nowhere.
        assert (note.ref_type, note.ref_id) == ("", "")
        # Straight back: refused, so a declined student cannot ring the
        # teacher once per request.
        again = client.post(reverse("classroom-join"), {"join_code": room.join_code})
        assert again.json()["error"]["code"] == "request_answered"
        assert Notification.objects.filter(user=user).count() == 1
        ClassroomJoinRequest.objects.filter(pk=req.pk).update(
            decided_at=timezone.now() - timedelta(days=2)
        )
        again = client.post(reverse("classroom-join"), {"join_code": room.join_code})
        assert again.status_code == 202
        req.refresh_from_db()
        assert req.status == ClassroomJoinRequest.Status.PENDING
        assert Notification.objects.filter(user=user).count() == 2

    def test_a_student_cannot_answer(self, user, other_user) -> None:
        room = _room(user)
        stranger = _user("s1")
        ClassroomMember.objects.create(classroom=room, user=stranger)
        _client(other_user).post(reverse("classroom-join"), {"join_code": room.join_code})
        req = ClassroomJoinRequest.objects.get()
        res = _client(stranger).post(reverse("classroom-approve", args=[room.slug, req.pk]))
        assert res.status_code == 403
        assert (
            _client(stranger).get(reverse("classroom-requests", args=[room.slug])).status_code
            == 403
        )

    def test_another_classroom_request_is_404(self, user, other_user) -> None:
        mine = _room(user)
        theirs = _room(_user("t1"), "9b")
        _client(other_user).post(reverse("classroom-join"), {"join_code": theirs.join_code})
        req = ClassroomJoinRequest.objects.get()
        res = _client(user).post(reverse("classroom-approve", args=[mine.slug, req.pk]))
        assert res.status_code == 404
        assert not theirs.members.exists()

    def test_instant_classroom_lets_in(self, user, other_user) -> None:
        room = _room(user, join_mode="instant")
        res = _client(other_user).post(reverse("classroom-join"), {"join_code": room.join_code})
        assert res.status_code == 201
        assert res.json()["status"] == "member"
        assert room.members.filter(user=other_user).exists()


@pytest.mark.django_db
class TestClassroomFull:
    def test_instant_join_past_the_limit(self, user, other_user) -> None:
        set_free_quota(class_members=1)
        room = _room(user, join_mode="instant")
        ClassroomMember.objects.create(classroom=room, user=_user("s1"))
        res = _client(other_user).post(reverse("classroom-join"), {"join_code": room.join_code})
        assert res.status_code == 400
        assert res.json()["error"]["code"] == "classroom_full"

    def test_full_classroom_still_queues_a_request(self, user, other_user) -> None:
        set_free_quota(class_members=1)
        room = _room(user)
        ClassroomMember.objects.create(classroom=room, user=_user("s1"))
        res = _client(other_user).post(reverse("classroom-join"), {"join_code": room.join_code})
        assert res.status_code == 202

    def test_approve_past_the_limit(self, user, other_user) -> None:
        set_free_quota(class_members=1)
        room = _room(user)
        _client(other_user).post(reverse("classroom-join"), {"join_code": room.join_code})
        ClassroomMember.objects.create(classroom=room, user=_user("s1"))
        req = ClassroomJoinRequest.objects.get()
        res = _client(user).post(reverse("classroom-approve", args=[room.slug, req.pk]))
        assert res.json()["error"]["code"] == "classroom_full"
        req.refresh_from_db()
        assert req.status == ClassroomJoinRequest.Status.PENDING

    def test_assistants_take_no_seat(self, user, other_user) -> None:
        set_free_quota(class_members=1)
        room = _room(user, join_mode="instant")
        ClassroomMember.objects.create(
            classroom=room, user=_user("a1"), role=ClassroomMember.Role.ASSISTANT
        )
        res = _client(other_user).post(reverse("classroom-join"), {"join_code": room.join_code})
        assert res.status_code == 201
        assert _client(user).get(_detail(room)).json()["member_count"] == 1

    def test_the_owners_plan_decides(self, user, other_user) -> None:
        set_free_quota(class_members=1)
        User.objects.filter(pk=user.pk).update(plan="judge")
        room = _room(user, join_mode="instant")
        ClassroomMember.objects.create(classroom=room, user=_user("s1"))
        res = _client(other_user).post(reverse("classroom-join"), {"join_code": room.join_code})
        assert res.status_code == 201


@pytest.mark.django_db
class TestRoles:
    def _setup(self, user: User) -> tuple[Classroom, User, User]:
        room = _room(user)
        helper = _user("helper")
        student = _user("pupil")
        ClassroomMember.objects.create(
            classroom=room, user=helper, role=ClassroomMember.Role.ASSISTANT
        )
        ClassroomMember.objects.create(classroom=room, user=student)
        return room, helper, student

    def test_my_role(self, user) -> None:
        room, helper, student = self._setup(user)
        for who, role in ((user, "owner"), (helper, "assistant"), (student, "student")):
            assert _client(who).get(_detail(room)).json()["my_role"] == role

    def test_what_each_role_sees(self, user) -> None:
        room, helper, student = self._setup(user)
        owner_view = _client(user).get(_detail(room)).json()
        helper_view = _client(helper).get(_detail(room)).json()
        student_view = _client(student).get(_detail(room)).json()
        assert owner_view["join_code"] == room.join_code
        assert "join_code" not in helper_view
        assert len(helper_view["members"]) == 2
        assert helper_view["pending_count"] == 0
        assert "members" not in student_view
        assert "join_code" not in student_view
        # Everyone sees the same count of students, not their own row.
        assert {owner_view["member_count"], helper_view["member_count"]} == {1}
        assert student_view["member_count"] == 1
        listed = _client(helper).get(reverse("classroom-list")).json()
        assert [row["member_count"] for row in listed] == [1]

    def test_assistant_answers_requests(self, user, other_user) -> None:
        room, helper, _ = self._setup(user)
        _client(other_user).post(reverse("classroom-join"), {"join_code": room.join_code})
        # The owner and the assistant both hear of it.
        assert Notification.objects.filter(code="classroom_join_requested").count() == 2
        rows = _client(helper).get(reverse("classroom-requests", args=[room.slug])).json()
        assert [row["username"] for row in rows] == [other_user.username]
        url = reverse("classroom-approve", args=[room.slug, rows[0]["id"]])
        assert _client(helper).post(url).status_code == 200

    def test_assistant_does_not_manage(self, user, problem) -> None:
        room, helper, student = self._setup(user)
        client = _client(helper)
        member = reverse("classroom-member", args=[room.slug, student.username])
        assert client.patch(member, {"role": "assistant"}, format="json").status_code == 403
        assert client.delete(member).status_code == 403
        assert client.post(reverse("classroom-refresh-code", args=[room.slug])).status_code == 403
        assert (
            client.patch(_detail(room), {"join_mode": "instant"}, format="json").status_code == 404
        )
        assert client.delete(_detail(room)).status_code == 404
        # Reports stay with the owner (decision 2026-11-10).
        assignment = Assignment.objects.create(classroom=room, title="T")
        assignment.problems.add(problem)
        progress = reverse("classroom-progress", args=[room.slug, assignment.pk])
        assert client.get(progress).status_code == 403

    def test_owner_sets_roles(self, user) -> None:
        room, _, student = self._setup(user)
        url = reverse("classroom-member", args=[room.slug, student.username])
        assert _client(user).patch(url, {"role": "assistant"}, format="json").status_code == 200
        assert room.members.get(user=student).role == ClassroomMember.Role.ASSISTANT
        res = _client(user).patch(url, {"role": "owner"}, format="json")
        assert res.status_code == 400

    def test_owner_removes(self, user) -> None:
        room, _, student = self._setup(user)
        url = reverse("classroom-member", args=[room.slug, student.username])
        assert _client(user).delete(url).status_code == 204
        assert not room.members.filter(user=student).exists()
        assert _client(user).delete(url).json()["error"]["code"] == "not_a_member"
        # Removed is not let back in by the old code at once.
        again = _client(student).post(reverse("classroom-join"), {"join_code": room.join_code})
        assert again.json()["error"]["code"] == "request_answered"

    def test_progress_counts_students_only(self, user, problem) -> None:
        room, _, student = self._setup(user)
        assignment = Assignment.objects.create(classroom=room, title="T")
        assignment.problems.add(problem)
        rows = _client(user).get(reverse("classroom-progress", args=[room.slug, assignment.pk]))
        assert [row["username"] for row in rows.json()["results"]] == [student.username]

    def test_join_mode_is_the_owners(self, user) -> None:
        room, _, _ = self._setup(user)
        res = _client(user).patch(_detail(room), {"join_mode": "instant"}, format="json")
        assert res.status_code == 200
        room.refresh_from_db()
        assert room.join_mode == Classroom.JoinMode.INSTANT


@pytest.mark.django_db
class TestLeaveAndCode:
    def test_student_leaves(self, user, other_user) -> None:
        room = _room(user)
        ClassroomMember.objects.create(classroom=room, user=other_user)
        res = _client(other_user).post(reverse("classroom-leave", args=[room.slug]))
        assert res.status_code == 204
        assert not room.members.exists()

    def test_owner_cannot_leave(self, user) -> None:
        room = _room(user)
        res = _client(user).post(reverse("classroom-leave", args=[room.slug]))
        assert res.json()["error"]["code"] == "owner_leaves"

    def test_new_code_retires_the_old_one(self, user, other_user) -> None:
        room = _room(user, join_mode="instant")
        old = room.join_code
        res = _client(user).post(reverse("classroom-refresh-code", args=[room.slug]))
        new = res.json()["join_code"]
        assert new != old
        client = _client(other_user)
        assert client.get(reverse("classroom-invite", args=[old])).status_code == 404
        assert client.post(reverse("classroom-join"), {"join_code": old}).status_code == 400
        assert client.post(reverse("classroom-join"), {"join_code": new}).status_code == 201

    def test_invite_preview(self, user, other_user) -> None:
        room = _room(user)
        url = reverse("classroom-invite", args=[room.join_code])
        body = _client(other_user).get(url).json()
        assert body == {
            "slug": room.slug,
            "name": "9-A",
            "owner": user.username,
            "join_mode": "approval",
            "member_count": 0,
            "state": "",
        }
        _client(other_user).post(reverse("classroom-join"), {"join_code": room.join_code})
        assert _client(other_user).get(url).json()["state"] == "pending"
        assert _client(user).get(url).json()["state"] == "owner"

    def test_archived_invite_is_404(self, user, other_user) -> None:
        room = _room(user, is_active=False)
        res = _client(other_user).get(reverse("classroom-invite", args=[room.join_code]))
        assert res.status_code == 404


@pytest.mark.django_db
class TestProblemAssignment:
    def _post(self, user: User, room: Classroom, problems: list[str]):
        return _client(user).post(
            reverse("classroom-assignments", args=[room.slug]),
            {"title": "T", "problems": problems},
            format="json",
        )

    def test_numbers_and_slugs(self, user, problem) -> None:
        other = Problem.objects.create(
            slug="b-plus-c", title="B", statement="s", difficulty=800, is_public=True, code=9001
        )
        res = self._post(user, _room(user), [f"#{problem.code}", "9001", problem.slug])
        assert res.status_code == 201, res.content
        assert sorted(res.json()["problems"]) == sorted([problem.slug, other.slug])

    def test_unknown_or_hidden_is_named(self, user, problem) -> None:
        Problem.objects.create(slug="hidden", title="H", statement="s", difficulty=800)
        res = self._post(user, _room(user), ["hidden", "#99999"])
        assert res.status_code == 400
        assert "hidden" in str(res.json())
        assert "#99999" in str(res.json())
        assert not Assignment.objects.exists()
