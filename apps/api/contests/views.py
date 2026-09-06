from __future__ import annotations

import json
import time
from collections.abc import Iterator
from typing import Any

from django.http import StreamingHttpResponse
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from contests.models import Contest, ContestRegistration, Standing
from contests.serializers import (
    ContestDetailSerializer,
    ContestSerializer,
    RegistrationSerializer,
    StandingSerializer,
)
from contests.services import start_virtual, virtual_deadline
from core.models import User

#: SSE oralig'i — 04-prd: standings 10–30 s da yangilansa yetarli.
SSE_INTERVAL_S = 10
SSE_MAX_DURATION_S = 300


class ContestViewSet(viewsets.ReadOnlyModelViewSet[Contest]):
    permission_classes = [AllowAny]
    lookup_field = "slug"
    queryset = Contest.objects.filter(is_public=True).prefetch_related("problems__problem")

    def get_serializer_class(self):  # type: ignore[no-untyped-def]
        return ContestDetailSerializer if self.action == "retrieve" else ContestSerializer

    @extend_schema(responses={200: StandingSerializer(many=True)})
    @action(detail=True, methods=["get"], permission_classes=[AllowAny])
    def standings(self, request: Request, slug: str | None = None) -> Response:
        contest = self.get_object()
        rows = (
            Standing.objects.filter(contest=contest).select_related("user").order_by("rank")[:500]
        )
        return Response(
            {
                "frozen": contest.is_frozen,
                "results": StandingSerializer(rows, many=True).data,
            }
        )

    @extend_schema(request=None, responses={201: RegistrationSerializer})
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def register(self, request: Request, slug: str | None = None) -> Response:
        contest = self.get_object()
        if contest.is_finished:
            return Response(
                {
                    "error": {
                        "code": "contest_finished",
                        "message": "Musobaqa tugagan",
                        "details": {},
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        assert isinstance(request.user, User)
        reg, created = ContestRegistration.objects.get_or_create(contest=contest, user=request.user)
        return Response(
            RegistrationSerializer(reg).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    @extend_schema(request=None, responses={201: RegistrationSerializer})
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def virtual(self, request: Request, slug: str | None = None) -> Response:
        """PRD P1-1 — tugagan musobaqani o'z vaqtingizda boshlash.

        Virtual ishtirok reytingga ta'sir qilmaydi va rasmiy jadvalga
        kirmaydi (contests.services.rebuild_standings).
        """
        contest = self.get_object()
        assert isinstance(request.user, User)
        try:
            reg = start_virtual(contest, request.user)
        except ValueError as exc:
            return Response(
                {"error": {"code": "not_finished", "message": str(exc), "details": {}}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = RegistrationSerializer(reg).data
        data["deadline"] = virtual_deadline(reg)
        return Response(data, status=status.HTTP_201_CREATED)


def standings_stream(request: Any, slug: str) -> StreamingHttpResponse:
    """SSE — 04-prd: WebSocket emas.

    Ba'zi korporativ/maktab proxy'lari SSE ni buferlaydi (test-strategy
    § compatibility), shuning uchun mijoz polling fallback'ga ega bo'lishi
    kerak. `X-Accel-Buffering: no` nginx buferlashini o'chiradi.
    """
    contest = get_object_or_404(Contest, slug=slug, is_public=True)

    def event_stream() -> Iterator[str]:
        deadline = time.monotonic() + SSE_MAX_DURATION_S
        last_payload = None
        while time.monotonic() < deadline:
            rows = list(
                Standing.objects.filter(contest=contest)
                .select_related("user")
                .order_by("rank")[:500]
            )
            payload = json.dumps(
                {
                    "frozen": contest.is_frozen,
                    "results": StandingSerializer(rows, many=True).data,
                },
                default=str,
            )
            if payload != last_payload:
                last_payload = payload
                yield f"event: standings\ndata: {payload}\n\n"
            else:
                yield ": keep-alive\n\n"
            time.sleep(SSE_INTERVAL_S)

    response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"
    return response
