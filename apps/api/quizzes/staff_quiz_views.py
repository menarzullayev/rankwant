"""Staff (admin UI) — testlar. `staff/quizzes/`, lookup: slug."""

from __future__ import annotations

from typing import ClassVar

from rest_framework import filters, viewsets
from rest_framework.permissions import IsAdminUser

from core.pagination import StandardPagination
from core.staff import StaffViewSet
from quizzes.models import Question, Quiz
from quizzes.staff_quiz_serializers import StaffQuestionLookupSerializer, StaffQuizSerializer


class StaffQuizViewSet(StaffViewSet):
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


class StaffQuestionLookupViewSet(viewsets.ReadOnlyModelViewSet[Question]):
    """Vaqtinchalik faqat-o'qish `staff/questions/`.

    Savol banki boshqaruvi alohida bo'lim; u ulanganda bu ro'yxatdan
    o'chiriladi (`# staff: questions (fallback)` qatori). Test paneli
    faqat `{id, text}` ga tayanadi.
    """

    permission_classes = [IsAdminUser]
    pagination_class = StandardPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields: ClassVar[list[str]] = ["text"]
    ordering_fields: ClassVar[list[str]] = ["pk", "difficulty", "created_at"]
    ordering: ClassVar[list[str]] = ["-pk"]
    queryset = Question.objects.all()
    serializer_class = StaffQuestionLookupSerializer
