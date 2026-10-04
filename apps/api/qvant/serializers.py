from __future__ import annotations

from typing import Any

from rest_framework import serializers

from qvant.models import (
    QvantQuest,
    QvantTransaction,
    QvantWallet,
    ShopItem,
    UserInventory,
    UserQuestCompletion,
)


class WalletSerializer(serializers.ModelSerializer[QvantWallet]):
    earned_today = serializers.IntegerField(read_only=True)
    remaining_today = serializers.IntegerField(read_only=True)

    class Meta:
        model = QvantWallet
        fields = ["balance", "earned_today", "remaining_today", "updated_at"]


class TransactionSerializer(serializers.ModelSerializer[QvantTransaction]):
    class Meta:
        model = QvantTransaction
        fields = ["id", "amount", "reason", "ref_type", "ref_id", "balance_after", "created_at"]


class QuestSerializer(serializers.ModelSerializer[QvantQuest]):
    done = serializers.BooleanField(read_only=True, default=False)

    class Meta:
        model = QvantQuest
        fields = ["code", "type", "title_uz", "title_ru", "title_en", "reward", "done"]


class QuestCompletionSerializer(serializers.ModelSerializer[UserQuestCompletion]):
    quest = serializers.SlugRelatedField[QvantQuest](slug_field="code", read_only=True)

    class Meta:
        model = UserQuestCompletion
        fields = ["quest", "period_key", "awarded", "completed_at"]


class ShopItemSerializer(serializers.ModelSerializer[ShopItem]):
    owned = serializers.BooleanField(read_only=True, default=False)

    class Meta:
        model = ShopItem
        fields = [
            "code",
            "category",
            "title_uz",
            "title_ru",
            "title_en",
            "price",
            "is_consumable",
            "owned",
        ]


class InventorySerializer(serializers.ModelSerializer[UserInventory]):
    item = ShopItemSerializer(read_only=True)

    class Meta:
        model = UserInventory
        fields = ["id", "item", "purchased_at", "is_equipped"]


class PurchaseSerializer(serializers.Serializer[dict[str, Any]]):
    item = serializers.SlugField()


class QvantTopSerializer(serializers.ModelSerializer[QvantWallet]):
    """A row of the public Qvant top list (HITL 2026-10-05).

    The balance is public here by the owner's decision; the ledger behind
    it (`/qvant/transactions/`) stays private to its user.
    """

    username = serializers.CharField(source="user.username", read_only=True)
    display_name = serializers.CharField(source="user.display_name", read_only=True)
    avatar_url = serializers.CharField(source="user.avatar_url", read_only=True)

    class Meta:
        model = QvantWallet
        fields = ["username", "display_name", "avatar_url", "balance"]
