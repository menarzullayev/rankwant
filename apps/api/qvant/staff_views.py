"""Staff API — quest va do'kon katalogini boshqarish (`staff/quests/`, `staff/shop-items/`)."""

from __future__ import annotations

from typing import ClassVar

from django.db.models import Count, ProtectedError, QuerySet
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from core.openapi_docs import crud_summaries
from core.staff import StaffViewSet
from qvant import quests
from qvant.models import QvantQuest, ShopItem
from qvant.staff_serializers import StaffQuestSerializer, StaffShopItemSerializer


@crud_summaries(
    one="topshiriq",
    many="topshiriqlar",
    extra={"sync": "Topshiriqlarni sinxronlash"},
)
class StaffQuestViewSet(StaffViewSet):
    """Quest ta'riflari. Kodlar `qvant.quests` dagi hodisalarga bog'lanadi —
    yangi kod qo'shish uni avtomatik ishga tushirmaydi, faqat katalogga kiradi."""

    serializer_class = StaffQuestSerializer
    lookup_field = "code"
    search_fields: ClassVar[list[str]] = ["code", "title_uz", "title_ru", "title_en"]
    ordering_fields: ClassVar[list[str]] = ["code", "type", "reward", "is_active"]
    ordering: ClassVar[list[str]] = ["type", "code", "pk"]

    def get_queryset(self) -> QuerySet[QvantQuest]:
        return QvantQuest.objects.annotate(completion_count=Count("completions"))

    @action(detail=False, methods=["post"])
    def sync(self, request: Request) -> Response:
        """ADR-0002 earn jadvalini bazaga qayta yozadi.

        Katalogdagi kodlar uchun tur/mukofot/nom asl holiga qaytadi va
        `is_active=True` bo'ladi; qo'lda qo'shilgan questlarga tegilmaydi.
        """
        return Response({"synced": quests.sync_catalogue()})


@crud_summaries(one="do'kon buyumi", many="do'kon buyumlari")
class StaffShopItemViewSet(StaffViewSet):
    """Do'kon katalogi — ADR-0002: faqat kosmetika va qulaylik."""

    serializer_class = StaffShopItemSerializer
    lookup_field = "code"
    search_fields: ClassVar[list[str]] = ["code", "title_uz", "title_ru", "title_en"]
    ordering_fields: ClassVar[list[str]] = ["code", "category", "price", "is_active"]
    ordering: ClassVar[list[str]] = ["price", "code", "pk"]

    def get_queryset(self) -> QuerySet[ShopItem]:
        return ShopItem.objects.annotate(owner_count=Count("owners"))

    def perform_destroy(self, instance: ShopItem) -> None:
        # Sotib olingan item inventarda PROTECT bilan turadi — o'chirish o'rniga
        # is_active=False qilinadi, aks holda egalarining xaridi yo'qoladi.
        try:
            instance.delete()
        except ProtectedError as exc:
            raise serializers.ValidationError(
                {"code": ["Sotib olingan itemni o'chirib bo'lmaydi — is_active ni o'chiring"]}
            ) from exc
