#!/usr/bin/env python3
"""Pre-push guard: what may be pushed, and under whose name.

`.githooks/pre-push` pipes git's ref lines into this script
(`<local ref> <local sha> <remote ref> <remote sha>`, one per line).

Two rules, each backed by a measured incident:

* No direct updates to `main`. The repository is private on a free plan, so
  GitHub answers branch protection and rulesets with HTTP 403 — nothing on the
  server stops a push. Merges happen on GitHub through a PR. A human can
  override in an emergency with `RANKWANT_ALLOW_MAIN_PUSH=1`.
* No commits under a placeholder identity. On 2026-09-16 a negative test ran
  inside the real repository and left `user.email=test@example.com` in
  `.git/config`; 42 commits went out under that name before anyone noticed.

Only commits the remote does not have yet are checked, so published history
(mapped in `.mailmap`) never blocks a push. Raw `%ae`/`%ce` are used on
purpose: the mailmapped forms would hide exactly the identity we look for.

Exit codes: 0 allowed, 1 rejected, 2 git could not be read (fail closed).
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

import _console

_console.force_utf8()

PROTECTED_REFS = ("refs/heads/main",)
OVERRIDE_ENV = "RANKWANT_ALLOW_MAIN_PUSH"

# RFC 2606 / RFC 6761 reserved names — never a real mailbox.
_PLACEHOLDER_DOMAIN = re.compile(
    r"(^|\.)(example\.(com|net|org)|example|invalid|localhost|localdomain|test)$",
    re.IGNORECASE,
)
_ZERO_SHA = re.compile(r"^0+$")


class GitError(RuntimeError):
    pass


def is_placeholder(email: str) -> bool:
    local, at, domain = email.strip().rpartition("@")
    if not at or not local or not domain:
        return True
    return bool(_PLACEHOLDER_DOMAIN.search(domain))


def _git(repo: Path, *args: str, allow_fail: bool = False) -> str | None:
    proc = subprocess.run(
        ["git", *args],
        cwd=repo,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode != 0:
        if allow_fail:
            return None
        raise GitError(f"git {' '.join(args)}: {proc.stderr.strip() or proc.returncode}")
    return proc.stdout


def _remote_exclusions(repo: Path, remote: str, remote_sha: str) -> list[str]:
    # `remote` is a URL when pushing without a named remote; fall back to every
    # remote-tracking ref instead of treating the whole history as new.
    named = _git(repo, "for-each-ref", "--count=1", f"refs/remotes/{remote}/")
    exclude = [f"--remotes={remote}"] if named else ["--remotes"]
    if not _ZERO_SHA.match(remote_sha):
        if _git(repo, "cat-file", "-e", f"{remote_sha}^{{commit}}", allow_fail=True) is not None:
            exclude.append(remote_sha)
    return exclude


def _new_commits(repo: Path, local_sha: str, remote: str, remote_sha: str) -> list[list[str]]:
    out = _git(
        repo,
        "log",
        "--format=%h%x1f%an%x1f%ae%x1f%ce%x1f%s",
        local_sha,
        "--not",
        *_remote_exclusions(repo, remote, remote_sha),
    )
    return [line.split("\x1f") for line in (out or "").splitlines() if line]


def check(repo: Path, remote: str, ref_lines: list[str], env: dict[str, str]) -> list[str]:
    problems: list[str] = []

    configured = (_git(repo, "config", "--get", "user.email", allow_fail=True) or "").strip()
    if configured and is_placeholder(configured):
        origin = (
            _git(repo, "config", "--show-origin", "--get", "user.email", allow_fail=True) or ""
        ).split("\t")[0]
        problems.append(
            f"✗ Git identity soxta: user.email={configured} ({origin}).\n"
            "  Tuzatish: git config --local --unset user.email && "
            "git config --local --unset user.name"
        )

    for line in ref_lines:
        parts = line.split()
        if not parts:
            continue
        if len(parts) != 4:
            raise GitError(f"push qatori o'qilmadi: {line!r}")
        _local_ref, local_sha, remote_ref, remote_sha = parts

        if remote_ref in PROTECTED_REFS and env.get(OVERRIDE_ENV) != "1":
            branch = remote_ref.removeprefix("refs/heads/")
            problems.append(
                f"✗ `{branch}` ga to'g'ridan-to'g'ri push yopiq (CONTRIBUTING.md).\n"
                "  Branch oching va PR orqali birlashtiring:\n"
                "    git switch -c <tur>/<nom> && git push -u origin HEAD && gh pr create\n"
                "  GitHub bu repoda branch protection bermaydi (bepul private tarif, 403) —\n"
                "  qoidani shu hook ushlab turadi. Favqulodda holat, faqat odam qarori bilan:\n"
                f"    {OVERRIDE_ENV}=1 git push ..."
            )

        if _ZERO_SHA.match(local_sha):
            continue  # branch deletion: nothing new to inspect
        bad = [
            row
            for row in _new_commits(repo, local_sha, remote, remote_sha)
            if is_placeholder(row[2]) or is_placeholder(row[3])
        ]
        if bad:
            rows = "\n".join(
                f"    {h}  {name} <{ae}>  {subject}" for h, name, ae, _ce, subject in bad
            )
            problems.append(
                f"✗ {len(bad)} ta commit soxta muallif nomi bilan push qilinmoqda:\n{rows}\n"
                "  Identity'ni tuzating, keyin commit'larni qayta yozing:\n"
                "    git rebase -r <asos> --exec 'git commit --amend --no-edit --reset-author'"
            )

    return problems


def main(argv: list[str]) -> int:
    remote = argv[1] if len(argv) > 1 else "origin"
    repo = Path.cwd()
    try:
        problems = check(repo, remote, sys.stdin.read().splitlines(), dict(os.environ))
    except GitError as exc:
        print(f"✗ push guard: holatni o'qib bo'lmadi — {exc}", file=sys.stderr)
        return 2
    for problem in problems:
        print(problem, file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
