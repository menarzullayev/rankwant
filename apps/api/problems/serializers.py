from __future__ import annotations

from rest_framework import serializers

from problems.models import Language, Problem, TestCase, Topic


class TopicSerializer(serializers.ModelSerializer[Topic]):
    class Meta:
        model = Topic
        fields = ["slug", "name_uz", "name_ru", "name_en", "parent"]


class LanguageSerializer(serializers.ModelSerializer[Language]):
    class Meta:
        model = Language
        fields = ["code", "name", "version"]


class SampleTestSerializer(serializers.ModelSerializer[TestCase]):
    class Meta:
        model = TestCase
        fields = ["order"]


class ProblemListSerializer(serializers.ModelSerializer[Problem]):
    level = serializers.CharField(read_only=True)
    level_label = serializers.CharField(read_only=True)
    topics = serializers.SlugRelatedField[Topic](many=True, read_only=True, slug_field="slug")

    class Meta:
        model = Problem
        fields = [
            "slug",
            "title",
            "difficulty",
            "level",
            "level_label",
            "topics",
            "solved_count",
            "attempt_count",
        ]


class ProblemDetailSerializer(ProblemListSerializer):
    class Meta(ProblemListSerializer.Meta):
        fields = [
            *ProblemListSerializer.Meta.fields,
            "statement",
            "statement_locale",
            "time_limit_ms",
            "memory_limit_kb",
            "checker_type",
            "source",
            "source_url",
        ]
