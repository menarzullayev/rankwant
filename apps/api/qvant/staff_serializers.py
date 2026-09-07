"""Staff (admin UI) serializerlari — quest va do'kon katalogi.

Ommaviy serializerlardan farqi: `is_active` va `asset_ref` ham tahrirlanadi.
Ledger, wallet va inventar bu yerda YO'Q — ular faqat o'qiladi (ADR-0002).
"""

from __future__ import annotations

from rest_framework import serializers

from qvant.models import QvantQuest, ShopItem


class StaffQuestSerializer(serializers.ModelSerializer[QvantQuest]):
    completion_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = QvantQuest
        fields = [
            "id",
            "code",
            "type",
            "title_uz",
            "title_ru",
            "title_en",
            "reward",
            "is_active",
            "completion_count",
        ]


class StaffShopItemSerializer(serializers.ModelSerializer[ShopItem]):
    owner_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = ShopItem
        fields = [
            "id",
            "code",
            "category",
            "title_uz",
            "title_ru",
            "title_en",
            "price",
            "asset_ref",
            "is_active",
            "is_consumable",
            "owner_count",
        ]
