#!/usr/bin/env python3
"""Logotipning hamma formatini bitta SVG dan generatsiya qiladi.

    python3 tools/brand.py

Nega skript: logotip yetti joyda kerak (favicon, PWA ikonkasi, Apple touch,
xat sarlavhasi, OG rasmi, sayt sarlavhasi, README). Ularni qo'lda yasash
logotipni o'zgartirishni qimmat qiladi — kimdir bittasini unutadi va
sayt ikki xil belgi ko'rsatib turadi.

Shu skript bilan o'zgartirish narxi: `docs/brand/logo.svg` ni tahrirlash
va shu buyruqni qayta ishga tushirish.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "docs" / "brand" / "mark-choqqi.svg"
OUT = ROOT / "apps" / "web" / "public" / "brand"

#: Xat mijozlari SVG ni ko'rsatmaydi — ularga PNG kerak, va Retina uchun 2x.
#: Favicon 32, PWA 192/512, Apple touch 180 — platformalar talab qilgan
#: o'lchamlar, o'zimiz o'ylab topganimiz emas.
SIZES = (32, 96, 180, 192, 512)

#: Belgining ranglari PNG dan o'lchangan (`mark-choqqi-params.md`) va
#: o'zgartirilmaydi. Qorong'i fonda esa navy kontur fonga singib ketadi —
#: shuning uchun u yerda ochroq navy ishlatiladi. Bu YAGONA farq.
NAVY = "#102038"
NAVY_DARK = "#33507e"


def darken(svg: str) -> str:
    """Qorong'i fon uchun konturni ochadi. Qolgan ranglar tegilmaydi."""
    return svg.replace(NAVY, NAVY_DARK)


def main() -> int:
    if not SOURCE.exists():
        print(f"manba topilmadi: {SOURCE}", file=sys.stderr)
        return 1
    if shutil.which("convert") is None:
        print("ImageMagick (`convert`) topilmadi — PNG generatsiya qilinmaydi", file=sys.stderr)
        return 1

    OUT.mkdir(parents=True, exist_ok=True)
    svg = SOURCE.read_text()

    light = OUT / "mark-choqqi.svg"
    light.write_text(svg)
    (OUT / "mark-choqqi-dark.svg").write_text(darken(svg))
    print(f"  ✓ {light.relative_to(ROOT)}  (+ mark-choqqi-dark.svg)")

    for size in SIZES:
        target = OUT / f"mark-{size}.png"
        # `-background none` shaffoflikni saqlaydi. Generatsiya qilingan JPEG
        # da aynan shu yo'q edi va u qorong'i fonda oq kvadrat bo'lardi.
        subprocess.run(
            ["convert", "-background", "none", "-density", "1200",
             str(light), "-resize", f"{size}x{size}", str(target)],
            check=True, capture_output=True,
        )
        print(f"  ✓ {target.relative_to(ROOT)}")

    ico = ROOT / "apps" / "web" / "public" / "favicon.ico"
    subprocess.run(
        ["convert", "-background", "none", "-density", "1200", str(light),
         "-define", "icon:auto-resize=16,32,48", str(ico)],
        check=True, capture_output=True,
    )
    print(f"  ✓ {ico.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
