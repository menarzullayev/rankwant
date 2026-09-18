#!/usr/bin/env python3
"""After a reboot: did everything that must come back on its own actually come back?

Owner decision (2026-09-17): the recovery chain is measured at the next natural reboot,
not by rebooting on purpose. Until that day nothing exercises it, and the chain changed
the same day: the WSL runner and its keepalive tasks are gone, CI runs in
`rankwant-ci-runner` (`restart: unless-stopped`). A second container
(`rankwant-ci-runner-2`) is optional until it is commissioned: if GitHub
lists it or the container is up, both sides must be healthy.
Run this once after the machine is back; it measures each link and exits 0 only if all hold.

Exit codes: 0 every link is back, 1 at least one is not, 2 facts could not be collected
(docker or gh missing). Unknown is never OK.

Tests pass collected facts instead of asking docker, gh and the network:
  --facts FILE   (JSON as `--dump-facts` prints)
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

import _console

_console.force_utf8()

REPO = "menarzullayev/rankwant"
# (container name, GitHub runner name). The first is always required. Later
# pairs are required only once commissioned (container up or GitHub registration).
RUNNERS = (
    ("rankwant-ci-runner", "nsn-pc-rankwant-container"),
    ("rankwant-ci-runner-2", "nsn-pc-rankwant-container-2"),
)
SERVICES = ("api", "worker", "beat", "judge", "web", "postgres", "redis", "minio")
HEALTHCHECKED = ("api", "postgres", "redis")
TASKS = (
    "RankWant CI Runner Watchdog",
    "RankWant CI Daily Report",
    "RankWant Monthly Backup",
    "RankWant Tunnel Monitor",
)


class Unmeasured(Exception):
    pass


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            cmd, stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding="utf-8", errors="replace"
        )
    except OSError as exc:
        raise Unmeasured(f"{cmd[0]} ishga tushmadi: {exc}") from exc


def http_status(url: str, host: str | None = None) -> int:
    # Cloudflare answers Python's default User-Agent with 403 (measured 2026-09-17:
    # 403 for Python-urllib, 200 for this one and for curl), which would report a
    # healthy tunnel as broken.
    headers = {"User-Agent": "rankwant-ops-check/1.0"}
    if host:
        headers["Host"] = host
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=20) as resp:
            return resp.status
    except urllib.error.HTTPError as exc:
        return exc.code
    except (urllib.error.URLError, OSError):
        return 0


def collect() -> dict:
    facts: dict = {}
    info = run(["docker", "info", "--format", "{{.ServerVersion}}"])
    facts["docker_engine"] = info.returncode == 0
    ps = run(["docker", "ps", "--format", "{{.Names}}|{{.Status}}"])
    facts["containers"] = dict(line.split("|", 1) for line in ps.stdout.splitlines() if "|" in line)
    facts["origin_api"] = http_status("http://127.0.0.1:8301/api/v1/health/", "rankwant.uz")
    facts["origin_web"] = http_status("http://127.0.0.1:8300/", "rankwant.uz")
    facts["public_api"] = http_status("https://rankwant.uz/api/v1/health/")
    runners = run(["gh", "api", f"repos/{REPO}/actions/runners"])
    if runners.returncode != 0:
        raise Unmeasured(f"gh api runners: {runners.stderr.strip()[:160]}")
    facts["runners"] = json.loads(runners.stdout).get("runners", [])
    script = (
        "$out = @{}; foreach ($n in '" + "','".join(TASKS) + "') { $t = Get-ScheduledTask -TaskName $n -ErrorAction SilentlyContinue;"
        " if ($t) { $i = Get-ScheduledTaskInfo -TaskName $n; $out[$n] = @{ state = [string]$t.State;"
        " last_run = $i.LastRunTime.ToUniversalTime().ToString('o') } } };"
        " $boot = (Get-CimInstance Win32_OperatingSystem).LastBootUpTime.ToUniversalTime().ToString('o');"
        " @{ tasks = $out; boot = $boot } | ConvertTo-Json -Depth 4 -Compress"
    )
    tasks = run(["powershell.exe", "-NoProfile", "-Command", script])
    if tasks.returncode != 0:
        raise Unmeasured(f"scheduled tasks: {tasks.stderr.strip()[:160]}")
    windows = json.loads(tasks.stdout)
    facts["tasks"] = windows.get("tasks") or {}
    facts["boot"] = windows.get("boot")
    return facts


def evaluate(facts: dict) -> list[tuple[str, bool, str]]:
    rows: list[tuple[str, bool, str]] = []
    rows.append(("Docker Desktop engine", facts.get("docker_engine") is True, "docker info"))
    containers = facts.get("containers", {})
    for service in SERVICES:
        name = f"rankwant-{service}-1"
        status = containers.get(name, "")
        ok = status.startswith("Up") and (service not in HEALTHCHECKED or "(healthy)" in status)
        rows.append((f"konteyner {name}", ok, status or "yo'q"))
    github_runners = {r.get("name"): r for r in facts.get("runners", [])}
    for index, (container, gh_name) in enumerate(RUNNERS):
        commissioned = index == 0 or container in containers or gh_name in github_runners
        if not commissioned:
            continue
        runner_status = containers.get(container, "")
        rows.append((f"konteyner {container}", runner_status.startswith("Up"), runner_status or "yo'q"))
        runner = github_runners.get(gh_name)
        labels = {label.get("name") for label in (runner or {}).get("labels", [])}
        rows.append((
            f"GitHub runner {gh_name}",
            runner is not None and runner.get("status") == "online" and "rankwant" in labels,
            "yo'q" if runner is None else f"{runner.get('status')}, labels={','.join(sorted(labels))}",
        ))
    for key, label in (("origin_api", "origin API :8301"), ("origin_web", "origin web :8300"), ("public_api", "rankwant.uz API (tunnel)")):
        code = facts.get(key)
        rows.append((label, code == 200, str(code)))
    tasks = facts.get("tasks", {})
    boot = str(facts.get("boot") or "")
    for name in TASKS:
        task = tasks.get(name)
        if task is None:
            rows.append((f"vazifa {name}", False, "yo'q"))
            continue
        ok = task.get("state") in ("Ready", "Running")
        detail = f"{task.get('state')}, oxirgi yurish {task.get('last_run')}"
        if name == "RankWant CI Runner Watchdog":
            # It runs every 2 minutes, so it must have run since the machine came back.
            ok = ok and bool(boot) and str(task.get("last_run") or "") > boot
        rows.append((f"vazifa {name}", ok, detail))
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--facts", type=Path, help="test fixture: collected facts as JSON")
    ap.add_argument("--dump-facts", action="store_true", help="print the collected facts as JSON and exit")
    args = ap.parse_args()
    try:
        if args.facts:
            try:
                facts = json.loads(args.facts.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                raise Unmeasured(f"{args.facts}: {exc}") from exc
        else:
            facts = collect()
    except (Unmeasured, json.JSONDecodeError) as exc:
        print(f"✗ Reboot tekshiruvi: o'lchab bo'lmadi — {exc}")
        return 2
    if args.dump_facts:
        print(json.dumps(facts, indent=2, ensure_ascii=False))
        return 0
    rows = evaluate(facts)
    width = max(len(label) for label, _, _ in rows)
    print(f"Oxirgi yuklanish (UTC): {facts.get('boot') or '?'}")
    for label, ok, detail in rows:
        print(f"  {'✓' if ok else '✗'} {label.ljust(width)}  {detail}")
    failed = [label for label, ok, _ in rows if not ok]
    if failed:
        print(f"✗ {len(failed)} ta halqa qaytmagan: {', '.join(failed)}")
        return 1
    print(f"✓ Hamma {len(rows)} halqa reboot'dan keyin qo'lsiz qaytgan")
    return 0


if __name__ == "__main__":
    sys.exit(main())
