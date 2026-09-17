#!/usr/bin/env python3
"""Deploy gate: agents may deploy only a `main` commit whose CI is green.

Owner decision (2026-09-17, CLAUDE.md § "Saidakbar aka qarorlari"): agents
deploy production without asking, provided `main` CI is green. That morning
production had been redeployed from the main checkout with nothing recording
who did it or whether CI had passed. `tools/deploy.sh` runs this gate before it
builds anything.

The gate passes only when both hold:
1. HEAD is the commit that `main` points to on GitHub right now, so production
   cannot drift to an unmerged or stale commit;
2. the latest `CI` and `Security` runs for that commit completed with `success`.

Exit codes: 0 deploy allowed, 1 not allowed, 2 could not be measured (git, gh or
the network failed). Unknown is never green: deploy.sh stops on 2 as well.

Tests pass fixtures instead of asking git and GitHub:
  --head SHA --main SHA --runs FILE   (FILE: JSON as `gh run list --json` prints)
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
REQUIRED = ("CI", "Security")
RUN_FIELDS = "workflowName,status,conclusion,createdAt"


class Unmeasured(Exception):
    pass


def git(*args: str) -> str:
    proc = subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8"
    )
    if proc.returncode != 0:
        raise Unmeasured(f"git {' '.join(args)}: {proc.stderr.strip()[:160]}")
    return proc.stdout.strip()


def remote_main() -> str:
    # ls-remote asks GitHub directly: a stale local `origin/main` would let a
    # commit that is no longer the tip of main pass.
    line = git("ls-remote", "origin", "refs/heads/main")
    if not line:
        raise Unmeasured("origin'da refs/heads/main topilmadi")
    return line.split()[0]


def runs_for(sha: str) -> list[dict]:
    try:
        proc = subprocess.run(
            [
                "gh",
                "run",
                "list",
                "--branch",
                "main",
                "--commit",
                sha,
                "--json",
                RUN_FIELDS,
                "--limit",
                "20",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except OSError as exc:
        raise Unmeasured(f"gh ishga tushmadi: {exc}") from exc
    if proc.returncode != 0:
        raise Unmeasured(f"gh run list: {proc.stderr.strip()[:160]}")
    return parse_runs(proc.stdout)


def parse_runs(text: str) -> list[dict]:
    try:
        runs = json.loads(text)
    except json.JSONDecodeError as exc:
        raise Unmeasured(f"run ro'yxati JSON emas: {exc}") from exc
    if not isinstance(runs, list):
        raise Unmeasured("run ro'yxati massiv emas")
    return runs


def verdict(head: str, main: str, runs: list[dict]) -> list[str]:
    if head != main:
        return [
            f"HEAD {head[:7]} `main` emas (GitHub'da main = {main[:7]}) — "
            "faqat main deploy qilinadi"
        ]
    latest: dict[str, dict] = {}
    for run in sorted(runs, key=lambda r: str(r.get("createdAt", ""))):
        latest[str(run.get("workflowName"))] = run  # a rerun replaces the earlier result
    problems = []
    for name in REQUIRED:
        run = latest.get(name)
        if run is None:
            problems.append(f"`{name}` run'i {head[:7]} uchun yo'q")
        elif run.get("status") != "completed":
            problems.append(f"`{name}` hali tugamagan ({run.get('status')})")
        elif run.get("conclusion") != "success":
            problems.append(f"`{name}` natijasi `{run.get('conclusion')}`")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--head", help="test fixture: HEAD commit")
    ap.add_argument("--main", help="test fixture: GitHub main commit")
    ap.add_argument("--runs", help="test fixture: JSON file of runs")
    args = ap.parse_args()
    try:
        head = args.head or git("rev-parse", "HEAD")
        main_sha = args.main or remote_main()
        if args.runs:
            try:
                runs = parse_runs(Path(args.runs).read_text(encoding="utf-8"))
            except OSError as exc:
                raise Unmeasured(f"{args.runs}: {exc}") from exc
        else:
            runs = runs_for(head) if head == main_sha else []
    except Unmeasured as exc:
        print(f"✗ Deploy darvozasi: o'lchab bo'lmadi — {exc}")
        return 2
    problems = verdict(head, main_sha, runs)
    if problems:
        print("✗ Deploy darvozasi: deploy qilinmaydi (qaror: faqat main CI yashil bo'lsa):")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    print(f"✓ Deploy darvozasi: main {head[:7]} — {' va '.join(REQUIRED)} yashil")
    return 0


if __name__ == "__main__":
    sys.exit(main())
