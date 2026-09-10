from __future__ import annotations

from typing import Any

from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from core.models import User
from core.pagination import TimeCursorPagination
from core.permissions import CanSubmit
from core.throttling import ResilientScopedRateThrottle
from judging.models import Attempt, CustomRun
from judging.serializers import (
    AttemptCreateSerializer,
    AttemptDetailSerializer,
    AttemptSerializer,
    CustomRunCreateSerializer,
    CustomRunSerializer,
)
from judging.services import enqueue, enqueue_custom
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
        return [ResilientScopedRateThrottle()] if self.action == "create" else []

    def get_queryset(self):  # type: ignore[no-untyped-def]
        params = self.request.query_params
        qs = Attempt.objects.select_related("user", "problem", "language")

        problem = params.get("problem")
        if problem:
            # ID bo'yicha — `problem__slug` ATAYIN emas. Join qo'shilishi
            # bilan Postgres `attempt_problem_feed` (problem, -created_at)
            # indeksidan foydalana olmay qoladi: u masalaning BARCHA
            # urinishlarini skanerlab, keyin saralab 26 tasini oladi.
            # O'lchandi (50 852 urinishli masala): 86.4 ms → 2.2 ms,
            # 156 881 bufer sahifasi o'rniga bir nechta.
            qs = qs.filter(problem_id=Problem.objects.filter(slug=problem).values("pk")[:1])
        username = params.get("username")
        if username:
            # Bu yerda esa join TEZROQ (o'lchandi: 6.0 ms, ID bilan 17.3) —
            # foydalanuvchi bo'yicha alohida indeks yo'q va rejalashtiruvchi
            # join'li shaklda yaxshiroq reja tanlaydi.
            qs = qs.filter(user__username=username)

        # Ommabop masalada urinish minglab bo'ladi va filtrsiz ro'yxat
        # o'qib bo'lmaydigan oqimga aylanadi (KEP ham verdikt, til va
        # «faqat meniki» filtrlarini beradi).
        verdict = params.get("verdict")
        if verdict:
            qs = qs.filter(verdict=verdict)
        language = params.get("language")
        if language:
            qs = qs.filter(language__code=language)
        if params.get("mine") in ("true", "1") and self.request.user.is_authenticated:
            qs = qs.filter(user=self.request.user)

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
        serializer = AttemptCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        assert isinstance(request.user, User)
        attempt = Attempt.objects.create(
            user=request.user,
            problem=Problem.objects.get(slug=data["problem"]),
            language=Language.objects.get(code=data["language"]),
            source_code=data["source_code"],
            contest=data.get("contest_obj"),
            verdict=Verdict.PENDING,
        )
        # Attempt AVVAL saqlanadi, keyin navbatga — navbat yiqilsa ham
        # submission yo'qolmaydi (10-operations § recovery).
        enqueue(attempt)
        return Response(AttemptSerializer(attempt).data, status=status.HTTP_201_CREATED)


class CustomRunViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet[CustomRun],
):
    """PRD P0-4 — custom test.

    Attempt EMAS: tarixga tushmaydi, reytingga ta'sir qilmaydi. Submit bilan
    bir xil rate limit qo'llanadi — bu ham judge resursini yeydi.
    """

    permission_classes = [IsAuthenticated, CanSubmit]
    throttle_scope = "submit"

    def get_throttles(self):  # type: ignore[no-untyped-def]
        return [ResilientScopedRateThrottle()] if self.action == "create" else []

    def get_queryset(self) -> QuerySet[CustomRun]:
        # Faqat o'z ishga tushirishlaringiz ko'rinadi
        assert isinstance(self.request.user, User)
        return CustomRun.objects.filter(user=self.request.user).select_related("language")

    def get_serializer_class(self):  # type: ignore[no-untyped-def]
        return CustomRunCreateSerializer if self.action == "create" else CustomRunSerializer

    @extend_schema(request=CustomRunCreateSerializer, responses={201: CustomRunSerializer})
    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = CustomRunCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        assert isinstance(request.user, User)
        run = CustomRun.objects.create(
            user=request.user,
            language=Language.objects.get(code=data["language"]),
            source_code=data["source_code"],
            stdin=data["stdin"],
            verdict=Verdict.PENDING,
        )
        enqueue_custom(run)
        return Response(CustomRunSerializer(run).data, status=status.HTTP_201_CREATED)
