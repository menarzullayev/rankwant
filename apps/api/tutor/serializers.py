from __future__ import annotations

from typing import Any

from rest_framework import serializers

from tutor.models import Message, Report
from tutor.services import MAX_CODE, MAX_QUESTION


class TutorMessageSerializer(serializers.ModelSerializer[Message]):
    #: The student flagged this reply (decision ⑦).
    reported = serializers.SerializerMethodField()

    def get_reported(self, message: Message) -> bool:
        return bool(message.reports.all())

    class Meta:
        model = Message
        fields = (
            "id", "role", "kind", "text", "hint_level", "attempt", "code", "code_language",
            "status", "error", "code_removed", "created_at", "answered_at", "reported",
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


class TutorReportCreateSerializer(serializers.Serializer[Any]):
    message = serializers.IntegerField(min_value=1)
    reason = serializers.ChoiceField(choices=Report.Reason.choices)
    note = serializers.CharField(required=False, allow_blank=True, max_length=500)


class StaffTutorReportSerializer(serializers.ModelSerializer[Report]):
    problem: serializers.SlugRelatedField[Any] = serializers.SlugRelatedField(
        slug_field="slug", read_only=True
    )
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Report
        fields = (
            "id", "problem", "username", "reason", "note", "question_text", "reply_text", "model",
            "status", "created_at", "resolved_at",
        )  # fmt: skip
        read_only_fields = tuple(f for f in fields if f != "status")


class TutorModelSpendSerializer(serializers.Serializer[Any]):
    model = serializers.CharField()
    replies = serializers.IntegerField()
    spent_usd = serializers.DecimalField(max_digits=12, decimal_places=6)


class TutorBudgetSerializer(serializers.Serializer[Any]):
    month = serializers.CharField(read_only=True)
    spent_usd = serializers.DecimalField(max_digits=12, decimal_places=6, read_only=True)
    replies = serializers.IntegerField(read_only=True)
    #: 0 — not set.
    limit_usd = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)
    percent = serializers.FloatField(read_only=True, allow_null=True)
    warning = serializers.BooleanField(read_only=True)
    over = serializers.BooleanField(read_only=True)
    by_model = TutorModelSpendSerializer(many=True, read_only=True)
