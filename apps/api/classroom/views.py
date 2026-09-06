from __future__ import annotations

from typing import Any

from django.db.models import Count, Q
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from classroom.models import Assignment, Classroom
from classroom.serializers import (
    AssignmentCreateSerializer,
    AssignmentSerializer,
    ClassroomCreateSerializer,
    ClassroomOwnerSerializer,
    ClassroomSerializer,
    JoinSerializer,
)
from classroom.services import ClassroomError, assignment_progress, join
from core.models import User
from problems.models import Problem


class ClassroomViewSet(viewsets.ModelViewSet[Classroom]):
    """PRD P2-2 — o'qituvchi sinfi."""

    permission_classes = [IsAuthenticated]
    lookup_field = "slug"
    pagination_class = None
    http_method_names = ["get", "post", "patch", "delete"]

    def get_queryset(self):  # type: ignore[no-untyped-def]
        assert isinstance(self.request.user, User)
        # Egasi bo'lgan yoki a'zo bo'lgan sinflar
        # Egasi bo'lgan YOKI a'zo bo'lgan sinflar
        return (
            Classroom.objects.filter(is_active=True)
            .filter(Q(owner=self.request.user) | Q(members__user=self.request.user))
            .annotate(member_count=Count("members", distinct=True))
            .select_related("owner")
            .distinct()
        )

    def get_serializer_class(self):  # type: ignore[no-untyped-def]
        if self.action == "create":
            return ClassroomCreateSerializer
        if self.action == "retrieve":
            return ClassroomOwnerSerializer
        return ClassroomSerializer

    def perform_create(self, serializer: Any) -> None:
        serializer.save(owner=self.request.user)

    @extend_schema(request=JoinSerializer, responses={201: ClassroomSerializer})
    @action(detail=False, methods=["post"])
    def join(self, request: Request) -> Response:
        serializer = JoinSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assert isinstance(request.user, User)
        try:
            member = join(request.user, serializer.validated_data["join_code"])
        except ClassroomError as exc:
            return Response(
                {"error": {"code": "join_failed", "message": str(exc), "details": {}}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(ClassroomSerializer(member.classroom).data, status=status.HTTP_201_CREATED)

    @extend_schema(responses={200: AssignmentSerializer(many=True)})
    @action(detail=True, methods=["get", "post"])
    def assignments(self, request: Request, slug: str | None = None) -> Response:
        classroom = self.get_object()

        if request.method == "GET":
            rows = classroom.assignments.prefetch_related("problems")
            return Response(AssignmentSerializer(rows, many=True).data)

        if classroom.owner_id != request.user.pk:
            return Response(
                {
                    "error": {
                        "code": "not_owner",
                        "message": "Faqat sinf egasi vazifa bera oladi",
                        "details": {},
                    }
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = AssignmentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        assignment = Assignment.objects.create(
            classroom=classroom,
            title=data["title"],
            description=data.get("description", ""),
            due_at=data.get("due_at"),
        )
        assignment.problems.set(Problem.objects.filter(slug__in=data["problems"]))
        return Response(AssignmentSerializer(assignment).data, status=status.HTTP_201_CREATED)

    @extend_schema(responses={200: None})
    @action(detail=True, methods=["get"], url_path=r"assignments/(?P<pk>\d+)/progress")
    def progress(
        self, request: Request, slug: str | None = None, pk: str | None = None
    ) -> Response:
        classroom = self.get_object()
        if classroom.owner_id != request.user.pk:
            return Response(
                {
                    "error": {
                        "code": "not_owner",
                        "message": "Faqat sinf egasi progressni ko'radi",
                        "details": {},
                    }
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        assignment = classroom.assignments.get(pk=int(pk or 0))
        return Response({"results": assignment_progress(assignment)})
