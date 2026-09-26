"""ASGI kirish nuqtasi — FAQAT `realtime` xizmati uchun (ADR-0029 §5).

⚠️ Bu `api` ning ASGI ga o'tishi EMAS. `api` gunicorn/WSGI bo'lib qoladi:
uni ASGI ga ko'chirish butun runtime'ni almashtirardi va nosozlik
izolyatsiyasini yo'qotardi (bitta to'yingan oqim butun API ni yopardi).

Ishga tushirish:

    uvicorn config.asgi:application --host 0.0.0.0 --port 8001 --workers 1
"""

from __future__ import annotations

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

from realtime.asgi import application  # noqa: E402

__all__ = ["application"]
