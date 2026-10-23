"""The burst harness tested against a stub — a negative test.

`check_judge_burst.py` is a measurement that can also fail. Its "failed"
signal has to be trusted, so a stub API is raised with a single-lane judge
and the harness is run three ways:

| Stub behaviour                          | Expected exit |
| --- | --- |
| honest judge                            | 0 |
| every 10th ordinary solution gets a TLE | 1, "false TLE" reported |
| every 5th submission is refused (429)   | 1, "not accepted" reported |

The stub replaces the queue, the sandbox and the clock, so this proves the
harness's logic, not the judge. The real measurement is the `burst` job.

    python tests/burst/selftest_burst.py
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import time
from datetime import UTC, datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from queue import Queue

HARNESS = Path(__file__).with_name("check_judge_burst.py")
# 80 connections arrive at once; the default backlog of 5 would refuse them.
ThreadingHTTPServer.request_queue_size = 256
JOB_S = 0.003


class Stub:
    def __init__(self, mode: str) -> None:
        self.mode = mode
        self.rows: list[dict] = []
        self.users = 0
        self.posts = 0
        self.ok_judged = 0
        self.lock = threading.Lock()
        self.queue: Queue[dict] = Queue()
        threading.Thread(target=self.judge, daemon=True).start()

    def judge(self) -> None:
        while True:
            row = self.queue.get()
            time.sleep(JOB_S)
            kind = row["kind"]
            with self.lock:
                verdict, cpu = ("TLE", 1000) if kind == "loop" else ("AC", 400 if kind == "canary" else 5)
                if kind == "ok":
                    self.ok_judged += 1
                    if self.mode == "false_tle" and self.ok_judged % 10 == 0:
                        verdict, cpu = "TLE", 1000
                row.update(verdict=verdict, time_ms=cpu, judged_at=datetime.now(UTC).isoformat())


def kind_of(source: str) -> str:
    if "for(;;)" in source:
        return "loop"
    return "canary" if "400000000ULL" in source else "ok"


def handler(stub: Stub) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args: object) -> None:
            pass

        def send(self, status: int, body: object, cookie: str | None = None) -> None:
            raw = json.dumps(body).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(raw)))
            if cookie:
                self.send_header("Set-Cookie", f"{cookie}; Path=/")
            self.end_headers()
            self.wfile.write(raw)

        def do_GET(self) -> None:
            if self.path.startswith("/health/"):
                return self.send(200, {"status": "ok"})
            user = (self.headers.get("Cookie") or "").split("sessionid=")[-1].split(";")[0]
            with stub.lock:
                mine = [r for r in stub.rows if r["user"] == user]
                body = [{k: v for k, v in r.items() if k not in ("user", "kind")} for r in reversed(mine)]
            self.send(200, {"results": body})

        def do_POST(self) -> None:
            length = int(self.headers.get("Content-Length") or 0)
            data = json.loads(self.rfile.read(length) or b"{}")
            if self.path.startswith("/auth/register/"):
                return self.send(201, {})
            if self.path.startswith("/auth/login/"):
                with stub.lock:
                    stub.users += 1
                    name = f"u{stub.users}"
                return self.send(200, {}, cookie=f"sessionid={name}")
            user = (self.headers.get("Cookie") or "").split("sessionid=")[-1].split(";")[0]
            with stub.lock:
                stub.posts += 1
                # After the baseline runs (10 submissions) so the burst, not the
                # preparation, is what gets refused.
                if stub.mode == "refuse" and stub.posts > 30 and stub.posts % 5 == 0:
                    return self.send(429, {})
                row = {
                    "id": len(stub.rows) + 1,
                    "user": user,
                    "kind": kind_of(data["source_code"]),
                    "verdict": "PENDING",
                    "time_ms": 0,
                    "created_at": datetime.now(UTC).isoformat(),
                    "judged_at": None,
                }
                stub.rows.append(row)
            stub.queue.put(row)
            self.send(201, {"id": row["id"]})

    return Handler


def run(mode: str) -> tuple[int, str]:
    stub = Stub(mode)
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler(stub))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    env = {
        **os.environ,
        "API": f"http://127.0.0.1:{server.server_port}",
        "BURST": "80",
        "BURST_USERS": "8",
        "BURST_POLL_S": "0.2",
        "BURST_DEADLINE_S": "60",
        "PYTHONIOENCODING": "utf-8",
    }
    done = subprocess.run(
        [sys.executable, str(HARNESS)],
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=180,
    )
    server.shutdown()
    return done.returncode, done.stdout + done.stderr


def main() -> int:
    problems: list[str] = []
    cases = [
        ("honest judge", "honest", 0, None),
        ("false TLE", "false_tle", 1, "false TLE"),
        ("refused submissions", "refuse", 1, "not accepted"),
    ]
    for label, mode, want, needle in cases:
        code, out = run(mode)
        ok = code == want and (needle is None or needle in out)
        print(f"  {'ok  ' if ok else 'FAIL'} {label}: exit {code} (wanted {want})")
        if not ok:
            problems.append(f"{label}: exit {code}, wanted {want}, {needle!r} {'found' if needle and needle in out else 'missing'}")
            print(out[-1500:])
    if problems:
        print("\nBurst self-test FAILED:", *problems, sep="\n  - ", file=sys.stderr)
        return 1
    print("Burst self-test passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
