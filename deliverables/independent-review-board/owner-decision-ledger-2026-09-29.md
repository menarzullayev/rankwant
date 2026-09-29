# RankWant — Owner Decision Ledger

**Sana**: 2026-09-29
**Facilitator**: Owner Decision Closure (AI) — **qaror qabul qilmaydi**
**Owner**: Saidakbar
**Manba**: `deliverables/independent-review-board/review-owner-decision-memo-2026-09-29.md`

> Har yozuv egasining aniq javobidan keyin qo'shiladi. Status faqat `ACCEPTED` / `REJECTED` / `DEFERRED`.

---

## Holat jadvali

| # | Decision | Status | Sana |
|---|---|---|---|
| D1 | ADR tili | **ACCEPTED** | 2026-09-29 |
| D2 | Phase 0 authoritative source (§21 vs §24) | **ACCEPTED** | 2026-09-29 |
| D3 | ADR 0028 classification / A− | **ACCEPTED** | 2026-09-29 |
| D4 | 3 triage corrections | **ACCEPTED** | 2026-09-29 |
| D5 | ADR 0044 secrets management | **ACCEPTED** | 2026-09-29 |
| D6 | ADR 0036 AI Gateway joylashuvi | **ACCEPTED** | 2026-09-29 |
| D7 | ADR 0042 dependency migration policy | **ACCEPTED** | 2026-09-29 |
| D8 | ADR 0037 content readiness | **ACCEPTED** | 2026-09-29 |
| D9 | ADR 0030 data origin | **ACCEPTED** | 2026-09-29 |
| D10 | ADR 0028 judge hardening target | **ACCEPTED** | 2026-09-29 |
| D11A | Gate-0 artefakti | **ACCEPTED** | 2026-09-29 |
| D11B | Verdict taxonomy scope | **ACCEPTED** | 2026-09-29 |

---

## D1 — ADR LANGUAGE — ACCEPTED

| Maydon | Qiymat |
|---|---|
| **Owner decision** | Ingliz sarlavha + o'zbek matn (bo'lim nomlari inglizcha, nasr o'zbekcha) |
| **Rationale** | Egasi izoh bermadi — qayd qilinmagan |
| **Evidence basis** | `docs/07-adr/` = 23 o'zbek + 4 ingliz (0022, 0023, 0024, 0027) · `CONTRIBUTING.md:82-96` ("yangi fayl inglizcha") · `check_docs.py` da til darvozasi **yo'q** (faqat yozuv aralashuvi) |
| **Consequences** | Korpusda 3 xil uslub: 23 o'zbek + 4 ingliz + 18 aralash. ADR shabloni (§7 — o'zbekcha bo'lim nomlari) yangilanishi shart |
| **Acceptance criteria** *(derived)* | 18 ADR faylida sarlavhalar inglizcha, nasr o'zbek (lotin) · `python tools/check_docs.py` yashil · `docs/07-adr/README.md` indeksi yangilangan (0027 ham qo'shilgan) |
| **Reversibility** | Asbob: two-way · Korpus: **one-way** (23 o'zbekcha ADR tahrirlanmaydi) |
| **Remaining follow-up** | ADR shablonidagi bo'lim nomlarini inglizchaga o'tkazish |
| **Status** | **ACCEPTED** |

---

## D2 — PHASE 0 AUTHORITATIVE SOURCE — ACCEPTED

| Maydon | Qiymat |
|---|---|
| **Owner decision (1)** | Yangi **reconciliation jadvali** authoritative qatlam bo'ladi; §24 done-condition **tie-break** qoidasi sifatida ishlatiladi |
| **Owner decision (2)** | Retrospektiv tekshiruv: **Ha — butun blueprint** |
| **Rationale** | Egasi izoh bermadi — qayd qilinmagan |
| **Evidence basis** | `:1741` §21 tartib qatori matnda "**Tartib taklifi**" deb belgilangan · `:1855` §24 Phase 0 komponentlari · `:1857` Phase 0 migratsiyasi (M1, M10, M2 boshlanishi, M5 o'lchov) · `:1859` Phase 0 done-condition (`privileged` tilga olinmagan) · `:1870` Phase 1 done-condition ④ (`privileged:true` yo'q) |
| **Consequences** | §21 tartib jadvali manba sifatida ishlatilmaydi · 0042 va 0036 **Phase 0 ga ko'chadi** · 0032 Phase 0 dan chiqadi · blueprint bo'ylab barcha faza↔komponent juftliklari tizimli qayta tekshiriladi |
| **Acceptance criteria** *(derived)* | Reconciliation jadvali artefakti mavjud · har nomuvofiqlik uchun qaror qayd etilgan · `python tools/check_docs.py` yashil |
| **Reversibility** | **Two-way** — hujjat/jarayon tanlovi |
| **Remaining follow-up** | Reconciliation jadvalini tuzish (yangi ish paketi — WP0 ga qo'shiladi) |
| **Status** | **ACCEPTED** |

---

## D3 — ADR 0028: M2 CHEGARASI + A− TASNIFI — ACCEPTED

| Maydon | Qiymat |
|---|---|
| **Owner decision (1)** | M2 **to'liq Phase 0 da** tugaydi — Phase 0 chiqishida **userns + seccomp** o'rnatilgan bo'lishi shart |
| **Owner decision (2)** | §24 Phase 1 done-condition ④ bilan ziddiyat **reconciliation jadvalida "owner override"** sifatida qayd etiladi; blueprint record o'zgarmaydi |
| **Owner decision (3)** | **0028 → A** (kod blokeri). **A− toifasi ishlatilmaydi** |
| **Rationale** | Egasi izoh bermadi — qayd qilinmagan |
| **Evidence basis** | `:1857` (M2 boshlanishi Phase 0) · `:1859` (Phase 0 done-condition) · `:1870` (Phase 1 done-condition ④) · `docker-compose.yml:192-193` · `sandbox.go:237-244` · `Dockerfile:222` · `check_negative.py:4139-4145` |
| **Consequences** | Phase 0 hajmi oshadi (userns + seccomp + bake-off Phase 0 ichida) · A− toifasi tarixdan chiqadi · reconciliation jadvalida 1 ta owner-override yozuvi paydo bo'ladi · 0028 endi oddiy A |
| **Acceptance criteria** *(derived)* | `privileged:true` va `cgroup: host` repo'da **yo'q** · nsjail bake-off 25 case o'tadi · judge p95 latency raqami yozilgan · reconciliation jadvalida override qayd etilgan |
| **Reversibility** | O'rta — compose + nsjail args o'zgaradi; M2 forward-only migratsiya intizomi, deploy-oldi dump shart |
| **Remaining follow-up** | **Bake-off hali o'lchanmagan** (UNVERIFIED) · seccomp profili loyihasi |
| **Status** | **ACCEPTED** |

---

## D4 — TRIAGE CORRECTIONS — ACCEPTED

| Maydon | Qiymat |
|---|---|
| **Owner decision** | **To'liq to'plamni qabul qilish:** `0042` → Phase 0 · `0036` → Phase 0 · `0028` → **A** · `0032` ≠ A (faqat M5 o'lchov) · **`0029` → B (Phase 1)** |
| **Rationale** | Egasi izoh bermadi — qayd qilinmagan |
| **Evidence basis** | D2 (§24 tie-break) · D3 (0028 → A) · `:1855` (Phase 0 komponentlari) · `:1857` (Phase 0 migratsiyasi) · Rex: 0029 "Phase 1, Phase 0 blokeri emas" |
| **Consequences** | Phase 0 to'plami qotdi: `check_architecture.py` + `check_ai_boundary.py` Phase 0 da · judge host ajratish Phase 1 da qoladi |
| **Acceptance criteria** *(derived)* | Gate'lar (0042, 0036) Phase 0 da mavjud va yashil · 0029 ning Phase 1 ga surilishi reconciliation jadvalida qayd etilgan |
| **Reversibility** | **Past** — tasnif qarori (two-way door) |
| **Remaining follow-up** | **Ochiq risk:** Phase 0 davomida judge hali ham Postgres/Redis/MinIO bilan bir hostda — D3 escape riskini kamaytiradi, lekin blast radius (DB + butun testdata) Phase 1 gacha saqlanadi |
| **Status** | **ACCEPTED** |

---

## D5 — ADR 0044 SECRETS MANAGEMENT — ACCEPTED

| Maydon | Qiymat |
|---|---|
| **Owner decision (1)** | **Env fayl + majburiy env (`${VAR:?}`) + fail-fast** |
| **Owner decision (2)** | Sir aylantirish — **wiring va fail-fast DAN KEYIN** |
| **Rationale** | Egasi izoh bermadi — qayd qilinmagan |
| **Evidence basis** | `docker-compose.yml:39,69,92,106,136,151,199` (hardcode) · overlay'lar override qilmaydi (0 moslik) · `.env.public` DB/S3 kalitlarini e'lon qilmaydi · `deploy.yml:211-215` (mavjud naqsh) · `settings.py:14-15` (faqat env o'qiydi) · `security.yml:32` `if: false` |
| **Consequences** | Mavjud naqsh kengaytiriladi · `.env.public` ga DB/MinIO/S3 kalitlari qo'shiladi · overlay hardcode olib tashlanadi · `security.yml` yoqiladi · Docker secrets va Vault **rad etildi** |
| **Acceptance criteria** *(derived)* | `grep "PASSWORD: dev"` va `grep "devdevdev"` → 0 natija · `security.yml` `if: false` olib tashlangan va CI yashil · default sir bilan prod build **yiqiladi** · `SECRET_KEY` fallback → `ImproperlyConfigured` |
| **Reversibility** | Menejer tanlovi — **two-way** · Exposed sirni aylantirish — **one-way** |
| **Remaining follow-up** | Sir bir muddat ko'proq ochiq turadi (aylantirish keyinga surildi) · rotation runbook yozilishi shart |
| **Status** | **ACCEPTED** |

---

## D6 — ADR 0036 AI GATEWAY JOYLASHUVI — ACCEPTED

| Maydon | Qiymat |
|---|---|
| **Owner decision** | **Monolit modul** — `apps/api/ai/` |
| **Rationale** | Egasi izoh bermadi — qayd qilinmagan |
| **Evidence basis** | Repo'da AI kodi **yo'q** · `check_ai_boundary.py` **mavjud emas** (Phase 0 da yoziladi — D4) · `§12.1` "modul yoki servis" vs `§12.6` "alohida servis" vs `§22` "monolith + 1 servis" (ichki ziddiyat) · `main.go:27-31` judge pretsedenti · `§22` "mikroservis yo'q" |
| **Consequences** | Gate import darajasida yoziladi · alohida servis **rad etildi** · chegara qoida + test bilan (OS darajasidagi uzilish yo'q) · deploy o'zgarmaydi |
| **Acceptance criteria** *(derived)* | `check_ai_boundary.py` bugungi repo'da **yashil** · DB-model import yoki testdata o'qish mutatsiyasi → **qizil** · AI'da `DATABASE_URL` yo'q |
| **Reversibility** | **Two-way** — modul↔servis: kod ko'chadi, compose + token + gate qayta yozish |
| **Remaining follow-up** | `0036 → 0042` ketma-ketligi (keyingi qaror) |
| **Status** | **ACCEPTED** |

---

## D7 — ADR 0042 DEPENDENCY MIGRATION POLICY — ACCEPTED

| Maydon | Qiymat |
|---|---|
| **Owner decision** | **Grandfather + RATCHET** — mavjud non-core import allowlist'da muzlaydi, ro'yxat faqat qisqaradi; **YANGI** import bugundan fail |
| **Rationale** | Egasi izoh bermadi — qayd qilinmagan |
| **Evidence basis** | O'lchandi: **417 qator / 244 production / 137 fayl / 67 tasi `core.models`** · `problems/services.py` va `problems/selectors.py` **mavjud emas** · blueprint: "Muddat yo'q — repo'da velocity yo'q" · IRB dissenti: "immediate fail ham soxta tanlov" |
| **Consequences** | `check_architecture.py` + allowlist fayli yoziladi · immediate-fail **rad etildi** (137 fayl yiqilardi) · sanali remediation **rad etildi** (velocity yo'q → fabrikatsiya) |
| **Acceptance criteria** *(derived)* | `check_architecture.py` mavjud va yashil · taqiqlangan **yangi** import → CI qizil · allowlist'da mavjud buzilishlar soni yozilgan |
| **Reversibility** | **Two-way** — allowlist bu fayl |
| **Remaining follow-up** | Ratchet egasi belgilanishi shart — aks holda ro'yxat qisqarmaydi va gate "muzlatilgan son" bo'lib qoladi |
| **Status** | **ACCEPTED** |

---

## D8 — ADR 0037 CONTENT READINESS — QISMIY

| Sub-qaror | Owner decision |
|---|---|
| **Mexanizm** | **Minimal holat-mashinasi** (enum + transition + gate, faqat gate uchun zarur holatlar bilan; taxonomy takrorlanmaydi) |
| **Test mezoni** | **Mezon, son emas** — ref-solution AC + namuna-echo AC emas + checker turi tasdiqlangan |
| **Trigger** | **Gibrid** — harness mexanik tekshiruvni tayyorlaydi, staff oxirgi tasdiqni beradi |
| **Arxiv** | **Hozircha tegmaslik** → **`DEFERRED`** |

| Maydon | Qiymat |
|---|---|
| **Rationale** | Egasi izoh bermadi — qayd qilinmagan |
| **Evidence basis** | `problems/models.py:229` (`readiness` yo'q, faqat `is_public`) · `models.py:268-313` (test gate yo'q) · `staff_serializers.py:116-130` (gate faqat **yangi** publish uchun) · `unpublish_testless.py:38-69` (delist vositasi **mavjud**) · `publish_problems.py:29-33` (bypass) · **`tests/regression/` papkasi YO'Q** · "≥5" asossiz (UNVERIFIED) |
| **Consequences** | Minimal holat-mashinasi + M1 backfill · "≥5" chegarasi **rad etildi** (mezon tanlandi) · delist **qilinmaydi** · taxonomy takrorlanmaydi (allaqachon shipped) |
| **Acceptance criteria** *(derived)* | `test_sample_echo_is_not_ac` yashil + `neg_refsolution_gate` buzilganda qizil · `is_public AND readiness IS NULL` = 0 · graded contest `validated` bo'lmagan masalani rad etadi · `check_verdict_codes.py` yashil |
| **Reversibility** | Aralash — ustun qo'shish two-way; migratsiya forward-only |
| **Remaining follow-up** | **Arxiv sub-qarori `DEFERRED`** → legacy masalalarning **graded eligibility** savoli ochiq (D8-F) |
| **Status** | **QISMIY** (3/4 hal, 1 `DEFERRED`) |

### D8-F — LEGACY GRADED ELIGIBILITY — ACCEPTED

| Maydon | Qiymat |
|---|---|
| **Owner decision** | **Graded'dan chiqarish** — 1 222 masala `legacy_unverified` default oladi, **public ko'rinishda qoladi**, lekin **graded contestdan chiqariladi** |
| **Rationale** | Egasi izoh bermadi — qayd qilinmagan |
| **Evidence basis** | Phase 0 done-condition: "`print('3 2 1')` endi AC OLMAYDI" · platformada 0 real user (narx hozir nazariy) |
| **Consequences** | Phase 0 done-condition bajariladi · **lekin** bugungi holatda `validated` ~0 → **graded contest remediatsiya tugaguncha o'tkazib bo'lmaydi** |
| **Acceptance criteria** *(derived)* | Graded contest `validated` bo'lmagan masalani **rad etadi** · `legacy_unverified` masala public ro'yxatda ko'rinadi, lekin contestda ishlatilmaydi |
| **Reversibility** | O'rta — masalani `validated` qilish orqali qaytariladi (remediatsiya orqali) |
| **Remaining follow-up** | Remediatsiya throughput'i o'lchanmagan (Q20) — contest qachon qayta ochilishini **aytib bo'lmaydi** |
| **Status** | **ACCEPTED** |

---

## D9 — ADR 0030 DATA ORIGIN — ACCEPTED

| Sub-qaror | Owner decision |
|---|---|
| **Model** | **`User.origin`** (enum) — **`Attempt.origin` denormalizatsiyasi YO'Q** |
| **Imported** | **Alohida origin qiymati** |
| **Neytron** | **Hozircha o'chirilmaydi** — platforma mantig'ini testlash uchun kerak; **2027 Q1 production launch**da baza tozalanadi |

| Maydon | Qiymat |
|---|---|
| **Rationale (egasi berdi)** | "bu kabi userlar butun platforma mantig'ini testlash uchun menga hali kerak bo'ladi. 2027-yilning dastlabki choragida platformani productionga chiqaramiz, o'shanda butun baza tozalanadi" |
| **Evidence basis** | `User.origin` ham, `is_seeded` ham repo'da **yo'q** (PROVEN) · seeder `seed_stress.py:26,84`, default **10 000** (`:51`) · `prune_test_users.py:40-65` (o'chirish vositasi + cascade + `recount_problems`) · ADR-0023:22,79 · imported mualliflar ham, stress userlar ham email'siz (`core/models.py:295-297`) |
| **Consequences** | 384 569 qatorli `Attempt` backfill **yo'q** (tejaldi) · North Star **JOIN** bo'ladi · `is_seeded` boolean **rad etildi** · o'chirish **DEFERRED → 2027 Q1** |
| **Acceptance criteria** *(derived)* | `origin` ustuni + enum mavjud · North Star SQL `origin='real'` bilan (JOIN orqali) ishlaydi · backfill audit raqami chop etilgan · `check_metrics.py` yashil |
| **Reversibility** | add→backfill→NOT NULL (forward-only) · O'chirish keyinroq — cascade bilan **one-way** |
| **Remaining follow-up** | **Son nomuvofiqligi ochiq:** 10 000 / 10 001 / 10 068 — aniq joriy son **o'lchanmagan** · `check_metrics.py` hali yozilmagan |
| **Status** | **ACCEPTED** |

---

## D10 — ADR 0028 JUDGE HARDENING YO'LI — ACCEPTED

| Maydon | Qiymat |
|---|---|
| **Owner decision** | **Bir bosqichda** — `privileged` off + **userns + seccomp** bitta deploy'da; oldidan **majburiy 25-case bake-off** |
| **Rationale** | Egasi izoh bermadi — qayd qilinmagan |
| **Evidence basis** | `docker-compose.yml:192-193` (`privileged: true` + `cgroup: host`) · `sandbox.go:237-244` (`outside=0`) · `Dockerfile:222` (`FROM scratch`, `USER` yo'q) · `check_negative.py:4139-4145` (mutatsiya fixture'i) · Archi dissenti: oraliq qadam xavfni kamaytirmasligi mumkin |
| **Consequences** | Oraliq `cap_drop` bosqichi **rad etildi** · bake-off deploy'dan **oldin** majburiy · contest oynasidan tashqarida deploy shart · deploy-oldi dump shart |
| **Acceptance criteria** *(derived)* | `privileged:true` va `cgroup: host` repo'da **yo'q** · nsjail bake-off 25 case o'tadi · judge p95 latency raqami yozilgan · runtime image'ga `USER` direktivasi qo'shilgan |
| **Reversibility** | O'rta — compose + nsjail args; M2 forward-only migratsiya intizomi |
| **Remaining follow-up** | **`privileged`siz nsjail ishlashi hali O'LCHANMAGAN** (UNVERIFIED) — bake-off natijasiga qadar bu yo'l isbotlanmagan · seccomp profili loyihasi |
| **Status** | **ACCEPTED** |

---

## D11A — GATE-0 ARTEFAKTI — ACCEPTED

| Maydon | Qiymat |
|---|---|
| **Owner decision** | **Mavjud tekshiruv + hujjatlashtirilgan siyosat** — alohida Gate-0 artefakti yaratilmaydi |
| **Rationale** | Egasi izoh bermadi — qayd qilinmagan |
| **Evidence basis** | `tools/check_deploy_window.py` **allaqachon mavjud** (exit 0/1/2), chaqiriladi `deploy.yml:230` va `deploy.sh:290` · Process o'rindig'i dissenti: u "gate" emas, "deploy-shart" (PR-CI'da ishlamaydi) · Gate-0 ro'yxati to'liq emas (`check_verdict_codes.py` yo'q) |
| **Consequences** | Yangi artefakt yo'q · ko'rinadigan majburlash nuqtasi bo'lmaydi · feature-flag infratuzilmasi (F62) **hamon yo'q** — M2/M3 dual-write uchun alohida ish |
| **Acceptance criteria** *(derived)* | Migration/deploy siyosati hujjatlashtirilgan · `check_deploy_window.py` deploy'da majburiy · contest oynasida deploy bloklanadi |
| **Reversibility** | **Past** — hujjat/siyosat |
| **Remaining follow-up** | **Feature flag yo'q (F62)** — M2/M3 dual-write uchun kerak; siyosat uni yaratmaydi |
| **Status** | **ACCEPTED** |

---

## D11B — VERDICT TAXONOMY SCOPE — ACCEPTED

| Maydon | Qiymat |
|---|---|
| **Owner decision** | **Faqat qolgan ish** — qaysi **4 kod** o'lik ekanini nomlash + 18 163 `RE` qatorning **M10 qayta yorliqlanishi**. Shipped mexanizmlar **takrorlanmaydi** |
| **Rationale** | Egasi izoh bermadi — qayd qilinmagan |
| **Evidence basis** | RE split **allaqachon kodda** (`verdicts.py:19-20`) · i18n parity + o'lik-kod detektori **allaqachon CI'da** (`check_verdict_codes.py:56,121,124-129`) · salbiy testlar (`check_negative.py:5504,5517,6091`) |
| **Consequences** | 0037 **sun'iy kattalashmaydi** · alohida `0037a` ADR **yaratilmaydi** · taxonomy implementation ishi **deyarli yo'q** |
| **Acceptance criteria** *(derived)* | 4 o'lik kod **nomlangan** va hujjatlashtirilgan · M10 migratsiyasi bajarilgan · `check_verdict_codes.py` yashil |
| **Reversibility** | **Past** — data/qaror ishi |
| **Remaining follow-up** | M10 data migration **egasi belgilanmagan** · 4 kod hali nomlanmagan (UNVERIFIED) |
| **Status** | **ACCEPTED** |

### ⚠️ Jarayon uchun yangi fakt

Egasi **production launch: 2027 Q1** deb belgiladi. Bu blueprint'da yo'q bo'lgan **yagona sanali ma'lumot** ("repo'da velocity yo'q / no timeline" deyilgan edi). Oqibati: **D7** da "velocity yo'q → sanalar fabrikatsiya" asosi bilan rad etilgan *sanali remediation* varianti qayta ko'rilishi mumkin. Bu — **ochiq belgi**, qayta ochilmagan qaror.
