"""Staff (admin UI) — Arena raundlarini boshqarish. Ruxsat: faqat `is_staff`."""

from __future__ import annotations

from django.db.models import Count
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from arena.models import ArenaParticipation, ArenaRound
from arena.services import ArenaError, finalize
from arena.staff_serializers import (
    FinalizeResultSerializer,
    RescheduleSerializer,
    StaffArenaSerializer,
)
from arena.views import _error
from core.staff import StaffViewSet


class StaffArenaViewSet(StaffViewSet):
    """`questions` — tartiblangan savol id'lari; yozishda to'liq almashtiriladi."""

    queryset = ArenaRound.objects.annotate(
        question_count=Count("items", distinct=True),
        participant_count=Count("participants", distinct=True),
    )
    serializer_class = StaffArenaSerializer
    lookup_field = "slug"
    search_fields = ["slug", "title"]
    ordering_fields = ["start_at", "created_at", "slug", "seconds_per_question"]
    ordering = ["-start_at"]

    @extend_schema(request=RescheduleSerializer, responses={200: StaffArenaSerializer})
    @action(detail=True, methods=["post"])
    def reschedule(self, request: Request, slug: str | None = None) -> Response:
        """Yangi `start_at`; qayta o'tkazilgan raund uchun mukofot belgisi tozalanadi."""
        arena = self.get_object()
        serializer = RescheduleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        arena.start_at = serializer.validated_data["start_at"]
        arena.rewards_applied_at = None
        arena.save(update_fields=["start_at", "rewards_applied_at"])
        return Response(self.get_serializer(arena).data)

    @extend_schema(request=None, responses={200: StaffArenaSerializer})
    @action(detail=True, methods=["post"])
    def reset(self, request: Request, slug: str | None = None) -> Response:
        """Demo uchun: ishtirokchilar va javoblar o'chiriladi, mukofot belgisi tozalanadi."""
        arena = self.get_object()
        ArenaParticipation.objects.filter(round=arena).delete()
        arena.rewards_applied_at = None
        arena.save(update_fields=["rewards_applied_at"])
        # annotate'lar eskirgan — qayta o'qiymiz
        return Response(self.get_serializer(self.get_object()).data)

    @extend_schema(request=None, responses={200: FinalizeResultSerializer})
    @action(detail=True, methods=["post"])
    def finalize(self, request: Request, slug: str | None = None) -> Response:
        arena = self.get_object()
        if not arena.is_finished:
            return _error(ArenaError("not_finished", "Raund hali tugamagan"))
        if arena.rewards_applied_at is not None:
            return _error(ArenaError("already_finalized", "Mukofotlar allaqachon berilgan"))
        awarded = finalize(arena)
        return Response(
            {"awarded": awarded, "rewards_applied_at": arena.rewards_applied_at},
            status=status.HTTP_200_OK,
        )
