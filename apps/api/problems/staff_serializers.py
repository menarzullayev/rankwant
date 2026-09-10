"""Staff (admin UI) serializerlari — masala, mavzu va test yuklash."""

from __future__ import annotations

from typing import Any

from rest_framework import serializers

from problems.models import (
    DIFFICULTY_STEP,
    Language,
    Problem,
    ProblemReport,
    TestCase,
    Topic,
)


class StaffTopicSerializer(serializers.ModelSerializer[Topic]):
    # `parent` nomi DRF `Field.parent` atributi bilan ustma-ust tushadi — stub'lar uchun ignore.
    parent = serializers.SlugRelatedField[Topic](  # type: ignore[assignment]
        slug_field="slug", queryset=Topic.objects.all(), allow_null=True, required=False
    )

    class Meta:
        model = Topic
        fields = ["id", "slug", "name_uz", "name_ru", "name_en", "parent"]


class StaffProblemReportSerializer(serializers.ModelSerializer[ProblemReport]):
    """Xabar — xodim uchun. Faqat `status` o'zgartiriladi.

    Sabab va izohni xodim tahrirlay olmaydi: xabar foydalanuvchining
    so'zi, uni o'zgartirish yozuvni ma'nosiz qilardi.
    """

    problem = serializers.SlugRelatedField[Problem](slug_field="slug", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = ProblemReport
        fields = ["id", "problem", "username", "reason", "comment", "status", "created_at"]
        read_only_fields = ["problem", "username", "reason", "comment", "created_at"]


class StaffProblemSerializer(serializers.ModelSerializer[Problem]):
    topics = serializers.SlugRelatedField[Topic](
        many=True, slug_field="slug", queryset=Topic.objects.all(), required=False
    )
    interactor_language = serializers.SlugRelatedField[Language](
        slug_field="code", queryset=Language.objects.all(), allow_null=True, required=False
    )
    checker_language = serializers.SlugRelatedField[Language](
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
            "editorial_price",
            "statement_locale",
            "difficulty",
            "topics",
            "time_limit_ms",
            "memory_limit_kb",
            "checker_type",
            "interactor_source",
            "interactor_language",
            "checker_source",
            "checker_language",
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

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Testsiz masala ommaga chiqmasin.

        Judge nol testni «hammasi o'tdi» deb emas, IE deb qaytaradi —
        ya'ni bunday masala arxivda ko'rinadi, ochiladi, lekin yechib
        bo'lmaydi. O'lchandi: import qilingan arxivda 2 096 ommaviy
        masaladan 870 tasi shu holatda edi.
        """
        ommaviy = attrs.get("is_public", getattr(self.instance, "is_public", False))
        if ommaviy:
            testlar = self.instance.tests.count() if self.instance else 0
            if not testlar:
                raise serializers.ValidationError(
                    {"is_public": "Testsiz masalani ommaga chiqarib bo'lmaydi"}
                )
        return attrs

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
