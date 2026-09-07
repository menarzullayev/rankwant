"""Savol banki — staff (admin UI) serializerlari.

Variantlar (`Choice`) alohida endpoint emas: savol bilan birga ichma-ich
yuboriladi va har saqlashda TO'LIQ almashtiriladi. Savol variantlarsiz
ma'nosiz, shuning uchun bitta atomik yozuv qulayroq.
"""

from __future__ import annotations

from typing import Any, ClassVar

from django.db import transaction
from rest_framework import serializers

from problems.models import Topic
from quizzes.models import Choice, Question


class StaffChoiceSerializer(serializers.ModelSerializer[Choice]):
    class Meta:
        model = Choice
        fields = ["id", "order", "text", "is_correct"]
        read_only_fields: ClassVar = ["id"]


class StaffQuestionSerializer(serializers.ModelSerializer[Question]):
    choices = StaffChoiceSerializer(many=True)
    topics = serializers.SlugRelatedField[Topic](
        slug_field="slug", many=True, required=False, queryset=Topic.objects.all()
    )

    class Meta:
        model = Question
        fields = [
            "id",
            "text",
            "explanation",
            "difficulty",
            "topics",
            "is_active",
            "choices",
            "created_at",
        ]
        read_only_fields: ClassVar = ["id", "created_at"]

    def validate_choices(self, value: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if len(value) < 2:
            raise serializers.ValidationError("Kamida 2 ta variant bo'lishi kerak")
        if sum(1 for c in value if c.get("is_correct")) != 1:
            raise serializers.ValidationError("Aynan bitta to'g'ri variant bo'lishi kerak")
        orders = [c["order"] for c in value]
        if len(set(orders)) != len(orders):
            raise serializers.ValidationError("Variant tartib raqamlari takrorlanmasligi kerak")
        return value

    @staticmethod
    def _replace_choices(question: Question, choices: list[dict[str, Any]]) -> None:
        question.choices.all().delete()
        Choice.objects.bulk_create(Choice(question=question, **c) for c in choices)

    @transaction.atomic
    def create(self, validated_data: dict[str, Any]) -> Question:
        choices = validated_data.pop("choices")
        topics = validated_data.pop("topics", [])
        question = Question.objects.create(**validated_data)
        question.topics.set(topics)
        self._replace_choices(question, choices)
        return question

    @transaction.atomic
    def update(self, instance: Question, validated_data: dict[str, Any]) -> Question:
        choices = validated_data.pop("choices", None)
        topics = validated_data.pop("topics", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if topics is not None:
            instance.topics.set(topics)
        # PATCH'da `choices` kelmasa — eskilari saqlanadi
        if choices is not None:
            self._replace_choices(instance, choices)
        return instance
