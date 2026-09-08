from __future__ import annotations

from django.db.models import Count
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from content.models import Article, Roadmap
from content.serializers import (
    ArticleDetailSerializer,
    ArticleListSerializer,
    RoadmapDetailSerializer,
    RoadmapListSerializer,
)
from core.pagination import StandardPagination


class ArticleViewSet(viewsets.ReadOnlyModelViewSet[Article]):
    """O'z o'qish kontenti — ADR-0005 differensiatori.

    Yozish Django admin orqali; API faqat o'qish uchun (masala arxivi bilan
    bir xil naqsh).
    """

    permission_classes = [AllowAny]
    lookup_field = "slug"
    pagination_class = StandardPagination
    filterset_fields = ["locale", "topics__slug", "kind"]
    ordering_fields = ["difficulty", "published_at"]
    ordering = ["difficulty"]

    def get_queryset(self):  # type: ignore[no-untyped-def]
        return (
            Article.objects.filter(is_published=True)
            .prefetch_related("topics", "problem_links__problem")
            .annotate(problem_count=Count("problem_links"))
        )

    def get_serializer_class(self):  # type: ignore[no-untyped-def]
        return ArticleDetailSerializer if self.action == "retrieve" else ArticleListSerializer


class RoadmapViewSet(viewsets.ReadOnlyModelViewSet[Roadmap]):
    permission_classes = [AllowAny]
    lookup_field = "slug"
    pagination_class = None

    def get_serializer_context(self):  # type: ignore[no-untyped-def]
        context = dict(super().get_serializer_context())
        user = self.request.user
        if user.is_authenticated:
            from ratings.models import UserSolvedProblem

            context["solved_problem_ids"] = set(
                UserSolvedProblem.objects.filter(user=user).values_list("problem_id", flat=True)
            )
        return context

    def get_queryset(self):  # type: ignore[no-untyped-def]
        return (
            Roadmap.objects.filter(is_published=True)
            .prefetch_related("steps__article", "steps__problem")
            .annotate(step_count=Count("steps"))
        )

    def get_serializer_class(self):  # type: ignore[no-untyped-def]
        return RoadmapDetailSerializer if self.action == "retrieve" else RoadmapListSerializer
