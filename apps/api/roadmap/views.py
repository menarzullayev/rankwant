"""Ochiq Roadmap API.

Mehmon ham O'QIYDI (taxta, batafsil, izohlar). Ovoz berish, izoh yozish
va taklif qilish uchun kirish shart — mehmonda bog'lanadigan hisob yo'q,
ya'ni "bir odam bir ovoz" qoidasini ushlab bo'lmaydi.
"""

from __future__ import annotations

from typing import Any, ClassVar

from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, viewsets
from rest_framework import status as http_status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from core.models import User
from core.pagination import StandardPagination
from roadmap import services
from roadmap.models import RoadmapItem
from roadmap.serializers import (
    RoadmapCommentSerializer,
    RoadmapCommentWriteSerializer,
    RoadmapItemSerializer,
    RoadmapItemWriteSerializer,
    RoadmapVoteSerializer,
)


class RoadmapItemViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet[RoadmapItem],
):
    """`/platform-roadmap/` — taxta, batafsil, ovoz, izoh, taklif."""

    serializer_class = RoadmapItemSerializer
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields: ClassVar[list[str]] = ["status"]
    search_fields: ClassVar[list[str]] = ["title", "body"]
    # `vote_count` — annotatsiya (`services.with_counts`), ya'ni tartiblash
    # undan keyin qo'llanadi. Nom `votes` EMAS: u modelning teskari
    # bog'lanishi bilan bir xil bo'lardi.
    ordering_fields: ClassVar[list[str]] = ["created_at", "vote_count"]
    #: Standart tartib ATAYLAB shu yerda: `annotate()` dan keyin `Meta.ordering`
    #: kuchga kirmaydi va queryset TARTIBSIZ qoladi — sahifalash esa
    #: beqaror bo'lib, bir yozuv ikki marta yoki umuman chiqmasligi mumkin
    #: (`UnorderedObjectListWarning`). `OrderingFilter` `?ordering=`
    #: bo'lmaganda ham shu ro'yxatni qo'llaydi.
    ordering: ClassVar[list[str]] = ["-created_at", "-pk"]

    def get_permissions(self) -> list[Any]:
        """Ruxsat AMALGA emas, METODGA qarab.

        `comments` — ham o'qish (GET), ham yozish (POST); shuning uchun
        amal bo'yicha ajratib bo'lmaydi. `mine` esa istisno: u GET, lekin
        shaxsiy ro'yxat, ya'ni kirish shart.
        """
        if self.action == "mine":
            return [IsAuthenticated()]
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self) -> QuerySet[RoadmapItem]:
        user = getattr(self.request, "user", None)
        # `select_related` — muallif va changelog havolasi har qatorda
        # kerak, usiz N+1 bo'lardi.
        queryset = services.visible().select_related("author", "update")
        return services.with_counts(queryset, user)

    @extend_schema(
        request=RoadmapItemWriteSerializer,
        responses={201: RoadmapItemSerializer},
    )
    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Taklif berish. Holat HAR DOIM `suggested`.

        Foydalanuvchi "chiqarildi" yoki "rejalashtirilgan" deb yozib
        qo'ya olmaydi — buni faqat jamoa o'zgartiradi.
        """
        payload = RoadmapItemWriteSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        assert isinstance(request.user, User)
        item = payload.save(
            author=request.user, status=RoadmapItem.Status.SUGGESTED
        )
        return Response(
            RoadmapItemSerializer(item, context=self.get_serializer_context()).data,
            status=http_status.HTTP_201_CREATED,
        )

    @extend_schema(request=None, responses={200: RoadmapVoteSerializer})
    @action(detail=True, methods=["post"])
    def vote(self, request: Request, pk: str | None = None) -> Response:
        """Ovoz berish. Idempotent: ikki marta bosilsa son o'zgarmaydi."""
        assert isinstance(request.user, User)
        voted, count = services.set_vote(request.user, self.get_object(), True)
        return Response({"voted": voted, "vote_count": count})

    @extend_schema(request=None, responses={200: RoadmapVoteSerializer})
    @vote.mapping.delete
    def unvote(self, request: Request, pk: str | None = None) -> Response:
        """Ovozni qaytarib olish — bir xil manzil, `DELETE` metodi."""
        assert isinstance(request.user, User)
        voted, count = services.set_vote(request.user, self.get_object(), False)
        return Response({"voted": voted, "vote_count": count})

    @extend_schema(
        request=RoadmapCommentWriteSerializer,
        responses={200: RoadmapCommentSerializer(many=True), 201: RoadmapCommentSerializer},
    )
    @action(detail=True, methods=["get", "post"])
    def comments(self, request: Request, pk: str | None = None) -> Response:
        """Izohlar: `GET` — hamma, `POST` — kirganlar.

        Moderatsiya KEYIN: izoh darhol ko'rinadi, jamoa kerak bo'lsa
        yashiradi (`is_hidden`). Oldindan tasdiq talab qilinsa muhokama
        sekinlashadi va jamoa har izohni kutib o'tirishi kerak bo'lardi.
        """
        item = self.get_object()

        if request.method == "POST":
            payload = RoadmapCommentWriteSerializer(data=request.data)
            payload.is_valid(raise_exception=True)
            assert isinstance(request.user, User)
            comment = services.add_comment(
                request.user, item, payload.validated_data["body"]
            )
            return Response(
                RoadmapCommentSerializer(
                    comment, context=self.get_serializer_context()
                ).data,
                status=http_status.HTTP_201_CREATED,
            )

        rows = services.comments_for(item)
        return Response(
            RoadmapCommentSerializer(
                rows, many=True, context=self.get_serializer_context()
            ).data
        )

    @extend_schema(responses={200: RoadmapItemSerializer(many=True)})
    @action(detail=False, methods=["get"])
    def mine(self, request: Request) -> Response:
        """Mening takliflarim — rad etilganlari ham.

        Rad etilgan taklifni ko'rsatish shart: aks holda odam "yozdim,
        javob bo'lmadi" degan taassurot bilan qoladi.
        """
        assert isinstance(request.user, User)
        rows = self.get_queryset().filter(author=request.user)
        return Response(self.get_serializer(rows, many=True).data)
