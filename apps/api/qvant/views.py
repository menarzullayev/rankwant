"""Qvant API — PRD P1-5 (balans, quest, ledger) va P1-8 (do'kon)."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from django.utils import timezone
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import User
from core.pagination import TimeCursorPagination
from qvant import ledger, quests
from qvant.models import QvantQuest, QvantTransaction, ShopItem, UserInventory, UserQuestCompletion
from qvant.serializers import (
    InventorySerializer,
    PurchaseSerializer,
    QuestSerializer,
    ShopItemSerializer,
    TransactionSerializer,
    WalletSerializer,
)
from qvant.services import PurchaseError, purchase


class WalletView(APIView):
    """Balans va bugungi emissiya holati."""

    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: WalletSerializer})
    def get(self, request: Request) -> Response:
        assert isinstance(request.user, User)
        wallet = ledger.get_wallet(request.user)
        data = WalletSerializer(wallet).data
        data["earned_today"] = ledger.earned_today(request.user)
        data["remaining_today"] = ledger.remaining_today(request.user)
        return Response(data)


class TransactionViewSet(viewsets.ReadOnlyModelViewSet[QvantTransaction]):
    """Ledger — balansning har bir o'zgarishi sababi bilan."""

    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = TimeCursorPagination

    def get_queryset(self):  # type: ignore[no-untyped-def]
        assert isinstance(self.request.user, User)
        return QvantTransaction.objects.filter(user=self.request.user)


class QuestListView(APIView):
    """Bugungi questlar va ularning holati."""

    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: QuestSerializer(many=True)})
    def get(self, request: Request) -> Response:
        assert isinstance(request.user, User)
        since = timezone.now() - timedelta(days=1)
        done = set(
            UserQuestCompletion.objects.filter(
                user=request.user, completed_at__gte=since
            ).values_list("quest__code", flat=True)
        )
        # Yutuqlar umrbod — ular alohida tekshiriladi
        lifetime_done = set(
            UserQuestCompletion.objects.filter(
                user=request.user, quest__type=QvantQuest.Type.ACHIEVEMENT
            ).values_list("quest__code", flat=True)
        )
        payload = []
        for quest in QvantQuest.objects.filter(is_active=True):
            data = QuestSerializer(quest).data
            data["done"] = quest.code in (
                lifetime_done if quest.type == QvantQuest.Type.ACHIEVEMENT else done
            )
            payload.append(data)
        return Response(payload)


class MarathonView(APIView):
    """Haftalik marafon — PRD P1-9.

    Ilgari to'plam faqat serverda hisoblanardi va hech qayerda
    ko'rsatilmasdi: foydalanuvchi qaysi masalalarni yechish kerakligini
    bilmasdi va 100 Qvant amalda faqat tasodifan tegardi.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: OpenApiResponse(description="Haftalik marafon")})
    def get(self, request: Request) -> Response:
        from problems.serializers import ProblemListSerializer
        from qvant import marathon

        assert isinstance(request.user, User)
        problems = marathon.marathon_problems(request.user)
        solved = marathon.solved_this_week(request.user)
        done = UserQuestCompletion.objects.filter(
            user=request.user,
            quest__code=marathon.MARATHON_QUEST,
            period_key=quests.week_key(),
        ).exists()
        return Response(
            {
                "week": quests.week_key(),
                "reward": marathon.MARATHON_REWARD,
                "completed": done,
                "solved_count": len(solved),
                "total": len(problems),
                "problems": [
                    {
                        **ProblemListSerializer(p, context={"request": request}).data,
                        "marathon_solved": p.pk in solved,
                    }
                    for p in problems
                ],
            }
        )


class ShopViewSet(viewsets.ReadOnlyModelViewSet[ShopItem]):
    """Do'kon — ADR-0002: v1 da faqat kosmetika va qulaylik."""

    serializer_class = ShopItemSerializer
    permission_classes = [AllowAny]
    lookup_field = "code"
    queryset = ShopItem.objects.filter(is_active=True)
    pagination_class = None

    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        owned: set[str] = set()
        if request.user.is_authenticated:
            owned = set(
                UserInventory.objects.filter(user=request.user).values_list("item__code", flat=True)
            )
        payload = []
        for item in self.get_queryset():
            data = ShopItemSerializer(item).data
            data["owned"] = item.code in owned
            payload.append(data)
        return Response(payload)

    @extend_schema(request=PurchaseSerializer, responses={201: InventorySerializer})
    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def purchase(self, request: Request) -> Response:
        serializer = PurchaseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assert isinstance(request.user, User)
        try:
            entry = purchase(request.user, serializer.validated_data["item"])
        except PurchaseError as exc:
            return Response(
                {"error": {"code": "purchase_failed", "message": str(exc), "details": {}}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(InventorySerializer(entry).data, status=status.HTTP_201_CREATED)


class InventoryViewSet(viewsets.ReadOnlyModelViewSet[UserInventory]):
    serializer_class = InventorySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):  # type: ignore[no-untyped-def]
        assert isinstance(self.request.user, User)
        return UserInventory.objects.filter(user=self.request.user).select_related("item")
