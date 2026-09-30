# ADR 0052 — Versiyalangan masala paketi va nashr darvozalari

**STATUS:** accepted
**Sana:** 2026-09-30
**Tasdiqlagan:** Saidakbar (owner)
**Manba:** PROMPT_0 §4 · §5 · §6 · §7 · §9 · §10
**Ta'sir doirasi:** `problems/release.py`, `problems/models.py`, `problems/staff_views.py`, `judging/models.py`
**Dalil:** o'lchov 2026-09-30 — `ProblemRevision` yo'q edi (§10 = 0%), release checklist kod darajasida emas edi (§9 = 43.8%)

## 1. Muammo

Ikki bo'shliq bir xil ildizga borib taqaladi: masala **o'zgaruvchan yozuv**,
paket emas.

- Nashr qilingan masala tahrirlansa, avvalgi natijalar yangi shart/testlar
  uchun ham haqiqiy deb qabul qilinardi (`Attempt` revision'ga bog'lanmagan).
- Release checklist hujjat edi, kod emas: «nima uchun nashr qilib bo'lmaydi?»
  degan savolga javob yo'q edi.

## 2. Variantlar

1. **Yangi `ProblemRevision` qatlami** — nashr qilingan paket muzlatiladi.
2. Masalani o'zgarmas qilish (tahrirni taqiqlash) — ishlamaydi, muallif
   xatoni tuzatishi kerak.
3. Har tahrirda versiya raqamini oshirish, surat saqlamasdan — tarixni
   tiklab bo'lmaydi.

## 3. Tanlov

**Variant 1**, plus shu yerda hal qilingan qo'shimchalar:

- `ProblemRevision` — paket surati (JSON) + xesh + status.
- `release.py` — 8 ta gate, barqaror xato kodlari.
- `LimitCalibration` + `JudgeEnvironment` — limitlarning dalili.
- `ProblemSolution` — yechim rollari (etalon / brute / alternativa /
  sekin / xato).

## 4. Sabab

- **Nashr qilingan paket o'zgarmasligi** — CP platformada integrity asosi.
- **`readiness` bilan zid emas:** `readiness` — kontent sifati (S1–S4),
  `ProblemRevision` — qaysi surat nashr qilingani. **Ortogonal.** Kanonik
  oqim bitta: `readiness=VALIDATED` → freeze → publish. Parallel state
  machine yaratilmaydi (PROMPT_0 to'g'ridan-to'g'ri shuni ogohlantiradi).
- **Surat JSON da:** revision yaxlit o'qiladi; test matni S3 da qoladi,
  ya'ni surat yengil va artefakt siljimaydi.
- **Xesh kalit tartibidan qat'i nazar barqaror** (`sort_keys`): aks holda
  kiritish tartibi o'zgarganda soxta mismatch chiqardi.
- **`Attempt.problem_revision` nullable:** eski urinishlar qaysi paketda
  yurgizilganini bilib bo'lmaydi; ularni «birinchi revision» deb yozish
  tarixni o'ylab topish bo'lardi. Shunday qoldi.

## 5. Oqibatlar

- `Problem.current_revision` — ommaviy API shu suratni ko'rsatadi.
- Muzlatilgandan keyin: testlar, statement, checker, validator, limitlar,
  editorial o'zgarishi = yangi revision.
- `publish` endi **transactional**: pointer almashinuvi va eski revision'ni
  `deprecated` qilish bitta tranzaksiyada.
- Gate'lar `READINESS_ENFORCE` (ADR 0050) bilan bir xil staged rollout'da
  ishlaydi — ya'ni legacy kontent to'sib qo'yilmaydi, lekin har bir chetlab
  o'tish logda qoladi.
- Barqaror kodlar: `STATEMENT_INCOMPLETE`, `TEST_GROUP_MISSING`,
  `VALIDATOR_NOT_VERIFIED`, `REFERENCE_FAILED`, `CHECKER_NOT_VERIFIED`,
  `LIMITS_NOT_CALIBRATED`, `REVIEW_REQUIRED`, `REVISION_NOT_FROZEN`.

### Ma'lum chegaralar (hal qilinmagan)

- **Generator framework (§1-06) — yo'q.** Keyingi faza.
- **Brute-force / stress avtomatik differensial tekshiruv (§7) —
  infrastruktura bor** (`ProblemSolution` rollari), lekin avtomatik
  yurgizuvchi command yo'q. Keyingi faza.
- **Validator/checker verification suite (§2) — qisman:** `verified_at`
  maydonlari va gate'lar bor, lekin ularni to'ldiradigan avtomatik
  tekshiruv command'i yo'q. Keyingi faza.

## 6. Qaytarilishi

Barcha migratsiya additive. `current_revision` / `problem_revision`
nullable — o'chirish eski xatti-harakatga qaytaradi.

## 7. Tasdiq

- `tests/test_release_and_revision.py` — 19 test: shart to'liqligi,
  8 gate, revision yaratish, freeze, xesh mutatsiyani aniqlashi, publish
  bloklanishi, versiya yagonaligi, API endpoint'lari.
- Regressiya to'plami (test_test_groups, test_problem_readiness,
  tests/regression) — 55 test, hammasi yashil.
