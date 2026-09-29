# RankWant — Phase 0 Implementation Plan + Task Decomposition

**Sana**: 2026-09-29
**Muallif**: Software Company — Architect (Bob)
**Holat**: 🟢 Tayyor — Engineer uchun ijroga tayyor (implementatsiya rejasi)
**Til qoidasi**: Hujjat **o'zbek (lotin)** tilida. Texnik atama, fayl yo'li va kod **inglizcha** qoladi.
**Asos hujjatlar**:
- `deliverables/software-company/implementation-prd-phase0-2026-09-29.md` — PM PRD (incremental)
- `deliverables/independent-review-board/acceptance-criteria-lock-2026-09-29.md` — muzlatilgan mezonlar
- `deliverables/independent-review-board/owner-decision-closure-matrix-2026-09-29.md` — qarorlar + scope freeze
- `deliverables/engineering-assurance/system-design-phase0-decision-closure-2026-09-29.md` — texnik asos
- `deliverables/software-architecture/software-architecture-rankwant-2026-09-29.md` — blueprint (§21–26)
- `deliverables/software-company/phase0-reconciliation-table-2026-09-29.md` — **authoritative** reconciliation (D2)

> ⚠️ Bu reja **muzlatilgan qarorlarni qayta ochmaydi**. Scope — **WP0–WP7 + D1**. Phase 1/3/4 ishlari oldindan hal qilinmaydi. Blueprint faza ro'yxati bilan zid chiqsa — reconciliation jadvali va §24 tie-break qoidasi ustun.

---

## 1. TL;DR

| Ko'rsatkich | Qiymat |
|---|---|
| Work package soni | **8** (WP0–WP7) + **1** cross-cutting (D1) |
| Jami task soni | **24** |
| Yangi fayl soni | **47** (shu jumladan 18 ADR) |
| O'zgaradigan fayl soni | **20** |
| Migration soni | **4** (M1 · M2 · M3 · M10) |
| Evidence gate soni | **1** (U1 — judge bake-off · PASS/FAIL) |
| Qo'shimcha o'lchov | **3** (U2 · U3 · U5) |
| CI'da yangi gate | **3** (`check_metrics` · `check_ai_boundary` · `check_architecture`) |
| Yangi salbiy (mutatsiya) guruh | **3** (`neg_refsolution_gate` · `neg_ai_boundary` · `neg_architecture`) |
| Taxminiy ijro tartibi | WP0 → (WP1 ∥ WP3 ∥ WP4 ∥ WP7) → WP5 → WP6; WP2 va D1 parallel |
| Kritik yo'l | WP0 → WP1 (inson-bound kontent) — eng uzun zanjir |

**Task taqsimoti (WP bo'yicha):** WP0 — 2 · WP1 — 4 · WP2 — 3 · WP3 — 3 · WP4 — 3 · WP5 — 2 · WP6 — 2 · WP7 — 3 · D1 — 2 = **24**.

---

## 2. Umumiy ijro tartibi (dependency graph)

```text
                    ┌──────────────────────────────┐
                    │ WP0  Reconciliation +        │  (hamma WPdan oldin)
                    │      migration/deploy siyosati│
                    └───────────────┬──────────────┘
                                    │
        ┌───────────────┬───────────┼────────────┬──────────────┐
        ▼               ▼           ▼            ▼              ▼
   ┌─────────┐    ┌─────────┐  ┌─────────┐  ┌─────────┐   ┌─────────┐
   │ WP1     │    │ WP3     │  │ WP4     │  │ WP7     │   │ D1      │
   │ content │    │ origin  │  │ secrets │  │ judge   │   │ ADR tili│
   │ (M1)    │    │ (M3)    │  │         │  │ (M2,U1) │   │         │
   └────┬────┘    └────┬────┘  └────┬────┘  └────┬────┘   └─────────┘
        │              │            │            │
        │  WP2 (M10) — mustaqil, WP1 bilan parallel (ikkalasi trust zanjiri)
        │              │            │            │
        └──────────────┴────────────┴────────────┘
                                    │
                                    ▼
                             ┌─────────────┐
                             │ WP5         │  0036 (AI boundary) — monolit modul
                             └──────┬──────┘
                                    │  KETMA-KET SHART: D6 → D7
                                    ▼
                             ┌─────────────┐
                             │ WP6         │  0042 (architecture allowlist)
                             └─────────────┘
```

**Bog'liqlik qoidalari:**
- **WP0 hammasidan oldin** — reconciliation authoritative; migration/deploy siyosati keyingi WP larga asos bo'ladi.
- **WP5 → WP6 ketma-ket SHART** — `check_architecture.py` allowlist AI joylashuvini (`apps/api/ai/`) **bilishi** kerak (D6 → D7). WP6 WP5 tugamaguncha boshlanmaydi.
- **WP1 (content) va WP7 (judge) mustaqil** — bir-biriga bog'liq emas; parallel boradi.
- **WP2** — shipped mexanizmlar ustida, mustaqil; WP1 bilan bir trust zanjirida.
- **WP3 · WP4 · WP7** — WP0 dan keyin **parallel** mumkin.
- **D1** — cross-cutting; ADR fayllari boshqa WP lar bilan parallel yoziladi (har ADR o'z WP komponentini hujjatlashtiradi).

---

## 3. Har WP uchun task decomposition

### WP0 — Reconciliation va migration siyosati (D2 · D11A · migration yo'q)

**Mazmun:** Reconciliation jadvali (D2) + migration/deploy siyosati (D11A).
**Bog'liq qaror:** D2 · D11A · **Migration:** — (yo'q)

| Task | Nima qilinadi | Fayl(lar) | Test | Gate |
|---|---|---|---|---|
| T-WP0.1 | Reconciliation jadvali + §24 tie-break qoidasini yozish (10 nomuvofiqlik qatori) | `deliverables/software-company/phase0-reconciliation-table-2026-09-29.md` (yangi) | `tools/check_docs.py` | `check_docs` |
| T-WP0.2 | Migration/deploy siyosatini qayd etish (forward-only · deploy-oldi dump · contest oyna) va `deploy.yml:230` chaqiruvini tasdiqlash | `deliverables/software-company/phase0-reconciliation-table-2026-09-29.md` §4 (yangi) | `tools/check_deploy_window.py` | `check_deploy_window` |

**Definition of Done:** Reconciliation jadvali artefakti mavjud; har nomuvofiqlik uchun qaror qayd etilgan; §24 tie-break qoidasi yozilgan; migration/deploy siyosati hujjatlashtirilgan; `check_docs.py` yashil.
**Xavf / rollback:** — (kod va migratsiya yo'q; faqat hujjat).
**Bog'liqlik:** — (birinchi WP).

### WP1 — Content readiness (D8 · D8-F · **M1**)

**Mazmun:** Minimal `Problem.readiness` + ref-solution harness + graded gate + `legacy_unverified` backfill.
**Bog'liq qaror:** D8 · D8-F · **Migration:** M1

| Task | Nima qilinadi | Fayl(lar) | Test | Gate |
|---|---|---|---|---|
| T-WP1.1 | `Problem.readiness` holat-mashinasi + model maydoni + `clean()` gate | `apps/api/problems/models.py` (o'zgartiriladi) · `apps/api/problems/readiness.py` (yangi) · `apps/api/problems/migrations/0023_problem_readiness.py` (yangi) | `apps/api/tests/test_problem_readiness.py` (yangi, R1–R10) | pytest (api job) |
| T-WP1.2 | `legacy_unverified` backfill (M1 data) + audit raqami | `apps/api/problems/migrations/0024_backfill_readiness.py` (yangi) · `apps/api/problems/management/commands/backfill_readiness.py` (yangi) | SQL: `is_public AND readiness IS NULL` = 0 | pytest · SQL |
| T-WP1.3 | Graded contest gate (`validated` bo'lmagan masala → 400) | `apps/api/contests/serializers.py` (o'zgartiriladi) · `apps/api/contests/services.py` (o'zgartiriladi) · `apps/api/problems/staff_views.py` (o'zgartiriladi) | `test_problem_readiness.py::test_graded_requires_validated` (R8) | pytest (api job) |
| T-WP1.4 | Ref-solution harness + `neg_refsolution_gate` salbiy test | `tests/regression/` (yangi papka: `__init__.py`, `conftest.py`, `README.md`, `test_ref_solution_verdicts.py`) · `tools/check_negative.py` (o'zgartiriladi) | `test_sample_echo_is_not_ac` · `neg_refsolution_gate` | `check_negative` |

**Definition of Done:** Readiness holat-mashinasi + M1 backfill + ref-solution harness + graded gate; `tests/regression/` harness yozilgan; `neg_refsolution_gate` qizil (salbiy test ishlaydi); `test_sample_echo_is_not_ac` yashil; graded contest `validated`sizni 400 bilan rad etadi; `legacy_unverified` public ko'rinadi, contestda ishlatilmaydi.
**Xavf / rollback:** M1 backfill (1 226 qator) default noto'g'ri bo'lsa hamma masala bloklanadi. **Rollback = forward-only** (readiness maydonini bo'shatish yoki qayta backfill). Deploy-oldi dump **shart**.
**Bog'liqlik:** T-WP1.1 → T-WP1.2 → T-WP1.3; T-WP1.4 T-WP1.1 dan keyin. WP0 tugagach.

### WP2 — Verdict taxonomy (faqat qolgan ish) (D11B · **M10**)

**Mazmun:** 4 o'lik kod nomlash + M10 tarixiy qayta yorliqlash.
**Bog'liq qaror:** D11B · **Migration:** M10

| Task | Nima qilinadi | Fayl(lar) | Test | Gate |
|---|---|---|---|---|
| T-WP2.1 | 4 o'lik verdict kodni nomlash + hujjatlashtirish | `apps/api/judging/verdicts.py` (o'zgartiriladi) · `docs/08-technical-spec/verdict-taxonomy-dead-codes.md` (yangi) | `check_verdict_codes.py` | `check_verdict_codes` |
| T-WP2.2 | M10 tarixiy qayta yorliqlash migratsiyasi (18 163 `RE` qator) | `apps/api/judging/migrations/0008_relabel_re_legacy.py` (yangi) | `apps/api/tests/test_verdict_taxonomy.py` (yangi) | pytest · `check_verdict_codes` |
| T-WP2.3 | Shipped mexanizmlarni (RE split · i18n parity) regressiyadan himoyalash | `apps/api/tests/test_verdict_taxonomy.py` (yangi) | i18n parity (10 til) testi | `check_verdict_codes` |

**Definition of Done:** 4 o'lik kod nomlangan va hujjatlashtirilgan; M10 migratsiyasi bajarilgan; `RE_SIGNAL`/`RE_EXIT` split va i18n parity **qayta yozilmagan** (shipped).
**Xavf / rollback:** 18 163 `RE` qator yorlig'i o'zgarsa 384 569 tarixiy `Attempt` bilan mos kelmasligi mumkin. **Rollback = forward-only** (yangi qayta yorliqlash). Deploy-oldi dump **shart**.
**Bog'liqlik:** Mustaqil; WP1 bilan parallel.

### WP3 — Data origin (D9 · **M3**)

**Mazmun:** `User.origin` + backfill + `check_metrics.py` (**`Attempt.origin` YO'Q**).
**Bog'liq qaror:** D9 · **Migration:** M3

| Task | Nima qilinadi | Fayl(lar) | Test | Gate |
|---|---|---|---|---|
| T-WP3.1 | `User.origin` enum + maydon (Attempt'siz) | `apps/api/core/models.py` (o'zgartiriladi) · `apps/api/core/migrations/0026_user_origin.py` (yangi) | `apps/api/tests/test_origin.py` (yangi) | pytest (api job) |
| T-WP3.2 | Origin backfill (M3) + audit raqami + seed user soni (U2) | `apps/api/core/management/commands/backfill_origin.py` (yangi) · data migration (M3) | `test_origin.py::test_backfill_audit` | pytest · SQL |
| T-WP3.3 | `check_metrics.py` — North Star `origin='real'` gate | `tools/check_metrics.py` (yangi) · `.github/workflows/ci.yml` (o'zgartiriladi) | `tools/check_negative.py` yangi guruh | `check_metrics` |

**Definition of Done:** `origin` ustuni + enum mavjud; `imported` alohida qiymat; M3 backfill + audit raqami chop etilgan; `check_metrics.py` CI'da exit 0; `Attempt.origin` **qo'shilmagan** (rad etilgan).
**Xavf / rollback:** Backfill 10 001 seed userni noto'g'ri tasniflasa segmentatsiya buziladi. **Rollback = forward-only**. Deploy-oldi dump **shart**.
**Bog'liqlik:** WP0 tugagach; mustaqil (parallel).

### WP4 — Secrets (D5 · migration yo'q)

**Mazmun:** Secrets: env + fail-fast + `security.yml` ON (rotation **keyin**).
**Bog'liq qaror:** D5 · **Migration:** — (yo'q)

| Task | Nima qilinadi | Fayl(lar) | Test | Gate |
|---|---|---|---|---|
| T-WP4.1 | Compose sirlarini env'ga o'tkazish + majburiy env (`${VAR:?}`) | `docker-compose.yml` (o'zgartiriladi) · `docker-compose.public.yml` (o'zgartiriladi) | grep: `PASSWORD: dev` va `devdevdev` → 0 natija | CI (api job) · grep |
| T-WP4.2 | `SECRET_KEY` fail-fast (`ImproperlyConfigured`) | `apps/api/config/settings.py` (o'zgartiriladi) | `apps/api/tests/test_settings_secrets.py` (yangi) | pytest |
| T-WP4.3 | `security.yml` `if: false` olib tashlash + rotation runbook (keyin) | `.github/workflows/security.yml` (o'zgartiriladi) · `docs/10-operations/runbooks/secrets-rotation.md` (yangi) | Security job yashil | Security workflow |

**Definition of Done:** `${VAR:?}` joriy etilgan; default sir bilan prod build **yiqiladi** (exit ≠ 0); `SECRET_KEY` fallback → `ImproperlyConfigured`; `security.yml` `if: false` olib tashlangan va CI yashil; rotation **wiring va fail-fast dan keyin**.
**Xavf / rollback:** `docker-compose.public.yml` ni o'zgartirish prod stack'ni buzishi mumkin. Rollback: env qiymatini `.env.public` ga qo'yish. Rotation **keyin** — tartib qulflangan.
**Bog'liqlik:** WP0 tugagach; mustaqil (parallel).

### WP5 — AI boundary (D6 · migration yo'q)

**Mazmun:** `check_ai_boundary.py` (modul chegarasi).
**Bog'liq qaror:** D6 · **Migration:** — (yo'q)

| Task | Nima qilinadi | Fayl(lar) | Test | Gate |
|---|---|---|---|---|
| T-WP5.1 | `check_ai_boundary.py` — AI modul chegarasi gate + mutatsiya testi | `tools/check_ai_boundary.py` (yangi) · `tools/check_negative.py` (o'zgartiriladi) | `check_negative` yangi guruh (`neg_ai_boundary`) | `check_ai_boundary` |
| T-WP5.2 | AI Gateway monolit modul skeleti (`apps/api/ai/`) | `apps/api/ai/__init__.py` (yangi) · `apps/api/ai/README.md` (yangi) | `apps/api/tests/test_ai_boundary.py` (yangi) | `check_ai_boundary` |

**Definition of Done:** `check_ai_boundary.py` bugungi repo'da yashil; DB-model import yoki testdata o'qish mutatsiyasi → qizil; AI qatlamida `DATABASE_URL` yo'q; AI Gateway monolit modul (`apps/api/ai/`).
**Xavf / rollback:** Gate vakuumli yashil o'tishi mumkin (AI kodi hali yo'q) — mutatsiya testi shuning uchun majburiy.
**Bog'liqlik:** WP0 tugagach. **WP6 dan oldin SHART** (D6 → D7).

### WP6 — Architecture boundary (D7 · migration yo'q)

**Mazmun:** `check_architecture.py` + allowlist (grandfather + ratchet).
**Bog'liq qaror:** D7 · **Migration:** — (yo'q)

| Task | Nima qilinadi | Fayl(lar) | Test | Gate |
|---|---|---|---|---|
| T-WP6.1 | `check_architecture.py` + allowlist (grandfather) | `tools/check_architecture.py` (yangi) · `tools/architecture-allowlist.txt` (yangi) | `apps/api/tests/test_architecture_boundary.py` (yangi) | `check_architecture` |
| T-WP6.2 | Ratchet qoidasi (ro'yxat faqat qisqaradi) + CI wiring | `tools/check_architecture.py` (o'zgartiriladi) · `.github/workflows/ci.yml` (o'zgartiriladi) · `tools/check_negative.py` (o'zgartiriladi) | `check_negative` yangi guruh (`neg_architecture`) | `check_architecture` |

**Definition of Done:** `check_architecture.py` + allowlist fayli mavjud; yangi taqiqlangan import → CI qizil; allowlist'da mavjud buzilishlar soni yozilgan; ratchet mavjud.
**Xavf / rollback:** Mavjud import'lar soni juda ko'p bo'lsa allowlist bosqichma-bosqich kengaytiriladi (grandfather). Ratchet buzilsa gate qizil.
**Bog'liqlik:** **WP5 dan keyin** (allowlist AI joylashuvini bilishi kerak).

### WP7 — Judge hardening (D3 · D10 · **M2** · U1)

**Mazmun:** Judge hardening: **bir bosqichda** userns + seccomp + `USER` + bake-off.
**Bog'liq qaror:** D3 · D10 · **Migration:** M2

| Task | Nima qilinadi | Fayl(lar) | Test | Gate |
|---|---|---|---|---|
| T-WP7.1 | 25-case bake-off (U1 evidence gate) + p95 latency raqami | `services/bakeoff/cases/` (o'zgartiriladi) · `services/bakeoff/harness/runner.py` (o'zgartiriladi) | bake-off exit 0 | **U1** (PASS/FAIL) |
| T-WP7.2 | userns + seccomp + `USER` bir bosqichda (oraliq `cap_drop` yo'q) | `docker-compose.yml` (o'zgartiriladi) · `services/judge-go/Dockerfile` (o'zgartiriladi) · `services/judge-go/sandbox.go` (o'zgartiriladi) · `services/judge-go/seccomp.json` (yangi) | grep: `privileged` va `cgroup: host` → 0 natija · `tests/security/run.sh` | `check_security_boundary` · `check_deploy_window` |
| T-WP7.3 | Deploy-oldi dump + judge-hardening runbook (rollback qaydi bilan) | `docs/10-operations/runbooks/judge-hardening.md` (yangi) · `tools/backup.sh` (o'zgartiriladi) | dump fayli | `check_deploy_window` |

**Definition of Done:** `privileged` va `cgroup: host` olib tashlangan; userns + seccomp bir deploy'da o'rnatilgan; runtime image'da `USER` direktivasi; p95 latency raqami yozilgan; deploy-oldi dump olingan; bake-off 25 case PASS.
**Xavf / rollback:** nsjail regressiyasi → 0 verdict. **U1 FAIL bo'lsa — yangi owner decision ochiladi** (WP7 yo'li qayta ko'riladi). Rollback: `privileged` ni qayta qo'shish (forward). Deploy-oldi dump **shart**.
**Bog'liqlik:** WP0 tugagach; **T-WP7.1 (bake-off) T-WP7.2 dan OLDIN** — U1 PASS bo'lmasa T-WP7.2 boshlanmaydi.

### D1 — ADR tili (cross-cutting) (D1 · migration yo'q)

**Mazmun:** 18 ADR (0028–0045) yozilishi + indeks yangilash.
**Bog'liq qaror:** D1 · **Migration:** — (yo'q)

| Task | Nima qilinadi | Fayl(lar) | Test | Gate |
|---|---|---|---|---|
| T-D1.1 | 18 ADR (0028–0045) yozish — sarlavha inglizcha, nasr o'zbek (lotin) | `docs/07-adr/0028…0045-*.md` (18 yangi) | `tools/check_docs.py` | `check_docs` |
| T-D1.2 | `docs/07-adr/README.md` indeksini yangilash (0027 ham qo'shiladi) | `docs/07-adr/README.md` (o'zgartiriladi) | indeks jadvali | `check_docs` |

**Definition of Done:** 18 ADR fayli yozilgan; sarlavhalar inglizcha, nasr o'zbek (lotin); indeks yangilangan (0027 ham); kirill/lotin aralashuvi yo'q.
**Xavf / rollback:** ADR fayllari mavjud (0001–0027) qayta raqamlanmaydi va tahrirlanmaydi.
**Bog'liqlik:** Mustaqil; boshqa WP lar bilan parallel (har ADR o'z komponentini hujjatlashtiradi).

---

## 4. Yangi fayllar ro'yxati

| Yo'l | Turi | WP |
|---|---|---|
| `deliverables/software-company/implementation-plan-phase0-2026-09-29.md` | doc | WP0 |
| `deliverables/software-company/phase0-reconciliation-table-2026-09-29.md` | doc | WP0 |
| `apps/api/problems/readiness.py` | code | WP1 |
| `apps/api/problems/migrations/0023_problem_readiness.py` | migration | WP1 |
| `apps/api/problems/migrations/0024_backfill_readiness.py` | migration | WP1 |
| `apps/api/problems/management/commands/backfill_readiness.py` | code | WP1 |
| `apps/api/tests/test_problem_readiness.py` | test | WP1 |
| `tests/regression/__init__.py` | test | WP1 |
| `tests/regression/conftest.py` | test | WP1 |
| `tests/regression/README.md` | test | WP1 |
| `tests/regression/test_ref_solution_verdicts.py` | test | WP1 |
| `docs/08-technical-spec/verdict-taxonomy-dead-codes.md` | doc | WP2 |
| `apps/api/judging/migrations/0008_relabel_re_legacy.py` | migration | WP2 |
| `apps/api/tests/test_verdict_taxonomy.py` | test | WP2 |
| `apps/api/core/migrations/0026_user_origin.py` | migration | WP3 |
| `apps/api/core/management/commands/backfill_origin.py` | code | WP3 |
| `tools/check_metrics.py` | gate | WP3 |
| `apps/api/tests/test_origin.py` | test | WP3 |
| `docs/10-operations/runbooks/secrets-rotation.md` | doc | WP4 |
| `apps/api/tests/test_settings_secrets.py` | test | WP4 |
| `tools/check_ai_boundary.py` | gate | WP5 |
| `apps/api/ai/__init__.py` | code | WP5 |
| `apps/api/ai/README.md` | doc | WP5 |
| `apps/api/tests/test_ai_boundary.py` | test | WP5 |
| `tools/check_architecture.py` | gate | WP6 |
| `tools/architecture-allowlist.txt` | gate | WP6 |
| `apps/api/tests/test_architecture_boundary.py` | test | WP6 |
| `services/judge-go/seccomp.json` | config | WP7 |
| `docs/10-operations/runbooks/judge-hardening.md` | doc | WP7 |
| `docs/07-adr/0028…0045-*.md` (18 ta fayl) | doc | D1 |

**Jami:** 30 qator — 29 yakka fayl + 1 qator (18 ADR fayli) = **47 fayl**.

---

## 5. O'zgaradigan fayllar ro'yxati

| Yo'l | Qanday o'zgaradi | WP | Risk |
|---|---|---|---|
| `docker-compose.yml` | sirlar `${VAR:?}`; `privileged` va `cgroup: host` olib tashlanadi | WP4 · WP7 | **yuqori** |
| `docker-compose.public.yml` | prod sirlar override (env) | WP4 | **yuqori** |
| `apps/api/config/settings.py` | `SECRET_KEY` fail-fast → `ImproperlyConfigured` | WP4 | o'rta |
| `.github/workflows/security.yml` | `if: false` olib tashlanadi | WP4 | past |
| `.github/workflows/ci.yml` | `check_metrics` · `check_ai_boundary` · `check_architecture` job wiring | WP3 · WP5 · WP6 | past |
| `.github/workflows/nightly.yml` | haqiqiy judge ref-solution + p95 latency | WP1 · WP7 | past |
| `apps/api/problems/models.py` | `readiness` maydoni + `clean()` gate | WP1 | o'rta |
| `apps/api/problems/serializers.py` | readiness ekspozitsiyasi | WP1 | past |
| `apps/api/problems/staff_serializers.py` | readiness validatsiya | WP1 | past |
| `apps/api/problems/staff_views.py` | readiness transition + graded gate | WP1 | o'rta |
| `apps/api/contests/serializers.py` | graded contest gate (400) | WP1 | o'rta |
| `apps/api/contests/services.py` | `validated` tekshiruv | WP1 | o'rta |
| `apps/api/judging/verdicts.py` | 4 o'lik kod nomlash | WP2 | past |
| `apps/api/core/models.py` | `User.origin` enum maydoni | WP3 | o'rta |
| `tools/check_negative.py` | 3 yangi salbiy guruh (`neg_refsolution_gate` · `neg_ai_boundary` · `neg_architecture`) | WP1 · WP5 · WP6 | past |
| `services/judge-go/Dockerfile` | `USER` direktivasi + `NSJAIL_REF` pin | WP7 | **yuqori** |
| `services/judge-go/sandbox.go` | rootless userns mapping (`inside=outside=65534`) | WP7 | **yuqori** |
| `services/bakeoff/cases/` | allaqachon 25 case (21 emas) — yangi case qo'shilmaydi | WP7 | past |
| `services/bakeoff/harness/runner.py` | 25-case hisobot | WP7 | past |
| `tools/backup.sh` | deploy-oldi dump qaydi | WP7 | past |
| `docs/07-adr/README.md` | indeks 0028–0045 + 0027 | D1 | past |

**Jami:** 20 fayl.

---

## 6. Migration rejasi (M1 · M2 · M3 · M10)

> Umumiy qoida: **forward-only**; har M alohida deploy; deploy-oldi **dump majburiy**; contest oynasida deploy **yo'q**; `check_deploy_window.py` majburiy (D11A).

| M# | WP | Mazmun | Forward yo'l | Deploy oynasi | Rollback | Dump talabi |
|---|---|---|---|---|---|---|
| **M1** | WP1 | `Problem.readiness` qo'shish + `legacy_unverified` backfill (1 226 qator) | `add` (nullable maydon) → `backfill` → `switch` (public uchun NOT NULL) | contest oynasi bo'sh | **forward-only** (qayta backfill yoki bo'shatish) | **shart** |
| **M2** | WP7 | Judge izolyatsiyasi: `privileged` + `cgroup: host` olib tashlash, userns + seccomp | compose + Dockerfile + sandbox.go bir deploy'da | contest oynasi bo'sh; **bake-off PASS sharti** | **forward-only** (`privileged` qayta qo'shish) | **shart** |
| **M3** | WP3 | `User.origin` ustuni + backfill (real · demo · imported · staff) | `add` → `backfill` → `switch` | contest oynasi bo'sh | **forward-only** | **shart** |
| **M10** | WP2 | 18 163 `RE` qatorni `RE_SIGNAL`/`RE_EXIT` ga qayta yorliqlash | `backfill` (yorliq) → `switch` | contest oynasi bo'sh | **forward-only** (yangi qayta yorliqlash) | **shart** |

**M2 haqida izoh:** M2 — DB migratsiyasi emas, **infratuzilma migratsiyasi** (judge konteyneri). Shuning uchun uning «dump talabi» — deploy-oldi DB dump (rollback uchun asos), «rollback» esa compose diff'ni qaytarish (forward). **Bir bosqichda** bajariladi (oraliq `cap_drop` bosqichi **yo'q**, D10).

---

## 7. Test strategiyasi

| WP | Test turi | Qayerda | CI job | Salbiy (mutatsiya) test |
|---|---|---|---|---|
| WP0 | hujjat yaxlitligi | `tools/check_docs.py` | PR (barcha) | — |
| WP1 | readiness matritsasi (R1–R10) + SQL + graded gate | `apps/api/tests/test_problem_readiness.py` · `tests/regression/` | PR (api) | **`neg_refsolution_gate`** (serializer buziladi → `test_sample_echo_is_not_ac` qizil) |
| WP2 | verdict taksonomiyasi + i18n parity (10 til) | `apps/api/tests/test_verdict_taxonomy.py` | PR (api) · PR (web) | `check_verdict_codes.py` (mavjud) |
| WP3 | origin enum + backfill audit + North Star SQL | `apps/api/tests/test_origin.py` | PR (api) · PR (tools) | `check_metrics.py` mutatsiya guruhi |
| WP4 | grep + build exit + fail-fast | `apps/api/tests/test_settings_secrets.py` | PR (api) · Security workflow | default sir bilan build **yiqilishi** |
| WP5 | AI boundary gate + DB import mutatsiyasi | `apps/api/tests/test_ai_boundary.py` | PR (tools) | **`neg_ai_boundary`** (DB-model import → qizil) |
| WP6 | import allowlist + yangi import | `apps/api/tests/test_architecture_boundary.py` | PR (tools) | **`neg_architecture`** (yangi taqiqlangan import → qizil) |
| WP7 | bake-off 25 case + escape testlari + latency | `services/bakeoff/` · `tests/security/run.sh` · `tests/latency/` | nightly | `tests/security/run.sh` (fork bomb · file write · network · /proc · symlink · setuid) |
| D1 | ADR tili + indeks | `tools/check_docs.py` | PR (barcha) | `neg_docs_missing_adr` (mavjud) |

**Salbiy test majburiy (muzlatilgan siyosat):** har yangi gate uchun mutatsiya testi **shart** — «hech qachon yiqilmaydigan tekshiruv» qabul qilinmaydi. Uch yangi gate → uch yangi salbiy guruh (`neg_refsolution_gate` · `neg_ai_boundary` · `neg_architecture`).

**O'lchov (decision emas):** U2 (seed user aniq soni) · U3 (jonli kontent raqamlari) · U5 (remediatsiya throughput) — M1/M3 dan oldin olinadi.

---

## 8. Gate rejasi

| Gate | WP0 | WP1 | WP2 | WP3 | WP4 | WP5 | WP6 | WP7 | D1 |
|---|---|---|---|---|---|---|---|---|---|
| `check_docs.py` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `check_deploy_window.py` | ✅ | ✅ | ✅ | ✅ | — | — | — | ✅ | — |
| `check_verdict_codes.py` | — | ✅ | ✅ | — | — | — | — | — | — |
| `check_metrics.py` | — | — | — | ✅ | — | — | — | — | — |
| `check_ai_boundary.py` | — | — | — | — | — | ✅ | — | — | — |
| `check_architecture.py` | — | — | — | — | — | — | ✅ | — | — |
| `check_negative.py` | — | ✅ | — | — | — | ✅ | ✅ | — | — |
| `check_security_boundary.py` | — | — | — | — | ✅ | — | — | ✅ | — |

**Izoh:** ✅ — shu WPda majburiy. `check_deploy_window.py` har M# bo'lgan WPda (WP1 · WP2 · WP3 · WP7) deploy'da majburiy. `check_docs.py` har PRda (hujjat o'zgargani uchun hamma WPda).

---

## 9. Decision conflict / ochiq bandlar

### 9.1 Decision conflict

**Yangi (ochiq) decision conflict: YO'Q.** Muzlatilgan qarorlar (D1–D11B, D8-F) o'zaro zid emas. Reja tuzishda topilgan barcha nomuvofiqliklar — **blueprint/assurance ↔ qaror** darajasida bo'lib, ular reconciliation jadvali (10 qator) va manba ierarxiyasi bilan yopilgan.

| # | Band | Turi | Yopilish |
|---|---|---|---|
| 1 | `A−` guruhi (assurance) ↔ D3 «A− ishlatilmaydi» | Tasnif | D3 ustun; `0028` → A |
| 2 | `Gate-0` yangi artefakt (assurance §9.3) ↔ D11A «yangi artefakt yo'q» | Artefakt | D11A ustun; mavjud gate + siyosat |
| 3 | blueprint §22.3 feature flag `F62` Phase 0 da kerak ↔ D11A | Artefakt | D11A ustun; feature flag kiritilmaydi |

### 9.2 Ochiq o'lchov / ish savollari (decision emas)

| # | Savol | Turi | Bloklaydimi |
|---|---|---|---|
| U1 | `privileged`siz nsjail ishlaydimi (25 case) | **Evidence gate** (PASS/FAIL) | ⚠️ HA — WP7 |
| U2 | Seed user aniq soni (10 000 / 10 001 / 10 068) | O'lchov | Yo'q (M1/M3 dan oldin) |
| U3 | 1 222 / 870 / 2 096 — jonli qiymatlar | O'lchov | Yo'q (M1 dan oldin) |
| U4 | Qaysi 4 verdict kodi o'lik | Qaror | Yo'q (WP2 ichida) |
| U5 | Remediatsiya throughput (Q20) | O'lchov | Yo'q (contest sanasini belgilaydi) |
| U6 | `tests/regression/` yo'q — harness yozilmagan | Ish | Yo'q (WP1 ichida) |
| U7 | Host cgroup v1/v2 | O'lchov | Yo'q |
| U8 | `.env.public` jonli runtime qiymatlari | O'lchov | Yo'q |
| U9 | `docs/07-adr/README.md` indeksi 0027 ni sanamaydi | Ish | Yo'q (D1 bilan birga) |

**U1 ta'kidlanadi:** bu **decision emas, evidence gate**. Natija PASS / FAIL. **FAIL bo'lsa — yangi owner decision ochiladi** (WP7 yo'li qayta ko'riladi). U1 PASS bo'lsa — qo'shimcha qaror kerak emas.

### 9.3 Ochilgan yangi fakt (qayd)

Owner **production launch: 2027 Q1** deb belgiladi. Bu blueprint'da yo'q bo'lgan yagona sanali ma'lumot; D7 da «sanali remediation» varianti qayta ko'rilishi mumkin. Bu — **ochiq belgi**; D7 **qayta ochilmagan** va scope'ga kirmaydi.

---

## 10. Deferred (Phase 1+)

Quyidagilar **ataylab** Phase 0 dan chiqarilgan (`owner-decision-closure-matrix` §7, so'zma-so'z). Phase 1/3/4 ishlari oldindan hal qilinmaydi.

| # | Deferred band | Faza |
|---|---|---|
| 1 | `0029` judge host ajratish (M6) | Phase 1 |
| 2 | Staging muhiti (0040) | Phase 1 |
| 3 | PITR / backup / DR (0043) | Phase 1 |
| 4 | Event sxemasi (0031) | Phase 2 |
| 5 | Object-level authz (0045) | Phase 4 |
| 6 | Billing (0041) | Phase 4 |
| 7 | AI Gateway **runtime** (0033–0035) | Phase 3 |
| 8 | Sentry / monitoring (0039) | Phase 1 |
| 9 | Judge queue semantikasi (0038) | Phase 1 |
| 10 | Throttle **ijrosi** (0032 — faqat o'lchov) | Phase 4 |
| 11 | `core/views.py` bo'lish (TD16) | — |
| 12 | Redis rol ajratish (TD23) | trigger |
| 13 | `neytron_*` userlarni o'chirish | 2027 Q1 (non-blocking DEFERRED) |

---

**STATUS:** Phase 0 Implementation Plan — tayyor. 8 WP + D1, 24 task, 47 yangi fayl, 20 o'zgargan fayl, 4 migratsiya. Scope WP0–WP7. U1 — evidence gate (PASS/FAIL).
