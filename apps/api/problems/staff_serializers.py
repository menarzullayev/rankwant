"""Staff (admin UI) serializerlari — masala, mavzu va test yuklash."""

from __future__ import annotations

from typing import Any

from rest_framework import serializers

from problems import evaluation, readiness, release, testgroups
from problems.models import (
    DIFFICULTY_STEP,
    Language,
    Problem,
    ProblemReport,
    ProblemRevision,
    ReferenceSolution,
    TestCase,
    Topic,
    Validator,
)
from problems.storage import MAX_TEST_BYTES


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
    manager_language = serializers.SlugRelatedField[Language](
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
            "task_kind",
            "manager_source",
            "manager_language",
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
        """Testsiz — va yashirin testsiz — masala ommaga chiqmasin.

        Judge nol testni «hammasi o'tdi» deb emas, IE deb qaytaradi —
        ya'ni bunday masala arxivda ko'rinadi, ochiladi, lekin yechib
        bo'lmaydi. O'lchandi: import qilingan arxivda 2 096 ommaviy
        masaladan 870 tasi shu holatda edi.

        Hamma testi NAMUNA bo'lsa buzilish jimroq, lekin og'irroq: kutilgan
        javob masala sahifasida ochiq turadi, ya'ni uni bosib chiqargan
        dastur AC oladi. O'lchandi: `3-ta-son` ga `print('3 2 1')` — AC.
        """
        # An `io_mode` / `checker_type` pair the judge cannot grade is refused
        # here, when it is typed — not at the first submission. `io_mode` is
        # not editable through this API, so it is read from the row (a new
        # problem starts as `stdio`).
        checker_type = attrs.get(
            "checker_type", getattr(self.instance, "checker_type", Problem.Checker.STANDARD)
        )
        io_mode = getattr(self.instance, "io_mode", Problem.IoMode.STDIO)
        has_subtasks = self.instance is not None and self.instance.subtasks.exists()
        task_kind = attrs.get(
            "task_kind", getattr(self.instance, "task_kind", Problem.TaskKind.PROGRAM)
        )
        error = (
            evaluation.combination_error(io_mode, checker_type)
            or evaluation.subtask_error(checker_type, has_subtasks)
            or evaluation.task_kind_error(task_kind, io_mode, checker_type)
        )
        if error:
            raise serializers.ValidationError(
                {"checker_type": f"{evaluation.EVALUATION_MODE_INVALID}: {error}"}
            )

        ommaviy = attrs.get("is_public", getattr(self.instance, "is_public", False))
        if not ommaviy or self.instance is None:
            # Yangi yozuv qoralama sifatida yaratiladi; ommaviy bo'lishi
            # uchun avval test yuklanadi, ya'ni bu tekshiruv tahrirda ishlaydi.
            return attrs
        if not self.instance.tests.exists():
            raise serializers.ValidationError(
                {"is_public": "A problem cannot go public without tests"}
            )
        # Yashirin test faqat E'LON QILISH paytida talab qilinadi: arxivdagi
        # 1 222 masalada u yo'q va ular hali tahrirlanishi kerak — har
        # saqlashda to'sib qo'yish statement tuzatishni ham to'xtatardi.
        elon_qilinyapti = not self.instance.is_public
        if elon_qilinyapti and not self.instance.tests.filter(is_sample=False).exists():
            raise serializers.ValidationError(
                {
                    "is_public": "A hidden problem cannot go public without tests — "
                    "a program that prints the sample would be accepted"
                }
            )
        # Guruh talabi (PROMPT_0 §3 · §9). Faqat E'LON QILISH paytida va
        # faqat `READINESS_ENFORCE` yoqilganda: 2026-09-30 gacha yozilgan
        # 2 096 masalada tasnif yo'q, ya'ni majburlash ularni tahrirlashni
        # ham to'sib qo'yardi. Sabab `readiness.enforcing()` docstringida.
        if elon_qilinyapti and readiness.enforcing():
            missing = testgroups.missing_required_groups(
                self.instance.tests.values_list("group", flat=True)
            )
            if missing:
                # API xabarlari inglizcha (`check_api_english` darvozasi).
                # Guruh NOMI emas, kaliti yoziladi: kalit barqaror, nom esa
                # tarjima qilinadi — xato kodi mashina o'qiydigan bo'lishi
                # kerak (PROMPT_0 §9: stable error codes).
                raise serializers.ValidationError(
                    {"is_public": f"TEST_GROUP_MISSING: {', '.join(missing)}"}
                )
        return attrs

    def validate_difficulty(self, value: int) -> int:
        # Model.clean() bilan bir xil qoida — API orqali ham 100 ga karrali bo'lsin.
        if value % DIFFICULTY_STEP:
            raise serializers.ValidationError(f"Value must be a multiple of {DIFFICULTY_STEP}")
        return value


class StaffTestCaseSerializer(serializers.ModelSerializer[TestCase]):
    class Meta:
        model = TestCase
        fields = [
            "id",
            "order",
            "is_sample",
            "group",
            "points",
            "input_ref",
            "output_ref",
        ]


class StaffRevisionSerializer(serializers.ModelSerializer[ProblemRevision]):
    """Masala paketining muzlatilgan surati (ADR 0052)."""

    integrity_ok = serializers.SerializerMethodField()

    class Meta:
        model = ProblemRevision
        fields = [
            "id",
            "version",
            "status",
            "package_hash",
            "integrity_ok",
            "judge_environment",
            "frozen_at",
            "published_at",
            "gate_report",
            "created_at",
        ]
        read_only_fields = fields

    def get_integrity_ok(self, obj: ProblemRevision) -> bool:
        """Paket xeshi buzilmaganmi — artefakt o'zgarganmi (§8 · §10)."""
        return bool(obj.package_hash) and release.verify_package(obj)


class _ProblemProgramSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    """Masalaga biriktirilgan dastur: validator yoki etalon yechim.

    Ikkalasi ham bitta shaklda — til va manba. `problem` maydoni ATAYIN
    yo'q: u URL dan olinadi. So'rov tanasidan kelsa, bitta masalani
    tahrirlayotgan xodim boshqasining validatorini almashtirib yuborishi
    mumkin bo'lardi.
    """

    language = serializers.SlugRelatedField[Language](
        slug_field="code", queryset=Language.objects.all()
    )
    #: Manba BAYT-BAYT saqlanadi. DRF `CharField` ni standart holatda
    #: qirqadi va oxirgi qator uzilishini jimgina yeb qo'yardi
    #: (o'lchandi) — platforma yuklangan dasturni o'zgartirmasligi kerak,
    #: keyin esa «men yuborgan fayl bu emas» degan savol qolardi.
    #:
    #: `source` nomi DRF `Field.source` atributi bilan ustma-ust tushadi
    #: — yuqoridagi `parent` bilan bir xil holat, stub'lar uchun ignore.
    source = serializers.CharField(trim_whitespace=False)  # type: ignore[assignment]

    def validate_source(self, value: str) -> str:
        # Bo'sh manba judge'da kompilyatsiya xatosiga aylanadi va hack
        # yuborgan foydalanuvchi sababini masala sozlamasidan izlamaydi.
        if not value.strip():
            raise serializers.ValidationError("Source is empty")
        return value


class StaffValidatorSerializer(_ProblemProgramSerializer):
    """Kirish validatori — hackingning birinchi darvozasi (ADR-0020)."""

    class Meta:
        model = Validator
        fields = ["language", "source", "updated_at"]
        read_only_fields = ["updated_at"]


class StaffReferenceSolutionSerializer(_ProblemProgramSerializer):
    """Etalon yechim — hack testining javobi shundan chiqadi (ADR-0021)."""

    class Meta:
        model = ReferenceSolution
        fields = ["language", "source", "updated_at"]
        read_only_fields = ["updated_at"]


def _check_size(value: str, field: str) -> str:
    """Test fayli hajmini BAYT bo'yicha tekshiradi.

    DRF `max_length` BELGINI sanaydi, chegara esa baytda qo'yilgan (S3 va
    judge baytni ko'radi). UTF-8 da belgi != bayt, ya'ni `max_length` yolg'iz
    o'zi yetarli emas.
    """
    size = len(value.encode("utf-8"))
    if size > MAX_TEST_BYTES:
        raise serializers.ValidationError(f"{field} is {size} bytes; the limit is {MAX_TEST_BYTES}")
    return value


class TestCaseUploadSerializer(serializers.Serializer[Any]):
    """Test matni S3 ga ketadi, DB da faqat havola qoladi (05-domain-model)."""

    order = serializers.IntegerField(min_value=1)
    input = serializers.CharField(
        allow_blank=True, trim_whitespace=False, max_length=MAX_TEST_BYTES
    )
    expected = serializers.CharField(
        allow_blank=True, trim_whitespace=False, max_length=MAX_TEST_BYTES
    )
    is_sample = serializers.BooleanField(default=False)
    #: Bo'sh qoldirilsa `testgroups.DEFAULT_GROUP` (`unclassified`) qo'yiladi —
    #: ya'ni «hali tasniflanmagan». Tasodifiy deb yozish yolg'on bo'lardi.
    group = serializers.ChoiceField(
        choices=TestCase.Group.choices, required=False, allow_blank=True
    )
    points = serializers.IntegerField(min_value=0, default=0)

    def validate_input(self, value: str) -> str:
        return _check_size(value, "input")

    def validate_expected(self, value: str) -> str:
        return _check_size(value, "expected")

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """`is_sample` va `group=SAMPLE` bir-biriga zid bo'lmasin.

        Namuna test ommaviy ko'rinadi (shartdagi misol). Ya'ni
        `group=sample` ni `is_sample=False` bilan qo'yish testni yashirin
        qoldirib, uni tasnif bo'yicha ommaviy deb ko'rsatardi — ikki manba
        ikki xil gapirardi. Shuning uchun bittasi ikkinchisini belgilaydi.
        """
        group = attrs.get("group") or ""
        if attrs.get("is_sample"):
            if group and group != TestCase.Group.SAMPLE:
                raise serializers.ValidationError(
                    {"group": "A sample test must be in the sample group"}
                )
            attrs["group"] = TestCase.Group.SAMPLE
        elif group == TestCase.Group.SAMPLE:
            raise serializers.ValidationError(
                {"group": "The sample group is reserved for `is_sample` tests"}
            )
        elif not group:
            attrs["group"] = testgroups.DEFAULT_GROUP
        return attrs
