#!/usr/bin/env python3
"""Judge bake-off harness.

Ikkala nomzodni (judge-go / judge-py) BIR XIL shartnoma va BIR XIL sinov to'plami
bilan o'lchaydi. Natija: ADR-0004 mezonlariga mos hisobot.

Ishlatish:
    python3 harness/runner.py --worker judge-go
    python3 harness/runner.py --worker judge-py --load 50
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import statistics
import sys
import time
import uuid

try:
    import redis
except ImportError:
    sys.exit("redis kerak:  pip install redis")

ROOT = pathlib.Path(__file__).resolve().parent.parent
CASES_DIR = ROOT / "cases"
JOBS_KEY = "rankwant:judge:jobs"
RESULTS_KEY = "rankwant:judge:results"

# Izolyatsiya sinovlarida host yon-ta'siri bo'lmasligi SHART.
HOST_ARTIFACTS = {
    "10-file-write": pathlib.Path("/etc/rankwant_pwned"),
}
# Bu case'larda SECURITY_VIOLATION ideal, lekin RE ham qabul qilinadi —
# muhimi host himoyalanishi.
ISOLATION_TOLERANT = {"09-fork-bomb", "10-file-write", "12-proc-read", "13-symlink"}
ISOLATION_CASES = {"09-fork-bomb", "10-file-write", "11-network", "12-proc-read", "13-symlink"}


def load_cases() -> list[dict]:
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(CASES_DIR.glob("*.json"))]


def submit(r: "redis.Redis", case: dict) -> str:
    job_id = str(uuid.uuid4())
    job = {
        "job_id": job_id,
        "attempt_id": 0,
        "language": case["language"],
        "source": case["source"],
        "limits": case["limits"],
        "tests": case["tests"],
        "checker": {"type": "interactive" if case["id"] == "14-interactive" else "standard"},
        "mode": case["mode"],
    }
    r.lpush(JOBS_KEY, json.dumps(job))
    return job_id


def collect(r: "redis.Redis", expected: int, timeout_s: int) -> dict[str, dict]:
    got: dict[str, dict] = {}
    deadline = time.monotonic() + timeout_s
    while len(got) < expected and time.monotonic() < deadline:
        item = r.brpop(RESULTS_KEY, timeout=2)
        if not item:
            continue
        res = json.loads(item[1])
        got[res["job_id"]] = res
    return got


def judge_case(case: dict, res: dict | None) -> tuple[str, list[str]]:
    """Qaytaradi: ('PASS'|'FAIL'|'TIMEOUT', izohlar)."""
    notes: list[str] = []
    if res is None:
        return "TIMEOUT", ["natija kelmadi"]

    verdict = res.get("verdict")
    want = case["expect_verdict"]

    ok = verdict == want
    if not ok and case["id"] in ISOLATION_TOLERANT and verdict in {"RE", "SECURITY_VIOLATION"}:
        ok = True
        notes.append(f"{verdict} (SECURITY_VIOLATION o'rniga qabul qilindi)")

    if not ok:
        notes.append(f"kutilgan {want}, kelgan {verdict}")

    # Host yon-ta'siri — bu MUZOKARA QILINMAYDI
    artifact = HOST_ARTIFACTS.get(case["id"])
    if artifact and artifact.exists():
        return "FAIL", notes + [f"XAVFSIZLIK: {artifact} yaratilgan — sandbox yorilgan"]

    if case["id"] == "11-network":
        out = json.dumps(res.get("per_test", []))
        if "CONNECTED" in out:
            return "FAIL", notes + ["XAVFSIZLIK: tarmoqqa chiqish muvaffaqiyatli bo'lgan"]

    meta = res.get("judge_meta") or {}
    if not meta.get("total_ms"):
        notes.append("judge_meta.total_ms yo'q — latency o'lchab bo'lmaydi")

    if case["id"] == "03-tle-cpu":
        t = res.get("time_ms") or 0
        if t >= 2000:
            notes.append(f"time_ms={t} — wall clock o'lchanayotganga o'xshaydi, CPU emas")
    if case["id"] == "04-idleness":
        t = res.get("time_ms") or 0
        if t >= 200:
            notes.append(f"time_ms={t} — uxlash CPU sifatida hisoblangan")

    return ("PASS" if ok else "FAIL"), notes


def pct(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    values = sorted(values)
    k = max(0, min(len(values) - 1, int(round((p / 100) * (len(values) - 1)))))
    return values[k]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--worker", required=True, help="judge-go | judge-py")
    ap.add_argument("--redis", default=os.environ.get("REDIS_URL", "redis://localhost:6379/0"))
    ap.add_argument("--timeout", type=int, default=180)
    ap.add_argument("--load", type=int, default=0, help="parallel submit soni (0 = o'tkazib yuborish)")
    ap.add_argument("--out", default=None, help="hisobotni faylga yozish (markdown)")
    args = ap.parse_args()

    r = redis.Redis.from_url(args.redis)
    r.delete(JOBS_KEY, RESULTS_KEY)

    cases = load_cases()
    print(f"Nomzod: {args.worker} · {len(cases)} ta case\n")

    ids = {submit(r, c): c for c in cases}
    t0 = time.monotonic()
    results = collect(r, len(cases), args.timeout)
    wall = time.monotonic() - t0

    rows, failures, latencies = [], 0, []
    for job_id, case in ids.items():
        res = results.get(job_id)
        status, notes = judge_case(case, res)
        if status != "PASS":
            failures += 1
        meta = (res or {}).get("judge_meta") or {}
        if meta.get("total_ms"):
            latencies.append(float(meta["total_ms"]))
        rows.append((case["id"], case["expect_verdict"], (res or {}).get("verdict", "—"),
                     status, meta.get("total_ms", "—"), "; ".join(notes)))

    iso_fail = [rid for rid, _, _, st, _, _ in rows if st != "PASS" and rid in ISOLATION_CASES]

    load_stat = None
    if args.load:
        r.delete(JOBS_KEY, RESULTS_KEY)
        base = next(c for c in cases if c["id"] == "01-aplusb")
        lids = [submit(r, base) for _ in range(args.load)]
        lt0 = time.monotonic()
        lres = collect(r, len(lids), args.timeout)
        lwall = time.monotonic() - lt0
        lat = [float((v.get("judge_meta") or {}).get("total_ms", 0)) for v in lres.values()]
        lat = [x for x in lat if x]
        load_stat = {
            "submitted": len(lids), "completed": len(lres), "wall_s": round(lwall, 1),
            "p50": round(pct(lat, 50)), "p95": round(pct(lat, 95)),
            "throughput": round(len(lres) / lwall, 1) if lwall else 0,
        }

    md = [f"# Bake-off natijasi — `{args.worker}`", "",
          f"Sana: {time.strftime('%Y-%m-%d %H:%M')} · Wall: {wall:.1f}s", "",
          "| Case | Kutilgan | Kelgan | Holat | total_ms | Izoh |",
          "| ---- | -------- | ------ | ----- | -------- | ---- |"]
    for rid, want, got, st, ms, note in rows:
        mark = {"PASS": "✅", "FAIL": "❌", "TIMEOUT": "⏱"}[st]
        md.append(f"| `{rid}` | {want} | {got} | {mark} | {ms} | {note} |")

    md += ["", "## Latency (funksional to'plam)", "",
           f"- p50: **{pct(latencies,50):.0f} ms** · p95: **{pct(latencies,95):.0f} ms**",
           f"- NFR byudjeti: p50 < 5000 ms, p95 < 15000 ms"]

    if load_stat:
        md += ["", f"## Yuklama ({load_stat['submitted']} parallel submit)", "",
               f"- Yakunlandi: {load_stat['completed']}/{load_stat['submitted']}",
               f"- p50: **{load_stat['p50']} ms** · p95: **{load_stat['p95']} ms**",
               f"- O'tkazuvchanlik: {load_stat['throughput']} submit/s"]

    verdict_line = ("**O'TDI**" if not failures else f"**O'TMADI** — {failures} ta case")
    if iso_fail:
        verdict_line = f"**O'TMADI (XAVFSIZLIK)** — izolyatsiya sinovlari: {', '.join(iso_fail)}"
    md += ["", "## Xulosa", "", verdict_line, "",
           "> Izolyatsiya sinovlarining **hammasi** o'tishi shart — bitta xato ham nomzodni rad etadi",
           "> ([ADR-0004](../../docs/07-adr/0004-judge-engine.md))."]

    report = "\n".join(md) + "\n"
    print(report)
    if args.out:
        pathlib.Path(args.out).write_text(report, encoding="utf-8")
        print(f"→ {args.out}")

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
