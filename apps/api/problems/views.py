from __future__ import annotations

from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from core.pagination import StandardPagination
from problems.filters import ProblemFilter
from problems.models import Language, Problem, Topic
from problems.serializers import (
    LanguageSerializer,
    ProblemDetailSerializer,
    ProblemListSerializer,
    TopicSerializer,
)


class ProblemViewSet(viewsets.ReadOnlyModelViewSet[Problem]):
    """Ommaviy masala arxivi.

    Yozish Django admin orqali (PRD P0-2) — API faqat o'qish uchun.
    """

    permission_classes = [AllowAny]
    lookup_field = "slug"
    filterset_class = ProblemFilter
    pagination_class = StandardPagination
    ordering_fields = ["difficulty", "solved_count", "created_at"]
    ordering = ["difficulty"]

    def get_queryset(self):  # type: ignore[no-untyped-def]
        return (
            Problem.objects.filter(is_public=True)
            .prefetch_related("topics")
            .order_by("difficulty", "slug")
        )

    def get_serializer_class(self):  # type: ignore[no-untyped-def]
        return ProblemDetailSerializer if self.action == "retrieve" else ProblemListSerializer


class TopicViewSet(viewsets.ReadOnlyModelViewSet[Topic]):
    permission_classes = [AllowAny]
    serializer_class = TopicSerializer
    lookup_field = "slug"
    queryset = Topic.objects.all().order_by("slug")


class LanguageViewSet(viewsets.ReadOnlyModelViewSet[Language]):
    permission_classes = [AllowAny]
    serializer_class = LanguageSerializer
    lookup_field = "code"
    queryset = Language.objects.filter(is_active=True).order_by("name")
