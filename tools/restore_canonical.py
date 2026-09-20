#!/usr/bin/env python3
"""Put `cp/rankwant` back on origin/main when it is idle.

HITL 2026-09-20 `restore-when-idle`: if porcelain is empty and no slot
manifest lists this path as `workspace`, the next agent fast-forwards it
to `origin/main`. Dirty or claimed trees are left alone.

Never: `git reset --hard`, `git clean -fd`. A local `main` that cannot
fast-forward is skipped, not rewritten.

    python tools/restore_canonical.py
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

# HITL 2026-09-20 `restore-when-idle`
CANONICAL = Path("C:/Users/nsn/project/cp/rankwant")
DEFAULT_BUS = Path("C:/Users/nsn/project/wt")
# These git verbs are forbidden here even if a future edit looks tempting.
FORBIDDEN_GIT = ("reset", "clean")


def git(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    if args and args[0] in FORBIDDEN_GIT:
        raise RuntimeError("restore-when-idle must not reset/clean")
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
    )


def bus_root() -> Path | None:
    raw = os.environ.get("RANKWANT_AGENT_BUS", "")
    if raw:
        p = Path(raw)
        return p if p.is_dir() else None
    return DEFAULT_BUS if DEFAULT_BUS.is_dir() else None


def claimed(bus: Path, canonical: Path) -> bool:
    needle = str(canonical).replace("\\", "/").lower()
    manifests = bus / ".agent" / "manifests"
    if not manifests.is_dir():
        return False
    for yml in manifests.glob("*.yml"):
        text = yml.read_text(encoding="utf-8", errors="replace").replace("\\", "/").lower()
        if needle in text:
            return True
    return False


def main() -> int:
    if not CANONICAL.is_dir():
        print(f"restore-when-idle: {CANONICAL} yo'q — CI/boshqa mashina")
        return 0
    bus = bus_root()
    if bus is None:
        print("restore-when-idle: agent bus yo'q — o'tkazib yuborildi")
        return 0
    if claimed(bus, CANONICAL):
        print(f"restore-when-idle: skip — manifest `workspace` {CANONICAL}")
        return 0
    porcelain = git(CANONICAL, "status", "--porcelain")
    if porcelain.returncode != 0:
        print(porcelain.stderr.strip() or porcelain.stdout.strip())
        return 1
    if porcelain.stdout.strip():
        print("restore-when-idle: skip — iflos daraxt")
        return 0
    fetched = git(CANONICAL, "fetch", "origin", "main")
    if fetched.returncode != 0:
        print(fetched.stderr.strip() or fetched.stdout.strip())
        return 1
    checked = git(CANONICAL, "checkout", "main")
    if checked.returncode != 0:
        print("restore-when-idle: skip — checkout main yiqildi")
        print(checked.stderr.strip() or checked.stdout.strip())
        return 0
    ff = git(CANONICAL, "merge", "--ff-only", "origin/main")
    if ff.returncode != 0:
        print("restore-when-idle: skip — ff-only yiqildi (reset yo'q)")
        print(ff.stderr.strip() or ff.stdout.strip())
        return 0
    print("restore-when-idle: cp/rankwant = origin/main")
    return 0


if __name__ == "__main__":
    sys.exit(main())
