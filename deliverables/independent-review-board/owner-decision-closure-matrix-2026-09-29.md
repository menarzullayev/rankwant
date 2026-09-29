# RankWant — Owner Decision Closure Matrix

**Sana**: 2026-09-29
**Facilitator**: Owner Decision Closure (AI) — **qaror qabul qilmagan**
**Owner**: Saidakbar
**Kirish**: 11 ta blocking owner decision (IRB `review-owner-decision-memo-2026-09-29.md`)
**Batafsil yozuvlar**: `owner-decision-ledger-2026-09-29.md`

> Har bir qator egasining **aniq javobi**dan keyin yozilgan. Tasdiqlanmagan hech narsa "accepted" deb belgilanmagan.

---

## 1. Owner Decision Matrix

| # | Decision | Owner decision | Status |
|---|---|---|---|
| **D1** | ADR tili | Ingliz sarlavha + o'zbek matn | **ACCEPTED** |
| **D2** | Phase 0 authoritative source | Reconciliation jadvali authoritative; §24 **tie-break**. Retrospektiv: **butun blueprint** | **ACCEPTED** |
| **D3** | ADR 0028 / A− | M2 **to'liq Phase 0 da**; §24 bilan ziddiyat reconciliation'da **owner override**; **0028 → A**; A− **ishlatilmaydi** | **ACCEPTED** |
| **D4** | Triage corrections | **To'liq to'plam** — 0042↑, 0036↑, 0028→A, 0032≠A, **0029→B** | **ACCEPTED** |
| **D5** | ADR 0044 secrets | **Env + majburiy env + fail-fast**; rotation **KEYIN** | **ACCEPTED** |
| **D6** | ADR 0036 AI boundary | **Monolit modul** (`apps/api/ai/`) | **ACCEPTED** |
| **D7** | ADR 0042 dependency policy | **Grandfather + ratchet** | **ACCEPTED** |
| **D8** | ADR 0037 content readiness | **Minimal holat-mashinasi** · **Mezon (son emas)** · **Gibrid trigger** · arxiv → D8-F | **ACCEPTED** |
| **D8-F** | Legacy graded eligibility | **Graded'dan chiqarish** (public qoladi, contestdan chiqariladi) | **ACCEPTED** |
| **D9** | ADR 0030 data origin | **`User.origin`** (Attempt'siz) · **imported alohida** · neytron **o'chirilmaydi** → 2027 Q1 | **ACCEPTED** |
| **D10** | ADR 0028 hardening yo'li | **Bir bosqichda** + oldidan **majburiy 25-case bake-off** | **ACCEPTED** |
| **D11A** | Gate-0 artefakti | **Mavjud tekshiruv + siyosat** (yangi artefakt yo'q) | **ACCEPTED** |
| **D11B** | Verdict taxonomy scope | **Faqat qolgan ish** — 4 kod nomlash + M10 qayta yorliqlash | **ACCEPTED** |

---

## 2. Status xulosasi

| Status | Soni | Izoh |
|---|---|---|
| **ACCEPTED** | **13** | 11 ta decision + 2 ta sub-decision (D8-F, D11A/B ichida) |
| **REJECTED** | **0** | — |
| **DEFERRED** | **1** | `neytron_*` userlarni o'chirish → **2027 Q1** (egasi: testlash uchun kerak). **Bloklamaydi** |

**Muhim:** D8 ning "arxiv" sub-savoli dastlab `DEFERRED` edi, keyin **D8-F** bilan yopildi. Ya'ni ochiq qolgan DEFERRED yo'q.

---

## 3. Dependency graph

```text
D1 (ADR tili)
   └── 18 ADR fayli (0028–0045) yozilishi mumkin bo'ladi
          └── Gate'dagi 6 qaror faylga ega bo'ladi

D2 (reconciliation jadvali + §24 tie-break)
   └── D4 (gate a'zoligi)

D3 (M2 to'liq Phase 0 da)
   ├── D4 (0028 → A)
   └── D10 (yo'l tanlovi)

D6 (monolit modul)
   └── D7 (0042 allowlist AI joylashuvini biladi)   ← ketma-ket SHART

D8 (readiness)
   └── D8-F (legacy graded eligibility)

Mustaqil: D5 · D9 · D11A · D11B
```

---

## 4. Qabul mezonlari (har ACCEPTED qaror uchun)

> ✅ Bu mezonlar qarorlardan **hosil qilingan** va egasi tomonidan **2026-09-29 da TASDIQLANGAN** (Lock criteria). To'liq muzlatilgan versiya: `acceptance-criteria-lock-2026-09-29.md`.

| Decision | Qabul mezonlari | Qanday o'lchanadi |
|---|---|---|
| **D1** | 18 ADR: sarlavhalar inglizcha, nasr o'zbek (lotin) | `python tools/check_docs.py` yashil · indeks yangilangan (0027 ham) |
| **D2** | Reconciliation jadvali mavjud; har nomuvofiqlik uchun qaror qayd etilgan | Jadval fayli + `check_docs.py` yashil |
| **D3** | `privileged:true` va `cgroup: host` repo'da **yo'q**; bake-off 25 case o'tadi; p95 latency yozilgan | `grep "privileged"` → 0 · bake-off exit 0 |
| **D4** | `check_architecture.py` va `check_ai_boundary.py` Phase 0 da mavjud; 0029 ning Phase 1 ga surilishi qayd etilgan | Gate fayllari + reconciliation yozuvi |
| **D5** | `grep "PASSWORD: dev"` va `grep "devdevdev"` → **0**; `security.yml` yoqilgan va CI yashil; default sir bilan prod build **yiqiladi** | grep natijasi · CI holati · build exit ≠ 0 |
| **D6** | `check_ai_boundary.py` bugungi repo'da **yashil**; DB-model import mutatsiyasi → **qizil** | Gate exit 0 · mutatsiya testi qizil |
| **D7** | `check_architecture.py` mavjud va yashil; **yangi** taqiqlangan import → CI qizil; allowlist'da mavjud son yozilgan | Gate exit 0 · allowlist fayli |
| **D8** | `test_sample_echo_is_not_ac` yashil + `neg_refsolution_gate` buzilganda **qizil**; `is_public AND readiness IS NULL` = 0; graded contest `validated`sizni rad etadi | Testlar + SQL · pytest R8 = 400 |
| **D8-F** | `legacy_unverified` masala public ro'yxatda ko'rinadi, lekin **contestda ishlatilmaydi** | Graded gate testi |
| **D9** | `origin` ustuni mavjud; North Star SQL `origin='real'` bilan (JOIN) ishlaydi; backfill audit raqami chop etilgan | `psql` · SQL xatosiz · `check_metrics.py` exit 0 |
| **D10** | nsjail bake-off 25 case o'tadi; runtime image'ga `USER` direktivasi qo'shilgan; deploy-oldi dump olingan | bake-off exit 0 · Dockerfile · backup fayli |
| **D11A** | Siyosat hujjatlashtirilgan; `check_deploy_window.py` deploy'da majburiy | Hujjat + `deploy.yml:230` |
| **D11B** | 4 o'lik kod **nomlangan**; M10 migratsiyasi bajarilgan | Hujjat + migratsiya + `check_verdict_codes.py` yashil |

---

## 5. Yopilmagan savollar (unresolved)

| # | Savol | Turi | Bloklaydimi |
|---|---|---|---|
| U1 | `privileged`siz nsjail ishlaydimi? | **O'lchov** | ⚠️ **HA — WP7** |
| U2 | Seed user aniq soni: **10 000 / 10 001 / 10 068** | **O'lchov** | Yo'q (M1/M3 dan oldin kerak) |
| U3 | 1 222 / 870 / 2 096 — jonli qiymatlar | **O'lchov** | Yo'q (M1 dan oldin) |
| U4 | Qaysi **4 verdict kodi** o'lik | **Qaror** | Yo'q (WP2 ichida) |
| U5 | Remediatsiya throughput'i (Q20) | **O'lchov** | Yo'q (contest qayta ochilish sanasini belgilaydi) |
| U6 | `tests/regression/` papkasi yo'q — harness yozilmagan | **Ish** | Yo'q (WP1 ichida) |
| U7 | Host cgroup v1/v2 | **O'lchov** | Yo'q |
| U8 | `.env.public` jonli runtime qiymatlari | **O'lchov** | Yo'q |
| U9 | `docs/07-adr/README.md` indeksi 0027 ni sanamaydi | **Ish** | Yo'q (D1 bilan birga) |

**Xulosa:** faqat **U1** implementation scope'ini bekor qilishi mumkin — va u **o'lchov**, qaror emas.

---

## 6. Implementation blockers

| Blocker | Holat |
|---|---|
| 18 ADR yozilmagan | ✅ **Ochildi** (D1) |
| Gate a'zoligi noaniq | ✅ **Ochildi** (D2, D4) |
| 0028 tasnifi noaniq | ✅ **Ochildi** (D3) |
| Secrets modeli yo'q | ✅ **Ochildi** (D5) |
| AI joylashuvi noaniq | ✅ **Ochildi** (D6) |
| Dependency policy yo'q | ✅ **Ochildi** (D7) |
| Readiness siyosati yo'q | ✅ **Ochildi** (D8, D8-F) |
| Origin modeli yo'q | ✅ **Ochildi** (D9) |
| Judge hardening yo'li noaniq | ✅ **Ochildi** (D10) |
| Migration discipline egasiz | ✅ **Ochildi** (D11A) |
| Taxonomy scope shishirilgan | ✅ **Ochildi** (D11B) |
| **Qabul mezonlari tasdiqlanmagan** | ✅ **YOPILDI** — 2026-09-29 da freeze qilindi |
| **Reconciliation jadvali qurilmagan** | ⚠️ **OCHIQ** — D2 natijasi, WP0 |
| **U1 — bake-off o'tkazilmagan** | ⚠️ **OCHIQ** — WP7 ni shartli qiladi |

---

## 7. Scope Freeze (yangilangan)

| WP | Mazmun | Asos | Migration |
|---|---|---|---|
| **WP0** | Reconciliation jadvali (D2) + migration/deploy siyosati (D11A) | D2, D11A | — |
| **WP1** | Minimal `Problem.readiness` + ref-solution harness + graded gate + `legacy_unverified` backfill | D8, D8-F | M1 |
| **WP2** | 4 o'lik kod nomlash + M10 tarixiy qayta yorliqlash | D11B | M10 |
| **WP3** | `User.origin` + backfill + `check_metrics.py` (**Attempt.origin YO'Q**) | D9 | M3 |
| **WP4** | Secrets: env + fail-fast + `security.yml` ON (rotation **keyin**) | D5 | — |
| **WP5** | `check_ai_boundary.py` (modul chegarasi) | D6 | — |
| **WP6** | `check_architecture.py` + allowlist (grandfather + ratchet) | D7 | — |
| **WP7** | Judge hardening: **bir bosqichda** userns + seccomp + `USER` + bake-off | D3, D10 | M2 |

**WP7 — yangi:** D3 va D10 tufayli ADR 0028 **Phase 0 ga ko'chdi** (avval Phase 1 edi).

**OUT of scope (tegilmaydi):** 0029 judge host ajratish · staging (0040) · PITR/backup (0043) · event schema (0031) · object-level authz (0045) · Billing (0041) · AI Gateway runtime (0033–0035) · Sentry (0039) · judge queue semantikasi (0038) · throttle **ijrosi** (0032 — faqat o'lchov) · `core/views.py` bo'lish (TD16) · Redis rol ajratish (TD23).

---

## 8. Software Company — Entry Gate

| Shart | Holat |
|---|---|
| Barcha implementation-blocking qarorlar ACCEPTED yoki non-blocking DEFERRED | ✅ **Bajarildi** (13/13 ACCEPTED, 1 non-blocking DEFERRED) |
| Qabul mezonlari **locked** | ✅ **BAJARILDI** — 2026-09-29 da freeze qilindi |
| Scope **frozen** | ✅ **Bajarildi** (WP0–WP7) |
| Yopilmagan savollar scope'ni bekor qila olmaydi | ⚠️ **SHARTLI** — faqat U1 (bake-off) WP7 ni shartli qiladi |
| Har bir keltirilgan artefakt solishtirilgan | ☐ WP0 reconciliation jadvali — **implementation ishi**, decision emas |

**Hukm: 🟢 PASS.**

`Software Company` **boshlanishi mumkin**. Qolgan ikki band endi **decision emas** — implementation ishi va evidence gate:

1. **WP0 — reconciliation jadvali** (D2 natijasi) → Software Company bilan **parallel**
2. **U1 — judge bake-off** (D10 evidence gate) → WP7 ning texnik asosini tasdiqlaydi yoki rad etadi. **U1 FAIL bo'lsa — yangi owner decision ochiladi**

---

## 9. Ochilgan yangi fakt

Egasi **production launch: 2027 Q1** deb belgiladi. Bu blueprint'da yo'q bo'lgan **yagona sanali ma'lumot** ("repo'da velocity yo'q / no timeline axis" deyilgan edi).

**Oqibati:** D7 da "velocity yo'q → sanalar fabrikatsiya bo'ladi" asosi bilan rad etilgan *sanali remediation* varianti **qayta ko'rilishi mumkin**. Bu — **ochiq belgi**; D7 qayta ochilmagan.

---

> Bu hujjat Owner Decision Closure Facilitator tomonidan AI yordamida tayyorlandi. Unda **hech qanday qaror o'ylab topilmagan** — har bir qator egasining aniq javobiga asoslanadi. Tasdiqlanmagan bandlar `derived` yoki `SHARTLI` deb belgilangan.
