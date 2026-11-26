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


GROUPS_PY = ROOT / "apps/api/notifications/groups.py"
SECTION_TS = ROOT / "apps/web/src/features/account/components/NotificationsSection.tsx"


def web_lists_match() -> list[str]:
    """The settings page's group and legacy lists equal `notifications.groups`.

    The page writes both by hand (2026-11-16 review: "TS/Python group list
    duplicated"); a group added, removed or reordered on one side only would
    show a switch that saves nowhere, or hide one that works.
    """
    namespace: dict[str, object] = {"__name__": "groups"}
    exec(compile(GROUPS_PY.read_text(encoding="utf-8"), str(GROUPS_PY), "exec"), namespace)  # noqa: S102
    visible = list(namespace["visible_groups"]())  # type: ignore[operator]
    legacy_of = namespace["legacy_kinds"]
    src = SECTION_TS.read_text(encoding="utf-8")
    problems: list[str] = []
    block = re.search(r"^const GROUPS = \[(.*?)\] as const;", src, re.M | re.S)
    web = re.findall(r'"(\w+)"', block.group(1)) if block else []
    if web != visible:
        problems.append(f"GROUPS {web} != visible_groups() {visible}")
    legacy = re.search(r"^const LEGACY_KINDS[^=]*= \{(.*?)^\};", src, re.M | re.S)
    web_legacy = (
        {k: re.findall(r'"(\w+)"', v) for k, v in re.findall(r"^\s+(\w+): \[([^\]]*)\]", legacy.group(1), re.M)}
        if legacy
        else {}
    )
    for group in visible:
        # A set: the page reads the kinds in any order.
        want = sorted(legacy_of(group))  # type: ignore[operator]
        if sorted(web_legacy.get(group, [])) != want:
            problems.append(f"LEGACY_KINDS[{group}] {web_legacy.get(group, [])} != legacy_kinds() {want}")
    return problems


def main() -> int:
    lists = web_lists_match()
    if lists:
        print(f"✗ {SECTION_TS.relative_to(ROOT).as_posix()} differs from notifications/groups.py:")
        for item in lists:
            print("   ", item)
        return 1
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
