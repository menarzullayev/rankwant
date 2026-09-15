#!/usr/bin/env python3
"""Markup cookie butunligini tekshiradi.

⚠️ **Nega bu tekshiruv bor.** Markup'ni o'zgartiruvchi har bir sozlama
**to'rt joyda** takrorlanadi:

1. `MarkupPrefs` tipi (`lib/prefs.ts`) — qaysi maydonlar cookie'ga tushadi
2. `parseMarkupCookie` — cookie'dan o'qish
3. `serializeMarkupCookie` — cookie'ga yozish (klient)
4. `app/layout.tsx` dagi boot skript — SSR'dan oldin, `m.push(...)`

To'rttasi mos bo'lmasa **hidratsiya buziladi**: server bir xil markup
chizadi, klient boshqasini kutadi. Bu xato ikki marta bo'lgan
(2026-09-15, verdict va loading bilan) va u **faqat brauzerda** ko'rinadi —
`tsc` ham, eslint ham jim o'tadi.

Shuning uchun sozlama qo'shilsa, to'rttasi birga yangilanishi shart.
Bu tekshiruv shuni majburlaydi.
"""
from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PREFS = ROOT / "apps/web/src/lib/prefs.ts"
LAYOUT = ROOT / "apps/web/src/app/layout.tsx"

#: `export type MarkupPrefs = Pick<AppearancePrefs, "a" | "b" | "c">;`
PICK_RE = re.compile(
    r"export type MarkupPrefs\s*=\s*Pick<\s*AppearancePrefs\s*,(.*?)>;", re.S
)
FIELD_RE = re.compile(r'"([a-zA-Z]+)"')

#: `if (k === "v") out.verdictStyle = ...`
PARSE_RE = re.compile(r'k === "([a-z]+)"\)\s*out\.([a-zA-Z]+)\s*=')
#: `if (a.verdictStyle && ...) parts.push(`v=${a.verdictStyle}`);`
SERIALIZE_RE = re.compile(r'parts\.push\(`([a-z])=')
#: `if (...) m.push("v="+a.verdictStyle);`
BOOT_RE = re.compile(r'm\.push\("([a-z])="\+a\.([a-zA-Z]+)\)')


def fail(msg: str) -> None:
    print(f"  ✕ {msg}")


def main() -> int:
    for p in (PREFS, LAYOUT):
        if not p.exists():
            print(f"Fayl topilmadi: {p}")
            return 1

    prefs_src = PREFS.read_text(encoding="utf-8")
    layout_src = LAYOUT.read_text(encoding="utf-8")

    problems = 0

    # ── 1. Tip ──────────────────────────────────────────────────────────
    m = PICK_RE.search(prefs_src)
    if not m:
        fail("`MarkupPrefs` topilmadi (`lib/prefs.ts`)")
        return 1
    fields = FIELD_RE.findall(m.group(1))
    if not fields:
        fail("`MarkupPrefs` bo'sh — hech qanday sozlama cookie'ga tushmaydi")
        return 1

    # ── 2. parseMarkupCookie ────────────────────────────────────────────
    parse_block = prefs_src[
        prefs_src.find("export function parseMarkupCookie") : prefs_src.find(
            "export function serializeMarkupCookie"
        )
    ]
    parse_pairs = PARSE_RE.findall(parse_block)
    parse_by_field = {f: code for code, f in parse_pairs}

    # ── 3. serializeMarkupCookie ────────────────────────────────────────
    ser_block = prefs_src[
        prefs_src.find("export function serializeMarkupCookie") : prefs_src.find(
            "export function writeMarkupCookie"
        )
        if "export function writeMarkupCookie" in prefs_src
        else len(prefs_src)
    ]
    ser_codes = SERIALIZE_RE.findall(ser_block)

    # ── 4. Boot skript ──────────────────────────────────────────────────
    boot_pairs = BOOT_RE.findall(layout_src)
    boot_by_field = {f: code for code, f in boot_pairs}

    # ── Taqqoslash ──────────────────────────────────────────────────────
    for field in fields:
        if field not in parse_by_field:
            fail(f"`{field}` — `MarkupPrefs` da bor, `parseMarkupCookie` da YO'Q")
            problems += 1
        if field not in boot_by_field:
            fail(
                f"`{field}` — `MarkupPrefs` da bor, boot skriptda YO'Q "
                "(SSR bilan mos kelmaydi → hidratsiya xatosi)"
            )
            problems += 1
        if field in parse_by_field and field in boot_by_field:
            if parse_by_field[field] != boot_by_field[field]:
                fail(
                    f"`{field}` — kalit kodi mos emas: "
                    f"parse `{parse_by_field[field]}` vs boot `{boot_by_field[field]}`"
                )
                problems += 1

    # Har bir parse kodi serialize'da ham bo'lishi shart.
    parse_codes = {c for c, _ in parse_pairs}
    for code in sorted(parse_codes):
        if code not in ser_codes:
            fail(f"`{code}` — `parseMarkupCookie` da bor, `serializeMarkupCookie` da YO'Q")
            problems += 1

    # Ortiqcha kodlar: serialize'da bor, tipda yo'q.
    for code in sorted(set(ser_codes) - parse_codes):
        fail(f"`{code}` — `serializeMarkupCookie` da bor, `parseMarkupCookie` da YO'Q")
        problems += 1

    if problems:
        print(
            f"\nJami: {problems} muammo — {len(fields)} markup sozlamasi, "
            f"4 joy tekshirildi."
        )
        return 1

    print(
        f"Tekshirildi: {len(fields)} markup sozlamasi × 4 joy "
        f"({', '.join(fields)})\nMarkup cookie butun ✓"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
