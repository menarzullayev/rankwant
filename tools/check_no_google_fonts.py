#!/usr/bin/env python3
"""Fail if any web source still reaches out to Google for fonts.

`next/font/google` performs a live HTTPS request to `fonts.googleapis.com`
on **every** `next build`, which couples the build to a third-party
service whose response is not stable: roughly one response in sixty
returns the font `src` URL in an extensionless form
(`https://fonts.gstatic.com/l/font?kit=...`). Turbopack cannot read that
and the whole build dies with

    Error while looking up import map:
    next/font/google queries have exactly one entry

Next's own `retry()` only covers transport errors and non-200 responses;
this failure is a 200, so it is never retried. The result was an
intermittent CI failure (vercel/next.js#99114).

The fix is that the fonts are vendored into the repository under
`apps/web/src/fonts/` and declared with `next/font/local`. This guard
exists so the fix cannot silently regress: if anyone reintroduces a
`next/font/google` import, the tree goes red here rather than flaking in
CI weeks later.

    python3 tools/check_no_google_fonts.py

Exit codes follow the repository convention:
    0  clean — no `next/font/google` anywhere
    1  drift — a Google font import came back
    2  could not measure (source tree missing)
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEB_SRC = ROOT / "apps" / "web" / "src"

# `import { Roboto } from "next/font/google"` and friends.
IMPORT = re.compile(
    r"""^\s*import\s+[^;\n]*?from\s+["']next/font/google["']""",
    re.M,
)
# `await import("next/font/google")` — the dynamic form.
DYNAMIC = re.compile(r"""import\s*\(\s*["']next/font/google["']\s*\)""")

SUFFIXES = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs"}

# Vendored sources are generated, not authored; skip nothing here — a
# Google import in no directory is acceptable.
IGNORED_DIRS = {"node_modules", ".next", "dist", "build", ".turbo"}


def iter_sources() -> list[Path]:
    """Every authored TypeScript/JavaScript file under `apps/web/src`."""
    found: list[Path] = []
    for path in WEB_SRC.rglob("*"):
        if path.suffix not in SUFFIXES:
            continue
        if any(part in IGNORED_DIRS for part in path.parts):
            continue
        found.append(path)
    return sorted(found)


def main() -> int:
    if not WEB_SRC.is_dir():
        print(f"✕ {WEB_SRC} topilmadi — o'lchab bo'lmadi")
        return 2

    hits: list[str] = []
    sources = iter_sources()
    if not sources:
        print(f"✕ {WEB_SRC} ichida manba fayl yo'q — o'lchab bo'lmadi")
        return 2

    for path in sources:
        text = path.read_text(encoding="utf8", errors="replace")
        for pattern in (IMPORT, DYNAMIC):
            for match in pattern.finditer(text):
                line = text.count("\n", 0, match.start()) + 1
                hits.append(f"{path.relative_to(ROOT)}:{line}")

    if hits:
        print(f"✕ `next/font/google` qaytdi — {len(hits)} joy:")
        for hit in hits[:20]:
            print(f"    {hit}")
        if len(hits) > 20:
            print(f"    ... yana {len(hits) - 20} ta")
        print("  Shriftlar `apps/web/src/fonts/` dan, `next/font/local` bilan berilishi kerak.")
        return 1

    print(f"✓ `next/font/google` yo'q ({len(sources)} manba fayl tekshirildi)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
