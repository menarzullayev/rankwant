from __future__ import annotations

from typing import Any

from django.utils import timezone
from rest_framework import serializers

from contests.models import Contest, ContestProblem, ContestRegistration
from judging.models import MAX_SOURCE_BYTES, Attempt, AttemptTestResult, CustomRun
from problems.models import Language, Problem, ProblemLanguage


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
            "source_size",
        ]


class AttemptDetailSerializer(AttemptSerializer):
    test_results = AttemptTestResultSerializer(many=True, read_only=True)

    class Meta(AttemptSerializer.Meta):
        fields = [*AttemptSerializer.Meta.fields, "source_code", "compile_output", "test_results"]


def _virtual_window_open(registration: ContestRegistration) -> bool:
    """Virtual ishtirok oynasi hali ochiqmi."""
    if registration.virtual_start_at is None:
        return False
    from contests.services import virtual_deadline

    return timezone.now() < virtual_deadline(registration)


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
        problem = Problem.objects.filter(slug=value, is_public=True).first()
        if problem is None:
            raise serializers.ValidationError("Masala topilmadi")
        # Testsiz masalada judge IE qaytaradi. Tugmani frontendda
        # yashirish yetarli emas: API mijozi baribir yuborardi va
        # foydalanuvchi tushunarsiz ichki xato ko'rardi.
        if not problem.tests.exists():
            raise serializers.ValidationError("Bu masalaning testlari hali tayyorlanmagan")
        return value

    def validate_language(self, value: str) -> str:
        if not Language.objects.filter(code=value, is_active=True).exists():
            raise serializers.ValidationError("Til qo'llab-quvvatlanmaydi")
        return value

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Musobaqa submission'i uchun shartlar.

        `contest` maydoni serializerda bor edi, lekin view uni umuman
        ishlatmasdi: har urinish `contest=None` bo'lib yozilar, natijada
        standings hech qachon to'lmasdi.
        """
        # Masalaga xos til ro'yxati — RUXSAT. Interaktiv yoki freymwork
        # masalasi hamma tilda ma'noga ega emas; ro'yxat bo'sh bo'lsa
        # cheklov ham yo'q.
        allowed = set(
            ProblemLanguage.objects.filter(problem__slug=attrs["problem"]).values_list(
                "language__code", flat=True
            )
        )
        if allowed and attrs["language"] not in allowed:
            raise serializers.ValidationError(
                {"language": f"Bu masala {', '.join(sorted(allowed))} tillarida yechiladi"}
            )

        slug = attrs.get("contest")
        if not slug:
            return attrs

        contest = Contest.objects.filter(slug=slug, is_public=True).first()
        if contest is None:
            raise serializers.ValidationError({"contest": "Musobaqa topilmadi"})

        user = self.context["request"].user
        registration = ContestRegistration.objects.filter(contest=contest, user=user).first()
        if registration is None:
            raise serializers.ValidationError({"contest": "Musobaqaga ro'yxatdan o'ting"})

        # Virtual ishtirok TUGAGAN musobaqada bo'ladi, ya'ni `is_running`
        # unda hech qachon rost emas. Ilgari tekshiruv faqat shunga
        # tayanardi va virtual butunlay ishlamasdi: «boshlash» tugmasi
        # muddat ko'rsatar, keyin har yuborish 400 qaytarardi.
        # Rasmiy jadval xavfsiz — u `end_at` gacha kelgan urinishlarni
        # oladi (contests.services.rebuild_standings).
        if not contest.is_running and not _virtual_window_open(registration):
            raise serializers.ValidationError({"contest": "Musobaqa faol emas"})
        if not ContestProblem.objects.filter(
            contest=contest, problem__slug=attrs["problem"]
        ).exists():
            raise serializers.ValidationError({"problem": "Masala bu musobaqada yo'q"})

        attrs["contest_obj"] = contest
        return attrs


class CustomRunSerializer(serializers.ModelSerializer[CustomRun]):
    language = serializers.SlugRelatedField[Language](slug_field="code", read_only=True)

    class Meta:
        model = CustomRun
        fields = [
            "id",
            "language",
            "verdict",
            "stdout",
            "compile_output",
            "time_ms",
            "memory_kb",
            "created_at",
            "judged_at",
        ]


class CustomRunCreateSerializer(serializers.Serializer[dict[str, Any]]):
    """PRD P0-4 — foydalanuvchi stdin → output."""

    language = serializers.SlugField()
    source_code = serializers.CharField()
    stdin = serializers.CharField(allow_blank=True, default="")

    def validate_source_code(self, value: str) -> str:
        if len(value.encode()) > MAX_SOURCE_BYTES:
            raise serializers.ValidationError(
                f"Manba {MAX_SOURCE_BYTES // 1024} KB dan oshmasligi kerak"
            )
        if not value.strip():
            raise serializers.ValidationError("Manba bo'sh")
        return value

    def validate_stdin(self, value: str) -> str:
        if len(value.encode()) > 64 * 1024:
            raise serializers.ValidationError("Kirish 64 KB dan oshmasligi kerak")
        return value

    def validate_language(self, value: str) -> str:
        if not Language.objects.filter(code=value, is_active=True).exists():
            raise serializers.ValidationError("Til qo'llab-quvvatlanmaydi")
        return value
