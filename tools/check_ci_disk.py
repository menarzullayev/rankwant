#!/usr/bin/env python3
"""CI disk tozalashini tekshiradi.

⚠️ **Nega bu tekshiruv bor.** 2026-09-16 da C: da 9.59 GB qolgandi.
Sabab: har CI yurishi yangi Docker obrazi qurib, eskisini o'chirmasdi.
O'lchandi — **420 ta `rw-smoke-*` + 122 ta `rankwant-build-*`** yig'ilib,
runner'ning WSL diskini 58 GB ga yetkazgan.

`docker compose down -v` konteyner va volume'larni olib tashlaydi, lekin
**qurilgan obrazlarni qoldiradi**. Shuning uchun har yurish oxirida
obrazlarni alohida tozalash kerak.

Bu qadam olib tashlansa, hech bir test qizil bo'lmaydi — muammo bir necha
hafta ichida asta-sekin qaytadi. Shu tekshiruv uni darhol ushlaydi.
"""
from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CI = ROOT / ".github/workflows/ci.yml"
DEPLOY = ROOT / ".github/workflows/deploy.yml"

#: Har bir fayl: (yo'l, job nomi, izlanadigan naqshlar).
EXPECTED = [
    (CI, "smoke", [r"docker\s+rmi", r"builder\s+prune"]),
    (DEPLOY, "deploy", [r"docker\s+rmi", r"builder\s+prune"]),
]


def job_steps(src: str, job: str) -> list[str]:
    """Berilgan job'ning qadamlarini qaytaradi (oddiy indent asosida)."""
    lines = src.splitlines()
    out: list[str] = []
    in_job = False
    in_steps = False
    for ln in lines:
        if re.match(r"^  \w[\w-]*:\s*$", ln):
            in_job = ln.strip().rstrip(":") == job
            in_steps = False
            continue
        if in_job and re.match(r"^\s{4}steps:\s*$", ln):
            in_steps = True
            continue
        if in_steps:
            if re.match(r"^\s{4}\S", ln):  # job ichidagi boshqa kalit
                in_steps = False
                continue
            out.append(ln)
    return out


def main() -> int:
    problems = 0
    for path, job, patterns in EXPECTED:
        if not path.exists():
            print(f"  ✕ topilmadi: {path}")
            problems += 1
            continue
        src = path.read_text(encoding="utf-8")
        steps = "\n".join(job_steps(src, job))
        if not steps:
            print(f"  ✕ {path.name}: '{job}' job'ida qadam yo'q")
            problems += 1
            continue
        for pat in patterns:
            if not re.search(pat, steps):
                print(
                    f"  ✕ {path.name} / {job}: `{pat}` topilmadi — "
                    f"obrazlar tozalanmaydi"
                )
                problems += 1
        if not re.search(r"if:\s*always\(\)", steps):
            print(
                f"  ✕ {path.name} / {job}: tozalash `if: always()` emas — "
                f"yurish yiqilsa obrazlar qoladi"
            )
            problems += 1

    if problems:
        print(
            f"\nJami: {problems} muammo.\n"
            "⚠️ CI har yurishda yangi Docker obrazi quradi. Tozalash "
            "bo'lmasa ular yig'ilib disk(small to'ldiradi — 2026-09-16 da "
            "58 GB ga yetgan edi."
        )
        return 1

    print(
        f"Tekshirildi: {len(EXPECTED)} workflow × "
        f"({', '.join(p for p in ('docker rmi', 'builder prune'))})\n"
        "CI disk tozalashi joyida ✓"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
