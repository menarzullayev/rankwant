# RankWant — Acceptance Criteria Lock (Frozen)

**Sana**: 2026-09-29
**Owner**: Saidakbar — **tasdiqlangan** (Lock criteria)
**Asos**: `owner-decision-closure-matrix-2026-09-29.md` (11/11 ACCEPTED)
**Holat**: 🔒 **FROZEN** — o'zgartirish uchun yangi owner decision talab qilinadi

> Bu mezonlar owner qarorlaridan **hosil qilingan** va egasi tomonidan **tasdiqlangan**. Endi ular implementation uchun majburiy.

---

## O'zgartirish siyosati (change control)

| Qoida | Mazmun |
|---|---|
| **Freeze** | Quyidagi mezonlar **qulflangan**. Ularni yumshatish yoki olib tashlash **yangi owner decision** talab qiladi |
| **Kuchaytirish** | Mezonni **kuchaytirish** (qattiqroq qilish) mumkin, lekin qayd etilishi shart |
| **O'lchovsiz mezon yo'q** | Har mezon **avtomatik yoki qo'lda o'lchanadigan** bo'lishi shart. "Bajarildi" degan so'z dalil emas |
| **Salbiy test** | Gate'lar uchun **salbiy (mutatsiya) testi majburiy** — hech qachon yiqilmaydigan tekshiruv qabul qilinmaydi |
| **U1 qayta ochilmaydi** | `privileged`siz nsjail — bu **decision emas**, **evidence gate**. Natija: PASS / FAIL |

---

## WP0 — Reconciliation va migration siyosati

| Element | Mazmun |
|---|---|
| **Qaror** | D2, D11A |
| **Mezonlar** | ① Reconciliation jadvali artefakti mavjud ② har faza↔komponent nomuvofiqligi uchun qaror qayd etilgan ③ §24 tie-break qoidasi yozilgan ④ migration/deploy siyosati hujjatlashtirilgan |
| **O'lchov** | Jadval fayli · `python tools/check_docs.py` yashil · `check_deploy_window.py` deploy'da majburiy |
| **Evidence gate** | — |

## WP1 — Content readiness

| Element | Mazmun |
|---|---|
| **Qaror** | D8, D8-F |
| **Mezonlar** | ① `test_sample_echo_is_not_ac` **yashil** ② `neg_refsolution_gate` buzilganda **qizil** (salbiy test) ③ `SELECT count(*) WHERE is_public AND readiness IS NULL` = **0** ④ graded contest `validated` bo'lmagan masalani **rad etadi** (400) ⑤ `legacy_unverified` masala public ko'rinadi, **contestda ishlatilmaydi** ⑥ taxonomy qayta yozilmaydi (allaqachon shipped) |
| **O'lchov** | pytest · SQL · graded gate testi · `check_verdict_codes.py` yashil |
| **Migration** | M1 |

## WP2 — Verdict taxonomy (faqat qolgan ish)

| Element | Mazmun |
|---|---|
| **Qaror** | D11B |
| **Mezonlar** | ① **4 o'lik kod nomlangan** va hujjatlashtirilgan ② M10 migratsiyasi bajarilgan ③ `RE_SIGNAL`/`RE_EXIT` split va i18n parity **qayta yozilmaydi** (shipped) |
| **O'lchov** | Hujjat · migratsiya · `check_verdict_codes.py` yashil |
| **Migration** | M10 |

## WP3 — Data origin

| Element | Mazmun |
|---|---|
| **Qaror** | D9 |
| **Mezonlar** | ① `origin` ustuni + enum mavjud ② **`Attempt.origin` YO'Q** (rad etilgan) ③ North Star SQL `origin='real'` bilan (JOIN) ishlaydi ④ backfill audit raqami chop etilgan ⑤ `imported` alohida qiymat ⑥ seed user aniq soni **o'lchangan** (10 000 / 10 001 / 10 068 nomuvofiqligi yopilgan) |
| **O'lchov** | `psql` · SQL xatosiz · `tools/check_metrics.py` exit 0 |
| **Migration** | M3 |

## WP4 — Secrets

| Element | Mazmun |
|---|---|
| **Qaror** | D5 |
| **Mezonlar** | ① `grep "PASSWORD: dev"` va `grep "devdevdev"` → **0 natija** ② `security.yml` `if: false` olib tashlangan va CI **yashil** ③ default sir bilan prod build **yiqiladi** (exit ≠ 0) ④ `SECRET_KEY` fallback → `ImproperlyConfigured` ⑤ rotation **keyin** bajariladi (tartib qulflangan) |
| **O'lchov** | grep · CI holati · build exit kodi · test |

## WP5 — AI boundary

| Element | Mazmun |
|---|---|
| **Qaror** | D6 |
| **Mezonlar** | ① `tools/check_ai_boundary.py` bugungi repo'da **yashil** ② DB-model import yoki testdata o'qish mutatsiyasi → **qizil** ③ AI qatlamida `DATABASE_URL` yo'q ④ AI Gateway **monolit modul** (`apps/api/ai/`) |
| **O'lchov** | Gate exit 0 · mutatsiya testi qizil |

## WP6 — Architecture boundary

| Element | Mazmun |
|---|---|
| **Qaror** | D7 |
| **Mezonlar** | ① `tools/check_architecture.py` + allowlist fayli mavjud ② **yangi** taqiqlangan import → CI **qizil** ③ allowlist'da mavjud buzilishlar soni yozilgan ④ ratchet mavjud (ro'yxat faqat qisqaradi) |
| **O'lchov** | Gate exit 0 · allowlist fayli · negative test |

## WP7 — Judge hardening

| Element | Mazmun |
|---|---|
| **Qaror** | D3, D10 |
| **Mezonlar** | ① `grep "privileged"` va `grep "cgroup: host"` → **0 natija** ② nsjail **bake-off 25 case PASS** ③ judge **p95 latency raqami yozilgan** ④ runtime image'da **`USER` direktivasi mavjud** ⑤ **bir bosqichda** bajarilgan (oraliq `cap_drop` bosqichi yo'q) ⑥ deploy-oldi dump olingan |
| **O'lchov** | grep · bake-off exit 0 · Dockerfile · runbook'dagi raqam |
| **Migration** | M2 |
| **⚠️ Evidence gate (U1)** | `privileged`siz nsjail ishlashi hali **o'lchanmagan**. U1 = bake-off natijasi. **PASS** → WP7 davom etadi · **FAIL** → owner qaroriga qaytadi (bu FAIL **yangi decision** ochadi) |

## D1 — ADR tili

| Element | Mazmun |
|---|---|
| **Qaror** | D1 |
| **Mezonlar** | ① 18 ADR (0028–0045): sarlavhalar **inglizcha**, nasr **o'zbek (lotin)** ② `docs/07-adr/README.md` indeksi yangilangan (**0027 ham qo'shilgan**) ③ kirill/lotin aralashuvi yo'q |
| **O'lchov** | `python tools/check_docs.py` yashil · indeks jadvali |

---

## Evidence gates (mezon emas — o'lchov)

| # | Gate | Nima o'lchanadi | Natija |
|---|---|---|---|
| **U1** | Judge bake-off | `privileged`siz nsjail ishlaydimi (25 case) | PASS / FAIL |
| **U2** | Seed user soni | Aniq joriy son (10 000 / 10 001 / 10 068) | Raqam |
| **U3** | Jonli kontent raqamlari | 1 222 / 870 / 2 096 | Raqamlar |
| **U5** | Remediatsiya throughput | Kuniga nechta masala `validated` | Raqam |

**Muhim:** U1 FAIL bo'lsa — bu **yangi owner decision** ochadi (WP7 yo'lini qayta ko'rish). U1 PASS bo'lsa — hech qanday qo'shimcha qaror kerak emas.

---

## Freeze holati

| Shart | Holat |
|---|---|
| Decision closure | ✅ 13/13 ACCEPTED |
| Scope freeze | ✅ WP0–WP7 |
| **Acceptance criteria locked** | ✅ **FROZEN (2026-09-29)** |
| WP0 reconciliation jadvali | ☐ bajarilishi kerak |
| U1 judge bake-off | ☐ bajarilishi kerak |

**Entry gate (yangilangan): 🟢 PASS** — qolgan ikki band (WP0, U1) **implementation ishi**, decision emas.

---

> Bu hujjat Owner Decision Closure Facilitator tomonidan tayyorlandi va egasi tomonidan **tasdiqlandi**. Mezonlar o'zgartirilishi uchun yangi owner decision talab qilinadi.
