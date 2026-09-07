"""Staff API — yangiliklar (`staff/posts/`)."""

from __future__ import annotations

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from blog.models import Post
from blog.tasks import announce_published
from core.models import User
from notifications.models import Notification


@pytest.fixture
def staff(db) -> User:
    return User.objects.create_user("staff1", password="x", is_staff=True)


@pytest.fixture
def staff_client(staff) -> APIClient:
    c = APIClient()
    c.force_authenticate(staff)
    return c


@pytest.fixture
def draft(db) -> Post:
    return Post.objects.create(slug="qoralama", title="Qoralama", body="matn")


PAYLOAD = {
    "slug": "yangi",
    "kind": "announcement",
    "title": "Yangi e'lon",
    "summary": "qisqa",
    "body": "# Salom",
    "locale": "uz",
    "is_published": False,
    "published_at": None,
    "notify_users": True,
}


@pytest.mark.django_db
class TestStaffPostAccess:
    def test_anonim_kirolmaydi(self, draft) -> None:
        assert APIClient().get(reverse("staff-post-list")).status_code in (401, 403)

    def test_oddiy_foydalanuvchi_kirolmaydi(self, user, draft) -> None:
        c = APIClient()
        c.force_authenticate(user)
        assert c.get(reverse("staff-post-list")).status_code == 403
        assert c.post(reverse("staff-post-list"), PAYLOAD, format="json").status_code == 403
        assert c.post(reverse("staff-post-publish", args=[draft.slug])).status_code == 403


@pytest.mark.django_db
class TestStaffPostCrud:
    def test_royxat_qoralamalarni_ham_koradi(self, staff_client, draft) -> None:
        body = staff_client.get(reverse("staff-post-list")).json()
        assert body["count"] == 1
        assert body["results"][0]["slug"] == draft.slug
        assert body["results"][0]["is_published"] is False
        # Ommaviy API o'zgarmagan: qoralama ko'rinmaydi
        assert APIClient().get(reverse("post-list")).json()["count"] == 0

    def test_yaratish_muallif_xodim(self, staff_client, staff) -> None:
        res = staff_client.post(reverse("staff-post-list"), PAYLOAD, format="json")
        assert res.status_code == 201, res.json()
        post = Post.objects.get(slug="yangi")
        assert post.author == staff
        assert post.kind == Post.Kind.ANNOUNCEMENT
        assert post.notify_users is True
        assert res.json()["author"] == staff.username

    def test_batafsil_va_tahrirlash(self, staff_client, draft) -> None:
        url = reverse("staff-post-detail", args=[draft.slug])
        assert staff_client.get(url).json()["body"] == "matn"
        res = staff_client.patch(url, {"title": "Yangilandi", "locale": "ru"}, format="json")
        assert res.status_code == 200
        draft.refresh_from_db()
        assert draft.title == "Yangilandi"
        assert draft.locale == "ru"

    def test_notified_at_qolda_ozgarmaydi(self, staff_client, draft) -> None:
        url = reverse("staff-post-detail", args=[draft.slug])
        res = staff_client.patch(url, {"notified_at": "2026-01-01T00:00:00Z"}, format="json")
        assert res.status_code == 200
        draft.refresh_from_db()
        assert draft.notified_at is None

    def test_slug_takrorlanmaydi(self, staff_client, draft) -> None:
        res = staff_client.post(
            reverse("staff-post-list"), {**PAYLOAD, "slug": draft.slug}, format="json"
        )
        assert res.status_code == 400
        assert "slug" in res.json()["error"]["details"]

    def test_ochirish(self, staff_client, draft) -> None:
        res = staff_client.delete(reverse("staff-post-detail", args=[draft.slug]))
        assert res.status_code == 204
        assert not Post.objects.filter(slug=draft.slug).exists()


@pytest.mark.django_db
class TestStaffPostPublish:
    def test_nashr_qilish(self, staff_client, draft) -> None:
        res = staff_client.post(reverse("staff-post-publish", args=[draft.slug]))
        assert res.status_code == 200
        assert res.json()["is_published"] is True
        assert res.json()["published_at"] is not None
        assert APIClient().get(reverse("post-list")).json()["count"] == 1

    def test_nashrdan_olish_sanani_saqlaydi(self, staff_client, draft) -> None:
        staff_client.post(reverse("staff-post-publish", args=[draft.slug]))
        draft.refresh_from_db()
        first = draft.published_at
        res = staff_client.post(reverse("staff-post-unpublish", args=[draft.slug]))
        assert res.status_code == 200
        assert res.json()["is_published"] is False
        draft.refresh_from_db()
        assert draft.published_at == first
        assert APIClient().get(reverse("post-list")).json()["count"] == 0

    def test_bildirishnoma_faqat_task_orqali_bir_marta(self, staff_client, user, draft) -> None:
        """Staff API o'zi yubormaydi — beat task yuboradi, ikkinchi marta emas."""
        draft.notify_users = True
        draft.save()
        staff_client.post(reverse("staff-post-publish", args=[draft.slug]))
        assert Notification.objects.count() == 0
        assert announce_published() == 2  # user + staff1
        # Qayta nashr qilinsa ham takror yuborilmaydi
        staff_client.post(reverse("staff-post-unpublish", args=[draft.slug]))
        staff_client.post(reverse("staff-post-publish", args=[draft.slug]))
        assert announce_published() == 0
        assert Notification.objects.count() == 2
