"""`/coaching/` — a student's coaches and a coach's students (ADR-0061 § 4)."""

from __future__ import annotations

from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from coaching import services
from coaching.models import CoachLink
from coaching.serializers import (
    AskSerializer,
    CoachLinkSerializer,
    CoachLinksSerializer,
    CoachStudentSerializer,
    ConsentSerializer,
    RecommendationSerializer,
    RecommendSerializer,
)
from coaching.services import CoachingError
from core.models import User


def _failed(exc: CoachingError) -> Response:
    return Response(
        {"error": {"code": exc.code, "message": str(exc), "details": {}}},
        status=status.HTTP_400_BAD_REQUEST,
    )


def _user(request: Request) -> User:
    assert isinstance(request.user, User)
    return request.user


class CoachingViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    #: Only so the schema knows the link id is an integer; every action
    #: filters by the reader itself.
    queryset = CoachLink.objects.none()
    lookup_value_regex = r"\d+"

    @extend_schema(
        summary="Murabbiylarim va menga kelgan so'rovlar", responses=CoachLinksSerializer
    )
    def list(self, request: Request) -> Response:
        user = _user(request)
        coaches = CoachLink.objects.filter(student=user, status__in=services.OPEN).select_related(
            "coach", "student"
        )
        requests = CoachLink.objects.filter(
            coach=user, status=CoachLink.Status.PENDING
        ).select_related("coach", "student")
        return Response(
            {
                "coaches": CoachLinkSerializer(coaches, many=True).data,
                "requests": CoachLinkSerializer(requests, many=True).data,
            }
        )

    @extend_schema(
        summary="Murabbiy bo'lishni so'rash",
        request=AskSerializer,
        responses={201: CoachLinkSerializer},
    )
    def create(self, request: Request) -> Response:
        body = AskSerializer(data=request.data)
        body.is_valid(raise_exception=True)
        try:
            link = services.ask(_user(request), body.validated_data["coach"])
        except CoachingError as exc:
            return _failed(exc)
        return Response(CoachLinkSerializer(link).data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Shu murabbiyga kodimni ko'rsatish",
        request=ConsentSerializer,
        responses=CoachLinkSerializer,
    )
    def partial_update(self, request: Request, pk: str | None = None) -> Response:
        body = ConsentSerializer(data=request.data)
        body.is_valid(raise_exception=True)
        try:
            link = services.set_consent(
                _user(request), int(pk or 0), body.validated_data["can_view_attempts"]
            )
        except CoachingError as exc:
            return _failed(exc)
        return Response(CoachLinkSerializer(link).data)

    def _answer(self, request: Request, pk: str | None, *, accept: bool) -> Response:
        try:
            link = services.answer(_user(request), int(pk or 0), accept=accept)
        except CoachingError as exc:
            return _failed(exc)
        return Response(CoachLinkSerializer(link).data)

    @extend_schema(summary="So'rovni qabul qilish", request=None, responses=CoachLinkSerializer)
    @action(detail=True, methods=["post"])
    def accept(self, request: Request, pk: str | None = None) -> Response:
        return self._answer(request, pk, accept=True)

    @extend_schema(summary="So'rovni rad etish", request=None, responses=CoachLinkSerializer)
    @action(detail=True, methods=["post"])
    def decline(self, request: Request, pk: str | None = None) -> Response:
        return self._answer(request, pk, accept=False)

    @extend_schema(summary="Bog'lanishni tugatish", request=None, responses=CoachLinkSerializer)
    @action(detail=True, methods=["post"])
    def end(self, request: Request, pk: str | None = None) -> Response:
        try:
            link = services.end(_user(request), int(pk or 0))
        except CoachingError as exc:
            return _failed(exc)
        return Response(CoachLinkSerializer(link).data)

    @extend_schema(
        summary="O'quvchiga masala tavsiya qilish",
        request=RecommendSerializer,
        responses={201: RecommendationSerializer},
    )
    @action(detail=True, methods=["post"])
    def recommend(self, request: Request, pk: str | None = None) -> Response:
        body = RecommendSerializer(data=request.data)
        body.is_valid(raise_exception=True)
        try:
            row = services.recommend(
                _user(request),
                int(pk or 0),
                body.validated_data["problem"],
                body.validated_data["note"],
            )
        except CoachingError as exc:
            return _failed(exc)
        data = {
            "id": row.pk,
            "coach": request.user.get_username(),
            "problem": row.problem.slug,
            "problem_title": row.problem.title,
            "note": row.note,
            "solved": False,
            "created_at": row.created_at,
        }
        return Response(RecommendationSerializer(data).data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Murabbiy paneli: o'quvchilarim", responses=CoachStudentSerializer(many=True)
    )
    @action(detail=False, methods=["get"])
    def students(self, request: Request) -> Response:
        return Response(
            CoachStudentSerializer(services.students_of(_user(request)), many=True).data
        )

    @extend_schema(
        summary="Murabbiylar tavsiya qilgan masalalar",
        responses=RecommendationSerializer(many=True),
    )
    @action(detail=False, methods=["get"])
    def recommendations(self, request: Request) -> Response:
        rows = services.recommendations_for(_user(request))
        return Response(RecommendationSerializer(rows, many=True).data)
