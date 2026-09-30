# Problem Package — Current State Matrix

**STATUS:** living — PHASE 1 artefakti (PROMPT_0 bo'yicha)
**Sana:** 2026-09-30
**Baseline:** `main = b193b869`, umumiy 48%
**Maqsad:** 61 mezon, 10 bo'lim, 100%

Bu fayl **kod o'qish** asosida tuzildi. Har bir qator: mavjud implementatsiya →
fayl → runtime yo'l → yetishmayotgan behavior → risk → kerakli ish → test.

---

## PHASE 0 — Runtime yo'llar (kod bilan tasdiqlangan)

| Savol | Javob | Fayl |
|---|---|---|
| Problem qanday yaratiladi? | `POST /api/v1/staff/problems/` (StaffOps), `is_public` read-only, `code` publish'da beriladi | `problems/staff_views.py`, `problems/models.py:315` |
| Problem qanday edit qilinadi? | `PATCH /api/v1/staff/problems/<slug>/`; `validate()` statement/publish qoidalarini tekshiradi | `problems/staff_serializers.py:105` |
| Test qanday yuklanadi? | `POST /api/v1/staff/problems/<slug>/tests/` → `storage.put_test_data("tests/<slug>/<order>.in")` → S3; DB'da faqat havola | `problems/staff_views.py:136`, `problems/storage.py:57` |
| Test qanday judge qilinadi? | `build_job()` → Redis navbat → `judge-go` PULL → `apply_result()` | `judging/services.py:21,240` |
| Validator qayerda ishlaydi? | `judge-go/validator.go` — **sandbox ICHIDA** (kiritmasi ishonchsiz); job'ga faqat `validate_input=True` bo'lsa biriktiriladi | `judging/services.py:82-96` |
| Checker qayerda ishlaydi? | `judge-go/checker.go` (`special`/`scorer`), `interactive.go` (`interactive`); sandboxsiz (ishonchli dastur) | `services/judge-go/judge.go:265` |
| Reference solution qanday tekshiriladi? | `manage.py verify_readiness` — S3 (ref AC) + S4 (echo not AC), `build_standalone_job` bilan, `Attempt` yaratmaydi | `problems/management/commands/verify_readiness.py` |
| Publish qanday sodir bo'ladi? | `PATCH is_public=true`; gate: kamida 1 test + e'lon qilishda kamida 1 yashirin test | `problems/staff_serializers.py:111-130` |
| Hack flow qanday? | `hacks/` — `Hack`, `HackRoom`, `HackLock`, `policies.py`; hack testi `TestCase.origin=hack` bo'lib qo'shiladi | `hacks/models.py`, `problems/models.py:395` |
| Submission qanday judge qilinadi? | `Attempt` → `enqueue()` → Redis → judge → `apply_result()` → `RatingHistory` | `judging/services.py:137,240` |

**Invariantlar (koddan):**
- `Attempt` **problem revision'ga bog'lanmagan** — faqat `problem` FK
- `TestCase.origin` = `author` | `hack` — bu **manba**, guruh emas
- `Problem.readiness` — 9 holatli sifat holati (`problems/readiness.py`)
- Judge DB credential'ga ega emas (PULL protokoli, ADR-0028)

---

## PHASE 1 — Criterion matrix

### §1 Masala paketi (9 komponent) — 68.3%

| Criterion | Current | Files | Missing | Risk | Required | Status |
|---|---|---|---|---|---|---|
| 1.1 Statement maydonlari | `statement`, `input_format`, `output_format`, `note`, `statement_locale` | `problems/models.py` | — | — | — | **PASS** |
| 1.2 Statement to'liqlik darvozasi | yo'q | — | `input_format` bo'sh bo'lsa ham publish bo'ladi | Bo'sh shart nashr bo'ladi | publish gate + error kodlari | **FAIL** |
| 1.3 Test data modeli | `TestCase` + S3 + upload API | `problems/models.py:402` | — | — | — | **PASS** |
| 1.4 Test guruh tasnifi | faqat `is_sample` | `problems/models.py:411` | MINIMAL…STRESS | Guruh bo'yicha siyosat yo'q | `group` maydoni + taxonomy | **FAIL** |
| 1.5 Validator | model + judge + sandbox | `problems/models.py`, `judge-go/validator.go` | majburiy emas | O'lik yo'l | domain policy | **PARTIAL** |
| 1.6 Reference solution | model + S3 harness | `problems/models.py`, `readiness.py` | — | — | — | **PASS** |
| 1.7 Checker | 4 tur + judge | `judge-go/checker.go` | har masala uchun test yo'q | Buzuq checker → noto'g'ri AC | checker verification | **PARTIAL** |
| 1.8 Generator | **yo'q** | — | hammasi | Test sifati qo'lda | generator framework | **FAIL** |
| 1.9 Quality tests | S4 echo | `readiness.py` | brute/stress/wrong | Zaif testlar | quality framework | **FAIL** |
| 1.10 Editorial | `editorial` + narx + qulf | `problems/models.py:282,579` | — | — | — | **PASS** |
| 1.11 Metadata | difficulty/topics/authors/limits/source | `problems/models.py` | package revision | — | revision bilan versioned | **PARTIAL** |

### §2 Validator/Checker/Interactor — 81.7%

| Criterion | Current | Missing | Status |
|---|---|---|---|
| 2.1 Validator determinizm/timeout/memory | `validator.go` sandbox bilan | policy hujjatlashtirilmagan | **PARTIAL** |
| 2.2 Validator test suite | `validator_test.go` bor | VALID/INVALID/EDGE/RESOURCE_LIMIT to'liq emas | **PARTIAL** |
| 2.3 Checker turlari | 4 tur ishlaydi | exit-code semantikasi testi | **PARTIAL** |
| 2.4 Interactor | `interactive.go` | protokol buzilishi testi | **PARTIAL** |
| 2.5 Job payload backward compat | `protocol.go` — `omitempty` maydonlar | — | **PASS** |

### §3 Test data guruhlari — 12.5%

| Criterion | Current | Missing | Status |
|---|---|---|---|
| 3.1 SAMPLE | `is_sample` | — | **PASS** |
| 3.2 MINIMAL…STRESS (7 guruh) | **yo'q** | model + API + pipeline | **FAIL** |
| 3.3 Guruh → ko'rinish siyosati | `is_sample` bilvosita | aniq siyosat | **FAIL** |

### §4 Reference / wrong / brute / alternative — 24%

| Criterion | Current | Missing | Status |
|---|---|---|---|
| 4.1 Reference | bor | — | **PASS** |
| 4.2 Brute-force / alternative / slow / wrong | **yo'q** | role/type enum + framework | **FAIL** |

### §5 Limitlar — 55%

| Criterion | Current | Missing | Status |
|---|---|---|---|
| 5.1 Limit maydonlari | `time_limit_ms`, `memory_limit_kb`, `ProblemLanguage` | — | **PASS** |
| 5.2 Til parametrlari | `Language` (compile/run/process_limit) | — | **PASS** |
| 5.3 Calibration pipeline | **yo'q** | o'lchov + evidence | **FAIL** |
| 5.4 JudgeEnvironment versioning | **yo'q** | model | **FAIL** |

### §6 Statement / editorial — 73.8%

| Criterion | Current | Missing | Status |
|---|---|---|---|
| 6.1 Maydonlar | bor | — | **PASS** |
| 6.2 To'liqlik validatsiyasi | yo'q | null/empty/whitespace/sample | **FAIL** |
| 6.3 Editorial | bor + qulf | revision-safe emas | **PARTIAL** |

### §7 Publication pipeline — 57.5%

| Criterion | Current | Missing | Status |
|---|---|---|---|
| 7.1 Draft | `Readiness.DRAFT` | — | **PASS** |
| 7.2 Test preparation | upload bor | guruh tekshiruvi | **PARTIAL** |
| 7.3 Validation | validator bor | publish'da majburiy emas | **PARTIAL** |
| 7.4 Reference verification | `verify_readiness` | — | **PASS** |
| 7.5 Checker verification | mutatsiya isboti (repo darajasi) | har masala uchun | **PARTIAL** |
| 7.6 Limit calibration | **yo'q** | — | **FAIL** |
| 7.7 Review | `needs_review` holati | workflow + actor | **PARTIAL** |
| 7.8 Publish | test gate bor | revision yo'q, atomik emas | **PARTIAL** |
| 7.9 Gate evidence (timestamp/actor) | yo'q | evidence model | **FAIL** |
| 7.10 "Why cannot publish?" | yo'q | stable error kodlari | **FAIL** |

### §8 Security / integrity — 64%

| Criterion | Current | Missing | Status |
|---|---|---|---|
| 8.1 nsjail sandbox | ADR-0028 | — | **PASS** |
| 8.2 Trusted author permissions | `StaffOps` | — | **PASS** |
| 8.3 Hidden test protection | S3 + `is_public` | — | **PASS** |
| 8.4 Upload size limit | **yo'q** (`CharField` max_lengthsiz) | limitlar | **FAIL** |
| 8.5 Path traversal / archive bomb | arxiv yo'q → tegishli emas | — | **N/A** |
| 8.6 Artifact hash | **yo'q** | manifest | **FAIL** |

### §9 Release checklist — 43.8%

| Criterion | Current | Missing | Status |
|---|---|---|---|
| 9.1–9.8 Kod darajasidagi gate | faqat test gate bor | 7 gate + error kodlari | **FAIL** |

### §10 Versioned Problem Package — 0%

| Criterion | Current | Missing | Status |
|---|---|---|---|
| 10.1 `ProblemRevision` | **yo'q** | hammasi | **FAIL** |
| 10.2 Published immutable | yo'q | freeze + enforcement | **FAIL** |
| 10.3 `Attempt` → revision | yo'q | FK | **FAIL** |
| 10.4 Hack → revision | yo'q | FK | **FAIL** |
| 10.5 Package manifest/hash | yo'q | hash-based integrity | **FAIL** |

---

## Arxitektura qarori: `Readiness` vs `ProblemRevision`

Prompt ogohlantiradi: "`ProblemRevision` bilan eski `Readiness`ni ma'nosiz ikki xil
lifecyclega aylantirma".

**Qaror: ular ORTOGONAL, ikkisi ham qoladi.**

- `Problem.readiness` — **kontent sifati** holati (S1–S4 bajarilganmi?). Bitta
  ishchi nusxa ustida ishlaydi.
- `ProblemRevision` — **muzlatilgan surat** (qaysi test/checker/limit bilan
  nashr qilingan?). Nashr qilingandan keyin o'zgarmaydi.

Ya'ni: `readiness=VALIDATED` → revision freeze qilinadi → `PUBLISHED`.
Bitta kanonik oqim, ikki xil savolga javob. Parallel state machine **yo'q**.

## Migratsiya rejasi (deterministik backfill)

| Qadam | Amal |
|---|---|
| M1 | `TestCase.group` qo'shiladi (default `SAMPLE` agar `is_sample`, aks holda `RANDOM`) |
| M2 | `ProblemRevision` + `ProblemRevisionTest` qo'shiladi |
| M3 | Har mavjud public problem uchun `Revision 1` yaratiladi (joriy holatdan surat) |
| M4 | `Attempt.problem_revision` (nullable) → mavjud attemptlar `Revision 1` ga |
| M5 | `Hack.problem_revision` (nullable) → xuddi shunday |
| M6 | `JudgeEnvironment` + `ProblemRevision.judge_environment` |

Barchasi **additive** — destruktiv emas, qaytarilishi mumkin.
