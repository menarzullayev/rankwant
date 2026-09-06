from __future__ import annotations

from typing import Any

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle

from core.models import User
from core.pagination import TimeCursorPagination
from core.permissions import CanSubmit
from judging.models import Attempt
from judging.serializers import (
    AttemptCreateSerializer,
    AttemptDetailSerializer,
    AttemptSerializer,
)
from judging.services import enqueue
from judging.verdicts import Verdict
from problems.models import Language, Problem


class AttemptViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet[Attempt],
):
    """Submit va urinishlar tarixi — PRD P0-3."""

    pagination_class = TimeCursorPagination
    throttle_scope = "submit"

    def get_permissions(self):  # type: ignore[no-untyped-def]
        if self.action == "create":
            return [IsAuthenticated(), CanSubmit()]
        return [AllowAny()]

    def get_throttles(self):  # type: ignore[no-untyped-def]
        return [ScopedRateThrottle()] if self.action == "create" else []

    def get_queryset(self):  # type: ignore[no-untyped-def]
        qs = Attempt.objects.select_related("user", "problem", "language")
        problem = self.request.query_params.get("problem")
        if problem:
            qs = qs.filter(problem__slug=problem)
        username = self.request.query_params.get("username")
        if username:
            qs = qs.filter(user__username=username)
        return qs.order_by("-created_at")

    def get_serializer_class(self):  # type: ignore[no-untyped-def]
        if self.action == "create":
            return AttemptCreateSerializer
        return AttemptDetailSerializer if self.action == "retrieve" else AttemptSerializer

    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        attempt = get_object_or_404(Attempt, pk=kwargs["pk"])
        data = AttemptDetailSerializer(attempt).data
        # Manba faqat egasiga va adminlarga ko'rinadi (IDOR himoyasi).
        if not (
            request.user.is_authenticated
            and (request.user.pk == attempt.user_id or request.user.is_staff)
        ):
            data.pop("source_code", None)
            data.pop("compile_output", None)
        return Response(data)

    @extend_schema(request=AttemptCreateSerializer, responses={201: AttemptSerializer})
    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = AttemptCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        assert isinstance(request.user, User)
        attempt = Attempt.objects.create(
            user=request.user,
            problem=Problem.objects.get(slug=data["problem"]),
            language=Language.objects.get(code=data["language"]),
            source_code=data["source_code"],
            verdict=Verdict.PENDING,
        )
        # Attempt AVVAL saqlanadi, keyin navbatga — navbat yiqilsa ham
        # submission yo'qolmaydi (10-operations § recovery).
        enqueue(attempt)
        return Response(AttemptSerializer(attempt).data, status=status.HTTP_201_CREATED)
