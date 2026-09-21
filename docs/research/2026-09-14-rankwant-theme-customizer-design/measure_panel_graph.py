#!/usr/bin/env python3
"""Source-graph bytes for the contestant customizer panel (D63).

Walks static imports from Customizer.tsx / AppearanceTab / A11yTab.
Does not run webpack. Type-only imports are skipped. node_modules stay out.

Usage (from any RankWant worktree):

    python docs/research/2026-09-14-rankwant-theme-customizer-design/measure_panel_graph.py
"""

from __future__ import annotations

import json
import re
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "apps/web/src"
PANEL = SRC / "components/customizer"

IMPORT = re.compile(
    r"""^\s*import\s+(?P<type>type\s+)?(?P<body>[\s\S]*?)\s+from\s+['"](?P<spec>[^'"]+)['"]""",
    re.M,
)
EXPORT_FROM = re.compile(
    r"""^\s*export\s+(?P<type>type\s+)?[\s\S]*?\s+from\s+['"](?P<spec>[^'"]+)['"]""",
    re.M,
)
SIDE_EFFECT = re.compile(r"""^\s*import\s+['"](?P<spec>[^'"]+)['"]""", re.M)

SKIP_PREFIX = (
    "react",
    "react-dom",
    "next/",
    "node:",
)


def resolve(spec: str, here: Path) -> Path | None:
    if spec.startswith("@/"):
        base = SRC / spec[2:]
    elif spec.startswith("."):
        base = (here.parent / spec)
    else:
        return None
    candidates = [
        Path(str(base) + ".tsx"),
        Path(str(base) + ".ts"),
        base / "index.tsx",
        base / "index.ts",
        base,
    ]
    for path in candidates:
        if path.is_file() and path.suffix in {".ts", ".tsx"}:
            return path.resolve()
    return None


def specs(text: str) -> list[str]:
    out: list[str] = []
    for match in IMPORT.finditer(text):
        if match.group("type"):
            continue
        out.append(match.group("spec"))
    for match in EXPORT_FROM.finditer(text):
        if match.group("type"):
            continue
        out.append(match.group("spec"))
    for match in SIDE_EFFECT.finditer(text):
        out.append(match.group("spec"))
    return out


def walk(entry: Path, skip: set[Path] | None = None) -> dict[Path, int]:
    seen: dict[Path, int] = {}
    blocked = {p.resolve() for p in (skip or set())}
    queue = deque([entry.resolve()])
    while queue:
        path = queue.popleft()
        if path in seen or path in blocked:
            continue
        text = path.read_text(encoding="utf-8")
        seen[path] = len(text.encode("utf-8"))
        for spec in specs(text):
            if spec.startswith(SKIP_PREFIX) or spec in {"react", "react-dom"}:
                continue
            nxt = resolve(spec, path)
            if nxt is not None and nxt not in seen and nxt not in blocked:
                queue.append(nxt)
    return seen


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def kb(n: int) -> str:
    return f"{n / 1024:.1f} KiB"


def main() -> int:
    tabs = {PANEL / "AppearanceTab.tsx", PANEL / "A11yTab.tsx"}
    shell = walk(PANEL / "Customizer.tsx", skip=tabs)
    appearance = walk(PANEL / "AppearanceTab.tsx")
    a11y = walk(PANEL / "A11yTab.tsx")
    customizer = walk(PANEL / "Customizer.tsx")
    appearance_only = {p: n for p, n in appearance.items() if p not in shell}
    a11y_only = {p: n for p, n in a11y.items() if p not in shell}
    both = set(appearance_only) & set(a11y_only)
    report = {
        "unit": "utf-8 source bytes, static import graph, type-only skipped",
        "shell_without_tabs": {
            "files": len(shell),
            "bytes": sum(shell.values()),
        },
        "appearance_tab_exclusive": {
            "files": len(appearance_only),
            "bytes": sum(appearance_only.values()),
            "paths": sorted(rel(p) for p in appearance_only),
        },
        "a11y_tab_exclusive": {
            "files": len(a11y_only),
            "bytes": sum(a11y_only.values()),
            "paths": sorted(rel(p) for p in a11y_only),
        },
        "tabs_shared_exclusive": {
            "files": len(both),
            "bytes": sum(appearance_only[p] for p in both),
        },
        "full_customizer_graph": {
            "files": len(customizer),
            "bytes": sum(customizer.values()),
        },
    }
    print("D63 customizer panel source graph")
    for key, row in report.items():
        if key == "unit":
            print(f"  {row}")
            continue
        print(f"  {key}: {row['files']} files, {row['bytes']} B ({kb(row['bytes'])})")
    dest = Path(__file__).with_name("PANEL-GRAPH.json")
    dest.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"  wrote {dest.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
