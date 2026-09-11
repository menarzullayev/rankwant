"""Domen almashgach: bazadagi avatar manzillarini joriy `SITE_URL` ga ko'chiradi.

Avatar to'liq manzil bo'lib saqlanadi — OG karta chizuvchisi nisbiy manzilni
ololmaydi. Eski domen yopilgach eski manzildagi rasm ochilmay qolardi.
Takroriy ishga tushirish xavfsiz.
"""

from __future__ import annotations

from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand, CommandParser
from django.db.models import Value
from django.db.models.functions import Concat, Substr

from core import avatars
from core.models import User


class Command(BaseCommand):
    help = "Avatar manzillarini eski domendan joriy SITE_URL ga ko'chiradi."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("old_origin", help="masalan https://rankwant.bugvector.uz")

    def handle(self, *args: Any, old_origin: str, **options: Any) -> None:
        old = old_origin.rstrip("/") + avatars.PATH_PREFIX
        new = settings.SITE_URL + avatars.PATH_PREFIX
        if old == new:
            self.stdout.write("Eski va joriy manzil bir xil — ko'chiriladigan narsa yo'q")
            return
        moved = User.objects.filter(avatar_url__startswith=old).update(
            avatar_url=Concat(Value(new), Substr("avatar_url", len(old) + 1))
        )
        self.stdout.write(self.style.SUCCESS(f"{moved} ta avatar manzili ko'chirildi"))
