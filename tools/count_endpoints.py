#!/usr/bin/env python3
"""API endpointlarini domen bo'yicha sanaydi.

Manba — `config/api_urls.py` va har bir app'ning `urls.py`. Router'lar
(`DefaultRouter`) registratsiyasini ham sanaymiz, chunki ular CRUD
endpointlarini avtomatik yasaydi va qo'lda yozilgan `path()` lardan
ko'rinmaydi.
"""
from __future__ import annotations

import pathlib
import re

API = pathlib.Path(__file__).resolve().parent.parent / "apps/api"

# Router.register("nom", ViewSet) — har biri ~5 endpoint (list/create/
# retrieve/update/destroy), lekin `read_only` bo'lsa 2-3.
ROUTE = re.compile(r"""\.register\(\s*["']([^"']+)["']""")
PATH = re.compile(r"""^\s*path\(\s*["']([^"']*)["']""")

rows: list[tuple[str, int, int]] = []
for app in sorted(p for p in API.iterdir() if p.is_dir() and (p / "urls.py").exists()):
    src = (app / "urls.py").read_text(encoding="utf-8", errors="replace")
    routes = ROUTE.findall(src)
    paths = [p for p in PATH.findall(src) if p]
    rows.append((app.name, len(routes), len(paths)))

total_r = sum(r for _, r, _ in rows)
total_p = sum(p for _, _, p in rows)

print(f"{'APP':<16}{'ROUTER':>8}{'PATH':>7}")
print("-" * 31)
for name, r, p in rows:
    print(f"{name:<16}{r:>8}{p:>7}")
print("-" * 31)
print(f"{'JAMI':<16}{total_r:>8}{total_p:>7}")
print()
print(f"Router yozuvlari: {total_r}  (~{total_r * 5} CRUD endpoint)")
print(f"Qo'lda path():    {total_p}")
