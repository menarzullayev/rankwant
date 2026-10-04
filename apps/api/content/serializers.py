from __future__ import annotations

from typing import Any

from drf_spectacular.utils import extend_schema_field
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
            "kind",
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
    solved_steps = serializers.SerializerMethodField()

    def get_solved_steps(self, roadmap: Roadmap) -> int:
        """Traektoriyaning nechta masalasi yechilgan.

        Alohida progress modeli yo'q — qadam masalaga bog'langan, yechilgan
        masalalar esa `UserSolvedProblem` da. Slug to'plamini viewset bitta
        so'rovda tayyorlaydi.
        """
        solved = self.context.get("solved_problem_ids")
        if not solved:
            return 0
        return sum(
            1
            for step in roadmap.steps.all()
            if step.problem_id is not None and step.problem_id in solved
        )

    step_count = serializers.IntegerField(read_only=True, default=0)
    next_step = serializers.SerializerMethodField()

    @extend_schema_field(RoadmapStepSerializer(allow_null=True))
    def get_next_step(self, roadmap: Roadmap) -> dict[str, Any] | None:
        """The first step whose problem this reader has not solved.

        A step without a problem (an article) has nothing to mark it done,
        so it is the next step only until a later problem is solved — the
        same rule `solved_steps` counts by. A guest gets the first step.
        """
        solved = self.context.get("solved_problem_ids") or set()
        steps = sorted(roadmap.steps.all(), key=lambda step: step.order)
        done_upto = max(
            (i for i, step in enumerate(steps) if step.problem_id in solved), default=-1
        )
        for step in steps[done_upto + 1 :]:
            if step.problem_id is None or step.problem_id not in solved:
                return dict(RoadmapStepSerializer(step).data)
        return None

    class Meta:
        model = Roadmap
        fields = [
            "slug",
            "title",
            "description",
            "locale",
            "step_count",
            "solved_steps",
            "next_step",
        ]


class RoadmapDetailSerializer(RoadmapListSerializer):
    steps = RoadmapStepSerializer(many=True, read_only=True)

    class Meta(RoadmapListSerializer.Meta):
        fields = [*RoadmapListSerializer.Meta.fields, "steps"]
