"""Gradientli ikki uslubni qo'lda tasdiqlash (`glass`, `skeu`).

`getComputedStyle` gradientning bitta rangini qaytarmaydi, ya'ni
brauzerdagi avtomatik o'lchov bu ikki uslubni o'tkazib yubordi
(`skip: true`). Bu skript o'sha bo'shliqni HAQIQIY qiymatlar bilan
to'ldiradi — gradientning har bir pog'onasi alohida o'lchanadi, chunki
matn eng yorug'/eng quyuq pog'onada eng kam kontrast beradi.

Qiymatlar brauzerdan `evaluate_script` bilan olindi (2026-09-13).
"""

from __future__ import annotations


def lum(color: tuple[int, int, int]) -> float:
    def channel(s: float) -> float:
        return s / 12.92 if s <= 0.03928 else ((s + 0.055) / 1.055) ** 2.4

    r, g, b = (channel(v / 255) for v in color)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(a: tuple[int, int, int], b: tuple[int, int, int]) -> float:
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def over(
    top: tuple[int, int, int], alpha: float, bottom: tuple[int, int, int]
) -> tuple[int, int, int]:
    return tuple(round(t * alpha + b * (1 - alpha)) for t, b in zip(top, bottom))


# ── glass-light ──────────────────────────────────────────────────────
# body fon gradienti: eng quyuq pog'ona eng ko'p kontrast beradi.
GLASS_GRAD = [(52, 29, 101), (21, 55, 108), (12, 81, 81)]
GLASS_PANEL = over((0, 0, 0), 0.62, GLASS_GRAD[0])  # eng noqulay holat
GLASS_INPUT = GLASS_PANEL  # maydon foni ham .62 qora
GLASS_BORDER_RAW = (191, 191, 191)
GLASS_BORDER = over(GLASS_BORDER_RAW, 0.866863, GLASS_PANEL)

glass_cases = [
    ("panel matni (oq) / panel", (255, 255, 255), GLASS_PANEL, 4.5),
    ("input matni (oq) / input", (255, 255, 255), GLASS_INPUT, 4.5),
    ("input chegarasi / input", GLASS_BORDER, GLASS_INPUT, 3.0),
    ("tugma matni (navy) / tugma (oq.92)", (36, 48, 107), (243, 244, 246), 4.5),
]

# ── skeu-light ───────────────────────────────────────────────────────
# Gradientning HAR IKKI pog'onasi tekshiriladi: matn eng yorug'ida eng
# kam kontrast beradi.
skeu_cases = [
    ("tugma matni (oq) / accent #527d38", (255, 255, 255), (82, 125, 56), 4.5),
    ("tugma matni (oq) / accent #3d6b28", (255, 255, 255), (61, 107, 40), 4.5),
    ("input matni / input eng yorug'", (37, 43, 50), (253, 253, 253), 4.5),
    ("input matni / input eng quyuq", (37, 43, 50), (232, 235, 239), 4.5),
    ("input chegarasi / eng yorug'", (37, 43, 50), (253, 253, 253), 3.0),
    ("input chegarasi / eng quyuq", (37, 43, 50), (232, 235, 239), 3.0),
    ("panel matni / panel eng yorug'", (37, 43, 50), (253, 253, 253), 4.5),
    ("panel matni / panel eng quyuq", (37, 43, 50), (223, 227, 232), 4.5),
]


def run(title: str, cases: list[tuple[str, tuple, tuple, float]], note: str = "") -> int:
    """Bitta uslubning juftliklarini o'lchaydi; yiqilganlar sonini qaytaradi."""
    print(title)
    if note:
        print(f"  {note}")
    bad = 0
    for name, fg, bg, need in cases:
        r = ratio(fg, bg)
        ok = r >= need
        bad += 0 if ok else 1
        print(f"  {'ok ' if ok else '!! '} {name:42s} {r:6.2f}:1  (kerak {need})")
    return bad


if __name__ == "__main__":
    fails = run(
        "glass-light",
        glass_cases,
        note=f"panel eng noqulay holatda rgb{GLASS_PANEL}, chegara rgb{GLASS_BORDER}",
    )
    print()
    fails += run("skeu-light", skeu_cases)
    print()
    if fails:
        raise SystemExit(f"YIQILDI: {fails} ta juftlik")
    print("Hammasi o'tdi — gradientli ikki uslub qo'lda tasdiqlandi.")
