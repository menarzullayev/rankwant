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
    #: What a reader recognises the problem by. The slug stays the key; a
    #: hidden problem keeps its title to itself (the slug was always shown).
    problem_title = serializers.SerializerMethodField()
    problem_code = serializers.SerializerMethodField()
    language = serializers.SlugRelatedField[Language](slug_field="code", read_only=True)
    #: `C++ 23`, not `cpp23`: the code is an internal key. Name and version
    #: are separate columns (`C++` + `23`, `Ada` + `(GNAT 14)`); the name
    #: alone would show two Pythons and two C's as one.
    language_name = serializers.SerializerMethodField()
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

    def get_language_name(self, obj: Attempt) -> str:
        return f"{obj.language.name} {obj.language.version}".strip()

    def get_problem_title(self, obj: Attempt) -> str:
        return obj.problem.title if obj.problem.is_public else ""

    def get_problem_code(self, obj: Attempt) -> int | None:
        return obj.problem.code if obj.problem.is_public else None

    class Meta:
        model = Attempt
        fields = [
            "id",
            "username",
            "user_title",
            "problem",
            "problem_title",
            "problem_code",
            "contest",
            "language",
            "language_name",
            "verdict",
            "score",
            "time_ms",
            "memory_kb",
            "failed_test_index",
            "running_test_index",
            "created_at",
            "judged_at",
            "source_size",
            "is_first_solver",
        ]


class AttemptDetailSerializer(AttemptSerializer):
    test_results = AttemptTestResultSerializer(many=True, read_only=True)
    #: How many tests the problem has. `test_results` stops at the first
    #: failure, so "1 of 100 passed" needs the total from the problem.
    tests_total = serializers.SerializerMethodField()

    def get_tests_total(self, obj: Attempt) -> int:
        # An interactive problem is judged as one dialogue: its tests are
        # not run, so there is no "N of M passed" to show. Without this an
        # accepted attempt read "0 of 3 passed" (measured 2026-10-07).
        if obj.problem.checker_type == "interactive":
            return 0
        return obj.problem.tests.count()

    class Meta(AttemptSerializer.Meta):
        fields = [
            *AttemptSerializer.Meta.fields,
            "source_code",
            "compile_output",
            "test_results",
            "tests_total",
        ]


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
        if self.context.get("answer_files"):
            # An answer attempt has no language; the view passes the stand-in.
            return value
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
        # An answer problem takes files, every other kind takes source: the
        # two doors are not interchangeable.
        takes_files = Problem.objects.filter(
            slug=attrs["problem"], task_kind=Problem.TaskKind.ANSWER
        ).exists()
        if takes_files != bool(self.context.get("answer_files")):
            raise serializers.ValidationError(
                {
                    "problem": "This problem takes answer files, not source code"
                    if takes_files
                    else "This problem takes source code, not answer files"
                }
            )

        rows = ProblemLanguage.objects.filter(problem__slug=attrs["problem"])
        function = Problem.objects.filter(
            slug=attrs["problem"], task_kind=Problem.TaskKind.FUNCTION
        ).exists()
        if function:
            # The submission is inserted into the harness of its language:
            # a language without one cannot be judged at all.
            rows = rows.exclude(harness="")
        allowed = set(rows.values_list("language__code", flat=True))
        if (allowed or function) and attrs["language"] not in allowed:
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
