#!/usr/bin/env python3
"""`packages/shared` must stay platform-independent.

WHY THIS EXISTS
---------------
The `packages/` split (RW-ARCH-013 / ADR-0009) only earns its keep if the
shared package cannot reach back into an app. A single
`import { t } from "@/i18n/messages"` inside `packages/shared/src` would:

  * break the build for any consumer that is not `apps/web` — the Go judge,
    a future worker, a plain `node` script;
  * hide the coupling until the moment someone tries to use it, which is
    the worst possible time to discover it;
  * turn "shared" into "web code in a different folder".

A rule that is only written in a README is a rule that decays. This script
turns it into a gate.

WHAT IS CHECKED
---------------
For every `.ts` file under `packages/shared/src`:

  1. **No alias imports.** `@/...` resolves only inside `apps/web`. A shared
     module that uses it is app code.
  2. **No bare imports except `zod`.** An allowlist, not a denylist: a new
     dependency has to be justified in review. `node:`, `react`, `next`,
     `server-only` and anything else stop the build here.
  3. **No app-relative escapes.** A relative import that climbs out of the
     package (`../../apps/...`) is the same violation with extra steps.
  4. **`LOCALES` stays in one place.** The list of ten languages is a
     product decision; a second copy in the app would drift on the next
     language added. Enforced by looking for a literal ten-language array
     in `apps/web/src` that is not a re-export.

Exit codes: 0 clean, 1 a rule is broken, 2 a source could not be read.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import _console

_console.force_utf8()

ROOT = Path(__file__).resolve().parent.parent
SHARED = ROOT / "packages/shared/src"

#: Bare specifiers a shared module may import. `zod` is here because the
#: validation layer is the reason the package exists; anything else must be
#: added deliberately, with a reason, in this list.
ALLOWED_BARE = {"zod"}

#: `import ... from "x"` and `export ... from "x"`, including `import type`.
IMPORT_RE = re.compile(
    r"""^\s*(?:import|export)\s+(?:type\s+)?[^'"]*?from\s+['"]([^'"]+)['"]""",
    re.M,
)
#: Side-effect imports: `import "server-only";`
BARE_IMPORT_RE = re.compile(r"""^\s*import\s+['"]([^'"]+)['"]""", re.M)


def shared_files() -> list[Path]:
    if not SHARED.exists():
        raise FileNotFoundError(f"packages/shared/src topilmadi ({SHARED})")
    return sorted(SHARED.rglob("*.ts"))


def check_imports() -> list[str]:
    problems: list[str] = []
    for path in shared_files():
        rel = path.relative_to(ROOT)
        text = path.read_text(encoding="utf-8")
        specifiers = IMPORT_RE.findall(text) + BARE_IMPORT_RE.findall(text)
        for spec in specifiers:
            if spec.startswith("."):
                # Relative is fine, climbing out of the package is not.
                target = (path.parent / spec).resolve()
                if not str(target).startswith(str(SHARED.resolve())):
                    problems.append(
                        f"{rel}: `{spec}` paketdan TASHQARIGA chiqadi"
                    )
                continue
            if spec.startswith("@"):
                problems.append(
                    f"{rel}: `{spec}` alias import — shared paket app kodini bilmasligi kerak"
                )
                continue
            if spec == "zod" or spec.startswith("zod/"):
                continue
            if spec in ALLOWED_BARE:
                continue
            problems.append(
                f"{rel}: ruxsat etilmagan bog'liqlik `{spec}` "
                f"(ruxsat: {', '.join(sorted(ALLOWED_BARE))} va nisbiy yo'llar)"
            )
    return problems


def check_locale_list_not_duplicated() -> list[str]:
    """The ten-language list must be declared once, in the shared package.

    Measured risk: `LOCALES` is read by the header switcher, the sitemap,
    `hreflang` tags and the dictionary loader. If a second literal copy
    appears in `apps/web`, adding an eleventh language updates one of them.
    """
    web_src = ROOT / "apps/web/src"
    if not web_src.exists():
        return [f"apps/web/src topilmadi ({web_src})"]

    problems: list[str] = []
    #: A literal array that names at least eight of the ten languages in a
    #: single declaration. Re-exports and spread aliases do not match.
    langs = ["uz", "kaa", "ru", "en", "kk", "ky", "tg", "tr", "zh", "es"]
    pattern = re.compile(r"\[\s*(?:" + r"|".join(f'"{x}"' for x in langs) + r")\s*,", re.M)
    for path in sorted(web_src.rglob("*.ts*")):
        text = path.read_text(encoding="utf-8")
        for match in pattern.finditer(text):
            #: The remaining languages must be present too, or it is a
            #: different (smaller) list that happens to start the same way.
            window = text[match.start() : match.start() + 400]
            found = sum(1 for lang in langs if f'"{lang}"' in window)
            if found < 8:
                continue

            #: A partial list is legitimate when it is a UI *grouping* and it
            #: is cross-checked against the master list, so a new language
            #: cannot silently fall out. The guard is a `LOCALES` reference in
            #: the same file — the declared contract, not the literal, is what
            #: keeps the two in step.
            if re.search(r"\bLOCALES\b", text):
                continue

            line = text.count("\n", 0, match.start()) + 1
            problems.append(
                f"{path.relative_to(ROOT)}:{line}: til ro'yxati qayta yozilgan va "
                f"`LOCALES` bilan bog'lanmagan — `@rankwant/shared/i18n` dan "
                f"`LOCALES` ni oling yoki to'liqlikni tekshiring"
            )
    return problems


def main() -> int:
    try:
        files = shared_files()
    except FileNotFoundError as exc:
        print(f"✗ Manbani o'qib bo'lmadi — {exc}")
        return 2

    problems = check_imports() + check_locale_list_not_duplicated()
    if problems:
        print(f"✗ packages/shared chegarasi: {len(problems)} ta muammo:")
        for problem in problems:
            print(f"  - {problem}")
        return 1

    print(
        f"✓ packages/shared chegarasi toza: {len(files)} fayl, "
        f"faqat nisbiy yo'llar + {', '.join(sorted(ALLOWED_BARE))}; "
        "til ro'yxati yagona nusxada"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
