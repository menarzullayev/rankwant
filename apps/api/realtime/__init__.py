"""`realtime` — SSE orqali jonli yangilanish (ADR-0029).

⚠️ Bu Django ilovasi **modellarsiz**: migratsiya yo'q, admin yo'q.
U `INSTALLED_APPS` ga qo'shilmaydi — chunki uning kodi Django middleware
zanjiridan tashqarida ishlaydi (sabab `realtime/asgi.py` docstring'ida).
Shu sababli u `apps.py` ham talab qilmaydi.
"""
