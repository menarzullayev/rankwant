#!/usr/bin/env python3
"""Scroll boxes are written one way.

Measured 2026-10-06: 44 scroll containers in 33 files, each built from raw
`overflow-*-auto` classes, so each behaved its own way — three overlays
locked the page with three copies of the same code, wide tables could not
be scrolled from the keyboard, and popovers passed the wheel on to the page
behind them. The vocabulary now lives in two places:

* CSS  — `rw-scroll-x`, `rw-scroll-y`, `rw-scroll`, `rw-scroll-trap`,
         `rw-snap-x` (`apps/web/src/app/theme.css`)
* code — `lockBodyScroll`, `revealElement` (`apps/web/src/lib/scroll.ts`)

This check keeps hand-written scrolling out of everything else.

Exit 0 — clean, 1 — a rule is broken, 2 — a file could not be read.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "apps/web/src"
THEME = SRC / "app/theme.css"
HELPER = SRC / "lib/scroll.ts"

#: The overlay scrollbar reads and moves scroll positions by design.
SCRIPT_ALLOWED = {"lib/scroll.ts", "lib/chiziq.ts"}

RAW_CLASS = re.compile(r"(?<![\w-])overflow-(?:[xy]-)?(?:auto|scroll)(?![\w-])")
RAW_SCRIPT = (
    (re.compile(r"\.style\.overflow\w*\s*="), "sets `style.overflow` — use `lockBodyScroll()`"),
    (re.compile(r"\.scrollIntoView\("), "calls `scrollIntoView` — use `revealElement()`"),
    (re.compile(r"\bscroll-smooth\b|scroll-behavior\s*:\s*smooth"), "forces smooth scrolling — ask for it through `revealElement({ smooth: true })`"),
)
UTILITIES = ("rw-scroll-x", "rw-scroll-y", "rw-scroll", "rw-scroll-trap", "rw-snap-x")


def problems() -> list[str]:
    found: list[str] = []
    theme = THEME.read_text(encoding="utf-8")
    for name in UTILITIES:
        if f"@utility {name} {{" not in theme:
            found.append(f"app/theme.css: `@utility {name}` is missing")
    if "scroll-padding-top: calc(var(--rw-header-h)" not in theme:
        found.append("app/theme.css: the root has no `scroll-padding-top` for the sticky header")
    helper = HELPER.read_text(encoding="utf-8")
    for name in ("lockBodyScroll", "revealElement"):
        if f"export function {name}(" not in helper:
            found.append(f"lib/scroll.ts: `{name}` is missing")

    for path in sorted([*SRC.rglob("*.tsx"), *SRC.rglob("*.ts")]):
        rel = path.relative_to(SRC).as_posix()
        if "/generated/" in rel:
            continue
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            stripped = line.strip()
            if stripped.startswith(("//", "*", "/*", "{/*")):
                continue
            if RAW_CLASS.search(line):
                found.append(f"{rel}:{number}: raw `overflow-*-auto` — use `rw-scroll-x` / `rw-scroll-y` / `rw-scroll`")
            if rel in SCRIPT_ALLOWED:
                continue
            for pattern, message in RAW_SCRIPT:
                if pattern.search(line):
                    found.append(f"{rel}:{number}: {message}")
    return found


def main() -> int:
    try:
        found = problems()
    except OSError as error:
        print(f"check_scroll: cannot read {error.filename}: {error.strerror}", file=sys.stderr)
        return 2
    if found:
        print("Scroll: hand-written scrolling found\n")
        for item in found:
            print(f"  ✗ {item}")
        print("\nSee apps/web/src/lib/scroll.ts and the SCROLL block in apps/web/src/app/theme.css.")
        return 1
    print("✓ Scroll: every scroll box uses the shared utilities and helpers")
    return 0


if __name__ == "__main__":
    sys.exit(main())
