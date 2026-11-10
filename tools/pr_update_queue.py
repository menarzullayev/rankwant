#!/usr/bin/env python3
"""Bring one auto-merge PR up to date with `main` at a time.

Owner decision 2026-11-10 (deploy-time audit, step D). The ruleset requires
an up-to-date branch (`strict`), so every merge leaves the other open PRs
BEHIND, and their CI runs again after `update-branch`. With several agent
sessions merging in parallel, each one updated its own PR at once, the next
merge made it BEHIND again and that CI run was thrown away: measured on the
last 30 merged PRs, 75 PR CI runs where 30 would do (median 2:51 each).

This runs on every watcher tick (`tools/auto_deploy.sh`). It updates a PR
only when no auto-merge PR is in flight (a CI check still running), and then
only the oldest BEHIND one. Agents leave BEHIND PRs alone (CLAUDE.md); a PR
with conflicts (DIRTY) still needs its agent, and a PR without auto-merge is
not touched at all.

`gh pr update-branch` merges `main` into the branch — no rebase, no force push.

Exit: 0 (also when there is nothing to do or GitHub cannot be read — the
watcher must not stop over this), 2 on a broken fixture.

Tests: --prs FILE (JSON as `gh pr list --json` prints) and --dry-run.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import _console

_console.force_utf8()

ROOT = Path(__file__).resolve().parent.parent
FIELDS = "number,isDraft,isCrossRepository,autoMergeRequest,mergeStateStatus,createdAt,statusCheckRollup"


def in_flight(pr: dict) -> bool:
    """A check of this PR is still queued or running."""
    for check in pr.get("statusCheckRollup") or []:
        # CheckRun has `status`; a StatusContext has `state` instead.
        status = check.get("status")
        if status is not None and status != "COMPLETED":
            return True
        if check.get("state") in ("PENDING", "EXPECTED"):
            return True
    return False


def eligible(pr: dict) -> bool:
    return bool(pr.get("autoMergeRequest")) and not pr.get("isDraft") and not pr.get("isCrossRepository")


def choose(prs: list[dict]) -> tuple[int | None, str]:
    """The PR to update now, or None with the reason."""
    queue = [p for p in prs if eligible(p)]
    # CLEAN with auto-merge is about to merge: updating another PR now would
    # leave it BEHIND again the moment this one lands.
    busy = [p["number"] for p in queue if in_flight(p) or p.get("mergeStateStatus") == "CLEAN"]
    if busy:
        return None, f"navbat band: #{busy[0]} CI'si yuryapti"
    behind = sorted(
        (p for p in queue if p.get("mergeStateStatus") == "BEHIND"),
        key=lambda p: str(p.get("createdAt", "")),
    )
    if not behind:
        return None, "orqada qolgan auto-merge PR yo'q"
    return behind[0]["number"], f"navbatda {len(behind)} ta"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--prs", help="test fixture: JSON file of open PRs")
    ap.add_argument("--dry-run", action="store_true", help="say what would be updated, update nothing")
    args = ap.parse_args()
    if args.prs:
        try:
            prs = json.loads(Path(args.prs).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"✗ PR ro'yxati o'qilmadi: {exc}")
            return 2
    else:
        proc = subprocess.run(
            ["gh", "pr", "list", "--state", "open", "--base", "main", "--json", FIELDS, "--limit", "50"],
            cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
        )
        if proc.returncode != 0:
            return 0  # GitHub unreadable: nothing to do this tick
        try:
            prs = json.loads(proc.stdout)
        except json.JSONDecodeError:
            return 0
    number, why = choose(prs)
    if number is None:
        return 0  # quiet: the watcher logs only actions
    if args.dry_run or args.prs:
        print(f"PR #{number} main bilan yangilanardi ({why})")
        return 0
    proc = subprocess.run(
        ["gh", "pr", "update-branch", str(number)],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
    )
    if proc.returncode == 0:
        print(f"PR #{number} main bilan yangilandi ({why})")
    else:
        print(f"PR #{number} yangilanmadi: {proc.stderr.strip()[:160]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
