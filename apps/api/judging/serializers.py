from __future__ import annotations

from typing import Any

from django.utils import timezone
from rest_framework import serializers

from contests.models import Contest, ContestProblem, ContestRegistration
from hacks.models import HackLock
from judging.models import MAX_SOURCE_BYTES, Attempt, AttemptTestResult, CustomRun
from problems.models import Language, Problem, ProblemLanguage
from profiles.titles import TitleField


class AttemptTestResultSerializer(serializers.ModelSerializer[AttemptTestResult]):
    class Meta:
        model = AttemptTestResult
        fields = ["index", "verdict", "time_ms", "memory_kb"]


class AttemptSerializer(serializers.ModelSerializer[Attempt]):
    username = serializers.CharField(source="user.username", read_only=True)
    #: `title` emas — urinish qatorida u masala nomi bilan adashtirilardi.
    user_title = TitleField(source="user")
    problem = serializers.SlugRelatedField[Problem](slug_field="slug", read_only=True)
    language = serializers.SlugRelatedField[Language](slug_field="code", read_only=True)
    #: Hack yuzasi masalani qaysi musobaqada lock qilishni shundan biladi
    #: (ADR-0020). ⚠️ `AttemptViewSet` `contest` ni `select_related` ga
    #: qo'shadi — usiz bu maydon har qatorga bitta so'rov qo'shardi.
    contest = serializers.SlugRelatedField[Contest](slug_field="slug", read_only=True)
    #: Masalani BIRINCHI yechgan urinishmi. Qiymatni `AttemptViewSet`
    #: annotatsiya qiladi (bitta subquery, har qator uchun emas).
    #: `getattr` — chunki serializer `create` javobida ham ishlatiladi va
    #: u yerda annotatsiya yo'q; `SerializerMethodField` o'rniga oddiy
    #: `BooleanField` bo'lsa `AttributeError` berardi.
    is_first_solver = serializers.SerializerMethodField()

    def get_is_first_solver(self, obj: Attempt) -> bool:
        return bool(getattr(obj, "is_first_solver", False))

    class Meta:
        model = Attempt
        fields = [
            "id",
            "username",
            "user_title",
            "problem",
            "contest",
            "language",
            "verdict",
            "score",
            "time_ms",
            "memory_kb",
            "failed_test_index",
            "created_at",
            "judged_at",
            "source_size",
            "is_first_solver",
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
            raise serializers.ValidationError(f"Source exceeds {MAX_SOURCE_BYTES // 1024} KB")
        if not value.strip():
            raise serializers.ValidationError("Source is empty")
        return value

    def validate_problem(self, value: str) -> str:
        problem = Problem.objects.filter(slug=value, is_public=True).first()
        if problem is None:
            raise serializers.ValidationError("Problem not found")
        # Testsiz masalada judge IE qaytaradi. Tugmani frontendda
        # yashirish yetarli emas: API mijozi baribir yuborardi va
        # foydalanuvchi tushunarsiz ichki xato ko'rardi.
        if not problem.tests.exists():
            raise serializers.ValidationError("This problem's tests are not ready yet")
        return value

    def validate_language(self, value: str) -> str:
        if not Language.objects.filter(code=value, is_active=True).exists():
            raise serializers.ValidationError("This language is not supported")
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
                {"language": f"This problem is solved in {', '.join(sorted(allowed))}"}
            )

        slug = attrs.get("contest")
        if not slug:
            return attrs

        contest = Contest.objects.filter(slug=slug, is_public=True).first()
        if contest is None:
            raise serializers.ValidationError({"contest": "Contest not found"})

        user = self.context["request"].user
        registration = ContestRegistration.objects.filter(contest=contest, user=user).first()
        if registration is None:
            raise serializers.ValidationError({"contest": "Register for the contest first"})

        # Virtual ishtirok TUGAGAN musobaqada bo'ladi, ya'ni `is_running`
        # unda hech qachon rost emas. Ilgari tekshiruv faqat shunga
        # tayanardi va virtual butunlay ishlamasdi: «boshlash» tugmasi
        # muddat ko'rsatar, keyin har yuborish 400 qaytarardi.
        # Rasmiy jadval xavfsiz — u `end_at` gacha kelgan urinishlarni
        # oladi (contests.services.rebuild_standings).
        if not contest.is_running and not _virtual_window_open(registration):
            raise serializers.ValidationError({"contest": "The contest is not active"})
        if not ContestProblem.objects.filter(
            contest=contest, problem__slug=attrs["problem"]
        ).exists():
            raise serializers.ValidationError({"problem": "This problem is not in the contest"})

        # Lock qilingan masalaga QAYTA yuborib bo'lmaydi (ADR-0020): hack
        # huquqi aynan shu narxda olinadi. Frontendda tugmani o'chirish
        # yetarli emas — API mijozi baribir yuborardi va lock qilgan odam
        # yechimini jimgina almashtirib, xonadagilarni aldagan bo'lardi.
        if HackLock.objects.filter(
            contest=contest, problem__slug=attrs["problem"], user=user
        ).exists():
            raise serializers.ValidationError(
                {"problem": "This problem is locked — you cannot submit again"}
            )

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
            raise serializers.ValidationError(f"Source exceeds {MAX_SOURCE_BYTES // 1024} KB")
        if not value.strip():
            raise serializers.ValidationError("Source is empty")
        return value

    def validate_stdin(self, value: str) -> str:
        if len(value.encode()) > 64 * 1024:
            raise serializers.ValidationError("Input must not exceed 64 KB")
        return value

    def validate_language(self, value: str) -> str:
        if not Language.objects.filter(code=value, is_active=True).exists():
            raise serializers.ValidationError("This language is not supported")
        return value
