# Judge bake-off — Sprint 0.5

[ADR-0004](../../docs/07-adr/0004-judge-engine.md) ni `proposed` → `accepted` ga o'tkazish uchun.
Bu **gate**: tugamaguncha Sprint 3 (submit oqimi) boshlanmaydi ([09](../../docs/09-development-plan/README.md)).

## Nomzodlar

| | Worker | Sandbox | Litsenziya |
| - | ------ | ------- | ---------- |
| **A** | Go | [nsjail](https://github.com/google/nsjail) | Apache-2.0 |
| **B** | Python | [isolate](https://github.com/ioi/isolate) | GPL-2.0+ |

Ikkalasi ham [protocol.md](protocol.md) shartnomasini bajaradi — ya'ni **almashtiriladigan**.

## Tuzilish

```
bakeoff/
├── protocol.md        job/result JSON shartnomasi (08-technical-spec dan)
├── cases/             14 ta sinov case — manba, limit, kutilgan verdict
└── harness/runner.py  o'lchash va hisobot
```

## Ishga tushirish

```bash
docker compose up -d redis
pip install redis

# 1-terminal: nomzodni ishga tushirish
cd services/judge-go && make run          # yoki: services/judge-py

# 2-terminal: o'lchash
python3 services/bakeoff/harness/runner.py \
    --worker judge-go \
    --load 50 \
    --out services/bakeoff/result-judge-go.md
```

Chiqish kodi: `0` — hamma case o'tdi · `1` — kamida bittasi yiqildi.

## Sinov to'plami

| Case | Kutilgan | Nimani o'lchaydi |
| ---- | -------- | ---------------- |
| `01-aplusb` | AC | bazaviy oqim, start latency |
| `02-wa` | WA | noto'g'ri javob aniqlanadimi |
| `03-tle-cpu` | TLE | **CPU vaqti** o'lchanadimi (wall emas) |
| `04-idleness` | IDLENESS | uxlash TLE deb hisoblanmaydimi |
| `05-mle` | MLE | peak RSS aniqligi |
| `06-re` | RE | runtime error |
| `07-ce` | CE | `compile_output` to'ldiriladimi |
| `08-ole` | OLE | chiqish limiti |
| `09-fork-bomb` | 🔒 | process limiti host'ni himoya qiladimi |
| `10-file-write` | 🔒 | sandbox tashqarisiga yozib bo'lmasligi |
| `11-network` | 🔒 | tarmoq izolyatsiyasi |
| `12-proc-read` | 🔒 | host `/proc` sizmasligi |
| `13-symlink` | 🔒 | Judge0 **CVE-2024-28185** vektori |
| `14-interactive` | AC | ikki tomonlama I/O |

🔒 = izolyatsiya sinovi. **Hammasi o'tishi shart** — bittasi yiqilsa nomzod rad etiladi.

## O'tish sharti

1. **Izolyatsiya:** 🔒 belgilangan 5 case'ning hammasi o'tadi va **host yon-ta'siri yo'q**
   (harness `/etc/rankwant_pwned` mavjudligini va tarmoq ulanishini alohida tekshiradi)
2. **Latency:** funksional to'plamda p50 < 5 s, p95 < 15 s ([04-prd](../../docs/04-prd/README.md) NFR)
3. **O'lchash aniqligi:** `03-tle-cpu` da CPU vaqti, `04-idleness` da wall vaqti to'g'ri ajratiladi
4. **Yuklama:** 50 parallel submit — natija yo'qolmaydi

## Qaror

G'olib aniqlangach: [ADR-0004](../../docs/07-adr/0004-judge-engine.md) `accepted` ga o'tkaziladi,
yutgan variant va o'lchov natijalari yoziladi, yutqazgan `services/` dan olib tashlanadi.
