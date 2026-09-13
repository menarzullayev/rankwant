# 8. Technical Specification

**STATUS:** locked (2026-09-06)

Stack [ADR-0003](../07-adr/0003-stack-django-next.md) · Auth [ADR-0008](../07-adr/0008-auth-session-plus-pat.md) · Judge [ADR-0004](../07-adr/0004-judge-engine.md)

## Stack va versiyalar

| Komponent  | Versiya / tanlov                                             |
| ---------- | ------------------------------------------------------------ |
| Python     | 3.12+                                                        |
| Django     | 5.2 **LTS** (6.0 emas — 2028 gacha qo'llab-quvvatlanadi)     |
| DRF        | joriy barqaror + `drf-spectacular`                           |
| Celery     | Redis broker                                                 |
| Node       | LTS                                                          |
| Next.js    | joriy barqaror + React 19                                    |
| TypeScript | 5.x, `strict`                                                |
| Tailwind   | 4.x + shadcn/ui                                              |
| PostgreSQL | 16+                                                          |
| Redis      | 7+ (cache + session + Celery broker + judge navbat)          |
| Sandbox    | bake-off: nsjail (Apache-2.0) / isolate (GPL-2.0+)           |

## Auth

**Web (birinchi tomon):** Django session, Redis backend.
Cookie: `httpOnly`, `Secure`, `SameSite=Lax`; muddat 30 kun, faollikda yangilanadi. CSRF — Django token, Next.js SSR uzatadi.

**API / bot (uchinchi tomon):** Personal Access Token.

```
Format:   rw_<32 bayt base62>
Header:   Authorization: Bearer rw_...
Saqlash:  SHA-256 hash; ochiq token faqat bir marta ko'rsatiladi
Scope:    read | submit | contest:manage
Muddat:   majburiy, maksimal 1 yil; foydalanuvchida ≤10 faol token
```

**Telegram:** login widget imzosi tekshiriladi → `User.telegram_id` bog'lanadi → **session** ochiladi.

### Rate limit

| Subyekt          | Limit                    |
| ---------------- | ------------------------ |
| Anonim           | 60 so'rov/min            |
| Session yoki PAT | 300 so'rov/min           |
| Submit           | 1 / 10s / foydalanuvchi  |
| Auth urinishi    | 10 / 15 min / IP         |

## API konvensiyalari

**Versiya:** URL prefiksda — `/api/v1/`. Buzuvchi o'zgarish = `/api/v2/`, eskisi ≥6 oy saqlanadi.

**Sahifalash:**

| Resurs                                  | Uslub                                   |
| --------------------------------------- | --------------------------------------- |
| `attempts`, `rating-history`, `qvant`   | **cursor** (o'sib boruvchi, barqaror)   |
| `problems`, `contests`, `users`         | limit/offset (filtr va sort bilan)      |

**Filtr:** `django-filter`; masalan `?difficulty__gte=1200&topics=dp&solved=false`

**Xato formati** — barcha 4xx/5xx uchun bir xil:

```json
{ "error": { "code": "rate_limited", "message": "…", "details": {} } }
```

**OpenAPI:** `drf-spectacular` → `/api/v1/schema/` (JSON) va `/api/v1/docs/` (Swagger UI).
Har PR da schema diff tekshiriladi — kutilmagan buzuvchi o'zgarish CI ni yiqitadi.

## Judge protokoli

**Model: PULL** ([ADR-0004](../07-adr/0004-judge-engine.md)) — judge host'da kiruvchi port **yo'q**.

```
API                    Redis navbat              Judge worker
 │                          │                          │
 ├── Attempt (PENDING) ─────┤                          │
 ├── enqueue(job) ─────────>│<──── BRPOP ──────────────┤
 │                          │                          ├── S3 dan test yuklab olish
 │                          │                          ├── compile → N test (sandbox)
 │                          │                          ├── checker
 │<──── natija yozish ──────┤<───── LPUSH result ──────┤
 └── Standing + Rating (Celery)                        │
```

**Tarmoq qoidasi:** judge → Redis ✅ · judge → S3 ✅ · judge → API/DB ❌ · tashqi internet ❌

### Job payload

```json
{
  "attempt_id": 12345,
  "language": {"code": "cpp23", "compile_cmd": "...", "run_cmd": "..."},
  "source_ref": "s3://…/12345.cpp",
  "limits": {"time_ms": 1000, "memory_kb": 262144, "output_kb": 65536},
  "tests": [{"index": 1, "input_ref": "s3://…/1.in", "output_ref": "s3://…/1.out"}],
  "checker": {"type": "standard", "ref": null},
  "mode": "acm"
}
```

> Testlar bitta `testset_ref` katalogi emas, har biri alohida havola bilan
> yuboriladi — subtask bog'lanishi va tartib uchun
> ([ADR-0010](../07-adr/0010-per-test-refs.md)).

### Verdict kodlari (20)

| Kod | Ma'no | | Kod | Ma'no |
| --- | ----- | - | --- | ----- |
| `PENDING` | navbatda | | `PE` | Presentation Error |
| `RUNNING` | tekshirilmoqda | | `PARTIAL` | qisman ball (IOI) |
| `AC` | Accepted | | `IE` | Internal Error |
| `WA` | Wrong Answer | | `SKIPPED` | o'tkazib yuborildi |
| `TLE` | Time Limit | | `COMPILE_TIMEOUT` | kompilyatsiya cho'zildi |
| `MLE` | Memory Limit | | `IDLENESS` | interactive kutish |
| `OLE` | Output Limit | | `SECURITY_VIOLATION` | sandbox qoidasi buzildi |
| `RE` | Runtime Error | | `CHECKER_ERROR` | checker yiqildi |
| `CE` | Compile Error | | `TESTING_ABORTED` | rejudge/bekor qilindi |
| `RATE_LIMITED` | submit limiti | | `DENIAL_OF_JUDGEMENT` | infra nosozligi |

`SECURITY_VIOLATION` **alohida alert** chiqaradi — bu potensial escape urinishi.

## DB

Schema: [05-domain-model](../05-domain-model/README.md) — entitylar, indekslar va migration tartibi shu yerda 🔒.

- Migration'lar **oldinga mos** yoziladi (add column → backfill → switch → drop, alohida deploylarda)
- Har migration `--plan` bilan review qilinadi; `RunPython` da `atomic = False` uzoq backfill uchun
- Test data va statement asset'lari DB da emas — S3/R2

## Reyting hisoblash (Celery)

| Task                        | Trigger                          | Izoh                                     |
| --------------------------- | -------------------------------- | ---------------------------------------- |
| `recalc_skills(user_id)`    | birinchi AC                      | inkremental, tez                         |
| `recalc_skills_for_problem` | `Problem.difficulty` o'zgarishi  | **batch** — [ADR-0007](../07-adr/0007-skills-uses-current-difficulty.md); `UserSolvedProblem(problem_id)` indeksi shart |
| `recalc_contest_rating`     | contest yakunlanishi             | `is_rated` + ≥10 ishtirokchi             |
| `recalc_activity`           | kunlik cron                      | 30 kunlik oyna                           |
| `update_standing`           | har judged attempt               | inkremental, materiallashtirilgan        |

Har o'zgarish `RatingHistory` ga sabab bilan yoziladi — principle #2.

## Env va secrets

`.env` **hech qachon commit qilinmaydi**. Ishlab chiqarishda secret store (Cloudflare/Vault/SOPS).

```
DJANGO_SECRET_KEY, DATABASE_URL, REDIS_URL
S3_ENDPOINT, S3_BUCKET, S3_KEY, S3_SECRET
JUDGE_QUEUE_URL, JUDGE_PROVIDER=own|judge0
TELEGRAM_BOT_TOKEN
SENTRY_DSN

EMAIL_CHAIN=brevo,mailjet,resend,mailersend
EMAIL_FROM, EMAIL_FROM_NAME
BREVO_API_KEY, BREVO_FROM
MAILJET_API_KEY, MAILJET_SECRET_KEY, MAILJET_FROM
RESEND_API_KEY, RESEND_FROM
MAILERSEND_API_KEY, MAILERSEND_FROM
```

## Email — bitta provayder emas, zanjir

Bepul planlar **kunlik** kvota qo'yadi: Brevo 300/kun, Mailjet 200/kun,
Resend 100/kun, MailerSend 500/oy (≈16/kun, ustiga 100 API so'rov/kun va
karta majburiy). Parol tiklash so'rovlari kun davomida notekis keladi,
shuning uchun `core.mailer` `EMAIL_CHAIN` bo'ylab yuradi: birinchisi
yiqilsa keyingisiga o'tadi, kaliti yo'q provayder jimgina tushib qoladi.

Har provayder **o'z subdomenidan** yuboradi: SPF `include:` 10 ta DNS
lookup bilan cheklangan va to'rttasi bitta yozuvga sig'maydi.

| Zanjirdagi o'rni | Provayder | Subdomen | Bepul kvota |
| ---------------- | --------- | -------- | ----------- |
| 1 | Brevo | `mail1.rankwant.bugvector.uz` | 300/kun |
| 2 | Mailjet | `mail2.rankwant.bugvector.uz` | 200/kun |
| 3 | Resend | `mail3.rankwant.bugvector.uz` | 100/kun |
| 4 | MailerSend | `mail4.rankwant.bugvector.uz` | 500/oy |

`rankwant.uz` hali ro'yxatdan o'tmagan, shuning uchun hozircha
`bugvector.uz` ostida. U kelganda har provayderga ikkinchi domen
qo'shiladi va `*_FROM` almashadi — kod o'zgarmaydi.

Kalit qo'shilgandan keyin birinchi qadam — haqiqiy tekshiruv:

```
python manage.py send_test_email siz@example.com --only brevo
```

Har yuborish `EmailDelivery` ga yoziladi (qaysi provayder ishlagani,
qolganlari nega tushib qolgani). Xat **tanasi saqlanmaydi** — tiklash
havolasi token, uni bazaga ko'chirmaymiz.

Ikki tuzoq, ikkalasi ham o'lchangan:

- **Resend va MailerSend API'lari Cloudflare ortida** va `urllib` ning
  standart `User-Agent` ini bot deb bloklaydi (`error_code 1010`).
  `core.mail_providers.USER_AGENT` shu sababli bor.
- **Brevo'da IP oq ro'yxati yoqilgan** — server IP'si qo'lda qo'shilishi
  kerak, aks holda Brevo jimgina rad etadi va zanjir Mailjet'ga tushadi.

Judge host'da **DB credential bo'lmaydi** — u faqat Redis va S3 ni biladi.

## Observability

- Structured JSON log; har so'rovda `request_id`
- Sentry — backend va frontend
- Metrikalar: **judge latency p50/p95** (NFR: <5s / <15s), navbat uzunligi, verdict taqsimoti, 5xx darajasi
- Alert: `SECURITY_VIOLATION`, navbat >5 min, judge worker yiqilishi

## Sifat shartlari

- `mypy` strict; biznes logika service layer'da, view'da emas
- **Majburiy test qamrovi:** judge pipeline, 4 reyting formulasi, Qvant ledger
- CI: lint + type + test + OpenAPI schema diff — har PR da

## Xavfsizlik checklist (launch oldidan)

- [ ] Judge host izolyatsiyasi tekshirildi (kiruvchi port yo'q, DB credential yo'q)
- [ ] Sandbox escape testi: fork bomb, fayl yozish, tarmoq, `/proc` o'qish
- [ ] PAT hash saqlanishi va bekor qilish oqimi
- [ ] Rate limit barcha auth endpointlarida
- [ ] **Tashqi xavfsizlik auditi** ([ADR-0004](../07-adr/0004-judge-engine.md) sharti)

## Assumptions

1. **Bepul email kvotalari yetarli.** Zanjir jami ≈ 616 xat/kun (Brevo 300 +
   Mailjet 200 + Resend 100 + MailerSend ≈16). Parol tiklash so'rovlari shu
   hajmga sig'adi degan taxmin; **real yuklamada o'lchanmagan**.
2. **Har provayder alohida subdomen oladi.** Sabab yozilgan: SPF `include:`
   10 DNS lookup bilan cheklangan va to'rttasi bitta yozuvga sig'maydi.
3. **`drf-spectacular` sxemasi shartnoma sifatida yetarli.** *"Har PR da schema
   diff tekshiriladi"* — ya'ni OpenAPI haqiqat manbai, qo'lda yozilgan API
   hujjati kerak emas.
4. **Redis bitta instans uch vazifani ko'taradi** — session, Celery broker,
   judge navbat (arxitekturadagi bir xil taxmin).

## Qulflash

**Tasdiq:** Saidakbar Narzullayev — Repo owner / maintainer, 2026-09-06.

2026-09-06: stack versiyalari, auth, API konvensiyalari, judge protokoli, Celery tasklari, env/secrets, observability va xavfsizlik checklist'i tasdiqlandi.
Bog'liq qarorlar: [ADR-0003](../07-adr/0003-stack-django-next.md) · [ADR-0004](../07-adr/0004-judge-engine.md) · [ADR-0007](../07-adr/0007-skills-uses-current-difficulty.md) · [ADR-0008](../07-adr/0008-auth-session-plus-pat.md).
O'zgartirish = yangi ADR (`docs/07-adr/`).

## Ochiq bandlar (Phase 2 — lock'ni bloklamaydi)

- [ ] O'z o'qish kontenti modeli (maqola ↔ masala)
- [ ] Obuna/to'lov integratsiyasi — narx ADR'idan keyin
- [ ] Judge nomzodi yakunlangach til obrazlari ro'yxati ([ADR-0004](../07-adr/0004-judge-engine.md) bake-off)

## Referens

- KEP endpoint ro'yxati: `kep-uz-platform-analysis.md`
- rankglass tech spec: `rankglass/docs/08-technical-spec/`
