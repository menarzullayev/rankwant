"""`/quizzes/mine/`, `/questions/mine/`, `/question-folders/` — a teacher's own
quizzes and question bank (ADR-0061 § 5). Anyone signed in may write them;
the plan's `quizzes` quota limits the quizzes."""

from __future__ import annotations

from typing import Any

from django.db.models import Count, ProtectedError
from rest_framework import status, viewsets
from rest_framework.exceptions import APIException
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from core import quotas
from core.models import User
from core.openapi_docs import crud_summaries
from quizzes.author_serializers import (
    AuthorQuestionSerializer,
    AuthorQuizSerializer,
    FolderSerializer,
)
from quizzes.models import Question, QuestionFolder, Quiz


class QuotaLimit(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "quota_exceeded"
    default_detail = "Your plan's quiz limit is reached"


class InUse(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "quiz_in_use"
    default_detail = "Given to a class or already taken: it cannot be deleted"


def _user(request: Request) -> User:
    assert isinstance(request.user, User)
    return request.user


@crud_summaries(one="savol papkasi", many="savol papkalari")
class FolderViewSet(viewsets.ModelViewSet[QuestionFolder]):
    serializer_class = FolderSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self) -> dict[str, Any]:
        return {**super().get_serializer_context(), "user": self.request.user}

    pagination_class = None
    http_method_names = ["get", "post", "patch", "delete"]

    def get_queryset(self):  # type: ignore[no-untyped-def]
        if getattr(self, "swagger_fake_view", False):
            return QuestionFolder.objects.none()
        return QuestionFolder.objects.filter(owner=_user(self.request)).annotate(
            question_count=Count("questions")
        )

    def perform_create(self, serializer: Any) -> None:
        serializer.save(owner=_user(self.request))


@crud_summaries(one="o'z savolim", many="o'z savollarim")
class MyQuestionViewSet(viewsets.ModelViewSet[Question]):
    serializer_class = AuthorQuestionSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self) -> dict[str, Any]:
        return {**super().get_serializer_context(), "user": self.request.user}

    http_method_names = ["get", "post", "patch", "delete"]

    def get_queryset(self):  # type: ignore[no-untyped-def]
        if getattr(self, "swagger_fake_view", False):
            return Question.objects.none()
        rows = (
            Question.objects.filter(owner=_user(self.request))
            .annotate(used=Count("quiz_items", distinct=True))
            .prefetch_related("choices")
            .order_by("-created_at")
        )
        folder = self.request.query_params.get("folder")
        if folder == "none":
            rows = rows.filter(folder=None)
        elif folder and folder.isdigit():
            rows = rows.filter(folder_id=int(folder))
        return rows

    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        question = self.get_object()
        if question.quiz_items.exists():
            return Response(
                {
                    "error": {
                        "code": "question_in_quiz",
                        "message": "Take it out of its quizzes first",
                        "details": {},
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        question.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@crud_summaries(one="o'z testim", many="o'z testlarim")
class MyQuizViewSet(viewsets.ModelViewSet[Quiz]):
    serializer_class = AuthorQuizSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self) -> dict[str, Any]:
        return {**super().get_serializer_context(), "user": self.request.user}

    lookup_field = "slug"
    pagination_class = None
    http_method_names = ["get", "post", "patch", "delete"]

    def get_queryset(self):  # type: ignore[no-untyped-def]
        if getattr(self, "swagger_fake_view", False):
            return Quiz.objects.none()
        return (
            Quiz.objects.filter(owner=_user(self.request))
            .annotate(
                attempt_count=Count("attempts", distinct=True),
                assignment_count=Count("classroom_assignments", distinct=True),
            )
            .order_by("-created_at")
        )

    def perform_create(self, serializer: Any) -> None:
        try:
            quotas.enforce(_user(self.request), "quizzes")
        except quotas.QuotaExceeded as exc:
            raise QuotaLimit(str(exc)) from exc
        serializer.save()

    def perform_destroy(self, instance: Quiz) -> None:
        if instance.attempts.exists():
            raise InUse()
        try:
            instance.delete()
        except ProtectedError as exc:  # given to a class
            raise InUse() from exc
