from __future__ import annotations

from typing import Any

from django.db.models import Count
from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from content.cpuz import glossary as cpuz_glossary
from content.models import Article, Roadmap
from content.serializers import (
    ArticleDetailSerializer,
    ArticleListSerializer,
    GlossaryEntrySerializer,
    LibraryEntrySerializer,
    RoadmapDetailSerializer,
    RoadmapListSerializer,
    RoadmapSectionPageSerializer,
    localized,
    reader_locale,
    step_title,
)
from core.openapi_docs import crud_summaries
from core.pagination import StandardPagination
from problems import translations as problem_translations


@crud_summaries(one="maqola", many="maqolalar", only=("list", "retrieve"))
class ArticleViewSet(viewsets.ReadOnlyModelViewSet[Article]):
    """O'z o'qish kontenti — ADR-0005 differensiatori.

    Yozish Django admin orqali; API faqat o'qish uchun (masala arxivi bilan
    bir xil naqsh).
    """

    permission_classes = [AllowAny]
    lookup_field = "slug"
    pagination_class = StandardPagination
    filterset_fields = ["locale", "topics__slug", "kind", "category", "level"]
    ordering_fields = ["difficulty", "published_at"]
    # `pk` — tiebreaker: bir xil `difficulty` li maqolalar tartibi aks holda
    # SQL ixtiyoriga qoladi va sahifalash beqaror bo'ladi.
    ordering = ["difficulty", "pk"]

    def get_queryset(self):  # type: ignore[no-untyped-def]
        query = Article.objects.filter(is_published=True).prefetch_related(
            "topics", "problem_links__problem"
        )
        if self.action == "retrieve":
            query = query.prefetch_related("external_links", "translations", "reviews")
        return query.annotate(problem_count=Count("problem_links"))

    @extend_schema(responses={200: GlossaryEntrySerializer(many=True)})
    @action(detail=False, methods=["get"], pagination_class=None)
    def glossary(self, request: Request) -> Response:
        """The algorithms library's glossary (ADR-0062 § 3), from the snapshot."""
        return Response(GlossaryEntrySerializer(cpuz_glossary(), many=True).data)

    @extend_schema(responses={200: LibraryEntrySerializer(many=True)})
    @action(detail=False, methods=["get"], pagination_class=None)
    def library(self, request: Request) -> Response:
        """The whole algorithms library in one answer (ADR-0062 § 5.3).

        163 lines, so the catalogue groups and filters them without paging.
        The reader's language gives the titles: the originals' in English.
        """
        locale = reader_locale({"request": request})
        rows = (
            Article.objects.filter(is_published=True)
            .exclude(source_ref="")
            .order_by("category", "order", "pk")
            .prefetch_related("translations")
        )
        data = LibraryEntrySerializer(rows, many=True).data
        for row, article in zip(data, rows, strict=True):
            title = next((t.title for t in article.translations.all() if t.locale == locale), None)
            if title and locale != article.locale:
                row["title"] = title
                row["locale"] = locale
        return Response(data)

    def get_serializer_class(self):  # type: ignore[no-untyped-def]
        return ArticleDetailSerializer if self.action == "retrieve" else ArticleListSerializer


def solved_problem_ids(request: Request) -> set[int]:
    """The reader's solved problems — every solve, the unofficial too: a study
    plan's progress counts them (ADR-0060 § 2.3)."""
    if not request.user.is_authenticated:
        return set()
    from ratings.models import UserSolvedProblem

    return set(
        UserSolvedProblem.objects.filter(user=request.user).values_list("problem_id", flat=True)
    )


@crud_summaries(one="o'quv yo'l xaritasi", many="o'quv yo'l xaritalari", only=("list", "retrieve"))
class RoadmapViewSet(viewsets.ReadOnlyModelViewSet[Roadmap]):
    permission_classes = [AllowAny]
    lookup_field = "slug"
    pagination_class = None

    def get_serializer_context(self):  # type: ignore[no-untyped-def]
        context = dict(super().get_serializer_context())
        context["solved_problem_ids"] = solved_problem_ids(self.request)
        return context

    def get_queryset(self):  # type: ignore[no-untyped-def]
        return (
            Roadmap.objects.filter(is_published=True)
            .prefetch_related("steps__article", "steps__problem", "sections")
            .annotate(
                step_count=Count("steps", distinct=True),
                section_count=Count("sections", distinct=True),
            )
        )

    def get_serializer_class(self):  # type: ignore[no-untyped-def]
        return RoadmapDetailSerializer if self.action == "retrieve" else RoadmapListSerializer

    @extend_schema(summary="O'quv rejasi bo'limi", responses=RoadmapSectionPageSerializer)
    @action(detail=True, url_path=r"sections/(?P<order>[0-9]+)")
    def section(self, request: Request, slug: str, order: str) -> Response:
        """One chapter of a study plan with the reader's progress (ADR-0060 § 2.4).

        A plan of 1 100 problems is read a chapter at a time: the plan's own
        page lists the chapters and their progress.
        """
        roadmap = Roadmap.objects.filter(slug=slug, is_published=True).first()
        if roadmap is None:
            raise Http404
        sections = list(roadmap.sections.all())
        index = next((i for i, s in enumerate(sections) if s.order == int(order)), None)
        if index is None:
            raise Http404
        section = sections[index]
        locale = reader_locale({"request": request})
        solved = solved_problem_ids(request)
        steps = list(
            section.steps.select_related("problem", "article")
            .prefetch_related(
                problem_translations.prefetch(locale, through="problem__translations")
            )
            .order_by("order")
        )
        rows: list[dict[str, Any]] = [
            {
                "order": step.order,
                "title": step_title(step, locale),
                "problem": step.problem.slug if step.problem else None,
                "article": step.article.slug if step.article else None,
                "difficulty": step.problem.difficulty if step.problem else None,
                "is_optional": step.is_optional,
                "solved": step.problem_id in solved,
            }
            for step in steps
        ]
        text = localized(
            roadmap.locale, roadmap.title, roadmap.description, roadmap.translations, locale
        )
        return Response(
            {
                "roadmap": {"slug": roadmap.slug, "title": text["title"], "locale": text["locale"]},
                "section": {
                    "order": section.order,
                    **localized(
                        roadmap.locale,
                        section.title,
                        section.description,
                        section.translations,
                        locale,
                    ),
                    "step_count": len(rows),
                    "solved_steps": sum(1 for row in rows if row["solved"]),
                },
                "steps": rows,
                "previous": sections[index - 1].order if index > 0 else None,
                "next": sections[index + 1].order if index + 1 < len(sections) else None,
            }
        )
