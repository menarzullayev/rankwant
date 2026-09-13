"""`ui_prefs` ni v1 (yassi) dan v2 (guruhlangan) ga ko'chiradi.

Qaror D35: **migratsiya + o'qishda moslash** — ikkalasi ham kerak.
Faqat baza migratsiyasi yetarli emas, chunki `localStorage` da eski shakl
yotadi va u hidratsiyadan OLDIN o'qiladi; tanilmasa bir yuklanishda eski
ko'rinish chaqnaydi. O'qishda moslash `core/prefs.py` `migrate()` da.

Bu migratsiya faqat mavjud hisoblarni ko'chiradi. Yangi yozuvlar allaqachon
v2 bo'lib keladi (serializer `prefs.validate()` orqali).
"""

from __future__ import annotations

from typing import Any

from django.db import migrations


def to_v2(apps: Any, schema_editor: Any) -> None:
    User = apps.get_model("core", "User")
    for user in User.objects.exclude(ui_prefs={}).iterator():
        raw = user.ui_prefs
        if not isinstance(raw, dict) or raw.get("version") is not None:
            # Allaqachon v2 yoki noma'lum versiya — TEGILMAYDI (D36).
            continue
        appearance: dict[str, Any] = {}
        if isinstance(raw.get("style"), str):
            appearance["style"] = raw["style"]
        new: dict[str, Any] = {"version": 2, "appearance": appearance}
        for key in ("sound", "effect"):
            if key in raw:
                new[key] = raw[key]
        user.ui_prefs = new
        user.save(update_fields=["ui_prefs"])


def to_v1(apps: Any, schema_editor: Any) -> None:
    """Orqaga qaytarish: `style` ni yassi shaklga chiqaradi."""
    User = apps.get_model("core", "User")
    for user in User.objects.exclude(ui_prefs={}).iterator():
        raw = user.ui_prefs
        if not isinstance(raw, dict) or raw.get("version") != 2:
            continue
        appearance = raw.get("appearance") or {}
        old: dict[str, Any] = {}
        if "style" in appearance:
            old["style"] = appearance["style"]
        for key in ("sound", "effect"):
            if key in raw:
                old[key] = raw[key]
        user.ui_prefs = old
        user.save(update_fields=["ui_prefs"])


class Migration(migrations.Migration):
    dependencies = [("core", "0015_user_phone")]
    operations = [migrations.RunPython(to_v2, to_v1)]
