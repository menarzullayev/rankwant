# RankWant — product docs pipeline

Har bosqich alohida papka. **Qulflash** = jamoa tasdiqlagandan keyin `STATUS: locked`.

```
Idea Selection                → docs/idea-selection/
  ↓
1. Vision                     → docs/01-vision/
  ↓
2. Problem Discovery          → docs/02-problem-discovery/
  ↓
3. Market & Competitor        → docs/03-market-research/
  ↓
4. PRD                        → docs/04-prd/
  ↓
5. Domain Model               → docs/05-domain-model/
  ↓
6. System Architecture        → docs/06-architecture/
  ↓
7. ADR                        → docs/07-adr/
  ↓
8. Technical Specification    → docs/08-technical-spec/
  ↓
9. Development Plan           → docs/09-development-plan/
  ↓
10. Quality & Operations      → docs/10-operations/
```

Sanali sessiya yozuvlari (qaror sessiyalari, dizayn variantlari, auditlar) —
pipeline bosqichi emas, tarixiy manba: [research/](research/README.md).

## Status (2026-09-06)

| #   | Papka             | Holat           | Izoh                                      |
| --- | ----------------- | --------------- | ----------------------------------------- |
| 00  | Idea Selection    | **Retroaktiv**  | 2026-09-13 da yozildi; 4-variant ochiq     |
| 01  | Vision            | **Locked**      | RankWant + Qvant — 2026-09-06             |
| 02  | Problem discovery | **Locked**      | North Star: haftalik faol yechuvchi — 2026-09-06 |
| 03  | Market            | **Locked**      | Raqobatchi + brend + bozor hajmi — 2026-09-06 |
| 04  | PRD               | **Locked**      | Fazalar + reyting formulalari + Qvant — 2026-09-06 |
| 05  | Domain            | **Locked**      | Entity, indeks, migration tartibi — 2026-09-06 |
| 06  | Architecture      | **Locked**      | Stack + xavfsizlik chegarasi — 2026-09-06 |
| 07  | ADR               | **living**      | 0001–0019; 0004 accepted (bake-off 2026-09-06) |
| 08  | Tech spec         | **Locked**      | Auth, API, judge protokoli — 2026-09-06   |
| 09  | Dev plan          | **Locked**      | Phase 0 va Phase 1 bajarildi — 2026-09-06 |
| 10  | Operations        | **draft**       | Topologiya, siyosat, incident turlari     |

## Qanday qaror qabul qilamiz

1. Bir vaqtda **bitta** bosqich — oldingisi yetarli darajada yozilgan bo'lsa.
2. Tasdiqlagach README ga `STATUS: locked` + sana.
3. Locked bo'limni o'zgartirish = yangi ADR (`docs/07-adr/`).

## project-alpha bilan moslik

**Ha — bu prinsip bizga mos.**

[project-alpha](https://github.com/menarzullayev/project-alpha) allaqachon shu 10 bosqichli zanjirni isbotlab bergan:

| Afzallik                                          | RankWant uchun ahamiyati                                                                  |
| ------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| Vision → PRD → Domain ketma-ketligi               | CP platformasi katta — oldin «nima quramiz» ni yozmasdan kod yozmaslik                    |
| Market research alohida bosqich                   | KEP/RoboContest tahlillari `03` ga joylashadi, kod aralashmaydi                           |
| ADR alohida                                       | Stack (Inertia vs REST, judge engine, Qvant iqtisodiyoti) keyinroq qayta ko'rib chiqiladi |
| Dev plan oxirida emas, lekin arxitekturadan keyin | MVP scope aniq bo'lgach rejalashtirish oson                                               |
| Operations alohida                                | Judge, WARP, monitoring — production masalalari hujjatdan ajralgan                        |

**Farq:** project-alpha — g'oya → startap; RankWant — raqobatchi benchmark + aniq brend bilan boshlangan. Shuning uchun `03-market-research` hozir eng to'liq bosqich.

**Namuna loyihalar (shu workspace):**

- `rankglass/docs/README.md` — Pogona; pipeline locked, Next.js MVP bor
- project-alpha — faqat hujjat, kod yo'q

## Agentlar uchun

- Birinchi o'qish: [../INDEX.md](../INDEX.md)
- Raqobatchi to'liq tahlil: `kep-uz-platform-analysis.md`, `robocontest-uz-platform-analysis.md`
  — ⚠️ ikkalasi ham **repo'da yo'q, Linux bo'limida qolgan**
  ([03-market-research](03-market-research/README.md) ga qarang)
- Brend tekshiruv skriptlari: `/home/nsn/Telegram/handlechecker/scripts/checkers/`
