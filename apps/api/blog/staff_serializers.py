from __future__ import annotations

from rest_framework import serializers

from blog.models import Post


class StaffPostSerializer(serializers.ModelSerializer[Post]):
    author = serializers.CharField(source="author.username", read_only=True, default=None)

    class Meta:
        model = Post
        fields = [
            "slug",
            "kind",
            "title",
            "summary",
            "body",
            "locale",
            "author",
            "is_published",
            "published_at",
            "notify_users",
            "notified_at",
            "created_at",
            "updated_at",
        ]
        # notified_at — faqat `blog.announce_published` task yozadi; qo'lda
        # o'zgartirilsa bildirishnoma qayta yuborilib ketadi.
        read_only_fields = ["notified_at", "created_at", "updated_at"]
