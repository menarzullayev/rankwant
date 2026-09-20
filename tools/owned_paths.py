"""owned_paths width — HITL 2026-09-20 `no-star-star`.

Slots are not roles, so a task card must not lock the whole tree. This module
is the predicate agents and `check_decisions.py` share. Named mutexes
(`PACKAGE_WRITE`, `HITL`, `DEPLOY`) are not globs; do not put them here.
"""

from __future__ import annotations

FORBIDDEN_EXACT = frozenset({"**", "*", ".", "./", "/", "~", ".."})
# One-segment directory names. A claim of `docs` or `docs/**` starves every
# docs task; `CONTRIBUTING.md` (a root file) is not in this set.
ROOT_DIRECTORIES = frozenset(
    {
        "apps",
        "compose",
        "docs",
        "services",
        "tests",
        "tools",
        ".cursor",
        ".github",
        ".githooks",
        "openapi",
    }
)

ILLEGAL_OWNED_PATHS = (
    "**",
    "*",
    ".",
    "/",
    "apps/**",
    "docs/**",
    "tools/**",
    "apps",
    "docs",
)

LEGAL_OWNED_PATHS = (
    "apps/web/**",
    "apps/web/src/layout/**",
    "docs/10-operations/**",
    "docs/10-operations/parallel-agents.md",
    "CONTRIBUTING.md",
    "CLAUDE.md",
    "tools/check_decisions.py",
    ".cursor/rules/parallel-agents.mdc",
    ".github/workflows/*",
)


def legal_owned_path(glob: str) -> bool:
    """True iff `glob` is a legal `owned_paths` entry under no-star-star."""
    raw = glob.strip().replace("\\", "/")
    if not raw or raw in FORBIDDEN_EXACT:
        return False
    directory_glob = False
    prefix = raw
    if prefix.endswith("/**"):
        directory_glob = True
        prefix = prefix[: -len("/**")]
    elif prefix.endswith("/*"):
        directory_glob = True
        prefix = prefix[: -len("/*")]
    if prefix.endswith("/"):
        directory_glob = True
        prefix = prefix.rstrip("/")
    if not prefix or prefix in FORBIDDEN_EXACT:
        return False
    segments = [part for part in prefix.split("/") if part]
    if not segments or any(part in FORBIDDEN_EXACT for part in segments):
        return False
    if len(segments) == 1:
        name = segments[0]
        if directory_glob or name in ROOT_DIRECTORIES:
            return False
        return True
    return True
