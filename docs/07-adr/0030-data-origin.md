# ADR 0030 — Data origin (real / demo / imported)

**STATUS:** accepted
**Sana:** 2026-09-29
**Tasdiqlagan:** Saidakbar (owner)
**Manba:** D9 (ADR 0030 data origin) · `owner-decision-closure-matrix-2026-09-29.md`
**Ta'sir doirasi:** Phase 0
**Dalil:** `apps/api/core/models.py` (`User`) · North Star SQL `is_seeded` ishlatadi, ustun **yo'q** (o'lchandi: `is_seeded` faqat `.venv` ichidagi `faker`da uchraydi, ilova kodida emas) · seed prefiks `neytron_` (`apps/api/contests/management/commands/seed_contest_scale.py`) · `apps/api/core/account.py` (`neytron_` prefiks izohi)

## 1. Muammo

North Star SQL `is_seeded` ustunini ishlatadi, lekin u **mavjud emas**. Seed qilingan foydalanuvchilar faqat `neytron_` prefiksi bilan ajraladi — bu mo'rt evristika. Oqibat: barcha metrikalar (faol user, retention, funnel) iflos, real va demo/imported userlar aralashib ketadi.

Ikki xil ehtiyoj ajratilmagan: (a) real foydalanuvchi, (b) stress/demo uchun yaratilgan sun'iy user, (c) Codeforces'dan import qilingan user, (d) staff.

## 2. Variantlar

1. `is_seeded` boolean.
2. `User.origin` enum + `Attempt.origin` denormalizatsiya.
3. Faqat event darajasida ajratish.
4. `neytron_` prefiksini saqlash.

## 3. Tanlov

**Variant 2 dan faqat `User.origin`** (D9):

| Qiymat | Ma'nosi |
|---|---|
| real | Haqiqiy ro'yxatdan o'tgan foydalanuvchi |
| demo | Demo/ko'rgazma uchun yaratilgan |
| imported | Import qilingan (Codeforces va h.k.) |
| staff | Staff/xodim |

- **`Attempt.origin` QO'SHILMAYDI** — D9 uni **rad etdi**.
- `imported` — **alohida** qiymat (real/demo bilan aralashtirilmaydi).
- `neytron_*` userlar **o'chirilmaydi** → 2027 Q1 (non-blocking DEFERRED).

## 4. Sabab

Boolean (`is_seeded`) `imported` va `staff` ni ajratmaydi, ya'ni metrika yana iflos qoladi. `User.origin` enum barcha to'rt segmentni bitta ustunda beradi va `check_metrics.py` qaysi maydonni tekshirishini aniq biladi. `Attempt.origin` denormalizatsiya qo'shimcha sinxronizatsiya yuki keltiradi, lekin Phase 0 ehtiyoji `User` darajasida yopiladi — shuning uchun rad etildi. `neytron_*` userlar testlash uchun kerak (egasi), shuning uchun saqlanadi.

## 5. Oqibatlar

- `User.origin` ustuni + enum; M3 migratsiya (add → backfill → switch).
- `check_metrics.py` `origin='real'` maydonini biladi va CI'da tekshiradi.
- North Star SQL endi `origin='real'` bilan (JOIN) ishlaydi.
- `Attempt.origin` **yo'q** — `Attempt` sxemasi o'zgarmaydi.
- Backfill audit raqami chop etiladi; seed user aniq soni (U2) o'lchanadi.

## 6. Qaytarilishi

Forward-only (M3). Rollback = qayta backfill yoki ustunni bo'shatish (forward). Deploy oldidan **dump** majburiy. Backfill 10 001 seed userni noto'g'ri tasniflasa segmentatsiya buziladi — shuning uchun audit raqami va U2 o'lchovi oldindan olinadi.

## 7. Tasdiq

- `origin` ustuni + enum mavjud.
- **`Attempt.origin` YO'Q** (rad etilgan) — repo ko'rigi.
- North Star SQL `origin='real'` bilan (JOIN) xatosiz ishlaydi.
- Backfill audit raqami chop etilgan.
- `imported` alohida qiymat.
- Seed user aniq soni **o'lchangan** (10 000 / 10 001 / 10 068 nomuvofiqligi yopilgan).
- `tools/check_metrics.py` exit 0.

## 8. Bog'liq hujjatlar

- D9 — `owner-decision-closure-matrix-2026-09-29.md`
- `acceptance-criteria-lock-2026-09-29.md` — WP3 bloki
- Blueprint §21 (ADR 0030) · §22.2 (M3) · §24 (Phase 2)
- `phase0-reconciliation-table-2026-09-29.md` — 8-qator (faza + migratsiya nomuvofiqligi)
- ADR 0031 (event schema) · ADR 0023 (indekslash)

**STATUS:** ADR 0030 — accepted. Phase 0; `User.origin` (Attempt'siz); `imported` alohida; `neytron_*` saqlanadi.
