# RankWant brend — LOCK-GATE

**STATUS:** open (Crest = locked **candidate** 2026-09-10; gate hali yopilmagan)  
**Nima qulflanadi:** **Crest** (grafik belgi) + **Wordmark** (`Rank` + accent `Want`) birgalikdagi ishlatish qoidalari.  
**Nima qulflanmaydi:** Qvant coin belgisi, v2 eskizlar (`belgi-v2/`), generator arxivi (`belgi-generated/`).

Yopilgach `mark-crest-params.md` dagi STATUS → **locked**, va o'zgartirish yangi qaror + PR talab qiladi.

**Vizual prototip (tasdiqdan oldin):** [`lock-gate-prototype/lock-gate-review.html`](lock-gate-prototype/lock-gate-review.html) — [`README`](lock-gate-prototype/README.md).

---

## Oldindan shartlar (kod/hujjat)

| # | Shart | Dalil |
|---|--------|--------|
| P1 | Crest manbai bitta SVG | `docs/brand/mark-crest.svg` |
| P2 | Barcha raster/favicon skriptdan | `python3 tools/brand.py` → `apps/web/public/brand/*`, `favicon.ico` |
| P3 | Parametrlar yozilgan | [`mark-crest-params.md`](mark-crest-params.md) |
| P4 | Wordmark yagona komponent | `apps/web/src/layout/BrandMark.tsx` |
| P5 | Pipeline hujjati | [`README.md`](README.md) |

---

## A — Mustaqil tanilish (ikki primitive)

Har band: **PASS** yoki **FAIL** + qisqa dalil (fayl yo'li, screenshot nomi, sana).

| ID | Test | Mezon | ☐ |
|----|------|--------|---|
| A1 | Crest **wordmarksiz** | 16×16 favicon: ikki cho‘qqi + nuqta silueti taniladi; ichki mezon — «uchburchik + quyosh» deb o‘qilmasligi (`eskiz-dashboard` nazorat matniga qarshi) | ☐ |
| A2 | Crest 24 / 32 | Brauzer tab va `mark-32.png` da bir xil «bizning» siluet | ☐ |
| A3 | Wordmark **crestsiz** | Header (`BrandMark` responsive), footer, auth: `RankWant` o‘qiladi; 320px da monogram **R** (HITL header qarori) | ☐ |
| A4 | Ajralish | CF ustun, podium, bracket, KEP-gradient «K», oddiy RW monogram bilan **bir qarashda** chalkashmaydi (≥3 nafar, qisqa izoh) | ☐ |

---

## B — Muhit va kontrast

| ID | Test | Mezon | ☐ |
|----|------|--------|---|
| B1 | Light UI | `mark-crest.svg` oq/kulrang fon ustida; wordmark accent o‘qiladi | ☐ |
| B2 | Dark UI | `mark-crest-dark.svg` yoki to‘liq rangli Crest; PWA `theme_color` `#102038` bilan mos | ☐ |
| B3 | OG / ijtimoiy | `og-default.png` (1200×630): platforma nomi + belgi bir qarashda | ☐ |
| B4 | Avatar crop | Crest markazlashuvi: 1:1 kvadrat (Telegram/GitHub o‘lchami simulyatsiyasi) — muhim detal kesilmaydi | ☐ |
| B5 | Monochrome | **Variant A:** `crest-black.svg` + `crest-white.svg` qo‘shilgan **yoki** **Variant B:** qaror yozilgan — «chop/merch hozircha faqat to‘liq rang Crest» | ☐ |

---

## C — Hujjat, ranglar, taqiqlar

| ID | Shart | ☐ |
|----|--------|---|
| C1 | **Clear space:** Crest atrofida min. bo‘sh joy = nuqta radiusi `r` (44.1 @1024) yoki undan katta — raqam `mark-crest-params.md` ga qo‘shilgan | ☐ |
| C2 | **Minimum size (raqamli):** Crest digital ≥16px; wordmark header ≥320px kenglikda to‘liq qoida bilan sinovdan o‘tgan | ☐ |
| C3 | **Crest ↔ UI rang:** jadval — Crest hex (`#44A0FC`, `#1074DC`, `#102038`) va `--rw-accent*` alohida yoki mapping bilan; bitta sahifada | ☐ |
| C4 | **Do-not-use** (kamida 5 ta): distort, rotate, alohida facetlarni ajratish, gradient qo‘shish, Crest ranglarini ixtiyoriy almashtirish | ☐ |
| C5 | **Ishlatish xaritasi** tasdiqlangan: header/auth/footer → wordmark; favicon/PWA/BIMI → Crest; OG → lockup (matn + belgi) | ☐ |
| C6 | Dalillar arxivi | `docs/brand/lock-gate-evidence/` (screenshot matrix, sana, commit SHA) — gate yopilish PRida | ☐ |

---

## Ixtiyoriy (launchdan keyin ham bo‘ladi)

| ID | Band | ☐ |
|----|------|---|
| O1 | BIMI DNS (`p=quarantine`/`reject` + TXT) — [README § BIMI](README.md) | ☐ |
| O2 | Vektor wordmark (`wordmark.svg`) — print/sponsor uchun | ☐ |
| O3 | Horizontal/stacked lockup SVG | ☐ |

---

## Qaror

| Maydon | Qiymat |
|--------|--------|
| **Gate** | ☐ PASS · ☐ FAIL |
| **Sana** | |
| **Dalil PR** | |
| **Tasdiq** | Saidakbar aka (brend o‘zgarishi — yangi qaror qatori `CLAUDE.md` da) |

**PASS qoidasi:** A1–A4, B1–B4, C1–C6 — hammasi belgilangan; B5 da A **yoki** B varianti tanlangan. O1–O3 gate uchun shart emas.

**FAIL:** Crest candidate qoladi; o‘zgartirish `mark-crest.svg` + qayta `tools/brand.py` + ushbu ro‘yxat qayta tekshiriladi.

---

## Tez havolalar

- Assetlar: [`README.md`](README.md)  
- Crest geometriya/rang: [`mark-crest-params.md`](mark-crest-params.md)  
- Raqobat cheklovlari: [`cp-logo-analysis-v2.md`](cp-logo-analysis-v2.md)  
- Wordmark kod: `apps/web/src/layout/BrandMark.tsx`
