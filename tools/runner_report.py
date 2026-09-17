#!/usr/bin/env python3
"""Daily CI report: what ran on the runner in the last day, and what needs attention.

Since 2026-09-17 CI has one runner, the `rankwant-ci-runner` container, and a watchdog
that restarts it when it stops taking jobs (tools/runner_watchdog.py). Neither tells
anyone. A scheduled task runs this every morning and writes one markdown page, so a red
nightly, a stuck run or a watchdog restart is seen the next day rather than whenever
someone happens to look. Nothing leaves the machine.

A file alone still waits for someone to open it, so when anything needs attention the
report also shows a Windows notification (owner decision, 2026-09-17). It stays on this
machine too.

usage:
  python tools/runner_report.py                        # ~/ci-runner/daily-report.md, last 24 h
  python tools/runner_report.py --hours 48 --out report.md
  python tools/runner_report.py --notify off           # no notification
  python tools/runner_report.py --attention items.json --notify print   # test fixture

Exit codes: 0 report written, 2 GitHub could not be read, 3 the report needs attention
but the notification could not be shown. The report is written in every case; 2 wins
over 3.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from xml.sax.saxutils import escape

import _console

_console.force_utf8()

REPO = "menarzullayev/rankwant"
HOME = Path.home()
DEFAULT_OUT = HOME / "ci-runner" / "daily-report.md"
WATCHDOG_LOG = HOME / "ci-runner" / "watchdog.log"
USER_AGENT = "rankwant-ops-check/1.0"  # Cloudflare answers Python's default one with 403
# Windows only shows toasts from registered app ids; PowerShell's is always there.
TOAST_APP_ID = r"{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\WindowsPowerShell\v1.0\powershell.exe"
TOAST_TAG = "rankwant-daily-report"  # same tag, so today's notification replaces yesterday's
TOAST_SCRIPT = """
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null
$doc = New-Object Windows.Data.Xml.Dom.XmlDocument
$doc.LoadXml($env:RW_TOAST_XML)
$toast = New-Object Windows.UI.Notifications.ToastNotification $doc
$toast.Tag = $env:RW_TOAST_TAG
$toast.Group = 'rankwant'
[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($env:RW_TOAST_APP).Show($toast)
"""


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


def toast_xml(attention: list[str], out: Path) -> str | None:
    """The notification for a report, or None when nothing needs attention."""
    if not attention:
        return None
    body = "; ".join(attention[:2])
    if len(body) > 180:
        body = body[:179] + "…"
    if len(attention) > 2:
        body += f" (+{len(attention) - 2})"
    texts = (f"RankWant CI: {len(attention)} ta e'tibor bandi", body, str(out))
    return (
        '<toast><visual><binding template="ToastGeneric">'
        + "".join(f"<text>{escape(t)}</text>" for t in texts)
        + "</binding></visual></toast>"
    )


def show_toast(xml: str) -> str | None:
    """Show the notification; returns why it failed, or None."""
    # The XML travels in the environment and the script as -EncodedCommand, so no
    # attention text is ever parsed as PowerShell.
    env = {**os.environ, "RW_TOAST_XML": xml, "RW_TOAST_APP": TOAST_APP_ID, "RW_TOAST_TAG": TOAST_TAG}
    encoded = base64.b64encode(TOAST_SCRIPT.encode("utf-16-le")).decode("ascii")
    try:
        proc = subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-EncodedCommand", encoded],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
            timeout=60,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return f"powershell ishga tushmadi: {exc}"
    if proc.returncode != 0:
        return (proc.stderr or proc.stdout).strip()[:200] or f"powershell exit {proc.returncode}"
    return None


def notify(attention: list[str], out: Path, mode: str) -> bool:
    """Notify per `mode`; False only when a needed notification could not be shown."""
    xml = toast_xml(attention, out)
    if xml is None or mode == "off":
        return True
    if mode == "print":
        print(xml)
        return True
    error = show_toast(xml)
    if error:
        print(f"bildirishnoma chiqmadi: {error}")
        return False
    print(f"bildirishnoma ko'rsatildi: {len(attention)} ta e'tibor bandi")
    return True


def build(hours: int) -> tuple[str, bool, list[str]]:
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
    return "\n".join(lines), github_ok, attention


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--hours", type=int, default=24)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument(
        "--notify",
        choices=("auto", "off", "print"),
        default="auto",
        help="auto: notify when something needs attention; off: never; print: print the toast instead",
    )
    ap.add_argument("--attention", type=Path, help="test fixture: attention items as a JSON list")
    args = ap.parse_args()

    if args.attention is not None:  # fixture: only the notification path, no report
        try:
            items = json.loads(args.attention.read_text(encoding="utf-8"))
            if not isinstance(items, list):
                raise TypeError(f"JSON ro'yxat emas: {type(items).__name__}")
            attention = [str(item) for item in items]
        except (OSError, ValueError, TypeError) as exc:
            print(f"e'tibor bandlari o'qilmadi: {exc}")
            return 2
        return 0 if notify(attention, args.out, args.notify) else 3

    report, github_ok, attention = build(args.hours)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(report, encoding="utf-8")
    first = next((line for line in report.splitlines() if line.startswith("- ")), "")
    print(f"{args.out}: {first}")
    shown = notify(attention, args.out, args.notify)
    if not github_ok:
        return 2
    return 0 if shown else 3


if __name__ == "__main__":
    sys.exit(main())
