"""Auth va token endpointlari — ADR-0008."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

import redis
from django.conf import settings
from django.contrib.auth import authenticate as django_authenticate
from django.contrib.auth import login, logout
from django.core.cache import cache
from django.db import connection
from django.db.models import Q, QuerySet
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import generics, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from contests.models import Contest
from core.models import ApiToken, User
from core.pagination import StandardPagination, TimeCursorPagination
from core.serializers import (
    ApiTokenCreateSerializer,
    ApiTokenSerializer,
    LoginSerializer,
    MeSerializer,
    RegisterSerializer,
    UserPublicSerializer,
)
from judging.models import Attempt
from problems.models import Problem

MAX_TOKEN_LIFETIME = timedelta(days=365)


class HealthView(APIView):
    """Readiness — 10-operations § deploy va monitoring.

    Bog'liqliklar HAQIQATAN tekshiriladi. Shartsiz `ok` qaytaradigan
    health endpoint yo'qidan yomonroq: DB o'lganda ham load balancer
    trafikni shu instansiyaga yuborishda davom etadi, chaos sinovi esa
    hech narsani o'lchamaydi.
    """

    permission_classes = [AllowAny]
    authentication_classes: list[Any] = []
    #: Throttle kesh (Redis) ga tayanadi. Health aynan shu bog'liqlik
    #: haqida hisobot beradi, ya'ni unga tayana olmaydi: Redis o'lganda
    #: throttle o'zi 500 bilan yiqilib, hisobotni bermay qo'yardi.
    throttle_classes: list[Any] = []

    @extend_schema(
        responses={
            200: OpenApiResponse(description="Barcha bog'liqliklar javob beradi"),
            503: OpenApiResponse(description="Bog'liqlik yetib bo'lmaydi"),
        }
    )
    def get(self, request: Request) -> Response:
        checks = {"database": _check_database(), "redis": _check_redis()}
        healthy = all(v == "ok" for v in checks.values())
        return Response(
            {"status": "ok" if healthy else "degraded", "checks": checks},
            status=status.HTTP_200_OK if healthy else status.HTTP_503_SERVICE_UNAVAILABLE,
        )


def _check_database() -> str:
    try:
        connection.ensure_connection()
    except Exception as exc:
        return type(exc).__name__
    return "ok"


def _check_redis() -> str:
    try:
        redis.Redis.from_url(settings.REDIS_URL, socket_connect_timeout=2).ping()
    except Exception as exc:
        return type(exc).__name__
    return "ok"


class PlatformStatsView(APIView):
    """Mehmon bosh sahifasi uchun umumiy raqamlar.

    Urinishlar soni boshqa hech qayerdan olinmaydi: `/attempts/` cursor
    paginatsiyada ishlaydi va `count` qaytarmaydi. Katta jadvalda
    `COUNT(*)` arzon emas, shuning uchun natija keshlanadi — landing
    raqami bir daqiqa eskirsa hech narsa yo'qotilmaydi.
    """

    permission_classes = [AllowAny]
    authentication_classes: list[Any] = []
    CACHE_S = 60

    @extend_schema(responses={200: OpenApiResponse(description="Platforma statistikasi")})
    def get(self, request: Request) -> Response:
        stats = cache.get("platform-stats")
        if stats is None:
            stats = {
                "users": User.objects.filter(is_active=True).count(),
                "problems": Problem.objects.filter(is_public=True).count(),
                "contests": Contest.objects.filter(is_public=True).count(),
                "attempts": Attempt.objects.count(),
            }
            cache.set("platform-stats", stats, self.CACHE_S)
        return Response(stats)


class CalendarView(APIView):
    """Barcha tadbirlar bir joyda — musobaqa, arena, chempionat, hakaton.

    Duellar shaxsiy: faqat kirgan foydalanuvchining o'zinikilari.
    """

    permission_classes = [AllowAny]
    DEFAULT_DAYS = 60

    @extend_schema(responses={200: OpenApiResponse(description="Tadbirlar ro'yxati")})
    def get(self, request: Request) -> Response:
        from arena.models import ArenaRound
        from duels.models import Duel
        from hackathons.models import Hackathon
        from tournaments.models import Tournament

        now = timezone.now()
        start = _parse_date(request.query_params.get("from")) or now - timedelta(days=7)
        end = _parse_date(request.query_params.get("to")) or now + timedelta(days=self.DEFAULT_DAYS)

        events: list[dict[str, Any]] = []

        def add(kind: str, slug: str, title: str, start_at: Any, end_at: Any, **extra: Any) -> None:
            events.append(
                {
                    "kind": kind,
                    "slug": slug,
                    "title": title,
                    "start_at": start_at,
                    "end_at": end_at,
                    **extra,
                }
            )

        for c in Contest.objects.filter(is_public=True, start_at__range=(start, end)):
            add("contest", c.slug, c.title, c.start_at, c.end_at, is_rated=c.is_rated)
        for a in ArenaRound.objects.filter(is_public=True, start_at__range=(start, end)):
            add("arena", a.slug, a.title, a.start_at, a.end_at)
        for t in Tournament.objects.filter(is_public=True, start_at__range=(start, end)):
            add("tournament", t.slug, t.title, t.start_at, t.end_at)
        for h in Hackathon.objects.filter(is_public=True, start_at__range=(start, end)):
            add(
                "hackathon",
                h.slug,
                h.title,
                h.start_at,
                h.end_at,
                submission_deadline=h.submission_deadline,
            )
        if isinstance(request.user, User):
            mine = Duel.objects.filter(
                status=Duel.Status.ACCEPTED, start_at__range=(start, end)
            ).filter(Q(challenger=request.user) | Q(opponent=request.user))
            for d in mine:
                add("duel", d.slug, d.title, d.start_at, d.end_at)

        events.sort(key=lambda e: e["start_at"])
        return Response({"from": start, "to": end, "results": events})


def _parse_date(raw: str | None) -> Any:
    if not raw:
        return None
    from django.utils.dateparse import parse_datetime

    parsed = parse_datetime(raw)
    if parsed is not None and timezone.is_naive(parsed):
        parsed = timezone.make_aware(parsed)
    return parsed


class SearchView(APIView):
    """Header qidiruvi — har turdan bir nechta natija, tez."""

    permission_classes = [AllowAny]
    PER_TYPE = 5

    @extend_schema(responses={200: OpenApiResponse(description="Qidiruv natijalari")})
    def get(self, request: Request) -> Response:
        from content.models import Article

        q = (request.query_params.get("q") or "").strip()
        if len(q) < 2:
            return Response({"q": q, "problems": [], "users": [], "articles": [], "contests": []})
        n = self.PER_TYPE
        return Response(
            {
                "q": q,
                "problems": [
                    {"slug": p.slug, "title": p.title, "difficulty": p.difficulty}
                    for p in Problem.objects.filter(is_public=True, title__icontains=q)[:n]
                ],
                "users": [
                    {
                        "username": u.username,
                        "display_name": u.display_name,
                        "rating_skills": u.rating_skills,
                    }
                    for u in User.objects.filter(is_active=True).filter(
                        Q(username__icontains=q) | Q(display_name__icontains=q)
                    )[:n]
                ],
                "articles": [
                    {"slug": a.slug, "title": a.title, "kind": a.kind}
                    for a in Article.objects.filter(is_published=True, title__icontains=q)[:n]
                ],
                "contests": [
                    {"slug": c.slug, "title": c.title, "start_at": c.start_at}
                    for c in Contest.objects.filter(is_public=True, title__icontains=q)[:n]
                ],
            }
        )


class RegisterView(generics.CreateAPIView[User]):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    queryset = User.objects.all()


class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(request=LoginSerializer, responses={200: MeSerializer})
    def post(self, request: Request) -> Response:
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = django_authenticate(
            request,
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
        )
        if user is None:
            return Response(
                {
                    "error": {
                        "code": "invalid_credentials",
                        "message": "Login yoki parol noto'g'ri",
                        "details": {},
                    }
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )
        login(request, user)
        return Response(MeSerializer(user).data)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=None, responses={204: None})
    def post(self, request: Request) -> Response:
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(generics.RetrieveUpdateAPIView[User]):
    serializer_class = MeSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self) -> User:
        assert isinstance(self.request.user, User)
        return self.request.user

    def perform_update(self, serializer: Any) -> None:
        user = serializer.save()
        # Profil to'ldirilgan bo'lsa — bir martalik quest (ADR-0002)
        from qvant.quests import on_profile_completed, profile_is_complete

        if profile_is_complete(user):
            on_profile_completed(user)


class UserViewSet(viewsets.ReadOnlyModelViewSet[User]):
    """Ommaviy profil va leaderboard."""

    serializer_class = UserPublicSerializer
    permission_classes = [AllowAny]
    lookup_field = "username"
    queryset = User.objects.filter(is_active=True)
    ordering_fields = ["rating_skills", "rating_contest", "rating_challenges", "date_joined"]
    ordering = ["-rating_skills"]


class RatingHistoryView(generics.ListAPIView[Any]):
    """Reyting o'zgarishlari tarixi — 05-domain-model 🔒.

    Ommaviy: reyting qanday shakllanganini har kim ko'ra olishi kerak
    (principle #2). Sabab, eski va yangi qiymat, contest holatida esa
    seed va rank ham beriladi.
    """

    permission_classes = [AllowAny]
    pagination_class = TimeCursorPagination

    def get_serializer_class(self):  # type: ignore[no-untyped-def]
        from ratings.serializers import RatingHistorySerializer

        return RatingHistorySerializer

    def get_queryset(self):  # type: ignore[no-untyped-def]
        from ratings.models import RatingHistory

        user = get_object_or_404(User, username=self.kwargs["username"], is_active=True)
        qs = RatingHistory.objects.filter(user=user)
        rating_type = self.request.query_params.get("type")
        if rating_type:
            qs = qs.filter(rating_type=rating_type)
        return qs


class SolvedProblemsView(generics.ListAPIView[Any]):
    """Foydalanuvchi yechgan masalalar — Skills reytingining manbai."""

    permission_classes = [AllowAny]
    pagination_class = StandardPagination

    def get_serializer_class(self):  # type: ignore[no-untyped-def]
        from ratings.serializers import SolvedProblemSerializer

        return SolvedProblemSerializer

    def get_queryset(self):  # type: ignore[no-untyped-def]
        from ratings.models import UserSolvedProblem

        user = get_object_or_404(User, username=self.kwargs["username"], is_active=True)
        return (
            UserSolvedProblem.objects.filter(user=user)
            .select_related("problem")
            .order_by("-problem__difficulty")
        )


class ApiTokenViewSet(viewsets.ModelViewSet[ApiToken]):
    """PAT boshqaruvi. Ochiq token FAQAT yaratilganda qaytariladi."""

    serializer_class = ApiTokenSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "delete"]

    def get_queryset(self) -> QuerySet[ApiToken]:
        assert isinstance(self.request.user, User)
        return ApiToken.objects.filter(user=self.request.user).order_by("-created_at")

    @extend_schema(request=ApiTokenCreateSerializer, responses={201: ApiTokenSerializer})
    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        assert isinstance(request.user, User)
        user = request.user

        serializer = ApiTokenCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        active = ApiToken.objects.filter(user=user, revoked_at__isnull=True).count()
        if active >= ApiToken.MAX_ACTIVE_PER_USER:
            return Response(
                {
                    "error": {
                        "code": "token_limit",
                        "message": f"Maksimal {ApiToken.MAX_ACTIVE_PER_USER} ta faol token",
                        "details": {},
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        expires_at = data["expires_at"]
        if expires_at <= timezone.now():
            return Response(
                {
                    "error": {
                        "code": "invalid_expiry",
                        "message": "Muddat kelajakda bo'lishi kerak",
                        "details": {},
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if expires_at > timezone.now() + MAX_TOKEN_LIFETIME:
            return Response(
                {
                    "error": {
                        "code": "invalid_expiry",
                        "message": "Maksimal muddat — 1 yil",
                        "details": {},
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        token, raw = ApiToken.issue(user, data["name"], data["scopes"], expires_at)
        payload = ApiTokenSerializer(token).data
        # Ochiq token faqat SHU YERDA, bir marta.
        payload["token"] = raw
        return Response(payload, status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance: ApiToken) -> None:
        # O'chirmaymiz — bekor qilamiz. Audit izi saqlanadi.
        instance.revoked_at = timezone.now()
        instance.save(update_fields=["revoked_at"])
