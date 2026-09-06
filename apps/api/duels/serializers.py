from __future__ import annotations

from typing import Any

from rest_framework import serializers

from duels.models import Duel
from duels.services import MIN_LEAD_MINUTES


class DuelProblemSerializer(serializers.Serializer[dict[str, Any]]):
    order = serializers.IntegerField()
    slug = serializers.CharField()
    title = serializers.CharField()
    difficulty = serializers.IntegerField()


class DuelSerializer(serializers.ModelSerializer[Duel]):
    challenger = serializers.SlugRelatedField[Any](slug_field="username", read_only=True)
    opponent = serializers.SlugRelatedField[Any](slug_field="username", read_only=True)
    winner = serializers.SlugRelatedField[Any](slug_field="username", read_only=True)
    end_at = serializers.DateTimeField(read_only=True)
    is_running = serializers.BooleanField(read_only=True)
    problems = serializers.SerializerMethodField()

    class Meta:
        model = Duel
        fields = [
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
            "is_running",
            "winner",
            "challenger_solved",
            "opponent_solved",
            "is_draw",
            "problems",
            "created_at",
        ]

    def get_problems(self, duel: Duel) -> list[dict[str, Any]]:
        """Masalalar faqat BOSHLANGACH va faqat ishtirokchilarga.

        Aks holda raqib masalalarni oldindan ko'rib tayyorlanib olardi.
        """
        user = self.context["request"].user
        if not user.is_authenticated or user.pk not in {duel.challenger_id, duel.opponent_id}:
            return []
        if duel.status == Duel.Status.OPEN or (
            duel.status == Duel.Status.ACCEPTED and not duel.is_running
        ):
            return []
        return [
            {
                "order": item.order,
                "slug": item.problem.slug,
                "title": item.problem.title,
                "difficulty": item.problem.difficulty,
            }
            for item in duel.items.select_related("problem")
        ]


class DuelCreateSerializer(serializers.Serializer[dict[str, Any]]):
    title = serializers.CharField(max_length=120)
    problem_count = serializers.IntegerField(min_value=1, max_value=8, default=4)
    difficulty = serializers.IntegerField(min_value=800, max_value=3500, default=1200)
    duration_minutes = serializers.IntegerField(min_value=15, max_value=240, default=60)
    start_at = serializers.DateTimeField(help_text=f"Kamida {MIN_LEAD_MINUTES} daqiqadan keyin")


class DuelRecordSerializer(serializers.Serializer[dict[str, Any]]):
    wins = serializers.IntegerField()
    draws = serializers.IntegerField()
    losses = serializers.IntegerField()
