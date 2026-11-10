from __future__ import annotations

from typing import Any

from rest_framework import serializers

from notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer[Notification]):
    is_read = serializers.BooleanField(read_only=True)

    class Meta:
        model = Notification
        fields = [
            "id",
            "kind",
            "title",
            "body",
            "code",
            "params",
            "ref_type",
            "ref_id",
            "is_read",
            "created_at",
        ]


class MarkReadSerializer(serializers.Serializer[dict[str, Any]]):
    ids = serializers.ListField(child=serializers.IntegerField(), required=False)


class NotificationIdsSerializer(serializers.Serializer[dict[str, Any]]):
    ids = serializers.ListField(child=serializers.IntegerField(), allow_empty=False, max_length=200)


class NotificationSummarySerializer(serializers.Serializer[dict[str, Any]]):
    total = serializers.IntegerField()
    unread = serializers.IntegerField()
    unseen = serializers.IntegerField(help_text="Unread and not yet shown in the bell")
    kinds = serializers.ListField(child=serializers.CharField(), help_text="Kinds present")


class NotificationUpdatedSerializer(serializers.Serializer[dict[str, Any]]):
    updated = serializers.IntegerField()


class EmailUnsubscribeSerializer(serializers.Serializer[dict[str, Any]]):
    token = serializers.CharField(required=False, help_text="Or `?token=` in the URL (RFC 8058)")


class EmailUnsubscribeResultSerializer(serializers.Serializer[dict[str, Any]]):
    kind = serializers.CharField(help_text="A notification kind, or `*` for every kind")
    done = serializers.BooleanField(help_text="True once email is off for that kind")
