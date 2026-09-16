"""Ochiq Updates API.

Mehmon ham o'qiydi (qaror 8-savol) — shuning uchun `AllowAny`. O'qilmagan
holat bilan bog'liq amallar esa faqat kirganlarga: mehmonda `UpdateRead`
yozuvi yo'q.
"""

from __future__ import annotations

from typing import Any, ClassVar

from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from core.models import User
from core.openapi_docs import crud_summaries
from core.pagination import StandardPagination
from updates import services
from updates.models import SystemUpdate, UpdateRead
from updates.serializers import (
    SystemUpdateSerializer,
    UnreadModuleSerializer,
    UpdateMarkReadSerializer,
    resolve_locale,
)


@crud_summaries(
    one="yangilik",
    many="yangiliklar",
    only=("list", "retrieve"),
    extra={"unread_count": "O'qilmaganlar soni"},
)
class SystemUpdateViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet[SystemUpdate]
):
    """`/updates/` — arxiv. Har yozuv doimiy havola oladi (SEO, tashqi havola)."""

    serializer_class = SystemUpdateSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardPagination
    # `filter_backends` ni e'lon qilish `DEFAULT_FILTER_BACKENDS` ni TO'LIQ
    # almashtiradi — shuning uchun uchtasi ham sanab o'tiladi. `SearchFilter`
    # busiz `search_fields` deklaratsiyasi JONLI EMAS edi: maydon e'lon
    # qilingan, lekin `?search=` hech narsa qilmasdi.
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields: ClassVar[list[str]] = ["kind", "module", "version"]
    search_fields: ClassVar[list[str]] = ["title", "body"]
    ordering_fields: ClassVar[list[str]] = ["released_at", "published_at"]

    #: Ro'yxat uchun bir marta hisoblangan o'qilgan id'lar. `None` — hisoblanmagan.
    _read_ids: set[int] | None = None

    def get_queryset(self) -> QuerySet[SystemUpdate]:
        """Ro'yxat — faqat lentadagi yozuvlar.

        Batafsil esa nashrdan olinganini ham ochadi (qaror 20: havola
        sindirilmaydi). Ilgari ikkalasi ham `published()` edi, ya'ni
        `withdraw()` docstring'i "havolasi ishlaydi" deb yozib turib,
        amalda 404 qaytarardi — hujjat bilan kod zid edi.
        """
        if self.action == "retrieve":
            return services.retrievable()
        return services.published()

    def _read_ids_for(self, rows: list[SystemUpdate]) -> set[int] | None:
        """Bitta so'rov — har yozuv uchun alohida `exists()` N+1 bo'lardi."""
        user = getattr(self.request, "user", None)
        if user is None or not user.is_authenticated or not rows:
            return None
        return set(
            UpdateRead.objects.filter(user=user, update_id__in=[r.pk for r in rows]).values_list(
                "update_id", flat=True
            )
        )

    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            self._read_ids = self._read_ids_for(page)
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_serializer_context(self) -> dict[str, Any]:
        ctx: dict[str, Any] = dict(super().get_serializer_context())
        ctx["locale"] = resolve_locale(self.request)
        ctx["read_ids"] = self._read_ids
        return ctx

    @extend_schema(responses={200: SystemUpdateSerializer(many=True)})
    @action(detail=False, methods=["get"], permission_classes=[AllowAny])
    def actionable(self, request: Request) -> Response:
        """Harakatga chaqiruvchi yozuvlar — arxiv tepasidagi alohida blok.

        Nega alohida so'rov: `breaking`/`deprecated` yozuvlari KAM, lekin
        muhim. Ular joriy sahifada umuman bo'lmasligi mumkin (arxiv 25
        tadan sahifalanadi), ya'ni sahifalangan ro'yxatdan ularni ajratib
        bo'lmaydi. Qaror 11 shu ikki turni rang VA joylashuvda ajratishni
        talab qiladi — joylashuv shu blok.
        """
        rows = list(self.get_queryset().filter(kind__in=SystemUpdate.ACTIONABLE))
        self._read_ids = self._read_ids_for(rows)
        return Response(self.get_serializer(rows, many=True).data)

    @extend_schema(responses={200: SystemUpdateSerializer(many=True)})
    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def unread(self, request: Request) -> Response:
        """O'qilmaganlar — qo'ng'iroq paneli uchun (qaror 6-savol)."""
        assert isinstance(request.user, User)
        queryset = services.unread_queryset(request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            self._read_ids = set()
            return self.get_paginated_response(self.get_serializer(page, many=True).data)
        return Response(self.get_serializer(queryset, many=True).data)

    @extend_schema(responses={200: None})
    @action(
        detail=False,
        methods=["get"],
        url_path="unread-count",
        permission_classes=[IsAuthenticated],
    )
    def unread_count(self, request: Request) -> Response:
        assert isinstance(request.user, User)
        return Response(
            {
                "count": services.unread_count(request.user),
                "actionable": services.actionable_unread(request.user).count(),
            }
        )

    @extend_schema(responses={200: UnreadModuleSerializer(many=True)})
    @action(
        detail=False,
        methods=["get"],
        url_path="unread-by-module",
        permission_classes=[IsAuthenticated],
    )
    def unread_by_module(self, request: Request) -> Response:
        """Nav chipi uchun — modul bo'yicha o'qilmaganlar (qaror 6-savol)."""
        assert isinstance(request.user, User)
        return Response(services.unread_by_module(request.user))

    @extend_schema(request=UpdateMarkReadSerializer, responses={200: None})
    @action(
        detail=False,
        methods=["post"],
        url_path="mark-read",
        permission_classes=[IsAuthenticated],
    )
    def mark_read(self, request: Request) -> Response:
        """`ids` bo'sh bo'lsa — hammasi o'qilgan ("Hammasi o'qildi")."""
        serializer = UpdateMarkReadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assert isinstance(request.user, User)
        ids = serializer.validated_data.get("ids")
        return Response({"updated": services.mark_read(request.user, ids)})
