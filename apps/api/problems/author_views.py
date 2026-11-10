"""Muallif yuzasi (ADR-0025, qaror 23) — `problems/mine/`.

Masala muallifi `is_staff` BO'LMAGAN foydalanuvchi bo'lishi mumkin: o'z
DRAFT masalasini yaratadi (`is_public=False`), bayonot va editorialni
tahrirlaydi. Nashr — staff-ops (`staff/problems/` yuzasida). Muallif o'z
draftining testlarini ham boshqaradi — bu xodim yuzasidagi `tests`
amalining obyekt tekshiruvi orqali (`problems/staff_views.py`).

The web page for this surface is `/studio/problems` (2026-11-10). Any
signed-in user may write drafts — the API allowed it from the start — so
two guards were added with it: at most `MAX_DRAFTS` unpublished problems
per author, and `review` refuses a draft that could not be published
anyway (no statement, no sample, no hidden test).

Yozish PAT bilan `submit` scope'ida ishlaydi (`CanSubmit`) — ADR-0008.
"""

from __future__ import annotations

from typing import Any

from django.db.models import Count, Q
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import APIException
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from core.models import User
from core.openapi_docs import crud_summaries
from core.permissions import STAFF_GROUP_OPS, CanSubmit
from problems.models import Problem
from problems.serializers import MineProblemSerializer

#: Unpublished problems one author may hold. Measured 2026-11-10: nobody
#: had authored a problem yet (0 rows in `Problem.authors`), so the number
#: is a guard against a flood, not a fit to existing use. Staff are exempt:
#: they work in the admin panel and import in bulk.
MAX_DRAFTS = 20


class DraftLimit(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "draft_limit"
    default_detail = f"At most {MAX_DRAFTS} unpublished problems per author"


class ReviewNotReady(APIException):
    """The draft lacks something publishing would refuse anyway.

    `details.missing` lists stable codes, so the page can say which.
    """

    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "review_not_ready"
    default_detail = "The draft is not ready for review"


class AlreadyPublic(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "already_public"
    default_detail = "A published problem is not reviewed again here"


def review_gaps(problem: Problem) -> list[str]:
    """What stops this draft from going to review — empty when nothing.

    The same three things the publish gate checks first: a statement, a
    sample (the problem page shows it) and a hidden test (publishing
    without one is refused unconditionally, `staff_serializers`).
    """
    gaps: list[str] = []
    if not problem.statement.strip():
        gaps.append("statement")
    counts = problem.tests.aggregate(
        samples=Count("pk", filter=Q(is_sample=True)),
        hidden=Count("pk", filter=Q(is_sample=False)),
    )
    if not counts["samples"]:
        gaps.append("sample_test")
    if not counts["hidden"]:
        gaps.append("hidden_test")
    return gaps


def staff_reviewers() -> Any:
    """Who is told about a review request: active staff-ops and superusers."""
    return (
        User.objects.filter(is_active=True, is_staff=True)
        .filter(Q(is_superuser=True) | Q(groups__name=STAFF_GROUP_OPS))
        .distinct()
    )


@crud_summaries(
    one="draft masala",
    many="draft masalalar",
    extra={"review": "Qoralamani xodim ko'rigiga yuborish"},
)
class MineProblemViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet[Problem],
):
    serializer_class = MineProblemSerializer
    permission_classes = [IsAuthenticated, CanSubmit]
    lookup_field = "slug"

    def get_queryset(self) -> Any:
        if getattr(self, "swagger_fake_view", False):
            return Problem.objects.none()
        assert self.request.user.is_authenticated
        return self.request.user.authored_problems.annotate(
            sample_count=Count("tests", filter=Q(tests__is_sample=True), distinct=True),
            hidden_count=Count("tests", filter=Q(tests__is_sample=False), distinct=True),
        ).order_by("-pk")

    def perform_create(self, serializer: Any) -> None:
        # Draft: nashr staff-ops qarori.
        user = self.request.user
        assert isinstance(user, User)
        drafts = user.authored_problems.filter(is_public=False).count()
        if not user.is_staff and drafts >= MAX_DRAFTS:
            raise DraftLimit()
        problem = serializer.save(is_public=False)
        problem.authors.add(user)

    def perform_update(self, serializer: Any) -> None:
        # A published problem is staff-ops' (ADR-0025): a legacy one without a
        # frozen revision shows its working copy, so an author's edit would go
        # live with no review.
        if serializer.instance.is_public:
            self.permission_denied(
                self.request, message="A published problem is edited by staff-ops"
            )
        serializer.save()

    def perform_destroy(self, instance: Problem) -> None:
        if instance.is_public:
            self.permission_denied(
                self.request,
                message="Nashr qilingan masala o'chirilmaydi — staff-ops bilan arxivlanadi",
            )
        super().perform_destroy(instance)

    @extend_schema(request=None, responses={200: MineProblemSerializer})
    @action(detail=True, methods=["post"])
    def review(self, request: Request, slug: str | None = None) -> Response:
        """Ask staff-ops to review the draft.

        Asking twice is harmless: the first time is kept and staff are told
        once — a second click must not ring every reviewer again.
        """
        problem = self.get_object()
        if problem.is_public:
            raise AlreadyPublic()
        gaps = review_gaps(problem)
        if gaps:
            raise ReviewNotReady(detail={"missing": gaps})
        if problem.review_requested_at is None:
            problem.review_requested_at = timezone.now()
            problem.save(update_fields=["review_requested_at", "updated_at"])
            self._tell_reviewers(problem)
        return Response(self.get_serializer(self.get_queryset().get(pk=problem.pk)).data)

    def _tell_reviewers(self, problem: Problem) -> None:
        # Through the service only: `notifications.models` is another app's
        # model (`check_architecture.py`). "system" is `Notification.Kind.SYSTEM`;
        # `test_studio_problems` pins it.
        from notifications.services import notify_many

        author = self.request.user
        assert isinstance(author, User)
        notify_many(
            staff_reviewers(),
            "system",
            code="problem_review_requested",
            params={"problem": problem.title, "user": author.username},
            ref_type="problem_review",
            ref_id=problem.slug,
        )
