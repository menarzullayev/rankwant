"""Blog va e'lonlar — PRD P1-3."""

from __future__ import annotations

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from blog.models import Post
from blog.tasks import announce_published
from notifications.models import Notification


@pytest.mark.django_db
class TestPost:
    def test_nashr_qilinganda_sana_qoyiladi(self, user) -> None:
        post = Post.objects.create(slug="salom", title="Salom", body="matn", is_published=True)
        assert post.published_at is not None

    def test_nashr_qilinmagan_korinmaydi(self) -> None:
        Post.objects.create(slug="qoralama", title="Qoralama", body="x")
        body = APIClient().get(reverse("post-list")).json()
        assert body["count"] == 0

    def test_royxat_va_batafsil(self, user) -> None:
        Post.objects.create(
            slug="yangilik",
            title="Yangilik",
            summary="qisqa",
            body="to'liq matn",
            is_published=True,
            author=user,
        )
        c = APIClient()
        assert c.get(reverse("post-list")).json()["count"] == 1
        detail = c.get(reverse("post-detail", args=["yangilik"])).json()
        assert detail["body"] == "to'liq matn"
        assert detail["author"] == user.username

    def test_royxatda_matn_yoq(self) -> None:
        """Ro'yxat yengil bo'lishi kerak."""
        Post.objects.create(slug="a", title="A", body="uzun matn", is_published=True)
        item = APIClient().get(reverse("post-list")).json()["results"][0]
        assert "body" not in item


@pytest.mark.django_db
class TestAnnouncement:
    def test_elon_bildirishnoma_yuboradi(self, user, other_user) -> None:
        Post.objects.create(
            slug="elon",
            title="Muhim e'lon",
            summary="tafsilot",
            body="x",
            is_published=True,
            notify_users=True,
        )
        assert announce_published() == 2
        assert Notification.objects.filter(kind=Notification.Kind.SYSTEM).count() == 2

    def test_ikki_marta_yuborilmaydi(self, user) -> None:
        Post.objects.create(
            slug="elon2",
            title="E'lon",
            body="x",
            is_published=True,
            notify_users=True,
        )
        announce_published()
        assert announce_published() == 0

    def test_bayroqsiz_post_yubormaydi(self, user) -> None:
        Post.objects.create(slug="oddiy", title="Oddiy", body="x", is_published=True)
        assert announce_published() == 0
