"""The team page: what the public sees and what staff can manage."""

from __future__ import annotations

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from core.models import User
from core.permissions import STAFF_GROUP_CONTENT
from team.models import Department, Member, Role


@pytest.fixture
def client() -> APIClient:
    return APIClient()


@pytest.fixture
def editor(db) -> APIClient:
    from django.contrib.auth.models import Group

    user = User.objects.create_user(username="muharrir", password="Parol!12345", is_staff=True)
    user.groups.add(Group.objects.get_or_create(name=STAFF_GROUP_CONTENT)[0])
    api = APIClient()
    api.force_login(user)
    return api


@pytest.mark.django_db
class TestSeed:
    def test_the_page_starts_with_the_launch_content(self) -> None:
        assert Department.objects.count() == 12
        assert Role.objects.count() == 24
        founder = Member.objects.get()
        assert founder.holds_all_roles
        assert founder.photo_url == "/team/saidakbar.jpg"
        # Every department has a role, and every role is written in three languages.
        assert not Department.objects.filter(roles__isnull=True).exists()
        for role in Role.objects.all():
            assert role.title_uz and role.title_ru and role.title_en
            assert role.about_uz and role.about_ru and role.about_en


@pytest.mark.django_db
class TestPublicPage:
    def test_a_guest_reads_the_whole_page_in_one_request(self, client) -> None:
        r = client.get(reverse("team"))

        assert r.status_code == 200
        body = r.json()
        assert len(body["departments"]) == 12
        assert len(body["roles"]) == 24
        assert [m["name"] for m in body["members"]] == ["Saidakbar Narzullayev"]
        assert "is_published" not in body["roles"][0]

    def test_drafts_are_not_shown(self, client) -> None:
        Role.objects.filter(department__order=11).update(is_published=False)
        Member.objects.create(name="Qoralama", title_uz="Sinov", is_published=False)

        body = client.get(reverse("team")).json()

        assert len(body["roles"]) == 23
        # A department left with no published role would be an empty chip.
        assert len(body["departments"]) == 11
        assert all(m["name"] != "Qoralama" for m in body["members"])

    def test_the_page_cannot_be_written_through_the_public_route(self, client) -> None:
        assert client.post(reverse("team"), {}, format="json").status_code in (401, 403, 405)


@pytest.mark.django_db
class TestStaff:
    def test_a_guest_and_a_plain_user_are_refused(self, client, user) -> None:
        url = reverse("staff-team-member-list")
        assert client.get(url).status_code in (401, 403)
        client.force_login(user)
        assert client.get(url).status_code == 403
        assert client.post(url, {"name": "X", "title_uz": "Y"}, format="json").status_code == 403

    def test_an_editor_adds_a_contributor(self, editor, client) -> None:
        r = editor.post(
            reverse("staff-team-member-list"),
            {
                "name": "Ali Valiyev",
                "section": "contributor",
                "title_uz": "Masalalar muallifi",
                "photo_url": "https://example.com/ali.jpg",
                "telegram_url": "https://t.me/example",
            },
            format="json",
        )

        assert r.status_code == 201, r.content
        names = [m["name"] for m in client.get(reverse("team")).json()["members"]]
        assert "Ali Valiyev" in names

    @pytest.mark.parametrize(
        "photo",
        [
            "javascript:alert(1)",
            "http://example.com/a.jpg",
            "//example.com/a.jpg",
            "data:image/png;base64,AAAA",
        ],
    )
    def test_a_photo_must_be_a_site_path_or_https(self, editor, photo) -> None:
        r = editor.post(
            reverse("staff-team-member-list"),
            {"name": "X", "title_uz": "Y", "photo_url": photo},
            format="json",
        )

        assert r.status_code == 400, photo
        assert "photo_url" in r.json()["error"]["details"]

    def test_only_one_member_holds_every_role(self, editor) -> None:
        r = editor.post(
            reverse("staff-team-member-list"),
            {"name": "Ikkinchi", "title_uz": "Yana bir asoschi", "holds_all_roles": True},
            format="json",
        )

        assert r.status_code == 400
        assert Member.objects.filter(holds_all_roles=True).count() == 1

    def test_the_holder_can_still_be_edited(self, editor) -> None:
        founder = Member.objects.get(holds_all_roles=True)

        r = editor.patch(
            reverse("staff-team-member-detail", args=[founder.pk]),
            {"context_uz": "Dasturchi", "holds_all_roles": True},
            format="json",
        )

        assert r.status_code == 200, r.content
        founder.refresh_from_db()
        assert founder.context_uz == "Dasturchi"

    def test_an_editor_adds_edits_and_removes_a_role(self, editor) -> None:
        department = Department.objects.order_by("order")[0]
        created = editor.post(
            reverse("staff-team-role-list"),
            {
                "department": department.pk,
                "title_uz": "Stajyor",
                "about_uz": "Kofe olib keladi.",
                "hue": 10,
            },
            format="json",
        )
        assert created.status_code == 201, created.content
        pk = created.json()["id"]

        edited = editor.patch(
            reverse("staff-team-role-detail", args=[pk]), {"hue": 400}, format="json"
        )
        assert edited.status_code == 400  # a hue is 0–359

        assert editor.delete(reverse("staff-team-role-detail", args=[pk])).status_code == 204
        assert not Role.objects.filter(pk=pk).exists()

    def test_a_department_with_roles_is_not_deleted_from_under_them(self, editor) -> None:
        department = Department.objects.order_by("order")[0]

        r = editor.delete(reverse("staff-team-department-detail", args=[department.pk]))

        assert r.status_code == 409
        assert Department.objects.filter(pk=department.pk).exists()

    def test_an_empty_department_can_be_deleted(self, editor) -> None:
        department = Department.objects.create(name_uz="Bo'sh", order=99)

        r = editor.delete(reverse("staff-team-department-detail", args=[department.pk]))

        assert r.status_code == 204
