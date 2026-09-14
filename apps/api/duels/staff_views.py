"""Staff API: duel nazorati — faqat ko'rish, bekor qilish, yakunlash."""

from __future__ import annotations

from typing import ClassVar

from drf_spectacular.utils import extend_schema
from rest_framework import exceptions
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from core.staff import StaffViewSet
from duels.models import Duel
from duels.services import DuelError, staff_cancel, staff_finalize
from duels.staff_serializers import StaffDuelFinalizeSerializer, StaffDuelSerializer
from duels.views import _error


class StaffDuelViewSet(StaffViewSet):
    """`staff/duels/` — barcha holatdagi duellar.

    Yaratish/tahrirlash/o'chirish yo'q: duel foydalanuvchilar o'rtasidagi
    kelishuv, xodim faqat kuzatadi va zarurat bo'lsa to'xtatadi.
    """

    serializer_class = StaffDuelSerializer
    lookup_field = "slug"
    http_method_names = ["get", "post", "head", "options"]
    search_fields: ClassVar[list[str]] = ["title", "challenger__username", "opponent__username"]
    ordering_fields: ClassVar[list[str]] = ["created_at", "start_at", "status"]
    # `-created_at` YAKKA o'zi yetarli emas: ikkita duel bir mikrosekundda
    # yaratilsa (testda `_open()` ketma-ket ishlaydi, `auto_now_add` esa
    # soat aniqligida yozadi) tartib SQLite/Postgres ixtiyoriga qoladi va
    # sahifalash beqaror bo'ladi. `-pk` — yakuniy, deterministik tiebreaker;
    # u `-created_at` bilan bir yo'nalishda, ya'ni mavjud natija
    # o'zgarmaydi, faqat teng holat barqarorlashadi.
    ordering: ClassVar[list[str]] = ["-created_at", "-pk"]

    def get_queryset(self):  # type: ignore[no-untyped-def]
        return Duel.objects.select_related("challenger", "opponent", "winner").prefetch_related(
            "problems"
        )

    def create(self, request: Request, *args: object, **kwargs: object) -> Response:
        raise exceptions.MethodNotAllowed("POST")

    @extend_schema(request=None, responses={200: StaffDuelSerializer})
    @action(detail=True, methods=["post"])
    def cancel(self, request: Request, slug: str | None = None) -> Response:
        try:
            duel = staff_cancel(self.get_object())
        except DuelError as exc:
            return _error(exc)
        return Response(self.get_serializer(duel).data)

    @extend_schema(request=StaffDuelFinalizeSerializer, responses={200: StaffDuelSerializer})
    @action(detail=True, methods=["post"])
    def finalize(self, request: Request, slug: str | None = None) -> Response:
        serializer = StaffDuelFinalizeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            duel = staff_finalize(self.get_object(), force=serializer.validated_data["force"])
        except DuelError as exc:
            return _error(exc)
        return Response(self.get_serializer(duel).data)
