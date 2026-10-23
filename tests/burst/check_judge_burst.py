"""Judge under a burst: what happens when many submissions arrive at once.

Question this answers (owner, 2026-10-23): with 1000 submissions in the
system at the same time, how does the judge behave, and does the queue make
other people's attempts hit the time limit?

What is known from the code and is CHECKED here:

* the judge takes one job at a time per process (`BRPOP` loop), so a burst
  becomes a queue and the last submission waits for all the others;
* a time limit is the CPU time of the sandbox, not the clock, so waiting in
  the queue cannot by itself turn a correct solution into TLE;
* the reaper (`judging.reap_stuck`) leaves attempts alone while the queue is
  not empty.

What is MEASURED:

1. accept phase — all submissions sent at once: how many are accepted, API
   latency, any 429 / 5xx;
2. drain phase — wait of each attempt (`judged_at - created_at`), how long
   the whole burst takes, attempts per minute;
3. correctness under load — the mix is 85 % ordinary correct solutions,
   10 % "canaries" (a fixed amount of work, ~0.3–0.5 s of CPU) and 5 % busy
   loops that SHOULD be TLE. Any verdict other than the expected one is a
   failure. The canaries' reported CPU time is compared with the same
   program run alone before the burst — contention shows as inflation.

Environment (`docker-compose.ci.yml` → `burst`):

| Variable | Default | Meaning |
| --- | --- | --- |
| `API` | `http://api:8000/api/v1` | API under test |
| `BURST` | `1000` | submissions sent at once |
| `BURST_USERS` | `100` | accounts the burst is spread over |
| `BURST_LANGUAGE` | `cpp23` | the language of every submission |
| `BURST_PROBLEM` | `a-plus-b` | seeded problem |
| `BURST_DEADLINE_S` | `4800` | give up waiting for verdicts after this |
| `BURST_SEED` | `7` | order of the mix |
| `BURST_CANARY` | `0.10` | share of fixed-work canaries (each costs ~45 s of judge time) |
| `BURST_POLL_S` | `5` | seconds between looks at the verdicts |

Output: a human report and one `BURST_JSON: {...}` line.
"""

from __future__ import annotations

import json
import math
import os
import random
import secrets
import statistics
import sys
import threading
import time
import urllib.error
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

API = os.environ.get("API", "http://api:8000/api/v1")
BURST = int(os.environ.get("BURST", "1000"))
USERS = int(os.environ.get("BURST_USERS", "100"))
LANGUAGE = os.environ.get("BURST_LANGUAGE", "cpp23")
PROBLEM = os.environ.get("BURST_PROBLEM", "a-plus-b")
DEADLINE_S = int(os.environ.get("BURST_DEADLINE_S", "4800"))
SEED = int(os.environ.get("BURST_SEED", "7"))
SEND_THREADS = 100
POLL_EVERY_S = float(os.environ.get("BURST_POLL_S", "5"))
BASELINE_RUNS = 5

REPORT_MARKER = "BURST_JSON: "

FINAL_BAD = {"IE", "DENIAL_OF_JUDGEMENT", "CHECKER_ERROR", "TESTING_ABORTED"}
PENDING = {"", "PENDING", "RUNNING", "TESTING"}

#: Share of the burst that are canaries. A canary does ~0.45 s of CPU work on
#: EVERY test, and a problem has many tests (a-plus-b: about a hundred), so one
#: canary keeps the judge busy for ~45 s where an ordinary solution takes ~1 s.
#: The first run (2026-10-23) used 10 % and was dominated by them; the share
#: is a parameter so the same burst can be run with and without that load.
CANARY_SHARE = float(os.environ.get("BURST_CANARY", "0.10"))
LOOP_SHARE = 0.05

#: kind → (share of the mix, expected verdicts)
MIX = {
    "ok": (1 - CANARY_SHARE - LOOP_SHARE, {"AC"}),
    "canary": (CANARY_SHARE, {"AC"}),
    "loop": (LOOP_SHARE, {"TLE"}),
}

SOURCES = {
    "ok": (
        "#include <cstdio>\n"
        'int main(){int a,b;scanf("%d %d",&a,&b);printf("%d\\n",a+b);return 0;}\n'
    ),
    # A fixed amount of work, not a fixed time: a time-based loop measures
    # itself and would never show contention. Run on every test of the problem.
    "canary": (
        "#include <cstdio>\n"
        "static volatile unsigned long long sink;\n"
        "int main(){int a,b;scanf(\"%d %d\",&a,&b);\n"
        "unsigned long long x=1;\n"
        "for(unsigned long long i=0;i<400000000ULL;i++){x=x*6364136223846793005ULL+i;}\n"
        'sink=x;printf("%d\\n",a+b);return 0;}\n'
    ),
    "loop": (
        "#include <cstdio>\n"
        "static volatile unsigned long long sink;\n"
        "int main(){int a,b;scanf(\"%d %d\",&a,&b);\n"
        "unsigned long long x=1;for(;;){x=x*6364136223846793005ULL+1;sink=x;}\n"
        'printf("%d\\n",a+b);return 0;}\n'
    ),
}


def request(path: str, data: dict | None = None, cookie: str = "", timeout: int = 60) -> tuple:
    url = API + path
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(url, data=body, method="POST" if data is not None else "GET")
    if body:
        req.add_header("Content-Type", "application/json")
    if cookie:
        req.add_header("Cookie", cookie)
        token = dict(c.split("=", 1) for c in cookie.split("; ") if "=" in c).get("csrftoken")
        if token and body:
            req.add_header("X-CSRFToken", token)
            req.add_header("Referer", url)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode()
        parsed = json.loads(raw) if raw.startswith(("{", "[")) else raw
        return parsed, resp.headers.get_all("Set-Cookie") or []


def percentile(values: list[float], pct: float) -> float:
    ordered = sorted(values)
    return ordered[max(1, math.ceil(pct / 100 * len(ordered))) - 1]


def make_user(index: int) -> str:
    suffix = f"{int(time.time())}{index}{secrets.token_hex(2)}"
    creds = {
        "username": f"burst{suffix}",
        "email": f"burst{suffix}@rankwant.uz",
        "password": secrets.token_urlsafe(24),
        "terms_accepted": True,
    }
    request("/auth/register/", creds)
    _, cookies = request("/auth/login/", {"identifier": creds["username"], "password": creds["password"]})
    if not cookies:
        raise RuntimeError("login gave no session")
    return "; ".join(c.split(";")[0] for c in cookies)


def submit(session: str, kind: str) -> tuple[int | None, int, float]:
    """(attempt id or None, http status, seconds the API took)."""
    started = time.monotonic()
    try:
        body, _ = request(
            "/attempts/",
            {"problem": PROBLEM, "language": LANGUAGE, "source_code": SOURCES[kind]},
            cookie=session,
        )
        return body["id"], 201, time.monotonic() - started
    except urllib.error.HTTPError as error:
        return None, error.code, time.monotonic() - started
    except Exception:
        return None, 0, time.monotonic() - started


def listing(session: str) -> list[dict]:
    body, _ = request("/attempts/?mine=true&page_size=100", cookie=session, timeout=30)
    return body["results"] if isinstance(body, dict) else body


def parse(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value) if value else None


def baseline(session: str) -> dict[str, float]:
    """The canary and an ordinary solution, alone, before anything else."""
    cpu: list[float] = []
    walls: list[float] = []
    for _ in range(BASELINE_RUNS):
        for kind, bucket in (("canary", cpu), ("ok", walls)):
            attempt_id, status, _ = submit(session, kind)
            if attempt_id is None:
                raise RuntimeError(f"baseline submit failed: HTTP {status}")
            end = time.monotonic() + 120
            while time.monotonic() < end:
                row = next((r for r in listing(session) if r["id"] == attempt_id), None)
                if row and row["verdict"] not in PENDING:
                    if kind == "canary":
                        bucket.append(float(row["time_ms"]))
                    else:
                        created, judged = parse(row["created_at"]), parse(row["judged_at"])
                        if created and judged:
                            bucket.append((judged - created).total_seconds() * 1000)
                    break
                time.sleep(min(1.0, POLL_EVERY_S))
    return {"canary_cpu_ms": statistics.median(cpu), "ok_wall_ms": statistics.median(walls)}


def main() -> int:
    print(f"Judge burst: {BURST} submissions, {USERS} accounts, {LANGUAGE}, problem {PROBLEM}")
    body, _ = request("/health/")
    if body.get("status") != "ok":
        print(f"  ✗ API not healthy: {body.get('checks')}", file=sys.stderr)
        return 1

    with ThreadPoolExecutor(max_workers=10) as pool:
        sessions = list(pool.map(make_user, range(USERS)))
    print(f"  {len(sessions)} accounts ready")

    alone = baseline(sessions[0])
    print(
        f"  alone: canary {alone['canary_cpu_ms']:.0f} ms CPU, "
        f"ordinary solution {alone['ok_wall_ms']:.0f} ms from submit to verdict"
    )

    rng = random.Random(SEED)
    kinds: list[str] = []
    for kind, (share, _) in MIX.items():
        kinds += [kind] * round(BURST * share)
    kinds = (kinds + ["ok"] * BURST)[:BURST]
    rng.shuffle(kinds)
    jobs = [(sessions[i % USERS], kind) for i, kind in enumerate(kinds)]

    # ── accept phase ────────────────────────────────────────────────
    results: list[tuple[int | None, int, float, str]] = []
    lock = threading.Lock()
    gate = threading.Barrier(min(SEND_THREADS, BURST))

    def fire(index: int) -> None:
        session, kind = jobs[index]
        if index < SEND_THREADS:
            gate.wait()  # the first wave leaves together
        attempt_id, status, took = submit(session, kind)
        with lock:
            results.append((attempt_id, status, took, kind))

    burst_started = time.monotonic()
    with ThreadPoolExecutor(max_workers=SEND_THREADS) as pool:
        list(pool.map(fire, range(BURST)))
    accept_s = time.monotonic() - burst_started

    statuses = Counter(status for _, status, _, _ in results)
    took = [t * 1000 for _, status, t, _ in results if status == 201]
    accepted = {attempt_id: kind for attempt_id, status, _, kind in results if attempt_id}
    print(f"\nAccept phase: {accept_s:.1f} s for {BURST} requests")
    print(f"  HTTP statuses: {dict(sorted(statuses.items()))}")
    if took:
        print(
            f"  API time per submit: p50 {percentile(took, 50):.0f} ms · "
            f"p95 {percentile(took, 95):.0f} ms · max {max(took):.0f} ms"
        )

    # ── drain phase ─────────────────────────────────────────────────
    rows: dict[int, dict] = {}
    deadline = time.monotonic() + DEADLINE_S
    last_report = 0.0
    while time.monotonic() < deadline:
        with ThreadPoolExecutor(max_workers=10) as pool:
            for batch in pool.map(listing, sessions):
                for row in batch:
                    if row["id"] in accepted:
                        rows[row["id"]] = row
        done = sum(1 for r in rows.values() if r["verdict"] not in PENDING)
        if time.monotonic() - last_report > 60:
            minutes = (time.monotonic() - burst_started) / 60
            print(f"  {minutes:5.1f} min · {done}/{len(accepted)} judged")
            last_report = time.monotonic()
        if done >= len(accepted):
            break
        time.sleep(POLL_EVERY_S)
    drain_s = time.monotonic() - burst_started

    # ── analysis ────────────────────────────────────────────────────
    failures: list[str] = []
    final = {i: r for i, r in rows.items() if r["verdict"] not in PENDING}
    unfinished = len(accepted) - len(final)
    by_kind: dict[str, Counter] = {k: Counter() for k in MIX}
    for attempt_id, row in final.items():
        by_kind[accepted[attempt_id]][row["verdict"]] += 1

    waits = []
    for row in final.values():
        created, judged = parse(row["created_at"]), parse(row["judged_at"])
        if created and judged:
            waits.append((judged - created).total_seconds())
    firsts = [parse(r["created_at"]) for r in final.values() if r["created_at"]]
    lasts = [parse(r["judged_at"]) for r in final.values() if r["judged_at"]]
    span = (max(lasts) - min(firsts)).total_seconds() if firsts and lasts else drain_s

    print(f"\nDrain phase: {drain_s / 60:.1f} min until the last verdict ({len(final)}/{len(accepted)} judged)")
    if waits:
        print(
            f"  wait (submit → verdict): p50 {percentile(waits, 50) / 60:.1f} min · "
            f"p95 {percentile(waits, 95) / 60:.1f} min · max {max(waits) / 60:.1f} min"
        )
        print(f"  throughput: {len(final) / span * 60:.1f} verdicts per minute")

    print("\nVerdicts by kind (expected: ok→AC, canary→AC, loop→TLE):")
    wrong = 0
    for kind, counts in by_kind.items():
        expected = MIX[kind][1]
        bad = sum(n for verdict, n in counts.items() if verdict not in expected)
        wrong += bad
        print(f"  {kind:<7} {dict(counts)}  → unexpected: {bad}")

    false_tle = sum(c["TLE"] for k, c in by_kind.items() if k != "loop")
    canary_cpu = [float(r["time_ms"]) for i, r in final.items() if accepted[i] == "canary" and r["time_ms"]]
    inflation = None
    if canary_cpu:
        inflation = statistics.median(canary_cpu) / alone["canary_cpu_ms"]
        print(
            f"\nCanary CPU time under load: median {statistics.median(canary_cpu):.0f} ms · "
            f"p95 {percentile(canary_cpu, 95):.0f} ms · max {max(canary_cpu):.0f} ms "
            f"(alone: {alone['canary_cpu_ms']:.0f} ms) → ×{inflation:.2f}"
        )
    print(f"False TLE (a TLE on a program that should pass): {false_tle}")

    refused = sum(n for s, n in statuses.items() if s != 201)
    if refused:
        failures.append(f"{refused} of {BURST} submissions were not accepted: {dict(statuses)}")
    if unfinished:
        failures.append(f"{unfinished} attempts had no verdict after {DEADLINE_S} s")
    if wrong:
        failures.append(f"{wrong} verdicts other than expected")
    if false_tle:
        failures.append(f"{false_tle} false TLE")
    bad_final = sum(c[v] for c in by_kind.values() for v in FINAL_BAD)
    if bad_final:
        failures.append(f"{bad_final} attempts ended as IE / DENIAL_OF_JUDGEMENT / checker error")

    payload = {
        "api": API,
        "cores": os.cpu_count(),
        "burst": BURST,
        "accepted": len(accepted),
        "statuses": dict(statuses),
        "accept_s": round(accept_s, 1),
        "drain_min": round(drain_s / 60, 1),
        "judged": len(final),
        "wait_p50_min": round(percentile(waits, 50) / 60, 1) if waits else None,
        "wait_p95_min": round(percentile(waits, 95) / 60, 1) if waits else None,
        "wait_max_min": round(max(waits) / 60, 1) if waits else None,
        "per_minute": round(len(final) / span * 60, 1) if final else None,
        "by_kind": {k: dict(v) for k, v in by_kind.items()},
        "false_tle": false_tle,
        "canary_alone_cpu_ms": round(alone["canary_cpu_ms"]),
        "canary_load_cpu_ms": round(statistics.median(canary_cpu)) if canary_cpu else None,
        "canary_inflation": round(inflation, 2) if inflation else None,
        "ok": not failures,
        "failures": failures,
    }
    print(REPORT_MARKER + json.dumps(payload))

    if failures:
        print("\nBurst FAILED:", file=sys.stderr)
        for item in failures:
            print(f"  - {item}", file=sys.stderr)
        return 1
    print("\nBurst passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
