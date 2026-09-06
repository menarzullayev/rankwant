# 4. PRD (Product Requirements Document)

**STATUS:** locked (2026-09-06)

Mahsulot funksional talablari — fazalar bo'yicha.

## Fazalar

### Phase 0 — Foundation (MVP core)

| ID   | Feature                                    | Acceptance                                        |
| ---- | ------------------------------------------ | ------------------------------------------------- |
| P0-1 | Auth (email + parol, keyin OAuth/Telegram) | Ro'yxat, login, `/me`                             |
| P0-2 | Problem bank                               | CRUD admin; list, filter difficulty/topic/lang    |
| P0-3 | Judge submit                               | Source upload, verdict (20 kod), time/memory      |
| P0-4 | Custom test                                | Foydalanuvchi stdin → output                      |
| P0-5 | Contest (ACM)                              | Yaratish, register, submit, standings             |
| P0-6 | User profile + rating                      | Profil; **Skills + Contests** reytingi (ADR-0006) |
| P0-7 | i18n                                       | UI: **uz + ru + en**; masala matni muallif tilida  |

### Phase 1 — Growth

| ID   | Feature                        | Manba                           |
| ---- | ------------------------------ | ------------------------------- |
| P1-1 | Virtual contest                | KEP/Robo                        |
| P1-2 | Problem recommendation         | KEP `/problems/recommendation/` |
| P1-3 | Blog/yangilik                  | KEP                             |
| P1-4 | Notifications                  | KEP                             |
| P1-5 | Qvant — balans + quest + ledger | [ADR-0002](../07-adr/0002-qvant-economy.md) |
| P1-6 | Streak + streak yutuqlari       | KEP / Robo                      |
| P1-7 | **Activity reyting** yoqiladi   | P1-5 + P1-6 manba (ADR-0006)    |
| P1-8 | **Qvant do'kon (minimal)**      | 4 kosmetik narsa — ADR-0002     |
| P1-9 | Haftalik marafon                | RoboContest patterni            |

### Phase 2 — Scale & B2B

| ID   | Feature                                |
| ---- | -------------------------------------- |
| P2-1 | Mirror musobaqalar                     |
| P2-2 | O'qituvchi sinfi + Judge panel         |
| P2-3 | Obuna (Free/Plus/Pro)                  |
| P2-4 | Qvant do'kon kengaytirish (mavsumiy)   |
| P2-5 | O'z o'qish kontenti — maqola + roadmap |
| P2-6 | MCQ quiz (RoboContest) — ixtiyoriy     |

### Phase 3 — Differensiator (ixtiyoriy)

- Duels / arena (KEP) — **Challenges reytingi** shu bilan yoqiladi (ADR-0006)
- Hackathon/projects
- Real pul/USDT sovrin (ADR + legal)
- AI yechim review (Robo Pro)

## User stories — Phase 0 (MVP)

1. **Talaba:** Masalani o'qib, C++ da submit qilaman, WA/AC verdictini ko'raman.
2. **Talaba:** Rated contestda qatnashaman, standings'da o'rnimni va Contests reytingim qanday o'zgarganini ko'raman.
3. **Talaba:** Profilimda Skills reytingim **qanday hisoblanganini** ko'raman — formula ochiq (principle #2).
4. **Admin:** Yangi masala qo'shaman, test case yuklayman, qiyinlik (800–3500) beraman.
5. **Tashkilotchi:** 2 soatlik rated contest ochaman, ACM penalty bilan.

> Virtual contest (P1-1), Qvant (P1-5) va o'z kontent (P2-5) story'lari o'z fazalarida yoziladi.

## Reyting formulalari

[ADR-0006](../07-adr/0006-rating-model.md) sharti: **4 formulaning har biri ochiq hujjatlanadi.** Yashirin og'irlik yoki «sirli» bonus yo'q — vision principle #2.

### Poydevor — qiyinlik shkalasi

`Problem.difficulty` — butun son **800–3500**, qadam 100 (Codeforces bilan mos → tashqi arxiv importi yo'qotishsiz).
Foydalanuvchi raqamni emas, **darajani** ko'radi:

| Raqam     | Daraja           | Rang        |
| --------- | ---------------- | ----------- |
| 800–1199  | Boshlang'ich     | kulrang     |
| 1200–1599 | O'rta            | yashil      |
| 1600–2099 | Qiyin            | ko'k        |
| 2100–2599 | Ekspert          | binafsha    |
| 2600+     | Master           | qizil       |

### 1. Skills reyting — Phase 0

Foydalanuvchi **birinchi marta AC** olgan masalalar to'plami ball bo'yicha **kamayish tartibida** saralanadi (`p₁ ≥ p₂ ≥ …`, `pᵢ = difficulty`):

```
Skills = round( Σᵢ  pᵢ × 0.95^(i−1) )
```

Xossalari (isbotlangan, 200k tasodifiy holatda tekshirilgan):

| Xossa | Ma'nosi |
| ----- | ------- |
| **Monoton** — foydalanuvchi harakatidan tushmaydi | Yangi masala yechish reytingni **hech qachon** kamaytirmaydi. Istisno: masala qayta baholansa o'zgarishi mumkin — [ADR-0007](../07-adr/0007-skills-uses-current-difficulty.md) |
| Maksimal koeffitsient yig'indisi = 20× | Reyting cheksiz o'smaydi, eng yuqori masaladan 20 baravardan oshmaydi |
| ~45 masaladan keyin to'yinadi | Bir xil qiyinlikda 90% ga yetiladi → **keyin faqat qiyinroq masala o'stiradi** |

Namuna: `500 × 800` (grind) → **16 000** · `20 × 2500` (chuqur) → **32 076**.
Ya'ni 20 ta qiyin masala 500 ta oson masaladan yuqori — mahorat o'lchanadi, sarflangan vaqt emas.

`pᵢ` = masalaning **joriy** qiyinligi ([ADR-0007](../07-adr/0007-skills-uses-current-difficulty.md)). Qayta baholash reytingni o'zgartirsa, sababi `RatingHistory` da yoziladi va foydalanuvchiga xabar beriladi.

### 2. Contests reyting — Phase 0 (Codeforces uslubi)

Faqat `Contest.is_rated = true` va **≥ 10 ishtirokchi** bo'lgan musobaqalar hisoblanadi.

1. **Kutilgan g'alaba ehtimoli:** `P(i,j) = 1 / (1 + 10^((Rⱼ − Rᵢ) / 400))`
2. **Kutilgan o'rin (seed):** `seedᵢ = 1 + Σ_{j≠i} P(j, i)`
3. **Maqsad o'rin:** `mᵢ = √(seedᵢ × rankᵢ)` — kutilgan va haqiqiy o'rinning geometrik o'rtachasi
4. **`R*ᵢ`** = `seed = mᵢ` beradigan reyting (binar qidiruv)
5. **O'zgarish:** `dᵢ = (R*ᵢ − Rᵢ) / 2`
6. **Inflyatsiya tuzatishi:** barcha `dᵢ` dan `Σd / n` ayiriladi → musobaqa umumiy reytingni shishirmaydi

| Parametr             | Qiymat                                       |
| -------------------- | -------------------------------------------- |
| Boshlang'ich reyting | 1400                                         |
| Quyi chegara         | 0 (manfiy bo'lmaydi)                         |
| Yangi foydalanuvchi  | birinchi 6 rated contestda `abs(d) × 1.5`    |
| Minimal ishtirokchi  | 10 (kamroq bo'lsa contest unrated)           |

Nega Codeforces uslubi: formulasi ommaga ochiq va CP jamoasi **allaqachon tushunadi** — principle #2 uchun eng kuchli tanlov.

### 3. Activity reyting — Phase 1

Oxirgi **30 kunlik siljuvchi oyna**:

```
Activity = 10 × faol_kun  +  5 × bajarilgan_quest  +  min(2 × streak_kun, 60)
```

- `faol_kun` — kun ichida ≥1 submit bo'lgan kunlar
- Maksimal: `300 + 150 + 60 = 510`
- Oyna siljigani uchun **tabiiy kamayadi** — faollik to'xtasa reyting ham tushadi

⚠️ **Qvant balansi ataylab ishlatilmaydi.** Aks holda do'konda xarid qilish reytingni tushirardi — ya'ni foydalanuvchi Qvant sarflashdan qo'rqardi. Faqat *bajarilgan quest soni* hisoblanadi.

### 4. Challenges reyting — Phase 3

1v1 duel uchun klassik Elo:

```
E  = 1 / (1 + 10^((R_raqib − R) / 400))
R' = R + K × (S − E)          S ∈ {1 = g'alaba, 0.5 = durang, 0 = mag'lubiyat}
```

`K = 32` (birinchi 10 duel), keyin `K = 16`. Boshlang'ich 1400.

### Qayta hisoblash

Skills va Contests — Celery task orqali; Contests musobaqa yakunlangach bir marta, Skills har AC da inkremental.
Formula o'zgarsa **yangi ADR** kerak va barcha reytinglar qayta hisoblanadi (foydalanuvchiga oldindan e'lon qilinadi).

## Qvant iqtisodiyoti

To'liq: [ADR-0002](../07-adr/0002-qvant-economy.md). Qisqacha:

- **Yopiq loop** — Qvant real pul qiymatiga ega emas
- **Earn:** kunlik quest (+10/+15), contest (+30), marafon (+100), streak yutuqlari (+50/+250/+2000), profil (+50 bir marta)
- **Spend (v1):** faqat kosmetika va qulaylik — streak freeze 200, avatar ramka 500, cover 800, badge 1500
- **Anti-farm:** faqat birinchi AC; kunlik maksimal 100 Qvant; rejudge da qaytarish; barcha o'zgarish ledgerda
- **Ataylab qoldirilgan:** yechim/editorial ochish (ADR-0005 ziddiyati), obuna chegirmasi, funksiya ochish — har biri alohida ADR

## Non-functional requirements

| Talab                  | Maqsad                                                       |
| ---------------------- | ------------------------------------------------------------ |
| **Judge latency**      | **p50 < 5s, p95 < 15s** (oddiy masala)                       |
| Contest yuklamasi      | 500 parallel submit navbatni buzmasligi                      |
| Uptime                 | 99.5% (production)                                           |
| API                    | REST + OpenAPI (`drf-spectacular`) — [ADR-0003](../07-adr/0003-stack-django-next.md) |
| SEO                    | Masala va maqola sahifalari SSR — o'z kontent differensiatori uchun shart |
| Reyting shaffofligi    | 4 formulaning hammasi UI da ochiq — [ADR-0006](../07-adr/0006-rating-model.md) |
| Security               | Judge alohida hostda, sandbox, rate limit — [ADR-0004](../07-adr/0004-judge-engine.md) |
| Privacy                | PINFL/telefon ixtiyoriy                                      |

Judge latency maqsadi [ADR-0004](../07-adr/0004-judge-engine.md) bake-off mezoniga to'g'ridan-to'g'ri ulanadi.

## Out of scope (v1)

- Mobile native app (API first)
- Qvant real pul / USDT konversiyasi — **alohida ADR + huquqiy tahlil** shart
- Qvant bilan kontent yoki obuna sotib olish
- cp.uz fork

## Ochiq nuqta

**Narx modeli** (P2-3 Free/Plus/Pro) — summalar hali yo'q. RoboContest 4 tier benchmark mavjud ([03-market-research](../03-market-research/positioning.md)). Bu Phase 2 masalasi va **alohida ADR** bo'ladi; MVP scope'ini bloklamaydi.

## Qulflash

2026-09-06: fazalar (P0–P3), user story'lar, **4 reyting formulasi**, Qvant iqtisodiyoti va NFR tasdiqlandi.
Bog'liq qarorlar: [ADR-0002](../07-adr/0002-qvant-economy.md) · [ADR-0003](../07-adr/0003-stack-django-next.md) · [ADR-0004](../07-adr/0004-judge-engine.md) · [ADR-0005](../07-adr/0005-content-strategy-own-content.md) · [ADR-0006](../07-adr/0006-rating-model.md)
O'zgartirish = yangi ADR (`docs/07-adr/`).

**Lock'dan keyingi tuzatishlar:**

- 2026-09-06 — [ADR-0007](../07-adr/0007-skills-uses-current-difficulty.md): Skills reyting **joriy** qiyinlikdan hisoblanadi; monotonlik kafolati «foydalanuvchi harakatidan tushmaydi» shakliga aniqlashtirildi.

## Keyingi qadam

`05-domain-model` — entity mapping va migration rejasi → `08-technical-spec`.
