#!/usr/bin/env python3
"""Daily CI report: what ran on the runner in the last day, and what needs attention.

Since 2026-09-17 CI has one runner, the `rankwant-ci-runner` container, and a watchdog
that restarts it when it stops taking jobs (tools/runner_watchdog.py). Neither tells
anyone. A scheduled task runs this every morning and writes one markdown page, so a red
nightly, a stuck run or a watchdog restart is seen the next day rather than whenever
someone happens to look. Nothing leaves the machine.

usage:
  python tools/runner_report.py                        # ~/ci-runner/daily-report.md, last 24 h
  python tools/runner_report.py --hours 48 --out report.md

Exit codes: 0 report written, 2 GitHub could not be read. The report is still written in
that case and says what could not be read.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

import _console

_console.force_utf8()

REPO = "menarzullayev/rankwant"
HOME = Path.home()
DEFAULT_OUT = HOME / "ci-runner" / "daily-report.md"
WATCHDOG_LOG = HOME / "ci-runner" / "watchdog.log"
USER_AGENT = "rankwant-ops-check/1.0"  # Cloudflare answers Python's default one with 403


class Unmeasured(Exception):
    pass


def gh_api(path: str) -> dict:
    try:
        proc = subprocess.run(
            ["gh", "api", path],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except OSError as exc:
        raise Unmeasured(f"gh ishga tushmadi: {exc}") from exc
    if proc.returncode != 0:
        raise Unmeasured(f"gh api {path}: {proc.stderr.strip()[:160]}")
    return json.loads(proc.stdout)


def http_check(url: str, host: str | None = None) -> str:
    headers = {"User-Agent": USER_AGENT}
    if host:
        headers["Host"] = host
    started = datetime.now()
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=20) as resp:
            code = resp.status
    except urllib.error.HTTPError as exc:
        code = exc.code
    except (urllib.error.URLError, OSError) as exc:
        return f"javob yo'q ({exc})"
    return f"{code}, {(datetime.now() - started).total_seconds():.2f} s"


def local(stamp: str) -> str:
    return datetime.fromisoformat(stamp.replace("Z", "+00:00")).astimezone().strftime("%m-%d %H:%M")


def watchdog_events(since_local: datetime) -> list[str]:
    if not WATCHDOG_LOG.exists():
        return ["watchdog logi yo'q — vazifa o'rnatilganmi?"]
    events = []
    for line in WATCHDOG_LOG.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            moment = datetime.strptime(line[:19], "%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue
        if moment >= since_local:
            events.append(line.strip())
    return events


def build(hours: int) -> tuple[str, bool]:
    now = datetime.now(timezone.utc)
    since = now - timedelta(hours=hours)
    lines = [f"# CI kundalik hisobot — {now.astimezone():%Y-%m-%d %H:%M}", ""]
    attention: list[str] = []
    github_ok = True

    try:
        runners = gh_api(f"repos/{REPO}/actions/runners").get("runners", [])
        created = urllib.parse.quote(f">={since:%Y-%m-%dT%H:%M:%SZ}")
        runs = []
        for page in range(1, 11):  # a busy day on 2026-09-17 already filled one page of 100
            batch = gh_api(
                f"repos/{REPO}/actions/runs?created={created}&per_page=100&page={page}"
            ).get("workflow_runs", [])
            runs.extend(batch)
            if len(batch) < 100:
                break
    except (Unmeasured, json.JSONDecodeError) as exc:
        github_ok = False
        runners, runs = [], []
        attention.append(f"GitHub o'qilmadi: {exc}")

    rows = []
    for run in sorted(runs, key=lambda r: r["created_at"]):
        on: list[str] = []
        if run.get("conclusion") not in (None, "success", "skipped"):
            # Only failed runs are worth one more request each: where did they fail?
            try:
                jobs = gh_api(f"repos/{REPO}/actions/runs/{run['id']}/jobs?per_page=100").get("jobs", [])
                on = sorted({j.get("runner_name") for j in jobs if j.get("runner_name")})
            except (Unmeasured, json.JSONDecodeError):
                on = ["?"]
        minutes = (
            datetime.fromisoformat(run["updated_at"].replace("Z", "+00:00"))
            - datetime.fromisoformat(run["created_at"].replace("Z", "+00:00"))
        ).total_seconds() / 60
        outcome = run.get("conclusion") or run.get("status")
        rows.append(
            f"| {local(run['created_at'])} | {run['name']} | {run['event']} | {run.get('head_branch')} "
            f"| {outcome} | {minutes:.1f} min | {', '.join(on) or '-'} | [{run['id']}]({run['html_url']}) |"
        )
        if outcome not in ("success", "skipped", "in_progress", "queued"):
            attention.append(f"{run['name']} ({run.get('head_branch')}, {local(run['created_at'])}): {outcome}")
        elif outcome == "queued" and (now - datetime.fromisoformat(run["created_at"].replace("Z", "+00:00"))) > timedelta(minutes=30):
            attention.append(f"{run['name']} 30 daqiqadan ko'p navbatda: {run['html_url']}")

    for runner in runners:
        if runner.get("status") != "online":
            attention.append(f"runner {runner.get('name')} {runner.get('status')}")
    if github_ok and not any("rankwant" in {l.get("name") for l in r.get("labels", [])} for r in runners):
        attention.append("`rankwant` label'li runner yo'q — CI job'lari hech qayerda ishlamaydi")

    since_local = since.astimezone().replace(tzinfo=None)
    events = watchdog_events(since_local)
    if any("✓" in e or "✗" in e for e in events):
        attention.append("watchdog aralashgan yoki xato bergan — pastdagi bo'limga qarang")

    public = http_check("https://rankwant.uz/api/v1/health/")
    origin = http_check("http://127.0.0.1:8301/api/v1/health/", "rankwant.uz")
    for label, result in (("ommaviy API", public), ("origin API", origin)):
        if not result.startswith("200"):
            attention.append(f"{label}: {result}")
    free_gb = shutil.disk_usage(HOME.anchor or "/").free / 1024**3
    if free_gb < 25:
        attention.append(f"C: da faqat {free_gb:.1f} GB bo'sh")

    counts = Counter((r.get("conclusion") or r.get("status")) for r in runs)
    lines += ["## Holat", ""]
    lines += [f"- ⚠️ {item}" for item in attention] or ["- ✅ E'tibor talab qiladigan narsa yo'q"]
    lines += [
        "",
        f"Oxirgi {hours} soat: {len(runs)} ta run — "
        + (", ".join(f"{k} {v}" for k, v in counts.most_common()) or "run yo'q"),
        "",
        "## Runner'lar",
        "",
        "| Nomi | Holat | Band | Label'lar |",
        "| --- | --- | --- | --- |",
    ]
    lines += [
        f"| {r.get('name')} | {r.get('status')} | {r.get('busy')} | {', '.join(l.get('name') for l in r.get('labels', []))} |"
        for r in runners
    ] or ["| — | GitHub o'qilmadi | | |"]
    lines += [
        "",
        "## CI run'lari",
        "",
        "| Vaqt | Workflow | Event | Branch | Natija | Davomiylik | Runner | Run |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    lines += rows or ["| — | run yo'q | | | | | | |"]
    lines += ["", "## Watchdog", ""]
    lines += [f"- `{e}`" for e in events] or ["- hodisa yo'q"]
    lines += [
        "",
        "## Sayt va disk",
        "",
        f"- ommaviy API: {public}",
        f"- origin API: {origin}",
        f"- C: bo'sh joy: {free_gb:.1f} GB",
        "",
    ]
    return "\n".join(lines), github_ok


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--hours", type=int, default=24)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()
    report, github_ok = build(args.hours)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(report, encoding="utf-8")
    first = next((line for line in report.splitlines() if line.startswith("- ")), "")
    print(f"{args.out}: {first}")
    return 0 if github_ok else 2


if __name__ == "__main__":
    sys.exit(main())
