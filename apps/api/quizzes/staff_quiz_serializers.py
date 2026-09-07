"""Staff (admin UI) serializerlari — testlar.

`questions` — savol ID'larining TARTIBLI ro'yxati. Yozishda mavjud
`QuizQuestion` qatorlari to'liq almashtiriladi: `order = pozitsiya + 1`.
Alohida bola endpoint yo'q — tartib bitta so'rovda yuboriladi, shunda
UNIQUE(quiz, order) bilan to'qnashuv bo'lmaydi.
"""

from __future__ import annotations

from typing import Any

from django.db import transaction
from rest_framework import serializers

from quizzes.models import Question, Quiz, QuizQuestion


class OrderedQuestionIdsField(serializers.ListField):
    """O'qishda `items` orqali tartib bilan qaytadi (M2M tartibni saqlamaydi)."""

    def get_attribute(self, instance: Quiz) -> list[int]:
        return [item.question_id for item in instance.items.all()]


class StaffQuizSerializer(serializers.ModelSerializer[Quiz]):
    questions = OrderedQuestionIdsField(child=serializers.IntegerField(min_value=1), required=False)

    class Meta:
        model = Quiz
        fields = [
            "id",
            "slug",
            "title",
            "description",
            "reward_qvant",
            "is_published",
            "questions",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate_questions(self, value: list[int]) -> list[int]:
        if len(set(value)) != len(value):
            raise serializers.ValidationError("Savol takrorlanmasin")
        found = set(Question.objects.filter(pk__in=value).values_list("pk", flat=True))
        missing = [qid for qid in value if qid not in found]
        if missing:
            raise serializers.ValidationError(f"Savol topilmadi: {missing}")
        return value

    @staticmethod
    def _replace_items(quiz: Quiz, question_ids: list[int]) -> None:
        quiz.items.all().delete()
        QuizQuestion.objects.bulk_create(
            [
                QuizQuestion(quiz=quiz, question_id=qid, order=pos + 1)
                for pos, qid in enumerate(question_ids)
            ]
        )

    def create(self, validated_data: dict[str, Any]) -> Quiz:
        question_ids: list[int] | None = validated_data.pop("questions", None)
        with transaction.atomic():
            quiz = super().create(validated_data)
            if question_ids is not None:
                self._replace_items(quiz, question_ids)
        return quiz

    def update(self, instance: Quiz, validated_data: dict[str, Any]) -> Quiz:
        question_ids: list[int] | None = validated_data.pop("questions", None)
        with transaction.atomic():
            quiz = super().update(instance, validated_data)
            if question_ids is not None:
                self._replace_items(quiz, question_ids)
        return quiz


class StaffQuestionLookupSerializer(serializers.ModelSerializer[Question]):
    """Faqat o'qish uchun — test paneli savol matnini ko'rsatishi uchun."""

    class Meta:
        model = Question
        fields = ["id", "text", "difficulty", "is_active"]
