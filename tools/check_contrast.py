#!/usr/bin/env python3
"""Matn ranglari WCAG AA (4.5:1) dan o'tishini tekshiradi.

`globals.css` da 12 uslub bor, ularning oltitasida qorong'u varianti ham —
jami 18 palitra. Har birida to'rt pog'onali matn zinapoyasi (`--rw-text`,
`--rw-text-2`, `--rw-muted`, `--rw-faint`) va bir nechta sirt bor. Ko'z
bilan tekshirib bo'lmaydi: o'lchanganda 18 palitradan 17 tasi yiqilgan,
`--rw-faint` esa 161 joyda matn tashiydi.

Shuningdek TUGMA juftligi tekshiriladi: `--rw-accent-fg` matni
`--rw-accent` foni ustida. Bu yerda ko'r nuqta bor edi — 2026-09-13 da
Lighthouse aynan shu yerda yiqilgan (`clay`: 4.23:1), tekshiruv esa
«o'tdi» deb turgan edi, chunki u faqat matn zinapoyalari, reyting
ranglari, fokus halqasi va maydon chegarasini ko'rardi. O'lchangan
oqibat: to'rtta uslubda olti juftlik yiqilgan (clay, dashboard,
flat, neu), shundan ikkitasi faqat dark rejimda — `flat.dark` va
`dashboard.dark` `--rw-accent-fg` ni e'lon qilmasdi, ya'ni oq matn
light blokdan meros bo'lib qolgan edi.

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
#: WCAG 1.4.11 forma maydonining chegarasiga ham shuncha talab qiladi:
#: maydon qayerdaligi ko'rinmasa, unga yozib bo'lmaydi. O'lchangan
#: oqibat: `material`, `neu` va `clay` da fon karta bilan bir xil va
#: chegara kengligi 0 edi — maydon umuman ko'rinmasdi.
FIELD_MIN = 3.0
#: Chegara rangi shu ulushda matn rangidan hosil qilinadi (`globals.css`).
FIELD_MIX = 0.65

#: Ajratgich — karta chegarasidan ALOHIDA token. `--rw-line` `clay` va `neu`
#: da ataylab shaffof, ya'ni u bilan chizilgan ajratgich ko'rinmas qolardi.
#: Shakl uchun WCAG 1.4.11 3:1 talab qiladi (matn uchun 4.5 emas).
DIVIDER_TOKEN = "--rw-divider"
DIVIDER_MIN = 3.0

#: `globals.css` da klaviatura halqasi shu token bilan chiziladi.
FOCUS_TOKEN = "--rw-accent-ink"
#: Tugma juftligi: (matn, fon). `.rw-accent-bg` shu ikkalasidan quriladi va
#: accent `--rw-accent-ink` dan farq qiladi — u tugma FONI, bu matn/fokus.
#: Gradient ham bo'lishi mumkin (`skeu`), shuning uchun har bir pog'ona
#: alohida o'lchanadi: matn eng yorug' pog'onada eng kam kontrast beradi.
ACCENT_PAIR = ("--rw-accent-fg", "--rw-accent")
#: Accent MATN sifatida. `.rw-accent-ink` havola rangida (fon/sirt ustida),
#: `.rw-accent-soft` esa chip fonida ishlatiladi. 2026-09-14 gacha bu
#: juftlik TEKSHIRILMAGAN edi: `FOCUS_TOKEN` xuddi shu tokenni ishlatadi,
#: lekin u klaviatura halqasi uchun (3:1), matn uchun emas. O'lchangan
#: oqibat: `dashboard` da uch joyda AA dan yiqilgan — ground 4.27:1,
#: surface 4.46:1, soft 4.02:1 — va CI buni ko'rmagan.
ACCENT_INK = "--rw-accent-ink"
#: Holat ranglari — matn sifatida ham, nishon sifatida ham ishlatiladi.
SEMANTIC = ("ok", "warn", "bad")
ACCENT_SOFT = "--rw-accent-soft"
TIERS = ("--rw-text", "--rw-text-2", "--rw-muted", "--rw-faint")
#: Unvon ranglari — ism shu rangda yoziladi (ADR-0018), ya'ni bu ham matn.
RANKS = tuple(f"--rw-rank-{i}" for i in range(1, 10))
#: Qiyinlik darajasi — `.level-*` shu ranglarda yoziladi. Reyting kabi bu ham
#: MATN: `DifficultyBadge` uni `--rw-chip` ustiga qo'yadi, ro'yxatlarda esa
#: to'g'ridan-to'g'ri sirt ustida turadi. 2026-09-13 gacha tekshirilmagan edi
#: va o'lchanganda 85 juftlikdan 50 tasi yiqilardi.
LEVELS = tuple(f"--rw-level-{i}" for i in range(1, 6))
#: Oraliq pog'onalar `globals.css` da ikki qo'shni rangning oklab aralashmasi
#: sifatida yasaladi. Aralashmaning yorqinligi chetlari ORASIDA bo'ladi, ya'ni
#: ikkala uchi o'tsa ham o'zi yiqilishi mumkin (biri fondan yorug', ikkinchisi
#: quyuq bo'lsa) — shuning uchun alohida o'lchanadi.
LEVEL_MIXES = ((".level-basic", 1, 2), (".level-upper", 2, 3))
#: Panel darajasidagi sirtlar — fon ustiga tushadi.
PANELS = ("--rw-surface", "--rw-surface-2", "--rw-chrome")
#: Panel ICHIDAGI sirtlar — panel ustiga tushadi.
INNER = ("--rw-chip", "--rw-field", "--rw-hover")
#: Updates turlari — `.rw-kind-*` nishoni (10 tur, qaror 11).
#:
#: Bu juftliklar palitradan MUSTAQIL: nishon o'z fonini o'zi bilan olib
#: yuradi, ya'ni `ink` ↔ `soft` kontrasti faqat shu ikki qiymatga bog'liq.
#: Shuning uchun ular bitta blokda e'lon qilinadi va bir marta o'lchanadi.
KINDS = (
    "new", "improved", "fixed", "performance", "security",
    "design", "content", "infrastructure", "breaking", "deprecated",
)

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


def srgb_linear(v: float) -> float:
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def linear_srgb(v: float) -> float:
    return v * 12.92 if v <= 0.0031308 else 1.055 * (v ** (1 / 2.4)) - 0.055


def oklab(color: Color) -> tuple[float, float, float]:
    """sRGB -> Oklab. CSS `color-mix(in oklab, ...)` shu fazoda aralashtiradi."""
    r, g, b = (srgb_linear(color[i] / 255) for i in range(3))
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l_, m_, s_ = l ** (1 / 3), m ** (1 / 3), s ** (1 / 3)
    return (
        0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_,
        1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_,
        0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_,
    )


def from_oklab(lab: tuple[float, float, float]) -> Color:
    L, a, b = lab
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l_ ** 3, m_ ** 3, s_ ** 3
    lin = (
        4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
        -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
        -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s,
    )
    return tuple(  # type: ignore[return-value]
        round(max(0.0, min(1.0, linear_srgb(v))) * 255) for v in lin
    ) + (1.0,)


def mix_oklab(first: Color, second: Color) -> Color:
    """`color-mix(in oklab, first, second)` — teng ulushda."""
    a, b = oklab(first), oklab(second)
    return from_oklab(tuple((a[i] + b[i]) / 2 for i in range(3)))  # type: ignore[arg-type]


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


def field_lines(css: str) -> dict[str, str]:
    """Chegarasini o'zi belgilagan uslublar — qolganlari hosil qilinadi."""
    return dict(
        re.findall(r'\[data-style="(\w+)"\]\s*\{[^}]*?--rw-field-line:\s*([^;]+);', css, re.S)
    )


def style_tokens(css: str) -> dict[tuple[str, str], dict[str, str]]:
    """Uslub tokenlarini KASKAD bo'yicha yechadi: {(uslub, rejim): tokenlar}.

    `[data-style=x].dark` faqat o'zi e'lon qilgan tokenni almashtiradi,
    qolganini `[data-style=x]` dan oladi. Blokni alohida o'qish yolg'on
    «o'tdi» beradi: `flat.dark` `--rw-accent`/`--rw-accent-fg` ni e'lon
    qilmasdi, ya'ni light blokdan meros bo'lib 3.82:1 bergan edi. Faqat
    shu sababli bu tekshiruv uni ko'rmasdi.
    """
    out: dict[tuple[str, str], dict[str, str]] = {}
    for match in re.finditer(r'\[data-style="(\w+)"\](\.dark)?\s*\{([^}]*)\}', css, re.S):
        style, dark, body = match.group(1), bool(match.group(2)), match.group(3)
        tokens = dict(re.findall(r"(--rw-[\w-]+)\s*:\s*([^;]+);", body))
        if not tokens:
            continue
        out.setdefault((style, "dark" if dark else "light"), {}).update(tokens)

    for key in list(out):
        style, mode = key
        if mode == "dark":
            out[key] = {**out.get((style, "light"), {}), **out[key]}
    return out


def kind_blocks(css: str) -> dict[str, dict[str, str]]:
    """`--rw-kind-*` bloklarini rejim bo'yicha o'qiydi.

    Izohlar AVVAL olib tashlanadi: light blok izohida `.dark` so'zi bor
    (nega tartib muhim emasligi tushuntirilgan), ya'ni izohsiz o'qilsa
    yorug' blok qorong'i deb hisoblanardi va ikkala rejim bir xil
    o'lchanib, yorug'dagi nuqson ko'rinmay qolardi.

    Blokni ATAYLAB alohida o'qiymiz: `style_tokens()` faqat
    `[data-style="nom"]` shaklini ko'radi, bu blok esa `[data-style]`
    (qiymatsiz). Selektorni shu yerda takrorlamasak tekshiruv jimgina
    o'tib ketardi.
    """
    clean = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    out: dict[str, dict[str, str]] = {}
    for match in re.finditer(r"([^{}]*)\{([^{}]*--rw-kind-new-ink[^{}]*)\}", clean):
        selector = re.sub(r"\s+", " ", match.group(1).strip())
        mode = "dark" if ".dark" in selector else "light"
        out.setdefault(mode, {}).update(
            dict(re.findall(r"(--rw-kind-[\w-]+)\s*:\s*([^;]+);", match.group(2)))
        )
    return out


def check_kinds(css: str) -> list[str]:
    """Har turning matni o'z nishon fonida AA dan o'tishini tekshiradi.

    `soft` — nishonning O'Z foni, palitra sirti emas; shuning uchun bu
    yerda eng yomon fonni qidirish kerak emas. Lekin token umuman
    o'qilmasa (yo'q, `transparent`, buzuq hex) — bu XATO, o'tkazib
    yuborilmaydi.
    """
    problems: list[str] = []
    blocks = kind_blocks(css)
    if not blocks:
        return ["--rw-kind-* bloklari topilmadi — tekshiruv ko'r bo'lib qolgan"]

    for mode in ("light", "dark"):
        tokens = blocks.get(mode)
        if not tokens:
            problems.append(f"kind.{mode}: blok yo'q")
            continue
        for kind in KINDS:
            ink_raw = tokens.get(f"--rw-kind-{kind}-ink", "").strip()
            soft_raw = tokens.get(f"--rw-kind-{kind}-soft", "").strip()
            ink, soft = parse(ink_raw), parse(soft_raw)
            if ink is None:
                problems.append(
                    f"kind.{mode}.{kind}: ink o'qilmadi ({ink_raw or 'token yo`q'})"
                )
                continue
            if soft is None:
                problems.append(
                    f"kind.{mode}.{kind}: soft o'qilmadi ({soft_raw or 'token yo`q'})"
                )
                continue
            ratio = contrast(ink, soft)
            if ratio < AA:
                problems.append(
                    f"kind.{mode}.{kind}: {ink_raw} ustida {soft_raw} "
                    f"→ {ratio:.2f}:1, kerak {AA}"
                )
    return problems


def check_semantic(css: str) -> list[str]:
    """`--rw-ok/warn/bad-ink` o'z `-soft` foni ustida o'tishini tekshiradi.

    ⚠️ **Shartnoma: bu tokenlar NISHON uchun.** `ink` faqat o'z `soft`
    foni ustida ishlatiladi — xuddi `--rw-kind-*` kabi. Ilovada yagona
    ishlatish ham shunday (`certificates/[id]`: `rw-ok-soft` + `rw-ok-ink`).

    2026-09-14 da qo'shildi: bu uchlik umuman tekshirilmagan edi va
    o'lchanganda **14 juftlik o'z soft fonida ham** yiqilardi
    (masalan `clay`: ok 2.96:1, warn 2.72:1) — ya'ni nishon matni
    hech qachon AA dan o'tmagan.

    Lighthouse orqali topildi: panel ularni SIRT ustida ishlatgan
    (`clay` da 2.87:1). Bu tokenlarning xatosi emas — ishlatish xatosi.
    Shuning uchun bu yerda sirt tekshirilmaydi: u shartnomaga kirmaydi
    va ba'zi palitralarda umuman bajarib bo'lmaydi (sirtlar bir vaqtda
    ham juda yorug', ham juda qorong'i).
    """
    problems: list[str] = []
    blobs = read_blobs(css)
    for (style, mode), tokens in sorted(style_tokens(css).items()):
        if "--rw-ground" not in tokens:
            continue
        label = f"{style}{'.dark' if mode == 'dark' else ''}"
        grounds = backgrounds(tokens, blobs.get(style, []))
        if not grounds:
            problems.append(f"{label}  fonlar o'qilmadi")
            continue
        base = grounds[0]
        for state in SEMANTIC:
            ink_raw = tokens.get(f"--rw-{state}-ink", "").strip()
            soft_raw = tokens.get(f"--rw-{state}-soft", "").strip()
            ink, soft = parse(ink_raw), parse(soft_raw)
            if ink is None:
                problems.append(
                    f"{label}  --rw-{state}-ink o'qilmadi ({ink_raw or 'token yo`q'})"
                )
                continue
            # `soft` gradient ham bo'lishi mumkin (`skeu`) — u holda eng
            # yomon pog'ona olinadi, xuddi tugma juftligidagi kabi.
            soft_stops = stops(soft_raw)
            if not soft_stops:
                problems.append(
                    f"{label}  --rw-{state}-soft o'qilmadi ({soft_raw or 'token yo`q'})"
                )
                continue
            worst_bg = min(
                (over(s, base) if s[3] < 1 else s for s in soft_stops),
                key=lambda bg: contrast(over(ink, bg) if ink[3] < 1 else ink, bg),
            )
            ratio = contrast(over(ink, worst_bg) if ink[3] < 1 else ink, worst_bg)
            if ratio < AA:
                problems.append(
                    f"{label}  {state} nishon matni ({state}-ink / {state}-soft): {ratio:.2f}:1, kerak {AA}"
                )
    return problems


def main() -> int:
    css = CSS.read_text(encoding="utf-8")
    blobs = read_blobs(css)
    own_line = field_lines(css)
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

        field = parse(tokens.get("--rw-field", "").strip())
        text = parse(tokens.get("--rw-text", "").strip())
        if field is not None and text is not None:
            checked += 1
            surface = stops(tokens.get("--rw-surface", ""))
            base = over(field, surface[0]) if field[3] < 1 and surface else field
            ink = over(text, base) if text[3] < 1 else text
            raw = own_line.get(style, "").strip()
            if raw.startswith("var(--rw-line)"):
                line = parse(tokens.get("--rw-line", "").strip())
                # `transparent` o'qilmaydi va nol kenglik chizilmaydi —
                # ikkalasi ham «chegara yo'q», ya'ni 1:1.
                zero = tokens.get("--rw-line-w", "1px").strip() == "0px"
                edge = None if line is None or zero else (over(line, base) if line[3] < 1 else line)
            else:
                edge = tuple(  # type: ignore[assignment]
                    round(ink[i] * FIELD_MIX + base[i] * (1 - FIELD_MIX)) for i in range(3)
                ) + (1.0,)
            ratio = (
                min(contrast(edge, base), *(contrast(edge, s) for s in surface or [base]))
                if edge is not None
                else 1.0
            )
            if ratio < FIELD_MIN:
                failures.append(
                    f"{name}  maydon chegarasi: {ratio:.2f}:1, kerak {FIELD_MIN}"
                )

        raw_divider = tokens.get(DIVIDER_TOKEN, "").strip()
        if raw_divider:
            # O'qilmagan qiymat — XATO, o'tkazib yuborilmaydi. `transparent`
            # aynan shu yo'l bilan sirg'alib ketardi: `parse` uni `None`
            # qaytaradi va tekshiruv jimgina o'tib ketardi — asl nuqson
            # (`clay`/`neu` da ko'rinmas ajratgich) shu sababdan topilmagan.
            divider = parse(raw_divider)
            if divider is None:
                failures.append(
                    f"{name}  ajratgich ({DIVIDER_TOKEN}): rang o'qilmadi ({raw_divider})"
                )
            else:
                checked += 1

                def on_bg(bg: Color, fg: Color = divider) -> float:
                    return contrast(over(fg, bg) if fg[3] < 1 else fg, bg)

                worst_bg = min(backs, key=on_bg)
                ratio = on_bg(worst_bg)
                if ratio < DIVIDER_MIN:
                    failures.append(
                        f"{name}  ajratgich ({DIVIDER_TOKEN}): {ratio:.2f}:1, kerak {DIVIDER_MIN}"
                    )
        elif "--rw-faint" in tokens:
            failures.append(f"{name}  {DIVIDER_TOKEN}: token yo'q")

        to_check: list[tuple[str, Color, str]] = []
        for tier in TIERS + RANKS + LEVELS:
            if tier not in tokens:
                failures.append(f"{name}  {tier}: token yo'q")
                continue
            color = parse(tokens[tier])
            if color is None:
                failures.append(f"{name}  {tier}: rang o'qilmadi ({tokens[tier].strip()})")
                continue
            to_check.append((tier, color, tokens[tier].strip()))

        for label, lo, hi in LEVEL_MIXES:
            first = parse(tokens.get(f"--rw-level-{lo}", ""))
            second = parse(tokens.get(f"--rw-level-{hi}", ""))
            if first is not None and second is not None:
                to_check.append((label, mix_oklab(first, second), f"oklab mix(level-{lo}, level-{hi})"))

        for tier, color, raw in to_check:
            checked += 1

            def against(bg: Color, fg: Color = color) -> float:
                return contrast(over(fg, bg) if fg[3] < 1 else fg, bg)

            worst_bg = min(backs, key=against)
            ratio = against(worst_bg)
            if ratio < AA:
                failures.append(
                    f"{name}  {tier}: {raw} → {ratio:.2f}:1 "
                    f"(fon #{worst_bg[0]:02x}{worst_bg[1]:02x}{worst_bg[2]:02x}), kerak {AA}"
                )

    for (style, mode), tokens in sorted(style_tokens(css).items()):
        if "--rw-ground" not in tokens:
            continue
        fg = parse(tokens.get(ACCENT_PAIR[0], "").strip())
        if fg is None:
            failures.append(f'{style}.{mode}  {ACCENT_PAIR[0]}: token yo\'q')
            continue
        label = f'{style}{".dark" if mode == "dark" else ""}'
        backs = backgrounds(tokens, blobs.get(style, []))

        for accent in stops(tokens.get(ACCENT_PAIR[1], "")):
            # Shaffof accent ostidagi fon bilan qo'shiladi, matn esa uning
            # ustida turadi — shuning uchun eng yomon fon olinadi. Gradient
            # bo'lsa har bir pog'ona alohida o'lchanadi.
            bases = [over(accent, b) for b in backs] if accent[3] < 1 else [accent]
            checked += 1

            def on(bg: Color, fg: Color = fg) -> float:
                return contrast(over(fg, bg) if fg[3] < 1 else fg, bg)

            worst = min(bases, key=on)
            ratio = on(worst)
            if ratio < AA:
                failures.append(
                    f"{label}  tugma matni ({ACCENT_PAIR[0]} ustida "
                    f"{ACCENT_PAIR[1]}): {ratio:.2f}:1 "
                    f"(fon #{worst[0]:02x}{worst[1]:02x}{worst[2]:02x}), kerak {AA}"
                )

    # Accent MATN sifatida — tugma juftligidan ALOHIDA tekshiruv.
    # `.rw-accent-ink` havola matnida, `.rw-accent-soft` chip fonida
    # ishlatiladi; `--rw-accent-ink` ikkalasiga ham sig'ishi kerak.
    for (style, mode), tokens in sorted(style_tokens(css).items()):
        if "--rw-ground" not in tokens:
            continue
        label = f'{style}{".dark" if mode == "dark" else ""}'
        ink = parse(tokens.get(ACCENT_INK, "").strip())
        if ink is None:
            failures.append(f"{label}  {ACCENT_INK}: token yo'q")
            continue
        targets = list(backgrounds(tokens, blobs.get(style, [])))
        soft = parse(tokens.get(ACCENT_SOFT, "").strip())
        if soft is not None:
            # Shaffof `soft` (qorong'i mavzuda rgba) ostidagi eng yomon fon
            # bilan qo'shiladi — xuddi tugma tekshiruvidagi kabi.
            targets.append(over(soft, targets[0]) if soft[3] < 1 else soft)
        for bg in targets:
            checked += 1
            ratio = contrast(over(ink, bg) if ink[3] < 1 else ink, bg)
            if ratio < AA:
                failures.append(
                    f"{label}  accent matni ({ACCENT_INK} ustida fon): "
                    f"{ratio:.2f}:1 "
                    f"(fon #{bg[0]:02x}{bg[1]:02x}{bg[2]:02x}), kerak {AA}"
                )

    failures += check_semantic(css)
    checked += 3 * sum(1 for row in style_tokens(css).values() if "--rw-ground" in row)

    failures += check_kinds(css)
    checked += 2 * len(KINDS)

    if failures:
        print(f"Kontrast AA dan o'tmadi ({len(failures)} ta):", file=sys.stderr)
        for line in failures:
            print(f"  {line}", file=sys.stderr)
        return 1

    print(f"Kontrast: {checked} ta matn rangi AA ({AA}:1) dan o'tdi")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
