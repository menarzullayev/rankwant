# RankWant — Project Alpha framework bo'yicha bosqichma-bosqich ko'rik

Sana: 2026-09-13 · Framework: `menarzullayev/project-alpha` @ `v1.0.0-production` (`1e8fa70c`)
Tekshirilayotgan repo: `rankwant/` (`.git` bor, `main`, HEAD `ee1e0a4`, remote `menarzullayev/rankwant`)

⚠️ `rankwant-handoff/` — `.git` siz nusxa, `feat/dual-boot-handoff` branch, eskiroq.
Unga tegilmadi; audit faqat `rankwant/` da.

## Usul

Har bosqich uchun framework uchta fayl beradi:

| Fayl | Vazifasi |
|---|---|
| `STAGE.md` | Preconditions, Inputs, Agent task, Outputs, Human approval, Handoff |
| `QUALITY-GATE.md` | PASS / BLOCK sharti |
| `TEMPLATE.md` | Artefaktning majburiy bo'limlari |

Baholash: RankWant'dagi tegishli hujjat `TEMPLATE.md` bo'limlarini qamraydimi va
`QUALITY-GATE.md` shartini bajaradimi. Har bir da'vo faylga ishora qiladi.

**Muhim chegara:** RankWant — allaqachon ishlab turgan mahsulot (`rankwant.uz`,
1226 masala, 384530 urinish). Bu yangi hujjat yozish emas — **mavjudini framework
shartnomasiga solishtirish**. Bo'shliq topilsa, u "hujjat yozilmagan" degani,
"mahsulot ishlamaydi" degani emas.

## Qadam 1 — Inventar

| Bosqich | Fayl | Hajm | Izoh |
|---|---|---|---|
| `idea-selection` | **0** | — | ⚠️ **YO'Q** — framework Stage 01 dan **oldin** talab qiladi |
| 01-vision | 1 | 5.5 KB | yupqa, lekin mazmunli |
| 02-problem-discovery | 1 | 3.4 KB | yupqa |
| 03-market-research | 5 | 32 KB | boy |
| 04-prd | 1 | 11 KB | — |
| 05-domain-model | 1 | 14 KB | — |
| 06-architecture | 1 | 5.4 KB | eng yupqa |
| 07-adr | **20** | **132 KB** | eng kuchli qism |
| 08-technical-spec | 1 | 11 KB | — |
| 09-development-plan | 1 | 11 KB | — |
| 10-operations | 3 | 52 KB | boy |

Qo'shimcha (framework'da yo'q): `brand/` (11 fayl), `tasks/`.

## Qadam 2 — Stage 01: Vision

Manba: `rankwant/docs/01-vision/README.md` (5555 bayt, STATUS: locked 2026-09-06)

### Template bo'limlari qamrovi

| Kerakli bo'lim | RankWant'da | Holat |
|---|---|---|
| Mission | `## Mission` | ✅ aniq |
| Vision | `## Vision` | ✅ aniq |
| Long-term goals | `## Long-term goals` — 5 ta raqamlangan | ✅ |
| Product principles | `## Product principles` — 6 ta | ✅ |
| **Strategic assumptions** | **yo'q** (alohida bo'lim sifatida) | ⚠️ |
| **Evidence** | **yo'q** (tarqoq havolalar bor) | ⚠️ |
| **Open questions** | **yo'q** | ⚠️ |
| Decisions / approvals | `## Qulflash` — sana bilan | ✅ (approver nomisiz) |

RankWant'da framework talab qilmaydigan qo'shimcha bo'limlar ham bor va ular
foydali: `Kim uchun` (5 segment jadvali), `Nima qiladi`, `Tagline` (3 til),
`Brend qisqacha`, `Muvaffaqiyat metrikalari`.

### Uch nuqson, dalil bilan

1. **Strategic assumptions alohida yozilmagan.** Matnda taxminlar bor
   ("Birinchi to'lqin: O'zbekiston", "kontent va mirror — mahalliy kuch") lekin
   ular taxmin sifatida belgilanmagan va tekshirilmagan. Gate buni majburiy
   deb talab qiladi.
2. **Open questions yo'q.** Hujjat `Keyingi bosqich` bilan tugaydi, ochiq
   savollar ro'yxatisiz. Gate: *"open questions are explicit"*.
3. **Approval yozuvida approver yo'q.** `## Qulflash`: *"2026-09-06: RankWant +
   Qvant tasdiqlandi"* — sana bor, **kim** tasdiqlagani yo'q. Bu Project Alpha'ning
   `docs/APPROVAL.md` shaklidan farq qiladi (approver, role, date, commit).

### Gate bahosi

`QUALITY-GATE.md` BLOCK sharti — *"product direction is materially ambiguous or
required approval is pending"* — **bajarilmagan**: yo'nalish aniq, tasdiq bor
(2026-09-06). Ya'ni BLOCK emas.

Lekin PASS shartining uch bandi bajarilmagan (strategic assumptions, open
questions, material claims evidenced). Bundan tashqari gate *"no critical
contradiction exists with Idea Selection"* ni talab qiladi — **`idea-selection`
hujjati yo'q**, shuning uchun bu shartni umuman baholab bo'lmaydi.

**Natija: WARN.** Mazmun kuchli, shakl to'liq emas.

### Tuzatish uchun minimal ish

1. `## Strategic assumptions` bo'limi — taxminlar ro'yxati + har biriga tekshirish usuli
2. `## Open questions` bo'limi
3. `## Qulflash` ga approver ismi va rolini qo'shish
4. `idea-selection` hujjatini yozish — RankWant framework'dan oldin boshlangan,
   shuning uchun bu **retroaktiv** hujjat bo'ladi va shunday belgilanishi kerak

## Qadam 3 — Stage 02: Problem Discovery

Manba: `rankwant/docs/02-problem-discovery/README.md` (3407 bayt, STATUS: locked 2026-09-06)

### Template bo'limlari qamrovi

| Kerakli bo'lim | RankWant'da | Holat |
|---|---|---|
| Target users | `## Target users` — 5 segment | ✅ (lekin asosiysi belgilanmagan) |
| Problems / pain points | `## Pain points (hozirgi bozor)` — 5 ta | ✅ |
| Jobs to be done / use cases | `## Use cases (asosiy)` — 6 ta | ✅ |
| **Current alternatives** | `Pain points` ichida aralash | ⚠️ alohida emas |
| **Problem severity** | **yo'q** | ⚠️ |
| Success metrics | `## North Star` + `## Input metrikalar (voronka)` | ✅ **kuchli** |
| **Evidence** | **yo'q** | ⚠️ |
| **Assumptions** | **yo'q** (taxminlar matn ichida) | ⚠️ |
| **Open questions** | **yo'q** | ⚠️ |
| Decisions / approvals | `## Qulflash` — sana bilan | ✅ (approver nomisiz) |

### Kuchli tomonlari — shablon talab qilganidan ortiq

- **North Star yaxshi ishlangan**: faqat nom emas, *nega aynan shu* ekani
  asoslangan (spam submitni hisoblamaydi, MVP birinchi kunidan o'lchanadi,
  ADR-0006 bilan bir xil hodisadan oziqlanadi) va **hisoblash formulasi**
  berilgan: `COUNT(DISTINCT user_id)`, `verdict = AC`, oxirgi 7 kun.
- **Voronka metrikalari** maqsadlari bilan (`< 7 kun median`, `> 30%`, `> 60%`,
  `pilot 5+ maktab`) — shablon buni umuman talab qilmaydi.
- **Non-goals** bo'limi bor — chegara aniq qo'yilgan (KEP nusxasi emas,
  crypto sovrin ADR talab qiladi, cp.uz audit — alohida scope).
- Raqobatchilar **nom bilan** va aniq da'volar bilan sanalgan
  (RoboContest — Inertia, KEP.uz — ~9k, Aurora white-label).

### To'rt nuqson, dalil bilan

1. **`Problem severity` umuman yo'q.** Gate: *"severity ... explicit"*. Har bir
   og'riqning kuchi (qanchalik tez-tez, qanchalik qimmatga tushadi, odam
   to'lashga tayyormi) hech qayerda yozilmagan — 5 ta og'riq teng vazn bilan
   sanalgan.
2. **`Evidence` va `Assumptions` ajratilmagan.** Gate aynan shuni talab qiladi.
   Hujjatda tekshirilishi mumkin bo'lgan da'volar bor (*"RoboContest API yopiq
   (Inertia)"*, *"KEP.uz ochiq REST, lekin kichikroq jamoa (~9k)"*) — **manba va
   sana yo'q**. Va taxminlar bor (*"Motivatsiya — faqat reyting yetmaydi"*) —
   taxmin sifatida belgilanmagan.
3. **`Open questions` yo'q.** Hujjat `Keyingi qadam` bilan tugaydi.
4. **Asosiy segment belgilanmagan.** 5 ta segment teng sanalgan, "primary"
   deb hech biri tanlanmagan. Gate *"primary users ... explicit"* deydi.
   Vision'dagi "Birinchi to'lqin: O'zbekiston CP/olimpiada iqtidorlari" ni
   hisobga olsak, niyat bor — lekin bu **02 hujjatida** yozilmagan.

Bundan tashqari `Qulflash` da **approver ismi yo'q** — 01-bosqichdagi kabi.

### Vision bilan ziddiyat bormi?

Yo'q. Ikkala hujjatdagi 5 segment **aynan bir xil**, va "Birinchi to'lqin:
O'zbekiston" Vision'dan olingan. Gate'ning BLOCK sharti
(*"materially contradicts Vision"*) bajarilmagan.

### Gate bahosi

**WARN.** Mazmun kuchli — North Star, voronka metrikalari va non-goals
shablon talab qilganidan **yuqori**. Lekin PASS shartining to'rt bandi
bajarilmagan: severity yo'q, evidence/assumptions ajratilmagan, open questions
yo'q, asosiy segment belgilanmagan. BLOCK emas — asosiy muammo va foydalanuvchi
aniq, Vision bilan ziddiyat yo'q.

### Tuzatish uchun minimal ish

1. `## Problem severity` — har bir og'riqqa kuch bahosi (chastota / xarajat / to'lov tayyorligi)
2. `## Evidence` va `## Assumptions` — ikki alohida bo'lim; da'volarga manba va sana
3. `## Open questions` bo'limi
4. Asosiy segmentni aniq belgilash (Vision'dagi "Birinchi to'lqin" ni shu yerga ko'chirish)
5. `## Qulflash` ga approver ismi va roli

## Qadam 4 — Stage 03: Market Research

Manba: `rankwant/docs/03-market-research/` — 5 fayl, 32 KB
(`README.md`, `competitor-summary.md`, `positioning.md`, `verdicts.md`,
`brand-discovery.md`), STATUS: locked 2026-09-06

### Template bo'limlari qamrovi

| Kerakli bo'lim | RankWant'da | Holat |
|---|---|---|
| Market definition | `README.md` → `## Bozor hajmi` (TAM/SAM/SOM) | ✅ **kuchli** |
| Competitors | `competitor-summary.md` — 5 platforma × 11 jihat | ✅ |
| **Substitutes** | alohida emas | ⚠️ |
| SWOT | `positioning.md` → `## SWOT` | ✅ |
| Positioning | `positioning.md` — one-liner, differensial, xarita | ✅ |
| **Pricing** | `## Narx (hozircha)` — faqat benchmark | ⚠️ |
| **Demand signals** | bo'lim yo'q, lekin 197k dan chiqarilgan | ⚠️ |
| **Regulatory / market risks** | SWOT `Threats` — 3 ta band | ⚠️ |
| **Evidence register** | `verdicts.md` da `## Manbalar` bor; qolganida yo'q | ⚠️ |
| **Assumptions** | bo'lim yo'q, lekin bozor hajmida ochiq yozilgan | ⚠️ |
| **Open questions** | **yo'q** | ⚠️ |
| Decisions / approvals | `## Qulflash` — sana bilan | ✅ (approver nomisiz) |

### Kuchli tomonlari

- **Bozor hajmi namunali yozilgan.** Hujjat o'zi ogohlantiradi: *"⚠️ Bu
  kuzatilgan raqobatchi raqamlaridan chiqarilgan taxmin, rasmiy statistika emas.
  Taxmin qilingan koeffitsientlar ochiq yozilgan — noto'g'ri chiqsa, qayta
  hisoblash oson."* Gate aynan *"uncertainty is explicit"* ni talab qiladi —
  bu bajarilgan.
- **TAM/SAM/SOM asoslangan**, "nima uchun RoboContest ulushini olish emas"
  savoliga ham javob berilgan (network effekti).
- **North Star ga o'tkazish jadvali** — ro'yxatdan o'tgan → haftalik faol
  (5–10% koeffitsient bilan, 3 yilga).
- **`verdicts.md` da `## Manbalar`** bor — Codeforces API hujjati, blog
  yozuvlari, AtCoder glossary, havolalar bilan. Ya'ni dalil ko'rsatish
  amaliyoti loyihada **bor**.
- **"Nusxalamaymiz"** ro'yxati — anti-patternlar aniq.

### Asosiy topilma — dalillar repo'dan tashqarida

`README.md` o'zi yozadi:

> To'liq tahlillar (workspace root — **repo tarkibida emas**):
> `kep-uz-platform-analysis.md` · `robocontest-uz-platform-analysis.md`

Tekshirdim: bu ikki fayl `rankwant/` da ham, uning atrofidagi papkalarda ham
**yo'q**. Ya'ni butun bozor hajmi asoslanadigan raqamlar — RoboContest `~197k`,
KEP `~9k`, `102 REST endpoint`, `1477 masala` — **repo ichidan tekshirib
bo'lmaydi**. Bu Project Alpha'ning asosiy prinsipiga zid: repo o'zi
yetarli bo'lishi kerak.

### Boshqa nuqsonlar, dalil bilan

1. **`Substitutes` tadqiq qilinmagan.** Global platformalar (`Codeforces`,
   `AtCoder`, `LeetCode`, `DMOJ`) `verdicts.md` da uchraydi — lekin **verdict
   kodlari** uchun, bozor o'rinbosari sifatida emas. O'zbek o'quvchisi uchun eng
   katta o'rinbosar — Codeforces (bepul, global reyting). Offline repetitor,
   maktab to'garagi, YouTube kurslari ham tahlil qilinmagan.
2. **`Pricing` tadqiq qilinmagan.** `## Narx (hozircha)`: *"RoboContest 4 tier —
   benchmark. RankWant narxlari PRD/ADR dan keyin."* Gate *"pricing ... researched"*
   deydi — bu qoldirilgan.
3. **Regulyatsiya to'liq emas — va bu jiddiy.** SWOT `Threats` da faqat
   *"Coin/regulyatsiya (real pul sovrin)"*. Lekin mahsulot **maktab
   o'quvchilariga** qaratilgan (02-bosqichdagi 1-segment) — ya'ni **voyaga
   yetmaganlar shaxsiy ma'lumotlari** masalasi bor. Butun `docs/` bo'ylab
   `GDPR`, "shaxsiy ma'lumot", "voyaga yetmagan" bo'yicha **birorta yozuv yo'q**.
4. **`Open questions` yo'q**, `Qulflash` da **approver ismi yo'q** (01 va 02 kabi).

### Gate bahosi

**WARN.** BLOCK emas: positioning **tasdiqlangan** (locked), va noaniqlik
ochiq e'lon qilingan (*"taxmin, rasmiy statistika emas"*) — gate'ning PASS
sharti *"uncertainty is explicit"* bajarilgan.

Lekin eng jiddiy topilma — **asosiy dalillar repo'dan tashqarida** — shu
bosqichning butun raqamli asosini tekshirib bo'lmaydigan qiladi. Bu kod yoki
mahsulot nuqsoni emas; **hujjat butunligi** nuqsoni.

### Tuzatish uchun minimal ish

1. Ikki tahlil faylini (`kep-uz-platform-analysis.md`,
   `robocontest-uz-platform-analysis.md`) repo'ga ko'chirish — yoki raqamlarni
   manba va sana bilan `README.md` ga ko'chirish
2. `## Substitutes` bo'limi — Codeforces/AtCoder (global), offline repetitor,
   maktab to'garagi
3. `## Regulatory / market risks` — voyaga yetmaganlar ma'lumotlari, real pul
   sovrin regulyatsiyasi
4. `## Open questions` bo'limi; `Qulflash` ga approver ismi
5. `## Narx` — hech bo'lmasa yo'nalish (obuna darajalari gipotezasi)

## Qadam 5 — Stage 04: PRD

Manba: `rankwant/docs/04-prd/README.md` (10955 bayt, STATUS: locked 2026-09-06)

### Template bo'limlari qamrovi

| Kerakli bo'lim | RankWant'da | Holat |
|---|---|---|
| Product scope | `## Fazalar` (P0–P3) + `## Out of scope (v1)` | ✅ |
| **Target users** | alohida bo'lim yo'q (user story'larda rollar) | ⚠️ |
| Features | `## Fazalar` — ID bilan (P0-1 … P2-6) | ✅ |
| User stories | `## User stories — Phase 0` — 5 ta | ✅ (faqat P0) |
| Functional requirements | P0 da `Acceptance` ustuni; P1–P3 da yo'q | ⚠️ |
| Non-functional requirements | `## Non-functional requirements` — 8 ta maqsad | ✅ **kuchli** |
| Priorities | fazalar = ustuvorlik | ✅ |
| **Constraints** | alohida bo'lim yo'q | ⚠️ |
| **Acceptance criteria** | faqat P0, va testlanadigan shaklda emas | ⚠️ **eng zaif** |
| **Requirement traceability** | ADR ga havola bor, **muammolarga yo'q** | ⚠️ |
| **Evidence / assumptions** | bo'lim yo'q | ⚠️ |
| Open questions | `## Ochiq nuqta` — 1 ta (narx) | ✅ qisman |
| Decisions / approvals | `## Qulflash` + "Lock'dan keyingi tuzatishlar" | ✅ (approver nomisiz) |

### Kuchli tomonlari — shablon talab qilganidan ancha ortiq

- **4 reyting formulasi to'liq yozilgan**: Skills (eksponensial susayish),
  Contests (Codeforces uslubi, 6 qadam), Activity (30 kunlik oyna), Challenges
  (Elo). Har birida **parametrlar, xossalar va ishlangan misol** bor:
  `500 × 800` (grind) → **16 000** · `20 × 2500` (chuqur) → **32 076**.
  Monotonlik xossasi *"200k tasodifiy holatda tekshirilgan"* deb yozilgan.
- **NFR lar raqamli**: judge latency `p50 < 5s, p95 < 15s`, uptime `99.5%`,
  500 parallel submit — va ADR-0004 bake-off mezoni bilan bog'langan.
- **Anti-farm qoidalari** Qvant uchun: faqat birinchi AC, kunlik maksimal 100,
  rejudge da qaytarish, hammasi ledgerda.
- **"Ataylab qoldirilgan"** ro'yxati — nima qilinmasligi va sababi.
- **"Lock'dan keyingi tuzatishlar"** — hujjat qulflangandan keyin ham
  o'zgarishlar kuzatiladi (ADR-0007 misoli). Bu kamdan-kam uchraydigan
  yaxshi amaliyot.

### Uch nuqson, dalil bilan

1. **Acceptance criteria testlanadigan emas.** Gate *"acceptance criteria are
   testable"* deydi. P0-1 ning mezoni — `Ro'yxat, login, /me` — bu **feature
   ro'yxati**, sinov sharti emas: qanday holatda o'tgan hisoblanadi, qaysi
   chegara, qaysi xato holati — yozilmagan. P1, P2, P3 da esa mezon **umuman
   yo'q** (faqat "Manba" ustuni).
2. **Requirement traceability yo'q.** Gate *"traceable to upstream problems and
   decisions"* deydi. **Qarorlarga** havola bor (ADR-0002…0007), lekin
   **muammolarga yo'q**: hech bir qator `02-problem-discovery` dagi og'riq
   yoki `03` dagi bozor topilmasiga bog'lanmagan. Masalan P1-5 (Qvant) —
   02 dagi *"Motivatsiya — faqat reyting yetmaydi"* og'rig'idan kelib chiqqani
   yozilmagan.
3. **`Target users`, `Constraints`, `Evidence / assumptions` bo'limlari yo'q.**
   Rollar user story'larda bor (Talaba, Admin, Tashkilotchi), lekin shablon
   alohida bo'lim talab qiladi.

Bundan tashqari `Qulflash` da **approver ismi yo'q** — 01, 02 va 03 dagi kabi.

### Gate bahosi

**WARN.** BLOCK emas: MVP scope **aniq** (P0 to'liq sanalgan), kritik talablar
**asoslangan** (ADR havolalari bilan), tasdiq bor. Lekin gate'ning **asosiy
o'qishi** — *testable* va *traceable* — ikkalasi ham zaif.

Mazmun bo'yicha bu hozirgacha **eng kuchli hujjat**: formulalar, NFR maqsadlari
va fazalar rejasi jiddiy ishlangan. Kamchilik shaklda, mazmunda emas.

### Tuzatish uchun minimal ish

1. Har bir P0 feature uchun testlanadigan mezon (kirish → kutilgan natija → chegara)
2. `## Requirement traceability` jadvali: feature ID → 02 og'riq / 03 topilma → ADR
3. `## Target users` bo'limi (02 dan meros, lekin shu yerda ham ko'rsatilsin)
4. `## Constraints` (judge host, byudjet, jamoa hajmi, huquqiy)
5. `Qulflash` ga approver ismi va roli

## Qadam 6 — Stage 05: Domain Model

Manba: `rankwant/docs/05-domain-model/README.md` (14282 bayt, STATUS: locked 2026-09-06)

### Template bo'limlari qamrovi

| Kerakli bo'lim | RankWant'da | Holat |
|---|---|---|
| Entities | `Core` · `Judging` · `Contest` · `Reyting` · `Qvant` guruhlari | ✅ |
| **Value objects** | alohida emas (verdict/qiynlik kodlari 04 da) | ⚠️ |
| **Aggregates** | alohida emas (guruhlar modul chegarasi bo'lib xizmat qiladi) | ⚠️ |
| Relationships | `## Entity diagram` (ASCII, to'liq) | ✅ |
| **Invariants** | **bor, lekin sarlavha ostida emas** | ✅ |
| **Business rules** | **bor, lekin sarlavha ostida emas** | ✅ |
| **Lifecycle rules** | faqat soft-delete; holat mashinalari yo'q | ⚠️ |
| **Domain boundaries** | guruhlash orqali nazarda tutilgan | ⚠️ |
| Traceability to requirements | maydonlar ichida havolalar (`04-prd P0-7`, ADR-0006…) | ✅ qisman |
| **Assumptions** | **yo'q** | ⚠️ |
| **Open questions** | **yo'q** | ⚠️ |
| Decisions / approvals | `## Qulflash` + "Lock'dan keyingi tuzatishlar" | ✅ (approver nomisiz) |

### Invariantlar sarlavha ostida emas — lekin MAVJUD

Bu muhim: sarlavhalar bo'yicha hukm chiqarsam, xato qilardim. Invariantlar
entity bo'limlari ichida yozilgan va ular aniq:

- *"foydalanuvchi kontenti (attempt, transaction) **hech qachon** o'chirilmaydi —
  `is_active` / `is_public` bilan yashiriladi"*
- *"hech qachon `UPDATE balance`, faqat ledger yozuvi"*
- `UserSolvedProblem` — **uniq `(user_id, problem_id)`** → "faqat birinchi AC"
- `UserQuestCompletion` — **uniq `(user, quest, period_key)`** → anti-farm
- `Attempt.source_size` — maksimal **64 KB**, kattasi rad etiladi
- `ApiToken.token_hash` — SHA-256, *"ochiq token saqlanmaydi"*
- Test ma'lumotlari **DB da emas, S3/R2 da** (hajm GB darajasida)
- `is_rated` **+ ≥10 ishtirokchi** → Contests reytingi faqat shunda

### Shablon talab qilganidan ortiq

- **`## Indekslar (kritik)`** — 12 ta indeks, har biri uchun *nima uchun*.
  Ayniqsa: `UserSolvedProblem (problem_id)` — *"qayta baholashda ta'sirlanganlarni
  topish (ADR-0007)"*. Ya'ni qaror **fizik indeksgacha** kuzatilgan.
- **`## Migration tartibi`** — 7 qadamli tartib, bog'liqliklar bo'yicha.
- **`## API resurs nomlari`** — resurs nomlash shartnomasi.
- **`Standing` materiallashtirilgan** va sababi yozilgan: *"500 parallel submit
  ostida live hisoblash standings so'rovini buzadi (04-prd NFR)"* — NFR dan
  arxitektura qaroriga to'g'ridan-to'g'ri iz.

### Uch nuqson

1. **`Value objects` va `Aggregates` tushuncha sifatida yo'q.** Gate ularni
   talab qiladi. Aslida ularning *mazmuni* bor (verdict kodlari, qiyinlik
   shkalasi, ACM/IOI scoring — 04 da; modul chegaralari — guruhlashda), lekin
   shu hujjatda **nomlanmagan**. Bu ko'proq terminologik kamchilik.
2. **`Lifecycle rules` to'liq emas.** Faqat soft-delete qoidasi bor. Holat
   mashinalari yo'q: contest (`scheduled → running → frozen → finished`),
   attempt (`pending → judging → judged`), Qvant quest (`available → completed`).
   Bularsiz arxitektura bosqichi har bir holatni o'zi taxmin qiladi.
3. **`Assumptions` va `Open questions` yo'q** — 01–04 dagi bir xil kamchilik.

`Qulflash` da **approver ismi yo'q** (beshinchi bosqich ketma-ket).

### Gate bahosi

**WARN — hozirgacha eng kuchli hujjat.** Gate'ning 7 talabidan 5 tasi aniq
bajarilgan (entities, relationships, invariants, business rules, traceability).
Qolgan ikkisi — value objects va aggregates — **nomlanmagan**, lekin mazmuni
bor. Lifecycle rules eng jiddiy kamchilik, chunki uni arxitektura bosqichi
to'ldirishi kerak bo'ladi va u yerda **taxmin** paydo bo'ladi.

BLOCK emas: domain chegaralari ziddiyatsiz, kritik biznes qoidalar
(`UPDATE balance` taqiqi, birinchi AC uniqligi, anti-farm) aniq va izchil.

### Tuzatish uchun minimal ish

1. `## Value objects` — verdict enum (20 kod), qiyinlik darajalari, scoring turlari
2. `## Aggregates` — guruhlarni agregat sifatida e'lon qilish + har birining ildizi
3. `## Lifecycle rules` — contest, attempt, quest holat mashinalari
4. `## Assumptions` va `## Open questions`
5. `Qulflash` ga approver ismi va roli

## Qadam 7 — Stage 06: Architecture

Manba: `rankwant/docs/06-architecture/README.md` (5411 bayt, STATUS: locked 2026-09-06)
— **eng yupqa bosqich** (10 bosqich ichida eng kichigi)

### Template bo'limlari qamrovi

| Kerakli bo'lim | RankWant'da | Holat |
|---|---|---|
| System context | `## Maqsad arxitektura` — ASCII diagramma | ✅ |
| Containers | diagrammada (Postgres, Redis, S3/R2, judge host) | ✅ |
| Components | `## Servislar` — 5 ta servis | ✅ |
| **Deployment** | "deploy alohida hostlarga" — boshqa hech narsa | ⚠️ **yo'q** |
| **Data flow** | diagrammada strelkalar, **yozma zanjir yo'q** | ⚠️ |
| **Integrations** | S3/R2, Telegram — email/Cloudflare/to'lov yo'q | ⚠️ |
| Security boundaries | `## Xavfsizlik chegarasi` + `## Auth chegarasi` | ✅ **kuchli** |
| **Reliability / scalability** | alohida bo'lim yo'q | ⚠️ |
| **Key trade-offs** | ADR-0003 ga havola; *nima yo'qotilgani* yozilmagan | ⚠️ |
| Architecture decisions | ADR-0003/0004/0008/0009 havolalari | ✅ |
| Traceability to requirements | matn ichida (`admin → P0-2`, `SSR → SEO`) | ✅ qisman |
| **Assumptions** | **yo'q** | ⚠️ |
| Open questions | `## Ochiq` — 1 ta (judge nomzodi) | ✅ qisman |
| Approvals | `## Qulflash` | ✅ (approver nomisiz) |

### Kuchli tomoni — xavfsizlik chegarasi

Bu eng muhim qism va u **juda aniq** yozilgan, muzokarasiz shartlar bilan:

- *"Judge host API/DB bilan bir serverda emas"*
- *"Judge host'da **kiruvchi port yo'q** — worker navbatdan ish tortadi (pull)"*
- Tarmoq jadvali: `judge → Redis ✅ · judge → S3 ✅ · judge → API/DB ❌ · tashqi internet ❌`
- *"Judge host'da **DB credential bo'lmaydi**"*
- *"Til obrazlari va sandbox versiyalari pin qilinadi"*

Yana: `JudgeProvider` interfeysi ortida judge tanlovi — bake-off natijasi
**arxitekturani o'zgartirmaydi**. Bu to'g'ri abstraksiya.

### To'rt nuqson, dalil bilan

1. **`Deployment` bo'limi yo'q.** Faqat bir jumla: *"deploy esa alohida
   hostlarga"*. Gate *"deployment ... explicit"* deydi. Yo'q: muhitlar
   (dev/staging/prod), CI/CD oqimi, host spetsifikatsiyasi, migratsiya deploy
   bilan qanday bog'lanishi, rollback. Diqqat: bu bo'shliq **amalda** allaqachon
   muammo bo'lgan — `tools/check_deploy.sh` ning butun mavjudligi sababi shu.
2. **`Data flow` yozma emas.** Diagrammada strelkalar bor, lekin zanjir matnda
   yo'q: `submit → navbat → judge → verdict → AttemptTestResult → Standing →
   reyting`. NFR maqsadi (`p50 < 5s`) qaysi qadamga tegishli ekani ko'rinmaydi —
   ya'ni uni qayerda o'lchash noma'lum.
3. **`Reliability / scalability` bo'limi yo'q.** 04 da `500 parallel submit`
   NFR bor, lekin unga **qanday** erishish yozilmagan: worker soni, navbat
   sig'imi, DB ulanish hovuzi, judge gorizontal kengaytirish, nosozlik
   holatlari (Redis yiqilsa nima bo'ladi).
4. **`Key trade-offs` yozma emas.** Rad etilgan variantlar ADR-0003 ga havola
   qilingan, lekin *nima yo'qotilgani* shu hujjatda yo'q. Masalan: API va web'ni
   alohida hostlarga qo'yish → operatsion murakkablik va ikki marta deploy.

Qo'shimcha: `Integrations` to'liq emas (email provayderi, Cloudflare, kelajakda
to'lov yo'q), `Assumptions` yo'q, approver ismi yo'q (oltinchi bosqich ketma-ket).

### Gate bahosi

**WARN.** BLOCK emas: kritik arxitektura qarorlari **asoslangan** (ADR
havolalari), domain va PRD bilan ziddiyat yo'q, tasdiq bor. Lekin gate'ning
to'qqiztalabidan **beshtasi** yo'q yoki juda yupqa — deployment, data flow,
integrations, reliability/scalability, trade-offs.

Bu bosqich **hajmi bo'yicha eng kichigi** (5411 bayt) va bu tasodif emas:
xavfsizlik chegarasi chuqur ishlangan, qolgan qismlar diagramma bilan
almashtirilgan.

### Tuzatish uchun minimal ish

1. `## Deployment` — muhitlar, CI/CD, host spetsifikatsiyasi, rollback
2. `## Data flow` — submit'dan reytinggacha yozma zanjir + NFR o'lchov nuqtasi
3. `## Reliability / scalability` — worker/navbat/DB sig'imi, nosozlik holatlari
4. `## Key trade-offs` — har tanlov uchun *nima yo'qotildi*
5. `## Assumptions`, `## Open questions` to'ldirish; `Qulflash` ga approver

## Qadam 8 — Stage 07: ADR

Manba: `rankwant/docs/07-adr/` — **19 ta ADR** (0001–0019) + `README.md`, 132 KB
STATUS: *"living — bu bosqich qulflanmaydi, qarorlar to'planib boradi"*

### Template bo'limlari qamrovi (19 ADR bo'yicha sanaldi)

| Kerakli bo'lim | Sarlavha bo'yicha topilgan | Holat |
|---|---|---|
| Decision ID | sarlavhada (`# ADR-0004: …`) | ✅ |
| Status | `README.md` jadvalida (accepted / proposed / rejected) | ✅ |
| Context / problem | `## Muammo` — **19 / 19** | ✅ |
| Options considered | `## Variant(lar)` — 14 / 19 | ✅ qisman |
| Selected solution | `## Tanlov` 9 ta + `## Qaror` 11 ta (nomi har xil) | ✅ |
| Rationale | `## Sabab` — 10 / 19 | ⚠️ |
| Consequences | `## Oqibat(lar)` — 16 / 19 | ✅ |
| **Evidence** | `## Dalil` / `## Evidence` — **0 / 19** | ⚠️ |
| **Reversibility** | `## Qaytarish` / `Reversib…` — **0 / 19** | ⚠️ **yo'q** |
| **Approval** | `## Tasdiq` / `## Approval` — **0 / 19** | ⚠️ **yo'q** |

Sanoq sarlavha nomlariga tayanadi, ya'ni **past baho** beradi: masalan
ADR-0004 da `## Variantlar` yo'q, lekin uning o'rnida `## Bake-off natijasi`
bor — bu variant tahlilining kuchliroq shakli. Shuning uchun quyidagi
xulosalar faqat **umuman yo'q** bo'lganlarga tayanadi.

### Kuchli tomonlari

- **19 ta ADR** — bu loyihada haqiqiy qaror madaniyati borligining eng kuchli
  dalili. 10 bosqich ichida eng katta hajm.
- **Holatlar README'da kuzatiladi**, va ular orasida **`rejected` ham bor**
  (ADR-0014 — Codeforces handle). Ya'ni qarorlar ko'rib chiqiladi, avtomatik
  qabul qilinmaydi.
- **ADR-0004 da haqiqiy bake-off**: o'lchovlar, o'tkazuvchanlik va sig'im
  hisoblari, va — eng qimmati — **tuzatilgan taxmin**: *"Tuzatilgan taxmin —
  isolate cgroup v2 da ISHLAYDI"*. Ya'ni dastlabki xulosa noto'g'ri bo'lgani
  ochiq yozilgan.
- ADR'lar bir-biriga `## Bog'liq hujjatlar` bilan bog'langan.

### Uch nuqson, dalil bilan

1. **`Reversibility` — 19 tadan 0 tasida.** Gate buni majburiy talab qiladi
   (*"problem, options, selected solution, rationale, consequences, and
   reversibility"*). Qaysi qaror qaytarilishi mumkin, qaysi biri
   qaytarilmasligi hech qayerda yozilmagan — holbuki qaytarilmas qaror
   boshqacha ehtiyot talab qiladi.
2. **`Approval` — 19 tadan 0 tasida.** Gate: *"Human approval required for
   high-impact or irreversible decisions"*. Hech bir ADR kim tomonidan
   tasdiqlanganini yozmaydi.
3. **⚠️ ADR-0004 alohida BLOCK-darajasidagi holat.** U **qaytarilmas** va
   **xavfsizlik uchun kritik** (foydalanuvchi kodi ishlaydigan host), lekin
   README'da hali **`proposed`** va hech qanday tasdiq yozuvi yo'q. Gate'ning
   BLOCK sharti aynan shunga tegishli: *"a high-impact or irreversible decision
   lacks required human approval"*.

   > **TUZATISH (qadam 10 dan keyin).** Bu band **qayta baholandi**.
   > `09-development-plan` da `Sprint 0.5 — Judge bake-off · GATE ✅ YOPILDI
   > (2026-09-06)` deb yozilgan: 7 ta sinov turi o'tkazilgan, g'olib
   > **Go + nsjail, 14/14**. Ya'ni qaror **tasdiqlangan va dalil bilan**.
   > Haqiqiy muammo — tasdiqning yo'qligi emas, **07 indeksining
   > eskirgani**: `proposed` o'rniga `accepted` bo'lishi kerak edi.
   > Ya'ni bu BLOCK emas, **bosqichlararo nomuvofiqlik**.

### Gate bahosi

**WARN — bitta yuqori-darajali band bilan (ADR-0004, keyin qayta baholandi).**

Stage bo'yicha BLOCK emas, chunki bu bosqich o'zi **"living"** deb e'lon
qilingan — qulflanmaydi, ya'ni qarorlar to'planishda davom etadi. ADR-0004
bo'yicha dastlabki xulosa qadam 10 da **tuzatildi**: qaror dalil bilan
tasdiqlangan, indeks eskirgan (yuqoriga qarang).

`Reversibility` va `Approval` bo'limlarining yo'qligi 19 tadan 0 — ya'ni bu
tasodif emas, **shablonning bir qismi umuman qo'llanilmagan**.

### Tuzatish uchun minimal ish

1. **ADR-0004 ga inson tasdig'i** — bu eng ustuvor band (qaytarilmas, xavfsizlik)
2. Har bir ADR ga `## Qaytarilishi` bo'limi: qaytariladigan / qiyin / qaytarilmas
3. Har bir ADR ga `## Tasdiq` — kim, qachon, rol
4. README jadvaliga `Reversibility` ustuni — bir qarashda ko'rinadi

## Qadam 9 — Stage 08: Technical Specification

Manba: `rankwant/docs/08-technical-spec/README.md` (11136 bayt, STATUS: locked 2026-09-06)

### Template bo'limlari qamrovi

| Kerakli bo'lim | RankWant'da | Holat |
|---|---|---|
| API contract | `## API konvensiyalari` — versiya, sahifalash, filtr, OpenAPI | ✅ |
| Database schema | `## DB` — 05 ga havola + migration qoidalari | ✅ |
| Events | `## Judge protokoli` + `### Job payload` + 20 verdict kod | ✅ **kuchli** |
| Authentication / authorization | `## Auth` + `### Rate limit` | ✅ |
| Security | `## Xavfsizlik checklist` — 5 ta band | ✅ |
| Performance targets | `## Sifat shartlari` + observability metrikalari | ✅ |
| Integrations | `## Email — zanjir` + S3/R2 + Telegram | ✅ **kuchli** |
| Error handling | yagona xato formati | ✅ |
| Observability requirements | `## Observability` — log, Sentry, metrikalar, 4 alert | ✅ |
| Traceability to requirements / ADRs | butun hujjat bo'ylab ADR havolalari | ✅ |
| **Assumptions** | alohida bo'lim yo'q | ⚠️ |
| Open questions | `## Ochiq bandlar` — 3 ta | ✅ |
| Approvals | `## Qulflash` | ✅ (approver nomisiz) |

### Nima uchun bu PASS

Gate aynan shunday deydi: *"PASS only when API, data, events, auth, security,
performance, integrations, errors, and observability are implementation-ready
and traceable to requirements and ADRs."*

**To'qqiz shartning to'qqiztasi ham bajarilgan**, va har biri *amalga oshirishga
tayyor* darajada — umumiy so'z emas, aniq shartnoma:

- **Auth:** cookie flag'lari (`httpOnly`, `Secure`, `SameSite=Lax`, 30 kun),
  CSRF, PAT formati (`rw_<32 bayt base62>`), saqlash (SHA-256), scope'lar,
  muddat, 4 bosqichli rate limit jadvali.
- **Judge protokoli:** PULL model, tarmoq qoidasi, **job payload JSON**,
  20 verdict kod jadvali. `SECURITY_VIOLATION` alohida alert chiqaradi.
- **Xato formati:** `{ "error": { "code", "message", "details" } }` — barcha 4xx/5xx uchun bir xil.
- **OpenAPI:** `drf-spectacular`, va *"har PR da schema diff tekshiriladi"*.
- **DB migration:** oldinga mos (add → backfill → switch → drop, alohida deploylarda).
- **Observability:** structured JSON log, `request_id`, Sentry, judge latency
  p50/p95, 4 ta alert sharti.

### Shablon talab qilganidan ortiq

- **`## Env va secrets`** — to'liq env o'zgaruvchilar ro'yxati.
- **`## Email — bitta provayder emas, zanjir`** — eng yaxshi yozilgan bo'lim:
  4 provayderning bepul kvotalari (Brevo 300/kun, Mailjet 200/kun,
  Resend 100/kun, MailerSend 500/oy), **nega har biri alohida subdomen**
  (SPF `include:` 10 lookup cheklovi), va **ikki o'lchangan tuzoq**:
  Resend/MailerSend Cloudflare ortida `urllib` ning standart User-Agent'ini
  bot deb bloklaydi (`error_code 1010`); Brevo'da IP oq ro'yxati qo'lda
  sozlanishi kerak, aks holda jimgina rad etadi.
- **`## Xavfsizlik checklist (launch oldidan)`** — bajariladigan ro'yxat,
  jumladan *"Sandbox escape testi: fork bomb, fayl yozish, tarmoq, `/proc` o'qish"*.

### Kamchiliklar (gate'ni bloklamaydi)

1. **`Assumptions` bo'limi yo'q** — lekin email bo'limi o'lchangan tuzoqlarni
   ochiq yozadi, ya'ni amalda taxminlar ko'rsatilgan.
2. **Approver ismi yo'q** — 7-bosqich ketma-ket takrorlanayotgan naqsh.
3. **`## Referens` → `kep-uz-platform-analysis.md`** — bu fayl **repo'da yo'q**
   (03 dagi bilan bir xil muammo). KEP endpoint ro'yxati tekshirib
   bo'lmaydi.

### Gate bahosi

**PASS** — 10 bosqich ichida **birinchi PASS**. Gate'ning to'qqiz sharti ham
bajarilgan va amalga oshirishga tayyor. Kamchiliklar gate ro'yxatidan tashqarida
(`Assumptions`), yoki bosqich darajasidagi konventsiya (approver).

## Qadam 10 — Stage 09: Development Plan

Manba: `rankwant/docs/09-development-plan/README.md` (11394 bayt, locked 2026-09-06)

### Template bo'limlari qamrovi

| Kerakli bo'lim | RankWant'da | Holat |
|---|---|---|
| Milestones | `## Milestone maqsadlari` | ✅ |
| **Epics** | alohida emas | ⚠️ |
| **Stories** | alohida emas | ⚠️ |
| **Tasks** | alohida emas (sprint = feature darajasi) | ⚠️ |
| **Estimates** | **yo'q** — sprintlarda muddat yo'q | ⚠️ |
| Dependencies | `## Bog'liq loyihalar` + kritik yo'l | ✅ |
| Critical path | `## Kritik yo'l` — ASCII diagramma, bloklovchi bog'lanishlar | ✅ **kuchli** |
| Risks | `## Xavf` | ✅ |
| Release plan | `## Launch gate` + sprintlar | ✅ |
| Traceability to requirements | sprint jadvalida **PRD ID** (P0-1, P0-2, P0-7…) | ✅ |
| **Assumptions** | **yo'q** | ⚠️ |
| **Open questions** | **yo'q** | ⚠️ |
| Approvals | `## Qulflash` | ✅ (approver nomisiz) |

### ⚠️ Asosiy topilma — bosqichlararo ZIDDIYAT

Bu ko'rikda topilgan **birinchi haqiqiy bosqichlararo nomuvofiqlik**:

**09 hujjati** (`## Sprint 0.5 — Judge bake-off · GATE ✅ YOPILDI (2026-09-06)`):

> Maqsad: ADR-0004 ni `proposed` → `accepted`.
> …
> `[x]` **Judge bake-off spike** — g'olib: **Go + nsjail, 14/14 ↓**

**07 hujjati** (`07-adr/README.md` jadvali):

> `| 0004 | Judge engine — o'z engine, bake-off | proposed (bake-off) |`

Ya'ni **qaror qabul qilingan va gate o'lchov bilan yopilgan** (14/14 sinov,
g'olib aniq), lekin **ADR indeksidagi holat yangilanmagan**. Bu Project
Alpha'ning M4 (Cross-Stage Semantic Consistency) aynan ushlashi kerak bo'lgan
nosozlik turi.

**Bu men avvalgi xulosamni tuzatadi:** 07-bo'limda ADR-0004 ni
"BLOCK-darajasidagi holat" deb belgilagandim. Endi aniq bo'ldiki, qaror
**tasdiqlangan va dalil bilan** — muammo tasdiqning yo'qligida emas,
**indeksning eskirganida**. Quyida tuzatish kiritildi.

### Kuchli tomonlari

- **Kritik yo'l aniq va bloklovchi bog'lanishlar bilan:** *"Judge bake-off
  tugamaguncha Sprint 3 (submit oqimi) boshlanmaydi"*. Bu haqiqiy bog'liqlik,
  bezak emas.
- **Sprint 0.5 da o'tish sharti yozilgan:** NFR byudjeti (p50 < 5s, p95 < 15s)
  va *"izolyatsiya sinovlarining hammasi o'tishi shart"* — 7 ta sinov turi
  sanab o'tilgan (fork bomb, fayl/tarmoq/`/proc`, interactive, 100×50 yuklama).
- **Traceability PRD ID bilan** — har sprint `P0-1`, `P0-2` kabi havola beradi.
- **`## Definition of Done`** va **`## Jamoa`** — shablon talab qilmaydi.
- Holat o'lchovlar bilan: *"65 test o'tadi · mypy strict toza (62 fayl) ·
  OpenAPI 23 endpoint, 0 xato"*.

### Boshqa nuqsonlar

1. **`Estimates` yo'q.** Gate *"estimates"* ni talab qiladi. Sprintlarda muddat
   yo'q — `Sprint 1–4` deb nomlangan, lekin bir sprint qancha davom etishi
   yozilmagan. Ya'ni **rejaning vaqt o'qi yo'q**.
2. **`Epics` / `Stories` / `Tasks` bo'limlari yo'q.** Reja sprint darajasida,
   story/task darajasiga tushmagan. Gate ularni sanaydi.
3. `Assumptions` va `Open questions` yo'q; approver ismi yo'q.

### Gate bahosi

**WARN.** Kuchli tomonlar jiddiy: kritik yo'l, gate mezonlari, PRD ID bilan
traceability. Lekin gate sanagan 9 elementdan **3 tasi umuman yo'q**
(epics, stories, tasks) va **estimates ham yo'q** — ya'ni reja *executable*
deb hisoblash qiyin, chunki vaqt o'lchovi berilmagan.

BLOCK emas: scope va release majburiyatlari aniq, tasdiq bor, va
qarama-qarshilik **reja tuzilmasida emas** (u 07 dagi indeks eskirganida).

### Tuzatish uchun minimal ish

1. **`07-adr/README.md` da ADR-0004 holatini `accepted` ga o'tkazish** — eng tez
   va eng aniq tuzatish
2. `## Estimates` — sprint davomiyligi, jami timeline
3. Story/task darajasi — hech bo'lmasa Phase 1 uchun
4. `## Assumptions`, `## Open questions`; `Qulflash` ga approver

## Qadam 11 — Stage 10: Quality & Operations

Manba: `rankwant/docs/10-operations/` — 3 fayl, 52 KB
(`README.md` 28620 · `test-strategy.md` 13146 · `menu.md` 1771)

### Template bo'limlari qamrovi

| Kerakli bo'lim | RankWant'da | Holat |
|---|---|---|
| Test strategy | `test-strategy.md` — **15 qatlam** | ✅ **kuchli** |
| CI/CD | `## CI/CD` + `### Runner` + `### Push'dan oldingi darvoza` | ✅ |
| Monitoring | `## Monitoring va alert` — 6 metrika | ✅ |
| Logging | 10 da yo'q — **08 da bor** (structured JSON, `request_id`) | ✅ bosqichlararo |
| Alerting | `## Monitoring va alert` — shart + sabab | ✅ |
| Backup | `## Backup` — jadval, cron, tiklash sinovi | ✅ **kuchli** |
| **Disaster recovery** | backup + `--restore-test`; **RTO/RPO yo'q** | ⚠️ |
| Runbooks | `## Incident turlari` — 4 tur, qadamlar bilan | ✅ |
| Incident readiness | `## Incident turlari` — ustuvorlik tartibi bilan | ✅ |
| Security / compliance readiness | 10 da yo'q — **08 da** (launch checklist) | ✅ bosqichlararo |
| Release / rollback plan | `## Deploy qoidalari`; prod deploy qo'lda; **rollback aniq emas** | ⚠️ |
| Production launch criteria | `## Ommaviy preview` + 09 dagi launch gate | ✅ qisman |
| Evidence | **o'lchangan** sig'imlar, sanalar bilan | ✅ **kuchli** |
| **Assumptions** | **yo'q** | ⚠️ |
| Open questions | 2 ta ochiq risk + `## Keyinroq to'ldiriladi` (4 band) | ✅ **kuchli** |
| **Approvals** | **yo'q** | ⚠️ |

### Favqulodda kuchli tomonlari

- **O'lchangan sig'imlar, sanalari bilan**: judge sig'imi (2026-09-06), API
  o'qish sig'imi (2026-09-07), standings sig'imi (2026-09-10). Taxmin emas.
- **Ikki ochiq risk to'liq bo'lim sifatida**: NAT ortidagi maktablar va anon
  rate limit; arxivda yashirin test yo'qligi.
- **Halol bo'shliq e'lon qilish.** `## Keyinroq to'ldiriladi` to'rt bandni
  ochiq sanaydi: hosting provayderi, **on-call rotatsiyasi**, **aniq runbook
  qadamlari**, **SLO/error budget**. Repo boshqaruvi jadvalida ham branch
  protection va secret scanning ❌ deb belgilangan, sabab va narxi bilan.
- **`"Tiklash sinovi o'tkazilmasa, backup yo'q deb hisoblanadi"`** — bu
  ko'rikda uchragan eng yaxshi operatsion tamoyil.
- **Eskirgan konteyner sinfi** alohida bo'lim sifatida yozilgan — *"CI
  ko'rmaydigan nosozlik sinfi"* — va undan keyin **eskirganlik EMAS** bo'lgan
  holat ham (2026-09-13 sanasi bilan).
- **CI izolyatsiyasi saboqi**: CI stack'i `name: rankwant-ci` bilan alohida
  compose loyihasida — aks holda CI tozalashdagi `down -v` jonli preview
  bazasini o'chirib yuborardi. Bu qimmatga tushgan aniq saboq.
- **Self-hosted runner ning halol narxi** yozilgan: *"muhit mustaqilligi
  yo'qoladi… «menda ishlayapti» sinfidagi muammolarni toza bulut runneri kabi
  tutmaydi"*.

### ⚠️ Nega bu BLOCK — gate so'zma-so'z bajarilgan

Gate aynan shunday deydi:

> **BLOCK until critical operational gaps are closed and production-launch
> human approval is recorded.**

Ikki shart ham bajarilmagan:

1. **Kritik operatsion bo'shliqlar ochiq** — hujjat **o'zi** sanaydi:
   on-call rotatsiyasi va eskalatsiya, aniq runbook qadamlari, SLO/error
   budget, hosting provayderi. Bular `## Keyinroq to'ldiriladi` da.
2. **Production-launch inson tasdig'i yozilmagan** — 10 bosqichning hech
   birida approver yo'q, bu yerda esa gate uni **majburiy** deb talab qiladi.

Ustiga: **xizmat allaqachon ommaviy ishlayapti.** Ko'rik davomida
`rankwant.uz` tekshirildi — sayt javob beradi, tunnel ishlayapti, tunnel
`status` esa `owner=windows since=2026-09-12T18:50:14Z`. Ya'ni "launch
tasdig'i yo'q" — nazariy emas, **hozirgi holat**.

### Boshqa nuqsonlar

1. **`Disaster recovery` to'liq emas** — backup va tiklash sinovi bor, lekin
   **RTO/RPO** yo'q va failover rejasi yo'q. Bitta mashina — bu o'zi eng katta
   DR riski va u yozilmagan.
2. **`Rollback` aniq emas** — prod deploy qo'lda tasdiqlanadi, lekin qaytarish
   tartibi yozilmagan (qaysi commit'ga, qanday, migratsiya bilan nima bo'ladi).
3. **`Assumptions` yo'q**; approver yo'q.

### Gate bahosi

**BLOCK edi → PASS (2026-09-13 da yopildi).**

Dastlabki baho: gate'ning BLOCK sharti **so'zma-so'z** bajarilgan edi —
kritik operatsion bo'shliqlar ochiq, launch tasdig'i yo'q, xizmat esa
allaqachon ommaviy. Bu "hujjat yozilmagan" emas, **"e'lon qilinmagan qaror"**
holati edi.

**Qaror (B1, savol-javob sessiyasi):** **A — to'liq production launch.**

Bajarildi (commit `58d3573`, +160/−21):

| Bo'shliq | Yozildi |
|---|---|
| SLO / error budget | ✅ `04-prd` NFR laridan (uptime 99.5%, p50<5s, p95<15s, 5xx<1%, navbat<5min) |
| On-call va eskalatsiya | ✅ bir kishi, eskalatsiyasiz — **xavf sifatida qayd etilgan** |
| Runbook qadamlari | ✅ 6 ta holat, haqiqiy `tools/` buyruqlari bilan |
| Disaster recovery | ✅ RPO ≤24 soat, RTO ~1 soat (baza), failover yo'q |
| Release / rollback | ✅ migratsiya nima uchun qaytarilmasligi bilan |
| Production launch tasdig'i | ✅ Saidakbar Narzullayev — Repo owner / maintainer, 2026-09-13 |

⚠️ **Muhim aniqlashtirish.** Tasdiq **to'rt-hostli production topologiyasi
uchun** — u hali qurilmagan. Joriy bitta-mashinali deploy esa hujjatning
o'z ta'rifi bo'yicha **ommaviy preview**, production emas:

> *"**Bu production EMAS** — yuqoridagi to'rt-hostli topologiya o'rniga bitta
> mashinada ishlaydigan ko'rsatuv nusxasi."*

Dastlab men buni "production launch tasdig'i" deb yozgandim va shu bilan
hujjatga **yolg'on da'vo** kiritdim — gate aynan shunday da'voni oldini
olish uchun bor. `## Holat va tasdiq` bo'limi ikkalasini ajratadi: joriy
holat (preview) va tayyorgarlik (production uchun tayyor).

**Qabul qilingan xavflar** (yashirilmagan): bitta mashina (failover yo'q) ·
eskalatsiya zanjiri yo'q (tungi avariya ertalabgacha) · dual-boot (har
tizimning o'z bazasi) · **production topologiyasi qurilmagan**.

### Tuzatish uchun minimal ish

✅ Bajarildi. Qolgan uchtasi `## Keyinroq to'ldiriladi` da — real trafikdan
keyin ko'rib chiqiladi.

## Qadam 12 — Global audit

### Barcha bosqichlar

| Bosqich | Baho | Asosiy sabab |
|---|---|---|
| `idea-selection` | **RETROAKTIV** | 2026-09-13 da yozildi; 4-variant (boshqa soha) ochiq — commit `97e32df` |
| 01 Vision | WARN | strategic assumptions, open questions, approver |
| 02 Problem Discovery | WARN | severity yo'q, evidence/assumptions ajratilmagan, asosiy segment |
| 03 Market Research | WARN | dalillar repo'dan tashqarida, substitutes, narx, regulyatsiya |
| 04 PRD | WARN | acceptance criteria testlanadigan emas, traceability muammolarga |
| 05 Domain Model | WARN | value objects/aggregates nomlanmagan, lifecycle |
| 06 Architecture | WARN | deployment, data flow, reliability, trade-offs |
| 07 ADR | WARN | reversibility 0/19, approval 0/19, indeks eskirgan |
| 08 Technical Spec | **PASS** | gate'ning 9 sharti ham amalga oshirishga tayyor |
| 09 Development Plan | WARN | epics/stories/tasks/estimates yo'q, bosqichlararo ziddiyat |
| 10 Operations | **PASS** | edi BLOCK → 2026-09-13 da yopildi (on-call, runbook, SLO, launch tasdig'i) |

**Yakuniy: `NOT READY`** — 2 PASS · 8 WARN · 0 BLOCK · 1 yo'q bosqich.

Hozirgi holat (2026-09-13, sessiyadan keyin): qolgan to'siq — `idea-selection`
yo'qligi va 8 ta `WARN`. `BLOCK` qolmadi.

> Dastlabki baho (sessiyadan oldin): 1 PASS · 8 WARN · **1 BLOCK** · 1 yo'q.

### Eng muhim to'rt topilma

**1. `idea-selection` umuman yo'q.** Framework Stage 01 dan **oldin** inson
tasdig'ini talab qiladi. RankWant framework'dan oldin boshlangan, ya'ni bu
**retroaktiv** hujjat bo'ladi — va shunday belgilanishi kerak. Hozircha bu
bo'shliq butun zanjirning boshida turadi.

**2. Dalillar repo'dan tashqarida (03 va 08).** `kep-uz-platform-analysis.md`
va `robocontest-uz-platform-analysis.md` repo'da yo'q. Butun TAM/SAM/SOM va
KEP endpoint ro'yxati shu fayllarga tayanadi. Project Alpha'ning asosiy
prinsipi — repo o'zi yetarli bo'lishi — **buzilgan**.

**3. Bosqichlararo ziddiyat (07 ↔ 09).** ADR-0004 `proposed` deb turadi, 09 esa
bake-off gate'i 2026-09-06 da yopilganini yozadi (g'olib Go + nsjail, 14/14).
Bu M4 (Cross-Stage Semantic Consistency) aynan ushlashi kerak bo'lgan nosozlik.

**4. 10 Operations — BLOCK.** Kritik operatsion bo'shliqlar ochiq (on-call,
runbook, SLO, hosting) va launch tasdig'i yozilmagan — **holbuki xizmat
allaqachon ommaviy ishlayapti**.

### Uchta takrorlanuvchi naqsh (11 bosqichning hammasida)

| Naqsh | Qamrov | Holat |
|---|---|---|
| `Assumptions` bo'limi yo'q | 01–10 — **hammasida** | ✅ tuzatildi |
| `Open questions` yo'q | 01, 02, 03, 04, 06, 07, 09 (05 va 10 da qisman bor) | ✅ tuzatildi |
| `Qulflash` bor, **approver ismi yo'q** | 01–10 — **hammasida** | ✅ tuzatildi |

**Tuzatildi — commit `929bff3`** (10 fayl, +262/−6).

Muhim chegara: taxminlar **o'ylab topilmadi** — har biri hujjatning o'zida
allaqachon yozilgan gapdan chiqarildi va **manbasi ko'rsatildi**. Javob
bo'lmagan joyda esa "javob yo'q" deb yozildi.

Ikki istisno, ataylab:

- **`01-vision`** — bo'lim `## Assumptions` emas, `## Strategic assumptions`
  deb nomlandi, chunki framework'ning o'z shabloni shunday ataydi.
- **`07-adr` va `10-operations` da approver yozilmadi.** 07 da ADR'lar
  `living`, 10 da esa launch tasdig'i **haqiqatan yo'q** — u yerda
  `## Tasdiq` bo'limi **PENDING** deb belgilandi. Bo'sh joyni to'ldirish
  o'rniga ochiq qoldirish to'g'ri, chunki gate aynan shuni talab qiladi.

Shu bilan birga **ustuvorlik #2** ham bajarildi: `07-adr/README.md` da
ADR-0004 `proposed (bake-off)` → **`accepted`** (bake-off 2026-09-06:
Go + nsjail, 14/14). Bosqichlararo ziddiyat yopildi.

**Qolgan ustuvorlik:** #1 (10 Operations — A/B qarori, bu sizdan) ·
#3 `idea-selection` · #4 tahlil fayllarini repo'ga ko'chirish ·
#6 06 deployment · #7 04 acceptance criteria.

### Muhim ijobiy xulosa

**Mazmun kuchli, shakl to'liq emas.** RankWant hujjatlari — jiddiy muhandislik
mahsuli: 4 reyting formulasi isbotlari bilan, 19 ta ADR (bittasi `rejected`),
o'lchangan sig'imlar sanalari bilan, 15 qatlamli test strategiyasi, va
"tiklash sinovi o'tkazilmasa backup yo'q deb hisoblanadi" kabi tamoyillar.

Topilgan nuqsonlarning **ko'pchiligi hujjat butunligi** masalasi — mahsulot
yoki kod masalasi emas. Bu muhim farq: hujjat nuqsoni bir kunda tuzatiladi,
mahsulot nuqsoni oylab.

### Nima qilish kerak — ustuvorlik tartibi

| # | Ish | Holat |
|---|---|---|
| 1 | **10 Operations — A/B qarori** | ✅ **bajarildi** — A (to'liq launch), commit `58d3573` |
| 2 | `07-adr/README.md` da ADR-0004 → `accepted` | ✅ **bajarildi** — commit `929bff3` |
| 3 | **`idea-selection` hujjati** (retroaktiv deb belgilanadi) | ⏳ keyingi (B2) |
| 4 | Ikki tahlil faylini repo'ga ko'chirish | ⏳ fayllar **Linux bo'limida** — belgilandi, commit `b680fbb` |
| 5 | Uch naqshni mexanik tuzatish | ✅ **bajarildi** — commit `929bff3` |
| 6 | 06 Architecture — deployment bo'limi | ⏳ keyingi (B3) |
| 7 | 04 PRD — acceptance criteria + traceability | ⏳ keyin |
| 8 | 03 — `Substitutes` + voyaga yetmaganlar regulyatsiyasi | ⏳ keyingi (B4) |

---

## Keyingi qadamlar

| Qadam | Bosqich | Holat |
|---|---|---|
| 1 | Inventar | ✅ bajarildi |
| 2 | 01 Vision | ✅ bajarildi — **WARN** |
| 3 | 02 Problem Discovery | ✅ bajarildi — **WARN** |
| 4 | 03 Market Research | ✅ bajarildi — **WARN** |
| 5 | 04 PRD | ✅ bajarildi — **WARN** |
| 6 | 05 Domain Model | ✅ bajarildi — **WARN** (eng kuchli) |
| 7 | 06 Architecture | ✅ bajarildi — **WARN** (eng yupqa) |
| 8 | 07 ADR (19 ta) | ✅ bajarildi — **WARN** + ADR-0004 da BLOCK-daraja |
| 9 | 08 Technical Spec | ✅ bajarildi — **PASS** (birinchi) |
| 10 | 09 Development Plan | ✅ bajarildi — **WARN** + bosqichlararo ziddiyat |
| 11 | 10 Operations | ✅ bajarildi — **BLOCK** |
| 12 | Global audit | ✅ bajarildi — **NOT READY** |
