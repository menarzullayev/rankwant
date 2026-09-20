#!/usr/bin/env python3
"""Which compose services must bake between two commits.

Docs/tools-only ranges print nothing. A web-only range prints `web`.
Judge is included only when `services/judge-go` (or a global bake file)
changed. `--from-live` reads `org.rankwant.git-sha` from running containers;
if a label is missing the script prints every service (cannot prove skip).
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ALL_SERVICES: tuple[str, ...] = ("api", "worker", "beat", "judge", "web")

SERVICE_PATHS: dict[str, tuple[str, ...]] = {
    "api": ("apps/api",),
    "worker": ("apps/api",),
    "beat": ("apps/api",),
    "web": ("apps/web",),
    "judge": ("services/judge-go",),
}

# Compose / deploy.sh change the bake itself — every image, not just one.
GLOBAL_PATHS: tuple[str, ...] = (
    "docker-compose.yml",
    "docker-compose.public.yml",
    "tools/deploy.sh",
)

ChangedFn = Callable[[str, str, tuple[str, ...]], bool]


def compute_scope(
    old: str | dict[str, str],
    new: str,
    *,
    changed: ChangedFn,
) -> list[str]:
    """Return services whose image context changed from `old` to `new`."""
    if isinstance(old, str):
        shas = {name: old for name in ALL_SERVICES}
    else:
        shas = {name: old.get(name, "") for name in ALL_SERVICES}

    seen: set[str] = set()
    for sha in shas.values():
        if not sha or sha in seen:
            continue
        seen.add(sha)
        if changed(sha, new, GLOBAL_PATHS):
            return list(ALL_SERVICES)

    out: list[str] = []
    for name in ALL_SERVICES:
        sha = shas[name]
        if not sha:
            out.append(name)
            continue
        if changed(sha, new, SERVICE_PATHS[name]):
            out.append(name)
    return out


def git_changed(old: str, new: str, paths: tuple[str, ...], cwd: Path) -> bool:
    proc = subprocess.run(
        ["git", "diff", "--quiet", old, new, "--", *paths],
        cwd=cwd,
        capture_output=True,
    )
    # 0 same, 1 different, anything else (missing sha) → treat as different.
    return proc.returncode != 0


def live_shas() -> dict[str, str] | None:
    """Per-service git-sha labels, or None if any label is unreadable."""
    out: dict[str, str] = {}
    for name in ALL_SERVICES:
        proc = subprocess.run(
            [
                "docker",
                "inspect",
                f"rankwant-{name}-1",
                "--format",
                '{{index .Config.Labels "org.rankwant.git-sha"}}',
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        sha = (proc.stdout or "").strip()
        if proc.returncode != 0 or not sha or sha in ("unknown", "<no value>"):
            return None
        out[name] = sha
    return out


def _parse_argv(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from", dest="old", default="", help="base commit (or --from-live)")
    parser.add_argument("--to", dest="new", default="HEAD", help="target commit")
    parser.add_argument(
        "--from-live",
        action="store_true",
        help="read org.rankwant.git-sha from rankwant-*-1 containers",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_argv(argv if argv is not None else sys.argv[1:])
    cwd = ROOT
    if args.from_live:
        labels = live_shas()
        if labels is None:
            print(" ".join(ALL_SERVICES))
            return 0
        old: str | dict[str, str] = labels
    else:
        if not args.old:
            print("deploy_scope.py: --from SHA yoki --from-live kerak", file=sys.stderr)
            return 2
        old = args.old

    def changed(left: str, right: str, paths: tuple[str, ...]) -> bool:
        return git_changed(left, right, paths, cwd)

    scope = compute_scope(old, args.new, changed=changed)
    if scope:
        print(" ".join(scope))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
