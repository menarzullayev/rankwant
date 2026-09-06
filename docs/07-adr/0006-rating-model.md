# ADR-0006: Reyting modeli — 4 reyting (KEP uslubi), fazali ochilish

**STATUS:** accepted (2026-09-06)

## Muammo

Vision principle #2: **«Reyting aniq — foydalanuvchi qanday ball olganini tushunadi (yashirin algoritm emas)»**. Lekin nechta reyting bo'lishi aniqlanmagan edi — `05-domain-model` 2 ta maydon (`rating_problem`, `rating_contest`) taklif qilgan, `01-vision` esa umumiy «reyting» deydi.

## Raqobatchilar

| Platforma       | Reytinglar                                                            |
| --------------- | --------------------------------------------------------------------- |
| Codeforces      | 1 — contest Elo                                                       |
| **RoboContest** | 3 — `roboRank` (o'rin), `contestRating` (Elo), `karma` (ijtimoiy)     |
| **KEP.uz**      | 4 — Skills, Activity, Contests, Challenges (home dashboard'da alohida) |

## Variantlar

1. **1 ta umumiy reyting** — eng sodda UI, brendga mos
2. **2 ta** — Contest (Elo) + Practice (deterministik)
3. **3 ta** — Robo uslubi (rank + Elo + karma)
4. **4 ta** — KEP uslubi

## Tanlov

**Variant 4 — 4 reyting:** `Skills`, `Activity`, `Contests`, `Challenges`.

## Sabab

- Har bir faoliyat turi o'z reytingini oshiradi → retention uchun kuchli (KEP isbotlagan pattern)
- Har bir reyting **bitta signalni** o'lchaydi, ya'ni formulasi sodda va e'lon qilinadigan bo'ladi — principle #2 **aynan shunda** bajariladi. Bitta umumiy reyting musobaqa kuchi va arxiv mehnatini yashirin og'irliklar bilan aralashtirar edi
- Contest reytingi Elo bo'lib qoladi → tashqi CP dunyosi (Codeforces) bilan taqqoslanadi

## Shart (principle #2 uchun majburiy)

4 formulaning **har biri** foydalanuvchiga ochiq hujjatlanadi: qaysi hodisa necha ball beradi, oyna qancha, decay bormi. Yashirin og'irlik yoki «sirli» bonus qo'shilmaydi. Bu shart bajarilmasa, 4 reyting principle #2 ni **buzadi** — 1 reytingdan ham yomonroq bo'ladi.

## Fazali ochilish

Barcha 4 reyting domain modelda **boshidan** loyihalanadi (keyin migratsiya qilmaslik uchun), lekin UI da faqat manba feature'i tayyor bo'lgani ko'rinadi:

| Reyting        | Manba feature                   | Ochilish              |
| -------------- | ------------------------------- | --------------------- |
| **Skills**     | masala + contest natijalari     | Phase 0 (MVP)         |
| **Contests**   | contest standings, Elo          | Phase 0 (MVP)         |
| **Activity**   | Qvant quest, daily login, streak | Phase 1 (P1-5, P1-6)  |
| **Challenges** | duels / arena                   | Phase 3               |

Bo'sh yoki nol reyting UI da ko'rsatilmaydi.

## Oqibatlar

- `05-domain-model` User: `rating_problem, rating_contest` → `rating_skills`, `rating_contest`, `rating_activity`, `rating_challenges`
- `04-prd` P0-6 acceptance: MVP da **2 reyting** ko'rinadi (Skills, Contests)
- Principle #5 («gamification va shop keyin») **buzilmaydi** — Activity reyting Qvant bilan birga Phase 1 da keladi, MVP ga gamification qo'shilmaydi
- Challenges reyting Phase 3 duels/arena ga bog'langan; o'sha faza kechiksa, reyting ham kechikadi — bu **qabul qilingan** kompromis

## Formulalar — yozildi (2026-09-06)

Principle #2 sharti bajarildi: 4 formulaning hammasi [04-prd § Reyting formulalari](../04-prd/README.md#reyting-formulalari) da ochiq yozilgan.

| Reyting    | Formula                                              |
| ---------- | ---------------------------------------------------- |
| Skills     | `Σ pᵢ × 0.95^(i−1)` (kamayish tartibida saralangan) — monoton, 20× cheklangan |
| Contests   | Codeforces uslubi: seed vs rank, `d = (R* − R)/2`, inflyatsiya tuzatishi |
| Activity   | `10×faol_kun + 5×quest + min(2×streak, 60)`, 30 kunlik oyna |
| Challenges | Klassik 1v1 Elo, `K = 32 → 16`                       |

Qiyinlik shkalasi: DB da 800–3500 (qadam 100), UI da 5 daraja yorlig'i.

**Bog'liqlik yopildi (2026-09-06):** [ADR-0002](0002-qvant-economy.md) quest ta'rifini aniqladi — `bajarilgan_quest` = kunlik quest'lar (kunning masalasi, kuniga ≥3 AC). Qvant *balansi* ataylab formulada yo'q: aks holda do'konda xarid reytingni tushirardi.

## Bog'liq hujjatlar

- [../01-vision/README.md](../01-vision/README.md) — principle #2, #5
- [0002-qvant-economy.md](0002-qvant-economy.md)
- [../05-domain-model/README.md](../05-domain-model/README.md)
