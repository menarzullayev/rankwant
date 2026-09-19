"""Staff (admin UI) — testlar. `staff/quizzes/`, lookup: slug."""

from __future__ import annotations

from typing import ClassVar

from core.openapi_docs import crud_summaries
from core.permissions import StaffOps
from core.staff import StaffViewSet
from quizzes.models import Quiz
from quizzes.staff_quiz_serializers import StaffQuizSerializer


@crud_summaries(one="test", many="testlar")
class StaffQuizViewSet(StaffViewSet):
    # StaffOps — ADR-0025 guruh bo'linishi.
    permission_classes = [StaffOps]

    queryset = Quiz.objects.prefetch_related("items")
    serializer_class = StaffQuizSerializer
    lookup_field = "slug"
    search_fields: ClassVar[list[str]] = ["slug", "title"]
    ordering_fields: ClassVar[list[str]] = [
        "pk",
        "slug",
        "title",
        "reward_qvant",
        "is_published",
        "created_at",
    ]
