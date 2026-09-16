"""Staff API: `staff/hackathons/` — hakaton CRUD, loyihalar ro'yxati, baholash.

Ommaviy `HackathonViewSet` da ham `score_entry` bor (IsAdminUser). Bu yerda
u takrorlanardi, chunki admin UI faqat `staff/…` yuzasi bilan gaplashadi va
ommaviy `submissions` muddatgacha begona loyihalarni yashiradi — xodimga
esa hammasi kerak. Endi baholash qadamlari `views.score_submission` da:
farqi faqat chiqish serializer'ida (`scored_by` kabi maydonlar shu yerda
ham chiqadi).
"""

from __future__ import annotations

from django.db.models import Count
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from core.staff import StaffViewSet
from hackathons.models import Hackathon, HackathonSubmission
from hackathons.serializers import ScoreSerializer
from hackathons.staff_serializers import StaffHackathonSerializer, StaffSubmissionSerializer
from hackathons.views import score_submission


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
        return score_submission(
            request,
            hackathon=self.get_object(),
            entry_id=entry_id,
            serializer_class=StaffSubmissionSerializer,
        )
