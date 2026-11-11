from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from content.models import Article, ArticleProblemLink, Roadmap, RoadmapSection, RoadmapStep
from problems import translations as problem_translations
from problems.models import Problem, Topic


def reader_locale(context: Mapping[str, Any]) -> str:
    """The reader's language, by the rule problems use (ADR-0058)."""
    return problem_translations.reader_locale(context.get("request"))


def localized(
    base_locale: str, title: str, description: str, translations: Any, locale: str
) -> dict[str, str]:
    """A study plan's or section's text in the reader's language (ADR-0060 § 2.4).

    A translation without a description falls back to the base one, as a
    problem's missing translated field does (ADR-0058).
    """
    if locale != base_locale:
        row = (translations or {}).get(locale) or {}
        if row.get("title"):
            return {
                "title": row["title"],
                "description": row.get("description") or description,
                "locale": locale,
            }
    return {"title": title, "description": description, "locale": base_locale}


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
    section_count = serializers.IntegerField(read_only=True, default=0)
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
                data = dict(RoadmapStepSerializer(step).data)
                # A step's own title is optional; without one it is named
                # after what it links to, not after that thing's slug.
                data["title"] = step_title(step, reader_locale(self.context))
                return data
        return None

    def to_representation(self, instance: Roadmap) -> dict[str, Any]:
        data = dict(super().to_representation(instance))
        data.update(
            localized(
                instance.locale,
                instance.title,
                instance.description,
                instance.translations,
                reader_locale(self.context),
            )
        )
        return data

    class Meta:
        model = Roadmap
        fields = [
            "slug",
            "title",
            "description",
            "locale",
            "track",
            "section_count",
            "step_count",
            "solved_steps",
            "next_step",
        ]


def step_title(step: RoadmapStep, locale: str) -> str:
    """A step's own title, else what it links to — a problem in the reader's
    language (ADR-0058)."""
    if step.title:
        return step.title
    if step.problem is not None:
        return problem_translations.title(step.problem, locale)
    return step.article.title if step.article is not None else ""


class RoadmapSectionSerializer(serializers.Serializer[RoadmapSection]):
    """A chapter with the reader's progress in it (ADR-0060 § 2.4)."""

    order = serializers.IntegerField()
    title = serializers.CharField()
    description = serializers.CharField()
    locale = serializers.CharField()
    step_count = serializers.IntegerField()
    solved_steps = serializers.IntegerField()


class RoadmapDetailSerializer(RoadmapListSerializer):
    #: Steps outside every section — in a plan without sections, all of them.
    #: A sectioned plan's steps are read a section at a time.
    steps = serializers.SerializerMethodField()
    sections = serializers.SerializerMethodField()

    @extend_schema_field(RoadmapStepSerializer(many=True))
    def get_steps(self, roadmap: Roadmap) -> list[dict[str, Any]]:
        loose = [step for step in roadmap.steps.all() if step.section_id is None]
        return list(RoadmapStepSerializer(loose, many=True).data)

    @extend_schema_field(RoadmapSectionSerializer(many=True))
    def get_sections(self, roadmap: Roadmap) -> list[dict[str, Any]]:
        solved = self.context.get("solved_problem_ids") or set()
        locale = reader_locale(self.context)
        steps = list(roadmap.steps.all())
        out = []
        for section in roadmap.sections.all():
            own = [step for step in steps if step.section_id == section.pk]
            out.append(
                {
                    "order": section.order,
                    **localized(
                        roadmap.locale,
                        section.title,
                        section.description,
                        section.translations,
                        locale,
                    ),
                    "step_count": len(own),
                    "solved_steps": sum(1 for step in own if step.problem_id in solved),
                }
            )
        return out

    class Meta(RoadmapListSerializer.Meta):
        fields = [*RoadmapListSerializer.Meta.fields, "steps", "sections"]


class SectionStepSerializer(serializers.Serializer[RoadmapStep]):
    order = serializers.IntegerField()
    title = serializers.CharField()
    problem = serializers.CharField(allow_null=True)
    article = serializers.CharField(allow_null=True)
    difficulty = serializers.IntegerField(allow_null=True)
    is_optional = serializers.BooleanField()
    solved = serializers.BooleanField()


class RoadmapSectionPageSerializer(serializers.Serializer[RoadmapSection]):
    """One chapter's page: its steps and the chapters around it."""

    roadmap = serializers.DictField()
    section = RoadmapSectionSerializer()
    steps = SectionStepSerializer(many=True)
    previous = serializers.IntegerField(allow_null=True)
    next = serializers.IntegerField(allow_null=True)
