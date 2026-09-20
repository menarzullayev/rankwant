"""Judge latency harness'ining O'ZINI sinash — salbiy test.

Nega kerak: `check_judge_latency.py` — bu darvoza, ya'ni uning «yiqildi»
signaliga ishonish kerak. Yashil natija yolg'on bo'lishi mumkin: byudjet
tekshiruvi umuman ishlamasa ham skript 0 qaytaraveradi. Shuning uchun bu
yerda stub API ko'tariladi va **ikkala yo'nalish** tekshiriladi:

| Byudjet | Kutilgan chiqish |
| --- | --- |
| Imkonsiz tor (`LATENCY_P50_MS=1`) | `1` — darvoza yiqilishi shart |
| Keng (`60000`) | `0` — o'tishi shart |

Stub haqiqiy judge'ni almashtiradi: navbat yo'q, sandbox yo'q. Ya'ni bu
sinov o'lchovning **to'g'riligini** emas, **darvoza mantiqini** tasdiqlaydi.
Haqiqiy nsjail ostidagi o'lchovni Nightly yuritadi.

Ishlatish:  python tests/latency/selftest.py
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HARNESS = Path(__file__).with_name("check_judge_latency.py")
SAMPLES = 3

_pending: dict[str, int] = {}
_lock = threading.Lock()


class Stub(BaseHTTPRequestHandler):
    """Minimal API: register, login, submit, poll — verdict ikkinchi so'rovda."""

    def log_message(self, *args: object) -> None:  # jim
        pass

    def _json(self, payload: dict, cookies: list[str] | None = None) -> None:
        body = json.dumps(payload).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        for cookie in cookies or []:
            self.send_header("Set-Cookie", cookie)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802 — http.server nomi
        path = self.path.split("?", 1)[0]
        if path.endswith("/health/"):
            return self._json({"status": "ok", "checks": {"database": "ok", "redis": "ok"}})
        if "/attempts/" in path:
            attempt = path.rstrip("/").rsplit("/", 1)[-1]
            with _lock:
                _pending[attempt] = _pending.get(attempt, 0) + 1
                seen = _pending[attempt]
            # Birinchi so'rov — hali navbatda; ikkinchisi — verdikt.
            verdict = "PENDING" if seen == 1 else "AC"
            return self._json({"id": attempt, "verdict": verdict})
        self.send_error(404)

    def do_POST(self) -> None:  # noqa: N802 — http.server nomi
        path = self.path.split("?", 1)[0]
        length = int(self.headers.get("Content-Length") or 0)
        self.rfile.read(length)
        if path.endswith("/auth/login/"):
            return self._json({}, ["sessionid=stub", "csrftoken=stub"])
        if path.endswith("/auth/register/"):
            return self._json({})
        if path.endswith("/attempts/"):
            with _lock:
                attempt = str(len(_pending) + 1)
                _pending[attempt] = 0
            return self._json({"id": attempt})
        self.send_error(404)


def run_harness(port: int, budget_ms: int) -> subprocess.CompletedProcess:
    env = {
        **os.environ,
        "API": f"http://127.0.0.1:{port}/api/v1",
        "LATENCY_SAMPLES": str(SAMPLES),
        "LATENCY_WARMUP": "0",
        "LATENCY_P50_MS": str(budget_ms),
        "LATENCY_P95_MS": str(budget_ms),
    }
    return subprocess.run(
        [sys.executable, str(HARNESS)], env=env, capture_output=True, text=True, timeout=120
    )


def main() -> int:
    server = ThreadingHTTPServer(("127.0.0.1", 0), Stub)
    server.daemon_threads = True
    threading.Thread(target=server.serve_forever, daemon=True).start()
    port = server.server_address[1]
    failures: list[str] = []

    try:
        print("1) Imkonsiz tor byudjet — darvoza YIQILISHI shart")
        tight = run_harness(port, budget_ms=1)
        print(f"   chiqish kodi: {tight.returncode} (kutilgan 1)")
        if tight.returncode != 1:
            failures.append(f"tor byudjet 0 qaytardi — darvoza ishlamayapti\n{tight.stdout}")
        elif "Latency YIQILDI" not in tight.stderr:
            failures.append("tor byudjet yiqildi, lekin sabab chop etilmadi")

        print("2) Keng byudjet — darvoza O'TISHI shart")
        loose = run_harness(port, budget_ms=60000)
        print(f"   chiqish kodi: {loose.returncode} (kutilgan 0)")
        if loose.returncode != 0:
            failures.append(f"keng byudjet {loose.returncode} qaytardi\n{loose.stderr}")
        elif "byudjetga sig'adi" not in loose.stdout:
            failures.append("o'tdi, lekin xulosa chop etilmadi")
        elif "p50 =" not in loose.stdout or "p95 =" not in loose.stdout:
            failures.append("o'tdi, lekin p50/p95 chop etilmadi")
    finally:
        server.shutdown()

    if failures:
        print("\nSELFTEST YIQILDI:", file=sys.stderr)
        for item in failures:
            print(f"  - {item}", file=sys.stderr)
        return 1
    print("\nSelftest o'tdi — darvoza ikkala yo'nalishda ham to'g'ri ishlaydi")
    return 0


if __name__ == "__main__":
    sys.exit(main())
