from __future__ import annotations

from rest_framework import serializers

from content.models import Article, ArticleProblemLink, Roadmap, RoadmapStep
from problems.models import Problem, Topic


class LinkedProblemSerializer(serializers.ModelSerializer[ArticleProblemLink]):
    slug = serializers.CharField(source="problem.slug", read_only=True)
    title = serializers.CharField(source="problem.title", read_only=True)
    difficulty = serializers.IntegerField(source="problem.difficulty", read_only=True)

    class Meta:
        model = ArticleProblemLink
        fields = ["slug", "title", "difficulty", "role"]


class ArticleListSerializer(serializers.ModelSerializer[Article]):
    topics = serializers.SlugRelatedField[Topic](many=True, read_only=True, slug_field="slug")
    problem_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Article
        fields = [
            "slug",
            "title",
            "summary",
            "difficulty",
            "locale",
            "topics",
            "reading_minutes",
            "problem_count",
            "published_at",
        ]


class ArticleDetailSerializer(ArticleListSerializer):
    problems = LinkedProblemSerializer(source="problem_links", many=True, read_only=True)
    author = serializers.CharField(source="author.username", read_only=True, default=None)

    class Meta(ArticleListSerializer.Meta):
        fields = [*ArticleListSerializer.Meta.fields, "body", "author", "problems"]


class RoadmapStepSerializer(serializers.ModelSerializer[RoadmapStep]):
    article = serializers.SlugRelatedField[Article](slug_field="slug", read_only=True)
    problem = serializers.SlugRelatedField[Problem](slug_field="slug", read_only=True)

    class Meta:
        model = RoadmapStep
        fields = ["order", "title", "article", "problem", "is_optional"]


class RoadmapListSerializer(serializers.ModelSerializer[Roadmap]):
    step_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Roadmap
        fields = ["slug", "title", "description", "locale", "step_count"]


class RoadmapDetailSerializer(RoadmapListSerializer):
    steps = RoadmapStepSerializer(many=True, read_only=True)

    class Meta(RoadmapListSerializer.Meta):
        fields = [*RoadmapListSerializer.Meta.fields, "steps"]
