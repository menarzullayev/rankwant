"""Hack endpointlari — ADR-0020.

Dvigatel `hacks.services` da; bu qatlam faqat so'rovni unga olib boradi
va rad javobini yagona xato formatiga o'giradi (08-technical-spec).
"""

from __future__ import annotations

from typing import Any, Never

from django.utils import timezone
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import mixins, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from contests.models import Contest
from core.models import User
from core.openapi_docs import crud_summaries
from core.pagination import TimeCursorPagination
from core.throttling import ResilientScopedRateThrottle
from hacks import services
from hacks.models import Hack, HackLock
from hacks.serializers import (
    HackCreateSerializer,
    HackDetailSerializer,
    HackEligibilitySerializer,
    HackLockCreateSerializer,
    HackLockSerializer,
    HackRoomSerializer,
    HackSerializer,
)
from judging.models import Attempt
from problems.models import Problem


def _error(exc: services.HackError) -> Response:
    """Dvigatelning rad javobi — 400 va SABAB.

    Sabab har doim uzatiladi: «hack qilib bo'lmaydi» degan quruq xabar
    foydalanuvchini nima yetishmayotganini taxmin qilishga majburlardi.
    """
    return Response(
        {"error": {"code": "hack_rejected", "message": str(exc), "details": {}}},
        status=status.HTTP_400_BAD_REQUEST,
    )


def _attempt_from(value: Any) -> Attempt | None:
    """So'rovdagi `attempt` ni xavfsiz o'giradi.

    Qiymat foydalanuvchidan keladi: `pk=` ga to'g'ridan-to'g'ri berilsa
    raqam bo'lmagan satr `ValueError` bilan 500 qaytarardi.
    """
    if not isinstance(value, int | str) or not str(value).isdigit():
        return None
    return (
        Attempt.objects.select_related("problem", "language", "contest", "user")
        .filter(pk=int(value))
        .first()
    )


@crud_summaries(
    one="hack urinishi",
    many="hack urinishlari",
    only=("list", "retrieve", "create"),
    extra={"eligibility": "Qatnashish huquqi", "room": "Hack xonasi holati"},
)
class HackViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet[Hack],
):
    """Hack yuborish va natijalar — ADR-0020."""

    pagination_class = TimeCursorPagination
    throttle_scope = "hack"

    def get_permissions(self):  # type: ignore[no-untyped-def]
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_throttles(self):  # type: ignore[no-untyped-def]
        return [ResilientScopedRateThrottle()] if self.action == "create" else []

    def throttled(self, request: Request, wait: float) -> Never:
        """Shift urilganini KO'RINADIGAN qilib yozadi, keyin 429 beradi.

        `Attempt.RATE_LIMITED` pretsedenti (`judging.views`): jim rad
        etilgan yuborish foydalanuvchini «yubordim, qayoqqa ketdi?»
        savoli bilan qoldiradi. Bitta portlash — bitta qator, aks holda
        rad etilgan so'rovlarning o'zi bazani to'ldirish yo'li bo'lardi.
        """
        data = request.data if isinstance(request.data, dict) else {}
        if self.action == "create" and request.user.is_authenticated:
            last = Hack.objects.filter(hacker=request.user).order_by("-created_at", "-pk").first()
            attempt = _attempt_from(data.get("attempt"))
            if attempt is not None and (last is None or last.status != Hack.Status.RATE_LIMITED):
                policy = services.open_policy(attempt)
                Hack.objects.create(
                    hacker=request.user,
                    defender_attempt=attempt,
                    problem=attempt.problem,
                    contest=attempt.contest,
                    policy=policy.code if policy else "",
                    status=Hack.Status.RATE_LIMITED,
                    stage=Hack.Stage.DONE,
                    judged_at=timezone.now(),
                )
        super().throttled(request, wait)

    def get_queryset(self):  # type: ignore[no-untyped-def]
        params = self.request.query_params
        qs = Hack.objects.select_related(
            "hacker", "problem", "contest", "generator_language", "defender_attempt__user"
        )
        problem = params.get("problem")
        if problem:
            # Slug bo'yicha join EMAS: `hack_problem_feed` indeksi
            # (problem, -created_at) shundagina ishlaydi — urinishlar
            # ro'yxatidagi bilan bir xil sabab (`judging.views`).
            qs = qs.filter(problem_id=Problem.objects.filter(slug=problem).values("pk")[:1])
        contest = params.get("contest")
        if contest:
            qs = qs.filter(contest_id=Contest.objects.filter(slug=contest).values("pk")[:1])
        attempt = params.get("attempt")
        if attempt and attempt.isdigit():
            # Bitta yechimga qilingan hacklar — urinish sahifasi shuni
            # ko'rsatadi. `isdigit` tekshiruvi SHART: xom satr bilan
            # filtrlash `ValueError` bilan 500 qaytarardi.
            qs = qs.filter(defender_attempt_id=int(attempt))
        status_param = params.get("status")
        if status_param:
            qs = qs.filter(status__in=[s for s in status_param.split(",") if s])
        if params.get("mine") in ("true", "1") and self.request.user.is_authenticated:
            qs = qs.filter(hacker=self.request.user)
        return qs.order_by("-created_at", "-pk")

    def get_serializer_class(self):  # type: ignore[no-untyped-def]
        return HackDetailSerializer if self.action == "retrieve" else HackSerializer

    @extend_schema(request=HackCreateSerializer, responses={201: HackSerializer})
    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = HackCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        assert isinstance(request.user, User)
        try:
            hack = services.submit(
                request.user,
                data["attempt_obj"],
                raw_input=data.get("test_input", ""),
                generator_language=data.get("generator_language_obj"),
                generator_source=data.get("generator_source", ""),
            )
        except services.HackError as exc:
            return _error(exc)
        return Response(
            HackSerializer(hack, context=self.get_serializer_context()).data,
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        parameters=[OpenApiParameter("attempt", int, required=True)],
        responses={200: HackEligibilitySerializer},
    )
    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def eligibility(self, request: Request) -> Response:
        """«Men buni hack qila olamanmi va nega yo'q?»

        UI shu javobga qarab tugmani ko'rsatadi. Tekshiruv dvigatelning
        O'ZIDAN so'raladi, ya'ni ko'rsatilgan sabab yuborishda qo'llanadigan
        qoida bilan bir xil bo'ladi.
        """
        attempt = _attempt_from(request.query_params.get("attempt"))
        if attempt is None:
            raise serializers.ValidationError({"attempt": "Urinish topilmadi"})

        assert isinstance(request.user, User)
        policy = services.open_policy(attempt)
        if policy is None:
            return Response(
                {
                    "can_hack": False,
                    "reason": "Bu yechim uchun hack oynasi yopiq",
                    "policy": None,
                    "policy_label": "",
                    "needs_lock": False,
                    "locked": False,
                }
            )
        reason = services.eligibility(request.user, attempt, policy)
        locked = bool(
            attempt.contest_id
            and HackLock.objects.filter(
                contest_id=attempt.contest_id,
                problem_id=attempt.problem_id,
                user=request.user,
            ).exists()
        )
        return Response(
            {
                "can_hack": not reason,
                "reason": reason,
                "policy": policy.code,
                "policy_label": policy.label,
                "needs_lock": policy.needs_lock,
                "locked": locked,
            }
        )

    @extend_schema(
        parameters=[OpenApiParameter("contest", str, required=True)],
        responses={200: HackRoomSerializer},
    )
    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def room(self, request: Request) -> Response:
        """O'z xonangiz va undagi ishtirokchilar (`contest_room`)."""
        contest = Contest.objects.filter(slug=request.query_params.get("contest") or "").first()
        if contest is None:
            raise serializers.ValidationError({"contest": "Musobaqa topilmadi"})
        assert isinstance(request.user, User)
        room = services.room_of(contest, request.user)
        if room is None:
            raise serializers.ValidationError({"contest": "Musobaqaga ro'yxatdan o'ting"})
        members = list(
            User.objects.filter(hack_rooms__room=room)
            .order_by("username")
            .values_list("username", flat=True)
        )
        return Response({"number": room.number, "members": members})


@crud_summaries(one="hack qulfi", many="hack qulflari")
class HackLockViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet[HackLock],
):
    """Masalani lock qilish — `contest_room` siyosatining sharti.

    `destroy` ATAYIN yo'q: lock qaytarilsa u xatar bo'lmay qolardi va
    hack huquqi tekinga aylanardi (ADR-0020).
    """

    permission_classes = [IsAuthenticated]
    serializer_class = HackLockSerializer

    def get_queryset(self):  # type: ignore[no-untyped-def]
        # Faqat O'Z locklaringiz: raqibning qaysi masalani lock qilgani
        # musobaqa davomida taktik ma'lumot.
        assert isinstance(self.request.user, User)
        qs = HackLock.objects.filter(user=self.request.user).select_related("contest", "problem")
        slug = self.request.query_params.get("contest")
        return qs.filter(contest__slug=slug) if slug else qs

    @extend_schema(request=HackLockCreateSerializer, responses={201: HackLockSerializer})
    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = HackLockCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        contest = Contest.objects.filter(slug=data["contest"]).first()
        if contest is None:
            raise serializers.ValidationError({"contest": "Musobaqa topilmadi"})
        problem = Problem.objects.filter(slug=data["problem"]).first()
        if problem is None:
            raise serializers.ValidationError({"problem": "Masala topilmadi"})

        assert isinstance(request.user, User)
        try:
            lock = services.lock(request.user, contest, problem)
        except services.HackError as exc:
            return _error(exc)
        return Response(HackLockSerializer(lock).data, status=status.HTTP_201_CREATED)
