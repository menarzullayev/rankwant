from __future__ import annotations

import json
import time
from collections.abc import Iterator
from typing import Any

from django.db.models import Count
from django.http import StreamingHttpResponse
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from arena.models import ArenaAnswer, ArenaRound
from arena.serializers import (
    AnswerResultSerializer,
    AnswerSerializer,
    ArenaDetailSerializer,
    ArenaSerializer,
    ArenaStandingSerializer,
    CurrentQuestionSerializer,
)
from arena.services import ArenaError, answer, join, standings
from core.models import User
from quizzes.serializers import QuestionPublicSerializer

#: Arena tez — savol 30–90 s. Standings 3 s da yangilansa yetarli.
SSE_INTERVAL_S = 3
SSE_MAX_DURATION_S = 900


def _error(exc: ArenaError, http_status: int = status.HTTP_400_BAD_REQUEST) -> Response:
    return Response(
        {"error": {"code": exc.code, "message": exc.message, "details": {}}}, status=http_status
    )


class ArenaViewSet(viewsets.ReadOnlyModelViewSet[ArenaRound]):
    """Jonli savol-javob raundi."""

    permission_classes = [AllowAny]
    lookup_field = "slug"

    def get_queryset(self):  # type: ignore[no-untyped-def]
        return (
            ArenaRound.objects.filter(is_public=True)
            .annotate(
                question_count=Count("items", distinct=True),
                participant_count=Count("participants", distinct=True),
            )
            .order_by("-start_at")
        )

    def get_serializer_class(self):  # type: ignore[no-untyped-def]
        return ArenaDetailSerializer if self.action == "retrieve" else ArenaSerializer

    @extend_schema(request=None, responses={201: ArenaDetailSerializer})
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def join(self, request: Request, slug: str | None = None) -> Response:
        arena = self.get_object()
        assert isinstance(request.user, User)
        try:
            join(request.user, arena)
        except ArenaError as exc:
            return _error(exc)
        return Response(
            ArenaDetailSerializer(arena, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(responses={200: CurrentQuestionSerializer})
    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated])
    def current(self, request: Request, slug: str | None = None) -> Response:
        """Hozir ochiq savol. Kelgusi savol BERILMAYDI — u hali ochilmagan."""
        arena = self.get_object()
        index = arena.current_index
        if index is None:
            return _error(ArenaError("not_running", "Raund hozir yurmayapti"))
        item = arena.items.select_related("question").filter(order=index + 1).first()
        if item is None:
            return _error(ArenaError("not_running", "Raund tugadi"))
        assert isinstance(request.user, User)
        answered = ArenaAnswer.objects.filter(
            participation__round=arena,
            participation__user=request.user,
            question=item.question,
        ).exists()
        return Response(
            {
                "index": index,
                "deadline": arena.question_deadline(index),
                "seconds_per_question": arena.seconds_per_question,
                "question": QuestionPublicSerializer(item.question).data,
                "answered": answered,
            }
        )

    @extend_schema(request=AnswerSerializer, responses={201: AnswerResultSerializer})
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def answer(self, request: Request, slug: str | None = None) -> Response:
        arena = self.get_object()
        serializer = AnswerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assert isinstance(request.user, User)
        try:
            record = answer(
                request.user,
                arena,
                serializer.validated_data["question_id"],
                serializer.validated_data["choice_id"],
            )
        except ArenaError as exc:
            return _error(exc)
        return Response(
            {
                "is_correct": record.is_correct,
                "points": record.points,
                "elapsed_ms": record.elapsed_ms,
            },
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(responses={200: ArenaStandingSerializer(many=True)})
    @action(detail=True, methods=["get"], permission_classes=[AllowAny])
    def standings(self, request: Request, slug: str | None = None) -> Response:
        return Response({"results": standings(self.get_object())})


def standings_stream(request: Any, slug: str) -> StreamingHttpResponse:
    """SSE — contests bilan bir xil naqsh, faqat oraliq qisqaroq."""
    arena = get_object_or_404(ArenaRound, slug=slug, is_public=True)

    def event_stream() -> Iterator[str]:
        deadline = time.monotonic() + SSE_MAX_DURATION_S
        last_payload = None
        while time.monotonic() < deadline:
            payload = json.dumps(
                {
                    "current_index": arena.current_index,
                    "finished": arena.is_finished,
                    "results": standings(arena),
                },
                default=str,
            )
            if payload != last_payload:
                last_payload = payload
                yield f"event: standings\ndata: {payload}\n\n"
            else:
                yield ": keep-alive\n\n"
            if arena.is_finished:
                break
            time.sleep(SSE_INTERVAL_S)

    response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"
    return response
