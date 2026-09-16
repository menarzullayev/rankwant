"""Staff (admin UI) serializerlari — masala, mavzu va test yuklash."""

from __future__ import annotations

from typing import Any

from rest_framework import serializers

from problems.models import (
    DIFFICULTY_STEP,
    Language,
    Problem,
    ProblemReport,
    ReferenceSolution,
    TestCase,
    Topic,
    Validator,
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
        """Testsiz — va yashirin testsiz — masala ommaga chiqmasin.

        Judge nol testni «hammasi o'tdi» deb emas, IE deb qaytaradi —
        ya'ni bunday masala arxivda ko'rinadi, ochiladi, lekin yechib
        bo'lmaydi. O'lchandi: import qilingan arxivda 2 096 ommaviy
        masaladan 870 tasi shu holatda edi.

        Hamma testi NAMUNA bo'lsa buzilish jimroq, lekin og'irroq: kutilgan
        javob masala sahifasida ochiq turadi, ya'ni uni bosib chiqargan
        dastur AC oladi. O'lchandi: `3-ta-son` ga `print('3 2 1')` — AC.
        """
        ommaviy = attrs.get("is_public", getattr(self.instance, "is_public", False))
        if not ommaviy or self.instance is None:
            # Yangi yozuv qoralama sifatida yaratiladi; ommaviy bo'lishi
            # uchun avval test yuklanadi, ya'ni bu tekshiruv tahrirda ishlaydi.
            return attrs
        if not self.instance.tests.exists():
            raise serializers.ValidationError(
                {"is_public": "Testsiz masalani ommaga chiqarib bo'lmaydi"}
            )
        # Yashirin test faqat E'LON QILISH paytida talab qilinadi: arxivdagi
        # 1 222 masalada u yo'q va ular hali tahrirlanishi kerak — har
        # saqlashda to'sib qo'yish statement tuzatishni ham to'xtatardi.
        elon_qilinyapti = not self.instance.is_public
        if elon_qilinyapti and not self.instance.tests.filter(is_sample=False).exists():
            raise serializers.ValidationError(
                {
                    "is_public": "Yashirin testsiz masalani ommaga chiqarib bo'lmaydi — "
                    "namuna javobini bosib chiqargan dastur AC oladi"
                }
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
            raise serializers.ValidationError("Manba bo'sh")
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


class TestCaseUploadSerializer(serializers.Serializer[Any]):
    """Test matni S3 ga ketadi, DB da faqat havola qoladi (05-domain-model)."""

    order = serializers.IntegerField(min_value=1)
    input = serializers.CharField(allow_blank=True, trim_whitespace=False)
    expected = serializers.CharField(allow_blank=True, trim_whitespace=False)
    is_sample = serializers.BooleanField(default=False)
    points = serializers.IntegerField(min_value=0, default=0)
