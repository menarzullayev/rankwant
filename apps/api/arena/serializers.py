from __future__ import annotations

from typing import Any

from rest_framework import serializers

from arena.models import ArenaParticipation, ArenaRound
from quizzes.serializers import QuestionPublicSerializer


class ArenaSerializer(serializers.ModelSerializer[ArenaRound]):
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
            "question_count",
            "participant_count",
            "reward_qvant",
            "is_running",
            "is_finished",
        ]


class ArenaDetailSerializer(ArenaSerializer):
    current_index = serializers.IntegerField(read_only=True, allow_null=True)
    joined = serializers.SerializerMethodField()

    class Meta(ArenaSerializer.Meta):
        fields = [*ArenaSerializer.Meta.fields, "current_index", "joined"]

    def get_joined(self, arena: ArenaRound) -> bool:
        user = self.context["request"].user
        if not user.is_authenticated:
            return False
        return ArenaParticipation.objects.filter(round=arena, user=user).exists()


class CurrentQuestionSerializer(serializers.Serializer[dict[str, Any]]):
    index = serializers.IntegerField()
    deadline = serializers.DateTimeField()
    seconds_per_question = serializers.IntegerField()
    question = QuestionPublicSerializer()
    answered = serializers.BooleanField()


class AnswerSerializer(serializers.Serializer[dict[str, Any]]):
    question_id = serializers.IntegerField()
    choice_id = serializers.IntegerField()


class AnswerResultSerializer(serializers.Serializer[dict[str, Any]]):
    is_correct = serializers.BooleanField()
    points = serializers.IntegerField()
    elapsed_ms = serializers.IntegerField()


class ArenaStandingSerializer(serializers.Serializer[dict[str, Any]]):
    rank = serializers.IntegerField()
    username = serializers.CharField()
    display_name = serializers.CharField()
    score = serializers.IntegerField()
    correct_count = serializers.IntegerField()
    total_ms = serializers.IntegerField()
