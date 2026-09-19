"""Organizator yuzasi (ADR-0025, qaror 23) — `contests/mine/`.

Musobaqa organizatori `is_staff` BO'LMAGAN foydalanuvchi bo'lishi mumkin:
o'z kontestini draft qilib yaratadi (`is_public=False`), tahrirlaydi,
qatnashchilar ro'yxatini ko'radi. Nashr (`is_public=True`) — staff-ops,
`staff/contests/` yuzasida. Bu foydalanuvchining BARCHA kontestlari
`organized_contests` orqali keladi, ya'ni obyektga oid huquq — qo'shimcha
rol maydoni shart emas.

PAT bilan yozish `contest:manage` scope'ida ishlaydi (`CanManageContest`) —
ADR-0008 naqshi: sessiya uchun scope cheklovi yo'q.
"""

from __future__ import annotations

from typing import Any

from drf_spectacular.utils import extend_schema
from rest_framework import mixins, serializers, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from contests.models import Contest
from core.models import User
from core.openapi_docs import crud_summaries
from core.permissions import CanManageContest


class OrganizerContestSerializer(serializers.ModelSerializer[Contest]):
    """Organizator ko'radigan maydonlar.

    `is_public` va `is_rated` — faqat O'QISH: nashr va reyting qo'llash
    staff-ops qarori (masala sifati va reyting tozaligi — ADR-0006/0013).
    """

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
        ]
        read_only_fields = ["is_public", "is_rated"]


class OrganizerParticipantSerializer(serializers.Serializer[Any]):
    username = serializers.CharField(source="user.username")
    display_name = serializers.CharField(source="user.display_name")
    registered_at = serializers.DateTimeField()


@crud_summaries(one="kontest", many="kontestlar")
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
        assert self.request.user.is_authenticated
        return (
            self.request.user.organized_contests.all()
            .prefetch_related("problems__problem")
            .order_by("-start_at", "-pk")
        )

    def perform_create(self, serializer: Any) -> None:
        # Draft: nashr va reyting staff-ops qarori.
        user = self.request.user
        assert isinstance(user, User)
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
    def participants(self, request: Request, pk: str | None = None) -> Response:
        contest = self.get_object()
        rows = contest.registrations.select_related("user").order_by("registered_at")
        return Response(OrganizerParticipantSerializer(rows, many=True).data)
