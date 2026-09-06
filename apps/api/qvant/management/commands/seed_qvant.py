"""Quest katalogi va do'kon narsalari — ADR-0002 jadvallaridan."""

from __future__ import annotations

from typing import Any

from django.core.management.base import BaseCommand
from django.db import transaction

from qvant.models import ShopItem
from qvant.quests import sync_catalogue

#: ADR-0002 § Spend — v1 da FAQAT kosmetika va qulaylik
SHOP = [
    ("streak-freeze", ShopItem.Category.STREAK_FREEZE, "Streak freeze (1 kun)", 200, True),
    ("frame-bronze", ShopItem.Category.AVATAR_FRAME, "Bronza ramka", 500, False),
    ("frame-silver", ShopItem.Category.AVATAR_FRAME, "Kumush ramka", 500, False),
    ("cover-night", ShopItem.Category.PROFILE_COVER, "Tungi cover", 800, False),
    ("cover-steppe", ShopItem.Category.PROFILE_COVER, "Dasht cover", 800, False),
    ("badge-solver", ShopItem.Category.USERNAME_BADGE, "Yechuvchi badge", 1500, False),
]


class Command(BaseCommand):
    help = "Qvant quest katalogi va do'kon narsalarini yaratadi"

    @transaction.atomic
    def handle(self, *args: Any, **options: Any) -> None:
        quests = sync_catalogue()
        for code, category, title, price, consumable in SHOP:
            ShopItem.objects.update_or_create(
                code=code,
                defaults={
                    "category": category,
                    "title_uz": title,
                    "price": price,
                    "is_consumable": consumable,
                    "is_active": True,
                },
            )
        self.stdout.write(self.style.SUCCESS(f"{quests} quest, {len(SHOP)} do'kon narsasi tayyor"))
