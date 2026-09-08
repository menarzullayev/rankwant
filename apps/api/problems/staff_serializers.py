"""Staff (admin UI) serializerlari — masala, mavzu va test yuklash."""

from __future__ import annotations

from typing import Any

from rest_framework import serializers

from problems.models import DIFFICULTY_STEP, Language, Problem, TestCase, Topic


class StaffTopicSerializer(serializers.ModelSerializer[Topic]):
    # `parent` nomi DRF `Field.parent` atributi bilan ustma-ust tushadi — stub'lar uchun ignore.
    parent = serializers.SlugRelatedField[Topic](  # type: ignore[assignment]
        slug_field="slug", queryset=Topic.objects.all(), allow_null=True, required=False
    )

    class Meta:
        model = Topic
        fields = ["id", "slug", "name_uz", "name_ru", "name_en", "parent"]


class StaffProblemSerializer(serializers.ModelSerializer[Problem]):
    topics = serializers.SlugRelatedField[Topic](
        many=True, slug_field="slug", queryset=Topic.objects.all(), required=False
    )
    interactor_language = serializers.SlugRelatedField[Language](
        slug_field="code", queryset=Language.objects.all(), allow_null=True, required=False
    )
    test_count = serializers.SerializerMethodField()

    class Meta:
        model = Problem
        fields = [
            "id",
            "code",
            "slug",
            "title",
            "statement",
            "input_format",
            "output_format",
            "note",
            "editorial",
            "statement_locale",
            "difficulty",
            "topics",
            "time_limit_ms",
            "memory_limit_kb",
            "checker_type",
            "interactor_source",
            "interactor_language",
            "is_public",
            "source",
            "source_url",
            "solved_count",
            "attempt_count",
            "test_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["code", "solved_count", "attempt_count", "created_at", "updated_at"]

    def get_test_count(self, obj: Problem) -> int:
        # Ro'yxatda annotatsiya bor; yaratish/tahrirlashdan keyingi javobda yo'q.
        count: int | None = getattr(obj, "test_count", None)
        return count if count is not None else obj.tests.count()

    def validate_difficulty(self, value: int) -> int:
        # Model.clean() bilan bir xil qoida — API orqali ham 100 ga karrali bo'lsin.
        if value % DIFFICULTY_STEP:
            raise serializers.ValidationError(f"Qiymat {DIFFICULTY_STEP} ga karrali bo'lishi kerak")
        return value


class StaffTestCaseSerializer(serializers.ModelSerializer[TestCase]):
    class Meta:
        model = TestCase
        fields = ["id", "order", "is_sample", "points", "input_ref", "output_ref"]


class TestCaseUploadSerializer(serializers.Serializer[Any]):
    """Test matni S3 ga ketadi, DB da faqat havola qoladi (05-domain-model)."""

    order = serializers.IntegerField(min_value=1)
    input = serializers.CharField(allow_blank=True, trim_whitespace=False)
    expected = serializers.CharField(allow_blank=True, trim_whitespace=False)
    is_sample = serializers.BooleanField(default=False)
    points = serializers.IntegerField(min_value=0, default=0)
