from __future__ import annotations

from typing import Any

from rest_framework import serializers

from problems.models import Topic
from quizzes.models import Choice, Question, Quiz, QuizAttempt


class ChoicePublicSerializer(serializers.ModelSerializer[Choice]):
    """`is_correct` ATAYLAB yo'q — baholash serverda."""

    class Meta:
        model = Choice
        fields = ["id", "order", "text"]


class QuestionPublicSerializer(serializers.ModelSerializer[Question]):
    choices = ChoicePublicSerializer(many=True, read_only=True)
    topics = serializers.SlugRelatedField[Topic](slug_field="slug", many=True, read_only=True)

    class Meta:
        model = Question
        fields = ["id", "text", "difficulty", "topics", "choices"]


class QuizSerializer(serializers.ModelSerializer[Quiz]):
    question_count = serializers.IntegerField(read_only=True)
    best_score = serializers.IntegerField(read_only=True, allow_null=True)

    class Meta:
        model = Quiz
        fields = [
            "slug",
            "title",
            "description",
            "reward_qvant",
            "question_count",
            "best_score",
            "created_at",
        ]


class QuizDetailSerializer(QuizSerializer):
    questions = serializers.SerializerMethodField()

    class Meta(QuizSerializer.Meta):
        fields = [*QuizSerializer.Meta.fields, "questions"]

    def get_questions(self, quiz: Quiz) -> list[dict[str, Any]]:
        items = quiz.items.select_related("question").prefetch_related(
            "question__choices", "question__topics"
        )
        return [QuestionPublicSerializer(i.question).data for i in items]


class SubmitSerializer(serializers.Serializer[dict[str, Any]]):
    answers = serializers.DictField(child=serializers.IntegerField(), allow_empty=True)

    def validate_answers(self, value: dict[str, int]) -> dict[int, int]:
        try:
            return {int(k): int(v) for k, v in value.items()}
        except (TypeError, ValueError) as exc:
            raise serializers.ValidationError("Keys must be question IDs") from exc


class ReviewItemSerializer(serializers.Serializer[dict[str, Any]]):
    question_id = serializers.IntegerField()
    chosen = serializers.IntegerField(allow_null=True)
    correct = serializers.IntegerField(allow_null=True)
    is_correct = serializers.BooleanField()
    explanation = serializers.CharField()


class QuizResultSerializer(serializers.ModelSerializer[QuizAttempt]):
    review = ReviewItemSerializer(many=True, read_only=True)

    class Meta:
        model = QuizAttempt
        fields = ["id", "score", "total", "qvant_awarded", "review", "created_at"]
