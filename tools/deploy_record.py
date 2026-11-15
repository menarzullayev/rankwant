#!/usr/bin/env python3
"""Leave a GitHub record of a deploy: a Deployment with its status and a tag.

    python3 tools/deploy_record.py success <sha>
    python3 tools/deploy_record.py failure <sha>
    python3 tools/deploy_record.py --selftest

The watcher (`tools/auto_deploy.sh`) calls this after a deploy and never lets
it change the deploy's outcome: a GitHub outage must not turn a finished
deploy into a failed one (owner decision 2026-11-15).

What it writes, with the `gh` the watcher already uses:

* a Deployment for environment `production` at `<sha>` and a status for it
  (`success` or `failure`), so a pull request shows "deployed" and the
  Environments page keeps a history;
* on success, a lightweight tag `deploy-YYYYMMDD-HHMM-<sha7>`, so "which commit
  is live" is visible on GitHub too, and the weekly release notes have a ref.

Both calls are idempotent enough to repeat: a tag that exists is left alone.
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone

ENVIRONMENT = "production"
SITE_URL = "https://rankwant.uz"
TAG_PREFIX = "deploy-"


def tag_name(sha: str, now: datetime) -> str:
    """`deploy-20261115-1432-0123abc` — sortable, and the short SHA names the commit."""
    return f"{TAG_PREFIX}{now.strftime('%Y%m%d-%H%M')}-{sha[:7]}"


def gh(*args: str, payload: dict | None = None) -> tuple[int, str]:
    proc = subprocess.run(
        ["gh", *args],
        input=json.dumps(payload) if payload is not None else None,
        capture_output=True,
        text=True,
        timeout=40,
    )
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def repo() -> str:
    code, out = gh("repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner")
    if code != 0:
        raise RuntimeError(f"repo noma'lum: {out.strip()[-120:]}")
    return out.strip()


def record(state: str, sha: str) -> int:
    slug = repo()
    code, out = gh(
        "api", f"repos/{slug}/deployments", "--input", "-",
        payload={
            "ref": sha,
            "environment": ENVIRONMENT,
            "auto_merge": False,
            "required_contexts": [],
            "transient_environment": False,
            "production_environment": True,
            "description": "RankWant auto-deploy",
        },
    )
    if code != 0:
        print(f"deployment yaratilmadi: {out.strip()[-160:]}")
        return 1
    deployment_id = json.loads(out)["id"]
    code, out = gh(
        "api", f"repos/{slug}/deployments/{deployment_id}/statuses", "--input", "-",
        payload={"state": state, "environment_url": SITE_URL, "auto_inactive": True},
    )
    if code != 0:
        print(f"deployment holati yozilmadi: {out.strip()[-160:]}")
        return 1
    print(f"deployment {deployment_id}: {state}")
    if state != "success":
        return 0
    tag = tag_name(sha, datetime.now(timezone.utc))
    code, out = gh("api", f"repos/{slug}/git/refs", "--input", "-", payload={"ref": f"refs/tags/{tag}", "sha": sha})
    if code != 0 and "already exists" not in out:
        print(f"tag yozilmadi: {out.strip()[-160:]}")
        return 1
    print(f"tag {tag}")
    return 0


def selftest() -> int:
    when = datetime(2026, 11, 15, 14, 32, tzinfo=timezone.utc)
    assert tag_name("0123456789abcdef", when) == "deploy-20261115-1432-0123456", tag_name("0123456789abcdef", when)
    assert tag_name("abc", when).startswith(TAG_PREFIX)
    names = sorted(
        [tag_name("a" * 40, datetime(2026, 11, 15, 9, 5, tzinfo=timezone.utc)), tag_name("b" * 40, when)]
    )
    assert names[0].endswith("aaaaaaa"), "tag nomlari vaqt bo'yicha tartiblanadi"
    print("ok: deploy_record selftest")
    return 0


def main(argv: list[str]) -> int:
    if argv == ["--selftest"]:
        return selftest()
    if len(argv) != 2 or argv[0] not in {"success", "failure"}:
        print(__doc__)
        return 2
    try:
        return record(argv[0], argv[1])
    except Exception as exc:  # the caller ignores the exit code; say why
        print(f"deploy_record: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
