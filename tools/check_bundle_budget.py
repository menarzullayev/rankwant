#!/usr/bin/env python3
"""Bundle budget — Next.js chiqishi byudjetga sig'adimi (RW-ARCH-016).

NEGA KERAK: `next build` hech qachon YIQILMAYDI. Bitta `import` qo'shilsa
va u 300 KB kutubxonani tortsa, build baribir yashil chiqadi va byudjet
faqat foydalanuvchi internetida bilinadi. Bu tekshiruv shu bo'shliqni
yopadi: build chiqishi diskda o'lchanadi va chegaradan oshsa exit 1.

NIMA O'LCHANADI — `apps/web/.next/static` ostidagi haqiqiy fayllar:

  * `js_gzip`  — barcha `.js` ning gzip'langan yig'indisi (telefon
    internetida foydalanuvchi yuklab oladigan hajm);
  * `css_gzip` — barcha `.css` ning gzip yig'indisi;
  * `chunk_max` — ENG KATTA bitta `.js` gzip hajmi. Yig'indi yashirin
    qoldiradigan narsani shu tutadi: 60 ta kichik chunk o'rniga bitta
    1 MB chunk kelishi mumkin.

Nega GZIP, xom emas: CDN (Cloudflare) JS/CSS ni gzip yoki brotli bilan
uzatadi, ya'ni sim orqali ketadigan hajm — gzip hajmi. Xom hajm esa
minifikatsiyadan keyin ham sun'iy katta ko'rinadi.

⚠️ TURBOPACK: Next 16 Turbopack build'i `First Load JS` jadvalini
CHIQARMAYDI (`next build --turbo` da faqat marshrutlar ro'yxati). Shuning
uchun tekshiruv build hisobotini o'qimaydi, fayllarni o'zi o'lchaydi —
hisobot formati versiyalar orasida o'zgaradi, `static/` tuzilishi esa
barqaror.

Chiqish: 0 — byudjet ichida; 1 — oshib ketdi; 2 — o'lchab bo'lmadi
(build qilinmagan).

Byudjetni yangilash: `python tools/check_bundle_budget.py --write`
(hozirgi o'lchovni `BUDGET` ga yozadi va sababni izohda qoldiradi).
"""

from __future__ import annotations

import argparse
import gzip
import json
import os
import sys
from pathlib import Path

import _console

_console.force_utf8()

ROOT = Path(__file__).resolve().parent.parent
#: Overridable so the negative tests can point at a directory that does not
#: exist and prove the gate reports exit 2 rather than a silent "within
#: budget" (a zero-size measurement passes every `<= limit` comparison).
STATIC = Path(
    os.environ.get("RW_BUNDLE_STATIC") or ROOT / "apps" / "web" / ".next" / "static"
)

#: Hozirgi o'lchovdan olingan byudjet (2026-09-24, RW-ARCH-016).
#:
#: Qiymatlar *gzip* baytda va ataylab biroz yumaloq: byudjet signal
#: bo'lishi kerak, har build'da qizib yonadigan tuzoq emas. Har biri
#: o'lchangan hajmdan ~15% yuqori — shu oraliq normal o'sishni
#: (yangi sahifa, kichik kutubxona) o'tkazadi, lekin ikki barobar
#: sakrashni ushlaydi.
#:
#: | Ko'rsatkich | O'lchandi | Byudjet |
#: |---|---|---|
#: | js_gzip    | 0.90 MiB | 1.05 MiB |
#: | css_gzip   | 0.05 MiB | 0.10 MiB |
#: | chunk_max  | 310.8 KB | 360.0 KB |
BUDGET: dict[str, int] = {
    "js_gzip": 1_100_000,  # ~1.05 MiB
    "css_gzip": 110_000,  # ~0.10 MiB
    "chunk_max": 370_000,  # ~361 KB
}


def _gzip_size(path: Path) -> int:
    """Faylning gzip hajmi. O'qib bo'lmasa — xom hajm (eng yomon holat)."""
    try:
        return len(gzip.compress(path.read_bytes(), 9))
    except OSError:
        return path.stat().st_size


def measure() -> tuple[dict[str, int], list[tuple[str, int]]]:
    """`static/` ichidagi JS/CSS ni o'lchaydi.

    Qaytadi: (ko'rsatkichlar, eng katta 5 JS chunk).
    """
    if not STATIC.is_dir():
        raise FileNotFoundError(STATIC)

    js: list[tuple[str, int]] = []
    css_total = 0
    for path in STATIC.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix == ".js":
            js.append((path.name, _gzip_size(path)))
        elif path.suffix == ".css":
            css_total += _gzip_size(path)

    if not js:
        # Build bor, lekin JS yo'q — bu ham o'lchov xatosi, "byudjet ichida"
        # emas. Aks holda bo'sh `static/` yashil o'tib ketardi.
        raise ValueError("`.next/static` da hech qanday `.js` topilmadi")

    js_total = sum(size for _, size in js)
    largest = max(size for _, size in js)
    stats = {
        "js_gzip": js_total,
        "css_gzip": css_total,
        "chunk_max": largest,
    }
    return stats, sorted(js, key=lambda row: -row[1])[:5]


def human(num: int) -> str:
    if num >= 1_048_576:
        return f"{num / 1_048_576:.2f} MiB"
    return f"{num / 1024:.1f} KB"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write",
        action="store_true",
        help="Hozirgi o'lchovni BUDGET ko'rinishida chiqaradi (qo'lda ko'chiriladi)",
    )
    parser.add_argument(
        "--json", action="store_true", help="Mashina o'qiydigan chiqish"
    )
    args = parser.parse_args()

    try:
        stats, top = measure()
    except FileNotFoundError:
        print("✗ Bundle: `apps/web/.next/static` yo'q — avval build qiling")
        print("  cd apps/web && npm run build")
        return 2
    except ValueError as exc:
        print(f"✗ Bundle: {exc}")
        return 2

    if args.json:
        print(json.dumps(stats, indent=2))
        return 0

    if args.write:
        print("BUDGET: dict[str, int] = {")
        for key, value in stats.items():
            # Bir oz yuqoriga yumaloqlaymiz — keyingi kichik o'sish
            # darvozani qizartirmasin.
            rounded = int(value * 1.15 // 1000 * 1000) + 10_000
            print(f'    "{key}": {rounded},  # o\'lchandi {human(value)}')
        print("}")
        return 0

    over: list[str] = []
    for key, limit in BUDGET.items():
        got = stats[key]
        used = got / limit * 100
        mark = "✓" if got <= limit else "✗"
        line = f"  {mark} {key:10s} {human(got):>10s} / {human(limit):>10s}  ({used:5.1f}%)"
        print(line)
        if got > limit:
            over.append(f"{key}: {human(got)} > {human(limit)} ({used:.0f}%)")

    if over:
        print()
        print("✗ Byudjet oshib ketdi:")
        for item in over:
            print(f"    - {item}")
        print()
        print("  Eng katta chunk'lar:")
        for name, size in top:
            print(f"    {size/1024:8.1f} KB  {name}")
        print()
        print("  Sabab topilsa tuzating; o'sish qasddan bo'lsa:")
        print("    python tools/check_bundle_budget.py --write")
        return 1

    print(f"✓ Bundle byudjet ichida — {len(BUDGET)} ko'rsatkich")
    return 0


if __name__ == "__main__":
    sys.exit(main())
