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
SOURCE = ROOT / "docs" / "brand" / "mark-crest.svg"
OUT = ROOT / "apps" / "web" / "public" / "brand"

#: Xat mijozlari SVG ni ko'rsatmaydi — ularga PNG kerak, va Retina uchun 2x.
#: Favicon 32, PWA 192/512, Apple touch 180 — platformalar talab qilgan
#: o'lchamlar, o'zimiz o'ylab topganimiz emas.
SIZES = (32, 96, 180, 192, 512)

#: Belgining ranglari PNG dan o'lchangan (`mark-crest-params.md`) va
#: o'zgartirilmaydi. Qorong'i fonda esa navy kontur fonga singib ketadi —
#: shuning uchun u yerda ochroq navy ishlatiladi. Bu YAGONA farq.
NAVY = "#102038"
NAVY_DARK = "#33507e"


def bimi(svg: str) -> str:
    """BIMI uchun SVG Tiny PS profiliga keltiradi.

    BIMI (pochta ro'yxatidagi avatar) oddiy SVG ni qabul qilmaydi: profil
    qat'iy — kvadrat `viewBox`, `baseProfile="tiny-ps"`, birinchi bola
    sifatida `<title>`, tashqi havola/skript/animatsiya yo'q, 32 KB gacha.
    Bizning belgimiz allaqachon faqat `fill` ishlatadi, ya'ni o'zgarish
    sarlavhada.
    """
    body = svg
    for teg in ("title", "desc", "!--"):
        while f"<{teg}" in body:
            boshi = body.index(f"<{teg}")
            oxiri = body.index("-->" if teg == "!--" else f"</{teg}>", boshi)
            oxiri += 3 if teg == "!--" else len(f"</{teg}>")
            body = body[:boshi] + body[oxiri:]
    boshi = body.index(">", body.index("<svg")) + 1
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" version="1.2" baseProfile="tiny-ps"'
        ' viewBox="0 0 1024 1024">\n  <title>RankWant</title>' + body[boshi:]
    )


def darken(svg: str) -> str:
    """Qorong'i fon uchun konturni ochadi. Qolgan ranglar tegilmaydi."""
    return svg.replace(NAVY, NAVY_DARK)


def find_magick() -> str | None:
    """Haqiqiy ImageMagick binarini topadi, `shutil.which` emas.

    `shutil.which("convert")` Windows'da ALDANADI: u
    `C:\\Windows\\System32\\convert.exe` ni topadi — bu diskni FAT dan
    NTFS ga o'giradigan TIZIM vositasi, ImageMagick emas. Uni chaqirish
    PNG o'rniga xato beradi (va niyat tushunilmasa, diskka tegib
    ketishi mumkin). Shuning uchun nom emas, `-version` chiqishi
    tekshiriladi.
    """
    for name in ("magick", "convert"):
        path = shutil.which(name)
        if not path:
            continue
        try:
            probe = subprocess.run(
                [path, "-version"], capture_output=True, text=True, timeout=10
            )
        except (OSError, subprocess.SubprocessError):
            continue
        if "ImageMagick" in (probe.stdout or "") + (probe.stderr or ""):
            return path
    return None


def main() -> int:
    if not SOURCE.exists():
        print(f"manba topilmadi: {SOURCE}", file=sys.stderr)
        return 1
    magick = find_magick()
    if magick is None:
        print("ImageMagick topilmadi — PNG generatsiya qilinmaydi", file=sys.stderr)
        print("  Windows: winget install ImageMagick.ImageMagick", file=sys.stderr)
        return 1

    OUT.mkdir(parents=True, exist_ok=True)
    svg = SOURCE.read_text()

    light = OUT / "mark-crest.svg"
    light.write_text(svg)
    (OUT / "mark-crest-dark.svg").write_text(darken(svg))
    print(f"  ✓ {light.relative_to(ROOT)}  (+ mark-crest-dark.svg)")

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

    tiny = OUT / "bimi.svg"
    tiny.write_text(bimi(svg))
    print(f"  ✓ {tiny.relative_to(ROOT)}  ({len(tiny.read_text())} bayt, chegara 32 KB)")

    ico = ROOT / "apps" / "web" / "public" / "favicon.ico"
    subprocess.run(
        [magick, "-background", "none", "-density", "1200", str(light),
         "-define", "icon:auto-resize=16,32,48", str(ico)],
        check=True, capture_output=True,
    )
    print(f"  ✓ {ico.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
