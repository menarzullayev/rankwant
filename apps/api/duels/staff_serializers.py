from __future__ import annotations

from typing import Any

from rest_framework import serializers

from duels.models import Duel


class StaffDuelSerializer(serializers.ModelSerializer[Duel]):
    """Nazorat uchun to'liq ko'rinish — barcha maydonlar faqat o'qishga.

    Xodim duelni tahrirlamaydi: bekor qilish va yakunlash alohida amallar.
    """

    challenger = serializers.SlugRelatedField[Any](slug_field="username", read_only=True)
    opponent = serializers.SlugRelatedField[Any](slug_field="username", read_only=True)
    winner = serializers.SlugRelatedField[Any](slug_field="username", read_only=True)
    problems = serializers.SlugRelatedField[Any](slug_field="slug", many=True, read_only=True)
    end_at = serializers.DateTimeField(read_only=True)
    is_due = serializers.BooleanField(read_only=True)

    class Meta:
        model = Duel
        fields = [
            "id",
            "slug",
            "title",
            "status",
            "challenger",
            "opponent",
            "problem_count",
            "difficulty",
            "duration_minutes",
            "start_at",
            "end_at",
            "is_due",
            "problems",
            "winner",
            "challenger_solved",
            "opponent_solved",
            "is_draw",
            "ratings_applied_at",
            "created_at",
        ]
        read_only_fields = fields


class StaffDuelFinalizeSerializer(serializers.Serializer[dict[str, Any]]):
    force = serializers.BooleanField(default=False)
