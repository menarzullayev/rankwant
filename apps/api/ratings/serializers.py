from __future__ import annotations

from typing import Any

from rest_framework import serializers

from ratings.models import RatingHistory, UserSolvedProblem


class RatingHistorySerializer(serializers.ModelSerializer[RatingHistory]):
    """Reyting o'zgarishlarining ochiq tarixi.

    Vision principle #2 ning ko'rinadigan qismi: foydalanuvchi HAR BIR
    o'zgarishning sababini ko'radi. Contest holatida `seed` va `rank` ham
    beriladi — Elo hisobini qayta tekshirish mumkin bo'lsin.
    """

    class Meta:
        model = RatingHistory
        fields = [
            "rating_type",
            "value_before",
            "value_after",
            "delta",
            "reason",
            "ref_type",
            "ref_id",
            "seed",
            "rank",
            "created_at",
        ]


class SolvedProblemSerializer(serializers.ModelSerializer[UserSolvedProblem]):
    slug = serializers.CharField(source="problem.slug", read_only=True)
    title = serializers.CharField(source="problem.title", read_only=True)
    #: Skills JORIY qiyinlikdan hisoblanadi (ADR-0007); `difficulty_at_solve`
    #: audit uchun ko'rsatiladi, ular farq qilsa masala qayta baholangan.
    difficulty = serializers.IntegerField(source="problem.difficulty", read_only=True)
    code = serializers.IntegerField(source="problem.code", read_only=True, allow_null=True)
    #: Faqat ro'yxat javobida (view `best` kontekstini beradi).
    best_time_ms = serializers.SerializerMethodField()
    best_memory_kb = serializers.SerializerMethodField()
    languages = serializers.SerializerMethodField()

    class Meta:
        model = UserSolvedProblem
        fields = [
            "slug",
            "code",
            "title",
            "difficulty",
            "difficulty_at_solve",
            "first_ac_at",
            "best_time_ms",
            "best_memory_kb",
            "languages",
        ]

    def _best(self, obj: UserSolvedProblem) -> dict[str, Any]:
        best: dict[int, dict[str, Any]] = self.context.get("best", {})
        return best.get(obj.problem_id, {})

    def get_best_time_ms(self, obj: UserSolvedProblem) -> int | None:
        return self._best(obj).get("time_ms")

    def get_best_memory_kb(self, obj: UserSolvedProblem) -> int | None:
        return self._best(obj).get("memory_kb")

    def get_languages(self, obj: UserSolvedProblem) -> list[str]:
        return list(self._best(obj).get("languages", []))
