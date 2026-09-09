"""Bir xil nomli mavzularni birlashtiradi.

Ishlatish:  python manage.py merge_topics

Import slug bo'yicha dedupe qilgan davrda `dp` va `dinamik-dasturlash`
alohida yozuv bo'lib qolgan edi — foydalanuvchi esa filtr panelida
«Dinamik dasturlash» ni ikki marta ko'rardi. Eng eskisi (kichik `pk`)
saqlanadi: uning slug'i havolalarda va roadmap'larda ishlatilgan.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from django.core.management.base import BaseCommand
from django.db import transaction

from problems.models import Topic


class Command(BaseCommand):
    help = "Bir xil nomli mavzularni bittaga yig'adi."

    @transaction.atomic
    def handle(self, *args: Any, **options: Any) -> None:
        by_name: dict[str, list[Topic]] = defaultdict(list)
        for topic in Topic.objects.order_by("pk"):
            by_name[topic.name_uz.strip().casefold()].append(topic)

        merged = 0
        for rows in by_name.values():
            if len(rows) < 2:
                continue
            keeper, *extras = rows
            for extra in extras:
                # Mavzuga UCHTA bog'lanish bor — masala, maqola va test
                # savoli. Bittasi unutilsa, o'chirish M2M qatorlarini
                # birga olib ketardi va bog'lanish jimgina yo'qolardi.
                keeper.problems.add(*extra.problems.all())
                keeper.articles.add(*extra.articles.all())
                keeper.questions.add(*extra.questions.all())
                extra.children.update(parent=keeper)
                self.stdout.write(f"{extra.slug} → {keeper.slug} ({keeper.name_uz})")
                extra.delete()
                merged += 1

        self.stdout.write(self.style.SUCCESS(f"{merged} takroriy mavzu birlashtirildi"))
