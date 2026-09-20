#!/usr/bin/env python3
"""Reap stale git worktrees under one tool folder.

HITL 2026-09-20 `stale-reap`: slots are not roles, so there is no janitor
agent. A leftover tree under `wt/<tool>/` may be removed by that same tool
when it has no fresh lock, no open PR, and no manifest heartbeat < 4 h.

Never: `wt/deploy`, `cp/rankwant`, another tool's folder, or a dirty tree.
Unpushed commits are the owner's problem after a 4 h heartbeat — AOP already
requires `wip/` push before leaving the session.

Usage (from any RankWant worktree):

    python tools/reap_stale_worktrees.py --tool cursor
    python tools/reap_stale_worktrees.py --tool cursor --yes
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ALLOWED_TOOLS = ("cursor", "workbuddy", "claude")
HEARTBEAT_HOURS = 4
# Live detach + the canonical checkout. Removing either is an incident.
NEVER_REAP = ("wt/deploy", "cp/rankwant")
DEFAULT_BUS = Path("C:/Users/nsn/project/wt")
REPO = "menarzullayev/rankwant"


def _norm(path: str | Path) -> str:
    return str(Path(path)).replace("\\", "/").rstrip("/").lower()


def protected(path: Path) -> bool:
    n = _norm(path)
    return any(n.endswith(frag) or f"/{frag}/" in f"/{n}/" for frag in NEVER_REAP)


def bus_root() -> Path | None:
    raw = os.environ.get("RANKWANT_AGENT_BUS", "")
    if raw:
        p = Path(raw)
        return p if p.is_dir() else None
    return DEFAULT_BUS if DEFAULT_BUS.is_dir() else None


def git(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
    )


def worktrees(repo: Path) -> list[tuple[Path, str]]:
    out = git(repo, "worktree", "list", "--porcelain").stdout
    rows: list[tuple[Path, str]] = []
    current: Path | None = None
    branch = ""
    for line in out.splitlines():
        if line.startswith("worktree "):
            current = Path(line[len("worktree ") :])
            branch = ""
        elif line.startswith("branch "):
            ref = line[len("branch ") :]
            branch = ref.rsplit("/", 1)[-1]
        elif line == "" and current is not None:
            rows.append((current, branch))
            current = None
    if current is not None:
        rows.append((current, branch))
    return rows


def under_tool(path: Path, tool: str, bus: Path) -> bool:
    try:
        path.resolve().relative_to((bus / tool).resolve())
        return True
    except ValueError:
        return False


def dirty(path: Path) -> bool:
    return bool(git(path, "status", "--porcelain").stdout.strip())


def open_pr(branch: str) -> bool:
    if not branch:
        return False
    proc = subprocess.run(
        [
            "gh",
            "pr",
            "list",
            "--repo",
            REPO,
            "--head",
            branch,
            "--state",
            "open",
            "--json",
            "number",
        ],
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
    )
    if proc.returncode != 0:
        return True
    return bool(proc.stdout.strip()) and proc.stdout.strip() not in ("[]", "")


def fresh_manifest(bus: Path, path: Path) -> bool:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=HEARTBEAT_HOURS)
    target = _norm(path)
    manifests = bus / ".agent" / "manifests"
    status_dir = bus / ".agent" / "status"
    if not manifests.is_dir():
        return False
    for yml in manifests.glob("*.yml"):
        text = yml.read_text(encoding="utf-8", errors="replace")
        if target not in _norm(text):
            continue
        stamp = status_dir / yml.with_suffix(".md").name
        if not stamp.is_file():
            return True
        body = stamp.read_text(encoding="utf-8", errors="replace")
        for line in body.splitlines():
            if not line.lower().startswith("updated:"):
                continue
            raw = line.split(":", 1)[1].strip()
            try:
                when = datetime.fromisoformat(raw.replace(" +05", "+05:00"))
            except ValueError:
                return True
            if when.tzinfo is None:
                when = when.replace(tzinfo=timezone.utc)
            return when >= cutoff
        return True
    return False


def decide(path: Path, branch: str, tool: str, bus: Path, self_path: Path) -> str | None:
    """Return a skip reason, or None if the tree may be reaped."""
    if path.resolve() == self_path.resolve():
        return "joriy worktree"
    if protected(path):
        return "himoyalangan (deploy/canonical)"
    if not under_tool(path, tool, bus):
        return "boshqa tool papkasi"
    if dirty(path):
        return "iflos daraxt"
    if open_pr(branch):
        return f"ochiq PR ({branch})"
    if fresh_manifest(bus, path):
        return "yangi manifest heartbeat"
    return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tool", required=True, choices=ALLOWED_TOOLS)
    parser.add_argument("--yes", action="store_true", help="haqiqatan o'chir")
    parser.add_argument("--repo", default="", help="git common dir (default: this clone)")
    args = parser.parse_args(argv)

    bus = bus_root()
    if bus is None:
        print("stale-reap: agent bus yo'q — CI/boshqa mashina, hech narsa o'chirilmaydi")
        return 0

    repo = Path(args.repo) if args.repo else Path(__file__).resolve().parent.parent
    self_path = Path.cwd().resolve()
    reaped = 0
    skipped = 0
    failed = 0
    for path, branch in worktrees(repo):
        if not under_tool(path, args.tool, bus) and not protected(path):
            continue
        reason = decide(path, branch, args.tool, bus, self_path)
        if reason:
            print(f"skip  {path}  ({reason})")
            skipped += 1
            continue
        print(f"reap  {path}  [{branch or 'detached'}]")
        if not args.yes:
            reaped += 1
            continue
        rm = git(repo, "worktree", "remove", "--force", str(path))
        if rm.returncode != 0:
            print(rm.stderr.strip() or rm.stdout.strip())
            failed += 1
            continue
        reaped += 1
    if not args.yes:
        print(f"stale-reap dry-run: {reaped} nomzod (qo'llash: --yes), skip {skipped}")
        return 0
    print(f"stale-reap: o'chirildi {reaped}, skip {skipped}, xato {failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
