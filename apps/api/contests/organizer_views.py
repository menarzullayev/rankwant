"""Organizator yuzasi (ADR-0025, qaror 23) — `contests/mine/`.

Musobaqa organizatori `is_staff` BO'LMAGAN foydalanuvchi bo'lishi mumkin:
o'z kontestini draft qilib yaratadi (`is_public=False`), tahrirlaydi,
qatnashchilar ro'yxatini ko'radi. Nashr (`is_public=True`) — staff-ops,
`staff/contests/` yuzasida. Bu foydalanuvchining BARCHA kontestlari
`organized_contests` orqali keladi, ya'ni obyektga oid huquq — qo'shimcha
rol maydoni shart emas.

The web page is `/studio/contests` (2026-11-10). Measured before it: the
`participants` action answered 500 (its signature took `pk`, the lookup is
`slug`), an end before the start was accepted, and only staff-ops could
attach problems. Now the organizer attaches problems of their OWN drafts —
an unpublished problem is outside the archive, which is what a contest
problem must be until the contest ends (ADR-0055) — while the contest is a
draft; once staff-ops publish it, its problem set is theirs. A draft cap
(`MAX_DRAFTS`) guards the open surface.

PAT bilan yozish `contest:manage` scope'ida ishlaydi (`CanManageContest`) —
ADR-0008 naqshi: sessiya uchun scope cheklovi yo'q.
"""

from __future__ import annotations

import logging
from typing import Any

from django.db import transaction
from django.db.models import Count
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import APIException
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from contests.insiders import notify_new_testers
from contests.models import Contest, ContestProblem
from contests.staff_serializers import crew_field
from core.models import User
from core.openapi_docs import crud_summaries
from core.permissions import CanManageContest
from problems.readiness import GRADED_READY, enforcing, graded_gate_error

log = logging.getLogger(__name__)

#: Unpublished contests one organizer may hold. Measured 2026-11-10: nobody
#: had organized a contest yet, so this guards against a flood rather than
#: fitting existing use. Staff are exempt.
MAX_DRAFTS = 5


class DraftLimit(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "contest_draft_limit"
    default_detail = f"At most {MAX_DRAFTS} unpublished contests per organizer"


class ContestLocked(APIException):
    """A published contest's problem set belongs to staff-ops."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "contest_locked"
    default_detail = "Staff-ops manage the problems of a published contest"


class OrganizerContestProblemSerializer(serializers.ModelSerializer[ContestProblem]):
    """One problem of the organizer's contest."""

    # The model through the relation, not `problems.models`: another app's
    # model is imported only through an allowlisted path (`check_architecture`).
    problem = serializers.SlugRelatedField[Any](
        slug_field="slug",
        queryset=ContestProblem._meta.get_field("problem").related_model._default_manager.all(),
    )
    title = serializers.CharField(source="problem.title", read_only=True)

    class Meta:
        model = ContestProblem
        fields = ["problem", "index_letter", "points", "title"]
        extra_kwargs = {"points": {"required": False}}


class OrganizerContestProblemListSerializer(serializers.Serializer[Any]):
    """The whole problem list, replaced at once — like the staff surface."""

    problems = OrganizerContestProblemSerializer(many=True)

    def validate_problems(self, value: list[dict[str, Any]]) -> list[dict[str, Any]]:
        letters = [row["index_letter"] for row in value]
        if len(letters) != len(set(letters)):
            raise serializers.ValidationError("Index letters must be unique")
        problems = [row["problem"].pk for row in value]
        if len(problems) != len(set(problems)):
            raise serializers.ValidationError("A problem cannot be added twice")
        user = self.context["request"].user
        own = set(user.authored_problems.filter(is_public=False).values_list("pk", flat=True))
        for row in value:
            if row["problem"].pk not in own:
                # Not "not found": the slug may exist, it is just not theirs.
                raise serializers.ValidationError(
                    f"{row['problem'].slug}: only your own unpublished problems"
                )
            # D8-F (ADR-0037) — the same gate as `staff/contests/.../problems/`,
            # so this surface is no way around it once it is enforced.
            if row["problem"].readiness != GRADED_READY:
                message = graded_gate_error(row["problem"])
                if not enforcing():
                    log.warning("readiness gate NOT enforced: %s", message)
                    continue
                raise serializers.ValidationError(message)
        return value


class OrganizerContestSerializer(serializers.ModelSerializer[Contest]):
    """Organizator ko'radigan maydonlar.

    `is_public` va `is_rated` — faqat O'QISH: nashr va reyting qo'llash
    staff-ops qarori (masala sifati va reyting tozaligi — ADR-0006/0013).
    The organizer picks the testers (ADR-0055, part 2); the jury is a
    staff decision.
    """

    testers = crew_field()
    problems = OrganizerContestProblemSerializer(many=True, read_only=True)
    participant_count = serializers.SerializerMethodField()

    def get_participant_count(self, contest: Contest) -> int:
        # The list annotates it (one query); a single create/update does not.
        cached: int | None = getattr(contest, "participant_total", None)
        return cached if cached is not None else int(contest.registrations.count())

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """An end before the start used to be accepted (201, measured)."""
        start_at = attrs.get("start_at", getattr(self.instance, "start_at", None))
        end_at = attrs.get("end_at", getattr(self.instance, "end_at", None))
        if start_at and end_at and end_at <= start_at:
            raise serializers.ValidationError({"end_at": "The end time must be after the start"})
        return attrs

    def validate_testers(self, value: list[User]) -> list[User]:
        """Once the contest has started the testers are fixed.

        A tester is unrated: adding one mid-contest would take a
        participant's official place away retroactively. Staff-ops can
        still correct it.
        """
        contest = self.instance
        if contest is not None and timezone.now() >= contest.start_at:
            if {u.pk for u in value} != set(contest.testers.values_list("pk", flat=True)):
                raise serializers.ValidationError(
                    "The testers cannot change after the contest has started"
                )
        return value

    def create(self, validated_data: dict[str, Any]) -> Contest:
        contest = super().create(validated_data)
        notify_new_testers(contest, set())
        return contest

    def update(self, instance: Contest, validated_data: dict[str, Any]) -> Contest:
        before = set(instance.testers.values_list("pk", flat=True))
        contest = super().update(instance, validated_data)
        notify_new_testers(contest, before)
        return contest

    class Meta:
        model = Contest
        fields = [
            "slug",
            "title",
            "description",
            "start_at",
            "end_at",
            "freeze_minutes",
            "scoring_type",
            "is_public",
            "is_rated",
            "testers",
            "problems",
            "participant_count",
        ]
        read_only_fields = ["is_public", "is_rated"]


class OrganizerParticipantSerializer(serializers.Serializer[Any]):
    username = serializers.CharField(source="user.username")
    display_name = serializers.CharField(source="user.display_name")
    registered_at = serializers.DateTimeField()


@crud_summaries(
    one="kontest",
    many="kontestlar",
    extra={
        "participants": "Ro'yxatdan o'tganlar",
        "contest_problems": "Musobaqa masalalari (faqat o'z qoralamalari)",
    },
)
class OrganizerContestViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet[Contest],
):
    """O'z kontestlari — draft yaratish, tahrirlash, o'chirish.

    Yo'q qilish faqat nashr qilinmagan (draft) kontestga ruxsat: reyting
    tarixi va sertifikatlar saqlanishi shart.
    """

    serializer_class = OrganizerContestSerializer
    permission_classes = [IsAuthenticated, CanManageContest]
    lookup_field = "slug"

    def get_queryset(self) -> Any:
        # Sxema generatsiyasida `request.user` — AnonymousUser, ya'ni
        # `organized_contests` yo'q va drf-spectacular modelni topa
        # olmaydi (o'lchandi 2026-09-24). Modelning o'zidan bo'sh
        # queryset qaytaramiz — u tur ma'lumotini beradi.
        if getattr(self, "swagger_fake_view", False):
            return Contest.objects.none()
        assert self.request.user.is_authenticated
        return (
            self.request.user.organized_contests.annotate(
                participant_total=Count("registrations", distinct=True)
            )
            .prefetch_related("problems__problem", "testers")
            .order_by("-start_at", "-pk")
        )

    def perform_create(self, serializer: Any) -> None:
        # Draft: nashr va reyting staff-ops qarori.
        user = self.request.user
        assert isinstance(user, User)
        drafts = user.organized_contests.filter(is_public=False).count()
        if not user.is_staff and drafts >= MAX_DRAFTS:
            raise DraftLimit()
        contest = serializer.save(is_public=False, is_rated=False)
        contest.organizers.add(user)

    def perform_destroy(self, instance: Any) -> None:
        if instance.is_public:
            self.permission_denied(
                self.request,
                message="Nashr qilingan kontest o'chirilmaydi — staff-ops bilan muzlatiladi",
            )
        super().perform_destroy(instance)

    @extend_schema(responses={200: OrganizerParticipantSerializer(many=True)})
    @action(detail=True, methods=["get"])
    def participants(self, request: Request, slug: str | None = None) -> Response:
        # `slug`, not `pk`: the viewset looks contests up by slug, and DRF
        # passes the lookup as a keyword — with `pk` every call was a 500.
        contest = self.get_object()
        rows = contest.registrations.select_related("user").order_by("registered_at")
        return Response(OrganizerParticipantSerializer(rows, many=True).data)

    @extend_schema(
        request=OrganizerContestProblemListSerializer,
        responses={200: OrganizerContestProblemSerializer(many=True)},
    )
    @action(detail=True, methods=["get", "put"], url_path="problems")
    def contest_problems(self, request: Request, slug: str | None = None) -> Response:
        """The contest's problems; PUT replaces the whole list.

        Only while the contest is a draft, and only the organizer's own
        unpublished problems (`OrganizerContestProblemListSerializer`).
        """
        contest = self.get_object()
        if request.method == "PUT":
            if contest.is_public:
                raise ContestLocked()
            serializer = OrganizerContestProblemListSerializer(
                data=request.data, context={"request": request}
            )
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
        return Response(OrganizerContestProblemSerializer(rows, many=True).data)
