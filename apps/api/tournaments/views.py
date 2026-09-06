from __future__ import annotations

from django.db.models import Count
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from tournaments.models import Tournament, TournamentStanding
from tournaments.serializers import (
    TournamentDetailSerializer,
    TournamentSerializer,
    TournamentStandingSerializer,
)


class TournamentViewSet(viewsets.ReadOnlyModelViewSet[Tournament]):
    permission_classes = [AllowAny]
    lookup_field = "slug"

    def get_queryset(self):  # type: ignore[no-untyped-def]
        return (
            Tournament.objects.filter(is_public=True)
            .annotate(stage_count=Count("stages", distinct=True))
            .prefetch_related("stages__contest")
            .order_by("-start_at")
        )

    def get_serializer_class(self):  # type: ignore[no-untyped-def]
        return TournamentDetailSerializer if self.action == "retrieve" else TournamentSerializer

    @extend_schema(responses={200: TournamentStandingSerializer(many=True)})
    @action(detail=True, methods=["get"])
    def standings(self, request: Request, slug: str | None = None) -> Response:
        rows = (
            TournamentStanding.objects.filter(tournament=self.get_object())
            .select_related("user")
            .order_by("rank")[:500]
        )
        return Response({"results": TournamentStandingSerializer(rows, many=True).data})
