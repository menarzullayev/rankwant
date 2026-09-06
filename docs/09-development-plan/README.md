# 9. Development Plan

**STATUS:** locked (2026-09-06)

Fazalar [04-prd](../04-prd/README.md) 🔒 dan; stack [ADR-0003](../07-adr/0003-stack-django-next.md).

## Kritik yo'l

```
Hujjat pipeline ──┬── Sprint 0.5 judge bake-off ──┐
                  │   (Judge ishini BLOKLAYDI)     │
                  └── repo scaffold + CI ──────────┴── Sprint 1–4 MVP
                                                          │
                                       Xavfsizlik auditi ──┴── PUBLIC LAUNCH
```

Ikkita narsa hech narsani kutmasdan parallel boshlanishi mumkin: **repo scaffold** va **judge bake-off**.
Judge bake-off tugamaguncha Sprint 3 (submit oqimi) boshlanmaydi.

## Sprint 0 — Hujjat + infra

- [x] Workspace `rankwant/` + docs pipeline
- [x] Raqobatchi tahlil (KEP, RoboContest, cp.uz)
- [x] Hujjat bosqichlari 01–06, 08 🔒 locked
- [x] ADR 0001–0009 accepted (0004 bake-off bilan yopildi)
- [ ] Domen/handle ro'yxatdan o'tkazish — `rankwant.uz`, `qvantcoin.uz`, `@rankwant`, `@qvantcoin`
      **Shoshilinch emas** (2026-09-06 qarori): bu nomlar yillar davomida bo'sh turgan, ya'ni talab past. Launch'gacha bajarilsa yetarli.
- [x] GitHub monorepo `rankwant` ([ADR-0009](../07-adr/0009-monorepo.md))
- [x] **Judge bake-off spike** — g'olib: Go + nsjail, 14/14 ↓

## Sprint 0.5 — Judge bake-off · GATE ✅ YOPILDI (2026-09-06)

Maqsad: [ADR-0004](../07-adr/0004-judge-engine.md) ni `proposed` → `accepted`.

**Nomzodlar:** A — Go worker + nsjail (Apache-2.0) · B — Python worker + isolate (GPL-2.0+)
Ikkalasi ham `JudgeProvider` interfeysi va **pull** protokoli ortida.

| Sinov                | Nimani tekshiradi                         |
| -------------------- | ----------------------------------------- |
| Oddiy A+B            | Bazaviy oqim, start latency               |
| Og'ir sikl (TLE)     | CPU vs wall time o'lchash aniqligi        |
| Katta massiv (MLE)   | Peak memory o'lchash aniqligi             |
| Fork bomb            | Process limiti ushlaydimi                 |
| Fayl / tarmoq / `/proc` urinishi | Izolyatsiya haqiqatan ishlaydimi |
| Interactive masala   | Ikki tomonlama I/O qo'llab-quvvatlanadimi |
| 100 test × 50 submit | Parallel yuklamada barqarorlik            |

**O'tish sharti:** NFR byudjeti — **p50 < 5s, p95 < 15s**; izolyatsiya sinovlarining **hammasi** o'tishi shart.
To'liq mezonlar: [ADR-0004 § Baholash mezonlari](../07-adr/0004-judge-engine.md).

## Sprint 1–4 — MVP (Phase 0)

| Sprint | Ish                                                            | PRD          | Holat |
| ------ | -------------------------------------------------------------- | ------------ | ----- |
| **1**  | Repo scaffold, CI (mypy strict + lint + test), Auth, `ApiToken` | P0-1         | ✅ |
| **2**  | Problem bank + Django admin; i18n poydevori                    | P0-2, P0-7   | ✅ |
| **2a** | Test ma'lumoti S3 da (judge o'qiydi) — masala tuzuvchi uchun yuklash UI hali yo'q | P0-2 | ⚠️ qisman |
| **3**  | Judge integratsiya (`JudgeProvider`), Attempt + 20 verdict, custom test | P0-3, P0-4 | ✅ |
| **4**  | Contest ACM + standings (SSE), profil + Skills/Contests reyting, Next.js UI | P0-5, P0-6 | ✅ |

**Phase 0 (P0-1 … P0-7) to'liq bajarildi.** Phase 1 dan: Qvant va Activity (Sprint 5).

Holat (2026-09-06): 65 test o'tadi · mypy strict toza (62 fayl) · ruff toza ·
OpenAPI 23 endpoint, 0 xato · Next.js build, lint va typecheck toza · 0 zaiflik ·
judge bake-off 14/14.

MVP **dasturlash tillari** (judge): C++, Python, Java. UI tillari alohida — 04-prd P0-7: uz/ru/en.

## Launch gate — public chiqishdan oldin

- [ ] [08 § Xavfsizlik checklist](../08-technical-spec/README.md) to'liq bajarilgan
- [ ] **Tashqi xavfsizlik auditi** o'tkazilgan ([ADR-0004](../07-adr/0004-judge-engine.md) sharti)
- [ ] Judge latency o'lchangan: p50 < 5s, p95 < 15s
- [x] 4 reyting formulasi **UI da ochiq** (principle #2) — `/rating` sahifasi
- [x] Faqat Phase 0 reytinglari ko'rinadi (Skills, Contests) — [ADR-0006](../07-adr/0006-rating-model.md) fazali ochilish
- [ ] Huquqiy: litsenziya tahlili yurist tomonidan tasdiqlangan ([ADR-0003](../07-adr/0003-stack-django-next.md))

## Sprint 5–8 — Phase 1

| Ish | PRD | Holat |
| --- | --- | ----- |
| **Qvant** — wallet + ledger + kunlik quest + streak yutuqlari | P1-5 | ✅ |
| **Streak** + streak yutuqlari (7/30/365) | P1-6 | ✅ |
| **Activity reyting** yoqildi (UI da ko'rinadi) | P1-7 | ✅ |
| **Qvant do'kon** (minimal, 6 kosmetik narsa) | P1-8 | ✅ |
| **Virtual contest** — tugagan musobaqani o'z vaqtida yechish | P1-1 | ✅ |
| **Masala tavsiyasi** — darajaga mos, yechilmaganlar | P1-2 | ✅ |
| **Blog / yangiliklar** + e'lon bildirishnomasi | P1-3 | ✅ |
| **Bildirishnomalar** — ADR-0007 majburiyati ham shu bilan yopildi | P1-4 | ✅ |
| **Haftalik marafon** — determinlashgan 10 masala | P1-9 | ✅ |

**Phase 1 to'liq bajarildi (P1-1 … P1-9).**

Holat: 149 test · mypy strict toza (97 fayl) · 39 endpoint · 0 zaiflik.
Ledger auditi: kesh va tranzaksiya yig'indisi har doim mos
([ADR-0002](../07-adr/0002-qvant-economy.md) sharti).

## Sprint 9+ — Phase 2

| Ish | PRD | Holat |
| --- | --- | ----- |
| **Mirror contest** — masalalar ko'chiriladi, reytingsiz | P2-1 | ✅ |
| **O'qituvchi sinfi** — sinf, a'zolik, uy vazifasi, progress | P2-2 | ✅ |
| **O'z o'qish kontenti** — maqola ↔ masala ↔ roadmap ([ADR-0005](../07-adr/0005-content-strategy-own-content.md)) | P2-5 | ✅ |
| Obuna (Free/Plus/Pro) | P2-3 | ⛔ **narx ADR'i kerak** |
| Qvant do'kon kengaytirish (mavsumiy) | P2-4 | ⬜ |
| MCQ quiz | P2-6 | ⬜ |

`P2-3` bloklangan: narx modeli mahsulot qarori, texnik ish emas.

## Definition of Done

Har PR uchun:

- [ ] `mypy` strict o'tadi, lint toza
- [ ] Biznes logika **service layer'da**, view'da emas
- [ ] Test: judge pipeline, reyting formulasi va Qvant ledger uchun **majburiy**
- [ ] OpenAPI schema diff ko'rib chiqilgan (kutilmagan buzilish yo'q)
- [ ] Migration `--plan` bilan review qilingan
- [ ] Arxitektura yoki mahsulot qarori bo'lsa — **ADR yozilgan**
- [ ] Fazali ochilish hurmat qilingan (masalan Activity reyting Phase 1 gacha UI da yo'q)

## Milestone maqsadlari

[03 § Bozor hajmi](../03-market-research/README.md) dan; North Star — **haftalik faol yechuvchi**:

| Bosqich          | Ro'yxatdan o'tgan | North Star  |
| ---------------- | ----------------- | ----------- |
| MVP launch + 3 oy | ~1k              | ~100        |
| Yil 1            | ~5k               | ~300–500    |
| Yil 2            | ~12k              | ~700–1 200  |

## Jamoa

Stack avval tanlandi, jamoa shunga qarab shakllantiriladi.

| Rol          | Mas'uliyat                                         | MVP uchun |
| ------------ | -------------------------------------------------- | --------- |
| Backend      | Django/DRF, Celery, reyting hisoblash              | shart     |
| Frontend     | Next.js SSR, contest UX, i18n                      | shart     |
| Judge/DevOps | `judge.rankwant.uz`, sandbox, til obrazlari, queue | shart     |
| Content      | Masala import, o'z maqola                          | Sprint 2+ |

Judge/DevOps roli **eng kam almashtiriladigan** — sandbox xavfsizligi shu odamda.

## Bog'liq loyihalar

- **rankglass (Pogona)** — boshqa mahsulot; docs pipeline namunasi va Next.js tajribasi
- **cp-uz** — raqobatchi benchmark (o'qish kontenti); hamkor emas, fork emas

## Qulflash

2026-09-06: kritik yo'l, sprintlar, **Definition of Done**, **launch gate**, milestone maqsadlari va xavflar tasdiqlandi.
O'zgartirish = yangi ADR (`docs/07-adr/`). Sprint ichidagi vazifa taqsimoti bu hujjatga kirmaydi — u issue tracker'da.

**Lock'dan keyingi tuzatishlar:**

- 2026-09-06 — domen/handle ro'yxatdan o'tkazish **shoshilinch emas** deb belgilandi (nomlar uzoq vaqt bo'sh; talab past). `03-market-research/brand-discovery.md` dagi «tez ro'yxatdan o'tkazish» tavsiyasi tadqiqot vaqtidagi baho edi — bajarilish muddati shu yerda belgilanadi.

## Xavf

| Xavf                        | Mitigatsiya                                                              |
| --------------------------- | ------------------------------------------------------------------------ |
| **Sandbox escape**          | Judge host izolyatsiyasi (pull, port yo'q, DB creds yo'q) + tashqi audit  |
| Judge murakkabligi          | Sprint 0.5 bake-off; sandbox primitivi tayyor olinadi                    |
| **0 user cold start**       | Maktab B2B pilot va mirror olimpiada — network effekt kutmaydi           |
| RoboContest network effekti | Tor SAM: o'zbek kontent + OJ bir joyda ([03](../03-market-research/positioning.md)) |
| Narx modeli yo'q            | Phase 2 gacha kerak emas; alohida ADR                                    |
| Scope creep                 | PRD fazalari 🔒; o'zgartirish = ADR                                       |
| Ikki til (Py + TS)          | Qabul qilingan narx; chegara REST/OpenAPI                                |
