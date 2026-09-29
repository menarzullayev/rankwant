# RankWant — modul dizayni va ma'lumotlar oqimi

**Sana:** 2026-09-24
**Holat:** sanali tadqiqot yozuvi (tirik siyosat emas)
**Manba:** `apps/api`, `apps/web`, `services/judge-go`, `docker-compose*.yml`,
`docs/06-architecture` (🔒 2026-09-06), `docs/07-adr/`, `services/bakeoff/protocol.md`

> Amaldagi qoidalar `docs/06`, `docs/08` va ADR larda. Bu yozuv **koddagi hozirgi
> holat**ni tushuntiradi. Zid kelganda locked hujjat va ADR ustun; kod ularni buzsa —
> yangi ADR kerak.

Diagrammalar: [ARCHITECTURE.html](ARCHITECTURE.html) — brauzerda ochiladigan bitta fayl,
7 bo'lim, 6 SVG diagramma.

---

## 1. Bir jumla

RankWant — **modular monolit**: foydalanuvchi bitta HTTPS sayt ko'radi; ichida Next.js web,
Django/DRF API, Celery orkestr va **izolyatsiya qilingan** Go+nsjail judge ishlaydi. Yangi
deployable biznes-servis ochilmagan — 50k qarori (2026-09-19) mikroservis emas, **replica**
ni tanlagan.

## 2. Qatlamlar va ularning vazifasi

| # | Qatlam | Vazifa | Mas'uliyat chegarasi |
|---|---|---|---|
| 0 | Chekka — Cloudflare | Domen, CDN kesh, Tunnel, maintenance sahifa | Mehmon HTML keshlaydi; `/api/*` to'g'ridan API'ga. Kirgan sessiya `private, no-store` |
| 1 | Web — Next.js | SSR, i18n, UI, mehmon kesh qarori | Biznes qoida **yozmaydi**. Cookie'ni API'ga uzatadi. PAT ishlatmaydi (ADR-0008) |
| 2 | API + Celery | REST, sessiya, orkestr, admin | Barcha yozuv service layer'da. Judge'ga HTTP **yubormaydi** — faqat Redis'ga job |
| 3 | Ma'lumot | Holat saqlash | Metadata Postgres'da; test/statya S3'da; navbat/kesh Redis'da |
| 4 | Judge | Foydalanuvchi kodini bajarish | Faqat Redis + S3. `DATABASE_URL` berilsa `exit 1` |

## 3. Konteynerlar va aloqalar

Runtime: bitta mashina, `docker compose -p rankwant`, ochiq port yo'q.

| Servis | Manba | Vazifa | Aloqa qiladi |
|---|---|---|---|
| `web` | `apps/web` | SSR, i18n, proxy | api, chekka |
| `api` | `apps/api` | REST, sessiya, orkestr | postgres, redis, s3, tashqi xizmatlar |
| `worker` | `apps/api` | Celery iste'molchi: drain, standings, reyting | postgres, redis |
| `beat` | `apps/api` | Davriy jadval (2 s … 3600 s) | redis |
| `migrate` | `apps/api` | Bir martalik `manage.py migrate` | postgres |
| `judge` | `services/judge-go` | Sandbox, verdikt | **faqat** redis, s3 |
| `postgres` | `postgres:16` | Yagona haqiqat manbai | api, worker, migrate |
| `redis` | `redis:7` | Session + broker + judge navbati | api, worker, beat, judge |
| `minio` | `quay.io/minio` | Lokal S3 | api, judge |

⚠️ `api`, `worker`, `beat`, `migrate` — **bitta Dockerfile, to'rt obraz**. Faqat `api` ni
qurish workerni eski kodda qoldiradi; o'lchangan oqibat: judge yangi verdikt yubordi, eski
worker uni tanimay `IE` ga aylantirdi.

---

## 4. Asosiy modullar — vazifa, mas'uliyat doirasi, bog'liqliklar

Har Django app — **bounded context**. Umumiy naqsh (ADR-0003): HTTP faqat `views.py` da,
biznes yozuv faqat `services.py` da. Bir xil fayl nomi = bir xil javobgarlik.

### 4.1 `core` — `apps/api/core/`

| | |
|---|---|
| **Vazifa** | Foydalanuvchi, auth, sessiya, PAT, email zanjiri, qidiruv, kalendar, SLO, maktab, tashqi ko'rinish, analytics |
| **Entity** | `User`, `ApiToken`, `SocialAccount`, `UserSession`, `UsernameHistory`, `EmailDelivery`, `EmailVerifyToken`, `PasswordResetToken`, `School`, `SiteAppearance`, `AnalyticsEvent` |
| **Kirish** | `/auth/*`, `/me/`, `/users/`, `/health/`, `/slo/`, `/search/`, `/calendar/`, `/stats/`, `/appearance/`, `/analytics/events/`, `/staff/*` |
| **Chiqish** | Barcha modullar `User` ga FK. Email: `core.mailer` → Brevo/Mailjet/Resend/MailerSend |
| **Mas'uliyat** | Session + PAT (ADR-0008). `User.role` CharField **yo'q** — staff rollari Django Groups (ADR-0025). Competitor parity maydonlari olib tashlanmaydi (ADR-0024). Paritet maydonlar funksiyasidan **oldin** qo'shilgan |
| **Bog'liq** | Hech kimga bog'liq emas — eng past qatlam. Hamma unga bog'liq |
| **Qilmaydi** | Reyting formulasi, pul mantig'i, submit |

**Ichki tuzilma:** ~65 fayl — eng katta modul. Auth (`auth.py`, `oauth.py`), sessiya
(`sessions.py`, `middleware.py`), email (`mailer.py`, `email_text.py`, `mail_providers.py`),
himoya (`throttling.py`, `turnstile.py`, `permissions.py`), yordamchi (`bases.py`, `cache.py`,
`pagination.py`, `errors.py`).

⚠️ `core/cache.py` — kesh **ixtiyoriy qatlam** qoidasining kod ko'rinishi: har
`cache.get`/`set`/`delete` o'ralgan, Redis uzilsa 500 emas, log yoziladi. Django'ning o'z
`RedisCache` backendida `IGNORE_EXCEPTIONS` yo'q.

⚠️ `core/middleware.py` → `EdgeCacheHeaders` javob chizig'ining **eng tashqarisida** turadi:
`SessionMiddleware`/`CsrfViewMiddleware` `Vary: Cookie` ni view'dan **keyin** qo'shadi, CDN esa
Cookie bo'yicha vary qilingan javobni amalda hech qachon keshlamaydi.

### 4.2 `problems` — katalog

| | |
|---|---|
| **Vazifa** | Masala katalogi, til katalogi, test, checker, editorial, ovoz, shikoyat |
| **Entity** | `Problem`, `Topic`, `Language`, `TestCase`, `Subtask`, `ProblemLanguage`, `Validator`, `ReferenceSolution`, `Favourite`, `ProblemVote`, `EditorialUnlock`, `ProblemRating`, `ProblemReport`, `SimilarProblem`, `ProblemAttachment` |
| **Kirish** | `/api/v1/problems/`; `author_views.py`, `staff_views.py` |
| **Chiqish** | `judging` test havolalarini o'qiydi; `hacks` `ReferenceSolution` + `Validator` ni oladi |
| **Mas'uliyat** | Test **S3 da**, DB da faqat havola. Yashirin testsiz yangi e'lon to'siladi. Til katalogi `languages.py` (ADR-0022) |
| **Bog'liq** | `core` (muallif = User) |
| **Qilmaydi** | Verdikt yozish, reyting hisoblash |

Maxsus fayllar: `filters.py` (arxiv filtri), `recommend.py` (o'xshash masala),
`kep.py` (KEP import), `html_to_markdown.py`, `storage.py` (S3 yozuv), `media_views.py`.

⚠️ Filtr rozetkasi **diapazonni bitta filtr** deb sanaydi: `difficulty__gte` + `difficulty__lte`
bitta tanlov, uch xil yozuv. Bu 2026-09-18 da o'lchandi — bitta «Qiyin» chip'i rozetkada
`Filtrlar2` ko'rsatgan va `main` #90 dan beri qizil bo'lgan.

### 4.3 `judging` — submit va natija

| | |
|---|---|
| **Vazifa** | Submit, custom-test, judge job qurish, natijani yozish |
| **Entity** | `Attempt`, `AttemptTestResult`, `CustomRun` |
| **Kirish** | `POST /api/v1/attempts/`, `/custom-test/` |
| **Chiqish** | Redis job; `ratings.on_attempt_judged`; `contests.rebuild_standings` (5 s debounce) |
| **Mas'uliyat** | Attempt **avval DB**ga. Noma'lum verdikt = `IE`. `HACKED` judge'dan kelsa **rad**. `API_ONLY` verdiktlar judge'dan qabul qilinmaydi |
| **Bog'liq** | `problems` (test, til, checker), `core` (User) |
| **Qilmaydi** | Sandbox (bu judge-go), hack bosqichlari (`hacks`) |

**`JudgeProvider` — chegara shartnomasi** (`judging/provider.py`):

```
submit(job)        → LPUSH rankwant:judge:jobs
poll(timeout)      → BRPOP rankwant:judge:results
pending_jobs()     → LLEN  (qotib qolganni yo'qolganidan ajratish uchun)
```

API judge'ga **hech qachon so'rov yubormaydi**. Provider ikkita: `RedisJudgeProvider`
(ishlab chiqarish) va `InMemoryJudgeProvider` (testlar).

⚠️ `_verdict_of()` — katalog tekshiruvi. Ustun `choices` bilan e'lon qilingan, lekin Postgres
uni majburlamaydi: o'lchandi — judge yuborgan `"HACKED"` bazaga tushdi va u yerdan statistika,
jadval va UI ga oqib ketdi. Endi tanilmagan verdict `IE` bo'ladi, `API_ONLY` kodlari rad etiladi.

⚠️ `STANDINGS_DEBOUNCE_S = 5` — contest spike'da 500 submit/10 s bo'ladi. Har verdiktda to'liq
qayta hisoblash (barcha urinishlarni skanerlash) ma'nosiz qimmat.

### 4.4 `hacks` — hack dvigateli

| | |
|---|---|
| **Vazifa** | Bitta dvigatel, to'rt siyosat (ADR-0020): `contest_room`, `global`, `lock`, `uphack` |
| **Entity** | `Hack`, `HackRoom`, `HackRoomMember`, `HackLock` |
| **Kirish** | `/api/v1/hacks/` |
| **Chiqish** | Judge job `hack_id` + `validate_input=True`. Muvaffaqiyatli → himoyachi `HACKED`. Test qo'shilsa `TestCase.origin=hack` |
| **Mas'uliyat** | Hack holati ≠ attempt verdikti. `close_due` ishlamasa `finalize_contest` reytingni qo'llamaydi |
| **Bog'liq** | `problems` (etalon yechim, validator), `judging` (`apply_result` → `on_accept_revoked`) |
| **Qilmaydi** | Etalon yechimni **saqlash** (bu `problems.ReferenceSolution`) |

Bitta hack **uchta alohida ish** ochadi va javoblar navbatdan istalgan tartibda qaytadi:

| Bosqich | Nima qiladi | Kiritma ishonchli? |
|---|---|---|
| `generate` | Generator dasturi kiritmani yasaydi | — |
| `reference` | Kiritma validatordan o'tadi, etalon yechim javob hisoblaydi | **Yo'q** → `validate_input=True` |
| `defend` | Himoyachi kodi o'sha test bilan ishlaydi | Ha |

⚠️ Worker bu belgilarni **talqin qilmaydi** — ishdan natijaga aynan ko'chiradi. Hack mantig'i
judge ichida **yo'q**: aks holda «bitta dvigatel» qoidasi judge ichiga ham ko'chib ketardi.

⚠️ `apply_hack_result` eski bosqich javobini **tashlab yuboradi** (`result.get("hack_stage")
!= hack.stage`) — bosqichsiz javob oldingi bosqich natijasi bilan aralashib ketardi.

### 4.5 `ratings` — to'rt reyting

| | |
|---|---|
| **Vazifa** | Skills, Contest, Aktivlik, Challenges (ADR-0006) |
| **Entity** | `UserSolvedProblem`, `RatingHistory` |
| **Kirish** | Boshqa modullar chaqiradi: `on_attempt_judged`, `apply_contest_ratings`, `recalc_skills_for_problem`, `apply_duel_ratings` |
| **Chiqish** | `User.rating_*`, `RatingHistory`, `notifications` (`problem_rerated`), `qvant.on_first_accepted` |
| **Mas'uliyat** | Skills = **joriy** `Problem.difficulty` (ADR-0007). Formula `ratings/formulas.py` da **sof** — DB yo'q, testlanadi. Har delta audit qatori bilan |
| **Bog'liq** | `judging` (Attempt), `problems` (difficulty), `core` (User) |
| **Qilmaydi** | **HTTP resurs emas** — `urls.py` yo'q. Pul |

⚠️ `on_attempt_judged` da tartib **qat'iy**: `UserSolvedProblem` → `recalc_skills` → **keyin**
Qvant. Qvant `try/except` ichida — reyting yozuvi Qvant xatosidan qat'i nazar saqlanadi.

⚠️ `bump_max_rating` — bitta SQL ifoda (`Greatest(Coalesce(...))`), ya'ni parallel yozuvchilar
uni **pasaytira olmaydi**. `apply_contest_ratings` da bu partiyada bajariladi: 10 000
ishtirokchida qatorma-qator yozish 30 000 so'rov beradi va ularning hammasi bitta
tranzaksiyada 10 000 user qatorini qulflab turadi.

⚠️ `_profile_stats_changed` — invalidatsiya `transaction.on_commit` da, `robust=True`.
Tranzaksiya ichida eskirtirilsa, parallel so'rov hali commit bo'lmagan eski ma'lumotni yangi
versiya ostida keshlab qo'yardi.

### 4.6 `qvant` — yopiq loop iqtisodiyot

| | |
|---|---|
| **Vazifa** | Quest, streak, do'kon, marafon (ADR-0002) |
| **Entity** | `QvantWallet`, `QvantTransaction`, `QvantQuest`, `UserQuestCompletion`, `ShopItem`, `UserInventory` |
| **Kirish** | `/api/v1/qvant/`; `ratings` / `contests` hodisalari |
| **Chiqish** | Balans **faqat** `qvant/ledger.py` orqali. Aktivlik uchun `ratings.formulas` |
| **Mas'uliyat** | `QvantWallet.balance` — **kesh**; haqiqat — ledger. Kunlik emissiya shifti. Anti-farm: `uniq(user, quest, period_key)` |
| **Bog'liq** | `core` (User), `ratings` (aktivlik formulasi) |
| **Qilmaydi** | To'g'ridan-to'g'ri `UPDATE balance` — **hech qachon** |

**Ledger shartnomasi:**

```
credit(user, amount, reason, ref_type, ref_id, respect_cap=True) → QvantTransaction | None
debit(user, amount, reason, ref_type, ref_id)                   → QvantTransaction  (yetmasa xato)
refund_ref(user, ref_type, ref_id)                              → int  (berilganini qaytarib oladi)
take_back(user, amount, ref_type, ref_id)                       → int  (havolasiz)
verify_balance(user)                                            → (kesh, ledger yig'indisi)
```

⚠️ **Qulf hisobdan OLDIN olinadi.** Ilgari shift qulfdan oldin hisoblanardi va bir vaqtda
kelgan mukofotlar bir-birini ko'rmasdi: o'lchandi — 100 lik shiftda sakkizta parallel mukofot
**400 Qvant** bergan. Qulf ostida `remaining_today` allaqachon yozilganlarni ko'radi.

⚠️ **Balans manfiyga tushmaydi.** Qaytarish mavjud balansgacha cheklanadi — foydalanuvchi
allaqachon sarflagan bo'lsa, ortiqchasi yozilmaydi (log ogohlantiradi).

⚠️ `CAP_EXEMPT = {STREAK, ADMIN}` — streak yutuqlari va admin tuzatishi kunlik shiftdan ozod
(ADR-0002).

### 4.7 `contests` — musobaqa formati

| | |
|---|---|
| **Vazifa** | Vaqt oynali masala to'plami, ACM/IOI, virtual ishtirok, sertifikat |
| **Entity** | `Contest`, `ContestProblem`, `ContestRegistration`, `Standing`, `Certificate` |
| **Kirish** | `/api/v1/contests/` |
| **Chiqish** | `ratings.apply_contest_ratings` (≥10 ishtirokchi, `is_rated`); `qvant.on_contest_finished`; hack oynasi maydonlari |
| **Mas'uliyat** | `Standing` **materializatsiya**. `finalize_contest` — `select_for_update` + `ratings_applied_at`. Virtual ishtirok reytingga **kirmaydi** |
| **Bog'liq** | `problems`, `judging` (Attempt), `ratings`, `hacks` (oyna holati) |
| **Qilmaydi** | Judge ishini qurish |

⚠️ `finalize_contest` `hack_phase_pending` bo'lsa **return 0** — hack fazasi tugamaguncha
reyting qo'llanmaydi. Bu ikki beat vazifasi (`hacks.close_due` 60 s, `contests.finalize_due`
60 s) o'rtasidagi shartnoma.

### 4.8 Formatlar va kontent modullari

| Modul | Vazifa | Judge? | Yakunlash |
|---|---|---|---|
| `arena` | Tezkor savol raundi | Yo'q (javob tanlash) | `arena.finalize_due` |
| `duels` | 1v1, Challenges reytingi | Ha (masala submit) | `duels.finalize_due` |
| `tournaments` | Bosqichlar + umumiy standing | Contest orqali | `stage` model |
| `hackathons` | Jamoa topshirig'i | Yo'q (fayl/repo) | staff baholash |
| `quizzes` | Test / tanlov | Yo'q | `quizzes.services.submit` |
| `classroom` | Sinf, a'zo, vazifa | Yo'q | o'qituvchi |
| `content` | O'quv maqola + yo'l xaritasi | Yo'q | — |
| `blog` | Yangilik | Yo'q | `announce_published` |
| `updates` | Platforma changelog (10 til) | Yo'q | — |
| `roadmap` | Mahsulot yo'l xaritasi | Yo'q | — |
| `notifications` | In-app + Telegram | Yo'q | — |

⚠️ `content.Roadmap` va `roadmap.RoadmapItem` — **ikki xil** narsa (o'quv yo'li vs mahsulot
rejaси). Ismlari o'xshash, maqsadi boshqa.

⚠️ `notifications` **hech qachon** asosiy oqimni ushlab qolmaydi: `bulk_create` xatosi
`try/except` ichida, `log.exception` bilan (`apply_contest_ratings`).

### 4.9 `profiles` — profil kengaytmasi

| | |
|---|---|
| **Vazifa** | Ko'nikma, ish/ta'lim, tashqi OJ, follow, jamoa, yutuq, statistika |
| **Entity** | `Skill`, `UserSkill`, `Education`, `WorkExperience`, `ExternalProfile`, `Follow`, `Team`, `TeamMember`, `UserAchievement` |
| **Kirish** | `/api/v1/` profil marshrutlari; yutuq `qvant.on_first_accepted` dan |
| **Chiqish** | `profiles.refresh_external` (task); `profiles.stats.bump` — kesh invalidatsiya |
| **Mas'uliyat** | Tashqi OJ maydonlari neytral nom (ADR-0026). Yutuq yiqilsa ham AC zanjiri davom etadi |
| **Bog'liq** | `core` (User), `ratings` (Skills), `contests` (Standing) |

**`profiles/stats.py` — versiyalangan kesh.** Hisob og'ir (2 000 urinishli foydalanuvchida
bir necha agregat so'rov; masalalar xaritasi 1 200+ masalani qamraydi). Naqsh:

```
bump(user_id)                       → cache.incr("pstats:v:<id>")   (versiya oshadi)
cached(user_id, name, build)        → kalit = "pstats:<id>:<versiya>:<name>"
```

Eski yozuv **o'chirilmaydi** — shunchaki o'qilmay qoladi va TTL bilan o'zi ketadi.

⚠️ `NOT_COUNTED` — statistika to'plamidan chiqarilgan verdiktlar: `PENDING`, `RUNNING`,
`RATE_LIMITED`, `TESTING_ABORTED`, `IE`, `WRONG_TEST`, `CHECKER_ERROR`, `DENIAL_OF_JUDGEMENT`.
Bular foydalanuvchining xatosi emas — infra yoki muallif aybi.

---

## 5. Ma'lumotlar oqimi — bosqichma-bosqich

Har qadam: **kim** → **nima** → **qayerga yoziladi**.

### 5.1 Submit → verdikt

| # | Qadam | Modul | Yozuv | Izoh |
|---|---|---|---|---|
| 1 | `POST /api/v1/attempts/` | web → `judging.views` | — | Session + CSRF; `CanSubmit`; throttle 1/10 s |
| 2 | Rate limit urilsa | `AttemptViewSet.throttled` | `Attempt(RATE_LIMITED)` | Tarix uchun; portlashda bitta qator; 429 |
| 3 | Validatsiya | `AttemptCreateSerializer` | — | problem slug, til, manba ≤64 KB, contest oynasi |
| 4 | **Saqlash** | `judging.views.create` | `Attempt(PENDING)` | **Avval DB** — navbat yiqilsa ham qoladi |
| 5 | Navbat | `judging.enqueue` | `Problem.attempt_count`; Redis jobs | `build_job`: test refs (S3), checker, til limiti override |
| 6 | Ishlash | `judge-go` | — | BRPOP → compile → N test → checker. `DATABASE_URL` bo'lsa `exit 1` |
| 7 | Natija | `judge-go` | Redis results | `verdict`, `per_test`, `score`, `compile_output`, `judge_meta` |
| 8 | Drain | `judging.drain_results` | — | 2 s; `max_items=500`; marshrut: hack → custom → attempt |
| 9 | Yozish | `judging.apply_result` | `Attempt` + `AttemptTestResult` | Katalog tashqari verdikt → `IE`; `ALERTING` → `log.error` |
| 10 | Keyingi | `ratings` / `contests` | §5.2 ga qarang | AC bo'lmasa reyting to'xtaydi; contest bo'lsa standings debounce 5 s |

**NFR:** `Attempt.created_at` → `judged_at`; p50 &lt; 5 s, p95 &lt; 15 s.

**Qotib qolish:** `judging.reap_stuck` (60 s). Shart: navbat **bo'sh** va urinish 5 daqiqadan
oshgan. Bir marta qayta `enqueue`; yana qotsa `DENIAL_OF_JUDGEMENT`. Navbat bo'sh emasligini
tekshirmaslik **o'lim spiraliga** olib borardi: o'lchandi — oltmish kutayotgan ish qayta
qo'yilib navbatni 120 ga chiqargan, bu esa yana ko'proq urinishni chegaradan o'tkazardi.

**Drain marshruti — tartib qat'iy:**

```
natija
  ├─ hack_id?        → hacks.apply_hack_result      ← BIRINCHI: u attempt_id=0 yuboradi
  ├─ custom_run_id?  → judging.apply_custom_result
  └─ aks holda       → judging.apply_result
```

### 5.2 Birinchi AC → Skills → Qvant → Aktivlik

`apply_result` oxirida, verdikt `AC` bo'lganda:

| # | Qadam | Modul | Yozuv |
|---|---|---|---|
| 1 | `on_attempt_judged` | `ratings.services` | Profil kesh `on_commit` invalidatsiya |
| 2 | `UserSolvedProblem.get_or_create` | `ratings` | Uniq (user, problem). **Takroriy AC → return** |
| 3 | Hisoblagichlar | `problems` / `core` | `Problem.solved_count += 1`; public bo'lsa `User.solved_count += 1` |
| 4 | `recalc_skills` | `ratings` | Joriy difficulty'lar → `User.rating_skills` + `RatingHistory` + `max_rating_*` |
| 5 | `qvant.on_first_accepted` | `qvant` | `try/except` — **yiqilsa ham 1–4 saqlanadi** |
| 5a | `streak.touch` | `qvant.streak` | `User.streak_*`; streak quest ledger orqali |
| 5b | `quests.on_accepted` | `qvant.quests` | `UserQuestCompletion` + `ledger.credit` (kunlik cap) |
| 5c | `achievements.on_solved` | `profiles` | Yutuq; yiqilsa ham streak/quest davom etadi |
| 5d | `recalc_activity` | `qvant` → `ratings.formulas` | 30 kunlik oyna; `RatingHistory` type=activity |
| 6 | Pasayish | `ratings.refresh_activity` | Soatiga — hech kim yubormasa ham aktivlik tushadi |

**Qaytarish (rejudge AC → boshqa verdikt):**

1. Shu attempt `first_ac` bo'lmasa — chiqish (hech narsa o'zgarmaydi).
2. Boshqa AC bor bo'lsa — `first_ac` **o'sha urinishga ko'chadi**, Skills/Qvant tegilmaydi.
3. Yo'q bo'lsa — qator o'chadi; `solved_count` **floor 0** bilan kamayadi; Skills
   `RECALCULATION` sababi bilan qayta hisoblanadi; Qvant **kun sharti** bo'yicha qaytariladi
   (attempt havolasi bilan emas). **Streak tegilmaydi.**

⚠️ Nol ostiga tushmaslik shart: o'lchandi — `solved_count` musbat maydon, sanoq qatorlardan
past bo'lib qolgan holatda `update` CHECK xatosi berib **butun tranzaksiyani** yiqitardi.
Bekor qilish yolg'iz ishlamaydi: uni hack dvigateli ham chaqiradi — begona sabab hackni
abadiy `TESTING` da qoldirardi.

### 5.3 Musobaqa: live → hack → reyting

| # | Qadam | Modul | Yozuv |
|---|---|---|---|
| 1 | Ro'yxatdan o'tish | `contests` | `ContestRegistration` |
| 2 | Submit | `judging` | `Attempt.contest_id` |
| 3 | Verdikt | `apply_result` | `_schedule_standings_rebuild` — Redis kalit 5 s |
| 4 | `rebuild_standings` | `contests.services` | ACM: yechilgan + 20 daq jarima. IOI: ball + hack_score. `Standing` upsert + kesh delete |
| 5 | Hack (ixtiyoriy) | `hacks.submit` | `Hack(TESTING)` + judge job `validate_input=True` |
| 6 | Hack natijasi | `hacks.apply_hack_result` | SUCCESSFUL / UNSUCCESSFUL / INVALID_… Himoyachi `HACKED` → `on_accept_revoked` |
| 7 | `hacks.close_due` | beat 60 s | Oyna yopiladi; yangi test qo'shiladi; AC qayta navbatga |
| 8 | `finalize_contest` | beat 60 s | `select_for_update`. `hack_phase_pending` → return 0. `ratings_applied_at` qo'yiladi |
| 9 | `apply_contest_ratings` | `ratings` | `is_rated` va ≥10 ishtirokchi. Virtual yo'q. Elo + `RatingHistory` |
| 10 | Quest | `qvant.on_contest_finished` | +30, contest boshiga (anti-farm) |

Mijoz standings'ni ~10 s da qayta so'raydi. To'liq SSE **yo'q** — `docs/06` dagi
«SSE + polling» qisman bajarilgan.

### 5.4 Kirish va sessiya

| Kanal | Mexanizm | Kod |
|---|---|---|
| Web (1-tomon) | Django session → Redis; `httpOnly`, `Secure`, `SameSite=Lax`, 30 kun | `core.sessions`, `core.account_views` |
| API / bot | PAT `rw_<32B>`, SHA-256 saqlanadi, scope `read`/`submit`/`contest:manage`, ≤1 yil, ≤10 faol | `core.models.ApiToken` |
| Google / GitHub / Telegram | OIDC Authorization Code → session | `SocialStartView` / `SocialCallbackView` |

⚠️ Telegram HMAC login vidjeti **olib tashlangan** — u ham OIDC. `auth/social/<provider>/link-start/`
yo'li olib tashlangan: u faqat vidjet uchun kerak edi, chunki callback `state`siz GET bo'lgani
uchun niyat alohida POST bilan belgilanardi.

⚠️ `UserSession.last_seen` har so'rovda yozilmaydi — `TOUCH_EVERY = 300` s. «Onlayn» oynasi
600 s, ya'ni ikki barobar zaxira sahifani o'qib o'tirgan odamni o'chib-yonishdan saqlaydi.

### 5.5 Mehmon o'qish (CDN)

50k qarorining maqsadi — origin'ni HTML bilan to'ldirmaslik.

| # | Qadam | Qayerda |
|---|---|---|
| 1 | `GET /` yoki `/problems` — sessiya/`rw_locale`/`?lang=`/RSC belgisi yo'q | Cloudflare Cache Rule |
| 2 | `proxy.ts` canonical 301; `?lang=` → sarlavha + cookie, `next()` dan **oldin** | web |
| 3 | Origin `Cache-Control: public, s-maxage=30, stale-while-revalidate=86400` | `home-cache.ts` |
| 4 | SSR katalogni `API_BASE_INTERNAL` dan oladi | web → api |
| 5 | Lug'at `/i18n/<til>.js?v=<hash>`, `immutable` | alohida kesh |
| 6 | Kirgan foydalanuvchi | `private, no-store` — CDN umuman ishlamaydi |

⚠️ Tartib muhim: `?lang=` sarlavhasi `NextResponse.next()` dan **oldin** yozilishi shart —
`next()` o'sha paytda `request.headers` ni ko'chirib `x-middleware-request-*` qatorlarini yozadi
(o'lchandi: `next@16.3.4`). Keyin qo'shilgan qiymat **joriy render'ga yetib bormaydi**.

⚠️ Til ustunligi: **havola → cookie → `Accept-Language` → `uz`**. Havoladan kelgan til
cookie'ga ham yoziladi — shuning uchun ichki havolalarni o'zgartirish **shart emas**.

### 5.6 Hak job marshрути

`drain_results` tartibi **qat'iy** — `hack_id` birinchi, chunki hack job `attempt_id=0`
yuboradi va `apply_result` uni «topilmadi» deb jimgina tashlab yuborardi: hack abadiy
«tekshirilmoqda» bo'lib qolardi.

---

## 6. Judge shartnomasi

| Kalit | Yo'nalish | Kod |
|---|---|---|
| `rankwant:judge:jobs` | API `LPUSH` → judge `BRPOP` | `settings.JUDGE_JOBS_KEY` |
| `rankwant:judge:results` | judge `LPUSH` → worker `BRPOP` | `settings.JUDGE_RESULTS_KEY` |

To'liq shartnoma: [`services/bakeoff/protocol.md`](../../../services/bakeoff/protocol.md).

### 6.1 Ikki shakl — butun chegara shu ikkovidan iborat

**`JudgeJob`** (`judging/provider.py`) — API → judge:

| Maydon | Ma'nosi |
|---|---|
| `job_id`, `attempt_id` | Bog'lovchi identifikator; `job_id` natijada aynan qaytadi |
| `hack_id`, `hack_stage` | Hack marshruti: judge **talqin qilmaydi**, aynan qaytaradi |
| `language` | argv ro'yxati: `compile`, `run`, `source_file`, `proc_self`, `open_files` |
| `limits` | `compile_time_ms`, `time_ms`, `memory_kb`, `output_kb`, `processes` |
| `tests[]` | `input_ref` / `output_ref` — **S3 havolasi**, matn emas |
| `checker` | `standard` / `special` / `scorer` / `interactive` |
| `subtasks[]` | IOI ballash: `{id, points, scoring}` |
| `mode` | `acm` (birinchi xatoda to'xtaydi) · `ioi` · `custom` |
| `validator`, `validate_input` | Kirish validator bosqichi (ADR-0020) |

⚠️ `to_json()` — **jim nuqson manbai**. Dataclass'ga yangi maydon qo'shib, `to_json()`
lug'atiga qo'shmaslik hech qanday xato bermaydi: maydon judge'ga umuman yetib bormaydi.

**`Result`** — judge → API: `verdict`, `score`, `time_ms`, `memory_kb`,
`failed_test_index`, `compile_output` (64 KB gacha), `per_test[]`, `judge_meta`
(`worker`, `sandbox`, `queue_wait_ms`, `sandbox_setup_ms`, `total_ms`).

### 6.2 Vaqt o'lchash — adolat masalasi

| O'lchov | Ma'nosi | Nega |
|---|---|---|
| `time_ms` | **CPU vaqti** (user + sys) | Judge host yuklangan bo'lsa wall clock adolatsiz TLE beradi |
| `IDLENESS` | CPU kam, wall clock oshgan | Interactive masalada deadlock |
| `memory_kb` | **peak RSS** | — |

⚠️ Bu uchtasining aniqligi — bake-off'ning asosiy o'lchovi: noto'g'ri o'lchash →
adolatsiz verdikt → **reyting ishonchsiz**.

### 6.3 Judge himoyasi

| Qoida | Kod |
|---|---|
| Kiruvchi port yo'q — PULL | `main.go`: `BRPOP` |
| DB credential yo'q | `DATABASE_URL` bo'lsa `log.Error` + `os.Exit(1)` |
| cgroup limitlari majburiy | `PreflightCgroup()` — o'tmasa worker ishga tushmaydi |
| Tashqi internet yo'q | faqat Redis + S3 mijozi (`store.go`) |
| Test S3 da | `s3://bucket/key`; 256 MB LRU kesh (bir xil testlar qayta so'raladi) |

⚠️ cgroup preflight — **real hodisa**: 2026-09-06 da cheklovsiz judge mashinani ikki marta
yiqitgan. Shu sababli bu tekshiruv ishga tushish shartiga aylantirilgan.

---

## 7. Bog'liqlik xaritasi

```
core.User
  ↑
problems ──► judging ──► ratings ──► qvant
                 │            │
                 ▼            ▼
              contests    notifications
                 │
                 ▼
               hacks ──► judging (hack job)

profiles ◄── qvant (yutuq)
content / classroom / quizzes    (katalogni o'qiydi, judge yo'q)
arena / duels / tournaments / hackathons   (formatlar)
```

Yo'nalish **bir tomonlama**: quyi qatlam yuqorini chaqirmaydi. `ratings` `judging`ni
chaqiradi, `judging` `ratings`ni emas — istisno faqat `apply_result` oxiridagi hodisa chaqiruvi,
u ham `import` ichkarida (aylanma bog'liqlikdan qochish uchun).

---

## 8. Xato va tiklanish

| Holat | Nima bo'ladi |
|---|---|
| Redis jobs yiqildi, Attempt yozilgan | `reap_stuck` qayta navbatga qo'yadi |
| Judge OOM / deploy | Ish yo'qoladi → `reap_stuck` → `DENIAL_OF_JUDGEMENT` |
| Noma'lum verdikt | `IE` + `log.error` |
| `SECURITY_VIOLATION` | `ALERTING` — har bitta hodisa alert chiqaradi |
| Qvant istisnosi | Attempt va Skills saqlanadi; log yoziladi |
| Ikki `finalize_contest` | `select_for_update` + `ratings_applied_at` |
| Standings spike | 5 s debounce — har verdiktda to'liq skaner emas |
| Email provayder kvotasi | Zanjir keyingisiga o'tadi; `warn_email_quota` |
| Kesh (Redis) yiqildi | Sahifa **sekinlashadi, o'chmaydi** (`core/cache.py`) |

---

## 9. O'zgarmas qoidalar (kodda majburiy)

Bu qoidalar izoh emas, **tekshiruv**: `tools/check_decisions.py` har PR'da qatorlarni
kodda ko'radi. Sabab — 2026-09-17 da «faqat lokal zaxira» qarori qabul qilingan kuniyoq
boshqa agent R2 ga shifrsiz offsite qo'shdi va foydalanuvchi ma'lumoti bor dump'lar
tashqariga chiqdi. **Jadvalni hech kim tekshirmasa, u to'xtatmaydi.**

| # | Qoida | Kodda |
|---|---|---|
| 1 | Judge izolyatsiyasi (06 🔒, ADR-0004) | `judge-go/main.go`, `sandbox.go` |
| 2 | Qvant ledger — balans to'g'ridan-to'g'ri yozilmaydi (ADR-0002) | `qvant/ledger.py` |
| 3 | Reyting auditi — har delta sabab bilan (principle #2) | `ratings/models.RatingHistory` |
| 4 | Attempt avval DB, keyin navbat | `judging/views.py`, `judging/services.py` |
| 5 | Soft-delete — foydalanuvchi kontenti o'chirilmaydi | `Attempt`, `QvantTransaction` |
| 6 | Chegara faqat loopback | `compose` zanjiri, `tools/check_security_boundary.py` |
| 7 | `migrate` ham quriladi — aks holda sxema orqada qoladi | `tools/deploy.sh` → `SERVICES` |

---

## 10. Hujjat va kod o'rtasidagi masofa

`docs/06-architecture` **2026-09-06** da qulflangan. O'shandan beri kodda paydo bo'lgan
narsalar (06 da yo'q yoki boshqacha):

- 20 Django app (06 da «19» edi — `judging` ajralib chiqqanidan keyin sanog o'zgargan);
- 10 tilli interfeys (06 da uz/ru/en);
- OIDC (06 da Telegram HMAC vidjeti);
- mehmon CDN keshi va `?lang=` mantiqi (06 da yo'q);
- Go+nsjail g'olibi (06 da bake-off ochiq edi);
- avtomatik deploy watcher (06 da qo'lda);
- 06 dagi ochiq bandlar: «Data flow yozma emas», «Reliability/scalability yo'q»,
  «Key trade-offs yozma emas» — bu yozuv birinchi va ikkinchisiga qisman javob beradi.

**O'zgartirish tartibi:** yangi ADR → keyin `docs/06` yangilash. Mavjud locked matn
bu yozuv bilan almashtirilmaydi.

---

## 11. Bog'liq yozuvlar

| Yozuv | Mavzu |
|---|---|
| [2026-09-20 as-built architecture](../2026-09-20-as-built-architecture/README.md) | Shu mavzuning oldingi to'liq tahlili (README · MODULES · FLOWS · DIAGRAMS) |
| [2026-09-20 architecture diagrams](../2026-09-20-architecture-diagrams/README.md) | Beshta mustaqil `.svg` asset |
| [2026-09-21 security boundary](../2026-09-21-security-boundary/README.md) | O'lchangan port to'plami, qabul qilingan risklar |
| [2026-09-19 scale-50k](../2026-09-19-scale-50k/) | Masshtab qarori: replica, CDN, SLO |
| [2026-09-21 judge latency](../2026-09-21-judge-latency/) | p50/p95 darvozasi va qayd zanjiri |
| `docs/06-architecture` 🔒 | Maqsad arxitektura va xavfsizlik chegarasi |
| `docs/07-adr/` | Har qaror alohida ADR |
| `services/bakeoff/protocol.md` | Judge shartnomasining to'liq matni |
