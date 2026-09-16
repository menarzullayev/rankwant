from __future__ import annotations

from typing import Any

from django.db.models import Count, Max, OuterRef, Subquery
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from core.models import User
from core.openapi_docs import crud_summaries
from quizzes.models import Quiz, QuizAttempt
from quizzes.serializers import (
    QuizDetailSerializer,
    QuizResultSerializer,
    QuizSerializer,
    SubmitSerializer,
)
from quizzes.services import submit


@crud_summaries(
    one="test",
    many="testlar",
    only=("list", "retrieve"),
    extra={"submit": "Testni topshirish"},
)
class QuizViewSet(viewsets.ReadOnlyModelViewSet[Quiz]):
    """PRD P2-6 — nazariy testlar."""

    permission_classes = [AllowAny]
    lookup_field = "slug"

    def get_queryset(self):  # type: ignore[no-untyped-def]
        qs = Quiz.objects.filter(is_published=True).annotate(
            question_count=Count("items", distinct=True)
        )
        user = self.request.user
        if isinstance(user, User):
            best = (
                QuizAttempt.objects.filter(quiz=OuterRef("pk"), user=user)
                .values("quiz")
                .annotate(m=Max("score"))
                .values("m")[:1]
            )
            qs = qs.annotate(best_score=Subquery(best))
        return qs.order_by("-created_at")

    def get_serializer_class(self):  # type: ignore[no-untyped-def]
        return QuizDetailSerializer if self.action == "retrieve" else QuizSerializer

    @extend_schema(request=SubmitSerializer, responses={201: QuizResultSerializer})
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def submit(self, request: Request, slug: str | None = None) -> Response:
        quiz = self.get_object()
        serializer = SubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assert isinstance(request.user, User)

        attempt, review = submit(request.user, quiz, serializer.validated_data["answers"])
        data: dict[str, Any] = QuizResultSerializer(attempt).data
        data["review"] = review
        return Response(data, status=status.HTTP_201_CREATED)
