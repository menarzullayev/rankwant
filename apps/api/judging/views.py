from __future__ import annotations

from typing import Any, Never

from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from core.models import User
from core.openapi_docs import crud_summaries
from core.pagination import TimeCursorPagination
from core.permissions import CanSubmit
from core.throttling import ResilientScopedRateThrottle
from hacks.services import can_view_source
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

#: Rad etilgan yuborishning manbasi tarix uchun saqlanadi, lekin to'liq
#: emas: bu qator natija emas, iz.
MAX_SOURCE_CHARS = 4096


@crud_summaries(one="urinish", many="urinishlar", only=("list", "retrieve", "create"))
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

    def throttled(self, request: Request, wait: float) -> Never:
        """Shift urilganini TARIXGA yozadi, keyin odatdagidek 429 beradi.

        Ilgari rad etilgan yuborish hech qanday iz qoldirmasdi:
        foydalanuvchi «yubordim, qayoqqa ketdi?» degan savol bilan
        qolardi. Endi urinishlar ro'yxatida `RATE_LIMITED` ko'rinadi.

        Bitta portlash — BITTA qator: aks holda sekundiga yuzlab rad
        etilgan so'rov shuncha qator yasab, bazani to'ldirish yo'liga
        aylanardi. Oxirgi urinish allaqachon `RATE_LIMITED` bo'lsa,
        yangisi yozilmaydi.
        """
        data = request.data if isinstance(request.data, dict) else {}
        if self.action == "create" and request.user.is_authenticated:
            oxirgi = (
                Attempt.objects.filter(user=request.user).order_by("-created_at", "-pk").first()
            )
            if oxirgi is None or oxirgi.verdict != Verdict.RATE_LIMITED:
                problem = Problem.objects.filter(slug=data.get("problem")).first()
                language = Language.objects.filter(code=data.get("language")).first()
                if problem and language:
                    Attempt.objects.create(
                        user=request.user,
                        problem=problem,
                        language=language,
                        source_code=str(data.get("source_code", ""))[:MAX_SOURCE_CHARS],
                        verdict=Verdict.RATE_LIMITED,
                        judged_at=timezone.now(),
                    )
        super().throttled(request, wait)

    def get_throttles(self):  # type: ignore[no-untyped-def]
        return [ResilientScopedRateThrottle()] if self.action == "create" else []

    def get_queryset(self):  # type: ignore[no-untyped-def]
        params = self.request.query_params
        # `contest` ham SHU YERDA: serializer uning slug'ini beradi va
        # usiz har qator uchun alohida so'rov ketardi (N+1).
        qs = Attempt.objects.select_related("user", "problem", "language", "contest")

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
            # Vergulli ro'yxat: `RE` ikkiga ajratilgandan keyin bitta
            # «Bajarilishda xato» filtri eski `RE` ni ham, yangi
            # `RE_SIGNAL`/`RE_EXIT` ni ham qamrashi kerak.
            qs = qs.filter(verdict__in=[v for v in verdict.split(",") if v])
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
            and (
                request.user.pk == attempt.user_id
                or request.user.is_staff
                # Hack oynasi ochiq va so'rovchi huquqli bo'lsa — aynan shu
                # yechim ochiladi (ADR-0020, 2-tamoyil). Bu umumiy
                # yopiqlikni almashtirmaydi, ustiga nuqtali istisno qo'yadi:
                # hack qilish uchun kodni ko'rish SHART.
                or can_view_source(request.user, attempt)
            )
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


@crud_summaries(one="namunaviy yugurish", many="namunaviy yugurishlar", only=("create", "retrieve"))
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
        # Faqat o'z ishga tushirishlaringiz ko'rinadi. Sxema
        # generatsiyasida `request.user` — AnonymousUser (o'lchandi
        # 2026-09-24: "could not derive type of path parameter id").
        if getattr(self, "swagger_fake_view", False):
            return CustomRun.objects.none()
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
