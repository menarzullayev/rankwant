#!/usr/bin/env python3
"""Matn ranglari WCAG AA (4.5:1) dan o'tishini tekshiradi.

`globals.css` da 12 uslub bor, ularning oltitasida qorong'u varianti ham —
jami 18 palitra. Har birida to'rt pog'onali matn zinapoyasi (`--rw-text`,
`--rw-text-2`, `--rw-muted`, `--rw-faint`) va bir nechta sirt bor. Ko'z
bilan tekshirib bo'lmaydi: o'lchanганda 18 palitradan 17 tasi yiqilgan,
`--rw-faint` esa 161 joyda matn tashiydi.

Nozik joyi — QATLAM TARTIBI. `--rw-hover` panel ustida turadi, fon
ustida emas; shaffof panel esa gradient VA `body::before` dog'lari
ustida. Bu tartib buzilsa o'lchov yolg'on natija beradi: shaffof
`hover` ni yorug' gradient ustiga qo'yish hech qanday matn o'ta
olmaydigan fon yasaydi.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSS = ROOT / "apps/web/src/app/globals.css"

AA = 4.5
#: WCAG 2.4.11 — fokus ko'rsatkichi yon rangga nisbatan shuncha bo'lishi
#: kerak. Matndan past, chunki bu shakl, o'qiladigan matn emas.
FOCUS_MIN = 3.0
#: `globals.css` da klaviatura halqasi shu token bilan chiziladi.
FOCUS_TOKEN = "--rw-accent-ink"
TIERS = ("--rw-text", "--rw-text-2", "--rw-muted", "--rw-faint")
#: Panel darajasidagi sirtlar — fon ustiga tushadi.
PANELS = ("--rw-surface", "--rw-surface-2", "--rw-chrome")
#: Panel ICHIDAGI sirtlar — panel ustiga tushadi.
INNER = ("--rw-chip", "--rw-field", "--rw-hover")

Color = tuple[int, int, int, float]


def parse(value: str) -> Color | None:
    value = value.strip()
    if value.startswith("#"):
        digits = value[1:]
        if len(digits) == 3:
            digits = "".join(c * 2 for c in digits)
        return (int(digits[0:2], 16), int(digits[2:4], 16), int(digits[4:6], 16), 1.0)
    match = re.match(r"rgba?\(([^)]+)\)$", value)
    if not match:
        return None
    parts = [p.strip() for p in match.group(1).replace("/", ",").split(",")]
    alpha = float(parts[3]) if len(parts) > 3 else 1.0
    return (int(float(parts[0])), int(float(parts[1])), int(float(parts[2])), alpha)


def stops(value: str) -> list[Color]:
    """Gradientni tashkil etuvchi ranglarga yoyadi; bitta rang bo'lsa — o'zi."""
    solid = parse(value)
    if solid:
        return [solid]
    found = re.findall(r"#[0-9a-fA-F]{3,8}|rgba?\([^)]*\)", value)
    return [c for c in (parse(f) for f in found) if c]


def over(top: Color, bottom: Color) -> Color:
    alpha = top[3]
    return (
        round(top[0] * alpha + bottom[0] * (1 - alpha)),
        round(top[1] * alpha + bottom[1] * (1 - alpha)),
        round(top[2] * alpha + bottom[2] * (1 - alpha)),
        1.0,
    )


def luminance(color: Color) -> float:
    def channel(value: int) -> float:
        v = value / 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4

    return 0.2126 * channel(color[0]) + 0.7152 * channel(color[1]) + 0.0722 * channel(color[2])


def contrast(fg: Color, bg: Color) -> float:
    a, b = luminance(fg), luminance(bg)
    return (max(a, b) + 0.05) / (min(a, b) + 0.05)


def read_blobs(css: str) -> dict[str, list[Color]]:
    """`body::before` dagi rangli dog'lar — panel ostidagi haqiqiy fon.

    Qiymat CSS dan o'qiladi: qo'lda ko'chirilgan nusxa fon o'zgarganda
    eskirib qoladi va tekshiruv yolg'on «o'tdi» beradi.
    """
    blobs: dict[str, list[Color]] = {}
    for match in re.finditer(r"\[data-style=\"(\w+)\"\][^{]*body::before\s*\{([^}]*)\}", css):
        found = re.findall(r"radial-gradient\([^)]*?(rgba\([^)]*\))", match.group(2))
        colors = [c for c in (parse(f) for f in found) if c]
        if colors:
            blobs[match.group(1)] = colors
    return blobs


def backgrounds(tokens: dict[str, str], blobs: list[Color]) -> list[Color]:
    ground = stops(tokens["--rw-ground"])
    # Dog'lar qarama-qarshi burchakda — har biri fon ustiga ALOHIDA tushadi.
    ground += [over(blob, base) for blob in blobs for base in list(ground)]

    def layer(keys: tuple[str, ...], unders: list[Color]) -> list[Color]:
        out: list[Color] = []
        for key in keys:
            for color in stops(tokens.get(key, "")):
                out += [over(color, u) for u in unders] if color[3] < 1 else [color]
        return out

    panels = layer(PANELS, ground)
    return ground + panels + layer(INNER, panels or ground)


def main() -> int:
    css = CSS.read_text(encoding="utf-8")
    blobs = read_blobs(css)
    failures: list[str] = []
    checked = 0

    for match in re.finditer(r"(^[^{}\n][^{}]*)\{([^}]*)\}", css, re.M):
        selector, body = match.group(1).strip(), match.group(2)
        if "--rw-faint" not in body or "--rw-ground" not in body:
            continue
        name = re.sub(r"\s+", " ", re.sub(r"/\*.*?\*/", "", selector, flags=re.S).strip())
        tokens = dict(re.findall(r"(--rw-[\w-]+)\s*:\s*([^;]+);", body))
        style_match = re.search(r'data-style="(\w+)"', name)
        style = style_match.group(1) if style_match else "dashboard"
        backs = backgrounds(tokens, blobs.get(style, []))

        focus = parse(tokens.get(FOCUS_TOKEN, ""))
        if focus is not None:
            checked += 1

            def ring(bg: Color, fg: Color = focus) -> float:
                return contrast(over(fg, bg) if fg[3] < 1 else fg, bg)

            ratio = ring(min(backs, key=ring))
            if ratio < FOCUS_MIN:
                failures.append(
                    f"{name}  fokus halqasi ({FOCUS_TOKEN}): {ratio:.2f}:1, kerak {FOCUS_MIN}"
                )

        for tier in TIERS:
            color = parse(tokens[tier])
            if color is None:
                failures.append(f"{name}  {tier}: rang o'qilmadi ({tokens[tier].strip()})")
                continue
            checked += 1

            def against(bg: Color, fg: Color = color) -> float:
                return contrast(over(fg, bg) if fg[3] < 1 else fg, bg)

            worst_bg = min(backs, key=against)
            ratio = against(worst_bg)
            if ratio < AA:
                failures.append(
                    f"{name}  {tier}: {tokens[tier].strip()} → {ratio:.2f}:1 "
                    f"(fon #{worst_bg[0]:02x}{worst_bg[1]:02x}{worst_bg[2]:02x}), kerak {AA}"
                )

    if failures:
        print(f"Kontrast AA dan o'tmadi ({len(failures)} ta):", file=sys.stderr)
        for line in failures:
            print(f"  {line}", file=sys.stderr)
        return 1

    print(f"Kontrast: {checked} ta matn rangi AA ({AA}:1) dan o'tdi")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
