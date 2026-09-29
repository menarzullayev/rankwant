# RankWant — Phase 0 Implementation PRD (incremental)

**Sana**: 2026-09-29
**Muallif**: Software Company — Product Manager (Alice)
**Holat**: 🟢 Tayyor — owner qarorlari muzlatilgan (FROZEN), implementatsiya boshlanishi mumkin
**Til qoidasi**: Hujjat **o'zbek (lotin)** tilida. Texnik atama, fayl yo'li va kod **inglizcha** qoladi. Bu `deliverables/` an'anasi va repo darvozasi (`tools/check_docs.py`) talabi.
**Asos hujjatlar**:
- `deliverables/independent-review-board/acceptance-criteria-lock-2026-09-29.md` — **asosiy mezon manbasi** (FROZEN)
- `deliverables/independent-review-board/owner-decision-closure-matrix-2026-09-29.md` — qarorlar + scope freeze
- `deliverables/independent-review-board/owner-decision-ledger-2026-09-29.md` — batafsil qaror yozuvlari
- `deliverables/engineering-assurance/system-design-phase0-decision-closure-2026-09-29.md` — texnik asos
- `deliverables/software-architecture/software-architecture-rankwant-2026-09-29.md` — blueprint (kontekst)
- `deliverables/engineering-assurance/implementation-ready-gate-archi-2026-09-29.md` — **eskiroq** (ziddiyatda ustun emas)

> Bu **incremental PRD** — faqat Phase 0 o'zgarish qismi. Owner qarorlari **qayta talqin qilinmaydi**; ular implementatsiya qilinadigan ish birliklariga aylantiriladi va traceability asosi beriladi.

---

## 1. TL;DR

| Ko'rsatkich | Qiymat |
|---|---|
| Work package soni | **8** (WP0–WP7) |
| Migration soni | **4** (M1 · M2 · M3 · M10) |
| Evidence gate soni | **1** (U1 — judge bake-off · PASS/FAIL) |
| Qo'shimcha o'lchovlar | **3** (U2 · U3 · U5 — raqam) |
| Entry holati | 🟢 **PASS** (13/13 ACCEPTED, 1 non-blocking DEFERRED) |
| Scope freeze | ✅ WP0–WP7 |
| Acceptance criteria | ✅ **FROZEN** (2026-09-29) |

---

## 2. Manba ierarxiyasi va konfliktlar

### 2.1 Ustunlik tartibi (authoritative precedence)

| Daraja | Hujjat | Roli |
|---|---|---|
| **1 (eng ustun)** | `acceptance-criteria-lock-2026-09-29.md` | Muzlatilgan qabul mezonlari — asosiy mezon manbasi |
| 2 | `owner-decision-closure-matrix-2026-09-29.md` | Owner qarorlari + scope freeze (WP0–WP7) |
| 3 | `owner-decision-ledger-2026-09-29.md` | Har qaror uchun batafsil yozuv |
| 4 | `system-design-phase0-decision-closure-2026-09-29.md` | Texnik asos (triage, assurance) |
| 5 | `software-architecture-rankwant-2026-09-29.md` | Blueprint (kontekst) |
| **6 (eng past)** | `implementation-ready-gate-archi-2026-09-29.md` | **Eskiroq** — ziddiyatda ustun emas |

Qoida: quyi daraja hujjat yuqori daraja bilan zid bo'lsa — **yuqori daraja ustun**. Ushbu PRD faqat **1-daraja** mezonlarini so'zma-so'z ko'chiradi.

### 2.2 Eski hujjatdagi farq (WP0–WP6 / Phase 1)

`implementation-ready-gate-archi-2026-09-29.md` (6-daraja, eskiroq) da:

- scope **WP0–WP6** (WP7 yo'q);
- ADR 0028 **ijrosi Phase 1** deb belgilangan.

`acceptance-criteria-lock-2026-09-29.md` (1-daraja) va `owner-decision-closure-matrix-2026-09-29.md` (2-daraja) ustun:

- scope **WP0–WP7** (WP7 = Judge hardening, D3 va D10 tufayli ADR 0028 **Phase 0 ga ko'chdi**);
- ADR 0028 **qarori ham, ijrosi ham Phase 0** ichida (M2).

Ya'ni: eski hujjatdagi "WP0–WP6 + 0028 ijrosi Phase 1" bayoni **bekor qilingan**; ushbu PRD **WP0–WP7** ni qabul qiladi.

### 2.3 O'lchangan repo holati (2026-09-29, tasdiqlangan)

| Fakt | Holat |
|---|---|
| `docker-compose.yml:192` → `privileged: true` | Mavjud (WP7 da olib tashlanadi) |
| `docker-compose.yml:193` → `cgroup: host` | Mavjud (WP7 da olib tashlanadi) |
| `.github/workflows/security.yml:32` → `if: false` | Mavjud (WP4 da olib tashlanadi) |
| `tests/regression/` papkasi | **Yo'q** (WP1 da yaratiladi) |
| `tools/check_metrics.py` | **Yo'q** (WP3 da yaratiladi) |
| `tools/check_architecture.py` | **Yo'q** (WP6 da yaratiladi) |
| `tools/check_ai_boundary.py` | **Yo'q** (WP5 da yaratiladi) |
| `tools/check_deploy_window.py` | **Mavjud** (WP0 da majburiy qilinadi) |
| `tools/check_verdict_codes.py` | **Mavjud** (WP2 da yashil bo'lishi shart) |
| `tools/check_negative.py` | **Mavjud** (WP1 salbiy testi shu yerga qo'shiladi) |
| `docs/07-adr/0001..0027` + README | Mavjud; `0028..0045` **hali yozilmagan** (D1) |

---

## 3. Scope

### 3.1 In-scope (WP0–WP7)

| WP | Mazmun | Asos (Qaror) | Migration |
|---|---|---|---|
| WP0 | Reconciliation jadvali + migration/deploy siyosati | D2 · D11A | — |
| WP1 | Minimal `Problem.readiness` + ref-solution harness + graded gate + `legacy_unverified` backfill | D8 · D8-F | M1 |
| WP2 | 4 o'lik kod nomlash + M10 tarixiy qayta yorliqlash | D11B | M10 |
| WP3 | `User.origin` + backfill + `check_metrics.py` (**Attempt.origin YO'Q**) | D9 | M3 |
| WP4 | Secrets: env + fail-fast + `security.yml` ON (rotation **keyin**) | D5 | — |
| WP5 | `check_ai_boundary.py` (modul chegarasi) | D6 | — |
| WP6 | `check_architecture.py` + allowlist (grandfather + ratchet) | D7 | — |
| WP7 | Judge hardening: **bir bosqichda** userns + seccomp + `USER` + bake-off | D3 · D10 | M2 |

### 3.2 Out-of-scope (tegilmaydi)

Quyidagi ro'yxat `owner-decision-closure-matrix-2026-09-29.md` §7 dan **so'zma-so'z** ko'chirilgan:

> **OUT of scope (tegilmaydi):** 0029 judge host ajratish · staging (0040) · PITR/backup (0043) · event schema (0031) · object-level authz (0045) · Billing (0041) · AI Gateway runtime (0033–0035) · Sentry (0039) · judge queue semantikasi (0038) · throttle **ijrosi** (0032 — faqat o'lchov) · `core/views.py` bo'lish (TD16) · Redis rol ajratish (TD23).

Phase 1/3/4 ishlari oldindan hal qilinmaydi.

---

## 4. WP katalogi

Har WP uchun: ID, mazmun, bog'liq qaror, migration, user story, Definition of Done, qabul mezonlari (1-daraja hujjatidan so'zma-so'z) va evidence gate.

### WP0 — Reconciliation va migration siyosati

- **ID**: WP0
- **Mazmun**: Reconciliation jadvali (D2) + migration/deploy siyosati (D11A)
- **Bog'liq qaror**: D2 · D11A
- **Migration**: — (yo'q)
- **User story**: Platforma egasi sifatida men faza↔komponent nomuvofiqliklarining yagona authoritative jadvalini xohlayman, shunda implementatsiya qaysi manbaga tayanishini aniq bilib ish tutadi.
- **Definition of Done**: Reconciliation jadvali artefakti mavjud; har nomuvofiqlik uchun qaror qayd etilgan; §24 tie-break qoidasi yozilgan; migration/deploy siyosati hujjatlashtirilgan.
- **Acceptance criteria (so'zma-so'z)**:
  - ① Reconciliation jadvali artefakti mavjud
  - ② Har faza↔komponent nomuvofiqligi uchun qaror qayd etilgan
  - ③ §24 tie-break qoidasi yozilgan
  - ④ Migration/deploy siyosati hujjatlashtirilgan
- **O'lchov**: Jadval fayli · `python tools/check_docs.py` yashil · `check_deploy_window.py` deploy'da majburiy
- **Evidence gate**: — (yo'q)

### WP1 — Content readiness

- **ID**: WP1
- **Mazmun**: Minimal `Problem.readiness` + ref-solution harness + graded gate + `legacy_unverified` backfill
- **Bog'liq qaror**: D8 · D8-F
- **Migration**: M1
- **User story**: Staff (kontent muharriri) sifatida men har bir public masala aniq `readiness` holatiga ega bo'lishini xohlayman, shunda faqat tekshirilgan masala baholi contestda ishlatiladi.
- **Definition of Done**: Readiness holat-mashinasi + M1 backfill + ref-solution harness + graded gate; `tests/regression/` harness yozilgan; `neg_refsolution_gate` salbiy testi qo'shilgan.
- **Acceptance criteria (so'zma-so'z)**:
  - ① `test_sample_echo_is_not_ac` **yashil**
  - ② `neg_refsolution_gate` buzilganda **qizil** (salbiy test)
  - ③ `SELECT count(*) WHERE is_public AND readiness IS NULL` = **0**
  - ④ Graded contest `validated` bo'lmagan masalani **rad etadi** (400)
  - ⑤ `legacy_unverified` masala public ko'rinadi, **contestda ishlatilmaydi**
  - ⑥ Taxonomy qayta yozilmaydi (allaqachon shipped)
- **O'lchov**: pytest · SQL · graded gate testi · `check_verdict_codes.py` yashil
- **Evidence gate**: — (yo'q)

### WP2 — Verdict taxonomy (faqat qolgan ish)

- **ID**: WP2
- **Mazmun**: 4 o'lik kod nomlash + M10 tarixiy qayta yorliqlash
- **Bog'liq qaror**: D11B
- **Migration**: M10
- **User story**: Developer sifatida men o'lik verdict kodlari nomlanishini va 18 163 `RE` qatorning M10 qayta yorliqlanishini xohlayman, shunda taxonomy va i18n parity izchil qoladi.
- **Definition of Done**: 4 o'lik kod nomlangan va hujjatlashtirilgan; M10 migratsiyasi bajarilgan; shipped mexanizmlar (RE split, i18n parity) qayta yozilmagan.
- **Acceptance criteria (so'zma-so'z)**:
  - ① **4 o'lik kod nomlangan** va hujjatlashtirilgan
  - ② M10 migratsiyasi bajarilgan
  - ③ `RE_SIGNAL`/`RE_EXIT` split va i18n parity **qayta yozilmaydi** (shipped)
- **O'lchov**: Hujjat · migratsiya · `check_verdict_codes.py` yashil
- **Evidence gate**: — (yo'q)

### WP3 — Data origin

- **ID**: WP3
- **Mazmun**: `User.origin` + backfill + `check_metrics.py` (**Attempt.origin YO'Q**)
- **Bog'liq qaror**: D9
- **Migration**: M3
- **User story**: Analitik sifatida men `User.origin` bo'yicha North Star'ni hisoblashni xohlayman, shunda real va demo/imported userlar aniq ajratiladi.
- **Definition of Done**: `origin` ustuni + enum mavjud; M3 backfill bajarilgan; `check_metrics.py` yozilgan va CI'da exit 0; `Attempt.origin` **qo'shilmagan** (rad etilgan).
- **Acceptance criteria (so'zma-so'z)**:
  - ① `origin` ustuni + enum mavjud
  - ② **`Attempt.origin` YO'Q** (rad etilgan)
  - ③ North Star SQL `origin='real'` bilan (JOIN) ishlaydi
  - ④ Backfill audit raqami chop etilgan
  - ⑤ `imported` alohida qiymat
  - ⑥ Seed user aniq soni **o'lchangan** (10 000 / 10 001 / 10 068 nomuvofiqligi yopilgan)
- **O'lchov**: `psql` · SQL xatosiz · `tools/check_metrics.py` exit 0
- **Evidence gate**: — (yo'q; U2 — o'lchov, quyida)

### WP4 — Secrets

- **ID**: WP4
- **Mazmun**: Secrets: env + fail-fast + `security.yml` ON (rotation **keyin**)
- **Bog'liq qaror**: D5
- **Migration**: — (yo'q)
- **User story**: Ops (SRE) sifatida men sirlar env orqali berilishini va default sir bilan prod build yiqilishini xohlayman, shunda prod parol hardcode bo'lmaydi.
- **Definition of Done**: Env + majburiy env (`${VAR:?}`) + fail-fast joriy etilgan; `security.yml` `if: false` olib tashlangan va CI yashil; rotation **wiring va fail-fast dan keyin**.
- **Acceptance criteria (so'zma-so'z)**:
  - ① `grep "PASSWORD: dev"` va `grep "devdevdev"` → **0 natija**
  - ② `security.yml` `if: false` olib tashlangan va CI **yashil**
  - ③ Default sir bilan prod build **yiqiladi** (exit ≠ 0)
  - ④ `SECRET_KEY` fallback → `ImproperlyConfigured`
  - ⑤ Rotation **keyin** bajariladi (tartib qulflangan)
- **O'lchov**: grep · CI holati · build exit kodi · test
- **Evidence gate**: — (yo'q)

### WP5 — AI boundary

- **ID**: WP5
- **Mazmun**: `check_ai_boundary.py` (modul chegarasi)
- **Bog'liq qaror**: D6
- **Migration**: — (yo'q)
- **User story**: Arxitektor sifatida men AI qatlami chegarasini gate bilan majburlashni xohlayman, shunda AI DB model yoki testdata'ga tegmaydi.
- **Definition of Done**: `tools/check_ai_boundary.py` yozilgan va bugungi repo'da yashil; mutatsiya testi (DB-model import / testdata o'qish) qizil; AI Gateway `apps/api/ai/` monolit modul sifatida joylashgan.
- **Acceptance criteria (so'zma-so'z)**:
  - ① `tools/check_ai_boundary.py` bugungi repo'da **yashil**
  - ② DB-model import yoki testdata o'qish mutatsiyasi → **qizil**
  - ③ AI qatlamida `DATABASE_URL` yo'q
  - ④ AI Gateway **monolit modul** (`apps/api/ai/`)
- **O'lchov**: Gate exit 0 · mutatsiya testi qizil
- **Evidence gate**: — (yo'q)

### WP6 — Architecture boundary

- **ID**: WP6
- **Mazmun**: `check_architecture.py` + allowlist (grandfather + ratchet)
- **Bog'liq qaror**: D7
- **Migration**: — (yo'q)
- **User story**: Arxitektor sifatida men import allowlist gate'i (grandfather + ratchet) bo'lishini xohlayman, shunda yangi taqiqlangan import CI'ni yiqitadi va ro'yxat faqat qisqaradi.
- **Definition of Done**: `tools/check_architecture.py` + allowlist fayli yozilgan; mavjud buzilishlar grandfather qilingan va soni yozilgan; ratchet qoidasi mavjud (ro'yxat faqat qisqaradi).
- **Acceptance criteria (so'zma-so'z)**:
  - ① `tools/check_architecture.py` + allowlist fayli mavjud
  - ② **Yangi** taqiqlangan import → CI **qizil**
  - ③ Allowlist'da mavjud buzilishlar soni yozilgan
  - ④ Ratchet mavjud (ro'yxat faqat qisqaradi)
- **O'lchov**: Gate exit 0 · allowlist fayli · negative test
- **Evidence gate**: — (yo'q)

### WP7 — Judge hardening

- **ID**: WP7
- **Mazmun**: Judge hardening: **bir bosqichda** userns + seccomp + `USER` + bake-off
- **Bog'liq qaror**: D3 · D10
- **Migration**: M2
- **User story**: SRE sifatida men judge privilegedsiz ishlashini va bake-off bilan tasdiqlanishini xohlayman, shunda nsjail escape blast radius kamayadi.
- **Definition of Done**: `privileged` va `cgroup: host` olib tashlangan; userns + seccomp bir deploy'da o'rnatilgan; runtime image'da `USER` direktivasi; p95 latency raqami yozilgan; deploy-oldi dump olingan; bake-off 25 case PASS.
- **Acceptance criteria (so'zma-so'z)**:
  - ① `grep "privileged"` va `grep "cgroup: host"` → **0 natija**
  - ② nsjail **bake-off 25 case PASS**
  - ③ Judge **p95 latency raqami yozilgan**
  - ④ Runtime image'da **`USER` direktivasi mavjud**
  - ⑤ **Bir bosqichda** bajarilgan (oraliq `cap_drop` bosqichi yo'q)
  - ⑥ Deploy-oldi dump olingan
- **O'lchov**: grep · bake-off exit 0 · Dockerfile · runbook'dagi raqam
- **Evidence gate (U1)**: `privileged`siz nsjail ishlashi hali **o'lchanmagan**. U1 = bake-off natijasi. **PASS** → WP7 davom etadi · **FAIL** → owner qaroriga qaytadi (bu FAIL **yangi decision** ochadi).

### D1 — ADR tili (cross-cutting ish birligi)

- **ID**: D1
- **Mazmun**: 18 ADR (0028–0045) yozilishi + indeks yangilash
- **Bog'liq qaror**: D1
- **Migration**: — (yo'q)
- **User story**: Hujjat o'quvchisi sifatida men ADR lar bir uslubda (ingliz sarlavha + o'zbek nasr) yozilishini xohlayman, shunda korpus izchil qoladi.
- **Definition of Done**: 18 ADR fayli (0028–0045) yozilgan; sarlavhalar inglizcha, nasr o'zbek (lotin); `docs/07-adr/README.md` indeksi yangilangan (0027 ham qo'shilgan).
- **Acceptance criteria (so'zma-so'z)**:
  - ① 18 ADR (0028–0045): sarlavhalar **inglizcha**, nasr **o'zbek (lotin)**
  - ② `docs/07-adr/README.md` indeksi yangilangan (**0027 ham qo'shilgan**)
  - ③ Kirill/lotin aralashuvi yo'q
- **O'lchov**: `python tools/check_docs.py` yashil · indeks jadvali
- **Evidence gate**: — (yo'q)

---

## 5. Acceptance Criteria Traceability Matrix

> **Status** ustuni `☐ PENDING` — Engineer/QA to'ldiradi. Ustunlar: `WP | Qaror | AC # | Mezon (qisqa) | O'lchov usuli | Evidence artefakti | Status`.

| WP | Qaror | AC # | Mezon (qisqa) | O'lchov usuli | Evidence artefakti | Status |
|---|---|---|---|---|---|---|
| WP0 | D2 · D11A | ① | Reconciliation jadvali artefakti mavjud | jadval fayli | reconciliation jadvali fayli | ☐ PENDING |
| WP0 | D2 · D11A | ② | Har faza↔komponent nomuvofiqligi uchun qaror qayd etilgan | jadvaldagi qaror ustuni | jadval + `check_docs.py` yashil | ☐ PENDING |
| WP0 | D2 · D11A | ③ | §24 tie-break qoidasi yozilgan | hujjat ko'rigi | siyosat hujjati | ☐ PENDING |
| WP0 | D2 · D11A | ④ | Migration/deploy siyosati hujjatlashtirilgan | `check_deploy_window.py` deploy'da majburiy | siyosat hujjati | ☐ PENDING |
| WP1 | D8 · D8-F | ① | `test_sample_echo_is_not_ac` yashil | pytest | pytest natijasi | ☐ PENDING |
| WP1 | D8 · D8-F | ② | `neg_refsolution_gate` buzilganda qizil (salbiy test) | `check_negative.py` | salbiy test natijasi | ☐ PENDING |
| WP1 | D8 · D8-F | ③ | `is_public AND readiness IS NULL` qator soni = 0 | SQL | SQL natijasi | ☐ PENDING |
| WP1 | D8 · D8-F | ④ | Graded contest `validated` bo'lmagan masalani rad etadi (400) | graded gate testi | pytest R8 natijasi | ☐ PENDING |
| WP1 | D8 · D8-F | ⑤ | `legacy_unverified` public ko'rinadi, contestda ishlatilmaydi | graded gate testi | graded gate natijasi | ☐ PENDING |
| WP1 | D8 · D8-F | ⑥ | Taxonomy qayta yozilmaydi (shipped) | `check_verdict_codes.py` yashil | mavjud gate natijasi | ☐ PENDING |
| WP2 | D11B | ① | 4 o'lik kod nomlangan va hujjatlashtirilgan | hujjat | dead-code hujjati | ☐ PENDING |
| WP2 | D11B | ② | M10 migratsiyasi bajarilgan | migratsiya fayli | M10 migratsiya | ☐ PENDING |
| WP2 | D11B | ③ | `RE_SIGNAL`/`RE_EXIT` split va i18n parity qayta yozilmaydi | `check_verdict_codes.py` yashil | mavjud gate natijasi | ☐ PENDING |
| WP3 | D9 | ① | `origin` ustuni + enum mavjud | `psql` | M3 migratsiya + psql chiqishi | ☐ PENDING |
| WP3 | D9 | ② | `Attempt.origin` YO'Q (rad etilgan) | repo ko'rigi | rad etish yozuvi | ☐ PENDING |
| WP3 | D9 | ③ | North Star SQL `origin='real'` bilan (JOIN) ishlaydi | SQL xatosiz | SQL natijasi | ☐ PENDING |
| WP3 | D9 | ④ | Backfill audit raqami chop etilgan | backfill skript chiqishi | audit raqami | ☐ PENDING |
| WP3 | D9 | ⑤ | `imported` alohida qiymat | enum ko'rigi | enum qiymatlari | ☐ PENDING |
| WP3 | D9 | ⑥ | Seed user aniq soni o'lchangan (nomuvofiqlik yopilgan) | U2 o'lchov | U2 raqami | ☐ PENDING |
| WP4 | D5 | ① | `grep "PASSWORD: dev"` va `grep "devdevdev"` → 0 natija | grep | grep natijasi | ☐ PENDING |
| WP4 | D5 | ② | `security.yml` `if: false` olib tashlangan va CI yashil | CI holati | CI yashil | ☐ PENDING |
| WP4 | D5 | ③ | Default sir bilan prod build yiqiladi (exit ≠ 0) | build exit kodi | build jurnali | ☐ PENDING |
| WP4 | D5 | ④ | `SECRET_KEY` fallback → `ImproperlyConfigured` | test | test natijasi | ☐ PENDING |
| WP4 | D5 | ⑤ | Rotation keyin bajariladi (tartib qulflangan) | runbook tartibi | secrets-rotation runbook | ☐ PENDING |
| WP5 | D6 | ① | `check_ai_boundary.py` bugungi repo'da yashil | gate exit 0 | gate natijasi | ☐ PENDING |
| WP5 | D6 | ② | DB-model import yoki testdata o'qish mutatsiyasi → qizil | mutatsiya testi | mutatsiya natijasi | ☐ PENDING |
| WP5 | D6 | ③ | AI qatlamida `DATABASE_URL` yo'q | runtime guard | guard natijasi | ☐ PENDING |
| WP5 | D6 | ④ | AI Gateway monolit modul (`apps/api/ai/`) | repo ko'rigi | `apps/api/ai/` tuzilishi | ☐ PENDING |
| WP6 | D7 | ① | `check_architecture.py` + allowlist fayli mavjud | gate exit 0 | gate + allowlist fayli | ☐ PENDING |
| WP6 | D7 | ② | Yangi taqiqlangan import → CI qizil | negative test | negative test natijasi | ☐ PENDING |
| WP6 | D7 | ③ | Allowlist'da mavjud buzilishlar soni yozilgan | allowlist fayli | allowlist soni | ☐ PENDING |
| WP6 | D7 | ④ | Ratchet mavjud (ro'yxat faqat qisqaradi) | allowlist diff | ratchet qoidasi | ☐ PENDING |
| WP7 | D3 · D10 | ① | `grep "privileged"` va `grep "cgroup: host"` → 0 natija | grep | grep natijasi | ☐ PENDING |
| WP7 | D3 · D10 | ② | nsjail bake-off 25 case PASS | bake-off exit 0 | bake-off jurnali | ☐ PENDING |
| WP7 | D3 · D10 | ③ | Judge p95 latency raqami yozilgan | runbook'dagi raqam | runbook | ☐ PENDING |
| WP7 | D3 · D10 | ④ | Runtime image'da `USER` direktivasi mavjud | Dockerfile | Dockerfile | ☐ PENDING |
| WP7 | D3 · D10 | ⑤ | Bir bosqichda bajarilgan (oraliq `cap_drop` bosqichi yo'q) | compose diff | compose diff | ☐ PENDING |
| WP7 | D3 · D10 | ⑥ | Deploy-oldi dump olingan | backup fayli | dump fayli | ☐ PENDING |
| D1 | D1 | ① | 18 ADR (0028–0045): sarlavhalar inglizcha, nasr o'zbek (lotin) | `check_docs.py` yashil | 18 ADR fayli | ☐ PENDING |
| D1 | D1 | ② | `docs/07-adr/README.md` indeksi yangilangan (0027 ham) | indeks jadvali | README indeksi | ☐ PENDING |
| D1 | D1 | ③ | Kirill/lotin aralashuvi yo'q | `check_docs.py` | `check_docs.py` yashil | ☐ PENDING |
| WP0 | D2 · D11A | EG-0 | Reconciliation jadvali + deploy siyosati artefakti (doc: evidence gate = —) | `check_docs.py` yashil · jadval fayli | reconciliation jadvali | ☐ PENDING |
| WP7 | D3 · D10 | U1 | `privileged`siz nsjail bake-off 25 case → PASS/FAIL | bake-off exit kodi | bake-off jurnali | ☐ PENDING |

**Jami qatorlar**: 43 (41 mezon + 2 evidence gate qatori). **Status**: barchasi `☐ PENDING` — Engineer/QA to'ldiradi.

---

## 6. Evidence gate'lar

**Muhim:** U1 — **decision emas, evidence gate**. U1 ning natijasi PASS / FAIL, qaror emas.

| # | Gate | Nima o'lchanadi | Natija | Turi |
|---|---|---|---|---|
| **U1** | Judge bake-off | `privileged`siz nsjail ishlaydimi (25 case) | **PASS / FAIL** | **Evidence gate** (WP7 ni shartli qiladi) |
| U2 | Seed user soni | Aniq joriy son (10 000 / 10 001 / 10 068) | Raqam | O'lchov |
| U3 | Jonli kontent raqamlari | 1 222 / 870 / 2 096 | Raqamlar | O'lchov |
| U5 | Remediatsiya throughput | Kuniga nechta masala `validated` | Raqam | O'lchov |

- **U1 PASS** → WP7 davom etadi, qo'shimcha qaror kerak emas.
- **U1 FAIL** → **yangi owner decision** ochiladi (WP7 yo'li qayta ko'riladi).
- U2 · U3 · U5 — **o'lchov**, decision emas; WP3 va contest qayta ochilish sanasi uchun kirish.

---

## 7. Owner qarorlari muzlatilganligi

Quyidagi jadval owner qarorlarini **so'zma-so'z** qayd etadi (qayta talqin qilinmagan).

| # | Qaror (so'zma-so'z) | Status |
|---|---|---|
| D1 | ADR tili: Ingliz sarlavha + o'zbek matn | **ACCEPTED** |
| D2 | Phase 0 authoritative source: Reconciliation jadvali authoritative; §24 **tie-break**. Retrospektiv: **butun blueprint** | **ACCEPTED** |
| D3 | ADR 0028 / A−: M2 **to'liq Phase 0 da**; §24 bilan ziddiyat reconciliation'da **owner override**; **0028 → A**; A− **ishlatilmaydi** | **ACCEPTED** |
| D4 | Triage corrections: **To'liq to'plam** — 0042↑, 0036↑, 0028→A, 0032≠A, **0029→B** | **ACCEPTED** |
| D5 | ADR 0044 secrets: **Env + majburiy env + fail-fast**; rotation **KEYIN** | **ACCEPTED** |
| D6 | ADR 0036 AI boundary: **Monolit modul** (`apps/api/ai/`) | **ACCEPTED** |
| D7 | ADR 0042 dependency policy: **Grandfather + ratchet** | **ACCEPTED** |
| D8 | ADR 0037 content readiness: **Minimal holat-mashinasi** · **Mezon (son emas)** · **Gibrid trigger** · arxiv → D8-F | **ACCEPTED** |
| D8-F | Legacy graded eligibility: **Graded'dan chiqarish** (public qoladi, contestdan chiqariladi) | **ACCEPTED** |
| D9 | ADR 0030 data origin: **`User.origin`** (Attempt'siz) · **imported alohida** · neytron **o'chirilmaydi** → 2027 Q1 | **ACCEPTED** |
| D10 | ADR 0028 hardening yo'li: **Bir bosqichda** + oldidan **majburiy 25-case bake-off** | **ACCEPTED** |
| D11A | Gate-0 artefakti: **Mavjud tekshiruv + siyosat** (yangi artefakt yo'q) | **ACCEPTED** |
| D11B | Verdict taxonomy scope: **Faqat qolgan ish** — 4 kod nomlash + M10 qayta yorliqlash | **ACCEPTED** |

**Status xulosasi**: ACCEPTED **13** · REJECTED **0** · DEFERRED **1** (`neytron_*` o'chirish → 2027 Q1, bloklamaydi).

> **D8-F siyosati qayd etiladi:** `legacy_unverified` masala **public qoladi**, lekin **graded contestga kiritilmaydi**.

---

## 8. Ochiq savollar / decision conflict

### 8.1 Decision conflict

**Ochiq (yopilmagan) decision conflict: YO'Q.** Muzlatilgan qarorlar (D1–D11B, D8-F) o'zaro zid emas.

PRD yozishda faqat **manba darajasidagi** zidlar topildi — ular quyi daraja hujjatlarda bo'lib, **manba ierarxiyasi bilan yopilgan** (yuqori daraja ustun):

| # | Zid | Qayerda | Yopilish | Holat |
|---|---|---|---|---|
| C1 | `Attempt.origin` **mavjud** deyilgan ↔ D9 "`Attempt.origin` YO'Q (rad etilgan)" | 6-daraja hujjat §2 (0030 mezoni) ↔ D9 | D9 ustun; PRD `Attempt.origin` ni qo'shmaydi | **Yopilgan** |
| C2 | Scope **WP0–WP6**, 0028 **ijrosi Phase 1** ↔ D3/D10 + 1/2-daraja: **WP0–WP7**, 0028 **Phase 0** | 6-daraja hujjat ↔ 1/2-daraja | 1/2-daraja ustun; PRD WP0–WP7 | **Yopilgan** |
| C3 | 0044 tavsiyasi: **Docker secret** (variant ②) ↔ D5 "Docker secrets va Vault **rad etildi**" | 4-daraja hujjat §3.3 ↔ D5 | D5 ustun; env fayl | **Yopilgan** |
| C4 | **A− guruhi** kiritilgan (Phase 0 chiqish blokeri) ↔ D3 "A− toifasi **ishlatilmaydi**" | 4-daraja hujjat §3.4 ↔ D3 | D3 ustun; 0028 → A | **Yopilgan** |

C1–C4 — **yangi owner decision talab qilmaydi** (hierarxiya qoidasi bilan hal qilingan).

### 8.2 Ochiq o'lchov / ish savollari (decision emas)

| # | Savol | Turi | Bloklaydimi |
|---|---|---|---|
| U1 | `privileged`siz nsjail ishlaydimi? | O'lchov (evidence gate) | ⚠️ HA — WP7 |
| U2 | Seed user aniq soni (10 000 / 10 001 / 10 068) | O'lchov | Yo'q (M1/M3 dan oldin) |
| U3 | 1 222 / 870 / 2 096 — jonli qiymatlar | O'lchov | Yo'q (M1 dan oldin) |
| U4 | Qaysi **4 verdict kodi** o'lik | Qaror | Yo'q (WP2 ichida) |
| U5 | Remediatsiya throughput (Q20) | O'lchov | Yo'q (contest sanasini belgilaydi) |
| U6 | `tests/regression/` yo'q — harness yozilmagan | Ish | Yo'q (WP1 ichida) |
| U7 | Host cgroup v1/v2 | O'lchov | Yo'q |
| U8 | `.env.public` jonli runtime qiymatlari | O'lchov | Yo'q |
| U9 | `docs/07-adr/README.md` indeksi 0027 ni sanamaydi | Ish | Yo'q (D1 bilan birga) |

**Xulosa:** faqat **U1** implementation scope'ini bekor qilishi mumkin — va u **o'lchov (evidence gate)**, decision emas.

---

## 9. Acceptance criteria change control

`acceptance-criteria-lock-2026-09-29.md` dan olingan siyosat:

| Qoida | Mazmun |
|---|---|
| **Freeze** | Mezonlar **qulflangan**. Yumshatish yoki olib tashlash **yangi owner decision** talab qiladi |
| **Kuchaytirish** | Mezonni **kuchaytirish** (qattiqroq qilish) mumkin, lekin **qayd etilishi shart** |
| **O'lchovsiz mezon yo'q** | Har mezon **avtomatik yoki qo'lda o'lchanadigan** bo'lishi shart. "Bajarildi" degan so'z dalil emas |
| **Salbiy test majburiy** | Gate'lar uchun **salbiy (mutatsiya) testi majburiy** — hech qachon yiqilmaydigan tekshiruv qabul qilinmaydi |
| **U1 qayta ochilmaydi** | `privileged`siz nsjail — bu **decision emas**, **evidence gate**. Natija: PASS / FAIL |

---

## Ilova — implementatsiya izchilligi

- **Migration ↔ WP**: M1 (WP1) · M2 (WP7) · M3 (WP3) · M10 (WP2). M5 — faqat o'lchov (kod emas, out-of-scope).
- **Migration intizomi**: forward-only; har M alohida deploy + deploy-oldi dump; `check_deploy_window.py` deploy'da majburiy (WP0, D11A).
- **Ketma-ket shart**: 0036 (WP5) → 0042 (WP6) — allowlist AI joylashuvini bilishi kerak (D6 → D7).
- **Parallel mumkin**: WP4 (D5), WP3 qarori, WP7 qarori.

**STATUS:** Phase 0 Implementation PRD — tayyor (Engineer/QA tasdig'iga tayyor). Qabul mezonlari **FROZEN** (2026-09-29). Scope **WP0–WP7**.
