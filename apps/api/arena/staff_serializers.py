"""Staff (admin UI) serializerlari — Arena raundi.

`questions` — tartiblangan savol id'lari ro'yxati. Yozishda ArenaQuestion
qatorlari TO'LIQ almashtiriladi (PUT uslubi): alohida child endpoint yo'q.
"""

from __future__ import annotations

from typing import Any

from django.db import transaction
from rest_framework import serializers

from arena.models import ArenaQuestion, ArenaRound
from quizzes.models import Question


class StaffArenaSerializer(serializers.ModelSerializer[ArenaRound]):
    # write_only: o'qishda tartiblangan ro'yxat `to_representation` da qo'yiladi
    questions = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        required=False,
        allow_empty=True,
        write_only=True,
    )
    question_count = serializers.IntegerField(read_only=True)
    participant_count = serializers.IntegerField(read_only=True)
    end_at = serializers.DateTimeField(read_only=True)
    is_running = serializers.BooleanField(read_only=True)
    is_finished = serializers.BooleanField(read_only=True)

    class Meta:
        model = ArenaRound
        fields = [
            "slug",
            "title",
            "description",
            "start_at",
            "end_at",
            "seconds_per_question",
            "reward_qvant",
            "is_public",
            "questions",
            "question_count",
            "participant_count",
            "is_running",
            "is_finished",
            "rewards_applied_at",
            "created_at",
        ]
        read_only_fields = ["rewards_applied_at", "created_at"]

    def validate_questions(self, ids: list[int]) -> list[int]:
        if len(set(ids)) != len(ids):
            raise serializers.ValidationError("Savol id'lari takrorlanmasin")
        found = set(Question.objects.filter(pk__in=ids).values_list("pk", flat=True))
        missing = [i for i in ids if i not in found]
        if missing:
            raise serializers.ValidationError(f"Savol topilmadi: {missing}")
        return ids

    def to_representation(self, instance: ArenaRound) -> dict[str, Any]:
        data = super().to_representation(instance)
        data["questions"] = list(instance.items.values_list("question_id", flat=True))
        data["question_count"] = len(data["questions"])
        # create/update javobida annotate yo'q — sanab qo'yamiz
        if "participant_count" not in data:
            data["participant_count"] = instance.participants.count()
        return data

    @staticmethod
    def _replace_questions(arena: ArenaRound, ids: list[int]) -> None:
        arena.items.all().delete()
        ArenaQuestion.objects.bulk_create(
            [ArenaQuestion(round=arena, question_id=qid, order=i + 1) for i, qid in enumerate(ids)]
        )

    @transaction.atomic
    def create(self, validated_data: dict[str, Any]) -> ArenaRound:
        ids = validated_data.pop("questions", [])
        arena = super().create(validated_data)
        self._replace_questions(arena, ids)
        return arena

    @transaction.atomic
    def update(self, instance: ArenaRound, validated_data: dict[str, Any]) -> ArenaRound:
        ids = validated_data.pop("questions", None)
        arena = super().update(instance, validated_data)
        if ids is not None:
            self._replace_questions(arena, ids)
        return arena


class RescheduleSerializer(serializers.Serializer[dict[str, Any]]):
    start_at = serializers.DateTimeField()


class FinalizeResultSerializer(serializers.Serializer[dict[str, Any]]):
    awarded = serializers.IntegerField()
    rewards_applied_at = serializers.DateTimeField(allow_null=True)
