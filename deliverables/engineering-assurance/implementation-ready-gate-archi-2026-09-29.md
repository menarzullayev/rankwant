# RankWant — Implementation-Ready Gate: Qarorlarni yopish va Acceptance Criteria lock

**Sana**: 2026-09-29 · **Muallif**: Archi (System Architect) · **Holat**: Proposed — egasi tasdig'ini kutadi
**Manba**: `system-design-phase0-decision-closure-2026-09-29.md`, `software-architecture-rankwant-2026-09-29.md` (§21–26), repo kodi (qayta tekshirildi).
**Constraint**: Kod yo'q · yakuniy qaror yo'q — faqat *texnik* mezonlar qulflanadi.

---

## 1. Gate Validation — to'plam va tartib

**Xulosa: to'plam deyarli to'liq — 1 ta bo'shliq (taxonomy scope) + 1 ta kesishuvchi shart (migration/deploy discipline).**

| Savol | Javob |
|---|---|
| {0037, 0030, 0044, 0036, 0042, 0028} **to'liq**mi? | **Yo'q — 2 tuzatish bilan to'liq bo'ladi** (quyida) |
| Verdict-taxonomy (RE split, 4 dead code, i18n) kerakmi? | **HA, lekin yangi ADR emas** — 0037 ichidagi *work package*. Aks holda 0037 "yopildi" deb e'lon qilinadi-yu, taxonomy ochiq qoladi. Bo'shliqni yopish: 0037 mezoniga ② dead-code + RE split + i18n parity qo'shilsin (yoki `0037a` ajratilsin). |
| `M5` throttle **o'lchovi** kerakmi? | **YO'Q (gate'ni bloklamaydi)** — bu *o'lchov*, qarori Phase 4 (ADR 0032). Parallel bajariladi. |
| `0029`/`0032` kerakmi? | **YO'Q** — B guruhi, Phase 1/4. |
| Migration discipline (M1/M2/M10 forward-only + deploy-window) kerakmi? | **HA** — ADR emas, lekin **kesishuvchi gate-sharti**. Rex buni Phase 0 blokeri deb belgilagan; `check_deploy_window.py` mavjud (exit 0/1/2). Gate'ga `Gate-0` sifatida kiritilsin. |

**Tartib — tasdiqlangan, 1 tuzatish bilan.** Egasi tartibi: `0037 → 0030 → 0044 → 0036 → 0042 → 0028`. Bu **yozish/tasdiqlash** tartibi sifatida to'g'ri (0037 — kritik yo'l boshi). Tuzatish: **0028 ning *qarori* M2 boshlanishidan oldin kerak**, M2 esa Phase 0 da boshlanadi → 0028 ni oxiriga surish *ijro* uchun to'g'ri, *qaror* uchun kech. Tavsiya: 0028 **qarori** 0030/0044 bilan parallel, **ijrosi** Phase 1.

**Parallelizm**: `0044` mustaqil (parallel). `0030` qarori mustaqil (parallel; faqat *ijro* 0037 backfill oynasi bilan ketma-ket). `0028` qarori mustaqil (parallel). **Ketma-ket bo'lishi shart**: `0036 → 0042` (0042 allowlist'i 0036 ning AI joylashuvini bilishi kerak).

---

## 2. Locked Acceptance Criteria (6 blok)

| Qaror | Qulflangan mezon | Qanday o'lchanadi | Kim tasdiqlaydi |
|---|---|---|---|
| **0037** Content readiness | ① `print('3 2 1')` graded masalada **AC emas** ② har public masala `readiness IS NULL` → 0 qator ③ graded contest `validated` bo'lmagan masalani rad etadi (400) ④ 1 222 arxiv `legacy_unverified` ga backfill ⑤ **dead-code + RE split + i18n** yopilgan | ① `test_ref_solution_verdicts.py::test_sample_echo_is_not_ac` yashil + `neg_refsolution_gate` buzilganda qizil ② `SELECT count(*) FROM problems WHERE is_public AND readiness IS NULL` = 0 ③ pytest R8 = 400 ④ M1 migration count = 1 222 ⑤ `check_verdict_codes.py` yashil, 10 locale `verdict.<CODE>` parity | Tessa (test) + Archi (kontrakt) |
| **0030** Data origin | ① `origin` ustuni + `Attempt.origin` mavjud ② North Star SQL `origin='real'` bilan **bajariladi** ③ backfill audit raqami ④ `check_metrics.py` **yashil** | ① `psql \d users` ② SQL xatosiz ishlaydi (`is_seeded` yo'q) ③ per-value `User.origin` soni chop etilgan ④ **yangi** `tools/check_metrics.py` CI'da exit 0 | Rex (data) + Tessa |
| **0044** Secrets | ① prod compose'da literal default **yo'q** ② `security.yml` `if: false` **olib tashlangan** ③ default sir bilan prod build **yiqiladi** ④ `SECRET_KEY` fallback olib tashlangan | ① `grep "PASSWORD: dev"` va `grep "devdevdev"` — `docker-compose*.yml` bo'ylab 0 natija ② CI job yashil (gitleaks/pip-audit/npm audit) ③ build exit ≠ 0 ④ `ImproperlyConfigured` testi | Cody (review) + Rex |
| **0036** AI boundary | ① `check_ai_boundary.py` mavjud va bugungi repo'da **yashil** ② AI DB-model import qilsa / testdata o'qisa → **qizil** ③ AI'da `DATABASE_URL` yo'q | ① **yangi** `tools/check_ai_boundary.py` exit 0 ② mutatsiya testi (import buziladi → qizil) ③ runtime guard (judge `main.go:27-31` naqshi) | Cody + Archi |
| **0042** Architecture boundary | ① `check_architecture.py` + allowlist fayli repo'da ② taqiqlangan import → CI qizil ③ mavjud buzilishlar **sanab** grandfathered yoki tuzatilgan | ① **yangi** `tools/check_architecture.py` exit 0 ② negative test qizil ③ allowlist'da yozilgan son | Cody + Archi |
| **0028** Judge privilege | ① `privileged: true` / `cgroup: host` **yo'q** ② `cap_drop: [ALL]` + minimal `cap_add` ③ nsjail bake-off **25 case** o'tadi ④ judge p95 latency **raqami yozilgan** | ① `grep "privileged"` va `grep "cgroup: host"` — `docker-compose.yml` bo'ylab 0 natija ② compose faylda mavjud ③ bake-off exit 0 ④ raqam runbook'da | Cody (review) + Rex |

---

## 3. Implementation Scope Freeze

**Birinchi yoziladigan work package'lar (tartib bilan):**

| WP | Mazmun | ADR | Migration |
|---|---|---|---|
| **WP0** | Migration/deploy discipline lock: forward-only M1/M2/M10, `check_deploy_window.py` majburiy, feature flag F62 | Gate-0 | — |
| **WP1** | `Problem.readiness` holat-mashinasi + ref-solution harness + graded gate | 0037 | M1 |
| **WP2** | Verdict taxonomy: `RE_SIGNAL`/`RE_EXIT` split, dead-code hujjati, i18n 10 til | 0037 | M10 |
| **WP3** | `origin` ustuni + backfill + `check_metrics.py` | 0030 | M3 |
| **WP4** | Secrets fail-fast + `security.yml` ON | 0044 | — |
| **WP5** | `check_ai_boundary.py` | 0036 | — |
| **WP6** | `check_architecture.py` | 0042 | — |

**OUT of scope (tegilmaydi):** AI Gateway (0033/0034/0035) · Billing (0041) · 4-host topologiya (0029/M6) · staging (0040) · **judge host separation (0029)** · event envelope/sxema (0031/M4) · object-level authz (0045) · backup/PITR/DR (0043) · monitoring/Sentry (0039) · judge queue semantikasi (0038) · **throttle ijrosi** (0032 — faqat *o'lchov* WP0 ichida) · `core/views.py` bo'lish (TD16) · Redis rol ajratish (TD23).

---

## 4. Remaining Open for the Owner

| # | Band | BLOCKING? |
|---|---|---|
| 1 | **ADR tili** — 0001–0027 **o'zbek (lotin)** (tekshirildi), brief "English" deydi | 🔴 **BLOCKING** (0028–0045 uslubi) |
| 2 | **A− guruhi kontseptsiyasi** (0028 = Phase 0 chiqish blokeri) tasdiqi | 🔴 **BLOCKING** (0028 gate'ga kiradimi) |
| 3 | **3 triage tuzatish**: 0042/0036 yuqoriga · 0028/0029 pastga · 0032 ≠ A | 🔴 **BLOCKING** (gate a'zoligini o'zgartiradi) |
| 4 | **Taxonomy scope**: 0037 ichida yoki alohida `0037a` | 🔴 **BLOCKING** (0037 chegarasi) |
| 5 | **Migration/deploy discipline** gate- elementi sifatida tasdiq | 🔴 **BLOCKING** (WP0) |
| 6 | 0037: yashirin-test chegarasi (≥5?), `legacy_unverified` public qoladimi, `validated` ni kim trigger qiladi | 🔴 **BLOCKING** 0037 |
| 7 | 0030: `neytron_*` (10 001) o'chiriladimi (Q16), `imported` alohida origin'mi | 🔴 **BLOCKING** 0030 |
| 8 | 0044: sir menejeri tanlovi, sirlarni hozir aylantirishmi | 🔴 **BLOCKING** 0044 |
| 9 | 0036: AI Gateway modulmi yoki alohida servis (Q19) | 🔴 **BLOCKING** 0042 (allowlist) |
| 10 | 0042: mavjud buzilishlar grandfathered yoki darhol fail | 🔴 **BLOCKING** 0042 |
| 11 | 0028: oraliq `cap_drop` yoki to'liq userns+seccomp | 🔴 **BLOCKING** 0028 |
| 12 | 0029/0032 qarorlari · `M5` o'lchov jadvali · Sentry/GlitchTip (0039) · staging (0040) | 🟢 NON-BLOCKING |

**UNVERIFIED**: aniq qaysi **4 verdict kodi** "o'lik" (PS F05 da nom yo'q) · `check_metrics.py` mavjud emas (yaratiladi) · `check_architecture.py`/`check_ai_boundary.py` mavjud emas (yaratiladi) · `ReferenceSolution` per-subtask (TD24, D5) · host cgroup v1/v2.
