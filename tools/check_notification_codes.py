#!/usr/bin/env python3
"""Coded notifications are stored as `code` + `params` and drawn later, in the
reader's language (decision 2026-10-27). So a stored row outlives the code that
wrote it: a code or a `{param}` removed from the catalog leaves old rows that
can no longer be drawn.

Rule: a code name and its params are never removed or renamed. A change of
meaning is a NEW code (`duel_won_2`). Additions are allowed but must be
recorded in `tools/notification-codes.json`, so the baseline stays the truth
the next removal is measured against.

    python tools/check_notification_codes.py            # exit 1 on a removal or an unrecorded addition
    python tools/check_notification_codes.py --update   # record additions (never removals)
"""

from __future__ import annotations

import json
import pathlib
import re
import sys

import _console

_console.force_utf8()

ROOT = pathlib.Path(__file__).resolve().parents[1]
CATALOG = ROOT / "apps/api/notifications/message_catalog.py"
BASELINE = ROOT / "tools/notification-codes.json"
PLACEHOLDER = re.compile(r"\{(\w+)\}")


def current() -> dict[str, list[str]]:
    namespace: dict[str, object] = {}
    exec(compile(CATALOG.read_text(encoding="utf-8"), str(CATALOG), "exec"), namespace)  # noqa: S102
    catalog = namespace["CATALOG"]
    assert isinstance(catalog, dict)
    found: dict[str, set[str]] = {}
    for sections in catalog.values():
        for code, parts in sections.items():
            names = found.setdefault(code, set())
            for text in parts.values():
                names.update(PLACEHOLDER.findall(text))
    return {code: sorted(names) for code, names in sorted(found.items())}


def main() -> int:
    now = current()
    baseline: dict[str, list[str]] = (
        json.loads(BASELINE.read_text(encoding="utf-8")) if BASELINE.exists() else {}
    )
    removed = [f"code '{c}'" for c in baseline if c not in now]
    removed += [
        f"param '{p}' of '{c}'" for c, params in baseline.items() if c in now for p in params if p not in now[c]
    ]
    added = [c for c in now if c not in baseline]
    added += [c for c, params in now.items() if c in baseline and set(params) - set(baseline[c])]

    if "--update" in sys.argv:
        if removed:
            print("✗ removals cannot be recorded:", ", ".join(removed))
            return 1
        BASELINE.write_text(json.dumps(now, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"✓ {len(now)} codes recorded")
        return 0
    if removed:
        print("✗ removed from the catalog (stored notifications could no longer be drawn):")
        for item in removed:
            print("   ", item)
        print("  Keep the code and add a new one for a change of meaning.")
        return 1
    if added:
        print("✗ not recorded in tools/notification-codes.json:", ", ".join(sorted(set(added))))
        print("  Run: python tools/check_notification_codes.py --update")
        return 1
    print(f"✓ {len(now)} notification codes match the baseline")
    return 0


if __name__ == "__main__":
    sys.exit(main())
