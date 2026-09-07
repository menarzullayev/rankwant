"""Staff (admin UI) kontent yuzasi — `staff/articles/`, `staff/roadmaps/`.

Ommaviy `ArticleViewSet` / `RoadmapViewSet` faqat o'qish uchun va nashr
qilinganini ko'rsatadi; bu yerda hammasi ko'rinadi va yoziladi.
"""

from __future__ import annotations

from typing import Any

from django.db.models import Count, QuerySet
from rest_framework.serializers import BaseSerializer

from content.models import Article, Roadmap
from content.staff_serializers import StaffArticleSerializer, StaffRoadmapSerializer
from core.staff import StaffViewSet


class StaffArticleViewSet(StaffViewSet):
    serializer_class = StaffArticleSerializer
    lookup_field = "slug"
    search_fields = ["slug", "title", "summary"]
    ordering_fields = ["pk", "slug", "difficulty", "published_at", "updated_at"]

    def get_queryset(self) -> QuerySet[Article]:
        return (
            Article.objects.select_related("author")
            .prefetch_related("topics", "problem_links__problem")
            .annotate(problem_count=Count("problem_links"))
        )

    def perform_create(self, serializer: BaseSerializer[Any]) -> None:
        serializer.save(author=self.request.user)


class StaffRoadmapViewSet(StaffViewSet):
    serializer_class = StaffRoadmapSerializer
    lookup_field = "slug"
    search_fields = ["slug", "title"]
    ordering_fields = ["pk", "slug", "order"]
    ordering = ["order", "slug"]

    def get_queryset(self) -> QuerySet[Roadmap]:
        return Roadmap.objects.prefetch_related("steps__article", "steps__problem").annotate(
            step_count=Count("steps")
        )
