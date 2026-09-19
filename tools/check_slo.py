#!/usr/bin/env python3
"""Origin SLO — Sentry yo'q (2026-09-19). Health + judge navbati.

Maqsad sukutda jonli preview API: 127.0.0.1:8301. Host header shart.
Chiqish: 0 — health 200; 1 — 503/xato; 2 — o'lchab bo'lmadi.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

import _console

_console.force_utf8()

def _origin() -> str:
    if explicit := os.environ.get("SLO_BASE"):
        return explicit
    # `check_negative` stub `RANKWANT_API_BASE=http://127.0.0.1:<port>/api/v1`
    api = os.environ.get("RANKWANT_API_BASE", "")
    if api:
        return api.removesuffix("/api/v1").rstrip("/")
    return "http://127.0.0.1:8301"


BASE = _origin()
HOST = os.environ.get("SLO_HOST", "rankwant.uz")


def get(path: str) -> tuple[int, dict[str, object]]:
    req = urllib.request.Request(
        f"{BASE}{path}",
        headers={"Host": HOST, "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as res:
            return res.status, json.loads(res.read().decode())
    except urllib.error.HTTPError as exc:
        body = exc.read().decode()
        try:
            return exc.code, json.loads(body)
        except json.JSONDecodeError:
            return exc.code, {"raw": body}


def main() -> int:
    try:
        health_status, health = get("/api/v1/health/")
        slo_status, slo = get("/api/v1/slo/")
    except OSError as exc:
        print(f"✗ o'lchab bo'lmadi: {exc}")
        return 2

    queue = slo.get("judge_queue") if slo_status == 200 else None
    print(f"health {health_status} {health.get('status')}")
    print(f"slo {slo_status} judge_queue={queue}")
    if health_status != 200:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
