#!/usr/bin/env python3
"""Every Tailwind `@source` path must resolve on disk.

Why this exists: `@source` paths rot when files move, and a gate that matches
the directive's *text* cannot see it. Measured 2026-09-24 —
`apps/web/src/app/auth.css` carried 11 paths of which **8 no longer resolved**
(the feature-folder refactor moved `components/auth`, `components/AuthForm`,
`components/ProviderMark`, `components/UpdatesBell` and
`components/{profile,problems,settings}` into `features/`). The live `/login`
sheet was still carrying `features/problems` and `features/profile` classes
(`[max-height:14rem]`, `text-[10px]`, `font-size:9px`), while the only guard in
place checked for the literal text `@source not "./(site/`.

Three rules, because the failure has two shapes:
  1. the directory part of every `@source` path must exist — a dead *include*
     drops classes silently, a dead *exclude* widens the sheet silently;
  2. a stylesheet that uses `@source` must also disable automatic detection
     (`source(none)`), otherwise the list is decorative and only `@source not`
     narrows anything;
  3. no include may sweep the `(site)` tree into a sheet that exists to stay
     narrow (LH-LOGIN-CSS: the full sheet put desktop FCP at 1.1-1.2 s).

Exit code: 0 — clean, 1 — a dead path or a missing `source(none)`.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# Windows writes the pipe as `cp1252` and dies on the first `✓`; the reason and
# the measurement live in `tools/_console.py`.
import _console

_console.force_utf8()

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "apps/web/src/app"

#: A directive is the optional `not`, then the quoted path.
SOURCE_RE = re.compile(r'@source(\s+not)?\s+"([^"]+)"')

#: The Tailwind entry import, with its optional `source(...)` argument.
#: Matching the directive — not a bare `"source(none)" in text` — is the whole
#: point: a comment that mentions `source(none)` (this file's own stylesheet
#: has one) would otherwise satisfy a substring test while the code is broken.
#: Measured 2026-09-24: the substring version passed a stylesheet whose import
#: had already lost `source(none)`.
TAILWIND_IMPORT_RE = re.compile(r'@import\s+"tailwindcss"\s*(?:source\(([^)]*)\))?\s*;')


def base_of(pattern: str) -> str:
    """`../components/**/*.{ts,tsx}` -> `../components`; a bare path stays.

    Only the part before the first `*` can be resolved; the rest is the
    pattern Tailwind matches inside it.
    """
    cut = pattern.find("*")
    base = pattern if cut < 0 else pattern[:cut]
    return base.rstrip("/") or "."


def main() -> int:
    problems: list[str] = []
    checked = 0

    for sheet in sorted(APP.glob("*.css")):
        rel = sheet.relative_to(ROOT).as_posix()
        text = sheet.read_text(encoding="utf-8")
        directives = SOURCE_RE.findall(text)
        if not directives:
            continue
        checked += 1

        for negated, pattern in directives:
            base = base_of(pattern)
            target = sheet.parent / base
            if not target.exists():
                kind = "not " if negated else ""
                problems.append(f"{rel}: `@source {kind}\"{pattern}\"` yechilmaydi — `{base}` yo'q")
                continue
            if not negated and (target / "(site)").exists():
                problems.append(
                    f"{rel}: `@source \"{pattern}\"` (site) daraxtini qamraydi — "
                    "tor sheet kengayib ketadi"
                )

        entry = TAILWIND_IMPORT_RE.search(text)
        if entry is None:
            problems.append(f"{rel}: `@import \"tailwindcss\"` topilmadi")
        elif (entry.group(1) or "").strip() != "none":
            problems.append(
                f"{rel}: `@source` bor, lekin import `source(none)` bilan emas — "
                "ro'yxat bezak bo'lib qoladi va o'lik istisno sheet'ni JIM kengaytiradi"
            )

    if problems:
        print(f"✗ CSS skan yo'llari: {len(problems)} ta muammo")
        for problem in problems:
            print(f"  - {problem}")
        print(
            "\nTuzatish: yo'lni haqiqiy papkaga qarating yoki o'chiring. "
            "`source(none)` bo'lmasa qo'shing."
        )
        return 1

    print(f"✓ CSS skan yo'llari yechiladi — {checked} fayl tekshirildi")
    return 0


if __name__ == "__main__":
    sys.exit(main())
