"""Loads the voice only while it is used (ADR-0064, phase 2).

The voice server holds about 8 GB of commit while it runs (measured 2026-11-12;
`README.md` § Memory), on the host the production stack shares. This process is
what listens on 127.0.0.1:8370 instead: it starts `server.py` on the first
request, forwards to it, and stops it again after `TTS_IDLE_MINUTES` without
requests. It refuses to start it when the host has less free commit than
`TTS_START_FREE_GB`, and stops it when free commit falls under
`TTS_RELEASE_FREE_GB` — the voice gives way, not the site.

Standard library only: it never imports torch, so it costs megabytes.

Environment:
    TTS_PORT               where this process listens (default 8370)
    TTS_CHILD_PORT         where `server.py` listens (default 8371)
    TTS_SERVER             the server script (default `server.py` beside this one)
    TTS_PYTHON             its interpreter (default this one)
    TTS_IDLE_MINUTES       stop the server after this long unused (default 10)
    TTS_START_FREE_GB      free commit needed to start it (default 11)
    TTS_RELEASE_FREE_GB    stop it when free commit falls under this (default 1.5)
    TTS_LOAD_TIMEOUT_S     how long a start may take (default 150)
"""

from __future__ import annotations

import ctypes
import json
import os
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
PORT = int(os.environ.get("TTS_PORT", "8370"))
CHILD_PORT = int(os.environ.get("TTS_CHILD_PORT", "8371"))
SERVER = Path(os.environ.get("TTS_SERVER", str(HERE / "server.py")))
PYTHON = os.environ.get("TTS_PYTHON", sys.executable)
IDLE_S = float(os.environ.get("TTS_IDLE_MINUTES", "10")) * 60
START_FREE_GB = float(os.environ.get("TTS_START_FREE_GB", "11"))
RELEASE_FREE_GB = float(os.environ.get("TTS_RELEASE_FREE_GB", "1.5"))
LOAD_TIMEOUT_S = float(os.environ.get("TTS_LOAD_TIMEOUT_S", "150"))
#: The model name the API checks (`X-Model`); the same rule as `server.py`.
MODEL_NAME = "navoiy-{}-{}".format(
    os.environ.get("TTS_EMOTION", "xotirjam"), os.environ.get("TTS_VOICE", "fleurs")
)
CHILD = f"http://127.0.0.1:{CHILD_PORT}"


class _MemoryStatus(ctypes.Structure):
    _fields_ = [
        ("dwLength", ctypes.c_ulong),
        ("dwMemoryLoad", ctypes.c_ulong),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]


def free_commit_gb() -> float | None:
    """The host's free commit (RAM + page file) in GB; None off Windows."""
    if os.name != "nt":
        return None
    status = _MemoryStatus()
    status.dwLength = ctypes.sizeof(status)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        return None
    return status.ullAvailPageFile / 2**30


def log(message: str) -> None:
    print(time.strftime("%Y-%m-%d %H:%M:%S"), "supervisor:", message, flush=True)


_job: int | None = None


def die_with_us(process: subprocess.Popen[bytes]) -> None:
    """Put the server in a job that Windows closes when this process exits.

    Without it a supervisor stopped by Task Scheduler (or killed) would leave the
    server running on its own, holding its 8 GB with nothing to stop it.
    """
    global _job
    if os.name != "nt":
        return
    from ctypes import wintypes

    class Basic(ctypes.Structure):
        _fields_ = [
            ("PerProcessUserTimeLimit", ctypes.c_int64),
            ("PerJobUserTimeLimit", ctypes.c_int64),
            ("LimitFlags", ctypes.c_uint32),
            ("MinimumWorkingSetSize", ctypes.c_size_t),
            ("MaximumWorkingSetSize", ctypes.c_size_t),
            ("ActiveProcessLimit", ctypes.c_uint32),
            ("Affinity", ctypes.c_size_t),
            ("PriorityClass", ctypes.c_uint32),
            ("SchedulingClass", ctypes.c_uint32),
        ]

    class Extended(ctypes.Structure):
        _fields_ = [
            ("BasicLimitInformation", Basic),
            ("IoInfo", ctypes.c_uint64 * 6),
            ("ProcessMemoryLimit", ctypes.c_size_t),
            ("JobMemoryLimit", ctypes.c_size_t),
            ("PeakProcessMemoryUsed", ctypes.c_size_t),
            ("PeakJobMemoryUsed", ctypes.c_size_t),
        ]

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.CreateJobObjectW.restype = wintypes.HANDLE
    kernel32.SetInformationJobObject.argtypes = [
        wintypes.HANDLE,
        ctypes.c_int,
        ctypes.c_void_p,
        wintypes.DWORD,
    ]
    kernel32.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
    if _job is None:
        job = kernel32.CreateJobObjectW(None, None)
        info = Extended()
        info.BasicLimitInformation.LimitFlags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        if not job or not kernel32.SetInformationJobObject(
            job,
            9,
            ctypes.byref(info),
            ctypes.sizeof(info),  # JobObjectExtendedLimitInformation
        ):
            error = ctypes.get_last_error()
            log(f"no job object (error {error}): the voice may outlive the supervisor")
            return
        _job = job
    if not kernel32.AssignProcessToJobObject(_job, int(process._handle)):  # type: ignore[attr-defined]
        log(f"the voice is not in the job (error {ctypes.get_last_error()})")


class Voice:
    """The `server.py` process, started and stopped on demand."""

    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.process: subprocess.Popen[bytes] | None = None
        self.last_used = 0.0

    def running(self) -> bool:
        return self.process is not None and self.process.poll() is None

    def _ready(self) -> bool:
        try:
            with urllib.request.urlopen(CHILD + "/health", timeout=2) as response:
                return bool(json.loads(response.read()).get("ready"))
        except (urllib.error.URLError, OSError, ValueError):
            return False

    def start(self) -> str | None:
        """Start the server if it is not running; the reason it was not, or None."""
        if self.running():
            return None
        free = free_commit_gb()
        if free is not None and free < START_FREE_GB:
            log(f"not starting: {free:.1f} GB of commit free, {START_FREE_GB} needed")
            return "low_memory"
        env = dict(os.environ, TTS_PORT=str(CHILD_PORT))
        log(f"starting the voice ({free if free is not None else '?'} GB of commit free)")
        self.process = subprocess.Popen([PYTHON, "-u", str(SERVER)], env=env)
        die_with_us(self.process)
        deadline = time.monotonic() + LOAD_TIMEOUT_S
        while time.monotonic() < deadline:
            if self.process.poll() is not None:
                log(f"the voice exited while loading (code {self.process.returncode})")
                self.process = None
                return "start_failed"
            if self._ready():
                log("the voice is ready")
                return None
            time.sleep(1)
        self.stop("did not load in time")
        return "start_failed"

    def stop(self, why: str) -> None:
        if self.process is None:
            return
        if self.process.poll() is None:
            log(f"stopping the voice: {why}")
            self.process.terminate()
            try:
                self.process.wait(timeout=20)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=20)
        self.process = None

    def synthesize(self, body: bytes) -> tuple[int, dict[str, str], bytes]:
        with self.lock:
            refused = self.start()
            if refused:
                return (
                    503,
                    {"Content-Type": "application/json"},
                    json.dumps({"error": refused}).encode(),
                )
            request = urllib.request.Request(
                CHILD + "/synthesize",
                data=body,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            try:
                with urllib.request.urlopen(request, timeout=LOAD_TIMEOUT_S) as response:
                    status, headers, audio = (
                        response.status,
                        dict(response.headers),
                        response.read(),
                    )
            except urllib.error.HTTPError as exc:
                status, headers, audio = exc.code, dict(exc.headers), exc.read()
            except (urllib.error.URLError, OSError) as exc:
                log(f"the voice did not answer: {exc}")
                self.stop("did not answer")
                return 503, {"Content-Type": "application/json"}, b'{"error": "voice_failed"}'
            self.last_used = time.monotonic()
            return status, headers, audio

    def watch(self) -> None:
        """Stop the server when it idles, or when the host runs short of commit."""
        while True:
            time.sleep(15)
            with self.lock:
                if not self.running():
                    if self.process is not None:
                        log(f"the voice exited (code {self.process.returncode})")
                        self.process = None
                    continue
                free = free_commit_gb()
                if free is not None and free < RELEASE_FREE_GB:
                    self.stop(f"only {free:.1f} GB of commit free")
                elif time.monotonic() - self.last_used > IDLE_S:
                    self.stop(f"unused for {IDLE_S / 60:.0f} min")


VOICE = Voice()
PASSED_HEADERS = ("Content-Type", "X-Model", "X-Audio-Seconds", "X-Synthesis-Seconds")


class Handler(BaseHTTPRequestHandler):
    def _send(self, status: int, headers: dict[str, str], body: bytes) -> None:
        self.send_response(status)
        for name in PASSED_HEADERS:
            if name in headers:
                self.send_header(name, headers[name])
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path != "/health":
            self._send(404, {}, b"")
            return
        free = free_commit_gb()
        body = {
            "model": MODEL_NAME,
            "ready": True,
            "loaded": VOICE.running(),
            "free_commit_gb": None if free is None else round(free, 1),
        }
        self._send(200, {"Content-Type": "application/json"}, json.dumps(body).encode())

    def do_POST(self) -> None:
        if self.path != "/synthesize":
            self._send(404, {}, b"")
            return
        body = self.rfile.read(int(self.headers.get("Content-Length", "0")))
        self._send(*VOICE.synthesize(body))

    def log_message(self, fmt: str, *args: Any) -> None:
        sys.stderr.write(f"{self.log_date_time_string()} {fmt % args}\n")


def main() -> None:
    if not SERVER.is_file():
        sys.exit(f"TTS_SERVER is not a file: {SERVER}")
    threading.Thread(target=VOICE.watch, daemon=True).start()
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    log(f"{MODEL_NAME} on demand at 127.0.0.1:{PORT}; the voice itself on {CHILD_PORT}")
    try:
        server.serve_forever()
    finally:
        VOICE.stop("supervisor stopping")


if __name__ == "__main__":
    main()
