from __future__ import annotations

from typing import Any

from django.db.models import Avg, Count
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import User
from core.pagination import StandardPagination
from problems.filters import ProblemFilter
from problems.models import Favourite, Language, Problem, ProblemRating, Topic
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
    ordering_fields = ["difficulty", "solved_count", "attempt_count", "created_at"]
    ordering = ["difficulty"]

    def get_queryset(self):  # type: ignore[no-untyped-def]
        return (
            Problem.objects.filter(is_public=True)
            .prefetch_related("topics")
            .order_by("difficulty", "slug")
        )

    def get_serializer_context(self):  # type: ignore[no-untyped-def]
        context: dict[str, Any] = dict(super().get_serializer_context())
        user = self.request.user
        if user.is_authenticated:
            from ratings.models import UserSolvedProblem

            context["solved_slugs"] = set(
                UserSolvedProblem.objects.filter(user=user).values_list("problem__slug", flat=True)
            )
        return context

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
