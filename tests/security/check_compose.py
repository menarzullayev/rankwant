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

# ── ADR-0028: tarmoq topologiyasi ────────────────────────────────────
#: Judge FAQAT shu tarmoqda (`internal: true`) — default'dan chiqarilgan.
JUDGE_NET = "judge-net"
#: Faqat default (implicit) tarmoqda — judge tarmog'ida EMAS. Bu invariant
#: asosiy yutuq: judge'dan DB/API'ga yo'l yo'q.
DEFAULT_ONLY = ("postgres", "api", "worker", "beat", "web", "migrate")
#: Ikkala tarmoqda — judge ularga yetadi, qolganlari ham yetadi (navbat
#: alohida Redis, S3 esa read-only user bilan). Postgres ularda YO'Q.
BOTH_NETWORKS = ("minio", "judge-queue")
#: Judge root kredensialini (A-2) UMUMAN ko'rmasligi kerak — qiymat bilan.
#: `check_security_boundary.py` kalitlarni tekshiradi, bu esa QIYMATNI:
#: ochiq repodagi root parol judge env'ida qayta paydo bo'lsa qizaradi.
ROOT_SECRET_VALUE = "devdevdev"


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
    # `judge-queue` — navbat Redis'i (ADR-0028), judge host EMAS: u
    # `privileged` bo'lmasligi va ikkala tarmoqda turishi kerak. Shu sababli
    # prefix-qidiruvdan chiqariladi — aks holda yolg'on qizil berardi.
    judges = [
        name
        for name in services
        if name.startswith("judge") and name not in ("judge-queue",)
    ]
    if not judges:
        print("  ⚠ compose da judge servisi yo'q — tekshiruv o'tkazib yuborildi")
        return 0

    for name in judges:
        env = services[name].get("environment") or {}
        keys = set(env) if isinstance(env, dict) else {e.split("=")[0] for e in env}
        values = (
            set(env.values())
            if isinstance(env, dict)
            else {e.split("=", 1)[1] for e in env if "=" in e}
        )
        for key in FORBIDDEN:
            if key in keys:
                problems.append(f"{name} servisiga {key} berilgan")
        if ROOT_SECRET_VALUE in values:
            problems.append(
                f"{name} env'da root MinIO paroli bor (A-2, ADR-0028) — "
                "judge faqat `judge-ro` userini ko'radi"
            )
        if not services[name].get("privileged"):
            problems.append(f"{name} privileged emas — nsjail ishlamaydi")

        depends = services[name].get("depends_on") or {}
        names = set(depends) if isinstance(depends, dict) else set(depends)
        if "postgres" in names:
            problems.append(f"{name} postgres ga bog'langan")

        # ADR-0028: judge FAQAT `judge-net`da — default (implicit) tarmoq
        # unga ko'rinmasligi kerak. `networks:` yo'q = hammasi default'da,
        # ya'ni bu qoidani tekshirmasdan o'tkazish YOLGON yashil bo'lardi.
        nets = services[name].get("networks")
        net_names = set(nets) if isinstance(nets, dict) else set(nets or [])
        if net_names != {JUDGE_NET}:
            problems.append(
                f"{name} faqat `{JUDGE_NET}`da bo'lishi kerak, hozir: "
                f"{sorted(net_names) or 'default (implicit)'}"
            )

    # Tarmoq topologiyasi — judge nima Ko'RADI, nima KO'RMAYDI.
    # `internal: true` bo'lmasa internal tarmoq nomi — oddiy ko'prik,
    # ya'ni preflight tarmog'i o'zi chetlab o'tiladigan bo'ladi.
    networks_block = compose.get("networks") or {}
    if (networks_block.get(JUDGE_NET) or {}).get("internal") is not True:
        problems.append(f"`{JUDGE_NET}` tarmog'i `internal: true` emas")

    def _nets(name: str) -> set[str]:
        n = services.get(name, {}).get("networks")
        return set(n) if isinstance(n, dict) else set(n or [])

    for name in BOTH_NETWORKS:
        if name not in services:
            problems.append(f"{name} servisi compose da yo'q (ADR-0028 talab qiladi)")
        elif _nets(name) != {"default", JUDGE_NET}:
            problems.append(
                f"{name} ikkala tarmoqda bo'lishi kerak (default + {JUDGE_NET}), "
                f"hozir: {sorted(_nets(name)) or 'default (implicit)'}"
            )
    for name in DEFAULT_ONLY:
        if name not in services:
            problems.append(f"{name} servisi compose da yo'q")
        elif JUDGE_NET in _nets(name):
            problems.append(f"{name} `{JUDGE_NET}` tarmog'ida — postgres yo'li ochiladi!")

    for p in problems:
        print(f"  ✗ {p}")
    if not problems:
        print(f"  ✓ judge servis(lar)i izolyatsiya qoidalariga mos: {', '.join(judges)}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
