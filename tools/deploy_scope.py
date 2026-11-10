#!/usr/bin/env python3
"""Which compose services must bake between two commits.

Docs/tools-only ranges print nothing. A web-only range prints `web`.
Judge is included only when `services/judge-go` (or a global bake file)
changed. `--from-live` reads `org.rankwant.git-sha` from running containers;
if a label is missing the script prints every service (cannot prove skip).
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from collections.abc import Callable
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ALL_SERVICES: tuple[str, ...] = ("api", "worker", "beat", "judge", "web", "realtime")

SERVICE_PATHS: dict[str, tuple[str, ...]] = {
    "api": ("apps/api",),
    "worker": ("apps/api",),
    "beat": ("apps/api",),
    #: SSE xizmati (ADR-0029). `apps/api` — chunki u AYNI obrazdan quriladi
    #: (`build: *api-build`), ya'ni api kodi o'zgarsa u ham yangilanishi
    #: shart. Ochilgan oqimlar uziladi-yu, `EventSource` qayta ulanadi va
    #: replay buferi yo'qolganini to'ldiradi.
    "realtime": ("apps/api",),
    #: The web build context is the repo root (`apps/web/Dockerfile` copies
    #: the workspace manifests, the lockfile and `packages/shared`), so a
    #: change there is a web change too.
    "web": (
        "apps/web",
        "packages",
        "package.json",
        "package-lock.json",
        ".dockerignore",
    ),
    "judge": ("services/judge-go",),
}

# deploy.sh changes how every image is built — every image, not just one.
GLOBAL_PATHS: tuple[str, ...] = ("tools/deploy.sh",)

# A compose edit rebuilds only the services whose resolved `build:` section
# changed. Everything else in a service (env, ports, volumes) is container
# config: `deploy.sh` runs `up` over every service and compose recreates
# exactly the containers whose config drifted. Until 2026-11-11 any compose
# edit rebuilt all six images; on 2026-11-10, six of seven judge rebuilds came
# from compose edits that did not touch the judge's build, and each one wrote
# 10.7 GB into Docker's disk (measured: importing the toolchain base image
# into the build cache).
COMPOSE_PATHS: tuple[str, ...] = (
    "docker-compose.yml",
    "docker-compose.public.yml",
)

ChangedFn = Callable[[str, str, tuple[str, ...]], bool]
#: `build_changed(old, new, service)` — did that service's resolved `build:`
#: section differ between the two commits? Unreadable must answer True.
BuildChangedFn = Callable[[str, str, str], bool]


def compute_scope(
    old: str | dict[str, str],
    new: str,
    *,
    changed: ChangedFn,
    build_changed: BuildChangedFn | None = None,
) -> list[str]:
    """Return services whose image inputs changed from `old` to `new`.

    Without `build_changed` a compose edit rebuilds every service, as before:
    nothing proves a build section stayed the same.
    """
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
            continue
        if changed(sha, new, COMPOSE_PATHS) and (
            build_changed is None or build_changed(sha, new, name)
        ):
            out.append(name)
    return out


def compose_builds(sha: str, cwd: Path) -> dict[str, str] | None:
    """Each service's resolved `build:` section at `sha`, as canonical JSON.

    `--no-interpolate` keeps `${GIT_SHA}` and friends as written, so the
    per-deploy values do not count as a change and no env file is needed;
    `--no-path-resolution` keeps contexts relative to the repo. None when the
    files cannot be read or resolved.
    """
    with tempfile.TemporaryDirectory() as tmp:
        for name in COMPOSE_PATHS:
            proc = subprocess.run(
                ["git", "show", f"{sha}:{name}"],
                cwd=cwd,
                capture_output=True,
                check=False,
            )
            if proc.returncode != 0:
                return None
            (Path(tmp) / name).write_bytes(proc.stdout)
        args = ["docker", "compose", "-p", "rankwant-scope"]
        for name in COMPOSE_PATHS:
            args += ["-f", name]
        args += [
            "config",
            "--no-interpolate",
            "--no-path-resolution",
            "--format",
            "json",
        ]
        proc = subprocess.run(
            args,
            cwd=tmp,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    if proc.returncode != 0:
        return None
    try:
        services = json.loads(proc.stdout)["services"]
    except (ValueError, KeyError, TypeError):
        return None
    return {
        name: json.dumps(spec.get("build"), sort_keys=True)
        for name, spec in services.items()
        if isinstance(spec, dict)
    }


def git_build_changed(cwd: Path) -> BuildChangedFn:
    cache: dict[str, dict[str, str] | None] = {}

    def builds(sha: str) -> dict[str, str] | None:
        if sha not in cache:
            cache[sha] = compose_builds(sha, cwd)
        return cache[sha]

    def build_changed(old: str, new: str, service: str) -> bool:
        left, right = builds(old), builds(new)
        if left is None or right is None:
            return True
        return left.get(service) != right.get(service)

    return build_changed


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
    parser.add_argument(
        "--from", dest="old", default="", help="base commit (or --from-live)"
    )
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

    scope = compute_scope(
        old, args.new, changed=changed, build_changed=git_build_changed(cwd)
    )
    if scope:
        print(" ".join(scope))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
