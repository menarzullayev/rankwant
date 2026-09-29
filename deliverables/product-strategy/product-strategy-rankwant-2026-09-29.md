# RankWant — Product Strategy, Roadmap va Backlog

**Sana:** 2026-09-29
**Turi:** Product Strategy (Vision + User/JTBD + Scope + Feature Catalog + Prioritization + Journey Map + Dependency Map + Roadmap + Backlog + AI Roadmap + Metrics + Risks)
**Asosiy manba (source of truth):** `docs/research/2026-09-29-ai-agent-enterprise/REPORT.md`
**Ikkinchi darajali manbalar:** `docs/01`–`docs/10` (locked 2026-09-06), `docs/07-adr/` (27 ADR), `README.md`, `INDEX.md`, `CLAUDE.md`, `docs/03-market-research/`, `docs/research/2026-09-19-scale-50k/`, `docs/research/2026-09-20-as-built-architecture/`, `docs/research/2026-09-21-security-boundary/`, va kod bazasi (`apps/`, `services/`, `tests/`)
**Ishtirok etgan a'zolar:** 方向明（Product Director — yetakchi, Vision va yig‘ish) · 析客（Requirement Analyst — 04/05/09) · 瑞思（User Researcher — 02/06) · 竞析（Competitive Analyst — raqobat/scope/out-of-scope) · 数析（Data Analyst — 13/14/12) · 路径（Roadmap Planner — 07/08/10)

---

## 📌 TL;DR

- **Asosiy tuzatish:** brifingdagi “loyiha katta qismi ishlab chiqilmagan” degan da’vo **repo bilan zid**. Kod tekshiruvi Phase 0, 1, 3 **to‘liq**, Phase 2 **deyarli** bajarilganini ko‘rsatadi (19 Django app, 87 migratsiya, 2 ishlaydigan judge, 82 web route). Vazifa — “noldan qurish” emas, **qurilganni ishonchli qilish, ishlab chiqarishga chiqarish va AI bilan kengaytirish**.
- **Mahsulot bugun ishonchsiz:** 1 226 public masaladan **1 222 tasida yashirin test yo‘q**; o‘lchangan isbot — `print('3 2 1')` **AC** oldi. North Star (haftalik faol yechuvchi) aynan shu yuzada o‘lchanadi, ya’ni **soxta bo‘lishi mumkin**.
- **Eng katta yagona mahsulot bo‘shlig‘i:** *“xatoni tushunish”* qadami — yagona **YO‘Q** qadam. AI **umuman yo‘q** (0 integratsiya), lekin bu aynan o‘sha uzilgan qadamni yopadigan joy.
- **Eng katta B2B blokeri:** anonim throttle 60 req/min/IP → bir IP ortida 20 foydalanuvchidan **94% HTTP 429**. Maktab kompyuter sinfi — B2B ning asosiy xarid stsenariysi — **bugun ishlamaydi**.
- **Qaror:** roadmap **qayta asoslandi**. Phase 0 = *Trust & Hardening*, Phase 1 = *Production & Scale*, Phase 2 = *Instrumentation* — **AI faqat shundan keyin**. Ya’ni: **ishonch → ishlab chiqarish → o‘lchov → AI → B2B**.

---

## 🎯 Core conclusion card

| Element | Qiymat |
|------|------|
| **Tavsiya etilgan yo‘nalish** | “Ishonchli baholash + shaffof reyting + o‘zbek tilidagi o‘quv halqasi”ni yopish; AI faqat “xatoni tushunish” qadamini yopish uchun, practice rejimida |
| **Ustuvorlik** | **P0** = kontent butunligi (F09–F11), verdikt yaxlitligi (F05), ishlab chiqarishga tayyorlik (F66–F69, F74), B2B throttle (F73) |
| **Kutilgan ta’sir** | North Star haqiqiy o‘lchanadigan bo‘ladi; B2B sinf stsenariysi ishlaydi; `rankwant.uz` “preview”dan productionga o‘tadi; AI uchun o‘lchanadigan poydevor paydo bo‘ladi |
| **Resurs talabi** | Kontent jamoasi (1 222 masala + 870 test — **inson-bound, eng katta yuk**), DevOps/SRE (staging, 4-host, monitoring), Backend (throttle, verdikt), AI Engineer (P3 dan) |
| **Risk darajasi** | **Yuqori** — 3 ta bir vaqtda: kontent inqirozi (mavjud va o‘lchangan), cold start (0 real user vs 197k tarmoq effekti), ma’lumot sifati (qarorlar seed data ustida) |
| **Muddat** | **Berilmaydi** — repo’da velocity yo‘q; faqat **sequencing + S/M/L** hajm (hafta yozish fabrikatsiya bo‘lardi) |

---

# 01. Product Vision

> Bu bo‘lim — Product Director’ning o‘z sintezi; qolgan barcha bo‘limlar mutaxassislar tomonidan mustaqil ishlab chiqilgan.

## 1.1 Vision (bir gap)

> **RankWant — o‘zbek tilida o‘qiydigan, halol baholanadigan va ko‘rinadigan reytingi bor yagona sport dasturlash platformasi: o‘qish, yechish, musobaqa va o‘sishni bir joyda yopadigan tizim.**

## 1.2 Mission

Sport dasturlash va informatika olimpiadasi iqtidorini **ishonchli baholash, shaffof reyting va tuzilgan o‘qish** orqali o‘stirish — O‘zbekiston birinchi bozor, nom va UI esa global. *(docs/01 dan, o‘zgartirilmagan)*

## 1.3 Core Value Proposition

**Foydalanuvchi uchun:** “Yechganing — haqiqatan yechilgan; reytinging qanday hisoblanganini ko‘rasan; xatoingni o‘z tilingda tushunasan; o‘sishing ko‘rinadi.”

**Uch ustun (bu tartibda muhim):**

1. **Ishonchli baholash** — AC bo‘lsa, u haqiqiy AC. Bugun bu **buzilgan** (1 222/1 226 masalada yashirin test yo‘q).
2. **Shaffof reyting** — 4 formula ochiq (ADR-0006), har o‘zgarish `RatingHistory` ga sabab bilan. Bu lokal maydonda **haqiqiy farq** (FACT).
3. **O‘zbek tilidagi yopiq halqa** — maqola ↔ masala ↔ musobaqa ↔ reyting, bitta tilda. Na RoboContest, na KEP, na Codeforces buni beradi.

**Biznes uchun:** *usage* segment — o‘quvchi; *revenue* segment — tashkilot (maktab tarmog‘i / vazirlik / IT Park). O‘rtada competitive programmer — seed-koprik (RECOMMENDATION, chunki “asosiy segment qaysi?” savoli repo’da **javobsiz**).

## 1.4 Asosiy differentiatorlar

| # | Differentiator | Dalil | Holat |
|---|---|---|---|
| 1 | **O‘zbek tilidagi kontent + judge bir joyda** | cp.uz’da OJ yo‘q; RoboContest/KEP’da o‘zbek o‘quv kontenti yo‘q | BOR (lekin 145 mavzu faqat uz/ru/en) |
| 2 | **Ochiq API** | RoboContest API **yopiq** (Inertia); cp.uz’da umuman yo‘q | BOR |
| 3 | **Shaffof reyting (4 formula ochiq)** | Raqobatchilarda o‘lchanmagan/oshkor emas | BOR |
| 4 | **Contest formatlari kengligi** | duel, arena, chempionat, hakaton, hack, mirror, virtual, marafon | BOR |
| 5 | **Qvant — yopiq halqa gamification** | Real pul qiymati yo‘q; ledger-only; anti-farm | BOR |
| 6 | **AI “xatoni tushunish” qadamini yopish (o‘zbekcha)** | Lokal platformalarda AI **nol**; globalda o‘zbek tili yo‘q → deyarli bo‘sh nisha | **YO‘Q** — strategik imkoniyat |

⚠️ #6 **negativ dalilga** tayanadi (“lokal platformalarda AI topilmadi”) va o‘zbekcha feedback sifati **o‘lchanmagan** — shu sababli u **P2**, P0 emas.

## 1.5 Product Principles

Mavjud 6 prinsip (docs/01) saqlanadi va **o‘lchangan topilmalardan kelib chiqqan holda 6 tasi qo‘shiladi**:

| # | Prinsip | Manba |
|---|---|---|
| 1 | Clone emas, benchmark | docs/01 |
| 2 | Reyting aniq — yashirin algoritm yo‘q | docs/01 |
| 3 | O‘zbek + global | docs/01 |
| 4 | Brend ikkiligi (platforma ≠ coin) | docs/01 |
| 5 | Fazali MVP | docs/01 |
| 6 | Huquqiy xavfsizlik (nusxalamaslik) | docs/01 |
| **7** | **Ishonch funksiyadan oldin.** Baholash yolg‘on bo‘lsa, yangi funksiya qiymat qo‘shmaydi — qiymatni **ko‘paytiradi**. | Yangi: 1 222/1 226 masala |
| **8** | **Metrika yo‘q — funksiya yo‘q.** Har bir AI (va har bir yangi) funksiya uchun metrika **qurilishdan oldin** belgilanadi. | Yangi: “agent washing” xavfi |
| **9** | **Contest’da AI o‘chirilgan; practice’da ruxsat.** Bu **texnik** qoida, marketing va’dasi emas. | REPORT.md §6 |
| **10** | **Bajarib bo‘lmaydigan integrity va’da berilmaydi.** Foydalanuvchi boshqa oynada o‘z AI’sini ishlatishi **to‘sib bo‘lmaydi** — buni ochiq tan olamiz va flag + inson ko‘rigi bilan boshqaramiz. | Yangi: REPORT.md ochiq savoli |
| **11** | **AI judge host’ga, testdata bucket’ga yoki DB’ga to‘g‘ridan-to‘g‘ri tegmaydi** — faqat ruxsat-cheklangan interfeys. | Yangi: ADR-0004 chegarasi |
| **12** | **Kontent — mahsulot.** Masala sifati — feature emas, mahsulotning o‘zi. | Yangi: kontent inqirozi |

## 1.6 RankWant nima EMAS

- Faqat statistika agregatori emas (CoderSTAT emas).
- KEP/RoboContest UI/API nusxasi emas; Aurora white-label emas.
- cp.uz forki emas va unga bog‘liq emas (ADR-0005).
- **Faqat AI mahsulot emas** — AI bu yerda **yordamchi qatlam**, mahsulotning o‘zi emas.
- Mobil-ilova-birinchi mahsulot emas (API-first, ADR-0008).
- Ochiq-litsenziyali fork emas (AGPL — DMOJ/Hydro — ataylab rad etilgan).

## 1.7 Strategik tezis (nega aynan shu tartib)

Mahsulotning uchta uzilish nuqtasi bor va ular **ketma-ket** yopiladi:

```
(1) Baholash ishonchsiz          →  hech narsa o'lchanmaydi
        ↓ tuzatiladi
(2) Ishlab chiqarishga tayyor emas → real foydalanuvchi qabul qilinmaydi
        ↓ tuzatiladi
(3) Real user xatti-harakati o'lchanmaydi → AI va monetizatsiya asossiz
        ↓ instrumentatsiya
(4) AI "xatoni tushunish" qadamini yopadi → retention va activation
        ↓
(5) B2B (throttle tuzatilgach) → daromad
```

**Ya’ni: ishonch → ishlab chiqarish → o‘lchov → AI → B2B.** Bu tartibni buzish (masalan, avval AI mentor chiqarish) foydalanuvchiga **noto‘g‘ri testga asoslangan** tushuntirish beradi — ya’ni ishonchni yanada buzadi.

---

# 02. User & JTBD Model

> **METODOLOGIK OGOHLANTIRISH (FACT):** RankWant bo‘yicha **birlamchi foydalanuvchi tadqiqoti yo‘q** — na intervyu, na so‘rovnoma, na real foydalanuvchi analitikasi. Bazada ~384 569 urinish bor, lekin faqat **1 tasi** haqiqiy judge qilingan (qolgani seed); real foydalanuvchi populyatsiyasi **0**. Shu sababli quyidagi persona/goal/pain — `docs/01`, `docs/02` va raqobatchi pattern’laridan chiqarilgan **INFERENCE/ASSUMPTION**, **FACT emas**.

## 2.1 Rollar

### R1 · O‘quvchi (maktab o‘quvchisi)
*Aziz, 16 · Toshkent · 10–11-sinf · DTM informatika + olimpiada · maktab labi (NAT) + arzon Android · uz*

| Element | Qiymat |
|---|---|
| Goal | DTM/olimpiada uchun masalalarni mustaqil yechib, birinchi AC olmoq va reyting ko‘tarmoq |
| JTBD | “Imtihon muddati yaqinlashib, lab vaqti cheklanganida, mos masalani topib, **to‘g‘ri** verdict olmoqchiman — xatolardan o‘rganib, reytingda ko‘tarilish uchun” |
| Pain | Yashirin test yo‘q → noto‘g‘ri javob ham AC (FACT, **HIGH**); testsiz masala IE qaytaradi (FACT, **HIGH**); xatoni tushunishga yordam yo‘q (FACT, **HIGH**); labda 429 (FACT, **HIGH**); “reyting yetmaydi” (ASSUMPTION, MEDIUM); verdikt yorliqlari faqat o‘zbekcha (FACT, LOW) |
| Desired Outcome | birinchi AC median < 7 kun; haftalik qaytish > 30% (docs/02 — “misol”, majburiyat emas) |
| Workflow | problem bank · judge submit · virtual contest · profil reytingi · Qvant quest/streak |

### R2 · Competitive programmer (universitet / sport CP)
*Diyor, 20 · universitet · ICPC jamoasi · noutbuk · en/ru/uz*

| Element | Qiymat |
|---|---|
| Goal | ICPC/sport CP mashqi, reyting, jamoa, mirror contest |
| JTBD | “ICPCga tayyorlanayotganimda, kuchli test datasi va haqqoniy standings kerak — o‘z darajamni boshqalar bilan o‘lchash uchun” |
| Pain | Test datasi zaif → reyting ishonchsiz (FACT, **HIGH**); community kichik (ASSUMPTION, MEDIUM) |
| Desired Outcome | mirror/real contest ishtiroki; reyting o‘zgarishini tushunish |
| Workflow | contests + standings · duels · arena · championship · problem bank · blog |

### R3 · Mustaqil o‘rganuvchi
*Malika, 24 · ishlaydi, kechqurun o‘qiydi · noutbuk · uz/ru*

| Element | Qiymat |
|---|---|
| Goal | ish bilan parallel CP/algoritm o‘rganish |
| JTBD | “Kam vaqt bilan o‘qiganimda, bog‘langan masalalari bor aniq roadmap kerak — hammasini o‘zim rejalashtirmasdan” |
| Pain | roadmap bor, lekin AI izoh yo‘q (FACT, **HIGH**); 145 mavzu faqat uz/ru/en (FACT, MEDIUM) |
| Desired Outcome | roadmap → problem → solve halqasi; streak; quest completion 30%+ DAU |
| Workflow | articles + roadmaps · problem bank · custom test · streak/Qvant · notifications |

### R4 · O‘qituvchi / murabbiy
*Nodira opa, 38 · maktab informatika o‘qituvchisi · sinf + lab*

| Element | Qiymat |
|---|---|
| Goal | sinfga uy vazifasi berish, progressni kuzatish |
| JTBD | “25 o‘quvchidan iborat sinfni o‘qitganimda, masala tayinlab, kim yechganini ko‘rmoqchiman — yordamni kerakli joyga qaratish uchun” |
| Pain | lab bitta NAT IP → 429 (FACT, **HIGH — BLOKER**); real sinf piloti yo‘q (FACT, MEDIUM) |
| Desired Outcome | class → assignment → progress; 5+ maktab pilot |
| Workflow | classroom · mirror contests · problem bank |

### R5 · Admin / operator
*Sardor, 27 · platforma operatori / olimpiada administratori*

| Element | Qiymat |
|---|---|
| Goal | contest/mirror tashkil qilish, foydalanuvchi va kontentni boshqarish |
| JTBD | “Rasmiy olimpiada o‘tkazganimda, contest yaratib, masala joylab, yuklamani kuzatmoqchiman — ishonchli tadbir uchun” |
| Pain | admin UI bor (21 bo‘lim, FACT) lekin production emas (FACT, MEDIUM); kontent sifati admin yukini oshiradi (FACT, **HIGH**); staging yo‘q (FACT, MEDIUM) |
| Desired Outcome | contest operation; kontent to‘ldirish; 0-downtime tadbir |
| Workflow | admin UI · mirror contests · contest + standings · judge |

### R6 · Tashkilot (B2B)
*maktab tarmog‘i / vazirlik / IT Park vakili (nom yo‘q — INFERENCE)*

| Element | Qiymat |
|---|---|
| Goal | rasmiy olimpiada infratuzilmasi, mirror contest, brend |
| JTBD | “Hududiy olimpiada o‘tkazganimizda, o‘z brendimiz bilan rasmiy infratuzilma kerak — judge’ni o‘zimiz qurmaslik uchun” |
| Pain | pricing yo‘q → sotib bo‘lmaydi (FACT, **HIGH**); NAT/429 (FACT, **HIGH**); staging/production topology yo‘q (FACT, MEDIUM); B2B onboarding/SLA yo‘q (INFERENCE, MEDIUM) |
| Desired Outcome | shartnoma, mirror contest, rasmiy event |
| Workflow | mirror contests · admin UI · own content |

## 2.2 Rol reytingi — kim primary, kim to‘laydi

> **OPEN QUESTION (hujjatlashtirilgan):** `docs/01` va `docs/02` ikkalasi ham “qaysi segment primary?” savolini **javobsiz** qoldirgan. Quyidagilar — **RECOMMENDATION**, FACT emas.

| Rol | Primary? | To‘lovchi? | Sabab |
|---|---|---|---|
| O‘quvchi | **1 — RECOMMENDED primary** | Yo‘q | Eng katta addressable populyatsiya; DTM/olimpiada — mahalliy wedge; gamifikatsiya aynan shunga qaratilgan. *Caveat: kontent sifati + NAT/429 hozir bloklaydi.* |
| Competitive programmer | 2 — seed/beachhead | Yo‘q | Contest kontenti, standings, community yaratadi; qo‘pol holatga chidamli; judge’ni validatsiya qiladi |
| Mustaqil o‘rganuvchi | 3 | Ba’zan (kelajak premium) | O‘qish+yechish birlashishi kerak; premium bloklangan |
| O‘qituvchi | 4 | Yo‘q (influencer/buyer) | Sotib olishga ta’sir qiladi, to‘lamaydi |
| Tashkilot | 5 (usage emas, revenue) | **HA — RECOMMENDED revenue segment** | Maktab tarmoqlari/vazirlik/IT Park shartnoma to‘lovchisi |
| Admin/operator | — (ichki) | Yo‘q | Internal rol |

**Xulosa:** *usage* = o‘quvchi · *revenue* = tashkilot (B2B) · competitive programmer — oradagi seed-koprik. **Bugun to‘lovchi YO‘Q** (pricing yo‘q).

## 2.3 Yetishmayotgan tadqiqot

| # | Savol | Metod |
|---|---|---|
| 1 | O‘quvchi nega yechishni to‘xtatadi — vaqt, qiyinlik, ishonchsiz verdict? | intervyu + diary study |
| 2 | Real motivator — reytingmi yoki Qvant/quest/streakmi? | so‘rovnoma + A/B instrumentatsiya |
| 3 | O‘qituvchi haqiqatan RankWant’da uy vazifasi beradimi? Workflow mos keladimi? | intervyu + sinf piloti |
| 4 | B2B shartnomani kim imzolaydi — maktab, vazirlik, ota-ona? | B2B intervyu |
| 5 | “Xatoni tushunish” uchun nima kerak — AI izoh, editorial, community? | concept test / so‘rovnoma |
| 6 | ru/en/kk foydalanuvchilar qaysi tillarni talab qiladi? | so‘rovnoma + funnel instrumentatsiya |
| 7 | Nechta real lab bitta NAT IP ortida? | field study / maktab tashrifi |
| 8 | Premium va B2B narxga sezgirlik? | pricing so‘rovnoma |

**Repo bugun nima o‘lchay oladi:** register, birinchi-AC vaqti, submit→verdict, WAS, contest register→participation, quest completion, Qvant spend. **Lekin 0 real user + seed data → hozir real foydalanuvchida hech narsani o‘lchab bo‘lmaydi (UNKNOWN).**
**O‘lchay olmaydi:** churn sababi, motivatsiya drayverlari, to‘lashga tayyorlik, o‘qituvchi workflow mosi, til ehtiyoji, real lab topologiyasi.

---

# 03. Product Scope (nima bor / nima kerak / nima keyin)

| Feature | Holat | Qaror | Sabab (evidence) |
|---|---|---|---|
| Auth/login | BOR | saqlanadi | Phase 0 done |
| Problem bank | BOR | **tuzatiladi** | 1 222/1 226 yashirin test yo‘q |
| Judge submit (20 verdict) | BOR | saqlanadi | Phase 0 done |
| Custom test | BOR | saqlanadi | Phase 0 done |
| ACM contests + standings | BOR | saqlanadi | Phase 0 done |
| Profile + Skills/Contests rating | BOR | saqlanadi | ADR-0006 ochiq formulalar |
| i18n (10 locale) | QISMAN | **tuzatiladi** | verdikt hardcoded uz; 16 tier nomi tarjimasiz |
| Virtual contest | BOR | saqlanadi | Phase 1 done |
| Recommendation | BOR | saqlanadi | Phase 1 done |
| Blog / Notifications | BOR | saqlanadi | Phase 1 done |
| Qvant wallet+ledger+quests+streaks | BOR | saqlanadi | ADR-0002 yopiq halqa |
| Activity rating | BOR | saqlanadi | Phase 1 done |
| Qvant shop | QISMAN | **keyinroq** | mavsumiy kengaytma tugamagan |
| Weekly marathon | BOR | saqlanadi | Phase 1 done |
| Mirror contests | BOR | saqlanadi | Phase 2 done |
| Teacher classroom | BOR | **tuzatiladi** | NAT throttle B2B blokeri (94% 429) |
| Learning content (articles+roadmaps) | BOR | **tuzatiladi** | 145 mavzu faqat uz/ru/en |
| MCQ quizzes | QISMAN | saqlanadi | scope bir qismi bajarilmagan |
| Duels / Arena | BOR | saqlanadi | Phase 3 done |
| Championship / Hackathon | BOR | saqlanadi | Phase 3 done |
| Calendar / Search / Algorithms ref | BOR | saqlanadi | Phase 3 done |
| Admin UI (21 bo‘lim) | BOR | saqlanadi | Phase 3 done |
| **Yashirin testlar (1 222 masala)** | **YO‘Q** | **quriladi** | `print('3 2 1')` → AC (o‘lchangan) |
| **Imported masalalar IE fix (870)** | **YO‘Q** | **quriladi** | 870/2 096 test yo‘q → IE |
| **Multi-answer checker fix (200)** | **YO‘Q** | **quriladi** | noto‘g‘ri `standard` checker |
| **Bo‘sh/qisqa statement fix** | **YO‘Q** | **quriladi** | 5 bo‘sh, 164 <100 belgi |
| Verdikt yorliqlari i18n | YO‘Q | **tuzatiladi** | UI’da hardcoded o‘zbekcha |
| Rating-tier nomlari i18n | YO‘Q | **tuzatiladi** | 16 nom 6+ tilga tarjimasiz |
| **NAT throttle fix** | **YO‘Q** | **quriladi** | 60 req/min; maktab labi sinadi |
| Pricing / subscription | YO‘Q | **keyinroq** | pricing ADR’da bloklangan |
| AI mentor (production) | YO‘Q | **keyinroq** | sifat o‘lchanmagan; 0 AI integratsiya |
| Staging environment | YO‘Q | **quriladi** | hozir yo‘q (docs/10 zid) |
| 4-host production topologiyasi | YO‘Q | **quriladi** | deploy 1 mashina, NOT production |
| Judge scale-out (~6–8 host) | YO‘Q | **quriladi** | 500/10s = 50/s; 8 worker 8/s |
| Backup PITR | YO‘Q | **quriladi** | RPO ≤30 kun, PITR yo‘q |
| Sentry / monitoring | YO‘Q | **quriladi** | hozir yo‘q |
| security.yml CI qayta yoqish | YO‘Q | **tuzatiladi** | workflow `if: false` |
| Judge privileged/cgroup fix | YO‘Q | **tuzatiladi** | ADR-0004’ga zid |
| MinIO parol (`devdevdev`) | YO‘Q | **tuzatiladi** | public repo’da literal |

---

# 04. Feature Catalog

**Holat legendasi:** `BOR` = kodda tasdiqlangan va ishlaydi · `QISMAN` = qisman qurilgan yoki qurilgan lekin nuqsonli · `YO‘Q` = mavjud emas.
**Ustuvorlik qoidasi:** P0–P3 **qolgan ishga** nisbatan. Allaqachon ishlab chiqarilgan (BOR) xususiyatlar past qoldiq ustuvorlik oladi — ularni “qayta qurish” ro‘yxatiga kiritish xatodir.
**Murakkablik:** S / M / L / XL.

## 4.1 Foundation

| ID | Feature | User | Problem | Value | Holat | P | CX | Dep | Phase | Acceptance criteria |
|---|---|---|---|---|---|---|---|---|---|---|
| F01 | Email + parol auth | yangi foydalanuvchi | hisob yaratish yo‘li | platformaga kirish | BOR | P3 | M | Postgres, DRF | 0 | ① 3 maydon bilan signup (ADR-0016) ② parol tiklash ③ session |
| F02 | PAT auth | API/CLI user | sessiyasiz kirish | avtomatlashtirish | BOR | P3 | S | F01 | 0 | ① `rw_…` yaratish/revoke ② Bearer header ③ scope/muddat |
| F03 | Telegram login widget | Telegram user | parolsiz kirish | ishqalanishsiz onboarding | BOR | P3 | S | F01 | 0 | ① widget kirish ② hisob bog‘lanadi ③ takroriy kirish |
| F04 | i18n infratuzilmasi (10 til) | barcha | bir tilga qulflash | reach | **QISMAN** | **P1** | L | — | 0–3 | ① `?lang=`→cookie→Accept-Language→uz ② 10 tilda 0 yetishmagan kalit ③ hreflang qarori ADR ④ sana/raqam 10 tilda |
| F05 | Verdikt kodlari va yorliqlari | submit qiluvchi, o‘qituvchi | 4 o‘lik kod + hardcoded yorliqlar | ishonchli feedback | **QISMAN** | **P0** | M | F12 | 0 | ① har kod yoziladi yoki o‘chiriladi ② yorliqlar i18n (10 til) ③ RE→RE_SIGNAL/RE_EXIT ④ WRONG_TEST/INPUT_PREPARATION_CRASHED ⑤ PE qarori ⑥ ustuvorlik tartibi hujjatlashtirilgan |
| F06 | Qvant wallet + ledger | faol yechuvchi | motivatsiya valyutasi | engagement | BOR | P2 | M | F01 | 1 | ① har o‘zgarish ledger orqali ② `qvant_audit` 0 nomuvofiqlik ③ kunlik cap 100 ④ rejudge refund |
| F07 | Reyting dvigateli (4 formula) | barcha | shaffof progress | ishonch, raqobat | BOR | P2 | L | F12 | 0–3 | ① 4 formula testlar bilan (MANDATORY) ② har o‘zgarish RatingHistory’ga ③ difficulty 800–3500, 7 daraja |

## 4.2 Core CP Platform

| ID | Feature | User | Problem | Value | Holat | P | CX | Dep | Phase | Acceptance criteria |
|---|---|---|---|---|---|---|---|---|---|---|
| F08 | Problem bank CRUD | admin/kontent | masala boshqaruvi | kontent quvuri | BOR | P3 | M | F58 | 0 | ① CRUD ② filtrlar ③ meta saqlanadi |
| **F09** | **Yashirin test quvuri** | yechuvchi, kontent | 1 226 dan 1 222’sida yashirin test yo‘q; `print('3 2 1')`=AC | **baholash ishonchliligi — mahsulot yuragi** | **QISMAN** | **P0** | **XL** | F10, F12 | yangi | ① har public masalada ≥5 yashirin test ② `print('3 2 1')` AC OLMAYDI (regressiya) ③ 0 masala IE qaytarmaydi ④ import har masalani validatsiya qiladi ⑤ testdata faqat judge quvuri orqali |
| **F10** | TestCase import + validatsiya | kontent muharriri | 870 masala test yo‘q → IE, user “platforma buzilgan” deb o‘ylaydi | kontent sifati | **QISMAN** | **P0** | L | F09 | yangi | ① testsiz masala “tayyor emas” deb belgilanadi ② importda majburiy test validatsiyasi ③ 5 bo‘sh + 164 qisqa statement tuzatiladi ④ har import audit yozadi |
| **F11** | Checker tanlash (standard vs special) | yechuvchi, kontent | 200 ko‘p-javobli masala noto‘g‘ri checker | to‘g‘ri baholash | **QISMAN** | **P0** | M | F12 | yangi | ① ko‘p-javobli masalalar special/token checker ② checker turi metasida ③ 200 masala qayta tasniflanadi ④ regressiya testi |
| F12 | Go + nsjail judge | submit qiluvchi | kodni ishonchli baholash | platforma yadrosi | BOR | P3 | XL | — | 0 | ① 20 verdict ② limitlar ③ 71 test fayli ④ p50<5s/p95<15s o‘lchanadi |
| F13 | Python + isolate judge | — | ikkinchi dvigatel kerakmi? | zaxira/taqqoslash | QISMAN | P2 | L | F12 | 0 | ① saqlanadi yoki ADR bilan chiqariladi ② protokol.md’ga mos ③ qaror hujjatlashtirilgan |
| F14 | Submit oqimi + verdict yozuvi | yechuvchi | kod yuborish | asosiy harakat | BOR | P3 | M | F12 | 0 | ① submit→navbat→verdict→UI ② SSE/polling ③ audit yozuvi |
| F15 | Custom test / run | yechuvchi | lokal sinov | tez iteratsiya | BOR | P3 | S | F12 | 0 | ① custom input ② natija ③ rate limit |
| F16 | ACM contest + standings | ishtirokchi | bellashuv | raqobat | BOR | P3 | L | F12 | 0 | ① create/register/submit ② standings real-time ③ 110k ko‘ruvchi NFR hujjatlashtirilgan |
| F17 | Virtual + mirror contest | mashq qiluvchi | vaqtga bog‘liq mashq | doimiy amaliyot | BOR | P3 | M | F16 | 1–2 | ① virtual reytingga ta’sir qilmaydi ② mirror reytinglanmagan ③ natijalar saqlanadi |
| F18 | Duel 1v1 (Elo) | raqib izlovchi | shaxsiy bellashuv | engagement | BOR | P3 | M | F07 | 3 | ① 1v1 ② Elo yangilanadi ③ RatingHistory’ga |
| F19 | Arena (live timed rounds) | ishtirokchi | qisqa live raund | hayajon | BOR | P3 | L | F12 | 3 | ① vaqtli raund ② live standings ③ yakunda natija |
| F20 | Championship / tournament | ishtirokchi | ko‘p bosqichli turnir | yuqori raqobat | BOR | P3 | L | F16 | 3 | ① bosqichlar ② umumiy standings ③ nishonlar |
| F21 | Hackathon + contest-hack | ishtirokchi | loyiha + raqib kodini buzish | xilma-xil format | BOR | P3 | L | F12 | 3 | ① submission+judging ② contest-hack lock ③ ADR-0020/0021’ga mos |
| F22 | Contest kalendari + sertifikatlar | ishtirokchi | rejalashtirish + dalil | reach, motivatsiya | BOR | P3 | M | F16 | 3 | ① kalendar ② sertifikat QR+PDF ③ tekshiriladigan havola |

## 4.3 Learning

| ID | Feature | User | Problem | Value | Holat | P | CX | Dep | Phase | Acceptance criteria |
|---|---|---|---|---|---|---|---|---|---|---|
| F23 | Maqola + ArticleProblemLink | o‘quvchi | nazariya+amaliyot bog‘lanishi | tuzilgan o‘rganish | BOR | P3 | M | F58 | 2 | ① maqola CRUD ② maqola↔masala ③ o‘qish taraqqiyoti |
| F24 | Roadmap + RoadmapStep | o‘quvchi | ketma-ketlik yo‘q | yo‘naltirilgan o‘rganish | BOR | P3 | M | F23 | 2 | ① qadamlar ② progress ③ tavsiyalar bilan bog‘liq |
| F25 | MCQ quizlar | o‘quvchi | tez bilim tekshiruvi | arzon mashq | QISMAN | P2 | M | F23 | 2 | ① quiz yaratish/echish ② natija saqlanadi ③ qolgan scope |
| F26 | Editorial + spoiler gate | yechuvchi | yechimni oldindan ko‘rish | halol o‘rganish | BOR | P2 | S | F23 | 2 | ① spoiler bilan yashirin ② ochish sharti ③ i18n |
| F27 | Problem tavsiya | yechuvchi | keyingi masala tanlash | uzluksiz o‘rganish | BOR | P2 | M | F07 | 1 | ① daraja/mavzuga mos ② moslashadi ③ AI varianti F42 |
| F28 | Algoritmlar ma’lumotnomasi | o‘quvchi | tez nazariy havola | mustaqil o‘rganish | BOR | P3 | S | — | 3 | ① algoritm sahifalari ② qidiruv ③ i18n |
| F29 | O‘quv kontent lokalizatsiyasi | o‘zbek bo‘lmagan o‘quvchi | 145 mavzu faqat uz/ru/en → 7 til o‘zbekcha | reach | **QISMAN** | **P1** | L | F04 | yangi | ① mavzu nomlari 10 tilda ② maqola/roadmap tarjimasi ③ tarjima yo‘qligida uz fallback (soxta tarjima emas) |

## 4.4 Social / Community

| ID | Feature | User | Problem | Value | Holat | P | CX | Dep | Phase | Acceptance criteria |
|---|---|---|---|---|---|---|---|---|---|---|
| F30 | Blog / news | hamjamiyat | yangiliklar | engagement | BOR | P3 | S | F58 | 1 | ① post CRUD ② ro‘yxat ③ i18n |
| F31 | Bildirishnomalar | barcha | hodisalardan xabarsiz | qaytish | BOR | P3 | M | — | 1 | ① in-app ② o‘qildi belgisi ③ kanal sozlamalari |
| F32 | Profil + reyting ko‘rinishi | barcha | progressni ko‘rsatish | identity | BOR | P3 | M | F07 | 0–3 | ① profil maydonlari (67, ADR-0024) ② 4 reyting ③ sozlamalar |
| F33 | Unvonlar / rollar / yutuqlar | faol yechuvchi | tan olinish | motivatsiya | BOR | P3 | M | F07 | 3 | ① unvon ② 16-daraja narvoni ③ yutuq bildirishnomasi |
| F34 | Kunlik quest + streak | kunlik yechuvchi | odat shakllantirish | retention | BOR | P3 | M | F06 | 1 | ① kunlik quest ② streak 7/30/365 ③ Qvant ledger orqali |
| F35 | Haftalik marafon | faol yechuvchi | haftalik maqsad | davriy qaytish | BOR | P3 | M | F16 | 1 | ① 10 masala ② haftalik natija ③ mukofot |
| F36 | Qvant shop | faol yechuvchi | Qvant sarflash | loop yopiladi | QISMAN | P2 | M | F06 | 1 | ① xarid ledger orqali ② 6 element ③ mavsumiy elementlar |
| F37 | Global leaderboard | barcha | umumiy o‘rin ko‘rinmaydi | raqobat | **UNKNOWN** | P2 | M | F07 | yangi | ① reyting bo‘yicha global jadval ② filtr ③ keshlash — *mavjudligi kod bo‘yicha aniqlanmagan (OPEN QUESTION)* |

## 4.5 AI (hammasi YO‘Q — Deep Research 8 yo‘nalishi)

> **Global AI cheklovlari (F38–F45 uchun majburiy):** practice’da AI ruxsat; **contest rejimida AI texnik jihatdan o‘chirilgan**; judge deterministik va izolyatsiyalangan qoladi; AI **hech qachon** judge host’ga, testdata bucket’ga yoki DB’ga to‘g‘ridan-to‘g‘ri tegmaydi — faqat ruxsat-cheklangan interfeys; har bir anti-cheat flag **inson ko‘rigini** talab qiladi; har bir AI xususiyati qurilishdan **OLDIN** metrikaga ega bo‘lishi shart.

| ID | Feature | User | Problem | Value | Holat | P | CX | Dep | Phase | Acceptance criteria |
|---|---|---|---|---|---|---|---|---|---|---|
| F38 | AI Feedback (WA/TLE sababi) | practice yechuvchi | nima uchun WA/TLE tushunarsiz | tez o‘rganish | **YO‘Q** | P2 | L | ruxsat-cheklangan AI interfeysi, F12 | yangi | ① faqat practice ② o‘zbek tilida sabab ③ contest’da o‘chirilgan (majburan) ④ metrika: qayta submit muvaffaqiyati ⑤ judge’ga tegmaydi |
| F39 | AI Mentor (suhbatdosh repetitor) | o‘quvchi | yo‘naltiruvchi yo‘q | shaxsiylashtirilgan yordam | **YO‘Q** | P2 | XL | F38 | yangi | ① practice’da suhbat ② contest’da o‘chirilgan ③ metrika: sessiya→AC konversiyasi ④ DB’ga to‘g‘ridan-to‘g‘ri yozmaydi |
| F40 | AI tarjima (10 til) | o‘zbek bo‘lmagan user | statik i18n; tarjima API yo‘q | reach | **YO‘Q** | P2 | L | F04 | yangi | ① 10 til ② inson tasdiqlash qadami ③ metrika: tarjima ulushi ④ manba matnga tegilmaydi |
| F41 | AI anti-cheat (plagiarism + AI-kod) | contest tashkilotchisi | halollik | adolat | **YO‘Q** | **P1** | XL | F16, inson ko‘rigi oqimi | yangi | ① plagiarism + AI-kod flagi ② **har flag inson ko‘rigini talab qiladi** ③ FP stavkasi o‘lchanadi ④ metric: inson tasdiqlagan aniqlik |
| F42 | AI tavsiya | yechuvchi | qoidaga asoslangan tavsiya (F27) yetarli emas | moslashuvchan o‘rganish | **YO‘Q** | P2 | L | F27, AI interfeysi | yangi | ① shaxsiy tavsiya ② metrika: tavsiya→yechish ③ F27 bilan A/B |
| F43 | AI problem / test generatsiya | kontent jamoasi | F09 inqiroziga test yetishmaydi | kontent miqyosi | **YO‘Q** | **P1** | XL | F09, F10 | yangi | ① generatsiya inson tekshiruvidan o‘tadi ② testdata’ga faqat cheklangan interfeys ③ metrika: rad etish darajasi ④ judge’ga tegmaydi |
| F44 | AI o‘qituvchi vositalari | o‘qituvchi | topshiriq tayyorlash vaqti | B2B unumdorlik | **YO‘Q** | P2 | L | F46 | yangi | ① topshiriq qoralamasi ② metrika: vaqt tejamkorligi ③ inson tasdiqlaydi |
| F45 | AI editorial yordam | kontent muharriri | editorial yozish sekin | kontent tezligi | **YO‘Q** | P2 | L | F26 | yangi | ① qoralama ② inson tahriri majburiy ③ spoiler gate bilan mos ④ metrika: qoralama→nashr vaqti |

## 4.6 Teacher / B2B

| ID | Feature | User | Problem | Value | Holat | P | CX | Dep | Phase | Acceptance criteria |
|---|---|---|---|---|---|---|---|---|---|---|
| F46 | Classroom (sinf/a’zolik/topshiriq/progress) | o‘qituvchi, o‘quvchi | sinf boshqaruvi | B2B asos | BOR | P2 | L | F01 | 2 | ① sinf ② topshiriq ③ progress ④ testlar qo‘shiladi (hozir yo‘q) |
| F47 | O‘qituvchi dashboard | o‘qituvchi | sinf holati bir joyda | tezkor qaror | QISMAN | P2 | M | F46 | 2 | ① o‘quvchilar + holat ② topshiriq holati ③ filtrlar |
| **F48** | Obuna narxlash | maktab/markaz | monetizatsiya modeli yo‘q | daromad | **YO‘Q** | **P1** | L | narxlash ADR (**BLOK**) | 2–3 BLOK | ① narxlash ADR tasdiqlanadi ② reja/tarif ③ to‘lov oqimi (real pul) ④ Qvant’dan AJRATILGAN |
| F49 | Ommaviy o‘quvchi onboarding | o‘qituvchi | 30 o‘quvchini birma-bir qo‘shish | B2B tez joriy etish | **YO‘Q** | P2 | M | F46 | yangi | ① CSV/ro‘yxat import ② bir martalik havola ③ 30 o‘quvchi <5 daqiqada |
| F50 | O‘qituvchi analitikasi | o‘qituvchi | kim qayerda qolgani noma’lum | maqsadli aralashuv | **YO‘Q** | P2 | M | F47, F56 | yangi | ① o‘quvchi/mavzu bo‘yicha bo‘shliq ② eksport ③ metrika: aralashuv samarasi |
| F51 | Institutsional billing | maktab ma’muriyati | hisob-faktura yo‘q | B2B savdo | **YO‘Q** | P2 | M | F48 | yangi | ① hisob-faktura ② licenziya ③ to‘lov tarixi |
| F52 | Assignment auto-grading | o‘qituvchi | qo‘lda baholash | vaqt tejash | QISMAN | P2 | M | F46, F12 | 2 | ① avtomatik baholash ② ball o‘qituvchiga ③ qo‘lda tuzatish |

## 4.7 Analytics

| ID | Feature | User | Problem | Value | Holat | P | CX | Dep | Phase | Acceptance criteria |
|---|---|---|---|---|---|---|---|---|---|---|
| F53 | Mahsulot analitikasi + funnel | mahsulot jamoasi | 0 real user, funnel yo‘q | qarorlar ma’lumotga asoslanadi | **YO‘Q** | **P1** | L | — | yangi | ① signup→first submit→first AC ② har qadam instrumentatsiya ③ dashboard |
| F54 | Haqiqiy foydalanuvchi telemetriyasi | mahsulot jamoasi | 384 569 attempt’dan faqat 1 tasi haqiqiy | real xulq | **YO‘Q** | **P1** | M | F53 | yangi | ① real vs seeded ajratiladi ② sessiyalar kuzatiladi ③ maxfiylik siyosatiga mos |
| F55 | Judge / queue metrikalari | ops | SLO uchun o‘tadigan raqam YO‘Q | ishlash ko‘rinishi | QISMAN | **P1** | M | F12 | yangi | ① navbat/latency metrikasi ② gate skript o‘tadigan raqam qayd etadi ③ 2.4→8.0 subs/s kuzatiladi |
| F56 | O‘rganish taraqqiyoti analitikasi | o‘quvchi, o‘qituvchi | progress ko‘rinmaydi | motivatsiya + aralashuv | QISMAN | P2 | M | F07, F24 | yangi | ① mavzu/daraja bo‘yicha taraqqiyot ② vaqt grafigi ③ o‘qituvchiga eksport |
| F57 | Biznes metrikalar dashboard | egasi | daromad/faollik ko‘rinmaydi | strategik qaror | **YO‘Q** | P2 | M | F48, F53 | yangi | ① MRR, B2B hisoblar, retention ② yagona joy ③ davriy hisobot |

## 4.8 Administration

| ID | Feature | User | Problem | Value | Holat | P | CX | Dep | Phase | Acceptance criteria |
|---|---|---|---|---|---|---|---|---|---|---|
| F58 | Admin UI (21 bo‘lim) | admin/staff | operatsion boshqaruv | kontent/ops | BOR | P3 | L | F01 | 3 | ① 21 bo‘lim ② ruxsatga ko‘ra ③ audit yozuvi |
| F59 | Staff guruhlar + object ownership | staff | rol ajratmasi | xavfsiz operatsiya | BOR | P3 | M | F58 | 3 | ① 3 guruh ② obyekt egaligi ③ ruxsatlar |
| F60 | Qvant audit vositasi | ops | ledger butunligi | moliyaviy ishonch | BOR | P3 | M | F06 | 1 | ① to‘liq audit ② nomuvofiqlik hisoboti ③ avtomatik |
| F61 | Kontent moderatsiya vositalari | content staff | sifatsiz kontentni topish | kontent sifati | QISMAN | **P1** | M | F58, F09 | yangi | ① testsiz/bo‘sh masalalar ro‘yxati ② ommaviy tuzatish ③ sifat hisoboti |
| F62 | Feature flaglar | mahsulot jamoasi | fazali chiqarish nazorati | xavfsiz rollout | **YO‘Q**/UNKNOWN | P2 | M | — | yangi | ① flag bilan yoqish/o‘chirish ② faza oldidan UI’da ko‘rinmasligi ③ audit |
| F63 | Audit log | ops/xavfsizlik | kim nima qildi | kuzatuvchanlik | QISMAN | P2 | M | F58 | yangi | ① sezgir amallar yoziladi ② filtr/qidiruv ③ saqlash muddati siyosati |

## 4.9 Infrastructure / Platform

| ID | Feature | User | Problem | Value | Holat | P | CX | Dep | Phase | Acceptance criteria |
|---|---|---|---|---|---|---|---|---|---|---|
| F64 | Monorepo + ADR jarayoni | injenerlar | kod tashkiloti | barqaror rivoj | BOR | P3 | M | — | 0 | ① monorepo ② ADR jarayoni ③ PR-only main |
| F65 | CI pipeline | injenerlar | sifat darvozasi | barqarorlik | QISMAN | **P1** | M | — | 0 | ① lint+mypy+test+OpenAPI+build ② security.yml qayta yoqiladi ③ gitleaks/pip-audit/npm audit majburiy ④ schema diff darvozasi |
| **F66** | Judge izolyatsiyasi (nsjail) | xavfsizlik | judge `privileged:true` + `cgroup:host` — ADR-0004’ga zid | xavfsizlik chegarasi | **QISMAN** | **P0** | L | F12 | yangi | ① `privileged:true` olib tashlanadi ② `cgroup:host` o‘rniga izolyatsiya ③ ADR-0004 bilan mos ④ user kodi host’dan chiqmaydi |
| **F67** | Staging muhiti | injenerlar | staging YO‘Q, docs/10 “staging deploy” deydi | xavfsiz reliz | **YO‘Q** | **P0** | L | F68 | yangi | ① alohida staging ② docs/10 ziddiyati tuzatiladi ③ reliz staging’da tekshiriladi |
| **F68** | Production 4-host topologiya | ops | deploy 1 mashina, “public preview”, production EMAS | ishlab chiqarishga tayyorlik | **YO‘Q** | **P0** | XL | F67 | yangi | ① 4-host topologiya ② rankwant.uz production deb belgilanadi ③ failover rejasi |
| **F69** | Backup + PITR | ops | backup oylik lokal; RPO ≤30 kun, PITR/failover yo‘q | ma’lumot yo‘qolmasligi | **QISMAN** | **P0** | M | F68 | yangi | ① kunlik avtomatik backup ② PITR ③ RPO ≤24 soat ④ restore testi avtomatik ⑤ off-site nusxa |
| F70 | Monitoring / Sentry | ops | Sentry yo‘q | hodisani erta aniqlash | **YO‘Q** | **P1** | M | F68 | yangi | ① xato kuzatuvi ② alerting ③ judge latency SLO ko‘rinadi |
| F71 | Standings CDN keshlash | tomoshabin | 110 000 tomoshabin/15s = 7 300 req/s, 330 MB/s | contest o‘tkazib yuborilmaydi | **YO‘Q** | **P1** | M | F16 | yangi | ① standings CDN orqali ② origin yuklamasi pasayadi ③ 7 300 req/s sinov |
| F72 | Judge gorizontal skalalash | ops | 8 worker=8.0/s; contest NFR 50/s → ~6–8 host kerak, bugun 1 | contest sig‘imi | **YO‘Q** | **P1** | L | F68, F12 | yangi | ① gorizontal masshtablash ② 50/s sinov ③ kompilyatsiya (830 ms/job) optimizatsiyasi |
| **F73** | Throttle / NAT sozlamasi | maktab labi | 60 req/min/IP; 20 parallel user → **94% 429** | maktab kompyuter sinfi ishlaydi | **QISMAN** | **P0** | M | — | yangi | ① throttle IP’ga emas, hisobga bog‘lanadi ② bitta NAT IP ortida 20+ user 429 OLMAYDI ③ sinf stsenariysi sinovdan o‘tadi ④ abuse himoyasi saqlanadi |
| **F74** | Sirlarni boshqarish | xavfsizlik | MinIO paroli `devdevdev` ochiq repoda | sir oshkor bo‘lmasligi | **QISMAN** | **P0** | M | F65 | yangi | ① sirlar env/secret manager orqali ② repoda 0 sir ③ `devdevdev` aylantiriladi ④ gitleaks CI’da majburiy |
| F75 | Email 4-provayder zanjiri | barcha | tranzaksion email | onboarding/retention | BOR | P3 | M | — | 1 | ① 4-provayder zanjiri ② brendlangan shablon ③ yetkazish kuzatuvi |
| F76 | On-call eskalatsiya | ops | bitta on-call, eskalatsiya yo‘q | uzilishni tez bartaraf etish | **YO‘Q** | **P1** | S | F70 | yangi | ① eskalatsiya zanjiri ② javob vaqti maqsadi ③ hodisa postmortemi |

**Katalog xulosasi:** 76 xususiyat — **BOR 34 · QISMAN 26 · YO‘Q 16** (1 UNKNOWN). Qolgan ish = QISMAN remediation (26) + YO‘Q (16).

---

# 05. Prioritization Matrix

## 5.1 Darajalar

| Daraja | Mezon | Xususiyatlar |
|---|---|---|
| **P0** | Product Foundation / Blocker — mahsulot ishonchsiz yoki ishlamaydigan bo‘lsa, qolgan hammasi ma’nosiz | F05, F09, F10, F11, F66, F67, F68, F69, F73, F74 |
| **P1** | Ishonch, reach yoki daromadga bevosita ta’sir; blokerni ochadi | F04, F29, F41, F43, F48, F53, F54, F55, F61, F65, F70, F71, F72, F76 |
| **P2** | Qiymat qo‘shadi, lekin P0/P1’siz ma’no bermaydi | F06, F13, F25, F26, F27, F36, F37, F38, F39, F40, F42, F44, F45, F46, F47, F49, F50, F51, F52, F56, F57, F62, F63 |
| **P3** | Allaqachon qurilgan (BOR) yoki past qoldiq ustuvorlik | F01–F03, F07, F08, F12, F14–F22, F23, F24, F28, F30–F35, F58, F59, F60, F64, F75 |

## 5.2 P0 ta’rifi — poydevor allaqachon qurilgan mahsulot uchun

An’anaviy CP platformasida P0 = “auth + judge”. RankWant’da **bu allaqachon BOR**. Shuning uchun bugungi P0 boshqacha: **kontent butunligi + ishlab chiqarishga tayyorlik + B2B throttle blokeri**. O‘lchangan dalil bilan:

1. **Kontent butunligi (F09–F11)** — 1 226 public masaladan **1 222’sida yashirin test yo‘q**; `print('3 2 1')` AC oldi. Ya’ni “judge bor” texnik jihatdan to‘g‘ri, lekin **amalda hech narsani baholamaydi**. Baholash yolg‘on bo‘lsa, reytinglar (F07), contest’lar (F16), sertifikatlar (F22) — hammasi yolg‘on.
2. **Ishlab chiqarishga tayyorlik (F66–F69, F74)** — `rankwant.uz` “public preview”; staging yo‘q; backup oylik lokal (RPO ≤30 kun, PITR yo‘q); judge `privileged:true`; MinIO paroli ochiq repoda. Real foydalanuvchi va B2B mijoz qabul qila olmaydigan holat.
3. **B2B throttle blokeri (F73)** — bitta NAT IP ortida 20 foydalanuvchi → **94% HTTP 429**. Maktab kompyuter sinfi — B2B ning asosiy xarid stsenariysi — bugun **ishlamaydi**. Shuning uchun F73 F48’dan **oldin**.

**Xulosa:** 10 P0’dan **7 tasi nuqson tuzatish**, 3 tasi yangi infratuzilma. Bu “qayta qurish” emas — **mavjud poydevorni ishonchli qilish**.

## 5.3 “Nega hozir / nega keyinroq?”

**P0**

| Feature | Nega hozir | Nega keyin emas |
|---|---|---|
| F09 Yashirin test | Busiz har AC/WA ma’nosiz; reyting va contest ishonchsiz | Mahsulotning yagona haqiqiy blokeri; hech narsa bundan oldin mazmunli emas |
| F10 Import/validatsiya | 870 masala IE qaytaradi — birinchi taassurot yo‘qoladi | F09 bilan bir epic, bir xil quvur |
| F11 Checker | 200 ko‘p-javobli masala noto‘g‘ri baholanadi | F09/F10 bilan bir to‘lqin |
| F05 Verdikt | 4 o‘lik kod ishonchni buzadi; hardcoded o‘zbekcha ru/en userni o‘chiradi | Judge BOR, lekin feedback sifati P0 darajadagi ishonch masalasi |
| F73 Throttle/NAT | 94% 429 B2B’ni butunlay bloklaydi; bitta sozlama o‘zgarishi | F48/F49/F51 B2B savdosi bundan keyin mantiqsiz |
| F66 Judge izolyatsiya | `privileged:true`+`cgroup:host` xavfsizlik chegarasini buzadi | Xavfsizlik P0 |
| F67/F68 Staging + topology | Real trafikni qabul qilish uchun; docs/10 zid | F53/F54 real telemetriya production muhitini talab qiladi |
| F69 Backup/PITR | RPO ≤30 kun = ma’lumot yo‘qotish | B2B SLA buni talab qiladi |
| F74 Sirlar | `devdevdev` ochiq repoda; 0 xarajat bilan tuzatiladi | Uyat xavfi |

**P1**

| Feature | Nega hozir | Nega keyin emas / shart |
|---|---|---|
| F48 Obuna narxlash | Monetizatsiya yo‘q; daromadsiz mahsulot yashamaydi | Narxlash ADR bloklangan → avval ADR. **Shart:** F73 bajarilgan |
| F53/F54 Analitika + telemetriya | 0 real user, funnel yo‘q; qarorlar ko‘r | F67/F68 keyin eng ko‘p ma’no beradi |
| F41 AI anti-cheat | Contest halolligi; AI-kod davrida flag kerak | Contest BOR, lekin anti-cheat yo‘q — ishonch xavfi. **Shart:** inson ko‘rigi oqimi |
| F43 AI test generatsiya | F09 inqiroziga miqyosli yechim | F09/F10 quvurisiz generatsiya yozadigan joy yo‘q |
| F55 Judge metrikalari | SLO uchun o‘tadigan raqam yo‘q; skript bor | F68 keyin. Arzon |
| F61 Kontent moderatsiya | F09/F10 inqirozini doimiy ushlab turish | Bir martalik tuzatishdan keyin barqarorlik |
| F65 CI security | security.yml o‘chirilgan — auditlar ishlamaydi | F74 bilan birga |
| F70/F76 Monitoring + on-call | Hodisani ko‘rish va eskalatsiya yo‘q | F68 keyin |
| F71/F72 Standings CDN + judge scale | Contest NFR (50/s, 7 300 req/s) bugun bajarilmaydi | Yirik contest rejalashtirilganda; lekin arzon tayyorgarlik |
| F04/F29 i18n | Reach — global nom, 10 til va’da qilingan | Kontent inqirozi avvalroq |

## 5.4 QISMAN remediation (qurilgan, lekin nuqsonli)

Bu xususiyatlar **yangi xususiyatlar bilan bir xil imkoniyat uchun raqobat qiladi** — byudjet rejasida hisobga olinishi shart.

| Xususiyat | Nuqson (dalil) | Remediation | P |
|---|---|---|---|
| F09 Yashirin test | 1 222/1 226 testsiz; `print('3 2 1')`=AC | Test quvuri + validatsiya | **P0** |
| F10 Import | 870 masala IE; 5 bo‘sh, 164 qisqa | Import validatsiyasi | **P0** |
| F11 Checker | 200 masala noto‘g‘ri checker | Qayta tasniflash | **P0** |
| F05 Verdikt | 4 o‘lik kod; hardcoded yorliqlar | Kod + i18n | **P0** |
| F66 Judge izolyatsiya | `privileged:true`+`cgroup:host` | Izolyatsiya | **P0** |
| F74 Sirlar | `devdevdev` ochiq repoda | Secret manager | **P0** |
| F73 Throttle | 94% 429 | Hisobga bog‘lash | **P0** |
| F69 Backup | Oylik lokal, PITR yo‘q | PITR + off-site | **P0** |
| F65 CI | security.yml `if:false` | Qayta yoqish | P1 |
| F55 Judge metrika | O‘tadigan SLO raqami yo‘q | Metrika | P1 |
| F04 i18n | 16 nom, 145 mavzu, kaa/ky/tg | To‘ldirish | P1 |
| F29 Kontent i18n | 7 til o‘zbekcha | Tarjima | P1 |
| F61 Moderatsiya | Qisman | To‘ldirish | P1 |
| F25 Quiz | Scope bir qismi bajarilmagan | Yakunlash | P2 |
| F36 Qvant shop | Mavsumiy yo‘q | Kengaytirish | P2 |
| F47 Teacher dashboard | Qisman | To‘ldirish | P2 |
| F52 Auto-grading | Qisman | To‘ldirish | P2 |
| F56 O‘rganish analitikasi | Qisman | To‘ldirish | P2 |
| F63 Audit log | Qisman | To‘ldirish | P2 |
| F13 Python judge | Bake-off nomzod | ADR qarori | P2 |
| F46 Classroom | Testlar yo‘q | Testlar | P2 |
| F37 Global leaderboard | UNKNOWN | Aniqlash | P2 |

## 5.5 “P0 emas, lekin eng ko‘p so‘raladigan”

- **F39 AI Mentor** — eng ko‘p so‘raladigan AI xususiyati. **Nega P0 emas:** (a) u F38 AI Feedback’ga tayanadi, u esa ruxsat-cheklangan interfeys va metrika talab qiladi; (b) qiymati **to‘g‘ri baholashga** bog‘liq — F09/F10/F11 tuzatilmaguncha mentor “WA sababini” **noto‘g‘ri testga asoslab** aytadi; (c) XL murakkablik P0 resursini tortib oladi. → P2’da ushlab turish.
- **F40 AI tarjima** — jozibali, lekin i18n (F04) statik va kontent inqirozi (F09) ustuvor. P2.
- **F37 Global leaderboard** — contest standings allaqachon BOR; global jadval F07’ga tayanadi va F09 tuzatilmaguncha **yolg‘on reytingni** ko‘rsatadi. P2.
- **F42 AI tavsiya** — F27 (qoidaga asoslangan) BOR; AI varianti “yaxshiroq” bo‘lishi isbotlanmagan. P2.

---

# 06. Core User Journey Map

Holat: **BOR** / **QISMAN** / **YO‘Q**

## J1 · Masala yechish (flagship loop)

| Qadam | Maqsad | System response (as built) | Edge case | Keyingi action | Holat |
|---|---|---|---|---|---|
| Masala topish | Mos masala | Problem bank, search, filter | 5 bo‘sh statement; 164 <100 belgi | Ochish | BOR |
| Ochish | Shartni o‘qish | Problem page | 7 tilda faqat uz (145 mavzu) | Tushunish | BOR |
| Tushunish | Misollarni ko‘rish | Statement + samples | Yashirin test yo‘q → faqat sample | O‘ylash | QISMAN |
| O‘ylash | Yechim izlash | — (mahsulot yordami yo‘q) | — | Kod yozish | YO‘Q |
| Kod yozish | Kod yozish | Submit code (in-browser editor: **UNKNOWN**) | — | Submit | YO‘Q/UNKNOWN |
| Submit | Javob yuborish | judge submit (20 verdict; p50<5s/p95<15s) | Queue (1 worker=2.4/s); 429 `RATE_LIMITED` tarixga yozilmaydi | Judge | BOR |
| Judge → verdict | Natija olish | 20 verdict | Test yo‘q→IE; yashirin test yo‘q→**false AC** | Xatoni tushunish | BOR (ishonchsiz) |
| **Xatoni tushunish** | Nimadan xato? | — **mahsulot yordami YO‘Q** | Faqat hardcoded uz verdict label | Yaxshilash | **YO‘Q — eng katta bo‘shliq** |
| Yaxshilash / qayta submit | Tuzatish | Resubmit | 429 tarixda yo‘q | Yechish | BOR |
| Yechish (AC) | Masala yopish | AC | false AC xavfi | Progress | BOR |
| Progress kuzatish | O‘sishni ko‘rish | Profile, Skills/Contests rating | Tier nomlari 6+ tilda tarjimasiz | Keyingi masala | BOR |

**Insight:** “Xatoni tushunish” — yagona **YO‘Q** qadam va eng katta unmet ehtiyoj; u **yo‘q AI feedback**ga bevosita bog‘liq.

## J2 · Reytingli contest

| Qadam | Maqsad | System response | Edge case | Keyingi action | Holat |
|---|---|---|---|---|---|
| Contest topish | Tadbirni topish | Contest list + calendar | — | Register | BOR |
| Register | Ro‘yxatdan o‘tish | Contest registration | register→participation >60% nishon | Ishtirok | BOR |
| Ishtirok | Yechish | Live round, submit | 429; queue | Standings | BOR |
| Standings | O‘rnimni ko‘rish | Standings, polling | 110k viewer/15s = 7 300 req/s → **CDN majburiy** | Reyting | BOR (load riski) |
| Rating o‘zgarishi | Yangi reyting | Contests rating yangilanadi | — | Formulani tushunish | BOR |
| Formulani tushunish | Nega shunday? | Formula ochiq (ADR-0006) | — | Sertifikat | BOR |
| Sertifikat | Natija hujjati | QR + PDF (ADR-0019) | — | — | BOR |

## J3 · Learning path

| Qadam | Maqsad | System response | Edge case | Keyingi action | Holat |
|---|---|---|---|---|---|
| Maqola/roadmap topish | O‘rganish | articles + roadmaps | — | O‘qish | BOR |
| O‘qish | Bilim olish | Content page | kaa/ky/tg ICU yo‘q → sana uz fallback | Masalaga o‘tish | BOR |
| Bog‘langan masala | Amaliyot | linked problem | — | Yechish | BOR |
| Yechish | Qo‘llash | judge | Yashirin test yo‘q (J1) | Maqolaga qaytish | BOR |
| Maqolaga qaytish | Mustahkamlash | — | Progress orqaga bog‘lanmagan | — | QISMAN |

## J4 · O‘qituvchi / sinf — **NAT/429 bilan bloklangan**

| Qadam | Maqsad | System response | Edge case | Keyingi action | Holat |
|---|---|---|---|---|---|
| Sinf yaratish | Sinf ochish | classroom | — | Taklif | BOR |
| O‘quvchilarni taklif | Qo‘shish | invite | **Lab bitta NAT IP → 94% 429** | Homework | **YO‘Q (funksional bloklangan)** |
| Homework berish | Vazifa tayinlash | assignments | — | Monitor | BOR |
| Progress kuzatish | Kim yechdi | monitor | — | — | BOR/QISMAN |
| Sinf piloti | Sinov | — | Hech qanday pilot yo‘q | — | YO‘Q |

## J5 · Motivatsiya loop

| Qadam | Maqsad | System response | Edge case | Keyingi action | Holat |
|---|---|---|---|---|---|
| Daily quest | Kunlik vazifa | quests | — | Streak | BOR |
| Streak | Uzluksizlik | streaks | — | Qvant | BOR |
| Qvant | Coin yig‘ish | wallet + ledger | — | Shop | BOR |
| Shop | Sarflash | 6 kosmetik item | Kengaytirish yo‘q | Ertaga qaytish | BOR |
| Ertaga qaytish | Odat | notifications | week-2 return >30% (misol) | — | BOR |

## J6 · Duel / arena / hackathon

| Qadam | Maqsad | System response | Edge case | Keyingi action | Holat |
|---|---|---|---|---|---|
| Matchmaking | Raqib topish | duels (1v1 Elo) | — | Live round | BOR |
| Live round | Jonli bellashuv | arena (timed rounds) | Load riski (J2) | Natija | BOR |
| Natija | Hisob | result + Challenges rating | — | Yana | BOR |
| Hackathon | Jamoa tadbiri | hackathon, hack-during-contest | — | — | BOR |

---

# 07. Feature Dependency Map

## 7.1 Bog‘liqlik zanjirlari

1. **Problem bank → tags/topics → user faolligi → skill model → recommendation.** Tavsiya yechilgan masala tegiga tayanadi; teg to‘liq bo‘lmasa skill model ham, tavsiya ham buziladi. (FACT: `recommendation` shipped; UNKNOWN: teg qamrovi o‘lchanmagan.)
2. **Yashirin test infratuzilmasi → ishonchli verdict → WAS → har qanday learning-progress metrikasi.** WAS = `verdict=AC` soni; yashirin test bo‘lmasa `print('3 2 1')` AC oladi → North Star **soxta**.
3. **Verdict taksonomiyasi (WRONG_TEST) → muallif tomonidagi triage → kontent sifati remediatsiyasi.** Test yo‘q masala hozir IE qaytaradi; WRONG_TEST bo‘lsa muallif “test yo‘q”ni boshqa sabablardan ajratadi.
4. **Submission → judge → submission history → AI feedback → AI mentor.**
5. **Auth → profile → submission.**
6. **Contest → standings → contest rating → certificates.**
7. **Classroom → assignment → progress → teacher analytics → B2B pricing.**
8. **Throttle/NAT fix → school lab usage → classroom adoption.** Bitta NAT IP ostida 94% 429 → laboratoriya ishlamaydi → maktab adopt qilmaydi.
9. **Staging → xavfsiz production deploy → 4-host topologiya → judge scale-out.**
10. **AI usage logging + eval harness → AI metrikasi → har qanday AI feature launch.** Metrikasiz ROI o‘lchanmaydi → “agent washing”.
11. **i18n kalitlari → content topics tarjimasi → to‘liq locale UI → uz’dan tashqari adoption.**
12. **Real-user instrumentation → funnel metrikalari → monetisation va AI ROI qarori.**

## 7.2 Critical path

```
BUGUN (shipped platforma: auth→judge→contest→classroom, 0 real user)
 ├─ TRUST TRUNK
 │   hidden-test infra → WRONG_TEST taksonomiya → kontent remediatsiya (870+ masala)
 │      → ishonchli verdict → ishonchli WAS
 ├─ PROD TRUNK
 │   staging → security hygiene (security.yml, MinIO secret, privileged judge)
 │      → 4-host topologiya → judge scale-out (6–8 host) → measured latency → external audit
 └─ INSTRUMENT TRUNK
     real-user funnel → AI eval harness skeleton → AI metrikalari
        │
 [TRUST] + [PROD] + [INSTRUMENT] → ishonchli, production-grade platform
        │
 AI feedback (practice-only, local) → AI mentor → translation → AI-assisted platform
```

**Critical path = TRUST TRUNK.** Sabab (INFERENCE): kontent remediatsiyasi **inson-bound** (870 testsiz + 1 222 yashirin-testsiz masala) — shuning uchun eng uzun zanjir. PROD/INSTRUMENT parallel boradi, lekin platforma “trustworthy” bo‘lmaguncha AI bosqichi boshlanmaydi. (ASSUMPTION: remediatsiya yuklamasi boshqa trunk’lardan kattaroq — author-throughput o‘lchovi kerak: UNKNOWN.)

## 7.3 Blocker jadvali

| Blocker | Nima bloklaydi | Yopish uchun nima kerak | Kim (role) |
|---|---|---|---|
| Throttle/NAT (60 req/min/IP, 94% 429) | School lab, Teacher/B2B, classroom adoption | Authenticated user-based throttle yoki school-IP allowlist; NAT-aware limit | Backend + DevOps/SRE |
| Kontent sifati (1 222 hidden test yo‘q; 870 test yo‘q) | Ishonchli WAS; practice surface; AI feedback uchun ground truth | Hidden-test generation pipeline + author review workflow + WRONG_TEST verdict | Content Ops + Judge/Backend |
| Staging yo‘q (docs/10 ziddiyati) | Xavfsiz deploy; 4-host topology sinovi | Staging muhiti (4-host kichigi), CI→staging→prod | DevOps/SRE |
| Measured judge-latency raqami yo‘q | Launch gate (p50<5s/p95<15s) yopilmaydi | Gate skriptni real yuk ostida ishga tushirib raqam yozish | Judge/Perf Engineer |
| Pricing ADR yo‘q | Subscription (P2-3) bloklangan; monetisation yo‘q | Pricing ADR + B2B pilot validatsiya | Product Director + Finance |
| AI eval harness yo‘q | Har qanday AI feature launch | Eval set + human-rating workflow + cost/latency tracking | AI Engineer + Data Analyst |
| security.yml o‘chirilgan; MinIO `devdevdev`; privileged judge | Xavfsizlik hygiene; external audit gate | CI re-enable; secret rotation; ADR-0004 moslashtirish | DevOps/SRE + Backend |
| `rankwant.uz` ro‘yxatdan o‘tmagan | Launch/brend; email `bugvector.uz`dan | Domen registratsiya | Ops + Legal |

## 7.4 Parallel lanes (kutmasdan birga boradi)

1. **Kontent integrity lane** (Content Ops) — hidden tests, WRONG_TEST, 200 checker, 5 bo‘sh + 164 qisqa statement.
2. **Infra/Production lane** (DevOps/SRE) — staging, 4-host, CDN/standings, monitoring, backup/DR.
3. **i18n lane** (Frontend + Content) — 16 tier nomi, 145 mavzu, kaa/ky/tg ICU.
4. **Verdict taxonomy lane** (Judge/Backend) — RE split, WRONG_TEST, 4 o‘lik kod, priority hujjati.
5. **Instrumentation lane** (Data Analyst + Backend) — funnel, analytics, content-quality dashboard.
6. **AI-prep lane** (AI Engineer) — eval harness skeleton, offline 7B sinovlari, MCP interfeys dizayni, zero-retention shartlari.

---

# 08. Product Roadmap (re-based)

**Nega re-base qilindi:** brifingdagi “Phase 0 Foundation, Phase 1 Core CP, Phase 2 Learning, Phase 4 Community, Phase 5 Teacher/B2B” — bularning aksari **allaqachon qurilgan** (19 Django app / 87 migratsiya / 2 judge / classroom+contest+duel+arena shipped). “Foundation qurish”dan boshlanadigan roadmap — fantastika. Shuning uchun roadmap **qolgan ishga**, ya’ni qiymat-yetkazishni bloklovchi narsalarga qayta qurildi.

**Majburiy assumption:** faza **davomiyligi baholanmaydi** — repo’da velocity yo‘q (`docs/09` “no estimates / no timeline axis” ochiq savoli); jamoa hajmi va throughput UNKNOWN. Shuning uchun **sequencing-only** roadmap + nisbiy hajm (S/M/L). Hafta yozish fabrikatsiya bo‘lardi.

| Phase | Maqsad | Asosiy funksiyalar | Dependency | Done Condition |
|---|---|---|---|---|
| **0 — Trust & Hardening** | Practice surface ishonchli bo‘ladi: yechilgan AC — haqiqiy AC. **Outcome:** North Star endi soxta bo‘lolmaydi | F09 hidden-test pipeline + author review; F10 import validatsiya; F11 checker; F05 WRONG_TEST/RE_SIGNAL/RE_EXIT + 4 o‘lik kod + i18n yorliqlar; F04/F29 i18n (16 tier, 145 mavzu, ICU); F55 measured judge latency; F67 staging; F66 judge izolyatsiya; F74 sirlar; F65 security.yml | Bugungi shipped platforma (FACT) | `print('3 2 1')` endi AC **OLMAYDI** (observable); 4 o‘lik kod yo‘q yoki hujjatlashtirilgan; judge latency p95 raqami **yozilgan**; staging’da deploy bo‘lgan; gitleaks/pip-audit/npm audit CI’da yashil. Hidden-test qamrov foizi — UNKNOWN (pipeline quvvati aniqlaydi) |
| **1 — Production & Scale** | Platforma real yuk ostida ishlaydi; launch gate’lar yopiladi. **Outcome:** `rankwant.uz` “preview”dan productionga o‘tadi | F68 4-host topology; F72 judge scale-out 6–8 host; F71 CDN/standings; F70 monitoring/Sentry; F69 backup/DR (PITR); external security audit; legal/licence review; F76 on-call eskalatsiya | P0 (staging, measured latency, hygiene) | 50 submissions/10s NFR **o‘lchangan holda** bajarilgan; standings 7 300 req/s CDN bilan; RPO/RTO raqamlangan; Sentry ishlaydi; external audit hisoboti yopilgan |
| **2 — Instrumentation & Analytics** | Real user xatti-harakati o‘lchanadi. **Outcome:** har keyingi qaror (AI, monetisation) ma’lumotga tayanadi | F53 product analytics/funnel; F54 real vs seeded; content-quality dashboard; AI eval harness skeleton; cost tracking; anti-cheat ground truth boshlanishi | P1 (production + real trafik) | register→first AC median, week-2 return, contest reg→participation **O‘LCHANADI**; funnel dashboard mavjud; eval set v1 mavjud (N — UNKNOWN); har AI feature uchun metrika aniqlangan |
| **3 — AI Practice Assistance** | Practice’da o‘quvchi tez, o‘zbekcha yordam oladi; contest toza qoladi. **Outcome:** qotib qolish kamayadi, retention o‘sadi | F38 local AI feedback MVP (WA/TLE, practice-only, contest’da OFF); F39 AI mentor; F40 10 tilga tarjima | P2 (eval harness + metrika); P0 (ishonchli verdict — feedback verdict’ga tayanadi) | FAR / HR / CPF / p95 latency raqamlangan va eval-set maqsadiga yetgan (maqsad raqamlari — UNKNOWN); contest rejimida AI endpoint **O‘CHIRILGAN** (observable); tarjima spot-check pass rate belgilangan |
| **4 — B2B & Monetisation** | Maktab laboratoriyalari ishlaydi; daromad modeli bor. **Outcome:** B2B pilot daromadga aylanadi | F73 NAT throttle fix; F46 classroom hardening + testlar; F48 pricing ADR + subscription; F49 ommaviy onboarding; F50 teacher analytics; F51 billing | P0 (throttle), P2 (funnel/analytics), P1 (scale) | Bitta NAT IP ostida 20 parallel user **429 OLMAYDI** (o‘lchangan); 5+ maktab pilot; pricing ADR qabul qilingan; subscription billing ishlaydi |
| **5 — AI Integrity & Content Scale** | Kontent miqyosi o‘sadi; anti-cheat inson nazorati bilan. **Outcome:** reyting adolati va kontent tezligi birga o‘sadi | F41 hybrid anti-cheat (har flag human review); F43 problem/test generation (editorial review); F45 editorial assistance; F44 teacher AI tools | P2 (ground truth, eval), P3 (AI infra), P0 (WRONG_TEST) | Anti-cheat precision/recall o‘lchangan; har AI flag inson ko‘rgan (observable); AI-generated problem faqat review’dan keyin publish (observable) |
| **6 — Advanced Platform** | Ekosistema va API orqali o‘sish. **Outcome:** tashqi integratsiya va mobile | Open API ecosystem; mobile (API orqali); advanced analytics; data asoslagan qolgan ishlar | P1–P5 | Ochiq API’da N tashqi integratsiya (N — UNKNOWN); mobile client API orqali ishlaydi; har yangi ish data bilan asoslangan |

**Nisbiy hajm:** P0 — **L** (inson-bound kontent; 870+ masala) · P1 — **M** · P2 — **M** · P3 — **M** (feedback MVP S bo‘lishi mumkin) · P4 — **M** · P5 — **L** · P6 — **S/M**.

**Roadmap’dan chiqarilgan ishlar**

| Chiqarilgan ish | Sabab | Qaytarish trigger |
|---|---|---|
| AI in-contest assistance | REPORT: “not fit”; integrity enforce qilinmaydi | Texnik enforcement isbotlangan (ehtimol hech qachon) |
| 32B self-hosted model | Bitta mashina feasibility **UNMEASURED** | Hardware o‘lchovi sig‘dirishini ko‘rsatsa |
| Autonomous grading / AI on judge host | Judge deterministik + izolyatsiya (ADR-0004) | Hech qachon |
| AI’ga to‘g‘ridan-to‘g‘ri DB/test-bucket access | Privacy/izolyatsiya | Permission-bounded MCP interfeys isbotlangan |
| AI-generated problem review’siz publish | Sifat/ishonch | Precision benchmark bajarilgan |
| Native mobile app | API stabillashmagan; WAS asossiz | API stable + WAS mobile’ni oqlasa |
| Qvant real-money value | ADR-0002 yopiq halqa | Legal review (ehtimol hech qachon) |
| Shop expansion | Monetisation/retention data yo‘q | P4 + retention data |

---

# 09. Product Backlog

> Tuzilma: **Epic → Feature → User Story → Acceptance Criteria.** Implementatsiya tafsilotlari (fayl/funksiya nomi) **yo‘q** — bu product backlog, engineering ticketlari emas.
> Format: “Rol sifatida … ni xohlayman, shunda …”.

## EPIC 1 — Content Integrity
**Feature 1.1 — Yashirin test quvuri.** *US:* Kontent muharriri sifatida men har bir masalaga yashirin test to‘plamini biriktirishni xohlayman, shunda baholash haqiqiy bo‘ladi.
- ① har public masalada ≥5 yashirin test ② testsiz masala “tayyor emas” deb belgilanadi ③ `print('3 2 1')` AC OLMAYDI ④ testdata faqat judge quvuri orqali yoziladi

**Feature 1.2 — Import validatsiyasi.** *US:* Muharrir sifatida men import qilishda testlar majburiy tekshirilishini xohlayman, shunda IE holati yo‘qoladi.
- ① 0 masala IE qaytarmaydi ② 5 bo‘sh + 164 qisqa statement tuzatiladi ③ har import audit yozadi

**Feature 1.3 — Checker to‘g‘riligi.** *US:* Kontent jamoasi sifatida men ko‘p-javobli masalalarga to‘g‘ri checker qo‘yilishini xohlayman, shunda noto‘g‘ri baho bo‘lmaydi.
- ① 200 masala qayta tasniflanadi ② checker turi metasida ko‘rinadi ③ regressiya testi

**Feature 1.4 — Verdict yaxlitligi.** *US:* Yechuvchi sifatida men faqat real verdict’larni ko‘rishni xohlayman, shunda feedback ishonchli bo‘ladi.
- ① 4 o‘lik kod yoziladi yoki o‘chiriladi ② yorliqlar 10 tilda ③ ustuvorlik tartibi hujjatlashtirilgan

## EPIC 2 — Production Readiness
**Feature 2.1 — Staging + production topologiyasi.** *US:* Ops sifatida men alohida staging va 4-host productionni xohlayman, shunda reliz xavfsiz bo‘ladi.
- ① staging mavjud ② `rankwant.uz` production deb belgilanadi ③ docs/10 ziddiyati tuzatiladi

**Feature 2.2 — Backup/PITR.** *US:* Ops sifatida men PITR va off-site backupni xohlayman, shunda RPO ≤24 soat bo‘ladi.
- ① kunlik avtomatik backup ② PITR yoqilgan ③ restore testi avtomatik

**Feature 2.3 — Judge izolyatsiyasi.** *US:* Xavfsizlik sifatida men judge’ning `privileged` bo‘lmasligini xohlayman, shunda izolyatsiya saqlanadi.
- ① `privileged:true` olib tashlanadi ② ADR-0004 bilan mos ③ user kodi host’dan chiqmaydi

**Feature 2.4 — Sirlar boshqaruvi.** *US:* Xavfsizlik sifatida men barcha sirlar secret manager’da bo‘lishini xohlayman, shunda repoda sir qolmaydi.
- ① 0 sir repoda ② `devdevdev` aylantiriladi ③ gitleaks CI’da majburiy

**Feature 2.5 — Monitoring + on-call.** *US:* Ops sifatida men xato kuzatuvi va eskalatsiyani xohlayman, shunda hodisa tez bartaraf etiladi.
- ① Sentry yoki ekvivalent ② eskalatsiya zanjiri ③ alerting ishlaydi

## EPIC 3 — Identity & Onboarding (mavjud yuza, faqat qoldiq)
**Feature 3.1 — Onboarding oqimi.** *US:* Yangi foydalanuvchi sifatida men bir necha qadamda hisob ochishni xohlayman, shunda tez boshlayman.
- ① 3 maydon bilan signup (BOR) ② Telegram kirish (BOR) ③ birinchi submitgacha yo‘l ko‘rsatiladi

**Feature 3.2 — Funnel instrumentatsiyasi.** *US:* Mahsulot jamoasi sifatida men onboarding funnelini ko‘rishni xohlayman, shunda to‘siqlarni topamiz.
- ① signup→first submit→first AC qadamlar ② har qadam instrumentatsiya ③ dashboard

## EPIC 4 — Problem Solving Core
**Feature 4.1 — Submit ishonchliligi.** *US:* Yechuvchi sifatida men to‘g‘ri verdict olishni xohlayman, shunda baho adolatli.
- ① 20 verdict to‘g‘ri ② limitlar ishlaydi ③ verdict testlari (MANDATORY)

**Feature 4.2 — Judge SLO metrikasi.** *US:* Ops sifatida men p50/p95 latency ko‘rishni xohlayman, shunda SLO kuzatiladi.
- ① p50<5s/p95<15s o‘lchanadi ② gate skript o‘tadigan raqam qayd etadi

**Feature 4.3 — Custom test.** *US:* Yechuvchi sifatida men o‘z testim bilan kod sinashni xohlayman, shunda tez iteratsiya qilaman.
- ① custom input ishlaydi ② rate limit qo‘llanadi ③ natija ko‘rinadi

## EPIC 5 — Contest & Competition
**Feature 5.1 — ACM contest + standings.** *US:* Ishtirokchi sifatida men real-time standings ko‘rishni xohlayman, shunda raqobatni kuzataman.
- ① contest create/register/submit ② standings SSE/polling ③ reyting sharti (≥10) qo‘llanadi

**Feature 5.2 — Contest sig‘imi.** *US:* Tashkilotchi sifatida men contest yuklamaga chidashini xohlayman, shunda katta contest o‘tkazaman.
- ① 50 submit/s sinovdan o‘tadi ② standings CDN orqali keshlanadi ③ 7 300 req/s sinov

**Feature 5.3 — Duel / Arena / Championship.** *US:* Faol yechuvchi sifatida men turli formatlarda bellashishni xohlayman, shunda qiziqarli bo‘ladi.
- ① duel Elo yangilanadi ② arena live ③ turnir bosqichlari + nishonlar

## EPIC 6 — Rating & Transparency
**Feature 6.1 — 4 reyting formulasi.** *US:* Yechuvchi sifatida men reytingim shaffof hisoblanishini xohlayman, shunda ishonaman.
- ① 4 formula testlar bilan (MANDATORY) ② har o‘zgarish RatingHistory’ga sabab bilan ③ to‘yinganlik hujjatlashtirilgan

**Feature 6.2 — Reyting ko‘rinishi.** *US:* Foydalanuvchi sifatida men reyting o‘zgarish tarixini ko‘rishni xohlayman, shunda sababini tushunaman.
- ① 4 reyting ko‘rinadi ② tarix sabab bilan ③ i18n

## EPIC 7 — Learning Content
**Feature 7.1 — Maqola + Roadmap.** *US:* O‘quvchi sifatida men tuzilgan roadmap bo‘ylab o‘qishni xohlayman, shunda izchil o‘rganaman.
- ① maqola↔masala bog‘lanishi ② roadmap progress ③ i18n

**Feature 7.2 — Editorial spoiler gate.** *US:* Yechuvchi sifatida men yechimni faqat urinib ko‘rgach ko‘rishni xohlayman, shunda halol o‘rganaman.
- ① spoiler yashirin ② ochish sharti ③ ADR-0013 bilan mos

**Feature 7.3 — Kontent lokalizatsiyasi.** *US:* O‘zbek bo‘lmagan o‘quvchi sifatida men kontentni o‘z tilimda ko‘rishni xohlayman, shunda o‘rgana olaman.
- ① mavzu nomlari 10 tilda ② tarjima yo‘q bo‘lsa uz fallback (soxta emas) ③ maqola/roadmap tarjimasi

## EPIC 8 — Teacher / B2B
**Feature 8.1 — Classroom.** *US:* O‘qituvchi sifatida men sinf yaratib topshiriq berishni xohlayman, shunda o‘quvchilarni boshqaraman.
- ① sinf/a’zolik ② topshiriq ③ progress + testlar

**Feature 8.2 — Ommaviy onboarding.** *US:* O‘qituvchi sifatida men 30 o‘quvchini bir yo‘la qo‘shishni xohlayman, shunda vaqt tejayman.
- ① ro‘yxat/CSV import ② bir martalik havola ③ 30 o‘quvchi <5 daqiqada

**Feature 8.3 — B2B throttle yechimi.** *US:* Maktab o‘qituvchisi sifatida men bir NAT IP orqasida butun sinf ishlashini xohlayman, shunda dars o‘tadi.
- ① 20+ foydalanuvchi bitta IP’da 429 OLMAYDI ② throttle hisobga bog‘lanadi ③ abuse himoyasi saqlanadi

**Feature 8.4 — Obuna narxlash.** *US:* Maktab ma’muriyati sifatida men obuna tarifini tanlashni xohlayman, shunda byudjetni rejalashtiraman.
- ① narxlash ADR tasdiqlanadi ② tarif tuzilmasi ③ Qvant’dan ajratilgan to‘lov oqimi

**Feature 8.5 — Billing.** *US:* Ma’muriyat sifatida men hisob-faktura olishni xohlayman, shunda buxgalteriya yuritiladi.
- ① hisob-faktura ② licenziya tarixi ③ to‘lov holati

## EPIC 9 — Qvant & Motivation
**Feature 9.1 — Ledger yaxlitligi.** *US:* Egasi sifatida men balans faqat ledger orqali o‘zgarishini xohlayman, shunda suiiste’mol bo‘lmaydi.
- ① balans to‘g‘ridan-to‘g‘ri yozilmaydi ② `qvant_audit` 0 nomuvofiqlik ③ kunlik cap 100

**Feature 9.2 — Quest / Streak / Marafon.** *US:* Faol yechuvchi sifatida men kunlik maqsadlar olishni xohlayman, shunda odat shakllanadi.
- ① kunlik quest ② streak 7/30/365 ③ haftalik marafon

**Feature 9.3 — Shop.** *US:* Faol yechuvchi sifatida men Qvant’ni sarflashni xohlayman, shunda rag‘bat bor.
- ① xarid ledger orqali ② kosmetik elementlar ③ mavsumiy kengaytma

## EPIC 10 — Analytics & Instrumentation
**Feature 10.1 — Funnel + telemetriya.** *US:* Mahsulot jamoasi sifatida men real foydalanuvchi funnelini ko‘rishni xohlayman, shunda qarorlar ma’lumotga asoslanadi.
- ① real vs seeded ajratiladi ② funnel qadamlar ③ maxfiylik siyosatiga mos

**Feature 10.2 — O‘rganish analitikasi.** *US:* O‘qituvchi sifatida men o‘quvchi bo‘shliqlarini ko‘rishni xohlayman, shunda aralashaman.
- ① mavzu bo‘yicha bo‘shliq ② eksport ③ o‘qituvchi dashboardi bilan bog‘liq

**Feature 10.3 — Biznes metrikalar.** *US:* Egasi sifatida men MRR va retention ko‘rishni xohlayman, shunda strategiya tanlayman.
- ① MRR/B2B hisoblar ② yagona dashboard ③ davriy hisobot

## EPIC 11 — AI Practice Assistance
**Feature 11.1 — AI Feedback.** *US:* Practice yechuvchi sifatida men WA/TLE sababini o‘zbekcha bilishni xohlayman, shunda tez o‘rganaman.
- ① faqat practice rejimida ② contest’da majburan o‘chirilgan ③ judge’ga tegmaydi ④ metrika oldindan belgilangan

**Feature 11.2 — AI Mentor.** *US:* O‘quvchi sifatida men suhbatdosh repetitor bilan mashq qilishni xohlayman, shunda yo‘naltirilaman.
- ① practice’da suhbat ② contest’da o‘chirilgan ③ DB’ga to‘g‘ridan-to‘g‘ri yozmaydi ④ metrika: sessiya→AC konversiyasi

**Feature 11.3 — AI tarjima.** *US:* O‘zbek bo‘lmagan foydalanuvchi sifatida men kontentni tarjima qilingan ko‘rishni xohlayman, shunda o‘qiyman.
- ① 10 til ② inson tasdiqlash qadami ③ manba matnga tegilmaydi

## EPIC 12 — AI Contest Integrity & Anti-cheat
**Feature 12.1 — Plagiarism / AI-kod aniqlash.** *US:* Contest tashkilotchisi sifatida men qoidabuzarlikni aniqlashni xohlayman, shunda adolat saqlanadi.
- ① plagiarism + AI-kod flagi ② **har flag inson ko‘rigini talab qiladi** ③ noto‘g‘ri pozitiv stavkasi o‘lchanadi

**Feature 12.2 — Contest rejimida AI nazorati.** *US:* Tashkilotchi sifatida men contest’da AI yordami texnik o‘chirilishini xohlayman, shunda halollik kafolatlanadi.
- ① contest rejimida AI interfeysi bloklangan ② majburiy amalga oshirilgan ③ audit yozuvi

**Feature 12.3 — Test generatsiyasi.** *US:* Kontent jamoasi sifatida men AI bilan test generatsiya qilishni xohlayman, shunda F09 inqirozini yopamiz.
- ① generatsiya inson tekshiruvidan o‘tadi ② testdata bucket’ga faqat cheklangan interfeys ③ rad etish darajasi o‘lchanadi

## EPIC 13 — i18n & Reach
**Feature 13.1 — i18n to‘liqligi.** *US:* Ru/en foydalanuvchi sifatida men barcha matnni o‘z tilimda ko‘rishni xohlayman, shunda tushunaman.
- ① 16 reyting nomi 10 tilda ② 145 mavzu nomi 10 tilda ③ kaa/ky/tg ICU’ga qo‘shiladi ④ 0 fallback

**Feature 13.2 — Verdict yorliqlari i18n.** *US:* Foydalanuvchi sifatida men verdict yorliqlarini o‘z tilimda ko‘rishni xohlayman, shunda tushunaman.
- ① hardcoded matn olib tashlanadi ② 10 til ③ regressiya testi

**Feature 13.3 — hreflang qarori.** *US:* Mahsulot jamoasi sifatida men til URL strategiyasi bo‘yicha qarorni xohlayman, shunda SEO izchil bo‘ladi.
- ① ADR yoziladi ② hreflang yoqiladi yoki rad etiladi (asos bilan)

## EPIC 14 — Admin & Operations
**Feature 14.1 — Kontent moderatsiya.** *US:* Content staff sifatida men sifatsiz kontentni topishni xohlayman, shunda sifatni ushlab turaman.
- ① testsiz/bo‘sh masalalar ro‘yxati ② ommaviy tuzatish ③ sifat hisoboti

**Feature 14.2 — Feature flaglar.** *US:* Mahsulot jamoasi sifatida men faza oldidan xususiyatni yashirishni xohlayman, shunda governance saqlanadi.
- ① flag bilan yoqish/o‘chirish ② faza oldidan UI’da ko‘rinmaydi ③ audit

**Feature 14.3 — Audit log.** *US:* Ops sifatida men sezgir amallar tarixini ko‘rishni xohlayman, shunda kuzatuvchanlik bor.
- ① sezgir amallar yoziladi ② filtr/qidiruv ③ saqlash siyosati

**Feature 14.4 — CI security darvozasi.** *US:* Injener sifatida men security.yml yoqilgan bo‘lishini xohlayman, shunda auditlar ishlaydi.
- ① security.yml qayta yoqiladi ② gitleaks/pip-audit/npm audit majburiy ③ PR bloklanadi buzilishda

---

# 10. AI Product Roadmap (alohida strategiya)

Hozir **AI umuman yo‘q** (FACT: grep bo‘yicha 0 LLM integratsiya; faqat `robots.ts` AI kraulerlarni bloklaydi — ADR-0023). Quyidagi har bir yo‘nalish uchun to‘liq zanjir.

## 10.1 Sakkiz yo‘nalish

**1) AI Feedback (WA/TLE izohi)**

| Maydon | Qiymat |
|---|---|
| Use case | WA/TLE sababini o‘zbekcha tushuntirish, practice-only |
| User value | Qotib qolish kamayadi; register→first AC tezlashadi |
| Required data | Submission kodi + verdict + statement (+ ideal: hidden-test diff) |
| Required infra | Local 7B inference (Qwen2.5-Coder-7B / Codestral-22B), queue, cache |
| Dependency | P0 ishonchli verdict; P2 eval harness |
| Risk | Noto‘g‘ri tushuntirish (hallucination); cost |
| Privacy | User kodi modelga ketadi → **self-host** (IP riski) |
| Contest integrity | Contest’da **O‘CHIQ** |
| HITL | Sample audit + escalation |
| Phase | 3 |

**2) AI Mentor**

| Maydon | Qiymat |
|---|---|
| Use case | Ko‘p qadamli o‘quv suhbati, roadmap bo‘yicha |
| User value | Retention, week-2 return |
| Required data | Submission history, skill model, learning content |
| Required infra | Feedback MVP + dialogue state + eval |
| Dependency | P3 feedback; P2 skill-model instrumentatsiya |
| Risk | Dependency/plagiarism, cost |
| Privacy | Chat tarixi + kod |
| Contest integrity | **O‘CHIQ** |
| HITL | Moderation sampling |
| Phase | 3 (feedback’dan keyin) |

**3) Translation (10 til)**

| Maydon | Qiymat |
|---|---|
| Use case | 145 topic + statement’larni 10 tilga |
| User value | uz’dan tashqari locale’larda mahsulot ishlaydi |
| Required data | Source content, glossary, human reference |
| Required infra | Batch MT + human review; content CMS |
| Dependency | P0 i18n keys; P2 metrika |
| Risk | Noto‘g‘ri tarjima, terminology drift |
| Privacy | Content public → past risk |
| Contest integrity | Statement tarjimasi contest’dan **OLDIN**, live emas |
| HITL | Human spot-check (majburiy) |
| Phase | 3 |

**4) Anti-cheat**

| Maydon | Qiymat |
|---|---|
| Use case | Plagiarism / AI-code detection flag |
| User value | Reyting adolati |
| Required data | Submission corpus, ground-truth labels |
| Required infra | Hybrid (local embeddings), eval |
| Dependency | P2 ground truth; P5 |
| Risk | False positive → noto‘g‘ri ayblov |
| Privacy | Submission corpus (sezgir) |
| Contest integrity | Faqat **FLAG**; avtomatik diskvalifikatsiya yo‘q |
| HITL | **MAJBURIY** har flag uchun |
| Phase | 5 |

**5) Recommendation**

| Maydon | Qiymat |
|---|---|
| Use case | Keyingi masala tavsiyasi |
| User value | Progress, retention |
| Required data | Tags, skill model, activity |
| Required infra | Rule-based BOR; ML kerak bo‘lsa keyin |
| Dependency | P0 tags; P2 skill model |
| Risk | Past sifat tavsiya |
| Privacy | Past |
| Contest integrity | Ta’sir yo‘q |
| HITL | Shart emas |
| Phase | 2/3 (medium fit) |

**6) Problem/Test Generation**

| Maydon | Qiymat |
|---|---|
| Use case | Hidden test va yangi masala generatsiyasi |
| User value | Kontent miqyosi |
| Required data | Reference solution, statement |
| Required infra | Local model + sandbox validation |
| Dependency | P0 WRONG_TEST + pipeline |
| Risk | Noto‘g‘ri test → noto‘g‘ri verdict |
| Privacy | Past (muallif content) |
| Contest integrity | Yangi masala contest’dan **oldin** review |
| HITL | **MAJBURIY** editorial review |
| Phase | 5 |

**7) Teacher tools**

| Maydon | Qiymat |
|---|---|
| Use case | Teacher panel, progress analitikasi, masala generatsiyasi |
| User value | B2B qiymat |
| Required data | Classroom, assignment, progress |
| Required infra | Analytics + AI feedback qayta ishlatish |
| Dependency | P2 analytics; P4 classroom |
| Risk | Noto‘g‘ri analytics |
| Privacy | O‘quvchi (bolalar) ma’lumoti → **YUQORI** |
| Contest integrity | Ta’sir yo‘q |
| HITL | Teacher nazorati |
| Phase | 4/5 |

**8) Editorial assistance**

| Maydon | Qiymat |
|---|---|
| Use case | Statement/editorial yozishga yordam |
| User value | Kontent tezligi |
| Required data | Mavjud editorial, style guide |
| Required infra | Local model |
| Dependency | P2 |
| Risk | Noto‘g‘ri editorial |
| Privacy | Past |
| Contest integrity | Ta’sir yo‘q |
| HITL | Editorial review |
| Phase | 5 |

## 10.2 Deployment model qarori

| Yo‘nalish | Model | Sabab (cost + privacy) |
|---|---|---|
| AI Feedback | **Local** | Yuqori hajm + user kodi IP riski; per-call cloud qimmat |
| AI Mentor | **Hybrid** | Yuqori hajm local; cloud faqat explicit consent + zero-retention |
| Translation | **Hybrid/batch** | Content public → cloud (DPA + zero-retention) maqbul; sezgir qism local |
| Anti-cheat | **Local** | Sezgir korpus |
| Recommendation | **Local/classical** | LLM shart emas |
| Problem/Test Gen | **Local** | Muallif content + validation |
| Teacher tools | **Local** (feedback infra reuse) | Bolalar ma’lumoti → local afzal |
| Editorial | **Local** | Content, past risk |

**RECOMMENDATION:** REPORT taklifiga rioya — high-volume/repetitive → **local**; cloud faqat explicit consent + zero-retention. ⚠️ **OPEN QUESTION:** REPORT’ning hardware feasibility assumption’i — *bitta mashina production yuk ostida 7B modelni ko‘taradi* — **UNMEASURED**. Bu o‘lchovsiz P3’ga kirilmaydi. Cost (GPU amortizatsiya vs cloud) — **UNKNOWN**, eval harness o‘lchanadi.

## 10.3 Contest integrity qoidasi

**Qoida:** Practice — AI **ALLOWED**. Contest — AI assistance **DISABLED**.

**Bugun enforce qilinadigan (product-side):** contest vaqtida AI panelini UI’da o‘chirish; AI endpoint’ni disable qilish; barcha AI chaqiruvlarni log qilish; suspicious submission’ni human review uchun flag qilish.

**Enforce QILINMAYDIGAN:** foydalanuvchi boshqa oynada o‘z tashqi AI’sini ishlatishi. **Hech qachon bajarib bo‘lmaydigan integrity va’da bermang** — bu ochiq tan olinadi.

## 10.4 AI metrikasi va eval harness (har qanday AI’dan OLDIN)

| Metrika | Hisoblash |
|---|---|
| Eval set | Golden verdict + golden feedback bilan N masala (N — UNKNOWN) |
| Human-rating workflow | Har sample 2 reviewer baholaydi |
| **FAR** (Feedback Acceptance Rate) | “Foydali” deb baholangan feedback / ko‘rsatilgan feedback |
| **HR** (Hallucination Rate) | Faktual xato deb belgilangan / sample qilingan feedback |
| **CPF** (Cost per Feedback) | Jami inference xarajat / yetkazilgan feedback |
| p95 Feedback Latency | Submit→feedback render vaqtining p95’i |
| **AER** (Abstention/Escalation Rate) | AI rad etgan yoki insonga uzatgan / jami holat |
| Anti-cheat Precision/Recall | Tasdiqlangan flag / ko‘tarilgan flag; qamrab olingan / jami |
| Translation quality | Human spot-check pass rate + MQM/chrF |
| Contest Integrity Incident Rate | Tasdiqlangan in-contest qoidabuzarlik / contest |

## 10.5 AI qilmang

| Qilmang | Sabab | Qayta ko‘rish trigger |
|---|---|---|
| AI contest ichida | REPORT: not fit; enforce qilinmaydi | Enforceable integrity isboti |
| Autonomous grading | Judge deterministik | Hech qachon |
| Judge host’da AI | ADR-0004 izolyatsiya | Hech qachon |
| AI’ga to‘g‘ridan-to‘g‘ri DB/test-bucket access | Privacy/izolyatsiya | Permission-bounded MCP isboti |
| AI-generated problem review’siz publish | Sifat/ishonch | Precision benchmark |
| 32B self-hosted hozirgi bitta mashinada | Feasibility UNMEASURED | Hardware o‘lchovi |

---

# 11. Product Metrics

## 11.1 North Star va uning himoyasi

**North Star: Weekly Active Solver (WAS)** — [FACT, docs/02 locked]

```sql
SELECT COUNT(DISTINCT user_id)
FROM submissions
WHERE verdict = 'AC'
  AND created_at >= NOW() - INTERVAL '7 days'
  AND is_seeded = false;   -- real foydalanuvchini ajratish
```

**Nega WAS to‘g‘ri:** sifat bilan tuzatilgan (faqat AC); birinchi kundan o‘lchanadi (Skills rating bilan bir xil event’dan oziqlanadi); yadro loop’ni aks ettiradi.

**Ma’lum zaifliklari:** o‘yinlashtirsa bo‘ladi (bitta oson AC yetarli, difficulty pol yo‘q); **o‘rganishni o‘lchamaydi**; B2B haqida jim; **amalda hozir o‘lchanmaydi** (0 real user, DB to‘liq seeded; `is_seeded` ustuni mavjudligi tasdiqlanmagan → OPEN QUESTION).

**Secondary North Star nomzodlari (RECOMMENDATION):**
1. **Weekly Learning Advance (WLA)** — haftada skill rating oshgan YOKI avvalgi maksimal difficulty’dan yuqori masalada birinchi AC olgan userlar soni. WAS’ni “mavjudlik”dan “taraqqiyot”ga to‘ldiradi va “bitta oson AC” o‘yinini yopadi.
2. **Weekly Active Classroom (WAC)** — haftada ≥1 topshiriq yaratilgan va ≥1 o‘quvchi submit qilgan sinflar soni. B2B qiymatini aks ettiruvchi yagona metrika; 5+ maktab pilot maqsadiga bog‘lanadi. Hozir 0.

## 11.2 Metrika katalogi

### Learning

| Metrika | Ta’rif | Nega muhim | O‘lchash usuli | Baseline |
|---|---|---|---|---|
| WAS (North Star) | yuqoridagi SQL | yadro loop | submissions (real filtr) | 0 real; seeded: 106 557 AC / 384 569 attempt |
| WLA | haftada rating↑ yoki difficulty↑ birinchi AC | taraqqiyot | rating_history + difficulty | UNKNOWN (instrument kerak) |
| Register→first AC | median(first AC − register) | activation | users ⨝ submissions | maqsad <7 kun (ASSUMPTION); real UNKNOWN |
| Week-2 return | W’da ro‘yxatdan o‘tib W+1’da faol bo‘lganlar % | retention | event log | maqsad >30% (ASSUMPTION); UNKNOWN |
| Skills rating taqsimoti | rating gistogrammasi | difficulty kalibrovka | ratings | UNKNOWN |
| AC / active solver / hafta | total AC ÷ WAS | engagement chuqurligi | submissions | UNKNOWN |

### Platform / Engagement

| Metrika | Ta’rif | Nega muhim | O‘lchash | Baseline |
|---|---|---|---|---|
| DAU/WAU/MAU | distinct faol user | o‘sish | event log | 0 real |
| Activation rate | birinchi submit bajargan yangi user % | onboarding | event log | UNKNOWN |
| Session chuqurligi | session’da ko‘rilgan problem / submission | engagement | event log | UNKNOWN |
| Contest reg→participation | ro‘yxatdan o‘tib ≥1 submit qilganlar % | contest funnel | contest + submissions | maqsad >60% (ASSUMPTION); UNKNOWN |
| **NAT-throttle 429 rate** | bitta IP’dagi 429 ÷ so‘rovlar | B2B viability | load test + logs | **20 parallel user’dan 94% 429** |

### Judge & Reliability

| Metrika | Ta’rif | Nega muhim | O‘lchash | Baseline |
|---|---|---|---|---|
| Judge throughput | subs/s per worker | capacity | load test | 1w 2.4/s · 4w 5.4/s · 8w 8.0/s |
| Judge latency p50/p95 | submit→verdict | SLO | latency gate script | SLO p50<5s / p95<15s; bench p95 857–1360 ms; **passing raqam yozilmagan** |
| Contest burst capacity | contest’dagi subs/s | contest NFR | load test | NFR 50/s; ~6–8 host kerak; bugun 1 |
| API read throughput | req/s | scale | load test | 57 req/s @20 VU; /problems/ p95 23 ms; standings 38 ms; 0% xato |
| Standings serve | req/s | live contest | load test | origin ~130 req/s; kerak 7 300 req/s → CDN majburiy |
| Uptime / error budget | availability | SLO | monitoring | SLO 99.5% ≈3h39m budget; real UNKNOWN |
| Backup RPO/RTO | yo‘qotish oynasi | DR | ops | RPO ≤30 kun; RTO DB ~9s, servis 1–12h; failover/PITR yo‘q |

### Content Quality

| Metrika | Ta’rif | Nega muhim | Baseline |
|---|---|---|---|
| **Hidden-test coverage %** | ≥1 non-sample test’li public problem ÷ public problem | judge integrity | **4/1 226 = 0.33%** |
| IE-returning problems | testsiz problem soni | buzilgan UX | 870/~2 096 |
| Statement length dist. | <100 belgili / bo‘sh statement % | kontent sifati | 5 bo‘sh, 164 <100 belgi |
| Checker-type mismatch | ko‘p javobli, lekin checker=`standard` | noto‘g‘ri verdict | 200 |
| Solve-rate sanity | AC% >95% va N≥30 bo‘lgan problem | buzilgan problem | real data yo‘q; `print('3 2 1')`→AC |

### i18n / Reach

| Metrika | Ta’rif | Baseline |
|---|---|---|
| Locale coverage % | tarjima qilingan string ÷ jami (per locale) | 10 locale; 16 tier nomi 6+ locale’da tarjimasiz; 145 topic faqat uz/ru/en; kaa/ky/tg ICU’da yo‘q |
| Non-uz label leak | ru/en user’ga uz verdict ko‘rsatilishi | barcha verdict label hardcoded uz |

### Monetisation / B2B

| Metrika | Ta’rif | Baseline |
|---|---|---|
| Free→paid conversion | paid ÷ registered | bloklangan (pricing yo‘q) |
| ARPU / ARPPU | revenue ÷ user | UNKNOWN |
| B2B pilot maktablar | aktiv pilot maktab soni | maqsad 5+ (ASSUMPTION); 0 |
| Qvant quest completion | quest bajargan DAU % | maqsad 30%+ (ASSUMPTION); UNKNOWN |

### AI (bugun mavjud emas — hammasi UNKNOWN)

| Metrika | Ta’rif | O‘lchash usuli |
|---|---|---|
| Feedback usefulness | “foydali” deb baholangan feedback % | UI rating + **human eval harness** |
| Feedback acceptance | taklif qo‘llanilgani (edit-then-AC yoki “apply”) % | event |
| Repeat submission after feedback | feedback’dan keyin N daqiqada qayta submit session % | event |
| Hallucination rate | user kod/verdict haqida ≥1 xato da’vo bo‘lgan feedback % | human eval harness + ground truth |
| Feedback latency | submit→feedback p50/p95 | instrumentation |
| Cost per feedback | (GPU amortizatsiya + API) ÷ feedback soni | cost attribution |
| Escalation rate | insonga eskalatsiya/report qilingan session % | event |
| Anti-cheat false-positive | belgilangan-lekin begunoh ÷ belgilanganlar | labelled dataset + human review |

> ⚠️ Bugun **ground truth yo‘q**, shuning uchun barcha AI metrikalari **inson baholash workflow’i** (namuna + anotatsiya) bilan boshlanishi shart. REPORT’ning “agent washing” ogohlantirishiga amal qilib, metrika AI feature qurilishidan **oldin** qat’iy belgilanadi.

## 11.3 Content Quality metrikasi — yangi oila

| Metrika | Ta’rif | Joriy | Maqsad (RECOMMENDATION) |
|---|---|---|---|
| Hidden-test coverage % | (# public problem, ≥1 `is_sample=false`) ÷ (# public problem) × 100 | **0.33%** | har graded contest’dan oldin ≥95% |
| IE-returning problem rate | IE qaytargan problem ÷ problem | **870/~2 096** | 0 |
| Statement length dist. | statement uzunligi gistogrammasi; <100 belgi bayroqlanadi | **5 bo‘sh, 164 <100** | 0 |
| Checker-type mismatch | (>1 to‘g‘ri javobli, lekin checker=`standard`) | **200** | 0 |
| Solve-rate sanity | AC% = AC ÷ total; AC% >95% va N≥30 → **buzilgan problem** | real data yo‘q | monitoring |

## 11.4 O‘lchash bo‘shliqlari

- **Real-user analytics YO‘Q** → event pipeline kerak.
- **Funnel instrumentation YO‘Q** → aniq event’lar: register, first problem view, first submit, first AC, contest join.
- **Seeded/real ajratish YO‘Q** → `is_seeded` flag yoki cohort filtri kerak; busiz har metrika **ifloslangan**.
- **AI eval harness YO‘Q** → human-rating workflow + ground-truth label kerak.
- **Anti-cheat ground truth YO‘Q** → labelled plagiarism/AI-code dataset kerak.
- **Cost tracking YO‘Q** → GPU/API xarajat attributsiyasi kerak.
- **Staging YO‘Q** → pre-prod xatti-harakatni o‘lchab bo‘lmaydi.
- **Judge SLO passing raqami YO‘Q** → latency gate’ni ishga tushirib natijani yozish kerak.

## 11.5 Dashboard taklifi

**Haftalik product review (12 tile):** ① WAS (faqat real) ② yangi real registered (7d) ③ Register→first AC (median kun + %) ④ Week-2 return ⑤ Judge latency p50/p95 vs SLO ⑥ Judge throughput vs capacity (subs/s vs 50/s) ⑦ Hidden-test coverage % ⑧ IE-returning problems (son, trend) ⑨ Contest participation rate ⑩ i18n coverage % (per locale, minimum) ⑪ B2B aktiv pilot sinflar ⑫ Uptime / qolgan error budget.

**Alerts:** judge p95 > 15 s · error rate > 1% yoki 5xx spike · error budget burn · hidden-test coverage tushishi / testsiz yangi problem · bitta IP’dan 429 spike · cost per feedback > budget (AI live bo‘lgach) · hallucination rate > tolerance (AI live bo‘lgach).

---

# 12. Product Risks & Open Questions

## 12.1 Risk reyestri

| # | Xavf | I | E | Score | Mitigatsiya | Trigger | Metrika |
|---|---|---|---|---|---|---|---|
| 1 | **Kontent sifati**: 1 222/1 226 problemda hidden test yo‘q | 5 | 5 | **25** | Majburiy hidden-test gate; graded contest’ni bloklash | `print('3 2 1')`→AC; coverage <95% | Hidden-test coverage %; IE problems |
| 2 | **Cold start**: 0 user vs RoboContest 197k tarmoq effekti | 5 | 5 | **25** | Fokusli launch (B2B maktab + contest), nisha (UZ-first, Qvant) | WAS plateau; activation past | WAS; register→first AC |
| 3 | **Ma’lumot sifati**: seeded data, real analytics yo‘q | 4 | 5 | **20** | Event pipeline + `is_seeded` filtri; qarorlar faqat real data’ga | Har metrika seeded’dan oziqlansa | barcha metrikalar |
| 4 | **Production readiness**: 1 machine, staging yo‘q, RPO 30 kun, 1 on-call | 5 | 4 | **20** | Staging + failover + PITR + escalation chain; contest’dan oldin | Backup restore testi; incident’da 1 kishi | Uptime; RPO/RTO |
| 5 | **B2B NAT throttle**: bitta IP 60 req/min | 4 | 5 | **20** | B2B uchun account-based throttle yoki school-IP boost | Maktab lab’ida 429 | 429 rate; B2B pilot |
| 6 | **Xavfsizlik**: privileged judge, `devdevdev` MinIO paroli, o‘chirilgan security.yml | 5 | 4 | **20** | security.yml yoqish; sirni almashtirish; sandbox hardening | gitleaks/pip-audit ishlamasa; sir leak | audit log |
| 7 | **Key-person risk** (yagona owner) | 5 | 4 | **20** | Hujjatlashtirish (bor), bilim tarqatish, 2-kishi onboarding | Bus-factor = 1 | docs coverage; PR review |
| 8 | AI feedback sifati (uz feedback o‘lchanmagan) | 4 | 4 | 16 | Chiqishdan oldin human eval; sifatsiz bo‘lsa chiqarmaslik | Feedback usefulness < threshold | Feedback usefulness |
| 9 | AI hallucination | 4 | 4 | 16 | HITL; namuna review; ishonch past bo‘lsa “AI off” | Hallucination rate > tolerance | Hallucination rate |
| 10 | Contest fairness/integrity | 5 | 3 | 15 | Contest’da AI o‘chirish; deterministic judge; human review | Cheating flag spike | Anti-cheat FP rate |
| 11 | Privacy / user kod IP leakage (3rd-party model) | 5 | 3 | 15 | Hybrid (self-host); cloud faqat consent + zero-retention | 3rd-party API’ga kod yuborilsa | Cost/consent log |
| 12 | Monetisation yo‘q (pricing ADR bloklangan) | 4 | 4 | 16 | Pricing ADR + WTP tadqiqot | Uzoq bloklanish | Free→paid; ARPU |
| 13 | Judge capacity gap: kerak 6–8 host, bugun 1 | 4 | 4 | 16 | Avtomatik scale + queue; contest oldidan capacity test | Contest burst’da p95 spike | Judge throughput; latency |
| 14 | AI cost per feedback | 3 | 4 | 12 | Self-host high-volume; budget cap | Cost/feedback > budget | Cost per feedback |
| 15 | Platform complexity / overengineering | 3 | 4 | 12 | Scope freeze; ADR-first; refactor backlog | Velocitet pasayishi | Cycle time |
| 16 | Feature sprawl (3 phase, 19 app allaqachon) | 3 | 4 | 12 | Roadmap prioritizatsiya; “no new app” qoidasi | O‘lik/bo‘sh feature’lar | Feature usage % |
| 17 | i18n debt (10 locale, kaa/ky/tg to‘liq emas) | 3 | 4 | 12 | Locale prioritizatsiya (uz/ru/en to‘liq) | Non-uz label leak | Locale coverage % |
| 18 | Licence / legal (21 UNKNOWN paket, AGPL qochirilgan) | 3 | 3 | 9 | SBOM + licence review; enterprise’dan oldin | UNKNOWN paketlar soni | 21 UNKNOWN |

## 12.2 Top 5 risk

1. **Kontent sifati (25)** — yadro mahsulot buzuq: 1 226 dan 1 222’sida hidden test yo‘q va judge aldanishi **isbotlangan** (`print('3 2 1')`→AC). Judge ishonchsiz bo‘lsa, contest ham, rating ham, B2B ham mantiqsiz. Boshqalardan ustun, chunki bu **mavjud va o‘lchangan** inqiroz.
2. **Cold start (25)** — 0 real user, RoboContest’ning 197k tarmoq effekti bilan raqobat. Strategiya “UZ-first nisha + B2B maktab” bilan yopiladi, aks holda mahsulot mavjud emas.
3. **Ma’lumot sifati (20)** — qarorlar seeded data ustida qurilyapti; real analytics, funnel va AI eval harness yo‘q. Ko‘r holda uchish.
4. **Production readiness (20)** — 1 machine, staging yo‘q, RPO 30 kun, 1 on-call, failover yo‘q. **Real contest’ni ishonchli o‘tkaza olmaydi** — bu yadro use case.
5. **B2B NAT throttle (20)** — bitta NAT IP ortidagi maktab lab’i 429 oladi; bu **yagona monetizatsiya yo‘lini** (maktablar) o‘ldiradi.

*Yaqin kuzatuvda: xavfsizlik (20) va key-person (20) — ikkalasi ham 20, lekin tez tuzatiladi / governance masalasi.*

## 12.3 Risklarni qabul qilish

- **i18n debt** — qabul (kaa/ky/tg to‘liq emas); fokus uz/ru/en; scale’da qayta ko‘riladi.
- **Licence UNKNOWN (21)** — joriy ekspozitsiya past; enterprise’dan oldin yopiladi.
- **Feature sprawl / complexity** — qisman qabul; scope freeze bilan yumshatiladi.
- **Monetisation yo‘q** — qisqa muddatda qabul (pricing ADR bloklangan), chunki user ham yo‘q.
- **Single on-call / failover yo‘q** — joriy scale’da (0 user) qabul; real contest’dan **oldin** albatta tuzatiladi.
- **4 o‘lik verdict kod** — kosmetik, qabul.
- **Seeded data** — demo sifatida qabul; lekin metrikalardan **chiqarib tashlanishi shart**.

## 12.4 Ochiq savollar

| Savol | Nega muhim | Yopish uchun nima kerak | Kim javob beradi |
|---|---|---|---|
| **Qaysi segment primary?** (docs/01, docs/02’da hal qilinmagan) | Roadmap va metrika fokusini belgilaydi | Segment qaror workshop’i | Product Director + User Researcher |
| **Pricing model?** (pricing ADR bloklangan) | Monetizatsiya yo‘li yo‘q | Pricing ADR + WTP tadqiqot | Product Director + Finance |
| 5–10% weekly-active ratio realmi? | Barcha Y1–Y3 proyeksiya shunga tayanadi | Real user’lar paydo bo‘lgach o‘lchash | Data Analyst |
| hreflang / locale-in-URL? | SEO va reach | i18n/SEO ADR | Product Director + Eng |
| **Staging mavjudmi?** (docs/10 “staging deploy” deydi, lekin staging yo‘q) | Test va pre-prod xavfsizligi | Ops qaror + muhit yaratish | Eng/Ops |
| REPORT’ning local-model taxminlari bu hardware’da to‘g‘rimi? | AI arxitekturasi shunga tayanadi | 7B modelni bitta machine’da load ostida benchmark | Eng/AI |
| Anti-cheat false-positive tolerance? | Adolat vs friction | Threshold + human review workflow | Product + AI |
| Denormalised counter sync mexanizmi? (docs/05’da aniqlanmagan) | Ma’lumot izchilligi | ADR | Eng |
| Domain/handle registration? (`rankwant.uz` ro‘yxatdan o‘tmagan) | Brend va onboarding | Qaror | Product + Eng |
| Hidden-test remediation rejasi/prioriteti? | Kontent inqirozini yopish | Content backlog + gate | Content + Product |
| Judge SLO passing raqami? | SLO e’lon qilinmagan | latency gate’ni ishga tushirish | Eng |
| Seeded data prod metrikadan chiqariladimi? | Metrika tozaligi | `is_seeded` flag / filtr | Data + Eng |
| NAT throttle product qarori? | B2B segment viability | Product qaror | Product + Eng |
| AI metrikalari AI qurilishidan oldin belgilanadimi? | “Agent washing”ning oldini olish | Metrika qat’iylashtirish | Product + Data |
| `neytron_*` 10 001 seed foydalanuvchini o‘chirish? (ADR-0023 ochiq follow-up) | `/users/` indeksatsiyasi va crawl yuki | Backup + o‘chirish + `/users/` disallow’dan chiqarish | Ops + Eng |

---

# 13. Out of Scope (nima hozir qilmaymiz)

| Feature | Nega hozir emas | Qayta ko‘rib chiqish triggeri |
|---|---|---|
| Native mobil app | v1 scope’dan tashqari; ochiq API yetarli | Haftalik faol solver > 2 000 VA mobil traffic > 30% |
| Qvant → real pul/USDT | ADR-0002 yopiq halqa; regulyatsiya | Yuridik ruxsat + alohida ADR tasdiqlangach |
| Crypto prize | Regulyatsiya + ishonch riski | Homiylar + yuridik tayyor bo‘lgach |
| O‘z sandbox primitivi | nsjail ishlaydi (14/14) | nsjail CVE yoki 2+ escape hodisasi |
| AGPL fork (DMOJ/Hydro) | Yopiq/commercial mahsulot | Biznes model ochiq-litsenziyaga o‘tsa |
| KEP duels’ni wholesale ko‘chirish | Differensiatsiya yo‘qoladi | — (rad etiladi) |
| cp.uz security audit | Aloqasi yo‘q loyiha | Hamkorlik shartnomasi imzolansa |
| Multi-region / microservices / K8s | 1 mashina, jamoa kichik | Faol user > 50k YOKI 2+ region talab |
| Kafka / RabbitMQ | Redis PULL protokoli yetarli | Judge throughput > 200/s barqaror |
| Real-time WebSocket standings | Polling yetarli; murakkablik | Contest’da > 5 000 bir vaqtli kuzatuvchi |
| Self-hosted 32B model (hozirgi 1 mashina) | GPU/resurs yo‘q; feasibility UNMEASURED | Judge hostlari ≥ 6 VA alohida GPU host |
| Marketplace / third-party masala sotish | Kontent sifati hali inqirozda | Hidden test coverage > 95% VA moderator jarayoni |
| B2C reklama | Brend va UX riski | — (rad etiladi) |
| AI mentor production (v1) | Sifat o‘lchanmagan (OPEN QUESTION) | O‘zbekcha eval’da aniqlik chegaradan oshsa |
| Yana 10+ til qo‘shish | 10 locale gap’lari yopilmagan | Mavjud locale’larda 0 hardcoded string |

**Umumiy trigger printsipi:** har bir “keyinroq” bandi **o‘lchanadigan** shartga bog‘lanadi — “keyin” emas, aniq son/chegara.

---

## ✅ Action list

| # | Amal | Kim | Timeframe |
|---|---|---|---|
| 1 | **Hidden-test quvuri va kontent remediatsiyasi** — F09/F10/F11; `print('3 2 1')` regressiya testi bilan qulflash | Content Ops + Judge/Backend | **Phase 0 (darhol)** |
| 2 | **Verdict yaxlitligi** — F05: 4 o‘lik kod, RE split, WRONG_TEST, yorliqlar i18n | Judge/Backend + Frontend | **Phase 0** |
| 3 | **B2B throttle fix** — F73: account-based limit; bitta NAT IP’da 20+ user 429 olmasligi sinovi | Backend + DevOps | **Phase 0 (B2B’dan oldin)** |
| 4 | **Security hygiene** — F74 sirlar, F66 judge izolyatsiya, F65 security.yml | DevOps/SRE + Backend | **Phase 0** |
| 5 | **Staging + measured judge latency** — F67 staging, F55 latency gate raqami | DevOps/SRE + Judge | **Phase 0→1** |
| 6 | **Instrumentation** — F53/F54 funnel + real/seeded ajratish + content-quality dashboard | Data + Backend | **Phase 2 (AI’dan oldin)** |
| 7 | **AI eval harness** — eval set + human-rating workflow + FAR/HR/CPF/AER | AI Engineer + Data | **Phase 2 (har qanday AI’dan oldin)** |
| 8 | **Pricing ADR** — F48 uchun qaror; B2B pilot bilan validatsiya | Product Director + Finance | **Phase 4** |
| 9 | **AI Feedback MVP** — F38, practice-only, local model, contest’da OFF | AI Engineer | **Phase 3** |

---

## ⚠️ To be confirmed / Assumptions / Non-goals

**Tasdiqlash kerak (qaror kutayotgan):**
1. **Asosiy segment** — usage = o‘quvchi, revenue = tashkilot (RECOMMENDATION; repo’da ochiq savol).
2. **P0 to‘plami** — 10 xususiyat; 7 tasi nuqson tuzatish, 3 tasi yangi infratuzilma.
3. **Roadmap re-basing** — Phase 0 = Trust & Hardening (brifingdagi fazalar qayta tuzildi).
4. **AI faqat Phase 3** — Phase 2 (instrumentatsiya) va Phase 0 (ishonchli verdict) shartsiz.
5. **Muddat berilmaydi** — sequencing + S/M/L; velocity yo‘q.
6. **`neytron_*` 10 001 seed user** o‘chirilsinmi (ADR-0023 ochiq follow-up).

**Asosiy assumptions (tekshirilmagan):**
- Kontent remediatsiyasi yuklamasi boshqa trunk’lardan kattaroq (author-throughput o‘lchanmagan).
- Bitta mashina production yuk ostida 7B modelni ko‘taradi (UNMEASURED).
- O‘zbekcha AI feedback sifati yetarli (UNMEASURED).
- 5–10% weekly-active ratio (taxmin; real o‘lchov yo‘q).
- Raqobatchi raqamlari (~197k, ~9k, TAM/SAM/SOM) — **UNVERIFIABLE** (manba fayllar repo’da yo‘q).
- `docs/03` bozor hajmi “kuzatilgan raqobatchi raqamlaridan chiqarilgan taxmin”.

**Non-goals (docs/01, docs/02 + bu hujjat):**
- Mobil native app (v1) · Qvant→real pul/USDT · Qvant bilan kontent/obuna sotib olish · cp.uz fork · KEP duels’ni to‘liq nusxalash · crypto sovrin · cp.uz security audit · o‘z sandbox primitivi · AGPL fork · **AI contest ichida** · AI’ga to‘g‘ridan-to‘g‘ri DB/test-bucket access · autonomous grading.

---

## 📚 Data sources & member output index

| A’zo | Bo‘lim | Asosiy hissa |
|---|---|---|
| **方向明** (Product Director) | 01 Vision | Vision/mission/value proposition/12 prinsip/strategik tezis; re-basing qarori; yakuniy yig‘ish |
| **析客** (Requirement Analyst) | 04, 05, 09 | 76 xususiyat (9 qatlam, BOR/QISMAN/YO‘Q), P0–P3 asoslash, 14 epic backlog |
| **瑞思** (User Researcher) | 02, 06, 03-user | 6 rol modeli, primary/revenue segment tavsiyasi, 6 journey, tadqiqot bo‘shliqlari |
| **竞析** (Competitive Analyst) | 03, 13, 12.1(3) | 11 raqobatchi matritsasi, SWOT, differensiatsiya, scope/out-of-scope |
| **数析** (Data Analyst) | 11, 12 | North Star himoyasi, metrika katalogi, Content Quality metrikasi, risk reyestri |
| **路径** (Roadmap Planner) | 07, 08, 10 | 12 dependency zanjiri, critical path, 7 fazali roadmap, AI roadmap |

**Asosiy manbalar:** `docs/research/2026-09-29-ai-agent-enterprise/REPORT.md` (498 qator, 6 bo‘lim, 55 manba) · `docs/01`–`docs/10` · `docs/07-adr/` (27 ADR) · `README.md` · `INDEX.md` · `CLAUDE.md` · `docs/03-market-research/` · `docs/research/2026-09-19-scale-50k/` · `docs/research/2026-09-20-as-built-architecture/` · `docs/research/2026-09-21-security-boundary/` · kod bazasi (`apps/`, `services/`, `tests/`).

---

> **Belgilash tizimi:** **FACT** = repo’da o‘lchangan/tasdiqlangan · **ASSUMPTION** = tekshirilmagan taxmin · **INFERENCE** = mavjud dalildan chiqarilgan xulosa · **RECOMMENDATION** = tavsiya (qaror emas) · **OPEN QUESTION** = hal qilinmagan · **UNKNOWN** = ma’lumot yo‘q.
>
> **Ma’lum cheklov:** brifingdagi “RankWant katta qismi ishlab chiqilmagan” degan da’vo repo bilan **zid**; bu hujjat repo’dagi **haqiqiy** holatga asoslangan (19 Django app, 87 migratsiya, 2 ishlaydigan judge, Phase 0/1/3 bajarilgan). Deep Research hisobotidagi **prognozlar fakt sifatida olinmagan**; `docs/03` dagi raqobatchi raqamlari **UNVERIFIABLE** deb belgilangan.
>
> **Kod o‘zgartirilmadi · Fayllar o‘chirilmadi · Research report tegilgan yo‘q.**
>
> Bu hisobot Product Strategy Team tomonidan AI hamkorligida tayyorlandi; muhim qarorlar Product Owner (Saidakbar aka) tomonidan tasdiqlanishi kerak.
