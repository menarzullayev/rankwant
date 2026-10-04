# RankWant — Tizim arxitekturasi va dizayn hujjati

> **Arxiv yozuvi.** Repoga 2026-10-04 da ko'chirildi; matn yozilgan kunidagi holatni aks ettiradi. Diagrammadagi «judge — ALOHIDA HOST» maqsad topologiyani bildiradi: hozir judge shu mashinada alohida konteyner ([threat model](../../10-operations/threat-model.md), A-1).

**Sana:** 2026-09-20 · **Manba:** kod o'qildi va o'lchandi (taxmin emas)
**Holat:** tahlil hujjati

---

## Mundarija

1. [Umumiy ko'rinish va qatlamlar](#1-umumiy-korinish-va-qatlamlar)
2. [Modul xaritasi — API domenlari](#2-modul-xaritasi--api-domenlari)
3. [Ma'lumot oqimi: submit → verdict → reyting](#3-malumot-oqimi-submit--verdict--reyting)
4. [Judge chegarasi va pull protokoli](#4-judge-chegarasi-va-pull-protokoli)
5. [Modul mas'uliyat jadvali](#5-modul-masuliyat-jadvali)
6. [Ma'lumot almashinuvi shartnomalari](#6-malumot-almashinuvi-shartnomalari)
7. [Deploy topologiyasi](#7-deploy-topologiyasi)
8. [Kuzatilgan nomuvofiqliklar va xavflar](#8-kuzatilgan-nomuvofiqliklar-va-xavflar)

---

## 1. Umumiy ko'rinish va qatlamlar

Tizim besh qatlamdan iborat, ularning ustida esa izolyatsiya qilingan **judge host** turadi.

```
                    ┌─────────────────────────────┐
                    │  Foydalanuvchi              │  brauzer · API bot · Telegram
                    └──────────────┬──────────────┘
                                   │
        ┌──────────────────────────▼───────────────────────────┐
        │  Edge — Cloudflare                                   │
        │  Tunnel (kiruvchi port yo'q) · Worker: texnik ishlar  │
        │  CDN va kesh qoidalari · Vary boshqaruvi             │
        └───────┬──────────────────────────────────┬───────────┘
                │ HTML / RSC                       │ /api/*
        ┌───────▼────────────┐         ┌───────────▼────────────────────────┐
        │  web — Next.js SSR │────────▶│  api — Django 5.2 LTS + DRF        │
        │  React 19 · 10 til │         │  19 domen moduli · service layer   │
        └────────────────────┘         └───┬────────────────────────┬───────┘
                                     ┌─────┴──────┐                 │
                              ┌──────▼─────┐ ┌────▼──────┐          │
                              │  worker    │ │   beat    │          │
                              │  Celery    │ │ 2s/60s/1h │          │
                              └──────┬─────┘ └────┬──────┘          │
                                     │            │                 │
        ┌────────────────────────────▼────────────▼─────────────────▼───────┐
        │  Postgres 16 (metadata)  ·  Redis 7 (session+Celery+navbat)        │
        │  S3 / MinIO (test ma'lumoti — s3:// havola)                        │
        └────────────────────────────┬──────────────────────────────────────┘
                                     │ ①pull (BRPOP)   ②natija (LPUSH)
        ╔════════════════════════════▼═══════════════════════════════════════╗
        ║  judge — ALOHIDA HOST (xavfsizlik chegarasi)                       ║
        ║  kiruvchi port YO'Q · DB credential YO'Q · tashqi internet YO'Q    ║
        ║  judge-go (Go + nsjail)  ·  judge-py (Python + isolate)            ║
        ║  JudgeProvider interfeysi ortida — almashtiriladi                  ║
        ╚════════════════════════════════════════════════════════════════════╝
                                     │
        ✗ api → judge taqiqlangan (na HTTP, na DB) · ✓ judge → Redis · ✓ judge → S3
```

**Eng muhim me'moriy qaror:** foydalanuvchi kodi faqat judge hostda ishlaydi. Bu qoida
hujjatda yozilgan, balki **kod bilan majburlangan**:

- `services/judge-go/main.go` — `DATABASE_URL` mavjud bo'lsa `os.Exit(1)`:
  _"DATABASE_URL berilgan — judge host'da DB credential bo'lmasligi shart"_
- `PreflightCgroup()` o'tmasa worker umuman ishga tushmaydi — cheklovsiz judge
  foydalanuvchi kodini host'ga qo'yib yuboradi (mashina 2026-09-06 da ikki marta yiqilgan)
- `docker-compose.yml` da `judge` servisiga `DATABASE_URL` **ataylab** berilmagan

**Asosiy tamoyil:** API judge'ga hech qachon so'rov yubormaydi. Aloqa faqat navbat orqali,
va faqat judge tomonidan *tortiladi* (pull).

---

## 2. Modul xaritasi — API domenlari

Bitta Django loyihasi, **19 domen moduli** + `config` + `openapi`. Ular
`config/api_urls.py` orqali `/api/v1/` ostida birlashadi.

| Domen | Modullar | Qator (o'lchandi) |
|---|---|---|
| Identitet va kirish | `core`, `profiles` | 10 361 + 3 013 |
| Masala va kontent | `problems`, `content`, `blog`, `updates`, `roadmap` | 4 429 + 589 + 262 + 916 + 822 |
| Tekshiruv (yadro) | `judging`, `hacks` | 1 328 + 1 599 |
| Musobaqa | `contests`, `arena`, `duels`, `tournaments`, `hackathons` | 1 533 + 815 + 753 + 440 + 483 |
| O'yinlashtirish va reyting | `qvant`, `ratings` | 1 553 + 793 |
| O'qitish va jamiyat | `classroom`, `quizzes`, `notifications` | 398 + 637 + 339 |

> Qator sonlari `migrations/` va `__pycache__` hisobga olinmagan holda o'lchandi.

### Bo'linish tamoyili

Bo'linish **domen** bo'yicha, texnik qatlam bo'yicha emas. Har bir modul o'z
`models.py`, `serializers.py`, `views.py`, `urls.py` va — muhimi — `services.py` ga ega:
biznes logika view'da emas, service qatlamida (ADR-0003).

Modullar orasidagi bog'lanish **bir tomonlama** (acyclic) saqlanadi:

```
core  ←──  problems  ←──  judging  ←──  hacks
                ↑             ↑
                │             │
            contests      ratings  ←──  qvant
```

Ya'ni `judging` `problems`ga tayanadi, lekin `problems` `judging` haqida bilmaydi.

---

## 3. Ma'lumot oqimi: submit → verdict → reyting

`docs/06-architecture` o'zida _"Data flow yozma emas"_ deb ochiq qoldirgan savol shu
bo'limda yopiladi.

```
Foydalanuvchi   web        api        Redis       judge      Postgres
     │           │          │           │           │           │
     │ ①submit   │          │           │           │           │
     ├──────────▶│          │           │           │           │
     │           │ ②POST    │           │           │           │
     │           ├─────────▶│           │           │           │
     │           │          │ ③Attempt(PENDING)     │           │
     │           │          ├──────────────────────────────────▶│
     │           │          │ ④build_job → LPUSH jobs           │
     │           │          ├──────────▶│           │           │
     │           │          │           │ ⑤BRPOP (pull)         │
     │           │          │           │◀──────────┤           │
     │           │          │           │           │ ⑥nsjail:  │
     │           │          │           │           │ kompilyat │
     │           │          │           │           │ +testlar  │
     │           │          │           │ ⑦LPUSH results        │
     │           │          │           │◀──────────┤           │
     │           │          │ ⑧beat: drain_results (2s)         │
     │           │          │◀──────────┤           │           │
     │           │          │ ⑨apply_result                     │
     │           │          ├──────────────────────────────────▶│
     │           │          │ ⑩ratings.on_attempt_judged        │
     │           │          ├──────────────────────────────────▶│
     │           │          │ ⑪standings debounce 5s            │
     │           │          ├──────────────────────────────────▶│
     │           │ ⑫SSE/poll            │           │           │
     │           │◀─────────┤           │           │           │
     │ ⑬verdict  │          │           │           │           │
     │◀──────────┤          │           │           │           │
```

### Qadamlar batafsil

1. **Submit qabul qilinadi** (`web → api`) — kod hajmi `MAX_SOURCE_BYTES = 64 KB` bilan
   cheklangan; session cookie orqali autentifikatsiya.
2. **Attempt yoziladi** (`api → Postgres`) — `Attempt` yozuvi `PENDING` verdict bilan
   **avval** saqlanadi. `enqueue()` docstring'i: _"navbat yiqilsa ham submission
   yo'qolmasligi shart"_. Ayni paytda `Problem.attempt_count` oshiriladi.
3. **Job quriladi** (`judging/services.py::build_job`) — testlar (`input_ref`/`output_ref` —
   S3 havolalari, inline emas), limitlar, checker turi, IOI subtask'lari, validator.
   Til ustma-ust limiti (`ProblemLanguage`) shu yerda qo'llanadi.
4. **Navbatga qo'yiladi** (`api → Redis`) — `LPUSH rankwant:judge:jobs`. Hech qanday
   HTTP so'rov yo'q.
5. **Judge tortib oladi** (`judge → Redis`) — `BRPOP`, 2 s bloklab kutadi.
   `SIGTERM` kelganda navbatni bo'shatib chiqadi (graceful drain).
6. **Sandboxda bajariladi** — kompilyatsiya, keyin har bir test alohida sandbox'da.
   Test ma'lumoti `s3://` havoladan o'qiladi, 256 MB gacha keshda saqlanadi.
7. **Natija qaytariladi** — `LPUSH rankwant:judge:results`. Judge javobda `hack_id` va
   `hack_stage` ni **aynan** qaytaradi — o'zi bu mantiqni bilmaydi ham.
8. **Natija olinadi** (`beat → worker`) — `judging.drain_results` har **2 soniyada**,
   bir siklda 500 tagacha. Uch xil egasi bor, marshrut tartibi muhim:
   `hack_id` → `custom_run_id` → oddiy attempt.
9. **Verdict yoziladi** — `apply_result()` bitta tranzaksiyada `Attempt` ni yangilaydi va
   `AttemptTestResult` qatorlarini qayta yaratadi. Judge yuborgan verdict **katalogga
   qarshi tekshiriladi**; tanilmagan kod `IE` bo'ladi.
10. **Reyting hisoblanadi** (`ratings`) — `on_attempt_judged()`. Faqat **birinchi AC**
    `UserSolvedProblem` yozadi va Skills reytingini o'zgartiradi. Har o'zgarish
    `RatingHistory` ga sabab bilan tushadi. Avvalgi AC bekor qilinsa —
    `on_accept_revoked` (teskari yo'l).
11. **Standings yangilanadi** (`contests`) — musobaqa ichidagi urinish bo'lsa, qayta
    hisoblash **5 soniya** debounce qilinadi (`cache.add` kaliti bilan). Sabab: 500 submit/10 s
    spike'da har verdictda to'liq qayta hisoblash ma'nosiz qimmat.
12. **Foydalanuvchi ko'radi** (`api → web`) — SSE + qisqa polling. WebSocket ataylab rad
    etilgan: standings 10–30 s da yetarli.

### Qotib qolish himoyasi — `judging.reap_stuck`

Judge navbatdan ishni olib, keyin yiqilsa (deploy, OOM), ish **yo'qoladi**: navbatda ham
yo'q, natija ham kelmaydi. Urinish abadiy `PENDING` bo'lib qolardi.

- Har **60 soniyada** ishlaydi; 5 daqiqadan oshgan urinishlarni **bir marta** qayta
  navbatga qo'yadi.
- Ikkinchi marta ham qotsa — `DENIAL_OF_JUDGEMENT` (yolg'on kutishdan ko'ra halol xato).
- ⚠️ **Muhim shart:** navbat bo'sh bo'lmasa vazifa hech narsa qilmaydi. Aks holda o'lim
  spirali boshlanadi — o'lchangan: 60 kutayotgan ish qayta qo'yilib navbatni 120 ga
  chiqargan, bu yana ko'proq urinishni chegaradan o'tkazgan.

### NFR o'lchovi qayerda

`Attempt.latency_ms = judged_at - created_at` — **butun zanjir** (p50 < 5 s, p95 < 15 s).
Sababni ajratish uchun judge telemetriyasi `Attempt.judge_meta` da saqlanadi:
`queue_wait_ms`, `sandbox_setup_ms`, `total_ms`, `worker`, `sandbox`.

---

## 4. Judge chegarasi va pull protokoli

Butun integratsiya **ikki Redis ro'yxatidan** iborat.

```
   ┌──────────────────┐                        ┌──────────────────┐
   │  api + worker    │                        │  judge (Go)      │
   │  DB credential   │                        │  DB credential   │
   │  bor             │                        │  YO'Q            │
   └───┬──────────┬───┘                        └───┬──────────┬───┘
       │ ①LPUSH  │ ④BRPOP                         │ ②BRPOP   │ ③LPUSH
       │          │                                │          │
   ┌───▼──────────┴────────┐              ┌────────┴──────────▼───┐
   │ rankwant:judge:jobs   │              │                       │
   │ (ish navbati)         │              │  (natija navbati)     │
   │ rankwant:judge:results│              │                       │
   └───────────────────────┘              └───────────────────────┘

   ✗ to'g'ridan-to'g'ri aloqa yo'q — na HTTP, na DB
```

| Kalit | Yozadi | O'qiydi |
|---|---|---|
| `rankwant:judge:jobs` | api (`LPUSH`) | judge (`BRPOP`) |
| `rankwant:judge:results` | judge (`LPUSH`) | worker (`BRPOP`) |

Bu shartnoma `services/bakeoff/protocol.md` da qotirilgan va **judge-go ham, judge-py ham**
unga bo'ysunadi — shuning uchun nomzodni almashtirish arxitekturani o'zgartirmaydi.

### S3 — test ma'lumoti

- API faqat **havolani** yuboradi: `s3://bucket/key`. Test tanasi DB'da saqlanmaydi.
- Judge MinIO mijozi bilan o'qiydi; 256 MB gacha keshda ushlab turadi, chegaradan oshsa
  kesh tozalanadi (LRU emas — testlar to'plami odatda kichik).
- S3 sozlanmagan bo'lsa faqat inline testli ishlar bajariladi — qolganlari **ko'rinadigan
  xato** (`IE`) beradi, jimgina `WA` emas.

### Protokol shakli — `Job` → `Result`

`JudgeJob.to_json()` 14 maydon yuboradi: `job_id`, `attempt_id`, `language`, `source`,
`limits`, `tests`, `checker`, `subtasks`, `mode`, `custom_run_id`, `validator`,
`validate_input`, `hack_id`, `hack_stage`.

`Result` qaytaradi: `job_id`, `attempt_id`, `custom_run_id`, `hack_id`, `hack_stage`,
`verdict`, `score`, `time_ms`, `memory_kb`, `failed_test_index`, `compile_output`,
`per_test[]`, `judge_meta`.

> ⚠️ **Jim nuqson xavfi.** Yangi maydon dataclass'ga qo'shilib, `to_json()` lug'atiga
> qo'shilmasa — maydon judge'ga umuman yetib bormaydi va **hech qanday xato chiqmaydi**.
> Bu `provider.py` da izoh bilan ogohlantirilgan.

### Verdict katalogi — umumiy til (24 kod)

| To'plam | A'zolari | Ma'nosi |
|---|---|---|
| `TERMINAL` | `PENDING`/`RUNNING` dan tashqari hammasi | Yakuniy verdict |
| `ALERTING` | `SECURITY_VIOLATION` | Har hodisa alert chiqaradi — potensial sandbox escape |
| `API_ONLY` | `HACKED` | Faqat API qo'yadi. Judge natijasida kelsa ishonilmaydi — aks holda ishonchsiz navbat yozuvchisi istalgan `AC` ni bekor qila olardi. |

Legacy: `RE` — judge endi chiqarmaydi (`RE_SIGNAL`/`RE_EXIT`), lekin bazada 18 163 qator
qolgan. Har qanday statistika ikkalasini hisobga olishi kerak.

---

## 5. Modul mas'uliyat jadvali

| Modul | Vazifasi | Mas'uliyati | Asosiy modellar |
|---|---|---|---|
| `core` | Identitet, sessiya, email, sozlamalar | Kim kirgan, sessiya haqiqiymi, xat yetib bordimi, platforma ko'rinishi | User, ApiToken, UserSession, SocialAccount, EmailDelivery, School, SiteAppearance, AnalyticsEvent |
| `problems` | Masala katalogi va mualliflik | Masala matni, limitlari, testlari, checker'i, teg va qiyinlik | Problem, Topic, Language, TestCase, Subtask, Validator, ReferenceSolution, EditorialUnlock |
| `judging` | Urinish va verdict | Navbatga qo'yish, natijani yozish, qotib qolganini qutqarish | Attempt, AttemptTestResult, CustomRun, Verdict |
| `hacks` | Hack fazasi (ADR-0020) | Boshqa yechimni sindiruvchi testlar; `AC` ni bekor qilish huquqi | Hack, HackRoom, HackRoomMember, HackLock |
| `contests` | Musobaqa | Vaqt oynasi, ro'yxatdan o'tish, standings, sertifikat | Contest, ContestProblem, ContestRegistration, Standing, Certificate |
| `ratings` | Reyting va tarix | 4 reyting turini hisoblash, har o'zgarish sababini yozish | UserSolvedProblem, RatingHistory |
| `qvant` | Ichki valyuta | Hamyon, tranzaksiya, quest, do'kon, streak, marafon | QvantWallet, QvantTransaction, QvantQuest, ShopItem, UserInventory |
| `profiles` | Ommaviy profil | Ko'nikma, texnologiya, ta'lim, ish tajribasi, jamoa, follower | Skill, UserSkill, UserTechnology, Education, WorkExperience, Team, Follow |
| `classroom` | O'qituvchi uchun sinf | Sinf a'zolari va topshiriqlar | Classroom, ClassroomMember, Assignment |
| `quizzes` | Test savollari | Savol banki, quiz tuzish, urinish baholash | Question, Choice, Quiz, QuizQuestion, QuizAttempt |
| `arena` | Tezkor raund | Vaqtli raund, ishtirok, javoblar | ArenaRound, ArenaQuestion, ArenaParticipation, ArenaAnswer |
| `duels` | 1 ga 1 duel | Ikki o'yinchi, duel masalalari, duel reytingi | Duel, DuelProblem |
| `tournaments` | Turnir | Bosqichlar va turnir jadvali | Tournament, TournamentStage, TournamentStanding |
| `hackathons` | Hackathon | Vaqtli hackathon va loyiha topshirish | Hackathon, HackathonSubmission |
| `content` | O'quv kontenti | Maqola, o'quv yo'li va qadamlar | Article, ArticleProblemLink, Roadmap, RoadmapStep |
| `blog` | Blog | E'lon qilingan postlarni tarqatish | Post |
| `updates` | Platforma yangiliklari | Tarjimali yangilik, o'qilganlik belgisi | SystemUpdate, SystemUpdateTranslation, UpdateRead |
| `roadmap` | Ommaviy roadmap | Taklif, ovoz berish, izoh | RoadmapItem, RoadmapVote, RoadmapComment |
| `notifications` | Bildirishnoma | Foydalanuvchiga hodisa yetkazish | Notification |

### Reyting turlari (`RatingHistory.Type`)

`skills` · `contest` · `activity` · `challenges`

`activity` — 30 kunlik siljuvchi oyna; hech kim faol bo'lmasa ham kunlik pasayishi kerak
(`ratings.refresh_activity`, har soatda), aks holda reyting muzlab qoladi.

### Celery jadvali — vaqt bo'yicha mas'uliyat

| Vazifa | Davr | Nima uchun kerak |
|---|---|---|
| `judging.drain_results` | 2 s | Judge natijalarini navbatdan olib DB'ga yozadi. **Busiz** submit qabul qilinadi, judge ishlaydi, lekin natija navbatda qolib ketadi. |
| `judging.reap_stuck` | 60 s | Yo'qolgan ishni qutqaradi; ikkinchi urinish ham qotsa — halol xato. |
| `contests.finalize_due` | 60 s | Vaqti tugagan musobaqani yakunlaydi va reytingni qo'llaydi. |
| `hacks.close_due` | 60 s | Hack oynasi yopilgach testlarni qo'shadi va `AC` larni qayta tekshiradi. **Ishlamasa** musobaqa yakunlanmay qoladi. |
| `hacks.reap_stuck` | 300 s | Javobi kelmagan hack fazani ham, musobaqani ham ushlab turadi. |
| `arena.finalize_due` | 60 s | Arena raundini yakunlaydi. |
| `duels.finalize_due` | 60 s | Duel natijasini yakunlaydi va duel reytingini qo'llaydi. |
| `blog.announce_published` | 300 s | E'lon qilingan postni tarqatadi. |
| `ratings.refresh_activity` | 3600 s | Activity reytingining kunlik pasayishi. |

---

## 6. Ma'lumot almashinuvi shartnomalari

### A. web → api (HTTP/JSON)

- Bazaviy yo'l: `/api/v1/`
- Sxema: `drf-spectacular` → `/api/v1/schema/`, Swagger → `/api/v1/docs/`
- Auth: `httpOnly` session cookie (birinchi tomon) yoki `rw_…` PAT (SHA-256 saqlanadi)
- SSR ichki manzil: `API_BASE_INTERNAL=http://api:8000/api/v1`
- Brauzer: bir xil origin — `/api/*` tunnel orqali API'ga, qolgani web'ga

### B. api → Redis (ish navbati)

- Kalit: `rankwant:judge:jobs` · `LPUSH` / `BRPOP`
- Shakl: `JudgeJob.to_json()`

### C. judge → Redis (natija navbati)

- Kalit: `rankwant:judge:results` · `LPUSH` / `BRPOP`
- Shakl: `Result`
- `attempt_id` tushib qolsa verdict hech qachon yozilmaydi — urinish `PENDING` qoladi

### D. api → judge (S3 orqali, bilvosita)

- Shakl: `s3://bucket/key` havolasi (test tanasi emas)
- Ruxsat: judge → S3 ✅ · judge → DB ❌

### Auth kanallari (`docs/06-architecture`)

| Kanal | Mexanizm |
|---|---|
| Web (birinchi tomon) | Django session, `httpOnly` cookie, Redis backend (`cached_db`) |
| API / bot | Personal Access Token (`rw_…`, SHA-256) |
| Telegram | login widget imzosi → **session** ochiladi |

### Middleware tartibi (12 qatlam)

```
core.middleware.EdgeCacheHeaders     ← eng tashqarida: javob shakllangach Vary ni tuzatadi
corsheaders.middleware.CorsMiddleware
django.middleware.security.SecurityMiddleware
whitenoise.middleware.WhiteNoiseMiddleware
django.contrib.sessions.middleware.SessionMiddleware
django.middleware.locale.LocaleMiddleware
django.middleware.common.CommonMiddleware
django.middleware.csrf.CsrfViewMiddleware
django.contrib.auth.middleware.AuthenticationMiddleware
core.middleware.TrackSession          ← autentifikatsiyadan KEYIN: request.user kerak
django.contrib.messages.middleware.MessageMiddleware
django.middleware.clickjacking.XFrameOptionsMiddleware
```

---

## 7. Deploy topologiyasi

### Hozir — bitta mashina (ommaviy preview)

| Narsa | Qiymat |
|---|---|
| Host | bitta mashina (dual-boot Linux/Windows) |
| Tashqi kirish | Cloudflare Tunnel — ochiq port yo'q |
| Domen | `rankwant.uz` (NS — Cloudflare) |
| Sirlar | `.env.public` (gitignore'da) |
| Debug | `DJANGO_DEBUG=0` |
| Django admin | tunnel'dan chiqarilmagan; faqat `127.0.0.1:8301/admin/` |
| Staging | **yo'q** |

```bash
docker compose -p rankwant --env-file .env.public \
  -f docker-compose.yml -f docker-compose.public.yml up -d --build --wait
bash tools/check_deploy.sh    # 0 bo'lishi shart
```

### Maqsad — to'rt host

```
app (api + worker)  ·  web (Next.js)  ·  judge × N  ·  data (Postgres, Redis)
```

Xavfsizlik chegarasidan kelib chiqadi: judge hostda **kiruvchi port yo'q**.
Replika rejasi: `compose/Caddyfile.replicas` — web×2 / api×2 (Docker DNS bir nomga
bir nechta IP qaytaradi).

### Uchta nozik joy

1. **`migrate` — alohida servis, o'z obrazi bilan.** Faqat `api`/`worker`/`beat` qayta
   qurilsa, `migrate` eski obrazda qoladi va yangi migration fayllarini **ko'rmaydi** —
   _"No migrations to apply"_ deydi, baza esa eskirgan qoladi.
2. **Build argumentlari uzun shaklda.** Qisqa shakl (`build: ./apps/api`) argumentlarni
   umuman uzatmaydi — `org.rankwant.git-sha` label'i `unknown` bo'lib qoladi va eskilik
   tekshiruvi **ko'r** bo'ladi.
3. **Log cheklovi.** `json-file` cheklanmasa konteyner loglari diskni to'ldiradi
   (2026-09-20 da `docker_data.vhdx` 40 → 132 GB).

### Migratsiya rollback qilinmaydi

Sxema oldinga mos yoziladi: `add → backfill → switch → drop`, alohida deploylarda.

---

## 8. Kuzatilgan nomuvofiqliklar va xavflar

Kodni o'qib aniqlangan — taxmin qilinmagan.

| # | Nima | Nima uchun muhim | Holat |
|---|---|---|---|
| 1 | `docs/06-architecture` o'zi _"Data flow yozma emas"_ deb ochiq qoldirgan | Diagrammada strelkalar bor edi, lekin zanjir matnda yo'q edi. Shu hujjatning 3-bo'limi bo'shliqni yopadi. | yopildi |
| 2 | Staging muhiti yo'q | Prod'ga chiqishdan oldin oraliq tekshiruv yo'q. `ci-local.sh` va `.githooks/pre-push` buni qisman qoplaydi, lekin ular **manbani** sinaydi, ishlab turgan konteynerni emas. | ochiq |
| 3 | Redis bitta instans uch vazifani ko'taradi | Session + Celery broker + judge navbati. U yiqilsa uchta narsa bir vaqtda to'xtaydi. "Assumption" deb belgilangan, lekin nosozlik rejasi yozilmagan. | xavf |
| 4 | `10-operations` CI/CD tavsifi staging'ni eslatadi, lekin u yo'q | Ikki hujjat bir-biriga zid. Qaysi biri to'g'ri ekani aniqlanishi kerak. | zid |
| 5 | Judge `RUNNING` holatini yozmaydi | "Navbatda kutayotgan" va "olingan, lekin yo'qolgan" ishni ajratib bo'lmaydi. `reap_stuck` buni navbat uzunligi bilan bilvosita aniqlaydi — ishlaydi, lekin mo'rt. | ishlaydi |
| 6 | `RE` verdicti legacy — bazada 18 163 qator | Judge endi `RE_SIGNAL`/`RE_EXIT` chiqaradi. Har qanday statistika ikkalasini hisobga olishi kerak. | ma'lum |
| 7 | Repo hujjatlari o'zbekcha, qoida esa inglizchani talab qiladi | `docs/` va `README` o'zbekcha — konvensiya bo'yicha repo hujjati inglizcha bo'lishi kerak. Ko'chirish katta hajmli ish. | ochiq |

### Nima yaxshi ishlangan

1. **Navbatdan oldin DB'ga yozish** — submission hech qachon yo'qolmaydi.
2. **Judge'ning DB credential'ini kod darajasida taqiqlash** (`os.Exit(1)`) — bu qoida
   emas, majburlov.
3. **Verdict katalogini ikki tomonda tekshirish** — ishonchsiz navbat yozuvchisi ham
   `AC` ni soxta yo'l bilan bekor qila olmaydi.

---

## Manbalar

| Fayl | Nima olindi |
|---|---|
| `docker-compose.yml` | 8 servis, `x-api-build`, `x-logging`, judge'da `DATABASE_URL` yo'qligi |
| `docker-compose.public.yml` | Bir xil origin siyosati, email/OAuth/Turnstile guruhlari |
| `apps/api/config/settings.py` | `INSTALLED_APPS`, `MIDDLEWARE`, `JUDGE_*`, `SESSION_ENGINE`, `CELERY_BEAT_SCHEDULE` |
| `apps/api/config/api_urls.py` | 19 modulning `/api/v1/` ostida birlashishi |
| `apps/api/judging/*.py` | Attempt/CustomRun, `build_job`, `apply_result`, `drain_results`, `reap_stuck`, verdict katalogi |
| `services/judge-go/{main,protocol,store}.go` | BRPOP/LPUSH sikli, cgroup preflight, `Job`/`Result`, S3 kesh |
| `services/bakeoff/protocol.md` | Ikki nomzodning bir xil shartnomasi |
| `apps/api/ratings/*.py` | 4 reyting turi, `on_attempt_judged`, `on_accept_revoked` |
| `apps/web/src/proxy.ts`, `src/app/` | Kanonik manzil, locale, eksperiment cookie, 40+ marshrut |
| `docs/06-architecture/README.md` | Tasdiqlangan stack, xavfsizlik chegarasi, auth kanallari |
| `compose/Caddyfile.replicas`, `compose/four-host/` | Replika rejasi, maqsad topologiya |
| `services/maintenance-worker/wrangler.toml` | Texnik ishlar sahifasi, fail-open talabi |
