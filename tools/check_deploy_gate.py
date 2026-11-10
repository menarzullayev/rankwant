#!/usr/bin/env python3
"""Deploy gate: agents may deploy only a `main` commit whose CI is green.

Owner decision (2026-09-17, CLAUDE.md § "Saidakbar aka qarorlari"): agents
deploy production without asking, provided `main` CI is green. That morning
production had been redeployed from the main checkout with nothing recording
who did it or whether CI had passed. `tools/deploy.sh` runs this gate before it
builds anything.

The gate passes only when all three hold:
1. HEAD is the commit that `main` points to on GitHub right now, so production
   cannot drift to an unmerged or stale commit;
2. the latest `CI` run for that commit completed with `success`;
3. the live checkout and the deploy worktree have no uncommitted
   `docker-compose*.yml` changes (D56). Isolated AOP trees are not scanned.

Rule 3 is about what a deploy silently removes. On 2026-09-17 the live stack was
recreated from the main checkout with an edited, uncommitted `docker-compose.public.yml`
that passed the Turnstile keys and a raised register throttle to `api`. A deploy from a
worktree builds from the committed compose, so it would have dropped both without a word.
On 2026-09-21 that same all-worktree scan froze a green-main web bake because an
isolated ADMINER tree had an untracked `docker-compose.tools.yml` — a file
`deploy.sh` never reads. D56 keeps the 2026-09-17 check on the two trees a
deploy can actually apply.

Rule 2 has one shortcut (owner decision 2026-11-10, audit of deploy time).
While `main` CI has not finished, the merged PR's own CI counts when all of
these hold: `main` HEAD is the squash commit of a merged PR, its tree is
byte-for-byte that PR head's tree (true while the ruleset requires an
up-to-date branch, `strict`; measured on five PRs), the latest `CI` run on that
PR head completed with `success`, and the latest FINISHED `main` CI run was
green. Measured cost before: main CI re-tested the identical tree for a median
3:02 while the deploy waited. `main` CI still runs; when it fails the deploy
stops as before, and a red `main` run turns the shortcut off until `main` is
green again.

Exit codes: 0 deploy allowed, 1 not allowed, 2 could not be measured (git, gh or
the network failed). Unknown is never green: deploy.sh stops on 2 as well. A
shortcut that cannot be measured is simply not taken: the gate then waits for
`main` CI as before.

A checkout that disappears while the gate runs is skipped, not an error. Agents
remove their merged worktrees as a matter of course; on 2026-09-18 one did so
between the gate's `git worktree list` and its `git status`, and the gate stopped
a deploy with "not a git repository" (exit 2). A directory that is gone holds
nothing a deploy could drop. Any other failure still stops the deploy.

Tests pass fixtures instead of asking git and GitHub:
  --head SHA --main SHA --runs FILE   (FILE: JSON as `gh run list --json` prints)
  --pr FILE                           (FILE: JSON evidence for the shortcut, see
                                       `pr_evidence`; without it, fixtures take
                                       no shortcut and never touch GitHub)
  --compose-status FILE               (FILE: JSON list of dirty compose entries)
  --checkouts FILE                    (FILE: JSON list of checkout paths to scan)
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import _console

_console.force_utf8()

ROOT = Path(__file__).resolve().parent.parent
REQUIRED = ("CI",)
RUN_FIELDS = "workflowName,status,conclusion,createdAt"
COMPOSE_PATHSPEC = "docker-compose*.yml"
# Same defaults as `tools/auto_deploy.sh`. Override in tests.
LIVE_DIR = Path(os.environ.get("RANKWANT_LIVE_DIR", "D:/Linux/Web_Projects/rankwant"))
DEPLOY_DIR = Path(os.environ.get("RANKWANT_DEPLOY_DIR", "D:/Windows/project/wt/deploy"))


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


def _norm(path: Path) -> str:
    return str(path).replace("\\", "/").rstrip("/").lower()


def checkouts() -> list[str]:
    """Live stack checkout + deploy worktree — not every AOP tree (D56).

    `deploy.sh` builds committed compose from the deploy tree (or the live
    checkout if someone runs it there). An isolated agent's untracked
    `docker-compose.tools.yml` cannot be what the bake applies, so it must
    not close the gate. `--checkouts` still overrides this list in tests.
    """
    found: list[str] = []
    seen: set[str] = set()
    for path in (LIVE_DIR, DEPLOY_DIR):
        if not path.is_dir():
            continue
        key = _norm(path)
        if key in seen:
            continue
        seen.add(key)
        found.append(str(path))
    return found


def dirty_compose(paths: list[str]) -> list[str]:
    """Uncommitted compose changes in any checkout, as `<checkout>: <status> <file>`."""
    # Each checkout answers for itself. An inherited `GIT_DIR` (git exports it
    # to hooks) would make every `git -C <path>` report on that one repository.
    env = {k: v for k, v in os.environ.items() if k not in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE")}
    found = []
    for path in paths:
        # Removed by its owner (see the module docstring): nothing to scan.
        if not Path(path).is_dir():
            continue
        proc = subprocess.run(
            ["git", "-C", path, "status", "--porcelain", "--", COMPOSE_PATHSPEC],
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=env,
        )
        if proc.returncode != 0:
            # Removed between the check above and `git status`.
            if not Path(path).is_dir():
                continue
            raise Unmeasured(f"git status ({path}): {proc.stderr.strip()[:120]}")
        found += [f"{path}: {line.strip()}" for line in proc.stdout.splitlines() if line.strip()]
    return found


def read_checkouts(file: str) -> list[str]:
    """The `--checkouts` fixture: a JSON list of paths."""
    try:
        paths = json.loads(Path(file).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise Unmeasured(f"{file}: {exc}") from exc
    if not isinstance(paths, list):
        raise Unmeasured(f"{file}: checkout ro'yxati massiv emas")
    return [str(path) for path in paths]


def parse_dirty(text: str) -> list[str]:
    try:
        entries = json.loads(text)
    except json.JSONDecodeError as exc:
        raise Unmeasured(f"compose holati JSON emas: {exc}") from exc
    if not isinstance(entries, list):
        raise Unmeasured("compose holati massiv emas")
    return [str(entry) for entry in entries]


def gh_json(*args: str):
    try:
        proc = subprocess.run(
            ["gh", *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8"
        )
    except OSError as exc:
        raise Unmeasured(f"gh ishga tushmadi: {exc}") from exc
    if proc.returncode != 0:
        raise Unmeasured(f"gh {' '.join(args[:2])}: {proc.stderr.strip()[:160]}")
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise Unmeasured(f"gh {' '.join(args[:2])}: JSON emas: {exc}") from exc


def pr_evidence(sha: str) -> dict | None:
    """What the shortcut needs, read from GitHub: the merged PR behind `sha`.

    Returns None when `sha` is not a PR's squash commit (a direct push, a merge
    from elsewhere): then there is nothing to trust but `main` CI.
    """
    pulls = gh_json("api", f"repos/{{owner}}/{{repo}}/commits/{sha}/pulls")
    pr = next(
        (p for p in pulls if p.get("merge_commit_sha") == sha and p.get("merged_at")), None
    )
    if pr is None:
        return None
    head = pr["head"]["sha"]
    head_tree = gh_json("api", f"repos/{{owner}}/{{repo}}/git/commits/{head}")["tree"]["sha"]
    pr_runs = gh_json(
        "run", "list", "--commit", head, "--workflow", "CI", "--event", "pull_request",
        "--json", RUN_FIELDS, "--limit", "20",
    )
    history = gh_json(
        "run", "list", "--branch", "main", "--workflow", "CI", "--event", "push",
        "--json", "headSha,status,conclusion,createdAt", "--limit", "10",
    )
    return {
        "number": pr["number"],
        "head": head,
        "head_tree": head_tree,
        "main_tree": git("rev-parse", f"{sha}^{{tree}}"),
        "pr_runs": pr_runs,
        "main_history": history,
    }


def shortcut(head: str, ev: dict | None) -> tuple[bool, str]:
    """May the merged PR's CI stand in for an unfinished `main` CI run?"""
    if not ev:
        return False, "PR yorlig'i yo'q (main CI kutiladi)"
    done = [
        r for r in ev.get("main_history", [])
        if r.get("status") == "completed" and r.get("headSha") != head
    ]
    if done:
        last = max(done, key=lambda r: str(r.get("createdAt", "")))
        if last.get("conclusion") != "success":
            return False, (
                f"oxirgi tugagan main CI ({str(last.get('headSha'))[:7]}) "
                f"`{last.get('conclusion')}` — PR CI qabul qilinmaydi, main CI kutiladi"
            )
    if not ev.get("head_tree") or ev.get("head_tree") != ev.get("main_tree"):
        return False, (
            f"main daraxti PR #{ev.get('number')} daraxtidan farq qiladi — main CI kutiladi"
        )
    pr_ci = sorted(
        (r for r in ev.get("pr_runs", []) if r.get("workflowName") == "CI"),
        key=lambda r: str(r.get("createdAt", "")),
    )
    if not pr_ci:
        return False, f"PR #{ev.get('number')} da `CI` run'i yo'q — main CI kutiladi"
    last_pr = pr_ci[-1]
    if last_pr.get("status") != "completed" or last_pr.get("conclusion") != "success":
        return False, (
            f"PR #{ev.get('number')} CI `{last_pr.get('conclusion') or last_pr.get('status')}` "
            "— main CI kutiladi"
        )
    return True, f"PR #{ev.get('number')} CI yashil, daraxt bir xil ({str(ev['main_tree'])[:7]})"


def verdict(
    head: str, main: str, runs: list[dict], dirty: list[str], ev: dict | None = None
) -> list[str]:
    # A dirty compose blocks on its own: the live stack may be running it, and a
    # deploy builds from the committed one.
    blocking = [f"commit qilinmagan compose — {entry}" for entry in dirty]
    if head != main:
        return blocking + [
            f"HEAD {head[:7]} `main` emas (GitHub'da main = {main[:7]}) — "
            "faqat main deploy qilinadi"
        ]
    latest: dict[str, dict] = {}
    for run in sorted(runs, key=lambda r: str(r.get("createdAt", ""))):
        latest[str(run.get("workflowName"))] = run  # a rerun replaces the earlier result
    problems = list(blocking)
    for name in REQUIRED:
        run = latest.get(name)
        if run is not None and run.get("status") == "completed":
            # A finished main run is the final word, green or red.
            if run.get("conclusion") != "success":
                problems.append(f"`{name}` natijasi `{run.get('conclusion')}`")
            continue
        ok, why = shortcut(head, ev)
        if ok:
            continue
        state = "yo'q" if run is None else f"hali tugamagan ({run.get('status')})"
        problems.append(f"`{name}` run'i {head[:7]} uchun {state}; {why}")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--head", help="test fixture: HEAD commit")
    ap.add_argument("--main", help="test fixture: GitHub main commit")
    ap.add_argument("--runs", help="test fixture: JSON file of runs")
    ap.add_argument("--compose-status", help="test fixture: JSON file of dirty compose entries")
    ap.add_argument("--checkouts", help="test fixture: JSON file listing checkout paths to scan")
    ap.add_argument("--pr", help="test fixture: JSON file of the merged-PR evidence")
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
        if args.compose_status:
            try:
                dirty = parse_dirty(Path(args.compose_status).read_text(encoding="utf-8"))
            except OSError as exc:
                raise Unmeasured(f"{args.compose_status}: {exc}") from exc
        else:
            dirty = dirty_compose(read_checkouts(args.checkouts) if args.checkouts else checkouts())
    except Unmeasured as exc:
        print(f"✗ Deploy darvozasi: o'lchab bo'lmadi — {exc}")
        return 2
    ev = None
    if args.pr:
        try:
            ev = json.loads(Path(args.pr).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"✗ Deploy darvozasi: o'lchab bo'lmadi — {args.pr}: {exc}")
            return 2
    elif not args.runs and head == main_sha and not finished(runs):
        # Only worth asking when main CI is still running. If GitHub cannot be
        # read, the shortcut is simply not taken: the gate waits as before.
        try:
            ev = pr_evidence(head)
        except Unmeasured as exc:
            ev = None
            print(f"  (PR CI yorlig'i o'qilmadi: {exc})")
    problems = verdict(head, main_sha, runs, dirty, ev)
    if problems:
        print("✗ Deploy darvozasi: deploy qilinmaydi (qaror: main CI yoki bir xil daraxtdagi PR CI yashil bo'lsa):")
        for problem in problems:
            print(f"  - {problem}")
        if dirty:
            print("  Jonli stack shu o'zgarish bilan ko'tarilgan bo'lishi mumkin va deploy uni")
            print("  jimgina olib tashlaydi. Avval o'zgarishni commit qiling (PR) yoki qaytaring.")
        return 1
    if finished(runs):
        print(f"✓ Deploy darvozasi: main {head[:7]} — {' va '.join(REQUIRED)} yashil")
    else:
        # Watchers read this line: `tools/auto_deploy.sh` keeps the commit and
        # reports main CI's own verdict once it lands.
        print(f"✓ Deploy darvozasi: main {head[:7]} — {shortcut(head, ev)[1]}; PR_CI_SHORTCUT")
    return 0


def finished(runs: list[dict]) -> bool:
    """Has the latest run of every required workflow completed?"""
    latest: dict[str, dict] = {}
    for run in sorted(runs, key=lambda r: str(r.get("createdAt", ""))):
        latest[str(run.get("workflowName"))] = run
    return all(latest.get(n, {}).get("status") == "completed" for n in REQUIRED)


if __name__ == "__main__":
    sys.exit(main())
