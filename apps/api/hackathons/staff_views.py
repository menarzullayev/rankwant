"""Staff API: `staff/hackathons/` — hakaton CRUD, loyihalar ro'yxati, baholash.

Ommaviy `HackathonViewSet` da ham `score_entry` bor (IsAdminUser). Bu yerda
u takrorlanadi, chunki admin UI faqat `staff/…` yuzasi bilan gaplashadi va
ommaviy `submissions` muddatgacha begona loyihalarni yashiradi — xodimga
esa hammasi kerak. Ikkalasi ham `hackathons.services.score` ga tayanadi.
"""

from __future__ import annotations

from django.db.models import Count
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from core.models import User
from core.staff import StaffViewSet
from hackathons.models import Hackathon, HackathonSubmission
from hackathons.serializers import ScoreSerializer
from hackathons.services import HackathonError, score
from hackathons.staff_serializers import StaffHackathonSerializer, StaffSubmissionSerializer
from hackathons.views import _error


class StaffHackathonViewSet(StaffViewSet):
    serializer_class = StaffHackathonSerializer
    lookup_field = "slug"
    search_fields = ["slug", "title"]
    ordering_fields = ["start_at", "submission_deadline", "end_at", "created_at", "slug"]
    ordering = ["-start_at", "-pk"]

    def get_queryset(self):  # type: ignore[no-untyped-def]
        return Hackathon.objects.annotate(submission_count=Count("submissions", distinct=True))

    @extend_schema(responses={200: StaffSubmissionSerializer(many=True)})
    @action(detail=True, methods=["get"])
    def submissions(self, request: Request, slug: str | None = None) -> Response:
        """Muddatdan qat'i nazar BARCHA loyihalar — hakam baholashi uchun."""
        qs = (
            HackathonSubmission.objects.filter(hackathon=self.get_object())
            .select_related("user", "scored_by")
            .order_by("-score", "submitted_at")
        )
        return Response({"results": StaffSubmissionSerializer(qs, many=True).data})

    @extend_schema(request=ScoreSerializer, responses={200: StaffSubmissionSerializer})
    @action(detail=True, methods=["post"], url_path=r"submissions/(?P<entry_id>\d+)/score")
    def score_entry(
        self, request: Request, slug: str | None = None, entry_id: str | None = None
    ) -> Response:
        entry = get_object_or_404(HackathonSubmission, pk=entry_id, hackathon=self.get_object())
        serializer = ScoreSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assert isinstance(request.user, User)
        data = serializer.validated_data
        try:
            score(request.user, entry, data["score"], data.get("feedback", ""))
        except HackathonError as exc:
            return _error(exc)
        return Response(StaffSubmissionSerializer(entry).data)
