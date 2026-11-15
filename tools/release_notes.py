#!/usr/bin/env python3
"""Weekly GitHub release from the merged pull requests (Conventional Commits).

    python3 tools/release_notes.py             # create the release if there is news
    python3 tools/release_notes.py --dry-run   # print the notes, create nothing
    python3 tools/release_notes.py --selftest

The release points at the newest `deploy-*` tag (written by
`tools/deploy_record.py` after every successful deploy), so it names a commit
that really went live. The notes list the pull requests merged since the
previous release, grouped by their Conventional Commit type. No release
exists yet on the first run: the window is then the last seven days.

Owner decision 2026-11-15: release notes come from PR titles, and nothing is
published when nothing was merged.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone

SECTIONS = (
    ("feat", "Yangi imkoniyatlar"),
    ("fix", "Tuzatishlar"),
    ("perf", "Tezlik"),
    ("ci", "CI va deploy"),
    ("docs", "Hujjatlar"),
    ("test", "Testlar"),
    ("refactor", "Ichki o'zgarishlar"),
    ("chore", "Boshqa"),
    ("build", "Boshqa"),
    ("style", "Boshqa"),
    ("ops", "CI va deploy"),
)
TITLE = re.compile(r"^(?P<type>[a-z]+)(\((?P<scope>[^)]*)\))?(?P<bang>!)?: (?P<subject>.+)$")


def group(prs: list[dict]) -> str:
    """Markdown body: one section per heading, newest first inside it."""
    sections: dict[str, list[str]] = {}
    for pr in sorted(prs, key=lambda p: -p["number"]):
        match = TITLE.match(pr["title"])
        kind = match["type"] if match else "chore"
        heading = dict(SECTIONS).get(kind, "Boshqa")
        subject = match["subject"] if match else pr["title"]
        scope = f"**{match['scope']}**: " if match and match["scope"] else ""
        mark = " ⚠️ buzuvchi" if match and match["bang"] else ""
        sections.setdefault(heading, []).append(f"- {scope}{subject} (#{pr['number']}){mark}")
    order = [h for _, h in SECTIONS]
    out: list[str] = []
    for heading in dict.fromkeys(order):
        if heading in sections:
            out += [f"## {heading}", *sections[heading], ""]
    return "\n".join(out).rstrip() + "\n"


def gh(*args: str) -> str:
    proc = subprocess.run(["gh", *args], capture_output=True, text=True, encoding="utf-8", timeout=60, check=False)
    if proc.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args[:2])}: {proc.stderr.strip()[-200:]}")
    return proc.stdout


def latest_deploy_tag() -> str | None:
    # `matching-refs` filters on the server and returns every match, so the
    # newest tag is found however many deploys there have been.
    refs = json.loads(gh("api", "--paginate", "repos/{owner}/{repo}/git/matching-refs/tags/deploy-"))
    tags = sorted((r["ref"].removeprefix("refs/tags/") for r in refs), reverse=True)
    return tags[0] if tags else None


def since() -> str:
    try:
        published = gh("release", "list", "--limit", "1", "--json", "publishedAt", "-q", ".[0].publishedAt").strip()
    except RuntimeError:
        published = ""
    if published:
        return published
    return (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")


def main(argv: list[str]) -> int:
    # The notes carry non-ASCII (headings, a warning sign); a Windows console is cp1252.
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    if argv == ["--selftest"]:
        return selftest()
    dry = "--dry-run" in argv
    start = since()
    prs = json.loads(
        gh("pr", "list", "--state", "merged", "--search", f"merged:>={start}", "--limit", "200", "--json", "number,title")
    )
    if not prs:
        print("yangilik yo'q — release yaratilmadi")
        return 0
    body = group(prs)
    tag = latest_deploy_tag()
    if tag is None:
        print("deploy tag'i yo'q — release yaratilmadi")
        return 0
    title = f"Hafta {datetime.now(timezone.utc).strftime('%Y-%m-%d')}"
    print(f"{title} → {tag}: {len(prs)} ta PR")
    if dry:
        print(body)
        return 0
    # The release tag IS the deploy tag, so two releases cannot name one deploy.
    gh("release", "create", tag, "--title", title, "--notes", body, "--verify-tag")
    return 0


def selftest() -> int:
    prs = [
        {"number": 5, "title": "feat(web): add the hero"},
        {"number": 6, "title": "fix: the cache key"},
        {"number": 7, "title": "feat!: drop the old API"},
        {"number": 8, "title": "no convention here"},
        {"number": 9, "title": "ops: tag every deploy"},
    ]
    text = group(prs)
    assert text.index("## Yangi imkoniyatlar") < text.index("## Tuzatishlar") < text.index("## Boshqa"), text
    assert "- **web**: add the hero (#5)" in text
    assert "(#7) ⚠️ buzuvchi" in text
    assert "- no convention here (#8)" in text
    assert text.index("(#7)") < text.index("(#5)"), "newest first"
    assert "## CI va deploy\n- tag every deploy (#9)" in text
    assert group([]) == "\n"
    print("ok: release_notes selftest")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
