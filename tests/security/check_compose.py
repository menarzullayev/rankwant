#!/usr/bin/env python3
"""docker-compose da judge servisi izolyatsiyasi — 06-architecture 🔒.

Matn qidirish emas, YAML tahlili: izohdagi `DATABASE_URL` so'zi
yolg'on ijobiy berardi.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

# Kodlash muammosining IKKINCHI yarmi: yuqoridagi `read_text` o'qishni
# tuzatadi, bu esa YOZISHNI. Hisobotdagi `✓`/`✗` Windows'da quvurga
# yo'naltirilganda `cp1252` ga sig'maydi va skript o'z natijasini chop
# etayotib quladi. Sabab va to'liq izoh — `tools/_console.py`; guard shu
# yerda takrorlanadi, chunki bu fayl `tests/` ichida va `tools/` ni
# import qilmaydi (bake-off harness'ida ham xuddi shunday qilingan).
for _stream in (sys.stdout, sys.stderr):
    if (getattr(_stream, "encoding", "") or "").lower().replace("-", "") != "utf8":
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError, OSError):
            pass

ROOT = Path(__file__).resolve().parent.parent.parent
#: Judge host'da BO'LMASLIGI kerak bo'lgan sozlamalar
FORBIDDEN = ("DATABASE_URL", "DJANGO_SECRET_KEY", "POSTGRES_PASSWORD")


def main() -> int:
    # `encoding="utf-8"` SHART: `read_text()` kodlashni LOKALdan oladi va
    # Windows'da (cp1252) `docker-compose.yml` dagi izohlarning `⚠️`/`—`
    # belgilarida `UnicodeDecodeError` bilan quladi. Ya'ni judge
    # izolyatsiyasini tekshiradigan skript ishlab chiquvchi mashinasida
    # UMUMAN ishlamasdi; CI Linux'da UTF-8 bo'lgani uchun buni hech kim
    # sezmagan (o'lchandi 2026-09-16).
    compose = yaml.safe_load((ROOT / "docker-compose.yml").read_text(encoding="utf-8"))
    services = compose.get("services", {})

    problems: list[str] = []
    judges = [name for name in services if name.startswith("judge")]
    if not judges:
        print("  ⚠ compose da judge servisi yo'q — tekshiruv o'tkazib yuborildi")
        return 0

    for name in judges:
        env = services[name].get("environment") or {}
        keys = set(env) if isinstance(env, dict) else {e.split("=")[0] for e in env}
        for key in FORBIDDEN:
            if key in keys:
                problems.append(f"{name} servisiga {key} berilgan")
        if not services[name].get("privileged"):
            problems.append(f"{name} privileged emas — nsjail ishlamaydi")

        depends = services[name].get("depends_on") or {}
        names = set(depends) if isinstance(depends, dict) else set(depends)
        if "postgres" in names:
            problems.append(f"{name} postgres ga bog'langan")

    for p in problems:
        print(f"  ✗ {p}")
    if not problems:
        print(f"  ✓ judge servis(lar)i izolyatsiya qoidalariga mos: {', '.join(judges)}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
