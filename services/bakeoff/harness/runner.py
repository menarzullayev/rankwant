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
# Bu case'larda SECURITY_VIOLATION ideal, lekin RE_* ham qabul qilinadi.
#
# Sabab: SECURITY_VIOLATION sandbox jarayonni O'LDIRGAN holat uchun (seccomp/SIGSYS).
# Bloklangan tarmoq yoki fayl urinishi esa dasturda oddiy istisno bo'ladi va
# jarayon o'zi nolga teng bo'lmagan kod bilan chiqadi — bu RE. Ya'ni verdict
# satri xavfsizlik kafolatining dalili EMAS.
#
# `RE` ikkiga ajratilgandan keyin (`RE_SIGNAL`/`RE_EXIT`) bu tolerantlik
# ANIQROQ bo'ldi: yuqoridagi «o'zi chiqadi» ta'rifi aynan `RE_EXIT`, seccomp
# o'ldirgan holat esa `RE_SIGNAL` yoki `SECURITY_VIOLATION`. Uchalasi ham
# qabul qilinadi — kafolatni pastdagi MODDIY tekshiruvlar beradi:
# host faylining yo'qligi, tarmoqqa chiqa olmaslik, /proc niqobi.
#
# Haqiqiy kafolat quyidagi MODDIY tekshiruvlar bilan tasdiqlanadi:
#   - /etc/rankwant_pwned yaratilmagan
#   - chiqishda CONNECTED yo'q
#   - chiqishda host jarayon ma'lumoti yo'q
ISOLATION_TOLERANT = {"09-fork-bomb", "10-file-write", "11-network",
                      "12-proc-read", "13-symlink"}
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
        "checker": case.get("checker") or {"type": "standard"},
        "mode": case["mode"],
        # Kirish validatori (19–21-case'lar). Qolganlarida `false`/`null`
        # ketadi — shartnomadagi standart qiymatlar.
        "validate_input": case.get("validate_input", False),
        "validator": case.get("validator"),
    }
    r.lpush(JOBS_KEY, json.dumps(job))
    return job_id


def other_consumer(r: "redis.Redis") -> bool:
    """Natijalar navbatini BOSHQA kimdir bo'shatyaptimi.

    To'liq stack ustida yurgizilganda `judging.drain_results` (Celery
    beat, har 2 s) natijalarni bizdan oldin olib ketadi — o'shanda case
    «natija kelmadi» bo'ladi va hisobot XAVFSIZLIKDAN O'TMADI deb yozadi.
    O'lchandi: aynan shu holatda 11-network va 13-symlink «yiqilgan»
    ko'rindi, worker to'xtatilgach ikkalasi ham o'tdi.

    Yolg'on xavfsizlik signali chinidan xavfliroq: u ishonchni yo'qotadi
    va keyingi safar haqiqiy signal ham e'tiborsiz qoladi.
    """
    probe = json.dumps({"job_id": "__bakeoff_probe__", "verdict": "PROBE"})
    r.lpush(RESULTS_KEY, probe)
    time.sleep(3)
    # O'zimiz qo'ygan yozuv joyidamikan?
    for item in r.lrange(RESULTS_KEY, 0, -1):
        if b"__bakeoff_probe__" in (item if isinstance(item, bytes) else item.encode()):
            r.lrem(RESULTS_KEY, 1, item)
            return False
    return True


def collect(r: "redis.Redis", expected: int, timeout_s: int) -> dict[str, dict]:
    got: dict[str, dict] = {}
    deadline = time.monotonic() + timeout_s
    while len(got) < expected and time.monotonic() < deadline:
        try:
            item = r.brpop(RESULTS_KEY, timeout=2)
        except redis.exceptions.TimeoutError:
            # brpop blokirovkasi socket timeout'idan uzunroq bo'lsa yuz beradi.
            # Bu nosozlik emas — navbat bo'sh, kutishda davom etamiz.
            continue
        except redis.exceptions.ConnectionError:
            time.sleep(0.5)
            continue
        if not item:
            continue
        res = json.loads(item[1])
        got[res["job_id"]] = res
    return got


def expected_verdict(case: dict, worker: str) -> str:
    """Nomzodga xos kutilgan verdict.

    Shartnoma ba'zan ikki xil TO'G'RI javobni tan oladi: validator bosqichi
    yo'q nomzod `validate_input` ishini `IE` bilan rad etishi shart
    (protocol.md § «Kirish validatori»). Bu yiqilish emas — yopiq yiqilish.
    """
    return case.get("expect_by_worker", {}).get(worker, case["expect_verdict"])


def judge_case(case: dict, res: dict | None, worker: str) -> tuple[str, list[str]]:
    """Qaytaradi: ('PASS'|'FAIL'|'TIMEOUT', izohlar)."""
    notes: list[str] = []
    if res is None:
        return "TIMEOUT", ["natija kelmadi"]

    verdict = res.get("verdict")
    want = expected_verdict(case, worker)

    ok = verdict == want
    # Fork bomb cgroup pids.max da qamalsa, jarayonlar CPU limitiga uriladi →
    # TLE. Bu ham to'g'ri natija: muhimi host himoyalangani, verdict satri emas.
    tolerated = {"RE", "RE_SIGNAL", "RE_EXIT", "SECURITY_VIOLATION"}
    if case["id"] == "09-fork-bomb":
        tolerated.add("TLE")
    if not ok and case["id"] in ISOLATION_TOLERANT and verdict in tolerated:
        ok = True
        notes.append(f"{verdict} (SECURITY_VIOLATION o'rniga qabul qilindi)")

    if not ok:
        notes.append(f"kutilgan {want}, kelgan {verdict}")

    # Host yon-ta'siri — bu MUZOKARA QILINMAYDI
    artifact = HOST_ARTIFACTS.get(case["id"])
    if artifact and artifact.exists():
        return "FAIL", notes + [f"XAVFSIZLIK: {artifact} yaratilgan — sandbox yorilgan"]

    if case["id"] == "11-network":
        out = json.dumps(res.get("per_test", []), ensure_ascii=False)
        if "CONNECTED" in out:
            return "FAIL", notes + ["XAVFSIZLIK: tarmoqqa chiqish muvaffaqiyatli bo'lgan"]
        notes.append("tarmoq bloklangan (moddiy tekshiruv)")

    if case["id"] == "12-proc-read":
        # Host PID 1 cmdline sizganini aniqlash: verdict WA/AC bo'lsa, dastur
        # /proc ni MUVAFFAQIYATLI o'qigan demak — bu izolyatsiya teshigi.
        if verdict in {"AC", "WA"}:
            return "FAIL", notes + ["XAVFSIZLIK: host /proc o'qilgan (dastur xatosiz yakunlandi)"]
        notes.append("/proc niqoblangan (moddiy tekshiruv)")

    # Validator case'lari: verdict satrining o'zi yetmaydi. `WRONG_TEST`
    # submission bir testda ishlab bo'lgandan keyin ham kelishi mumkin —
    # kafolat esa «submission UMUMAN ishga tushmadi».
    if case.get("expect_no_run") and res.get("per_test"):
        return "FAIL", notes + [
            f"submission {len(res['per_test'])} ta testda ishga tushdi — "
            "validatsiya undan OLDIN tugashi shart"
        ]
    if "expect_failed_test_index" in case and want == case["expect_verdict"]:
        got_index = res.get("failed_test_index")
        if got_index != case["expect_failed_test_index"]:
            return "FAIL", notes + [
                f"failed_test_index {got_index}, kutilgan {case['expect_failed_test_index']}"
            ]
        notes.append(f"birinchi yaroqsiz test #{got_index}, submission ishga tushmagan")

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
    ap.add_argument(
        "--cases", default="",
        help="faqat shu case'lar — vergul bilan id prefikslari, masalan 01,19,20,21",
    )
    args = ap.parse_args()

    # socket_timeout brpop blokirovkasidan (2s) kattaroq bo'lishi shart
    r = redis.Redis.from_url(args.redis, socket_timeout=30, socket_connect_timeout=10)
    r.delete(JOBS_KEY, RESULTS_KEY)

    cases = load_cases()
    if args.cases:
        prefixes = tuple(p.strip() for p in args.cases.split(",") if p.strip())
        cases = [c for c in cases if c["id"].startswith(prefixes)]
        if not cases:
            print(f"--cases {args.cases!r} hech bir case'ga mos kelmadi", file=sys.stderr)
            return 2
    print(f"Nomzod: {args.worker} · {len(cases)} ta case\n")

    # Boshqa iste'molchi natijalarni olib ketsa, hisobot XAVFSIZLIK
    # yiqilishi bo'lib chiqadi — aslida sandbox soz. Buni oldindan
    # aytamiz, chunki yolg'on xavfsizlik signali chinidan xavfliroq.
    if other_consumer(r):
        print(
            "TO'XTATILDI: natijalar navbatini boshqa jarayon bo'shatyapti.\n"
            "  To'liq stack ishlayotgan bo'lsa `judging.drain_results` (Celery beat)\n"
            "  natijalarni bizdan oldin oladi va case'lar «natija kelmadi» bo'ladi.\n"
            "  Yechim: `docker compose stop worker beat` yoki alohida Redis.\n",
            file=sys.stderr,
        )
        return 2

    # ── XAVFSIZLIK DARVOZASI ────────────────────────────────────────────
    # 09-fork-bomb host'ni yiqitishi mumkin, agar worker cgroup limitlarini
    # qo'ya olmasa. 2026-09-06 da aynan shu bo'ldi: limitlar jimgina
    # qo'yilmagan, fork bomb cheklovsiz ko'paygan, global OOM va swap
    # thrashing mashinani ikki marta qotirgan.
    #
    # Shuning uchun: avval 05-mle ni yuboramiz. U MLE qaytarsa, xotira
    # limiti HAQIQATAN ishlayapti degani. Faqat shundan keyin fork bomb.
    # Hali yozilmagan funksiyalar nomzodni rad etmasligi kerak —
    # ular sandbox sifati emas, ish hajmi masalasi.
    pending = [c for c in cases if c.get("implemented") is False]
    cases = [c for c in cases if c.get("implemented") is not False]

    DANGEROUS = {"09-fork-bomb"}
    safe = [c for c in cases if c["id"] not in DANGEROUS]
    dangerous = [c for c in cases if c["id"] in DANGEROUS]

    ids = {submit(r, c): c for c in safe}
    t0 = time.monotonic()
    results = collect(r, len(safe), args.timeout)

    mle = next((v for k, v in results.items()
                if ids[k]["id"] == "05-mle"), None)
    limits_proven = bool(mle) and mle.get("verdict") == "MLE"

    if dangerous:
        if limits_proven:
            print("  ✓ xotira limiti tasdiqlandi (05-mle → MLE) — fork bomb ishga tushirilmoqda")
            dids = {submit(r, c): c for c in dangerous}
            ids.update(dids)
            results.update(collect(r, len(dids), args.timeout))
        else:
            got = mle.get("verdict") if mle else "natija yo'q"
            print(f"  ⚠ XAVFSIZLIK DARVOZASI: 05-mle → {got} (MLE emas).")
            print("    Xotira limiti ishlashi isbotlanmadi — fork bomb O'TKAZIB YUBORILDI.")
            print("    Sabab: limitsiz fork bomb host'ni global OOM ga olib boradi.")
            for c in dangerous:
                ids[f"__skipped__{c['id']}"] = c
    wall = time.monotonic() - t0

    rows, failures, latencies = [], 0, []
    for job_id, case in ids.items():
        if job_id.startswith("__skipped__"):
            rows.append((case["id"], case["expect_verdict"], "—", "SKIP", "—",
                         "xavfsizlik darvozasi: limitlar isbotlanmagan"))
            failures += 1
            continue
        res = results.get(job_id)
        status, notes = judge_case(case, res, args.worker)
        if status != "PASS":
            failures += 1
        meta = (res or {}).get("judge_meta") or {}
        if meta.get("total_ms"):
            latencies.append(float(meta["total_ms"]))
        want = expected_verdict(case, args.worker)
        rows.append((case["id"], want, (res or {}).get("verdict", "—"),
                     status, meta.get("total_ms", "—"), "; ".join(notes)))

    for c in pending:
        rows.append((c["id"], c["expect_verdict"], "—", "PENDING", "—",
                     "hali yozilmagan — ADR-0004 da ochiq band"))

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
        mark = {"PASS": "✅", "FAIL": "❌", "TIMEOUT": "⏱", "SKIP": "⏭", "PENDING": "🔧"}[st]
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
