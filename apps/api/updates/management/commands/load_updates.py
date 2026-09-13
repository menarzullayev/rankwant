"""`manage.py load_updates <fayl.json>` — git tarixidan tayyorlangan yozuvlarni yuklash.

Manba: `rankwant-updates-design/backfill/backfill.py` (git tarixini kalit
so'z bo'yicha mavzuli yozuvlarga guruhlaydi).

**Idempotent.** Kalit — `(released_at, title)`: bir xil faylni ikki marta
yuklash yangi yozuv yaratmaydi, balki mavjudini yangilaydi. Bu muhim,
chunki backfill qayta ishga tushirilishi mumkin (git tarixi o'sadi).

Standart holat — **qoralama** (`draft`). Nashr qilish `--publish` bilan:
qaror 15-savol — har yozuv qo'lda tasdiqlanadi, ya'ni yuklash o'zi nashr
etmaydi.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand, CommandParser

from updates.models import SystemUpdate, SystemUpdateTranslation


class Command(BaseCommand):
    help = "Git tarixidan tayyorlangan Updates yozuvlarini yuklaydi (idempotent)"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("path", type=str, help="JSON fayl yo'li")
        parser.add_argument(
            "--publish",
            action="store_true",
            help="Yuklanganlarni darhol nashr etish (standart: qoralama)",
        )
        parser.add_argument(
            "--translations",
            type=str,
            default="",
            help="Tarjimalar JSON fayli (ixtiyoriy)",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        path = Path(options["path"])
        if not path.exists():
            self.stderr.write(f"Fayl topilmadi: {path}")
            return

        rows = json.loads(path.read_text(encoding="utf-8"))
        status = SystemUpdate.Status.PUBLISHED if options["publish"] else SystemUpdate.Status.DRAFT

        created = updated = 0
        for row in rows:
            defaults = {
                "body": row.get("body", ""),
                "kind": row["kind"],
                "module": row["module"],
                "status": status,
                "locale": row.get("locale", "uz"),
                "source_repo": row.get("source_repo", ""),
                "source_refs": row.get("source_refs", []),
                "source_url": row.get("source_url", ""),
                "version": row.get("version", ""),
                "image": row.get("image", ""),
            }
            obj, was_created = SystemUpdate.objects.update_or_create(
                released_at=row["released_at"],
                title=row["title"],
                defaults=defaults,
            )
            if was_created:
                created += 1
            else:
                updated += 1

            for tr in row.get("translations", []):
                SystemUpdateTranslation.objects.update_or_create(
                    update=obj,
                    locale=tr["locale"],
                    defaults={
                        "title": tr.get("title", ""),
                        "body": tr.get("body", ""),
                        "is_machine": tr.get("is_machine", True),
                    },
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Yaratildi: {created} · Yangilandi: {updated} · "
                f"Holat: {status} · Jami bazada: {SystemUpdate.objects.count()}"
            )
        )
