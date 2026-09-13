"""Staff Updates API — `staff/updates/`.

Qaror 15-savol: **har yozuv qo'lda tasdiqlanadi**. Shuning uchun oqim:
qoralama (`draft`) → `publish` → nashr. `withdraw` — o'chirish emas
(qaror 20-savol): yozuv arxivda qoladi, havolasi ishlaydi.

`is_enabled` — feature flag (qaror 17-savol). `withdraw` dan farqi:
`withdraw` — yozuvni umuman nashrdan olish; `is_enabled=False` — modul
butunlay o'chirilganda vaqtincha yashirish.
"""

from __future__ import annotations

from typing import Any, ClassVar

from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from core.staff import StaffViewSet
from updates import services
from updates.models import SystemUpdate
from updates.serializers import StaffSystemUpdateSerializer


class StaffUpdateViewSet(StaffViewSet):
    queryset = SystemUpdate.objects.prefetch_related("translations").select_related("author")
    serializer_class = StaffSystemUpdateSerializer
    search_fields: ClassVar[list[str]] = ["title", "body", "version"]
    ordering_fields: ClassVar[list[str]] = ["pk", "released_at", "published_at", "kind", "module"]
    filterset_fields: ClassVar[list[str]] = ["status", "kind", "module"]

    def perform_create(self, serializer: Any) -> None:
        serializer.save(author=self.request.user)

    @action(detail=True, methods=["post"])
    def publish(self, request: Request, pk: str | None = None) -> Response:
        obj = services.mark_published(self.get_object())
        return Response(self.get_serializer(obj).data)

    @action(detail=True, methods=["post"])
    def withdraw(self, request: Request, pk: str | None = None) -> Response:
        obj = services.withdraw(self.get_object())
        return Response(self.get_serializer(obj).data)

    def _set_enabled(self, request: Request, value: bool) -> Response:
        obj = self.get_object()
        obj.is_enabled = value
        obj.save(update_fields=["is_enabled", "updated_at"])
        services.prune_reads(obj)
        return Response(self.get_serializer(obj).data)

    @action(detail=True, methods=["post"])
    def enable(self, request: Request, pk: str | None = None) -> Response:
        return self._set_enabled(request, True)

    @action(detail=True, methods=["post"])
    def disable(self, request: Request, pk: str | None = None) -> Response:
        """Feature flag o'chirish — rollback (qaror 17-savol)."""
        return self._set_enabled(request, False)
