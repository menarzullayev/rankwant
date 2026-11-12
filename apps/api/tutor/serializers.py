from __future__ import annotations

from typing import Any

from rest_framework import serializers

from tutor.models import Message
from tutor.services import MAX_CODE, MAX_QUESTION


class TutorMessageSerializer(serializers.ModelSerializer[Message]):
    class Meta:
        model = Message
        fields = (
            "id", "role", "kind", "text", "hint_level", "attempt", "code", "code_language",
            "status", "error", "code_removed", "created_at", "answered_at",
        )  # fmt: skip
        read_only_fields = fields


class TutorUsageSerializer(serializers.Serializer[Any]):
    used = serializers.IntegerField()
    #: `null` — no daily limit (staff).
    limit = serializers.IntegerField(allow_null=True)
    resets_at = serializers.DateTimeField()


class TutorConversationSerializer(serializers.Serializer[Any]):
    #: `false` when the tutor cannot answer here; `reason` says why.
    available = serializers.BooleanField()
    reason = serializers.CharField(allow_null=True)
    hint_level = serializers.IntegerField()
    usage = TutorUsageSerializer()
    messages = TutorMessageSerializer(many=True)


class TutorAskSerializer(serializers.Serializer[Any]):
    kind = serializers.ChoiceField(choices=Message.Kind.choices)
    question = serializers.CharField(required=False, allow_blank=True, max_length=MAX_QUESTION)
    hint_level = serializers.IntegerField(required=False, min_value=1, max_value=3)
    attempt = serializers.IntegerField(required=False, min_value=1)
    code = serializers.CharField(
        required=False, allow_blank=True, max_length=MAX_CODE, trim_whitespace=False
    )
    code_language = serializers.CharField(required=False, allow_blank=True, max_length=64)
