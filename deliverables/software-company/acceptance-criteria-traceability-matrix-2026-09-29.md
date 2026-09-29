# RankWant — Acceptance Criteria Traceability Matrix

**Sana**: 2026-09-29
**Muallif**: Software Company — Architect (Bob)
**Holat**: 🟢 Tayyor — qabul mezonlari ↔ evidence izi (WP0–WP7 + D1)
**Til qoidasi**: Hujjat **o'zbek (lotin)** tilida. Texnik atama, fayl yo'li va kod **inglizcha** qoladi.
**Asos hujjatlar**:
- `deliverables/independent-review-board/acceptance-criteria-lock-2026-09-29.md` — muzlatilgan mezonlar (1-daraja)
- `deliverables/software-company/implementation-prd-phase0-2026-09-29.md` §5 — 43 qatorli skeleton
- `deliverables/software-company/implementation-plan-phase0-2026-09-29.md` — WP ↔ task ↔ gate

> ⚠️ Bu jadval **dalilsiz PASS yozmaydi**. Har `✅ PASS` qatori orqasida o'lchangan artefakt bor. Mezon **yumshatilmaydi** — o'zgartirish uchun yangi owner decision talab qilinadi (`acceptance-criteria-lock`).

---

## 1. Maqsad va ustunlar

**Maqsad:** Owner so'ragan yakuniy mahsulot — har qabul mezoni uchun **yagona iz**: qaysi WP, qaysi qaror, qanday o'lchanadi, dalil qayerda va **kim** tekshirgan.

| Ustun | Ma'nosi |
|---|---|
| **WP** | Ish birligi (WP0–WP7 + D1) |
| **Qaror** | Manba owner qarori (D#) |
| **AC #** | Mezon raqami (①…⑥) yoki evidence gate qatori (`EG-0` · `U1`) |
| **Mezon** | Qisqa mezon matni (so'zma-so'z manba: `acceptance-criteria-lock`) |
| **O'lchov usuli** | Mezon qanday o'lchanadi (gate · pytest · SQL · grep) |
| **Evidence artefakti** | Dalil fayli / natija |
| **Status** | `✅ PASS` · `⏳ IN PROGRESS` · `☐ PENDING` · `❌ FAIL` |
| **Tekshirgan** | Kim tasdiqladi (faqat PASS/IN PROGRESS qatorida) |

---

## 2. Status legendasi

| Belgi | Ma'nosi |
|---|---|
| ✅ PASS | Mezon uchun dalil **mavjud** — o'lchandi |
| ⏳ IN PROGRESS | Ish davom etmoqda — dalil hali to'liq emas |
| ☐ PENDING | Boshlanmagan — dalil yo'q |
| ❌ FAIL | Mezon buzildi |

---

## 3. Traceability matritsasi (43 qator)

| WP | Qaror | AC # | Mezon | O'lchov usuli | Evidence artefakti | Status | Tekshirgan |
|---|---|---|---|---|---|---|---|
| WP0 | D2 · D11A | ① | Reconciliation jadvali artefakti mavjud | jadval fayli | `phase0-reconciliation-table-2026-09-29.md` §2 (10 nomuvofiqlik qatori) | ✅ PASS | software-qa-engineer (QA batch 1) |
| WP0 | D2 · D11A | ② | Har faza↔komponent nomuvofiqligi uchun qaror qayd etilgan | jadvaldagi «Yozilgan qaror» ustuni | jadval §2 (10/10 «Yopilgan») · `check_docs.py` exit 0 | ✅ PASS | software-qa-engineer (QA batch 1) |
| WP0 | D2 · D11A | ③ | §24 tie-break qoidasi yozilgan | hujjat ko'rigi | jadval §1 (4 qadamli tartib) | ✅ PASS | software-qa-engineer (QA batch 1) |
| WP0 | D2 · D11A | ④ | Migration/deploy siyosati hujjatlashtirilgan | `check_deploy_window.py` deploy'da majburiy | jadval §4 (8 qoida) · `.github/workflows/deploy.yml:218` va `:230` majburiy | ✅ PASS | software-qa-engineer (QA batch 1) |
| WP1 | D8 · D8-F | ① | `test_sample_echo_is_not_ac` yashil | pytest | pytest natijasi | ☐ PENDING | — |
| WP1 | D8 · D8-F | ② | `neg_refsolution_gate` buzilganda qizil (salbiy test) | `check_negative.py` | salbiy test natijasi | ☐ PENDING | — |
| WP1 | D8 · D8-F | ③ | `is_public AND readiness IS NULL` qator soni = 0 | SQL | SQL natijasi | ☐ PENDING | — |
| WP1 | D8 · D8-F | ④ | Graded contest `validated` bo'lmagan masalani rad etadi (400) | graded gate testi | pytest R8 natijasi | ☐ PENDING | — |
| WP1 | D8 · D8-F | ⑤ | `legacy_unverified` public ko'rinadi, contestda ishlatilmaydi | graded gate testi | graded gate natijasi | ☐ PENDING | — |
| WP1 | D8 · D8-F | ⑥ | Taxonomy qayta yozilmaydi (shipped) | `check_verdict_codes.py` yashil | mavjud gate natijasi | ☐ PENDING | — |
| WP2 | D11B | ① | 4 o'lik kod nomlangan va hujjatlashtirilgan | hujjat | dead-code hujjati | ☐ PENDING | — |
| WP2 | D11B | ② | M10 migratsiyasi bajarilgan | migratsiya fayli | M10 migratsiya | ☐ PENDING | — |
| WP2 | D11B | ③ | `RE_SIGNAL`/`RE_EXIT` split va i18n parity qayta yozilmaydi | `check_verdict_codes.py` yashil | mavjud gate natijasi | ☐ PENDING | — |
| WP3 | D9 | ① | `origin` ustuni + enum mavjud | `psql` | M3 migratsiya + psql chiqishi | ☐ PENDING | — |
| WP3 | D9 | ② | `Attempt.origin` YO'Q (rad etilgan) | repo ko'rigi | rad etish yozuvi | ☐ PENDING | — |
| WP3 | D9 | ③ | North Star SQL `origin='real'` bilan (JOIN) ishlaydi | SQL xatosiz | SQL natijasi | ☐ PENDING | — |
| WP3 | D9 | ④ | Backfill audit raqami chop etilgan | backfill skript chiqishi | audit raqami | ☐ PENDING | — |
| WP3 | D9 | ⑤ | `imported` alohida qiymat | enum ko'rigi | enum qiymatlari | ☐ PENDING | — |
| WP3 | D9 | ⑥ | Seed user aniq soni o'lchangan (nomuvofiqlik yopilgan) | U2 o'lchov | U2 raqami | ☐ PENDING | — |
| WP4 | D5 | ① | `grep "PASSWORD: dev"` va `grep "devdevdev"` → 0 natija | grep | grep natijasi | ⏳ IN PROGRESS | — |
| WP4 | D5 | ② | `security.yml` `if: false` olib tashlangan va CI yashil | CI holati | CI yashil | ⏳ IN PROGRESS | — |
| WP4 | D5 | ③ | Default sir bilan prod build yiqiladi (exit ≠ 0) | build exit kodi | build jurnali | ⏳ IN PROGRESS | — |
| WP4 | D5 | ④ | `SECRET_KEY` fallback → `ImproperlyConfigured` | test | test natijasi | ⏳ IN PROGRESS | — |
| WP4 | D5 | ⑤ | Rotation keyin bajariladi (tartib qulflangan) | runbook tartibi | secrets-rotation runbook | ⏳ IN PROGRESS | — |
| WP5 | D6 | ① | `check_ai_boundary.py` bugungi repo'da yashil | gate exit 0 | `tools/check_ai_boundary.py` exit 0 | ✅ PASS | software-qa-engineer (QA batch 1) |
| WP5 | D6 | ② | DB-model import yoki testdata o'qish mutatsiyasi → qizil | mutatsiya testi | 6/6 mutatsiya guruhi qizil | ✅ PASS | software-qa-engineer (QA batch 1) |
| WP5 | D6 | ③ | AI qatlamida `DATABASE_URL` yo'q | runtime guard | guard natijasi | ✅ PASS | software-qa-engineer (QA batch 1) |
| WP5 | D6 | ④ | AI Gateway monolit modul (`apps/api/ai/`) | repo ko'rigi | `apps/api/ai/` tuzilishi | ✅ PASS | software-qa-engineer (QA batch 1) |
| WP6 | D7 | ① | `check_architecture.py` + allowlist fayli mavjud | gate exit 0 | `tools/check_architecture.py` + allowlist exit 0 | ✅ PASS | software-qa-engineer (QA batch 1) |
| WP6 | D7 | ② | Yangi taqiqlangan import → CI qizil | negative test | `neg_architecture` natijasi | ✅ PASS | software-qa-engineer (QA batch 1) |
| WP6 | D7 | ③ | Allowlist'da mavjud buzilishlar soni yozilgan | allowlist fayli | `tools/architecture-allowlist.txt` = 111 yozuv (QA AST: 111 = 111) | ✅ PASS | software-qa-engineer (QA batch 1) |
| WP6 | D7 | ④ | Ratchet mavjud (ro'yxat faqat qisqaradi) | allowlist diff | ratchet 3 yo'nalishda tekshirildi | ✅ PASS | software-qa-engineer (QA batch 1) |
| WP7 | D3 · D10 | ① | `grep "privileged"` va `grep "cgroup: host"` → 0 natija | grep | grep natijasi | ☐ PENDING | — |
| WP7 | D3 · D10 | ② | nsjail bake-off 25 case PASS | bake-off exit 0 | bake-off jurnali | ☐ PENDING | — |
| WP7 | D3 · D10 | ③ | Judge p95 latency raqami yozilgan | runbook'dagi raqam | runbook | ☐ PENDING | — |
| WP7 | D3 · D10 | ④ | Runtime image'da `USER` direktivasi mavjud | Dockerfile | Dockerfile | ☐ PENDING | — |
| WP7 | D3 · D10 | ⑤ | Bir bosqichda bajarilgan (oraliq `cap_drop` bosqichi yo'q) | compose diff | compose diff | ☐ PENDING | — |
| WP7 | D3 · D10 | ⑥ | Deploy-oldi dump olingan | backup fayli | dump fayli | ☐ PENDING | — |
| D1 | D1 | ① | 18 ADR (0028–0045): sarlavhalar inglizcha, nasr o'zbek (lotin) | `check_docs.py` yashil | 18 ADR fayli (0028–0045) | ✅ PASS | software-architect (gate: check_docs exit 0) |
| D1 | D1 | ② | `docs/07-adr/README.md` indeksi yangilangan (0027 ham) | indeks jadvali | README indeksi 45 qator (0001–0045) | ✅ PASS | software-architect (gate: check_docs exit 0) |
| D1 | D1 | ③ | Kirill/lotin aralashuvi yo'q | `check_docs.py` | `check_docs.py` yashil (kirill 0) | ✅ PASS | software-architect (gate: check_docs exit 0) |
| WP0 | D2 · D11A | EG-0 | Reconciliation jadvali + deploy siyosati artefakti | `check_docs.py` yashil · jadval fayli | `phase0-reconciliation-table-2026-09-29.md` | ✅ PASS | software-qa-engineer (QA batch 1) |
| WP7 | D3 · D10 | U1 | `privileged`siz nsjail bake-off 25 case → PASS/FAIL | bake-off exit kodi | bake-off jurnali | ☐ PENDING | — |

**Jami**: **43 qator** (41 mezon + 2 evidence gate qatori: `EG-0` · `U1`).

---

## 4. Evidence gate'lar (mezon emas — o'lchov)

| # | Gate | Nima o'lchanadi | Natija | Holat |
|---|---|---|---|---|
| U1 | Judge bake-off | `privileged`siz nsjail ishlaydimi (25 case) | PASS / FAIL | ☐ O'LCHANMAGAN |
| U2 | Seed user soni | Aniq joriy son (10 000 / 10 001 / 10 068) | Raqam | ☐ O'LCHANMAGAN |
| U3 | Jonli kontent raqamlari | 1 222 / 870 / 2 096 | Raqamlar | ☐ O'LCHANMAGAN |
| U5 | Remediation throughput | Kuniga nechta masala `validated` | Raqam | ☐ O'LCHANMAGAN |

> **U1** — WP7 ni **shartli** qiladi: FAIL bo'lsa **yangi owner decision** ochiladi. U2 · U3 · U5 — sof o'lchov (decision emas).

---

## 5. Xulosa

| Status | Soni |
|---|---|
| ✅ PASS | 16 |
| ⏳ IN PROGRESS | 5 |
| ☐ PENDING | 22 |
| ❌ FAIL | 0 |
| **Jami** | **43** |

**Taqsimot (WP bo'yicha):**
- ✅ PASS: WP0 (4) · WP5 (4) · WP6 (4) · D1 (3) · EG-0 (1) = **16**
- ⏳ IN PROGRESS: WP4 (5) = **5**
- ☐ PENDING: WP1 (6) · WP2 (3) · WP3 (6) · WP7 (6) · U1 (1) = **22**
- ❌ FAIL: **0**

**Izoh:** PASS qatorlari — dalili **bugun mavjud** mezonlar (gate exit 0 · QA mustaqil tasdiq · reconciliation yopilgan). WP4 hozir Engineer tomonidan bajarilmoqda (`⏳`). WP1 · WP2 · WP3 · WP7 va U1 — boshlanmagan (`☐`). Hech bir mezon **buzilmagan** (`❌ FAIL` = 0).

---

**STATUS:** Acceptance Criteria Traceability Matrix — tayyor. 43 qator: 16 PASS · 5 IN PROGRESS · 22 PENDING · 0 FAIL. Dalilsiz PASS yo'q.
