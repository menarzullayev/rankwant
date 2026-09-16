"""Staff (admin UI) — musobaqalar: CRUD, masalalar ro'yxati, standings/yakunlash."""

from __future__ import annotations

from typing import ClassVar

from django.db import transaction
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from contests.models import Contest, ContestProblem
from contests.services import finalize_contest, rebuild_standings
from contests.staff_serializers import (
    StaffContestProblemListSerializer,
    StaffContestProblemSerializer,
    StaffContestSerializer,
)
from core.openapi_docs import crud_summaries
from core.staff import StaffViewSet


@crud_summaries(
    one="musobaqa",
    many="musobaqalar",
    extra={"rebuild_standings": "Turnik jadvalini qayta hisoblash"},
)
class StaffContestViewSet(StaffViewSet):
    queryset = Contest.objects.prefetch_related("problems__problem").select_related("mirror_of")
    serializer_class = StaffContestSerializer
    lookup_field = "slug"
    search_fields: ClassVar[list[str]] = ["slug", "title"]
    ordering_fields: ClassVar[list[str]] = ["pk", "slug", "start_at", "end_at", "created_at"]
    # `-pk` — tiebreaker: bir xil `start_at` li musobaqalar tartibi aks holda
    # SQL ixtiyoriga qoladi va sahifalash beqaror bo'ladi.
    ordering: ClassVar[list[str]] = ["-start_at", "-pk"]

    @extend_schema(
        request=StaffContestProblemListSerializer,
        responses={200: StaffContestProblemSerializer(many=True)},
    )
    @action(detail=True, methods=["get", "put", "post"])
    def problems(self, request: Request, slug: str | None = None) -> Response:
        """Masalalar ro'yxati.

        GET — joriy ro'yxat. PUT/POST — `[{problem, index_letter, points?}]`
        yoki `{"problems": [...]}` ko'rinishida; mavjud ContestProblem
        qatorlari TO'LIQ almashtiriladi (qisman yangilash yo'q).
        """
        contest = self.get_object()
        if request.method != "GET":
            data = request.data if isinstance(request.data, dict) else {"problems": request.data}
            serializer = StaffContestProblemListSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            with transaction.atomic():
                ContestProblem.objects.filter(contest=contest).delete()
                ContestProblem.objects.bulk_create(
                    [
                        ContestProblem(
                            contest=contest,
                            problem=row["problem"],
                            index_letter=row["index_letter"],
                            points=row.get("points", 100),
                        )
                        for row in serializer.validated_data["problems"]
                    ]
                )
        rows = ContestProblem.objects.filter(contest=contest).select_related("problem")
        return Response(StaffContestProblemSerializer(rows, many=True).data)

    @extend_schema(request=None, responses={200: {"type": "object"}})
    @action(detail=True, methods=["post"], url_path="rebuild-standings")
    def rebuild_standings(self, request: Request, slug: str | None = None) -> Response:
        contest = self.get_object()
        return Response({"rows": rebuild_standings(contest)})

    @extend_schema(request=None, responses={200: {"type": "object"}})
    @action(detail=True, methods=["post"])
    def finalize(self, request: Request, slug: str | None = None) -> Response:
        """Standings + reyting. Tugamagan yoki allaqachon yakunlangan → affected 0."""
        contest = self.get_object()
        affected = finalize_contest(contest)
        contest.refresh_from_db(fields=["ratings_applied_at"])
        return Response(
            {"affected": affected, "ratings_applied_at": contest.ratings_applied_at},
            status=status.HTTP_200_OK,
        )
