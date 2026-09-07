"""Staff (admin UI) serializerlari — kontent yozish yuzasi.

Bolalar (`ArticleProblemLink`, `RoadmapStep`) alohida endpoint olmaydi:
ota-ona ichida `problems` / `steps` ro'yxati yuborilsa, mavjud qatorlar
TO'LIQ almashtiriladi (PUT-uslub). Ro'yxat yuborilmasa — tegilmaydi.
"""

from __future__ import annotations

from typing import Any

from django.db import transaction
from rest_framework import serializers

from content.models import Article, ArticleProblemLink, Roadmap, RoadmapStep
from problems.models import Problem, Topic


class StaffArticleProblemLinkSerializer(serializers.ModelSerializer[ArticleProblemLink]):
    problem = serializers.SlugRelatedField[Problem](
        slug_field="slug", queryset=Problem.objects.all()
    )

    class Meta:
        model = ArticleProblemLink
        fields = ["problem", "role", "order"]


class StaffArticleSerializer(serializers.ModelSerializer[Article]):
    topics = serializers.SlugRelatedField[Topic](
        many=True, slug_field="slug", queryset=Topic.objects.all(), required=False
    )
    problems = StaffArticleProblemLinkSerializer(source="problem_links", many=True, required=False)
    author = serializers.CharField(source="author.username", read_only=True, default=None)
    problem_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Article
        fields = [
            "slug",
            "kind",
            "title",
            "summary",
            "body",
            "locale",
            "difficulty",
            "topics",
            "is_published",
            "reading_minutes",
            "problems",
            "problem_count",
            "author",
            "published_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["problem_count", "author", "published_at", "created_at", "updated_at"]

    def validate_problems(self, value: list[dict[str, Any]]) -> list[dict[str, Any]]:
        seen: set[tuple[int, str]] = set()
        for link in value:
            key = (link["problem"].pk, link.get("role", ArticleProblemLink.Role.PRACTICE))
            if key in seen:
                raise serializers.ValidationError(
                    f"«{link['problem'].slug}» bir rolda ikki marta bog'langan"
                )
            seen.add(key)
        return value

    @staticmethod
    def _replace_links(article: Article, links: list[dict[str, Any]]) -> None:
        article.problem_links.all().delete()
        ArticleProblemLink.objects.bulk_create(
            [ArticleProblemLink(article=article, **link) for link in links]
        )

    @transaction.atomic
    def create(self, validated_data: dict[str, Any]) -> Article:
        links = validated_data.pop("problem_links", None)
        article = super().create(validated_data)
        if links is not None:
            self._replace_links(article, links)
        return article

    @transaction.atomic
    def update(self, instance: Article, validated_data: dict[str, Any]) -> Article:
        links = validated_data.pop("problem_links", None)
        article = super().update(instance, validated_data)
        if links is not None:
            self._replace_links(article, links)
        return article


class StaffRoadmapStepSerializer(serializers.ModelSerializer[RoadmapStep]):
    article = serializers.SlugRelatedField[Article](
        slug_field="slug", queryset=Article.objects.all(), required=False, allow_null=True
    )
    problem = serializers.SlugRelatedField[Problem](
        slug_field="slug", queryset=Problem.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = RoadmapStep
        fields = ["order", "title", "article", "problem", "is_optional"]

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        # Model.clean bilan bir xil qoida — bo'sh qadam foydalanuvchiga hech narsa ko'rsatmaydi
        if attrs.get("article") is None and attrs.get("problem") is None:
            raise serializers.ValidationError("Qadamda maqola yoki masala bo'lishi kerak")
        return attrs


class StaffRoadmapSerializer(serializers.ModelSerializer[Roadmap]):
    steps = StaffRoadmapStepSerializer(many=True, required=False)
    step_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Roadmap
        fields = [
            "slug",
            "title",
            "description",
            "locale",
            "is_published",
            "order",
            "steps",
            "step_count",
        ]

    def validate_steps(self, value: list[dict[str, Any]]) -> list[dict[str, Any]]:
        orders = [step["order"] for step in value]
        if len(orders) != len(set(orders)):
            raise serializers.ValidationError("Qadam tartib raqamlari takrorlanmasligi kerak")
        return value

    @staticmethod
    def _replace_steps(roadmap: Roadmap, steps: list[dict[str, Any]]) -> None:
        roadmap.steps.all().delete()
        RoadmapStep.objects.bulk_create([RoadmapStep(roadmap=roadmap, **step) for step in steps])

    @transaction.atomic
    def create(self, validated_data: dict[str, Any]) -> Roadmap:
        steps = validated_data.pop("steps", None)
        roadmap = super().create(validated_data)
        if steps is not None:
            self._replace_steps(roadmap, steps)
        return roadmap

    @transaction.atomic
    def update(self, instance: Roadmap, validated_data: dict[str, Any]) -> Roadmap:
        steps = validated_data.pop("steps", None)
        roadmap = super().update(instance, validated_data)
        if steps is not None:
            self._replace_steps(roadmap, steps)
        return roadmap
