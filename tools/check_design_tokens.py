#!/usr/bin/env python3
"""Dizayn token intizomini tekshiradi — faqat HAQIQIY nomuvofiqliklar.

Nega kerak: `globals.css` da 638 ta `--rw-*` token bor, ya'ni «17 xil
border-radius, 12 xil ko'k rang» muammosi tuzilma darajasida yechilgan.
Lekin token tizimi faqat **ishlatilganda** ishlaydi — komponent ichida
yozilgan xom `#1f2328` ham, `text-[10px]` ham token qatlamini chetlab
o'tadi va keyingi palitra o'zgarishida ko'rinmasdan qolib ketadi.

⚠️ **Nima tekshirilmaydi va nega.** Tailwind ixtiyoriy qiymatining
hammasi xato emas — 2026-09-24 da o'lchandi, 50 dan ortiq `[...]`
uchraydi va ular uch guruhga bo'linadi:

  1. **To'g'ri naqsh** — `size-[1.05em]`, `fill-[var(--rw-faint)]`,
     `w-[var(--input-width)]`. `em` shriftga nisbatan, `var()` esa
     tokenga bog'langan. Bularni jazolash tizimni yaxshilamaydi.
  2. **O'lchangan qaror** — `w-[260px]` / `w-[86px]` sidebar kengligi
     (`CLAUDE.md` → `mobile_header_fits_narrow_screen`), `max-w-[8rem]`
     nom qirqish chegarasi. Bular `docs/research/` dagi o'lchovdan
     chiqqan; token qilish o'sha o'lchovni uzib qo'yadi.
  3. **Nomalum** — quyida qidiriladigan ikkita tor sinf.

Ya'ni bu skript **tor**: faqat (a) xom hex rang va (b) px asosidagi
shrift o'lchamini qidiradi. Kengroq qoida yolg'on signal berardi va
o'chirib qo'yilardi — o'shanda haqiqiy muammo ham o'tib ketardi.

Chiqish kodi: 0 — toza, 1 — nomuvofiqlik topildi.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# Chiqish quvurga yo'naltirilganda Windows uni `cp1252` deb yozadi va
# birinchi `✓` belgisida qulaydi — sabab va o'lchov `tools/_console.py` da.
import _console

_console.force_utf8()

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "apps/web/src"

# (a) Xom hex rang — oq ro'yxatdan tashqari.
HEX_RE = re.compile(r"#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b")
# (b) px asosidagi shrift o'lchami — `text-[10px]`. Shrift pog'onasi
#     `--rw-text-xs` kabi tokenga bog'lanishi kerak: px da qotirilsa
#     foydalanuvchi shrift kattaligi sozlamasi ta'sir qilmaydi.
TEXT_PX_RE = re.compile(r"\btext-\[[0-9.]+px\]")

# Fayl → istisno naqshlari. Har biri sababi bilan.
HEX_ALLOWED: dict[str, str] = {
    "features/account/components/ProviderMark.tsx": (
        "Brend belgilari: Google to'rt rangi (`#4285F4` ko'k, `#34A853` yashil, "
        "`#FBBC05` sariq, `#EA4335` qizil). Tashqi logotip — tokenga bog'lash "
        "uni noto'g'ri ko'rsatadi."
    ),
    "features/account/components/AuthForm.tsx": (
        "Provider tugmalari: Google `#1f1f1f` matni va oq foni, GitHub "
        "`#1f2328`, Telegram `#1a77a4` (brend ko'ki `#229ED9` dan "
        "quyuqlashtirilgan — oq matn 4.95:1 kontrast beradi)."
    ),
    "layout/LocaleFlag.tsx": (
        "Qoraqalpoq bayrog'i (`#1eb53a` yashil, `#f7c200` sariq, `#0099b5` "
        "ko'k, `#ce1126` qizil) — rasmiy davlat ramzi. Token qilish uni "
        "palitra o'zgarganda buzib qo'yardi."
    ),
}

# Butun papkani qamrab oluvchi istisno — OG rasm generatori.
# Bu fayllar `ImageResponse` (Satori) ichida chiziladi: CSS o'zgaruvchisi
# mavjud emas, chunki chiqish — PNG. Rang shu yerda qotirilishi shart.
HEX_DIR_ALLOWED = {
    "app/(site)/users/[username]/opengraph-image.tsx": (
        "OG rasm (Satori/PNG) — CSS o'zgaruvchisi mavjud emas, rang qotirilgan."
    ),
    "app/(site)/contests/[slug]/opengraph-image.tsx": (
        "OG rasm (Satori/PNG) — CSS o'zgaruvchisi mavjud emas."
    ),
    "app/(site)/problems/[slug]/opengraph-image.tsx": (
        "OG rasm (Satori/PNG) — CSS o'zgaruvchisi mavjud emas."
    ),
}

# Satr darajasidagi istisno — foydalanuvchi MA'LUMOTI yoki misol matn.
HEX_LINE_ALLOWED = (
    'color: "#4f46e5"',      # `type="color"` maydonining boshlang'ich qiymati
    'color: "#fff"',         # foydalanuvchi tanlagan fon ustidagi matn
    'placeholder="#5B8CFF"',  # HEX maydonining namuna matni (atribut, rang emas)
)

# px matn o'lchami istisnosi — `fill-[var(...)]` bilan birga SVG ichida
# ishlatiladigan kichik yorliqlar (grafik o'qlari). Ular SVG viewBox
# koordinatasida yashaydi, sahifa shrift pog'onasiga bog'lanmaydi.
TEXT_PX_ALLOWED_FILES = {
    "features/profile/components/RatingChart.tsx",
    "features/profile/components/ActivityHeatmap.tsx",
    "features/profile/components/SolvedOverview.tsx",
}


def scan() -> tuple[list[tuple[str, int, str]], list[tuple[str, int, str]]]:
    hex_hits: list[tuple[str, int, str]] = []
    px_hits: list[tuple[str, int, str]] = []

    for path in sorted(SRC.rglob("*.tsx")):
        rel = path.relative_to(SRC).as_posix()
        for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            stripped = line.strip()
            # Izoh qatorlari — hujjat, kod emas.
            if stripped.startswith(("*", "//", "/*")):
                continue

            if rel in HEX_ALLOWED or rel in HEX_DIR_ALLOWED:
                continue
            if any(a in line for a in HEX_LINE_ALLOWED):
                continue
            for m in HEX_RE.finditer(line):
                hex_hits.append((rel, i, m.group(0)))

            if rel not in TEXT_PX_ALLOWED_FILES:
                for m in TEXT_PX_RE.finditer(line):
                    px_hits.append((rel, i, m.group(0)))

    return hex_hits, px_hits


def main() -> int:
    hex_hits, px_hits = scan()

    print(f"Skanerlandi: {SRC.relative_to(ROOT)} — {len(list(SRC.rglob('*.tsx')))} fayl")
    print(f"Oq ro'yxat: {len(HEX_ALLOWED)} fayl (brend) · "
          f"{len(HEX_DIR_ALLOWED)} fayl (OG rasm) · "
          f"{len(HEX_LINE_ALLOWED)} satr (foydalanuvchi rangi) · "
          f"{len(TEXT_PX_ALLOWED_FILES)} fayl (SVG o'qi)")

    if not hex_hits and not px_hits:
        print("\n✓ Xom rang ham, px shrift ham yo'q — qatlam token orqali ishlaydi")
        return 0

    if hex_hits:
        print(f"\n✗ xom hex rang: {len(hex_hits)} ta")
        for rel, line, token in hex_hits:
            print(f"  {rel}:{line}  {token}")
    if px_hits:
        print(f"\n✗ px shrift o'lchami: {len(px_hits)} ta")
        for rel, line, token in px_hits:
            print(f"  {rel}:{line}  {token}")

    print(
        "\nTuzatish: rangni `--rw-*` tokenga, shriftni `text-theme-xs` kabi\n"
        "pog'onaga o'tkazish. Agar qiymat HAQIQATAN kerak bo'lsa — sababini\n"
        "shu fayldagi istisno ro'yxatiga YOZIB qo'shish kerak (jim qoldirish emas)."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
