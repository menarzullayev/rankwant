# Test strategiyasi — RankWant

**STATUS:** draft (2026-09-06) · [10-operations](README.md) ning bir qismi

15 qatlam. Taksonomiya umumiy, **misollar CP/OJ platformasiga xos** — bot yoki e-commerce'ga emas.

## Test piramidasi

```
                       E2E
                     /     \
                Smoke       Security
               /                  \
          Integration          Performance
            /                        \
         Unit               Load / Stress / Spike / Soak
```

Asos keng (unit), tepa tor (E2E) — lekin RankWant'da **Security qatlami piramidadan tashqarida turadi**: sandbox escape mahsulot xatosi emas, host kompromissi.

---

## 1. Functional

«Nima qilishi kerak?» degan savolga javob.

| Ssenariy | Kutilgan |
| -------- | -------- |
| To'g'ri yechim yuborish | `AC`, `time_ms`/`memory_kb` to'ldirilgan |
| Cheksiz sikl | `TLE`, wall time emas **CPU time** bo'yicha |
| 1 GB massiv | `MLE` |
| Sintaksis xatosi | `CE` + `compile_output` |
| Contest tugagach submit | rad etiladi |
| Admin endpoint, oddiy user | `403` |
| `read` scope'li PAT bilan submit | `403` |
| Noto'g'ri `difficulty` (750, 850) | validatsiya xatosi (800–3500, qadam 100) |

## 2. Unit

Tashqi bog'liqliklar (Telegram API, DB, Redis, S3) **mock** qilinadi.

| Funksiya | Nima tekshiriladi |
| -------- | ----------------- |
| `skills_rating(solved)` | monotonlik, 20× chegara, ~45 to'yinish ([04-prd](../04-prd/README.md)) |
| `elo_seed(ratings)` | seed yig'indisi = N |
| `elo_delta(...)` | inflyatsiya tuzatishidan keyin `Σd ≈ 0` |
| `activity_rating(window)` | maksimal 510; oyna siljishi |
| `qvant_balance(txns)` | ledger yig'indisi = balans; refund |
| `acm_penalty(...)` | noto'g'ri urinish jarimasi |
| `difficulty_to_level(d)` | 1199→Boshlang'ich, 1200→O'rta chegaralari |
| `verdict_from_tests(...)` | birinchi mag'lubiyat verdicti qaytadi |

**Property-based test** (Hypothesis) reyting formulalari uchun majburiy — monotonlik va chegaralar tasodifiy kirishda ham buzilmasligi kerak.

## 3. Integration

Haqiqiy test DB va Redis; judge **fake provider** bilan.

```
POST /api/v1/attempts/
   → handler → service → repository → PostgreSQL
   → navbatga qo'yildi
   → fake judge natija qaytardi
   → Attempt.verdict yangilandi
   → Standing qayta hisoblandi
   → UserSolvedProblem yaratildi
   → RatingHistory yozuvi paydo bo'ldi
```

Alohida tekshiriladi: Celery task'lari real Redis bilan · migration'lar bo'sh DB da to'liq o'tadi · `drf-spectacular` schema generatsiyasi buzilmaydi.

## 4. E2E

Foydalanuvchi nuqtai nazaridan, real brauzer (Playwright).

**Oqim A — birinchi AC:**
```
ro'yxatdan o'tish → login → masala ochish → C++ kod → submit
   → verdict AC → Skills reyting oshdi → profilda ko'rinadi
   → RatingHistory da sabab yozilgan
```

**Oqim B — contest:**
```
contest yaratish (is_rated, 3 masala) → 3 user ro'yxatdan o'tdi
   → submitlar → standings tartibi va penalty to'g'ri
   → freeze oxirgi 30 daqiqada ishlaydi
   → contest tugadi → Contests reytingi qayta hisoblandi
   → har userda RatingHistory (seed, rank, delta)
```

**Oqim C — Qvant (Phase 1):**
```
kunlik quest bajarish → +10 Qvant → ledgerda yozuv
   → do'konda streak freeze sotib olish → balans kamaydi
   → Activity reyting quest sonidan hisoblandi (balansdan EMAS)
```

## 5. Smoke

Deploydan keyin, tez va kam sonli. `tests/smoke/check.py` — compose
tarmog'i ichida ishlaydi, CI da har PR da to'liq stack ko'tariladi:

- [x] API masalalar ro'yxatini beradi
- [x] OpenAPI sxemasi ochiladi
- [x] SSR api'dan ma'lumot oladi (brauzer va server manzillari boshqa)
- [x] Autentifikatsiya: register → login → himoyalangan endpoint
- [x] **Canary submit** — `a-plus-b` ga to'g'ri yechim → `AC`

Oxirgi qadam API va judge'ni birga ishlatadigan yagona joy. U qo'shilganda
darhol uchta uzilish topdi: compose'da Celery worker/beat yo'q edi, API
`input_ref` yuborib judge `input` kutardi, va judge natijada `attempt_id`
qaytarmasdi. Uchalasi ham alohida test to'plamlarida ko'rinmagan edi.

Canary submit **eng muhimi**: qolgan hammasi tirik bo'lib, judge o'lik bo'lishi mumkin.

## 6. Regression

**Golden set:** ~50 masala × ma'lum yechimlar × kutilgan verdict. Har PR da ishlaydi.

Yangi feature qo'shilganda golden set qayta ishlatiladi:
`AC` → `AC`, `TLE` → `TLE` — verdictlar **o'zgarmasligi** shart. Judge engine almashsa (bake-off g'olibi) bu to'plam mos kelishning asosiy dalili.

## 7. Load — kutilayotgan yuklama

| Ssenariy | Maqsad |
| -------- | ------ |
| 100 / 500 / 1000 parallel ko'rish | p95 sahifa < 1s |
| 50 submit/sek barqaror | judge p50 < 5s, p95 < 15s |
| Standings so'rovi 500 ishtirokchida | < 300 ms |

O'lchanadi: latency, throughput, CPU/RAM, DB connection pool, navbat uzunligi, error rate.

## 8. Stress — sig'imdan oshirish

Submit oqimini navbat to'yingunicha oshirish: `50 → 100 → 250 → 500 submit/sek`.

Savol: **qachon va qanday buziladi?** Talab: **ma'lumot yo'qolmasligi** — navbat uzaysa ham har `Attempt` DB da qoladi va oxir-oqibat tekshiriladi. Qabul qilinadigan degradatsiya: kutish vaqti oshadi. Qabul qilinmaydi: submit yo'qoladi yoki `IE` beradi.

## 9. Spike — keskin sakrash

**RankWant uchun eng real ssenariy: contest boshlanishi.**

```
0 submit/sek
      ↓  (contest boshlandi)
500 submit 10 soniya ichida
```

Tekshiriladi: navbat qabul qiladimi · birinchi 10 s da 5xx bo'lmaydimi · standings SSE oqimi uzilmaydimi · autoscale (worker qo'shish) qancha vaqtda reaksiya qiladi.

## 10. Soak / Endurance

`50 submit/sek ──────── 12 soat ────────`

Qidiriladigan muammolar:

- Judge worker'da **memory leak**
- **Sandbox chiqindisi** — qolib ketgan cgroup, mount, `/tmp` kataloglari (CP judge'da klassik nosozlik)
- DB connection exhaustion
- Navbat asta-sekin to'planishi
- Redis xotira o'sishi (session + queue)

## 11. Security — eng yuqori daraja

### 11a. Sandbox escape (kritik)

| Hujum | Kutilgan |
| ----- | -------- |
| Fork bomb | process limiti ushlaydi, host ta'sirlanmaydi |
| Sandbox tashqarisiga fayl yozish | rad etiladi |
| Symlink orqali binary almashtirish | rad etiladi (Judge0 CVE-2024-28185 vektori) |
| Tarmoqqa chiqish | bloklanadi |
| `/proc`, `/sys` o'qish | cheklanadi |
| `setuid` / capability ko'tarish | bloklanadi |
| Boshqa submit fayllarini o'qish | bloklanadi |

Har biri `SECURITY_VIOLATION` verdicti va **alert** chiqarishi kerak.

### 11b. Ilova darajasi

- **IDOR** — boshqa foydalanuvchi attempt manbasini contest tugamasdan o'qish
- **Auth bypass** — admin endpointga oddiy session/PAT bilan
- **PAT scope** — `read` token submit qila olmaydi; muddati o'tgan token rad etiladi
- **Injection** — masala matni, username, contest nomida
- **Secret sizishi** — log, xato javobi, Sentry payload'ida token/parol yo'qligi
- **Rate-limit bypass** — IP almashtirish, header spoofing

## 12. Abuse / rate-limit

| Hujum | Kutilgan |
| ----- | -------- |
| 1000 so'rov/sek bitta userdan | `429`, downstream himoyalangan |
| Submit spam | 1/10s limiti ([ADR-0008](../07-adr/0008-auth-session-plus-pat.md)) |
| **Qvant farming** — bir masalani qayta yechish | 0 Qvant ([ADR-0002](../07-adr/0002-qvant-economy.md)) |
| Kunlik Qvant limitidan oshirish | 100 Qvant/kun da to'xtaydi |
| Ko'p akkaunt bilan quest | anomaliya alerti |

## 13. Recovery

| Nosozlik | Kutilgan xatti-harakat |
| -------- | ---------------------- |
| Postgres DOWN | API toza `503`, ma'lumot yo'qolmaydi; UP bo'lgach normal davom |
| Redis DOWN | submit qabul qilinmaydi, **lekin `Attempt` yozuvi saqlanadi**; UP bo'lgach navbatga qaytadi |
| Judge worker o'ldi | tekshirilayotgan attempt qayta navbatga tushadi, yo'qolmaydi |
| S3 mavjud emas | judge `IE` emas, **qayta urinish**; N martadan keyin `DENIAL_OF_JUDGEMENT` |

## 14. Chaos / fault injection

Staging'da ataylab buzish: judge worker'ni tekshiruv o'rtasida `kill -9` · DB latency `+5s` · S3 `500` qaytarish · Redis paket yo'qotish · **contest davomida** judge host o'chirish.

Har birida tekshiriladi: ma'lumot yo'qolmadimi, foydalanuvchi tushunarli
xato ko'rdimi, tizim o'zi tiklandimi. Skript endi shu uchtasini
TASDIQLAYDI — avval faqat health kodini chop etib, xulosani odamga
qoldirardi.

Ilk haqiqiy ishga tushirish ikkita nuqson topdi: `/health/` shartsiz
`ok` qaytarardi (Postgres o'lganda ham 200), va Redis uzilganda throttle
backend'i yiqilib har so'rov 500 berardi — 10-operations va'da qilgan
«toza 503» o'rniga.

## 15. Compatibility

- **Til matritsasi:** e'lon qilingan versiya judge image'idagi haqiqat bilan
  bir xilmi (`tests/compatibility/check_languages.py`). Har til o'z runtime
  versiyasini chop etadi, ya'ni e'londan mustaqil manba. Ilk ishga tushirishda
  ikki nomuvofiqlik topdi: `py312` amalda Python 3.11 edi, `cpp23` esa GCC 12
  da C++2b qoralamasi. Bunday farq foydalanuvchiga tushunarsiz `SyntaxError`
  bo'lib ko'rinadi va u aybni o'z kodidan qidiradi.
- Brauzer: Chrome, Firefox, Safari + mobil
- **i18n:** uz/ru/en render; masala matnidagi LaTeX/MathJax
- Kod muharriri: katta manba (64 KB chegarasi), unicode, tab/space
- **SSE proxy orqali** — ba'zi korporativ/maktab proxy'lari SSE oqimini buferlaydi; standings yangilanishi shu sabab qotib qolishi mumkin (fallback polling shart)

---

## CI/CD pipeline

```
                    PR
                     │
          ┌──────────┼──────────┐
          ▼          ▼          ▼
        Lint      mypy       Unit
          └──────────┼──────────┘
                     ▼
             Integration (test DB)
                     ▼
          Regression (golden set)
                     ▼
             OpenAPI schema diff
                     ▼
                   Build
                     ▼
              Deploy Staging
                     │
             ┌───────┴───────┐
             ▼               ▼
          Smoke             E2E
             └───────┬───────┘
                     ▼
        Security suite (sandbox escape)
                     ▼
              Production (qo'lda tasdiq)
                     ▼
           Production Smoke + Canary
```

**Nightly:** Load · Soak (haftalik) · Chaos (staging).
**Har release oldidan:** Stress · Spike.

## Amalga oshirilgan holat (2026-09-06)

| Qatlam | Holat | Joyi |
| ------ | ----- | ---- |
| Unit (formulalar, ledger, verdict) | ✅ | `apps/api/tests/`, `services/judge-py/test_judge.py` |
| Integration (submit → verdict → reyting) | ✅ | `apps/api/tests/test_judging.py` |
| Functional (API shartnomasi) | ✅ | `apps/api/tests/` — 190 test |
| Regression (golden set) | ✅ | `services/bakeoff/cases/` — 14 case |
| Security — sandbox escape | ✅ | `services/bakeoff` izolyatsiya case'lari + `tests/security/run.sh` |
| Security — ilova (IDOR, PAT scope, rate limit) | ✅ | testlar + `tests/security/run.sh` |
| E2E | ✅ | `tests/e2e/` — CI da compose stack'iga qarshi |
| Load | ✅ | `tests/load/main.js` `ci` ssenariysi — nightly, compose stack |
| Stress / Spike / Soak | ✅ skript | `tests/load/main.js` — staging kerak |
| Chaos | ✅ | `tests/chaos/run.sh` — nightly, compose stack |
| Smoke | ✅ | `tests/smoke/` — CI da to'liq compose stack |
| Compatibility — til matritsasi | ✅ | `tests/compatibility/` — nightly |
| Compatibility — brauzer | ✅ | Chromium · Firefox · WebKit · mobil — nightly |

«Skript» degani: yozilgan va sintaksis tekshirilgan, lekin **ishlayotgan
staging'siz bajarilmaydi**. Ular nightly workflow'da `STAGING_URL`
sozlangandagina ishga tushadi.

E2E avval shu toifada edi. Uni compose stack'iga qarshi haqiqatan ishga
tushirgach uchta nosozlik chiqdi: `package-lock.json` commit qilinmagan
(ya'ni `npm ci` ishlamas edi), sarlavha regex'ida `+` ekranlanmagan, va
sessiya bilan POST qilishda CSRF sarlavhasi yuborilmagan. Yozilgan, lekin
hech qachon bajarilmagan test — bajarilgan test emas.

## Vositalar

| Qatlam | Vosita |
| ------ | ------ |
| Unit / Integration | `pytest`, `pytest-django`, `factory_boy`, `Hypothesis` |
| Mock | `pytest-mock`, fake `JudgeProvider` |
| Test DB | `testcontainers` yoki docker-compose service |
| E2E | Playwright |
| Load / Stress / Spike / Soak | k6 |
| Security | maxsus judge harness + `bandit`, `pip-audit`, `npm audit` |
| Chaos | staging'da skript (`kill`, `tc netem`, S3 mock) |

## Majburiy qamrov

[09 § Definition of Done](../09-development-plan/README.md) bo'yicha test **shart** bo'lgan sohalar:

1. Judge pipeline (submit → verdict)
2. 4 reyting formulasi
3. Qvant ledger
4. Auth va PAT scope

Bu to'rttasida qamrovsiz PR **birlashtirilmaydi**.
