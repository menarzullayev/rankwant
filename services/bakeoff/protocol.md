# Judge protokoli — bake-off shartnomasi

Ikkala nomzod ham **aynan shu** shartnomani bajaradi. Shartnoma [08-technical-spec](../../docs/08-technical-spec/README.md) 🔒 dan olingan; bu yerda bake-off uchun aniqlashtirilgan.

## Transport — PULL

[ADR-0004](../../docs/07-adr/0004-judge-engine.md): worker navbatdan ish tortadi, kiruvchi port ochmaydi.

```
Redis LIST  rankwant:judge:jobs      worker BRPOP qiladi
Redis LIST  rankwant:judge:results   worker LPUSH qiladi
```

Worker `DATABASE_URL` **olmaydi**. Faqat `REDIS_URL` va S3 (bake-off'da local katalog).

## Job

```json
{
  "job_id": "uuid",
  "attempt_id": 12345,
  "language": {
    "code": "cpp23",
    "compile": ["g++", "-std=c++23", "-O2", "-o", "{bin}", "{src}"],
    "run": ["{bin}"]
  },
  "source": "…manba kod…",
  "limits": {
    "compile_time_ms": 10000,
    "time_ms": 1000,
    "memory_kb": 262144,
    "output_kb": 65536,
    "processes": 1
  },
  "tests": [
    {"index": 1, "input": "1 2\n", "expected": "3\n"}
  ],
  "checker": {"type": "standard"},
  "mode": "acm"
}
```

`mode: acm` — birinchi muvaffaqiyatsiz testda to'xtaydi. `mode: ioi` — hamma test bajariladi.

## Result

```json
{
  "job_id": "uuid",
  "attempt_id": 12345,
  "verdict": "AC",
  "score": 100,
  "time_ms": 12,
  "memory_kb": 3420,
  "failed_test_index": null,
  "compile_output": "",
  "per_test": [
    {"index": 1, "verdict": "AC", "time_ms": 12, "memory_kb": 3420}
  ],
  "judge_meta": {
    "worker": "judge-go",
    "sandbox": "nsjail",
    "queue_wait_ms": 4,
    "sandbox_setup_ms": 11,
    "total_ms": 78
  }
}
```

`judge_meta` — **bake-off uchun majburiy**: `sandbox_setup_ms` va `total_ms` ADR-0004 dagi latency mezonini o'lchaydi.

## Verdict kodlari

Bake-off'da ishlatiladigan qism (to'liq 20 ta: [08](../../docs/08-technical-spec/README.md)):

`AC` · `WA` · `TLE` · `MLE` · `OLE` · `RE` · `CE` · `COMPILE_TIMEOUT` · `IDLENESS` · `SECURITY_VIOLATION` · `IE`

## Vaqt o'lchash — muhim farq

- `time_ms` — **CPU vaqti** (user + sys), wall clock emas.
  Sabab: judge host yuklangan bo'lsa wall clock adolatsiz TLE beradi.
- `IDLENESS` — CPU vaqti kam, lekin wall clock chegaradan oshgan (interactive'da deadlock).
- `memory_kb` — **peak RSS**.

Bu uchtasining aniqligi bake-off'ning asosiy o'lchovi: noto'g'ri o'lchash → adolatsiz verdict → **reyting ishonchsiz**.
