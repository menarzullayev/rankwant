"""Staff (admin UI) — chempionat CRUD + yig'ma jadvalni qayta hisoblash."""

from __future__ import annotations

from typing import ClassVar

from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from core.staff import StaffViewSet
from tournaments import services
from tournaments.models import Tournament
from tournaments.staff_serializers import StaffTournamentSerializer


class StaffTournamentViewSet(StaffViewSet):
    queryset = Tournament.objects.prefetch_related("stages__contest")
    serializer_class = StaffTournamentSerializer
    lookup_field = "slug"
    search_fields: ClassVar[list[str]] = ["slug", "title"]
    ordering_fields: ClassVar[list[str]] = ["pk", "slug", "title", "start_at", "end_at"]
    ordering: ClassVar[list[str]] = ["-start_at"]

    @extend_schema(request=None, responses={200: {"type": "object"}})
    @action(detail=True, methods=["post"])
    def rebuild(self, request: Request, slug: str | None = None) -> Response:
        tournament: Tournament = self.get_object()
        return Response({"participants": services.rebuild(tournament)})
