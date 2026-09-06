from __future__ import annotations

from django.db.models import Count
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from core.models import User
from hackathons.models import Hackathon, HackathonSubmission
from hackathons.serializers import (
    HackathonSerializer,
    ScoreSerializer,
    SubmissionSerializer,
    SubmitSerializer,
)
from hackathons.services import HackathonError, score, submit


def _error(exc: HackathonError) -> Response:
    return Response(
        {"error": {"code": exc.code, "message": exc.message, "details": {}}},
        status=status.HTTP_400_BAD_REQUEST,
    )


class HackathonViewSet(viewsets.ReadOnlyModelViewSet[Hackathon]):
    permission_classes = [AllowAny]
    serializer_class = HackathonSerializer
    lookup_field = "slug"

    def get_queryset(self):  # type: ignore[no-untyped-def]
        return (
            Hackathon.objects.filter(is_public=True)
            .annotate(submission_count=Count("submissions", distinct=True))
            .order_by("-start_at")
        )

    @extend_schema(request=SubmitSerializer, responses={201: SubmissionSerializer})
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def submit(self, request: Request, slug: str | None = None) -> Response:
        serializer = SubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assert isinstance(request.user, User)
        try:
            entry = submit(request.user, self.get_object(), **serializer.validated_data)
        except HackathonError as exc:
            return _error(exc)
        return Response(SubmissionSerializer(entry).data, status=status.HTTP_201_CREATED)

    @extend_schema(responses={200: SubmissionSerializer(many=True)})
    @action(detail=True, methods=["get"])
    def submissions(self, request: Request, slug: str | None = None) -> Response:
        """Muddatgacha faqat o'ziniki — boshqalar loyihasini ko'rib olish yo'q."""
        hackathon = self.get_object()
        qs = HackathonSubmission.objects.filter(hackathon=hackathon).select_related("user")
        if hackathon.accepts_submissions:
            qs = qs.filter(user=request.user) if request.user.is_authenticated else qs.none()
        return Response({"results": SubmissionSerializer(qs, many=True).data})

    @extend_schema(request=ScoreSerializer, responses={200: SubmissionSerializer})
    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAdminUser],
        url_path=r"submissions/(?P<entry_id>\d+)/score",
    )
    def score_entry(
        self, request: Request, slug: str | None = None, entry_id: str | None = None
    ) -> Response:
        entry = get_object_or_404(HackathonSubmission, pk=entry_id, hackathon=self.get_object())
        serializer = ScoreSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assert isinstance(request.user, User)
        try:
            data = serializer.validated_data
            score(request.user, entry, data["score"], data.get("feedback", ""))
        except HackathonError as exc:
            return _error(exc)
        return Response(SubmissionSerializer(entry).data)
