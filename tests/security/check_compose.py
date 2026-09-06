#!/usr/bin/env python3
"""docker-compose da judge servisi izolyatsiyasi — 06-architecture 🔒.

Matn qidirish emas, YAML tahlili: izohdagi `DATABASE_URL` so'zi
yolg'on ijobiy berardi.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent.parent
#: Judge host'da BO'LMASLIGI kerak bo'lgan sozlamalar
FORBIDDEN = ("DATABASE_URL", "DJANGO_SECRET_KEY", "POSTGRES_PASSWORD")


def main() -> int:
    compose = yaml.safe_load((ROOT / "docker-compose.yml").read_text())
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
