from __future__ import annotations

from typing import Any

from rest_framework import serializers

from notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer[Notification]):
    is_read = serializers.BooleanField(read_only=True)

    class Meta:
        model = Notification
        fields = ["id", "kind", "title", "body", "ref_type", "ref_id", "is_read", "created_at"]


class MarkReadSerializer(serializers.Serializer[dict[str, Any]]):
    ids = serializers.ListField(child=serializers.IntegerField(), required=False)
