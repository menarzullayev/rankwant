#!/usr/bin/env python3
"""Every page has an access level, and the protected ones are guarded.

Measured 2026-10-08 on the live site, as a guest: of 80 pages only three
turned a guest away on the server (`/settings`, `/settings/<section>`,
`/onboarding`). `/notifications` and all 24 admin pages answered 200 and
let the browser hide them; who may open what was written in three places
and listed in none. The list now lives in one file
(`apps/web/src/lib/access.ts`, ADR-0054) and this check keeps it true:

* every route's first segment is in the list — a new section cannot ship
  without somebody deciding who it is for;
* the list names no section that has no page (a stale entry reads as
  protection that is not there);
* every page of a `user` section is behind `requireUser()` and every page
  of a `staff` section behind `requireStaff()`, in the page itself or in a
  layout above it;
* `proxy.ts` uses the list, so a guest is turned away before page code runs.

Exit 0 — clean, 1 — a rule is broken, 2 — a file could not be read.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# A piped Windows stdout is `cp1252` and dies on the first `✓`; see `_console.py`.
import _console

_console.force_utf8()

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "apps/web/src"
APP = SRC / "app"
LIST = SRC / "lib/access.ts"
PROXY = SRC / "proxy.ts"

LEVELS = {"public", "guest", "user", "staff"}
#: Either guard signs a visitor in; only the second also asks for staff.
GUARD = {"user": ("requireUser", "requireStaff"), "staff": ("requireStaff",)}

ENTRY = re.compile(r'^\s+(?:"([^"]*)"|([A-Za-z][\w-]*)):\s*"(\w+)",\s*$')


def access_list(text: str) -> dict[str, str]:
    """The `ACCESS` object: section → level."""
    match = re.search(r"export const ACCESS\b[^=]*=\s*\{\n(.*?)\n\};", text, re.DOTALL)
    if not match:
        return {}
    found: dict[str, str] = {}
    for line in match.group(1).splitlines():
        entry = ENTRY.match(line)
        if entry:
            found[entry.group(1) if entry.group(1) is not None else entry.group(2)] = entry.group(3)
    return found


def route_of(page: Path) -> list[str]:
    """Path segments of a page, without route groups: `(site)/a/[b]` → a, [b]."""
    parts = page.relative_to(APP).parent.parts
    return [part for part in parts if not (part.startswith("(") and part.endswith(")"))]


def code_of(path: Path) -> str:
    """The file without its comments — a guard named in a comment guards nothing."""
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    return "\n".join(line for line in text.splitlines() if not line.lstrip().startswith("//"))


def calls_guard(code: str, names: tuple[str, ...]) -> bool:
    """`await requireUser("/x")`, with or without a type argument."""
    return any(re.search(rf"\bawait {name}(?:<[^>()]*>)?\(", code) for name in names)


def guarded(page: Path, calls: tuple[str, ...]) -> bool:
    """The page, or a layout between it and the app root, makes the call."""
    if calls_guard(code_of(page), calls):
        return True
    folder = page.parent
    while folder != APP.parent:
        layout = folder / "layout.tsx"
        # The root layout wraps every page; a guard there would not be this
        # section's, so it does not count.
        if folder != APP and layout.exists() and calls_guard(code_of(layout), calls):
            return True
        folder = folder.parent
    return False


def main() -> int:
    try:
        levels = access_list(LIST.read_text(encoding="utf-8"))
        proxy = code_of(PROXY)
        pages = sorted(APP.rglob("page.tsx"))
    except OSError as error:
        print(f"✗ o'qib bo'lmadi: {error}", file=sys.stderr)
        return 2
    if not levels or not pages:
        print("✗ access ro'yxati yoki sahifalar topilmadi", file=sys.stderr)
        return 2

    problems: list[str] = []
    for section, level in levels.items():
        if level not in LEVELS:
            problems.append(f"access.ts: `{section}` — unknown level `{level}`")

    seen: set[str] = set()
    for page in pages:
        segments = route_of(page)
        section = segments[0] if segments else ""
        seen.add(section)
        rel = page.relative_to(ROOT).as_posix()
        if section not in levels:
            problems.append(f"{rel}: section `{section}` has no access level in lib/access.ts")
            continue
        calls = GUARD.get(levels[section])
        if calls and not guarded(page, calls):
            problems.append(f"{rel}: a `{levels[section]}` page with no `{calls[0]}()` guard")

    for section in sorted(set(levels) - seen):
        problems.append(f"access.ts: `{section}` is listed but has no page")

    if "needsSignIn(" not in proxy:
        problems.append("proxy.ts does not use the access list (`needsSignIn`)")

    for problem in problems:
        print(f"✗ {problem}")
    if problems:
        return 1
    protected = sum(1 for level in levels.values() if level in GUARD)
    print(f"✓ {len(pages)} sahifa, {len(levels)} bo'lim: har biri darajaga ega, {protected} tasi server qo'riqchisi ortida")
    return 0


if __name__ == "__main__":
    sys.exit(main())
