"""Roadmap API serializerlari.

`vote_count`, `comment_count`, `has_voted` — `services.with_counts()`
annotatsiyalaridan keladi. `default` — annotatsiya bo'lmagan yo'l
(masalan bitta obyektni saqlagandan keyingi javob) uchun zaxira:
usiz DRF `AttributeError` beradi.

Chiqarilgan bandning changelog havolasi IKKI YASSI maydon
(`update_id`, `update_title`) — ichma-ich obyekt emas. Sabab: `update`
nomi model maydoni bilan bir xil bo'lgani uchun mypy uni qayta
belgilash deb hisoblaydi (`assignment` xatosi).
"""

from __future__ import annotations

from typing import Any

from rest_framework import serializers

from roadmap.models import RoadmapComment, RoadmapItem

#: Izoh uzunligi. Spam va tasodifiy joylashtirilgan matn oldini oladi;
#: muhokama uchun 4000 belgi yetarli.
COMMENT_MAX = 4000


class RoadmapItemSerializer(serializers.ModelSerializer[RoadmapItem]):
    """Ochiq o'qish — mehmon ham ko'radi."""

    vote_count = serializers.IntegerField(read_only=True, default=0)
    comment_count = serializers.IntegerField(read_only=True, default=0)
    has_voted = serializers.BooleanField(read_only=True, default=False)
    author = serializers.CharField(source="author.username", read_only=True, default=None)
    author_name = serializers.CharField(
        source="author.display_name", read_only=True, default=None
    )
    update_id = serializers.IntegerField(source="update.id", read_only=True, default=None)
    update_title = serializers.CharField(
        source="update.title", read_only=True, default=None
    )

    class Meta:
        model = RoadmapItem
        fields = [
            "id",
            "title",
            "body",
            "status",
            "target_quarter",
            "vote_count",
            "has_voted",
            "comment_count",
            "author",
            "author_name",
            "update_id",
            "update_title",
            "planned_at",
            "started_at",
            "released_at",
            "created_at",
        ]


class RoadmapItemWriteSerializer(serializers.ModelSerializer[RoadmapItem]):
    """Foydalanuvchi taklifi.

    `status` ATAYLAB yo'q: taklif har doim `suggested` bo'lib tug'iladi
    va uni faqat jamoa o'zgartiradi. Aks holda foydalanuvchi o'zini
    "chiqarildi" deb belgilab qo'yishi mumkin bo'lardi.
    """

    class Meta:
        model = RoadmapItem
        fields = ["title", "body"]


class RoadmapCommentSerializer(serializers.ModelSerializer[RoadmapComment]):
    author = serializers.CharField(source="author.username", read_only=True, default=None)
    author_name = serializers.CharField(
        source="author.display_name", read_only=True, default=None
    )
    is_mine = serializers.SerializerMethodField()

    class Meta:
        model = RoadmapComment
        fields = ["id", "body", "author", "author_name", "is_mine", "created_at"]

    def get_is_mine(self, obj: RoadmapComment) -> bool:
        """Izohni o'chirish tugmasi faqat egasiga (va xodimga) ko'rinadi."""
        user = getattr(self.context.get("request"), "user", None)
        return bool(user and user.is_authenticated and obj.author_id == user.pk)


class RoadmapCommentWriteSerializer(serializers.Serializer[dict[str, Any]]):
    body = serializers.CharField(max_length=COMMENT_MAX, trim_whitespace=True)


class RoadmapVoteSerializer(serializers.Serializer[dict[str, Any]]):
    """Ovoz amalining javobi — UI jonli sonni shundan yangilaydi."""

    voted = serializers.BooleanField()
    vote_count = serializers.IntegerField()


class StaffRoadmapItemSerializer(serializers.ModelSerializer[RoadmapItem]):
    """Staff yozadi.

    `status` READ-ONLY: holat `set_status()` orqali o'zgaradi, chunki
    o'sha metod o'tish vaqtini ham yozadi. To'g'ridan-to'g'ri yozish
    tarixni bo'sh qoldirardi.
    """

    author = serializers.CharField(source="author.username", read_only=True, default=None)
    vote_count = serializers.IntegerField(read_only=True, default=0)
    comment_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = RoadmapItem
        fields = [
            "id",
            "title",
            "body",
            "status",
            "target_quarter",
            "update",
            "planned_at",
            "started_at",
            "released_at",
            "is_enabled",
            "author",
            "vote_count",
            "comment_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "status",
            "planned_at",
            "started_at",
            "released_at",
            "created_at",
            "updated_at",
        ]


class StaffStatusSerializer(serializers.Serializer[dict[str, Any]]):
    status = serializers.ChoiceField(choices=RoadmapItem.Status.choices)


class StaffRoadmapCommentSerializer(serializers.ModelSerializer[RoadmapComment]):
    author = serializers.CharField(source="author.username", read_only=True, default=None)
    item_title = serializers.CharField(source="item.title", read_only=True)

    class Meta:
        model = RoadmapComment
        fields = [
            "id",
            "item",
            "item_title",
            "author",
            "body",
            "is_hidden",
            "created_at",
        ]
        read_only_fields = ["item", "author", "body", "created_at"]
