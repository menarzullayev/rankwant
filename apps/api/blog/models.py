"""Blog va yangiliklar — PRD P1-3.

DIQQAT: bu «o'z o'qish kontenti» (P2-5) EMAS. U alohida feature:
maqola ↔ masala bog'lanishi, roadmap va o'quv ketma-ketligi bilan
([ADR-0005](../../docs/07-adr/0005-content-strategy-own-content.md)).
Bu yerda faqat platforma yangiliklari va e'lonlari.
"""

from __future__ import annotations

from typing import ClassVar

from django.db import models
from django.utils import timezone

from core.bases import TimeStampedModel


class Post(TimeStampedModel):
    class Kind(models.TextChoices):
        NEWS = "news", "Yangilik"
        ANNOUNCEMENT = "announcement", "E'lon"
        EDITORIAL = "editorial", "Muharrir maqolasi"

    slug = models.SlugField(unique=True, max_length=120)
    kind = models.CharField(max_length=16, choices=Kind.choices, default=Kind.NEWS)
    title = models.CharField(max_length=200)
    summary = models.CharField(max_length=300, blank=True)
    body = models.TextField(help_text="Markdown")
    locale = models.CharField(max_length=2, default="uz")

    author = models.ForeignKey(
        "core.User", null=True, blank=True, on_delete=models.SET_NULL, related_name="posts"
    )
    is_published = models.BooleanField(default=False, db_index=True)
    published_at = models.DateTimeField(null=True, blank=True)
    #: E'lon bo'lsa — barcha foydalanuvchiga bildirishnoma yuboriladi
    notify_users = models.BooleanField(
        default=False, help_text="Nashr qilinganda foydalanuvchilarga xabar berish"
    )
    notified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering: ClassVar = ["-published_at", "-created_at"]
        indexes: ClassVar = [
            models.Index(fields=["is_published", "-published_at"], name="post_feed")
        ]

    def __str__(self) -> str:
        return self.slug

    def save(self, *args: object, **kwargs: object) -> None:
        if self.is_published and self.published_at is None:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)  # type: ignore[arg-type]
