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
from quizzes import services
from quizzes.models import Quiz, QuizAttempt
from quizzes.serializers import (
    QuizDetailSerializer,
    QuizResultSerializer,
    QuizSerializer,
    QuizStartSerializer,
    QuizSubmitSerializer,
)
from quizzes.services import QuizError


def _failed(exc: QuizError) -> Response:
    return Response(
        {"error": {"code": exc.code, "message": str(exc), "details": {}}},
        status=status.HTTP_400_BAD_REQUEST,
    )


def _result(attempt: QuizAttempt, review: list[services.ReviewItem]) -> dict[str, Any]:
    data: dict[str, Any] = QuizResultSerializer(attempt).data
    shown = services.answers_shown(attempt.quiz)
    data["review"] = review if shown else services.hidden(review)
    data["answers_hidden"] = not shown
    return data


@crud_summaries(
    one="test",
    many="testlar",
    only=("list", "retrieve"),
    extra={
        "submit": "Testni topshirish",
        "start": "Vaqtli testni boshlash",
        "result": "Oxirgi natija",
    },
)
class QuizViewSet(viewsets.ReadOnlyModelViewSet[Quiz]):
    """PRD P2-6 — nazariy testlar."""

    permission_classes = [AllowAny]
    lookup_field = "slug"

    def get_queryset(self):  # type: ignore[no-untyped-def]
        user = self.request.user
        if self.action == "list":
            # The catalogue lists public quizzes only; a teacher's quiz is
            # reached from the class it is given to (ADR-0061 § 5).
            base = Quiz.objects.filter(owner=None, is_published=True)
        else:
            base = services.visible_to(user if isinstance(user, User) else None)
        qs = base.annotate(question_count=Count("items", distinct=True))
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

    def get_serializer_context(self) -> dict[str, Any]:
        return {**super().get_serializer_context(), "user": self.request.user}

    @extend_schema(request=QuizSubmitSerializer, responses={201: QuizResultSerializer})
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def submit(self, request: Request, slug: str | None = None) -> Response:
        quiz = self.get_object()
        serializer = QuizSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assert isinstance(request.user, User)
        try:
            attempt, review = services.submit(
                request.user, quiz, serializer.validated_data["answers"]
            )
        except QuizError as exc:
            return _failed(exc)
        return Response(_result(attempt, review), status=status.HTTP_201_CREATED)

    @extend_schema(request=None, responses={201: QuizStartSerializer})
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def start(self, request: Request, slug: str | None = None) -> Response:
        """Open an attempt; a timed quiz shows its questions after this."""
        quiz = self.get_object()
        assert isinstance(request.user, User)
        try:
            attempt = services.start(request.user, quiz)
        except QuizError as exc:
            return _failed(exc)
        return Response(
            {"deadline": services.deadline(quiz, attempt)}, status=status.HTTP_201_CREATED
        )

    @extend_schema(responses={200: QuizResultSerializer})
    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated])
    def result(self, request: Request, slug: str | None = None) -> Response:
        """The latest finished attempt, with its review once answers are shown."""
        quiz = self.get_object()
        assert isinstance(request.user, User)
        found = services.last_result(request.user, quiz)
        if found is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(_result(*found))
