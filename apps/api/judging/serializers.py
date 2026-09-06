from __future__ import annotations

from typing import Any

from rest_framework import serializers

from judging.models import MAX_SOURCE_BYTES, Attempt, AttemptTestResult
from problems.models import Language, Problem


class AttemptTestResultSerializer(serializers.ModelSerializer[AttemptTestResult]):
    class Meta:
        model = AttemptTestResult
        fields = ["index", "verdict", "time_ms", "memory_kb"]


class AttemptSerializer(serializers.ModelSerializer[Attempt]):
    username = serializers.CharField(source="user.username", read_only=True)
    problem = serializers.SlugRelatedField[Problem](slug_field="slug", read_only=True)
    language = serializers.SlugRelatedField[Language](slug_field="code", read_only=True)

    class Meta:
        model = Attempt
        fields = [
            "id",
            "username",
            "problem",
            "language",
            "verdict",
            "score",
            "time_ms",
            "memory_kb",
            "failed_test_index",
            "created_at",
            "judged_at",
        ]


class AttemptDetailSerializer(AttemptSerializer):
    test_results = AttemptTestResultSerializer(many=True, read_only=True)

    class Meta(AttemptSerializer.Meta):
        fields = [*AttemptSerializer.Meta.fields, "source_code", "compile_output", "test_results"]


class AttemptCreateSerializer(serializers.Serializer[dict[str, Any]]):
    problem = serializers.SlugField()
    language = serializers.SlugField()
    source_code = serializers.CharField()
    contest = serializers.SlugField(required=False, allow_null=True)

    def validate_source_code(self, value: str) -> str:
        if len(value.encode()) > MAX_SOURCE_BYTES:
            raise serializers.ValidationError(
                f"Manba {MAX_SOURCE_BYTES // 1024} KB dan oshmasligi kerak"
            )
        if not value.strip():
            raise serializers.ValidationError("Manba bo'sh")
        return value

    def validate_problem(self, value: str) -> str:
        if not Problem.objects.filter(slug=value, is_public=True).exists():
            raise serializers.ValidationError("Masala topilmadi")
        return value

    def validate_language(self, value: str) -> str:
        if not Language.objects.filter(code=value, is_active=True).exists():
            raise serializers.ValidationError("Til qo'llab-quvvatlanmaydi")
        return value


class CustomTestSerializer(serializers.Serializer[dict[str, Any]]):
    """PRD P0-4 — foydalanuvchi stdin → output."""

    language = serializers.SlugField()
    source_code = serializers.CharField()
    stdin = serializers.CharField(allow_blank=True, default="")

    def validate_source_code(self, value: str) -> str:
        if len(value.encode()) > MAX_SOURCE_BYTES:
            raise serializers.ValidationError("Manba juda katta")
        return value
