from __future__ import annotations

from collections import Counter
from typing import Any

from django.db.models import Avg, Count, F, Max, Q
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import User
from core.pagination import StandardPagination
from judging.verdicts import Verdict
from problems.filters import ProblemFilter
from problems.models import (
    DIFFICULTY_LEVELS,
    Favourite,
    Language,
    Problem,
    ProblemRating,
    Topic,
    difficulty_level,
)
from problems.recommend import recommend, target_difficulty
from problems.serializers import (
    LanguageSerializer,
    ProblemDetailSerializer,
    ProblemListSerializer,
    RateProblemSerializer,
    TopicSerializer,
)


class ProblemViewSet(viewsets.ReadOnlyModelViewSet[Problem]):
    """Ommaviy masala arxivi.

    Yozish Django admin orqali (PRD P0-2) — API faqat o'qish uchun.
    """

    permission_classes = [AllowAny]
    lookup_field = "slug"
    filterset_class = ProblemFilter
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["title", "slug"]
    ordering_fields = [
        "difficulty",
        "solved_count",
        "attempt_count",
        "view_count",
        "created_at",
    ]
    ordering = ["difficulty"]

    def get_queryset(self):  # type: ignore[no-untyped-def]
        # Baho ro'yxatda ham ko'rinadi — har qatorga alohida so'rov
        # bo'lmasligi uchun annotatsiya.
        return (
            Problem.objects.filter(is_public=True)
            .prefetch_related("topics")
            .annotate(
                rating_avg=Avg("ratings__score"),
                rating_count=Count("ratings", distinct=True),
            )
            .order_by("difficulty", "slug")
        )

    def get_serializer_context(self):  # type: ignore[no-untyped-def]
        context: dict[str, Any] = dict(super().get_serializer_context())
        user = self.request.user
        if not user.is_authenticated:
            return context

        from judging.models import Attempt
        from problems.models import Favourite
        from ratings.models import UserSolvedProblem

        # Uchalasi ham foydalanuvchi bo'yicha bitta so'rov — qator soniga
        # bog'liq emas.
        context["solved_slugs"] = set(
            UserSolvedProblem.objects.filter(user=user).values_list("problem__slug", flat=True)
        )
        context["favourite_ids"] = set(
            Favourite.objects.filter(user=user).values_list("problem_id", flat=True)
        )
        # Oxirgi urinish verdikti — «urindim, WA oldim» signali. Ikkita
        # so'rov, ikkalasi ham urinilgan masalalar soni bilan chegaralangan
        # (`DISTINCT ON` Postgres'ga bog'lab qo'yardi, testlar SQLite'da).
        last_ids = dict(
            Attempt.objects.filter(user=user).values_list("problem_id").annotate(last=Max("pk"))
        )
        verdicts = dict(
            Attempt.objects.filter(pk__in=last_ids.values()).values_list("pk", "verdict")
        )
        context["my_verdicts"] = {
            problem_id: verdicts.get(attempt_id) for problem_id, attempt_id in last_ids.items()
        }
        return context

    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        response = super().retrieve(request, *args, **kwargs)
        # Bitta arzon UPDATE, o'qishdan keyin — sanoq xato bo'lsa ham
        # sahifa ochilishi buzilmasin.
        Problem.objects.filter(slug=kwargs.get("slug")).update(view_count=F("view_count") + 1)
        return response

    def get_serializer_class(self):  # type: ignore[no-untyped-def]
        return ProblemDetailSerializer if self.action == "retrieve" else ProblemListSerializer

    @extend_schema(request=None, responses={200: {"type": "object"}})
    @action(detail=True, methods=["post", "delete"], permission_classes=[IsAuthenticated])
    def favourite(self, request: Request, slug: str | None = None) -> Response:
        problem = self.get_object()
        assert isinstance(request.user, User)
        if request.method == "DELETE":
            Favourite.objects.filter(user=request.user, problem=problem).delete()
            return Response({"is_favourite": False})
        Favourite.objects.get_or_create(user=request.user, problem=problem)
        return Response({"is_favourite": True})

    @extend_schema(request=RateProblemSerializer, responses={200: {"type": "object"}})
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated], url_path="rate")
    def rate(self, request: Request, slug: str | None = None) -> Response:
        problem = self.get_object()
        serializer = RateProblemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assert isinstance(request.user, User)
        ProblemRating.objects.update_or_create(
            user=request.user,
            problem=problem,
            defaults={"score": serializer.validated_data["score"]},
        )
        stats = problem.ratings.aggregate(average=Avg("score"), count=Count("pk"))
        return Response(
            {
                "average": round(stats["average"], 1) if stats["average"] else None,
                "count": stats["count"],
                "my_rating": serializer.validated_data["score"],
            }
        )


class RecommendationView(APIView):
    """PRD P1-2 — darajangizga mos, yechmagan masalalaringiz."""

    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: ProblemListSerializer(many=True)})
    def get(self, request: Request) -> Response:
        assert isinstance(request.user, User)
        limit = min(int(request.query_params.get("limit", 10)), 50)
        problems = recommend(request.user, limit=limit)
        return Response(
            {
                "target_difficulty": target_difficulty(request.user),
                "results": ProblemListSerializer(problems, many=True).data,
            }
        )


class ProblemStatsView(APIView):
    """Masala statistikasi — verdikt/til taqsimoti va yechganlar.

    Ochiq: raqamlar hech kimning manbasini oshkor qilmaydi.
    """

    permission_classes = [AllowAny]
    #: Yechganlar ro'yxati cheklanadi — ommabop masalada minglab bo'lishi
    #: mumkin, sahifada esa bir nechtasi kifoya.
    SOLVER_LIMIT = 50

    @extend_schema(responses={200: OpenApiResponse(description="Masala statistikasi")})
    def get(self, request: Request, slug: str) -> Response:
        from judging.models import Attempt

        problem = get_object_or_404(Problem, slug=slug, is_public=True)
        attempts = Attempt.objects.filter(problem=problem)

        verdicts = [
            {"verdict": row["verdict"], "count": row["n"]}
            for row in attempts.values("verdict").annotate(n=Count("pk")).order_by("-n")
        ]
        languages = [
            {"language": row["language__code"], "count": row["n"], "solved": row["ac"]}
            for row in attempts.values("language__code")
            .annotate(n=Count("pk"), ac=Count("pk", filter=Q(verdict=Verdict.AC)))
            .order_by("-n")
        ]

        # Har foydalanuvchining BIRINCHI AC si. `DISTINCT ON` Postgres'ga
        # bog'lab qo'yardi (testlar SQLite'da), shuning uchun eng erta
        # AC'lar id bo'yicha olinib, Python'da bir marta filtrlanadi.
        seen: set[int] = set()
        solvers = []
        for attempt in (
            attempts.filter(verdict=Verdict.AC)
            .select_related("user", "language")
            .order_by("pk")[: self.SOLVER_LIMIT * 4]
        ):
            if attempt.user_id in seen:
                continue
            seen.add(attempt.user_id)
            solvers.append(
                {
                    "username": attempt.user.username,
                    "language": attempt.language.code,
                    "time_ms": attempt.time_ms,
                    "memory_kb": attempt.memory_kb,
                    "created_at": attempt.created_at,
                }
            )
            if len(solvers) >= self.SOLVER_LIMIT:
                break

        return Response(
            {
                "total": attempts.count(),
                "verdicts": verdicts,
                "languages": languages,
                "solvers": solvers,
            }
        )


class ProgressView(APIView):
    """Daraja bo'yicha yechilganlar — arxiv yon panelidagi progress bloki.

    Mehmonda ham ochiladi: o'shanda faqat jami masalalar ko'rinadi va
    `solved` nol bo'ladi, ya'ni blok arxiv hajmini ko'rsatuvchi kartaga
    aylanadi.
    """

    permission_classes = [AllowAny]

    @extend_schema(responses={200: OpenApiResponse(description="Daraja bo'yicha progress")})
    def get(self, request: Request) -> Response:
        totals: Counter[str] = Counter()
        for value in Problem.objects.filter(is_public=True).values_list("difficulty", flat=True):
            totals[difficulty_level(value)[0]] += 1

        solved: Counter[str] = Counter()
        if request.user.is_authenticated:
            from ratings.models import UserSolvedProblem

            for value in UserSolvedProblem.objects.filter(
                user=request.user, problem__is_public=True
            ).values_list("problem__difficulty", flat=True):
                solved[difficulty_level(value)[0]] += 1

        levels = [
            {"code": code, "label": label, "total": totals[code], "solved": solved[code]}
            for _, code, label in DIFFICULTY_LEVELS
        ]
        return Response(
            {
                "levels": levels,
                "total": sum(totals.values()),
                "solved": sum(solved.values()),
            }
        )


class TopicViewSet(viewsets.ReadOnlyModelViewSet[Topic]):
    permission_classes = [AllowAny]
    serializer_class = TopicSerializer
    lookup_field = "slug"
    queryset = Topic.objects.all().order_by("slug")


class LanguageViewSet(viewsets.ReadOnlyModelViewSet[Language]):
    permission_classes = [AllowAny]
    serializer_class = LanguageSerializer
    lookup_field = "code"
    queryset = Language.objects.filter(is_active=True).order_by("name")
