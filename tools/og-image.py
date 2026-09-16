#!/usr/bin/env python3
"""Ijtimoiy ulashish rasmini (Open Graph) generatsiya qiladi.

    python3 tools/og-image.py

Natija: `apps/web/public/brand/og-default.png` (1200×630).

Nega alohida skript: `brand.py` ImageMagick'ka tayanadi va u Windows'da
`C:\\Windows\\System32\\convert.exe` (disk formatlash vositasi) bilan
to'qnashadi. Bu yerda esa faqat Pillow ishlatiladi — tashqi binarsiz,
hamma platformada bir xil natija beradi.

O'lcham 1200×630 — Telegram, Twitter va Facebook qabul qiladigan eng
keng tarqalgan nisbat (1.91:1). Kichikroq rasm karta ichida cho'zilib
xunuk ko'rinadi, kattasi esa kesiladi.
"""

from __future__ import annotations

import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Pillow kerak:  pip install pillow", file=sys.stderr)
    raise SystemExit(1)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "apps" / "web" / "public" / "brand" / "og-default.png"
MARK = ROOT / "apps" / "web" / "public" / "brand" / "mark-512.png"

W, H = 1200, 630

#: Brend ranglari `mark-crest.svg` dan o'lchangan — uslub tokenlari
#: (`--rw-accent`, binafsha) ATAYLAB ishlatilmaydi: ulashish kartasi
#: brend belgisi bilan bir xil oilada ko'rinishi kerak, tanlangan
#: uslubga qarab o'zgarmaydi.
NAVY = "#102038"
BLUE = "#44A0FC"
BLUE_MID = "#1074DC"
INK_SOFT = "#4a5568"
INK_FAINT = "#8a94a6"
GROUND = "#ffffff"

TITLE = "RankWant"
TAGLINE = [
    "Sport dasturlash va informatika",
    "olimpiadasi platformasi",
]
URL = "rankwant.uz"


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    """Shriftni topadi. Windows'da Segoe UI, Linux'da DejaVu — ikkalasi
    ham lotin va kirillni qoplaydi, ya'ni o'zbekcha va ruscha matn
    bir xil ko'rinadi."""
    candidates = [
        Path("C:/Windows/Fonts") / name,
        Path("/usr/share/fonts/truetype/dejavu") / name,
        Path("/usr/share/fonts/truetype/liberation") / name,
    ]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size)
    raise SystemExit(f"shrift topilmadi: {name}")


def main() -> int:
    if not MARK.exists():
        print(f"belgi topilmadi: {MARK}", file=sys.stderr)
        print("avval `python3 tools/brand.py` ishga tushiring", file=sys.stderr)
        return 1

    img = Image.new("RGB", (W, H), GROUND)
    draw = ImageDraw.Draw(img)

    # Chapdagi ingichka brend chizig'i — rasmni "bo'sh oq" bo'lishdan
    # saqlaydi va uslub tokenlaridan mustaqil tanilish belgisi beradi.
    draw.rectangle([0, 0, 14, H], fill=NAVY)
    draw.rectangle([14, 0, 20, H], fill=BLUE)

    # Belgi — shaffof PNG, ya'ni oq fonga to'g'ridan-to'g'ri qo'yiladi.
    mark = Image.open(MARK).convert("RGBA").resize((208, 208), Image.LANCZOS)
    img.paste(mark, (86, 176), mark)

    f_title = font("segoeuib.ttf", 104)
    f_tag = font("segoeui.ttf", 34)
    f_url = font("segoeuib.ttf", 30)

    draw.text((344, 196), TITLE, font=f_title, fill=NAVY)

    y = 330
    for line in TAGLINE:
        draw.text((348, y), line, font=f_tag, fill=INK_SOFT)
        y += 50

    # Aksent chizig'i — tagline ostida, ko'k.
    draw.rectangle([348, y + 18, 468, y + 26], fill=BLUE_MID)

    draw.text((348, y + 58), URL, font=f_url, fill=INK_FAINT)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, "PNG", optimize=True)
    print(f"  ✓ {OUT.relative_to(ROOT)}  ({OUT.stat().st_size // 1024} KB, {W}×{H})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
