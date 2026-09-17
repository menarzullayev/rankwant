#!/usr/bin/env python3
"""Runner watchdog: restart a self-hosted runner that sits idle while its jobs wait.

actions/runner#4444: when a job ends, the listener can stop polling the broker.
The runner stays `online` with `busy=false`, and every job that needs its
labels sits in `queued` until the listener restarts. A healthy idle listener
also logs nothing for an hour at a time (measured: two lines in 69 minutes), so
the runner's own log cannot tell the two apart. The queue can.

Measured 2026-09-17: the container runner went quiet at 13:34:24 UTC after a job
hit its timeout, and four queued jobs waited until a broker reconnect at 13:41
woke it. The runner is 2.337.0; the WSL runner, on the same version, was removed
the same day.

A runner is restarted only when two checks at least CONFIRM seconds apart both
find it online and idle while a job it could run has been queued for at least
STALL seconds. One check is not enough: between one job ending and the next
starting, a runner is idle for a few seconds with a long-queued job, and a
restart then would break a healthy pickup. After a restart the runner is left
alone for COOLDOWN seconds.

Exit codes: 0 nothing stuck, or every stuck runner restarted; 1 a restart failed
or a stuck runner has no restart command; 2 GitHub could not be read. Unknown is
never healthy.

Runs every 2 minutes on this machine, see tools/runner/README.md. Tests pass
fixtures instead of asking GitHub, and --dry-run restarts nothing:
  --runners FILE --jobs FILE --now ISO --state FILE --dry-run
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import _console

_console.force_utf8()

REPO = "menarzullayev/rankwant"
STALL = 180
CONFIRM = 90
COOLDOWN = 600
# How each runner on this machine is restarted. A restart keeps the
# registration: the listener opens a fresh broker session when it starts.
RESTART = {
    "nsn-pc-rankwant-container": ["docker", "restart", "rankwant-ci-runner"],
    "nsn-pc-rankwant-container-2": ["docker", "restart", "rankwant-ci-runner-2"],
}
DEFAULT_STATE = Path.home() / "AppData" / "Local" / "RankWant" / "runner-watchdog.json"


class Unmeasured(Exception):
    pass


def parse_time(value: object) -> datetime:
    if not isinstance(value, str) or not value:
        raise Unmeasured(f"vaqt o'qilmadi: {value!r}")
    try:
        moment = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise Unmeasured(f"vaqt o'qilmadi: {value!r}") from exc
    if moment.tzinfo is None:
        raise Unmeasured(f"vaqt zonasiz: {value!r}")
    return moment


def gh_api(path: str) -> dict:
    try:
        # stdin=DEVNULL: the scheduled task starts this under `conhost --headless`,
        # where the inherited stdin handle is invalid and CreateProcess fails
        # with "[WinError 6] The handle is invalid" (measured on its first run).
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
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise Unmeasured(f"gh api {path}: JSON emas — {exc}") from exc
    if not isinstance(data, dict):
        raise Unmeasured(f"gh api {path}: kutilmagan javob")
    return data


def fetch_runners() -> list[dict]:
    return list(gh_api(f"repos/{REPO}/actions/runners?per_page=100").get("runners", []))


def fetch_queued_jobs() -> list[dict]:
    # A run that already has a job running still holds queued jobs, so both
    # run states are read.
    jobs: list[dict] = []
    for status in ("queued", "in_progress"):
        runs = gh_api(f"repos/{REPO}/actions/runs?status={status}&per_page=100")
        for run in runs.get("workflow_runs", []):
            page = gh_api(f"repos/{REPO}/actions/runs/{run['id']}/jobs?per_page=100")
            jobs.extend(job for job in page.get("jobs", []) if job.get("status") == "queued")
    return jobs


def read_list(path: Path) -> list[dict]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise Unmeasured(f"{path}: {exc}") from exc
    if not isinstance(data, list):
        raise Unmeasured(f"{path}: massiv emas")
    return data


def load_state(path: Path) -> tuple[dict, str | None]:
    """The state is this script's own memory, so a broken file starts it over
    instead of failing every run: the worst case is one extra confirmation."""
    if not path.exists():
        return {}, None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {}, f"holat fayli o'qilmadi, noldan boshlanadi — {exc}"
    if not isinstance(data, dict):
        return {}, "holat fayli obyekt emas, noldan boshlanadi"
    return data, None


def state_time(entry: dict, key: str) -> datetime | None:
    try:
        return parse_time(entry.get(key)) if key in entry else None
    except Unmeasured:
        entry.pop(key, None)
        return None


def waiting_jobs(runner: dict, jobs: list[dict], now: datetime) -> list[tuple[str, int]]:
    """Jobs this runner could take that have been queued for at least STALL seconds."""
    names = {str(label.get("name", "")).lower() for label in runner.get("labels", [])}
    found = []
    for job in jobs:
        wants = {str(label).lower() for label in job.get("labels", [])}
        if not wants or not wants <= names:
            continue
        queued = int((now - parse_time(job.get("created_at") or job.get("started_at"))).total_seconds())
        if queued >= STALL:
            found.append((str(job.get("name")), queued))
    return found


def decide(
    runners: list[dict], jobs: list[dict], now: datetime, state: dict
) -> tuple[list[tuple[str, str]], list[tuple[str, str]], dict]:
    """Return runners to restart, runners newly suspected, and the next state."""
    restart: list[tuple[str, str]] = []
    suspected: list[tuple[str, str]] = []
    next_state: dict = {}
    for runner in runners:
        name = str(runner.get("name"))
        entry = state.get(name, {})
        entry = dict(entry) if isinstance(entry, dict) else {}
        since = state_time(entry, "suspect_since")
        last = state_time(entry, "restarted_at")
        idle = runner.get("status") == "online" and runner.get("busy") is False
        waiting = waiting_jobs(runner, jobs, now) if idle else []
        if not waiting:
            entry.pop("suspect_since", None)
        else:
            job, queued = max(waiting, key=lambda item: item[1])
            reason = f"online va bo'sh, `{job}` {queued} s navbatda"
            if since is None:
                entry["suspect_since"] = now.isoformat()
                suspected.append((name, reason))
            else:
                confirmed = (now - since).total_seconds() >= CONFIRM
                cooled = last is None or (now - last).total_seconds() >= COOLDOWN
                if confirmed and cooled:
                    restart.append((name, reason))
                    entry["restarted_at"] = now.isoformat()
                    entry.pop("suspect_since", None)
        if entry:
            next_state[name] = entry
    return restart, suspected, next_state


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dry-run", action="store_true", help="report only, restart nothing")
    ap.add_argument("--state", type=Path, help=f"state file (default {DEFAULT_STATE})")
    ap.add_argument("--runners", type=Path, help="test fixture: JSON list of runners")
    ap.add_argument("--jobs", type=Path, help="test fixture: JSON list of queued jobs")
    ap.add_argument("--now", help="test fixture: current time, ISO 8601 with a zone")
    args = ap.parse_args()
    state_path = args.state or DEFAULT_STATE
    state, warning = load_state(state_path)
    try:
        now = parse_time(args.now) if args.now else datetime.now(timezone.utc)
        runners = read_list(args.runners) if args.runners else fetch_runners()
        jobs = read_list(args.jobs) if args.jobs else fetch_queued_jobs()
        restart, suspected, next_state = decide(runners, jobs, now, state)
    except Unmeasured as exc:
        print(f"{datetime.now():%Y-%m-%d %H:%M:%S} ✗ Runner watchdog: o'lchab bo'lmadi — {exc}")
        return 2

    stamp = f"{now.astimezone():%Y-%m-%d %H:%M:%S}"
    code = 0
    if warning:
        print(f"{stamp} ⚠ {warning}")
    for name, reason in suspected:
        print(f"{stamp} ? {name}: {reason} — keyingi tekshiruvda ham shunday bo'lsa restart")
    for name, reason in restart:
        command = RESTART.get(name)
        if command is None:
            print(f"{stamp} ✗ {name}: tiqilgan ({reason}), lekin restart buyrug'i yo'q")
            code = 1
        elif args.dry_run:
            print(f"{stamp} → {name}: restart qilinardi ({reason})")
        else:
            proc = subprocess.run(
                command,
                stdin=subprocess.DEVNULL,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            if proc.returncode == 0:
                print(f"{stamp} ✓ {name}: restart qilindi ({reason})")
            else:
                err = proc.stderr.strip()[:160]
                print(f"{stamp} ✗ {name}: restart yiqildi (exit {proc.returncode}) — {err}")
                code = 1

    # A manual dry run must not start a cooldown the real watchdog would honour.
    if not (args.dry_run and args.state is None):
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(json.dumps(next_state, indent=2), encoding="utf-8")
    return code


if __name__ == "__main__":
    sys.exit(main())
