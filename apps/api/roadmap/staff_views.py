"""Staff Roadmap API — `staff/platform-roadmap/`.

Uch ish:
  * `set-status` — holatni o'zgartirish. `status` to'g'ridan-to'g'ri
    yozilmaydi (serializerda read-only), chunki o'tish vaqtini ham
    yozish kerak — aks holda batafsil sahifadagi "holat tarixi" bo'sh
    qolardi.
  * bandni tahrirlash — sarlavha, matn, muddat, changelog havolasi,
    feature flag.
  * izohni yashirish — post-moderatsiya.

Alohida "nashr qilish" oqimi ATAYLAB yo'q: band `suggested` bo'lib
tug'iladi va jamoa uni `planned` ga o'tkazadi — tasdiq shu o'tishning
o'zi. `updates` modulida esa nashr alohida amal, chunki u yerda yozuv
avtomatik qoralama bo'lib keladi.
"""

from __future__ import annotations

from typing import ClassVar

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.request import Request
from rest_framework.response import Response

from core.openapi_docs import crud_summaries
from core.staff import StaffViewSet
from roadmap import services
from roadmap.models import RoadmapComment, RoadmapItem
from roadmap.serializers import (
    StaffRoadmapCommentSerializer,
    StaffRoadmapItemSerializer,
    StaffStatusSerializer,
)


@crud_summaries(
    one="platforma yo'l xaritasi bandi",
    many="platforma yo'l xaritasi bandlari",
    extra={"set_status": "Band holatini o'zgartirish"},
)
class StaffRoadmapViewSet(StaffViewSet):
    queryset = RoadmapItem.objects.select_related("author", "update")
    serializer_class = StaffRoadmapItemSerializer
    # `StaffViewSet` da `filter_backends` faqat Search + Ordering, ya'ni
    # `filterset_fields` o'sha holatda JONSIZ bo'lardi (e'lon qilingan,
    # lekin hech narsa qilmaydi). DjangoFilterBackend shu yerda qo'shiladi.
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields: ClassVar[list[str]] = ["title", "body", "target_quarter"]
    ordering_fields: ClassVar[list[str]] = ["pk", "created_at", "status", "released_at"]
    filterset_fields: ClassVar[list[str]] = ["status", "is_enabled"]

    @action(detail=True, methods=["post"], url_path="set-status")
    def set_status(self, request: Request, pk: str | None = None) -> Response:
        payload = StaffStatusSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        item = self.get_object()
        item.set_status(payload.validated_data["status"])
        return Response(self.get_serializer(item).data)


class StaffRoadmapCommentViewSet(StaffViewSet):
    """Izohlar moderatsiyasi — post-modelleratsiya.

    Izoh o'chirilmaydi, `is_hidden` qilinadi: qaror keyin ko'rib
    chiqilishi va muallifga nima uchun yashirilganini aytish mumkin
    bo'lishi kerak.
    """

    queryset = RoadmapComment.objects.select_related("author", "item")
    serializer_class = StaffRoadmapCommentSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields: ClassVar[list[str]] = ["body", "author__username", "item__title"]
    ordering_fields: ClassVar[list[str]] = ["pk", "created_at"]
    filterset_fields: ClassVar[list[str]] = ["is_hidden", "item"]

    def _set_hidden(self, request: Request, hidden: bool) -> Response:
        comment = services.hide_comment(self.get_object(), hidden)
        return Response(self.get_serializer(comment).data)

    @action(detail=True, methods=["post"])
    def hide(self, request: Request, pk: str | None = None) -> Response:
        return self._set_hidden(request, True)

    @action(detail=True, methods=["post"])
    def unhide(self, request: Request, pk: str | None = None) -> Response:
        return self._set_hidden(request, False)


__all__ = [
    "StaffRoadmapCommentViewSet",
    "StaffRoadmapViewSet",
]
