# WP1 — Content Readiness implementatsiya kontrakti

**Sana**: 2026-09-29
**Muallif**: Software Company — Architect (Bob)
**Holat**: 🟢 Tayyor — Engineer uchun ijro kontrakti (dizayn, kod emas)
**Til qoidasi**: Hujjat **o'zbek (lotin)** tilida. Texnik atama, fayl yo'li va kod **inglizcha** qoladi.
**Asos hujjatlar**:
- `deliverables/independent-review-board/acceptance-criteria-lock-2026-09-29.md` — WP1 bloki (6 mezon)
- `deliverables/independent-review-board/owner-decision-ledger-2026-09-29.md` — D8 · D8-F yozuvlari
- `docs/07-adr/0037-content-integrity-gate.md` — tanlangan variant (minimal readiness)
- `deliverables/engineering-assurance/system-design-phase0-decision-closure-2026-09-29.md` §6 — holat-mashinasi · R1–R10 · Q20
- `deliverables/software-company/implementation-plan-phase0-2026-09-29.md` — T-WP1.1…T-WP1.4

> ⚠️ Bu kontrakt **muzlatilgan qarorlarni qayta talqin qilmaydi**. Har da'vo `fayl:satr` bilan o'lchandi. Zid chiqsa — pastdagi «Reja xatolari» bo'limiga qarang.

---

## 1. O'lchangan repo faktlari (2026-09-29)

| # | Fakt | Manba |
|---|---|---|
| 1 | `Problem.is_public = BooleanField(default=False, db_index=True)` | `apps/api/problems/models.py:229` |
| 2 | `Problem.Meta`: `ordering=["difficulty","slug"]`, bitta indeks `problem_public_diff (is_public,difficulty)` | `apps/api/problems/models.py:259-263` |
| 3 | `Problem.save()` → `_save_with_code()`; `code` faqat `is_public=True` bo'lganda beriladi | `apps/api/problems/models.py:268-299` |
| 4 | `Problem.clean()` — **faqat** `difficulty % 100` ni tekshiradi (readiness gate **yo'q**) | `apps/api/problems/models.py:309-313` |
| 5 | `TestCase`: `order`, `is_sample` (:350), `origin` (`author`/`hack`) | `apps/api/problems/models.py:336-364` |
| 6 | `Validator` — OneToOne `related_name="validator"` | `apps/api/problems/models.py:429-444` |
| 7 | **`ReferenceSolution` MAVJUD** — OneToOne `related_name="reference_solution"`, `language`, `source` | `apps/api/problems/models.py:447-474` |
| 8 | `problems/migrations/` eng oxirgi fayl = **`0022_problem_authors.py`** | `apps/api/problems/migrations/` |
| 9 | **Qisman publish gate MAVJUD** — `StaffProblemSerializer.validate()`: e'lon uchun test **bor** + `is_sample=False` **kamida bitta** bo'lishi shart; arxiv masalalari (allaqachon public) qayta tekshirilmaydi | `apps/api/problems/staff_serializers.py:99-131` |
| 10 | Staff `is_public` ni shu serializer orqali o'zgartiradi (nashr shu yerdan o'tadi) | `apps/api/problems/staff_views.py:112-129` |
| 11 | Etalon yechim endpointi: `PUT staff/problems/<slug>/reference-solution/` | `apps/api/problems/staff_views.py:231-237` |
| 12 | `Contest` da **`graded` bayrog'i YO'Q**; mavjud: `is_rated` (:33), `scoring_type` (:30), `is_public` (:35) | `apps/api/contests/models.py:16-73` |
| 13 | `ContestProblem(contest, problem, index_letter, points)` — masalani contestga ulash nuqtasi | `apps/api/contests/models.py:109-125` |
| 14 | **Asosiy ulash nuqtasi** — `StaffContestViewSet.problems` amali; `ContestProblem.objects.bulk_create(...)` | `apps/api/contests/staff_views.py:52-79` (bulk_create `:66-77`) |
| 15 | Ro'yxat serializatori — `StaffContestProblemListSerializer.validate_problems` (400 shu yerdan chiqadi) | `apps/api/contests/staff_serializers.py:66-78` |
| 16 | Ommaviy (o'qish) serializatori `ContestProblemSerializer` — gate nuqtasi **EMAS** | `apps/api/contests/serializers.py:11-17` |
| 17 | **Ikkinchi ulash nuqtasi** — `create_mirror()` `ContestProblem.objects.bulk_create(...)` | `apps/api/contests/services.py:285-295` |
| 18 | Judge provider: `RedisJudgeProvider.submit` → `lpush(JUDGE_JOBS_KEY)`; `poll` → `brpop(JUDGE_RESULTS_KEY)` | `apps/api/judging/provider.py:76-96` |
| 19 | `InMemoryJudgeProvider` + `set_provider()` — testlar uchun | `apps/api/judging/provider.py:99-133` |
| 20 | `build_job(attempt, validate_input=False)` — `Attempt` dan `JudgeJob` quradi (masala testlari + checker + limits) | `apps/api/judging/services.py:21-108` |
| 21 | `drain_results` marshruti: `hack_id` → hack; `custom_run_id` → custom; aks holda `apply_result` (attempt_id bo'yicha) | `apps/api/judging/tasks.py:44-55` |
| 22 | `Verdict`: `AC`, `WA`, `RE_SIGNAL`, `RE_EXIT`, `CE`, `PE`, `PARTIAL`, `IE`, `WRONG_TEST`, … | `apps/api/judging/verdicts.py:8-38` |
| 23 | Testlar — pytest + `@pytest.mark.django_db`; `memory_judge` fixture navbatni `InMemoryJudgeProvider` ga almashtiradi | `apps/api/tests/conftest.py:118-124` |
| 24 | `problem` fixture — `is_public=True` + 1 test; `contest` fixture — `is_rated=True` + 1 `ContestProblem` | `apps/api/tests/conftest.py:148-191` |
| 25 | **`tests/regression/` papkasi YO'Q** (U6 tasdiqlandi) | `tests/regression/` (glob — natija yo'q) |

---

## 2. Holat-mashinasi

**Holatlar (enum):** `draft` · `needs_tests` · `has_hidden_tests` · `checker_validated` · `ref_solution_verified` · `validated` · `legacy_unverified` · `blocked` · `needs_review`.

| Holat | O'tish | Trigger | Shart |
|---|---|---|---|
| `draft` (boshlang'ich) | → `needs_tests` | staff (test yuklaydi) | masalada kamida 1 `TestCase` bor |
| `needs_tests` | → `has_hidden_tests` | staff (test yuklaydi) | kamida 1 `is_sample=False` test bor |
| `has_hidden_tests` | → `checker_validated` | staff (masala saqlanadi) | checker turi to'liq (pastga qarang) |
| `checker_validated` | → `ref_solution_verified` | **harness** (`manage.py verify_readiness`) | etalon yechim barcha testlarda **AC** |
| `ref_solution_verified` | → `validated` | **staff** (insoni tasdiq) | sample-echo **≠ AC** (harness dalili) + staff qo'l qo'yadi |
| `validated` | — (terminal, graded-eligible) | — | — |
| `*` (public, tuzatilmagan) | → `legacy_unverified` | **M1 backfill** | `is_public=True` **va** yashirin test yo'q |
| `*` (public, qisman tayyor) | → `needs_review` | **M1 backfill** | `is_public=True` **va** yashirin test bor (harness o'tmagan) |
| har qanday | → `blocked` | **harness** | sample-echo **AC** berdi (masala buzuq) |
| `blocked` | → `needs_review` | staff (tuzatgandan keyin) | staff qayta ko'rikni boshlaydi |
| `needs_review` | → `checker_validated` (qayta) | staff | checker qayta tekshirildi |

**Taqiqlangan o'tishlar (rad etiladi):**
- `draft → validated` (yoki istalgan **sakrash**) → `ValidationError` (R10).
- `blocked → validated` to'g'ridan-to'g'ri → faqat `needs_review` orqali.
- `legacy_unverified → validated` to'g'ridan-to'g'ri → avval `needs_review`, keyin zanjir.

---

## 3. Readiness maydoni kontrakti

**Joy:** `apps/api/problems/models.py` — `Problem` ichida, `is_public` (:229) **ostida**.
**Tip:** `TextChoices` (repo naqshi: `Problem.Checker` · `ProblemReport.Status` · `Verdict`).

```python
class Problem(TimeStampedModel):
    class Readiness(models.TextChoices):
        DRAFT = "draft", "Qoralama"
        NEEDS_TESTS = "needs_tests", "Test kerak"
        HAS_HIDDEN_TESTS = "has_hidden_tests", "Yashirin test bor"
        CHECKER_VALIDATED = "checker_validated", "Checker tekshirilgan"
        REF_SOLUTION_VERIFIED = "ref_solution_verified", "Etalon tekshirilgan"
        VALIDATED = "validated", "Tasdiqlangan"
        LEGACY_UNVERIFIED = "legacy_unverified", "Arxiv (tekshirilmagan)"
        BLOCKED = "blocked", "Bloklangan"
        NEEDS_REVIEW = "needs_review", "Ko'rik kerak"

    readiness = models.CharField(
        max_length=24, choices=Readiness.choices, default=Readiness.DRAFT, db_index=True
    )
```

**Doimiy qoidalar:**
- `default=Readiness.DRAFT` — yangi masala har doim qoralamadan boshlanadi.
- `db_index=True` — remediatsiya dashboardi `readiness` bo'yicha filtrlaydi (Q20).
- `legacy_unverified` **`is_public=True` bilan birga yashaydi** (D8-F) — maydon `is_public` ni **almashtirmaydi**, faqat to'ldiradi.
- Indeks (ixtiyoriy, tavsiya): `models.Index(fields=["readiness", "is_public"], name="problem_readiness_pub")` — Q20 hisobi uchun.
- **`clean()` kengaytiriladi**: `clean()` (:309-313) ga holat-o'tish validatsiyasi qo'shiladi (sakrashni model darajasida ham to'sadi, R10).

---

## 4. Semantik validatsiya mezoni (operatsion ro'yxat)

> **D8 qat'iy talabi:** mezon **semantik, son emas**. «≥5 yashirin test» kabi **o'zboshimchalik soni TAQIQLANADI**. Quyidagi to'rt band — bajariladigan shartlar.

`validated` holatiga **faqat** quyidagi **to'rt band** bir vaqtda bajarilganda o'tiladi:

| # | Band | Tekshiriladi | Qayerda |
|---|---|---|---|
| **S1** | **Yashirin test MAVJUD** | `problem.tests.filter(is_sample=False).exists()` — **mavjudlik**, son emas | `problems/readiness.py` |
| **S2** | **Checker turi mos** | `standard` → qo'shimcha shart yo'q; `special`/`scorer` → `checker_source` **va** `checker_language` bor; `interactive` → `interactor_source` **va** `interactor_language` bor | `problems/readiness.py` |
| **S3** | **Etalon yechim AC** | `ReferenceSolution` bor **va** barcha testlarda verdict = `AC` (harness) | `manage.py verify_readiness` |
| **S4** | **Sample-echo ≠ AC** | namunaviy chiqishni chop etuvchi dastur **`AC` OLMAYDI** (harness) | `manage.py verify_readiness` |

**Rad etish:** S1 yoki S2 bajarilmasa → holat oldinga o'tmaydi (tegishli holatda qoladi). S3 yoki S4 bajarilmasa → `blocked` (masala buzuq: namunani chop etish bilan yechiladi).

**Nega son emas:** chegara masala turiga bog'liq (interaktiv masalada bitta yashirin test yetarli bo'lishi mumkin, murakkab masalada o'nlab kerak). Semantik shart — «namunani ko'chirib `AC` olish **mumkin emas**» — aynan mahsulot yadrosini himoya qiladi (`print('3 2 1')` → AC muammosi).

---

## 5. Gibrid trigger

| O'tish | Trigger | Turi | Nega |
|---|---|---|---|
| `draft → needs_tests` | staff (test yuklash) | **inson** | Test mazmunini odam yozadi |
| `needs_tests → has_hidden_tests` | staff (test yuklash) | **inson** | Yashirin testni odam qo'shadi |
| `has_hidden_tests → checker_validated` | staff (saqlash) | **inson** (avtomatik tekshiruv bilan) | S2 statik — saqlashda avtomatik |
| `checker_validated → ref_solution_verified` | **harness** | **avtomatik** | S3 — judge hukmi (tez, obyektiv) |
| `ref_solution_verified → validated` | **staff** | **inson** | S4 dalili + insoni tasdiq (ishonch) |
| `→ blocked` | **harness** | **avtomatik** | S4 buzildi — mashina aniqlaydi |
| `blocked → needs_review` | staff | **inson** | Tuzatishdan keyin qayta ko'rik |

**Gibrid naqsh:** harness **tez va obyektiv** qismni (S3 · S4) bajaradi; staff **ishonch** qismini (yakuniy tasdiq) beradi. Avtomatik qism inson xatosini kamaytiradi, inson qismi harness'ni aldamchi holatlardan himoya qiladi.

---

## 6. `legacy_unverified` aniqlash so'rovi

**Ta'rif:** `is_public=True` **va** yashirin (`is_sample=False`) testi **yo'q** masalalar.

**ORM:**
```python
from django.db.models import Count, Q
legacy = (
    Problem.objects.filter(is_public=True)
    .annotate(hidden=Count("tests", filter=Q(tests__is_sample=False)))
    .filter(hidden=0)
)
```

**SQL (dalil uchun):**
```sql
SELECT p.id FROM problems_problem p
WHERE p.is_public
  AND NOT EXISTS (
    SELECT 1 FROM problems_testcase t
    WHERE t.problem_id = p.id AND t.is_sample = false
  );
```

**M1 backfill taqsimoti (loyiha raqamlari):**

| Guruh | Shart | Yangi `readiness` | Kutilgan son |
|---|---|---|---|
| A | `is_public=True` **va** yashirin test yo'q | `legacy_unverified` | **1 222** |
| B | `is_public=True` **va** yashirin test bor | `needs_review` | ~4 (1 226 − 1 222) |
| C | `is_public=False` | `draft` | qolgani |

> **Mezon ③** `SELECT count(*) WHERE is_public AND readiness IS NULL` = **0** — M1 backfill barcha public masalaga qiymat beradi (A + B), C esa `draft` oladi. NULL qolmaydi.

---

## 7. D8-F qulfi (ikki talab bir vaqtda)

**D8-F:** `legacy_unverified` masala **public qoladi**, lekin **graded contestga kiritilmaydi**.

| Talab | Ta'minlanadi | Qayerda |
|---|---|---|
| **Public qoladi** | `is_public` **o'zgarmaydi**; M1 backfill faqat `readiness` yozadi; mavjud publish gate (:99-131) **faqat o'tishda** ishlaydi, allaqachon public yozuvga tegmaydi | `apps/api/problems/models.py:229` · `staff_serializers.py:112-115` |
| **Contestga kirmaydi** | Ulash nuqtasida `problem.readiness != validated` → **400** | `contests/staff_serializers.py:66-78` · `contests/staff_views.py:66` · `contests/services.py:285-295` |

**Muhim dizayn qoidasi:** `is_public` **`readiness` ga bog'lanmaydi**. Aks holda 1 222 arxiv masalasi majburan private bo'lardi va D8-F buzilardi. Ya'ni: **public ko'rinish ≠ graded eligibility** — ikki alohida gate.

**«Graded contest» ta'rifi (operatsion):** `ContestProblem` qatori mavjud istalgan `Contest` — ya'ni har bir contest baholanadi (standings hisoblanadi). Practice (contestdan tashqari yechish) baholanmaydi. Shuning uchun gate **ulash nuqtasida** turadi, submit oqimida emas.

---

## 8. Ref-solution harness dizayni

**Ikki qavat (test + real judge):**

**8.1 Sof funksiya (testlanadigan, judgesiz):**
```python
# apps/api/problems/readiness.py
def evaluate_readiness(problem, *, ref_verdict, echo_verdict, previous) -> str:
    """Judge natijalaridan keyingi readiness holatini hisoblaydi (judgesiz test)."""
    if not _has_hidden_test(problem):          # S1
        return previous
    if not _checker_ok(problem):               # S2
        return previous
    if echo_verdict == Verdict.AC:             # S4 buzildi
        return Problem.Readiness.BLOCKED
    if ref_verdict != Verdict.AC:              # S3 buzildi
        return Problem.Readiness.BLOCKED
    return Problem.Readiness.REF_SOLUTION_VERIFIED
```

**8.2 Judge bilan gaplashish (1 qator):** harness **o'sha Redis navbati** orqali gapiradi — `judging.provider.get_provider().submit(JudgeJob(...))` bilan ish qo'yadi va `poll()` bilan natijani oladi; testlarda `InMemoryJudgeProvider` (mavjud `memory_judge` fixture) qo'yiladi.

**8.3 Job qurilishi:** `build_job()` `Attempt` talab qiladi (:21). Harness **`Attempt` yaratmaydi** (urinishlar tarixi va reyting ifloslanmasin). `judging/services.py:enqueue_custom` (:135-157) naqshidan foydalanib, **mustaqil** `JudgeJob` quriladi: masala testlari, `checker`, `mode="acm"`, `attempt_id=0`.

**8.4 Marshrutlash diqqati:** `drain_results` (:44-55) `attempt_id=0` va `hack_id`/`custom_run_id` yo'q natijani `apply_result` orqali **jimgina tashlab yuboradi** — ya'ni beat ishlab tursa harness natijasini «o'g'irlaydi». Shuning uchun real-judge rejimi **bake-off intizomi** bilan yuritiladi: `worker beat` **to'xtatilgan** holda (CI/nightly). Testlarda navbat allaqachon `InMemoryJudgeProvider`.

**8.5 Buyruq:** `python manage.py verify_readiness <slug>` (yangi management command) — etalon yechimni yuboradi (S3), sample-echo programmasini yuboradi (S4), natijaga qarab `ref_solution_verified` / `blocked` yozadi.

---

## 9. `neg_refsolution_gate` dizayni

**Muzlatilgan siyosat:** «hech qachon yiqilmaydigan tekshiruv qabul qilinmaydi». Har yangi gate uchun **salbiy (mutatsiya) testi majburiy**.

| # | Nima buziladi (mutatsiya) | Qaysi test **qizil** bo'lishi SHART | Qavat |
|---|---|---|---|
| **M-A** | `evaluate_readiness` dan S4 (`echo_verdict == AC` sharti) olib tashlanadi | `test_sample_echo_is_not_ac` | gate (sof funksiya) |
| **M-B** | `StaffContestProblemListSerializer.validate_problems` (:66-78) dan readiness tekshiruvi olib tashlanadi | `test_graded_requires_validated` (R8) | data (serializer) |

**Ikki qavat nega:** birinchi qavat **kod** yo'lini tutadi; ikkinchi qavat **serializer'ni chetlab o'tgan** yozuvni ham tutadi (masalan `create_mirror` yo'li). Bittasi yetmaydi.

**Mexanizm:** `tools/check_negative.py` ga yangi guruh qo'shiladi (mavjud naqsh: fayl vaqtincha `Mutation` bilan o'zgartiriladi, test yurgiziladi, **qizil bo'lmasa** — gate yiqiladi). Manba: assurance §6 (:265).

---

## 10. R1–R10 test matritsasi

| # | Test | Fayl | Nimani tekshiradi |
|---|---|---|---|
| R1 | `test_default_readiness_is_draft` | `apps/api/tests/test_problem_readiness.py` | Yangi masala `draft`; `is_public=False` |
| R2 | `test_publish_without_tests_is_400` | `test_problem_readiness.py` | Testsiz e'lon → **400** (mavjud gate :116-119 saqlanadi) |
| R3 | `test_publish_without_hidden_test_is_400` | `test_problem_readiness.py` | Faqat namuna test bilan e'lon → **400** (mavjud gate :124-130) |
| R4 | `test_transition_forward_step_ok` | `test_problem_readiness.py` | To'g'ri qadam (`needs_tests → has_hidden_tests`) qabul qilinadi |
| R5 | `test_checker_type_required` | `test_problem_readiness.py` | `special`/`scorer` checker dasturisiz `checker_validated` ga **o'tmaydi** (S2) |
| R6 | `test_reference_solution_is_ac` | `tests/regression/test_ref_solution_verdicts.py` | Etalon yechim `AC` → `ref_solution_verified` (S3) |
| R7 | `test_sample_echo_is_not_ac` | `tests/regression/test_ref_solution_verdicts.py` | Namunani chop etish `AC` bersa → **`blocked`** (S4) |
| R8 | `test_graded_requires_validated` | `apps/api/tests/test_problem_readiness.py` | `validated` bo'lmagan masalani contestga ulash → **400** |
| R9 | `test_legacy_unverified_public_but_not_in_contest` | `test_problem_readiness.py` | `legacy_unverified` public ko'rinadi, contestga ulash → **400** (D8-F) |
| R10 | `test_draft_to_validated_jump_rejected` | `test_problem_readiness.py` | `draft → validated` sakrash → **`ValidationError`** |

**Test infratuzilmasi:** pytest + `@pytest.mark.django_db`; `memory_judge` fixture (:118-124) judgesiz ishlaydi; `problem` (:148) va `contest` (:180) fixture'lari qayta ishlatiladi; yangi `tests/regression/` papkasi (`__init__.py`, `conftest.py`, `README.md`, `test_ref_solution_verdicts.py`) — **hozir yo'q** (U6).

---

## 11. M1 forward yo'l

| Qadam | Fayl | Amal | Oraliq holat xavfsizmi |
|---|---|---|---|
| **add** | `apps/api/problems/migrations/0023_problem_readiness.py` | `AddField` — `readiness` **nullable** (`null=True`, default yo'q) | ✅ Ha — eski kod ishlayveradi, maydon `NULL` |
| **backfill** | `apps/api/problems/migrations/0024_backfill_readiness.py` | `RunPython`: A → `legacy_unverified`, B → `needs_review`, C → `draft`; so'ng `AlterField` → **NOT NULL**, `default=draft` | ✅ Ha — avval qiymat yoziladi, keyin cheklov |
| **switch** | `0024` ichida (yoki alohida `0025`) | `AlterField` NOT NULL + `CheckConstraint` (`is_public=False OR readiness IS NOT NULL`) | ✅ Ha |

**Raqamlar tasdiqlandi:** eng oxirgi mavjud migration — **`0022_problem_authors.py`** → rejadagi **0023 / 0024 TO'G'RI**.

**Muhim:** data migration **judge'ni ishga tushirmaydi** — S3/S4 (harness) M1 da bajarilmaydi. Shu sabab hech bir masala M1 da `validated` **bo'lmaydi**; remediatsiya keyingi ish.

---

## 12. Xavf va rollback

| Xavf | Sabab | Aniqlash | Yumshatish |
|---|---|---|---|
| **Backfill noto'g'ri default** | A guruhi (1 222) `legacy_unverified` o'rniga `validated` olsa — ishonchsiz masala contestga kirar | `test_graded_requires_validated` (R8) · R9 | M1 dan oldin U3 (jonli kontent raqamlari) + U5 (throughput) olinadi; backfill **faqat** statik shartlarni o'qiydi (judge chaqirmaydi) |
| **Hamma masala bloklanadi** | A+B guruhi noto'g'ri hisoblansa graded contest masalasiz qoladi | Q20 hisobi: `validated` soni | Forward-fix (qayta backfill); deploy-oldi **dump** shart |
| **`is_public` majburan private** | Agar `is_public` `readiness` ga bog'lansa — D8-F buziladi | R9 | `is_public` **readiness ga bog'lanmaydi** (§7) |
| **Harness natijasi o'g'irlanadi** | `drain_results` beat ishlab tursa `attempt_id=0` natijani yutadi | Natija kelmaydi / `blocked` | Real-judge rejimi `worker beat` to'xtatilgan holda (§8.4) |
| **Darvozalar o'lik bo'lib qoladi** | Salbiy test yozilmasa | `neg_refsolution_gate` yashil qolsa | M-A + M-B majburiy (§9) |

**Rollback:** forward-only (M1). Mumkin — qayta backfill yoki maydonni bo'shatish; oxirgi chora — `pg-deploy-*.sql.gz` dump'ni **qo'lda** tiklash. Mumkin emas — `git revert` bilan sxema qaytarish.

---

## 13. Reja xatolari

| # | Qayerda | Yozilgan | Haqiqat (o'lchandi) | Harakat |
|---|---|---|---|---|
| 1 | `implementation-plan` T-WP1.3 · §5 | Gate fayli: `apps/api/contests/serializers.py` | Bu **ommaviy o'qish** serializatori (:11-17) — gate nuqtasi **EMAS**. Haqiqiy nuqta: `contests/staff_serializers.py:66-78` + `contests/staff_views.py:66` + `contests/services.py:285-295` | Reja fayl ro'yxatini tuzatish |
| 2 | blueprint §730 · `docs/...` | Backfill mezoni: `validated` **faqat ≥5 non-sample test** bo'lsa | D8 «**son emas, semantik**» deydi — «≥5» **taqiqlangan** son | **D8 ustun**; §4 dagi S1–S4 semantik mezon qo'llanadi |
| 3 | blueprint §730 | `readiness`: `draft → validated → published` | `published` — `is_public` bilan ustma-ust tushadi; D8-F talabi bilan `legacy_unverified` qo'shiladi | §2 holat-mashinasi (9 holat) ustun |
| 4 | `implementation-plan` §6 (M1) | Forward: `add → backfill → switch`, **har qadam alohida deploy** | Fayl ro'yxati faqat **2** migration (0023 · 0024) beradi | Kontrakt: 0023 = add; 0024 = backfill + switch (yoki alohida 0025) — reja bilan mos |
| 5 | `implementation-plan` §7 | Ref-solution harness → `tests/regression/` | Papka **yo'q** (U6) — yaratiladi | Tasdiqlandi, tuzatish shart emas |

> **D8 bilan haqiqiy zid:** **faqat #2** (blueprint «≥5» ↔ D8 «son emas»). D8 muzlatilgan → **D8 ustun**, blueprint §730 soni **bekor**. Bu — blueprint ↔ qaror ziddi (reconciliation jadvali doirasida, yangi owner decision **talab qilmaydi**). Boshqa bandlar — fayl/atama tuzatishi.

---

**STATUS:** WP1 Content Readiness implementatsiya kontrakti — tayyor. 9 holatli mashina · semantik mezon (4 band, son emas) · gibrid trigger · `legacy_unverified` so'rovi · D8-F qulfi (ikki gate) · ref-solution harness (Redis navbat + `InMemoryJudgeProvider`) · `neg_refsolution_gate` (M-A · M-B) · R1–R10 · M1 (0023 + 0024). Reja xatolari: 5 (1 zid — blueprint «≥5» ↔ D8).
