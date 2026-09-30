# ADR 0037 — Content integrity gate

**STATUS:** accepted
**Sana:** 2026-09-29
**Tasdiqlagan:** Saidakbar (owner)
**Manba:** D8 (ADR 0037 content readiness) · D8-F (legacy graded eligibility) · `owner-decision-closure-matrix-2026-09-29.md`
**Ta'sir doirasi:** Phase 0
**Dalil:** `apps/api/problems/models.py` (`is_public` bor, `readiness` **yo'q**) · `apps/api/problems/models.py` (`save()`/`clean()` — yashirin-test gate yo'q) · `apps/api/judging/verdicts.py` (verdict taksonomiyasi — allaqachon shipped)

## 1. Muammo

1 222 / 1 226 public masalada yashirin test yo'q. `Problem` da faqat `is_public` boolean bor (`apps/api/problems/models.py` — `Problem.is_public`); `readiness` maydoni yo'q va `save()`/`clean()` da (`Problem.save()`/`clean()`) yashirin-test gate yo'q. Oqibat: `print('3 2 1')` kabi yechim **AC** oladi — ya'ni reyting, contest va sertifikat ishonchsiz (mahsulot yadrosi yaroqsiz). 870 import masala IE qaytaradi; 200 ko'p-javobli masalada checker noto'g'ri.

## 2. Variantlar

1. Faqat publish-time to'siq (status quo).
2. `Problem.readiness` holat-mashinasi + gate.
3. Alohida `ProblemReadiness` modeli.
4. AI generatsiya.

## 3. Tanlov

**Variant 2** (D8) — **minimal** `Problem.readiness` holat-mashinasi. Uch xususiyat qat'iy:

1. **Holat-mashinasi minimal:** `draft → needs_tests → has_hidden_tests → checker_validated → ref_solution_verified → validated`; yon holatlar `blocked` va `needs_review`.
2. **Mezon — semantik, son emas:** validatsiya mezoni «≥5 yashirin test» kabi **o'zboshimchalik soni emas**, balki semantik shart (yashirin test mavjud + checker turi mos + ref-solution AC + sample-echo ≠ AC).
3. **Trigger — gibrid:** ref-solution **harness** + **staff** (inson tasdig'i) birgalikda.

**D8-F (qaytarilmaydigan siyosat):** `legacy_unverified` masala **public qoladi**, lekin **graded contestga kiritilmaydi**.

## 4. Sabab

Publish-time to'siq (variant 1) arxivni ushlamaydi — 1 222 masala «published» bo'lib qolaveradi. Alohida model (variant 3) ortiqcha murakkablik; AI generatsiya (variant 4) inson ko'rigini talab qiladi. Minimal holat-mashinasi remediatsiyani **kuzatiladigan** qiladi (nechtasi tuzatildi?) va graded contestni to'sadi. Son chegarasi («≥5») emas, semantik mezon tanlandi — chunki chegara masala turiga bog'liq bo'lib, o'zboshimchalik kiritadi. Gibrid trigger harness'ni tez, staff'ni ishonchli qiladi.

## 5. Oqibatlar

- `Problem.readiness` ustuni + holat-mashinasi; M1 migratsiya (`add → backfill → switch`).
- Arxiv 1 222/1 226 masala `legacy_unverified` ga backfill qilinadi.
- Graded contest `validated` bo'lmagan masalani rad etadi (400).
- `legacy_unverified` masala public ro'yxatda ko'rinadi, lekin contestda ishlatilmaydi (D8-F).
- Verdict taksonomiyasi **qayta yozilmaydi** — u allaqachon shipped (`apps/api/judging/verdicts.py`).

## 6. Qaytarilishi

Forward-only (M1). Rollback = qayta backfill yoki maydonni bo'shatish (forward). Deploy oldidan **dump** majburiy. Backfill default noto'g'ri bo'lsa hamma masala bloklanadi — shuning uchun U3 (jonli kontent raqamlari) va U5 (throughput) M1 dan oldin olinadi.

## 7. Tasdiq

- `test_sample_echo_is_not_ac` **yashil**; `neg_refsolution_gate` buzilganda **qizil** (salbiy test).
- `SELECT count(*) WHERE is_public AND readiness IS NULL` = **0**.
- Graded contest `validated` bo'lmagan masalani **400** bilan rad etadi.
- `legacy_unverified` masala public ko'rinadi, **contestda ishlatilmaydi**.
- Taxonomy qayta yozilmaydi (`check_verdict_codes.py` yashil).

## 8. Bog'liq hujjatlar

- D8 · D8-F — `owner-decision-closure-matrix-2026-09-29.md`
- `acceptance-criteria-lock-2026-09-29.md` — WP1 bloki
- Blueprint §21 (ADR 0037) · §22.2 (M1) · §24 (Phase 0)
- ADR 0030 (data origin) · ADR 0036 (AI data boundary)

**STATUS:** ADR 0037 — accepted. Phase 0; minimal readiness + semantik mezon + gibrid trigger; D8-F siyosati qaytarilmaydi.
