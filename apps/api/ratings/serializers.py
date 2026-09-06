from __future__ import annotations

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

    class Meta:
        model = UserSolvedProblem
        fields = ["slug", "title", "difficulty", "difficulty_at_solve", "first_ac_at"]
