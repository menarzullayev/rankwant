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
    "compile": [
      "g++",
      "-std=c++23",
      "-O2",
      "-o",
      "{bin}",
      "{src}"
    ],
    "run": [
      "{bin}"
    ]
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
    {
      "index": 1,
      "input": "1 2\n",
      "expected": "3\n"
    }
  ],
  "checker": {
    "type": "standard"
  },
  "subtasks": [
    {
      "id": 1,
      "points": 40,
      "scoring": "min"
    }
  ],
  "mode": "acm",
  "validate_input": false,
  "validator": null
}
```

`mode: acm` — birinchi muvaffaqiyatsiz testda to'xtaydi. `mode: ioi` — hamma test bajariladi.

## Kirish validatori

`validator` — masala bilan keladigan, test cheklovlarga mosligini tekshiruvchi dastur ([ADR-0020](../../docs/07-adr/0020-hacking.md)). Shakli `checker.program` bilan bir xil: `{code, compile, run, source}`.

Chaqirilishi: kiritma **stdin** orqali beriladi. Chiqish kodi `0` — kiritma to'g'ri; nolga teng bo'lmasa — cheklov buzilgan, sababi **stderr**'da (testlib shunday yozadi).

| Maydon | Ma'nosi |
| ------ | ------- |
| `validate_input` | `true` bo'lsa, HAMMA test kirishi submission kompilyatsiya qilinishidan va ishga tushishidan OLDIN validatordan o'tadi |
| `validator` | validator dasturi; `validate_input: true` bo'lsa MAJBURIY |

Qoidalar shartnomaning bir qismi:

1. **Validator sandbox ICHIDA ishlaydi.** Checker va interactor undan farq qiladi — ular sandboxsiz bajariladi, chunki ularning kiritmasi ham bizniki. Validatorning kiritmasi esa ishonchsiz: u hacker yuborgan test bo'lishi mumkin, va u validatorning o'zini cheksiz aylantirib navbatni to'xtatib qo'yishi mumkin.
2. **Alohida bosqich, alohida katalog.** Validator submission bilan bitta `/box` ni bo'lishmaydi: o'z katalogida kompilyatsiya qilinadi va ishlaydi, bosqich tugagach katalog o'chiriladi. Submission `/box` ga yoza oladi — validator testlar orasida o'sha joyda ishlasa, 1-testda ishga tushgan submission validatorni almashtirib keyingi tekshiruvlarni chetlab o'tardi. Interactive masalalar ham shu bosqichdan o'tadi.
3. **Submission yo'l shartnomasi.** Kompilyatsiya ham sandbox ichida; fayl nomi va `{src}` / `{bin}` o'rinlari submission'niki bilan bir xil (`/box/main.cpp`, `/box/Main.java`, `/box/prog`). Shunda submission uchun ishlaydigan har til validator uchun ham ishlaydi.
4. **O'z chegaralari.** Masala limitlari submission uchun, validator ularni meros olmaydi: CPU 5 s, wall 10 s, xotira 1 GiB, 64 jarayon (JVM oqimlari `pids.max` da sanaladi), stdout 1 MB; kompilyatsiya 30 s. Aks holda tor limitli masalada TO'G'RI kiritma `WRONG_TEST` olardi.
5. **Yopiq yiqilish.** `validate_input: true` kelgan, lekin validatorni qo'llab-quvvatlamaydigan nomzod ishni `IE` bilan RAD ETISHI shart. Jimgina o'tkazib yuborish validatsiyani butunlay o'chirib qo'yardi — nomzodlar almashtiriladigan bo'lgani uchun bu xavf nazariy emas.

Natija:

| Holat | `verdict` | `failed_test_index` | `compile_output` |
| ----- | --------- | ------------------- | ---------------- |
| hamma kiritma to'g'ri | submission odatdagidek baholanadi | odatdagidek | odatdagidek |
| kiritma rad etildi: kod ≠ 0, vaqt yoki chiqish chegarasi | `WRONG_TEST` | birinchi yaroqsiz test | validator xabari, 1 KB gacha |
| validator kompilyatsiya qilinmadi yoki ishga tushmadi | `IE` | `null` | sabab |
| `validate_input: true`, `validator: null` | `IE` | `null` | sabab |

`WRONG_TEST` da `per_test` bo'sh — submission ishga tushmagan; bu submission aybi emas, test yaroqsiz. Hack qatlamida u `INVALID_INPUT` natijasiga aylanadi ([ADR-0020](../../docs/07-adr/0020-hacking.md), 4-qaror). Validator ishlamay qolsa `IE` qaytadi — hacker testi nohaq «yaroqsiz» deb belgilanmaydi.

Nomzodlar: `judge-go` da bosqich to'liq; `judge-py` da bosqich yo'q, 5-qoida bo'yicha `IE` (bake-off `19`–`21`).

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

`AC` · `WA` · `PE` · `TLE` · `MLE` · `OLE` · `RE_SIGNAL` · `RE_EXIT` · `CE` · `COMPILE_TIMEOUT` · `IDLENESS` · `SECURITY_VIOLATION` · `CHECKER_ERROR` · `WRONG_TEST` · `PARTIAL` · `IE`

`RE` — eski kod, judge endi uni chiqarmaydi: signal bilan o'ldirilgan
dastur (`RE_SIGNAL`) va o'zi nolga teng bo'lmagan kod bilan chiqqan
dastur (`RE_EXIT`) ajratildi (DMOJ modeli).

## Vaqt o'lchash — muhim farq

- `time_ms` — **CPU vaqti** (user + sys), wall clock emas.
  Sabab: judge host yuklangan bo'lsa wall clock adolatsiz TLE beradi.
- `IDLENESS` — CPU vaqti kam, lekin wall clock chegaradan oshgan (interactive'da deadlock).
- `memory_kb` — **peak RSS**.

Bu uchtasining aniqligi bake-off'ning asosiy o'lchovi: noto'g'ri o'lchash → adolatsiz verdict → **reyting ishonchsiz**.
