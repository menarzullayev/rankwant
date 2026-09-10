"""Ijtimoiy kirish — ADR-0016.

Kutubxona qo'shilmadi (`django-allauth` o'z shablonlari, URL'lari va
modellari bilan keladi). Bizda API headless, frontend esa alohida —
uchala provayder ham oddiy HTTP almashuvi, xuddi email zanjiridagi kabi.
"""

from __future__ import annotations

from django.conf import settings

#: Har provayder uchun: kalit sozlanganini bildiruvchi sozlama nomlari.
#: Kaliti yo'q provayder ro'yxatga umuman tushmaydi va uning tugmasi
#: frontendda ko'rinmaydi — email zanjiridagi bilan bir xil qoida.
REQUIRED: dict[str, tuple[str, ...]] = {
    "google": ("GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET"),
    "github": ("GITHUB_CLIENT_ID", "GITHUB_CLIENT_SECRET"),
    "telegram": ("TELEGRAM_BOT_TOKEN",),
}


def configured() -> list[str]:
    """Sozlangan provayderlar — frontend shu ro'yxat bo'yicha tugma chizadi."""
    return [
        name for name, keys in REQUIRED.items() if all(getattr(settings, key, "") for key in keys)
    ]
