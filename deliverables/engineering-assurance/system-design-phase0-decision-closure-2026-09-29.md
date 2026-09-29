# RankWant — Phase 0: Texnik Qarorlarni Yopish va Assurance Hisoboti

**Sana**: 2026-09-29
**Workflow**: 2 — System Design (Technical Decision Closure + Assurance)
**Jamoa**: Engineering Assurance Team — Zhen (Engineering Director, rahbar) · Archi (System Architect) · Cody (Code Reviewer) · Rex (SRE Engineer) · Tessa (Testing Expert) · Docu (Technical Writer)
**Manba**: `deliverables/software-architecture/software-architecture-rankwant-2026-09-29.md` (§4, §7, §11, §13, §17, §21–26), `deliverables/product-strategy/product-strategy-rankwant-2026-09-29.md`, `docs/07-adr/0001..0027`, repo kodi.

**Scope chegarasi (egasi tomonidan qat'iy belgilangan)**:
- Kod **yozilmagan** — bu sessiya faqat texnik aniqlashtirish va assurance.
- Yakuniy product/architecture qarorlari **qabul qilinmagan** — hammasi egasi tasdig'ini kutadi.
- 18 ADR ning **hammasi** emas — faqat keyingi implementationni **bloklayotganlari**.

---

## 📌 TL;DR

- **Bloklovchi qarorlar soni: 5 ta** (ADR 0037, 0030, 0044, 0036, 0042) + **1 ta Phase 0 chiqish blokeri** (ADR 0028, kelishmovchilik hal qilindi).
- **Implementation-Ready Gate (§9)**: 6 qaror tasdiqlanmaguncha `Software Company` boshlanmaydi. Gate'da **2 bo'shliq** topildi (verdict-taxonomy scope, migration/deploy discipline). Egasi uchun **11 ta BLOCKING** band.
- Blueprint'ning Phase 0 ro'yxatiga **3 tuzatish** kiritildi: `0042` va `0036` **yuqoriga** ko'chirildi, `0028`/`0029`/`0032` pastga tushirildi.
- **Kod bo'yicha eng og'ir topilma**: `docker-compose.public.yml` production parollarini **override qilmaydi** — ya'ni prod DB paroli literally `dev`. Bu blueprint'dagi G16 dan **kuchliroq** da'vo.
- Severity taqsimoti: 🔴 **8** · 🟠 **4** · 🟡 **2**.
- Bloklovchi: **12 ta topilma** (ulardan 8 tasi 🔴). B2B yoki "ishonchli judge" e'loni bu yopilmaguncha asossiz.

---

## 🎯 核心结论卡片

| 项目 | 内容 |
|------|------|
| 整体评级 | 🟡 **有条件通过** — Phase 0 kodini boshlash mumkin, lekin chiqish mezonlari yopilmagan |
| 阻塞项数量 | **5 ta qaror** + **8 ta 🔴 topilma** |
| 关键行动项 | **8 ta egasi qarori** (gate) + **3 ta injenerlik amali** |
| 建议下一步 | **Implementation-Ready Gate**: 6 qarorni (0037, 0030, 0044, 0036, 0042, 0028) tasdiqlash → keyin `Software Company` |

**Nega "shartli"**: Phase 0 ning *kodini* bloklaydigan qarorlar aniq (5 ta). Lekin Phase 0 ning *maqsadi* — "ishonch" — bugungi kod holatida **ta'minlanmagan**: judge izolyatsiyasi bitta nsjail bug'ga bog'liq, prod parollari hardcode, `security.yml` o'chirilgan.

---

## 1. Talab va maqsad

Arxitektura blueprint'i tugagan, lekin **qaror sifatida ochiq**: 18 ADR fayli yozilmagan, 20 texnik savol javobsiz, 5 ta Product ↔ Repository ziddiyati hal qilinmagan, 28 texnik qarz (10 tasi P0).

**Maqsad**: keyingi implementation qadamini bloklayotgan texnik qarorlarni **aniqlashtirish** (qabul qilish emas), Phase 0 texnik dizaynini, test strategiyasini va runbook rejasini berish.

**Done mezoni**: har bloklovchi qaror uchun — qaror bayoni, variantlar, repo dalili, tavsiya etilgan texnik yechim, ishonch darajasi, falsifikator va **o'lchanadigan qabul mezoni**.

---

## 2. Yuqori darajali dizayn

```text
Blueprint (§21-26)
   │
   ├── A  guruhi (5)  → kod blokeri        → Phase 0 kodini boshlashdan OLDIN yopilishi shart
   ├── A- guruhi (1)  → Phase 0 chiqish blokeri (M2 boshlanishi) → qaror hozir, ijro Phase 1
   ├── B  guruhi (2)  → Phase 0 ichida, lekin kodni bloklamaydi
   └── C  guruhi (10) → Phase 1+ (bu hisobotda ochib berilmaydi)
```

Phase 0 ning texnik konturi (Archi dizayni):

```text
Content integrity (ADR 0037)
        ├── Problem.readiness holat-mashinasi
        ├── ref-solution regressiya harness
        ├── checker validatsiya
        └── verdict taksonomiyasi
                ↓
Uch darvoza (gates)  ←  ADR 0042 (check_architecture) · ADR 0030 (check_metrics) · ADR 0036 (check_ai_boundary)
                ↓
Secrets gate + security.yml ON  ←  ADR 0044
```

---

## 3. ADR Triage va Qaror-Qoralamalari

### 3.1 Triage (18 ADR)

Test: *"Phase 0 kodini shu qaror qabul qilinmasa yozib bo'ladimi?"* — YO'Q → **A**.

| ADR | Mavzu | Phase 0 komponenti | Guruh | Sabab |
|---|---|---|---|---|
| 0037 | Content integrity gate | readiness + regressiya + checker + taksonomiya | **A** | Shu komponentlarning kontrakti — qarorsiz model va gate yozilmaydi |
| 0030 | Data origin | `check_metrics.py` | **A** | Gate `origin='real'` maydonini bilishi shart |
| 0044 | Secrets management | secrets gate + `security.yml` ON | **A** | Gate siyosatni talab qiladi |
| 0036 | AI data boundary | `check_ai_boundary.py` | **A** | Gate taqiq ro'yxatini talab qiladi |
| 0042 | Modul chegarasi | `check_architecture.py` | **A** | Gate import allowlist'ini talab qiladi |
| 0028 | Judge privilege modeli | M2 boshlanishi | **A−** | Kodni bloklamaydi, lekin Phase 0 ni "tugadi" deb e'lon qilishni bloklaydi |
| 0029 | Judge host ajratish | 4-host topologiya | **B** | Topologiya ishi, kod blokeri emas |
| 0032 | NAT throttle | M5 o'lchov (kod emas) | **B** | Phase 0 faqat o'lchov; qaror Phase 4 |
| 0031 | Event sxemasi | — | C | Phase 2 |
| 0033 | AI Gateway | — | C | Phase 3 |
| 0034 | AI model routing | — | C | Phase 3 |
| 0035 | AI contest isolation | — | C | Phase 3 |
| 0038 | Judge queue semantikasi | — | C | Phase 1 |
| 0039 | Monitoring / Sentry | — | C | Phase 1 |
| 0040 | Staging | — | C | Phase 1 |
| 0043 | Backup / PITR / DR | — | C | Phase 1 |
| 0041 | Billing boundary | — | C | Phase 4 |
| 0045 | Audit + object-level authz | — | C | Phase 4 |

**Blueprint tartibiga 3 tuzatish:**

1. **`0042` va `0036` yuqoriga ko'chirildi.** Blueprint ularni Phase 1 va Phase 3 ga qo'ygan. Lekin `check_architecture.py` va `check_ai_boundary.py` — Phase 0 **komponenti** va done-condition ⑤. Darvozani qarorsiz yozib bo'lmaydi.
2. **`0028` va `0029` pastga tushirildi.** Blueprint o'zi §24 da `privileged:true yo'q` ni **Phase 1** done-condition deb belgilaydi, Phase 0 komponentlar ro'yxatida esa judge privilege umuman yo'q — ichki nomuvofiqlik.
3. **`0032` A emas.** Phase 0 da faqat *o'lchov* bor (kod emas).

### 3.2 Kelishmovchilik va uning yechimi — ADR 0028

Jamoalar orasida **haqiqiy kelishmovchilik** chiqdi va uni rahbar sifatida yopish kerak edi:

| Tomon | Da'vo |
|---|---|
| **Archi** | ADR 0028 — **B** guruhi (Phase 1): Phase 0 kodi uni kutmasdan yoziladi |
| **Cody** | 🔴 **bloklaydi** — izolyatsiya chegarasi faqat nsjail; bitta nsjail/kernel bug = host root |
| **Rex** | Phase 0 da M2 **boshlanadi**; M1/M2/M10 deploy+rollback rejasi Phase 0 ni bevosita bloklaydi |
| **Blueprint** | Phase 0 migratsiya ro'yxatida `M2 (boshlanishi)` bor, lekin done-condition uni Phase 1 ga qo'yadi |

**Yechim (rahbar qarori):** ziddiyat "Phase 0 kodini **boshlash**" va "Phase 0 ni **tugadi deb e'lon qilish**" tushunchalarini aralashtirishdan kelib chiqadi.

- Phase 0 kodini 0028 qarorisiz **boshlash mumkin** → Archi haq.
- Phase 0 ni **tugadi** deb e'lon qilish mumkin emas → Cody va Rex haq.

Shu sababli yangi guruh kiritildi: **A− — Phase 0 chiqish blokeri**. ADR 0028 qarori **hozir** kerak (chunki M2 Phase 0 da boshlanadi), ijrosi Phase 1 ga cho'ziladi.

### 3.3 A guruhi — qaror-qoralamalari

#### ADR 0037 — Content integrity quality gate

| Element | Mazmun |
|---|---|
| **Qaror** | `Problem.readiness` ni aniq holat-mashinasi sifatida belgilash va uni public ko'rinish hamda graded contest uchun **yagona** gate qilish |
| **Nega bloklaydi** | `Problem` da `readiness` yo'q — faqat `is_public` boolean (`apps/api/problems/models.py:229`); `save()`/`clean()` da yashirin-test gate yo'q (`:268-313`) |
| **Variantlar** | ① faqat publish-time to'siq (status quo) ② `readiness` enum + transition + gate ③ alohida `ProblemReadiness` modeli ④ AI-generatsiya |
| **Tavsiya** | **②** — ishonch: **yuqori** |
| **Falsifikator** | Agar harness ref-solution'ni judge'da ishga tushira olmasa (latency yoki credential), backfill bloklanadi |
| **Qabul mezoni** | `print('3 2 1')` graded masalada hech qachon AC emas; har public masala `readiness='validated'`; graded contest `validated` bo'lmagan masalani rad etadi; 1 222 arxiv `legacy_unverified` ga backfill |
| **NEEDS OWNER** | yashirin test chegarasi (≥5?); `legacy_unverified` public qoladimi; `validated` ni kim trigger qiladi |

#### ADR 0030 — Data origin (real / demo)

| Element | Mazmun |
|---|---|
| **Qaror** | `is_seeded` boolean yoki `User.origin` enum + denormalizatsiya `Attempt.origin` |
| **Nega bloklaydi** | `check_metrics.py` qaysi maydonni tekshirishini bilishi shart; North Star SQL `is_seeded` ishlatadi — ustun **yo'q** (CONFLICT-2) |
| **Variantlar** | ① `is_seeded` boolean ② `User.origin` enum {real, demo, imported, staff} + `Attempt.origin` ③ faqat event darajasi ④ `neytron_` prefiks |
| **Tavsiya** | **②** — ishonch: **o'rta-yuqori** |
| **Falsifikator** | Backfill 10 001 seed userni noto'g'ri tasniflasa segmentatsiya buziladi |
| **Qabul mezoni** | North Star `origin='real'` bilan hisoblanadi; `check_metrics.py` yashil; backfill audit raqami mavjud |
| **NEEDS OWNER** | 10 001 `neytron_*` user o'chiriladimi (Q16); `imported` alohida origin'mi |

#### ADR 0044 — Secrets management

| Element | Mazmun |
|---|---|
| **Qaror** | Production'da default **yo'q** (fail-fast); sir env/Docker secret orqali; `security.yml` majburiy |
| **Nega bloklaydi** | secrets gate + `security.yml` ON — Phase 0 done-condition ④; gate siyosatni talab qiladi |
| **Variantlar** | ① env fayl ② Docker secret ③ Vault |
| **Tavsiya** | **② + fail-fast + sir aylantirish** — ishonch: **yuqori** |
| **Falsifikator** | Dev-default bilan ishlaydigan servis fail-fast'da yiqilsa — bosqichma-bosqich o'tish kerak |
| **Qabul mezoni** | `security.yml` CI'da yashil; prod compose'da default yo'q; default sir bilan prod build **yiqiladi** |
| **NEEDS OWNER** | sir menejeri tanlovi; sirlarni hozir aylantirishmi |

#### ADR 0036 — AI data boundary

| Element | Mazmun |
|---|---|
| **Qaror** | AI qatlami nima o'qiy oladi — context whitelist, `DATABASE_URL` yo'q, judge va testdata'ga tegilmaydi; `check_ai_boundary.py` majburlaydi |
| **Nega bloklaydi** | `check_ai_boundary.py` — Phase 0 done-condition ⑤; chegara ta'rifisiz darvoza bo'sh |
| **Variantlar** | ① to'liq DB kirish ② read replica ③ context whitelist + DB credential yo'q + tool allowlist |
| **Tavsiya** | **③** — ishonch: **yuqori** (darvoza hozir vakuumli yashil o'tadi) |
| **Repo pretsedenti** | Judge `DATABASE_URL` ni **rad etadi** (`services/judge-go/main.go:24-115`) — takrorlanadigan naqsh |
| **Qabul mezoni** | Darvoza AI kodi DB modelini import qilsa yoki testdata o'qisa **yiqiladi**; bugungi repo'da yashil |
| **NEEDS OWNER** | AI Gateway modulmi yoki alohida servis (Q19) |

#### ADR 0042 — Modul chegarasi (dependency rules)

| Element | Mazmun |
|---|---|
| **Qaror** | App'lar import allowlist'i + `tools/check_architecture.py` |
| **Nega bloklaydi** | `check_architecture.py` — Phase 0 done-condition ⑤; qoida yo'q bo'lsa darvoza yo'q |
| **Variantlar** | ① faqat hujjat qoidasi ② to'liq paket ajratish ③ import allowlist + darvoza (inkremental) |
| **Tavsiya** | **③** (baseline grandfathering) — ishonch: **o'rta** |
| **Falsifikator** | Mavjud import'lar soni juda ko'p bo'lsa, allowlist bosqichma-bosqich kengaytiriladi |
| **Qabul mezoni** | Taqiqlangan import'da darvoza CI'ni yiqiladi; allowlist repo'da |
| **NEEDS OWNER** | Mavjud buzilishlar grandfathered yoki darhol fail |

### 3.4 A− guruhi — ADR 0028 (Phase 0 chiqish blokeri)

| Element | Mazmun |
|---|---|
| **Qaror** | Judge konteyneri `privileged` **bo'lmaydi**: systemd `Delegate=yes` bilan cgroup delegatsiya + nsjail userns + aniq seccomp profili |
| **Nega A−** | Phase 0 kodi kutmasdan yoziladi, lekin M2 Phase 0 da **boshlanadi** va Phase 0 ning "ishonch" maqsadi usiz ta'minlanmaydi |
| **Kod dalili** | `docker-compose.yml:192-193` (`privileged: true` + `cgroup: host`); `services/judge-go/sandbox.go:237-244` (nsjail `inside=65534, outside=0`) |
| **Tavsiya** | Rootless userns + seccomp; oraliq qadam sifatida `cap_drop: [ALL]` + minimal `cap_add` |
| **Falsifikator** | `privileged` siz nsjail ishlamasa yoki perf regressiyasi bo'lsa — bake-off 25 case bilan qayta o'lchash |
| **Qabul mezoni** | `privileged:true` repo'da **yo'q**; nsjail bake-off 25 case o'tadi; judge p95 latency raqami yozilgan |

### 3.5 ADR yozish tartibi (A guruhi)

1. **0037** — kritik yo'l boshi; readiness va taksonomiya boshqa butun trust ishining verdict semantikasini belgilaydi.
2. **0030** — `check_metrics.py` va remediation dashboard'lari origin'ga bog'liq; 0037 backfill bilan bir migratsiya intizomida.
3. **0044** — mustaqil, past xavf; done-condition ④ ni ochadi; 0037/0030 bilan **parallel** yozilishi mumkin.
4. **0036** — AI modul/servis qarori (Q19) 0042 allowlist'iga ta'sir qiladi; darvoza hozir vakuumli yoziladi.
5. **0042** — allowlist AI joylashuvini (0036) hisobga olishi uchun **oxirgi**.

---

## 4. Kod Darajasidagi Assurance (Cody)

| # | Sev | Kategoriya | Fayl:satr | Muammo | Tavsiya | Phase 0 bloklaydimi |
|---|---|---|---|---|---|---|
| 1 | 🔴 | Security / Isolation | `docker-compose.yml:192-193` | `privileged: true` + `cgroup: host` — barcha capabilities, seccomp/AppArmor cheklovisiz, host cgroupns ulashilgan | Host ajratish + userns + seccomp; oraliq: `cap_drop: [ALL]` + minimal `cap_add` | yes |
| 2 | 🔴 | Security / Isolation | `services/judge-go/sandbox.go:237-244` | nsjail `inside=65534, outside=0` — submission host uid 0 da ishlaydi. #1 bilan birga: konteyner root = host root | Rootless userns (65534:65534) | yes |
| 3 | 🔴 | Secrets | `docker-compose.yml:39` | `POSTGRES_PASSWORD: dev` — **hardcode**, `${...}` emas. `docker-compose.public.yml` uni **override qilmaydi** → prod DB paroli literally `dev` | `${POSTGRES_PASSWORD:?}` | yes |
| 4 | 🔴 | Secrets | `docker-compose.yml:69,92,106,136,151,199` | `MINIO_ROOT_PASSWORD: devdevdev`, `S3_SECRET: devdevdev` — hardcode, public overlay override qilmaydi | `${MINIO_ROOT_PASSWORD:?}` / `${S3_SECRET:?}` | yes |
| 5 | 🔴 | Secrets | `config/settings.py:22` | `SECRET_KEY` fallback `dev-only-not-for-production` — ommaviy repo'da ma'lum kalit; sessiya/CSRF/PAT forge → superuser egallash | Defaultni olib tashlash; bo'sh bo'lsa `ImproperlyConfigured` | yes |
| 6 | 🔴 | Security / Supply chain | `.github/workflows/security.yml:32` | `if: false` — gitleaks, pip-audit, npm audit CI'da **umuman ishlamaydi** | Job'ni yoqish | yes |
| 7 | 🟠 | Correctness / Supply chain | `services/judge-go/Dockerfile:13,26` | `ARG NSJAIL_REF=master` — harakatlanuvchi havola; "pinned images" da'vosi nsjail uchun **FALSE** | `NSJAIL_REF` ni commit-SHA ga qotirish; image'larni `@sha256:` bilan pin qilish | no |
| 8 | 🔴 | Authorization | `apps/api` (butun papka) | `has_object_permission` — **0 ta moslik**. Avtorizatsiya faqat imperativ: `classroom/views.py:116,145`, `core/permissions.py:39` | Umumiy `BasePermission` + `has_object_permission` | yes |
| 9 | 🟠 | Authorization / Multi-tenant | `classroom/models.py:19-27`; `classroom/serializers.py:29-35` | `Organization` yo'q; `join_code` — sinfga kirishning yagona darvozasi; a'zolar ro'yxati oshkor | Org-scoped authz + `join_code` rotatsiyasi | yes (B2B oldidan) |
| 10 | 🟠 | Maintainability / Boundary | `arena/services.py:15`; `judging/serializers.py:8-9`; `ratings/services.py:12,284,371`; `classroom/serializers.py:8` | App'lar bir-birining `models`ini import qiladi; `check_security_boundary.py` faqat compose chegarasini o'lchaydi, Python import chegarasini **EMAS** | `check_architecture.py` (ADR 0042) | no |
| 11 | 🟠 | Correctness / Reliability | `services/judge-go/main.go:74-114` | At-most-once: `BRPOP` job'ni olib tashlaydi; crash bo'lsa job **yo'qoladi**; `LPush` xatosida ham `continue` — retry yo'q | Ack pattern (RPOPLPUSH / streams) yoki `reap_stuck` hujjatlash; worker pool | no |
| 12 | 🟡 | Performance | `core/throttling.py:34-55,95-112` | Baza compose `TRUSTED_CLIENT_IP_HEADER` ni o'rnatmaydi (faqat public overlay) → dev stack'da bucket kollapsi | Base compose'ga ham sozlamani qo'yish | no |
| 13 | 🟡 | Performance | `docker-compose.yml` (barcha servislar) | `deploy.resources` / `mem_limit` / `cpus` yo'q (G10) | Limitlar qo'shish | no |

**Cody'ning FACT vs ASSUMPTION ajratmasi (judge izolyatsiyasi):**

- **FACT**: `DATABASE_URL` yo'qligi haqiqiy — runtime guard `main.go:27-31` (bo'lsa `exit 1`) va `check_security_boundary.py:46,210-213`. Judge port nashr etmaydi (`:53`, `INTERNAL_ONLY`). Per-run network ns `--iface_no_lo` (`sandbox.go:272`). cgroup limitlari bor (`sandbox.go:271-306,349-366`) — lekin **o'sha privileged konteyner ichida**. Runtime image `FROM scratch`, **USER direktivasi yo'q** → konteyner root.
- **ASSUMPTION**: nsjail versiyasi xavfsiz deb qabul qilingan (`NSJAIL_REF=master`). Escape testlari hozircha ishlamaydi (`security.yml:94-99` "bake-off'dan keyin" deb belgilaydi).
- **UNVERIFIED**: host cgroup versiyasi (v1/v2), seccomp/AppArmor host profili, `.env.public` haqiqiy qiymatlari, `tests/security/run.sh` mavjudligi.

**Muhim tuzatish**: blueprint G16 "dev-default'lar" degan. Cody aniqroq o'lchadi — **public overlay ham override qilmaydi**, ya'ni bu shunchaki "dev default" emas, balki **production'da ham amal qiladigan hardcode**. TD6 ning og'irligi oshadi.

---

## 5. Ishlatish va Reliability (Rex)

| # | Band | Joriy holat | Target | Phase 0 bloklaydimi |
|---|---|---|---|---|
| 1 | Judge host ajratish (ADR 0029) | 1 host, 9 konteyner; `compose/four-host/README.md` allaqachon target | judge alohida host(lar); faqat judge → data Redis/S3 | **Yo'q** (Phase 1) |
| 2 | Staging yo'qligi (ADR 0040) | `deploy.yml:25-29` faqat input; infra yo'q | minimal viable staging, four-host rejasiga mos | **Yo'q** (Phase 1) |
| 3 | Backup / PITR / DR (ADR 0043) | `tools/backup.sh:24-28` — oylik, off-site **OFF**, PITR yo'q, RPO ≤30 kun | kunlik + off-site ON + shifrlash + WAL→R2; RPO ≤24 soat | **Yo'q** (to'liq target), lekin deploy-oldi dump **shart** |
| 4 | Resource limitlar (G10 / TD15) | hech bir servisda limit yo'q; faqat log limiti (10m × 3) | har servisga `mem_limit` + `cpus`; judge eng qattiq | **Yo'q**, lekin M2 bilan birga tavsiya |
| 5 | Alerting (TD25 / CONFLICT-4) | metrics store yo'q; faqat `/api/v1/slo/` (`core/views.py:141-160`) | Telegram ops kanali | **Yo'q** (Phase 1) |
| 6 | Deploy / rollback — M1/M2/M10 | forward-only migratsiya; contest oynasi tekshiriladi | har M alohida deploy + dump-only | **HA** |

**Uch muhim operatsion topilma:**

1. **Off-site backup `off` — sababi bor.** `tools/backup.sh:125-127`: 2026-09-17 da shifrlanmagan PII dump R2 ga ketgan. Ya'ni **off-site'ni yoqishdan OLDIN shifrlash shart** — tartib teskari bo'lsa PII yana sizadi.
2. **Telegram bot allaqachon bor** (`notifications/tasks.py:35` `send_telegram`, `TELEGRAM_BOT_TOKEN`). Alerting shu tokenni alohida **ops** chat_id bilan ishlatishi mumkin — va bu Sentry CI taqiqini **buzmaydi**. ⚠️ GlitchTip ham Sentry SDK ishlatadi → CI qoidasi bilan ziddiyat ehtimoli bor.
3. **Deploy himoyalari real**: `check_deploy_window.py` contest oynasida deploy'ni to'xtatadi; `check_deploy.sh` GIT_SHA yorlig'ini tekshiradi; `backup.sh` da avtomatik `restore_test()` va `verify_dump` bor (kuchli tomon).

**M1/M2/M10 risklari**: M1 backfill (1 226 qator) — default noto'g'ri bo'lsa hamma masala bloklanadi. M2 — nsjail regressiyasi → 0 verdict. M10 — 18 163 `RE` qator yorlig'i o'zgarsa 384 569 tarixiy `Attempt` bilan mos kelmasligi mumkin.

---

## 6. Test Strategiyasi (Tessa)

**Mavjud asos (o'lchangan, qayta ishlatiladi)**: `tools/check_negative.py` (6 992 qator) — **mutatsiya/salbiy test naqshi allaqachon bor**; `tools/check_verdict_codes.py` — verdict taksonomiyasi darvozasi; `test_staff_problems.py::TestTestsizOmmagaChiqmaydi` — mavjud e'lon darvozasi testlari. **Yo'q**: `Problem.readiness`, `check_architecture.py`, `check_ai_boundary.py`.

**Ref-solution harness**: `tests/regression/test_ref_solution_verdicts.py` — `test_sample_echo_is_not_ac` + `test_reference_solution_is_ac`.

**Salbiy (mutatsiya) testi MAJBURIY**: `check_negative.py` ga `neg_refsolution_gate` guruhi qo'shiladi — serializer vaqtincha buziladi va `test_sample_echo_is_not_ac` **qizil bo'lishi TALAB qilinadi**. O'tsa — test o'lik, darvoza yiqiladi. Ikki qavat: darvoza (serializer) + data/judge (chetlab o'tilgan yozuvni ham tutadi).

**`Problem.readiness` matritsasi**: `draft → needs_tests → has_hidden_tests → checker_validated → ref_solution_verified → validated`, yon holatlar `blocked` / `needs_review`. 10 test (R1–R10), jumladan: R2 testsiz e'lon → 400; R5 checker turi majburiy; R7 sample-echo AC bersa → `blocked`; R8 `validated` bo'lmagan masala baholi contestga → 400; R10 `draft → validated` sakrash → `ValidationError`.

**Q20 (eng muhim o'lchanmagan raqam)**: `validated` = ≥1 yashirin test + checker turi metasida + ref-solution AC + sample-echo ≠ AC. Counter = append-only `ContentReadinessEvent`. Baseline hozir **0** (instrumentatsiya yo'q) — bu o'zi bir topilma.

**CI taqsimoti**: PR(api) → readiness + content pytest · PR(web|tools) → `check_negative` (`neg_refsolution_gate` bilan) · PR(barcha) → `check_docs` / `check_decisions` / `check_verdict_codes` · Nightly → haqiqiy judge ref-solution + latency p95 < 15 s.

---

## 7. Hujjat Strukturasi va Runbook (Docu)

**ADR shabloni (0028–0045)**: Metadata (STATUS, Approved by, Evidence, Ta'siri) + 8 bo'lim: Muammo · Variantlar · Tanlov · Sabab · Oqibatlar · **Qaytarilishi** (yangi) · **Tasdiq** (yangi) · Bog'liq hujjatlar. Mavjud ADR lar qayta raqamlanmaydi va tahrirlanmaydi.

**Indekslash**: fayl yo'li — `docs/07-adr/NNNN-slug.md` (4 xonali raqam + kebab-case slug). Index jadvali uch ustundan iborat: faylga nisbiy havola, sarlavha, holat. Holat qalin yoziladi (`accepted`, `rejected`, `proposed`); sana qavsda qo'shilishi mumkin.

**Runbook to'plami**: deploy (mavjudni kengaytirish) · rollback (yangi) · judge-incident (yangi) · backup-restore (yangi) · secrets-rotation (yangi). Umumiy skelet: trigger → old shart → qadamlar → tasdiq → rollback → eskalatsiya.

**Doc debt tuzatish siyosati**: qulflangan hujjat (06-architecture, 08-technical-spec, accepted ADR) — **hech qachon joyida tahrirlanmaydi** → yangi ADR + errata. Qulflanmagan (`docs/10-operations` README — draft) → joyida tuzatish mumkin. Sana bilan belgilangan deliverable → errata + yangi ADR.

| Hujjat | Da'vo | Tuzatish usuli |
|---|---|---|
| `docs/10-operations/README.md` (378, 730, 960) | staging mavjud (CONFLICT-3) | Qulflanmagan → joyida |
| `docs/10-operations/README.md` (84, 90) | throttle `60/min` (CONFLICT-1) | Joyida → `1500/hour` |
| `deliverables/product-strategy/...2026-09-29.md` | Sentry quriladi (CONFLICT-4) | Record → yangi ADR + errata |

**Ochiq savol (egasi hal qilishi kerak)**: brief "repo docs = English" deydi, **lekin o'lchandi** — ADR-0001..0027 va `check_docs.py` xabarlari **o'zbek (lotin)**. Yangi ADR lar qaysi tilda yozilishini tasdiqlash kerak, aks holda 0028–0045 uslubi buziladi.

**check_docs.py tuzoqlari**: `ADR-NNNN` mavjud bo'lmagan faylga → xato (yangi ADR yozilguncha `ADR NNNN` ishlatilsin) · katakdagi `\|` → ustun soni buziladi · kirill/lotin aralashuvi nasrda → xato · `deliverables/` **to'liq** tekshiriladi.

---

## 8. Risklar va Savdolar

| # | Risk | Sabab | Yumshatish |
|---|---|---|---|
| R1 | Prod parollari haqiqatan `dev` bo'lishi mumkin | Public overlay override qilmaydi | ADR 0044 ni birinchi bo'lib tasdiqlash |
| R2 | nsjail escape → host root | `privileged` + `outside=0` | ADR 0028 (A−), seccomp + userns |
| R3 | Kontent remediatsiyasi cho'zilib ketishi | Inson-bound, throughput o'lchanmagan | Q20 o'lchovini Phase 0 ning birinchi ishi qilish |
| R4 | Darvozalar "o'lik test" ga aylanishi | Salbiy test yozilmasa | `neg_refsolution_gate` majburiy |
| R5 | ADR tili bo'yicha kelishmovchilik | Mavjud ADR lar o'zbekcha | Egasi qarori |
| R6 | Migratsiya M2 judge'ni sindirishi | nsjail sozlamasi o'zgaradi | Bake-off 25 case + deploy-oldi dump |

---

## 9. Implementation-Ready Gate

> Bu bo'lim egasi talabiga ko'ra qo'shildi (rev.2). Batafsil mezon jadvali: `implementation-ready-gate-archi-2026-09-29.md` (Archi, System Architect).

**Asosiy xulosa:** Engineering Assurance bosqichi **mazmunan tugagan**, lekin loyiha **"implementation-ready" emas**. `Software Company` ga o'tishdan oldin 6 ta qaror egasi tomonidan tasdiqlanishi shart.

### 9.1 Gate zanjiri

```text
Egasi tasdig'i (11 ta BLOCKING band)
   │
   ├─ 0037 Content readiness ─┐
   ├─ 0030 Data origin        │  PARALLEL mumkin:
   ├─ 0044 Secrets            │  0037 · 0030 · 0044 · 0028(qarori)
   ├─ 0036 AI boundary        │  KETMA-KET SHART:
   ├─ 0042 Architecture bnd   │  0036 → 0042
   └─ 0028 Judge privilege    ┘
        ↓
Engineering Assurance:
   decision closure confirmed
   → acceptance criteria locked
   → implementation scope frozen
        ↓
Software Company
```

**Tartibga tuzatish:** egasi tartibi (`0037 → 0030 → 0044 → 0036 → 0042 → 0028`) **yozish/tasdiqlash** uchun to'g'ri — 0037 kritik yo'l boshi. Lekin **0028 ning qarori M2 boshlanishidan oldin kerak** (M2 Phase 0 da boshlanadi). Ya'ni 0028 ni oxiriga surish *ijro* uchun to'g'ri, *qaror* uchun kech. Tavsiya: 0028 qarori **parallel**, ijrosi Phase 1.

### 9.2 To'plam to'liqmi — 2 bo'shliq topildi

| Savol | Javob |
|---|---|
| {0037, 0030, 0044, 0036, 0042, 0028} to'liqmi? | **Yo'q — 2 tuzatish bilan to'liq bo'ladi** |
| Verdict-taxonomy (RE split, 4 dead code, i18n 10 til) kerakmi? | **HA, lekin yangi ADR emas** — 0037 ichidagi work package. Aks holda 0037 "yopildi" deb e'lon qilinadi-yu taxonomy ochiq qoladi. Yechim: 0037 mezoniga qo'shilsin yoki `0037a` ajratilsin |
| Migration/deploy discipline (M1/M2/M10 forward-only + `check_deploy_window.py`) kerakmi? | **HA** — ADR emas, lekin kesishuvchi gate-shart. `Gate-0` sifatida kiritilsin |
| `M5` throttle o'lchovi kerakmi? | **YO'Q** — bu o'lchov, qarori Phase 4 (ADR 0032). Parallel bajariladi |
| `0029` / `0032` qarorlari kerakmi? | **YO'Q** — B guruhi, Phase 1/4 |

### 9.3 Implementation Scope Freeze

| WP | Mazmun | ADR | Migration |
|---|---|---|---|
| **WP0** | Migration/deploy discipline lock: forward-only, `check_deploy_window.py` majburiy, feature flag | Gate-0 | — |
| **WP1** | `Problem.readiness` holat-mashinasi + ref-solution harness + graded gate | 0037 | M1 |
| **WP2** | Verdict taxonomy: `RE_SIGNAL`/`RE_EXIT` split, dead-code hujjati, i18n 10 til | 0037 | M10 |
| **WP3** | `origin` ustuni + backfill + `check_metrics.py` | 0030 | M3 |
| **WP4** | Secrets fail-fast + `security.yml` ON | 0044 | — |
| **WP5** | `check_ai_boundary.py` | 0036 | — |
| **WP6** | `check_architecture.py` | 0042 | — |

**OUT of scope (bu pass'da tegilmaydi):** AI Gateway (0033/0034/0035) · Billing (0041) · 4-host topologiya (0029/M6) · staging (0040) · judge host separation (0029) · event envelope (0031/M4) · object-level authz (0045) · backup/PITR/DR (0043) · monitoring/Sentry (0039) · judge queue semantikasi (0038) · throttle ijrosi (0032 — faqat o'lchov) · `core/views.py` bo'lish (TD16) · Redis rol ajratish (TD23).

### 9.4 Egasi uchun ochiq bandlar

**🔴 BLOCKING (11 ta):** ADR tili · A− guruhi kontseptsiyasi · 3 triage tuzatish · taxonomy scope · migration discipline gate elementi · 0037 chegaralari · 0030 `neytron_*` · 0044 sir menejeri · 0036 modul/servis (Q19) · 0042 grandfathering · 0028 cap_drop yoki userns.

**🟢 NON-BLOCKING:** 0029/0032 qarorlari · M5 o'lchov jadvali · Sentry/GlitchTip (0039) · staging (0040).

---

## ✅ 行动清单

> **Tuzatish (2026-09-29, rev.2):** oldingi versiyada **ADR 0036 va ADR 0042** action ro'yxatidan tushib qolgan edi — holbuki ikkalasi ham §3.1 da **A (kod blokeri)** deb belgilangan. Bu yig'ish xatosi edi va quyida tuzatildi.

### A. Egasi qarorlari — Implementation-Ready Gate'ni bloklaydi

| # | Amal | Mas'ul rol | Shoshilinchlik | Kutilgan natija |
|---|---|---|---|---|
| 1 | **ADR 0037** (content readiness) ni tasdiqlash — ≥5 yashirin test, `legacy_unverified` taqdiri, kim trigger qiladi | Egasi + Archi | **P0** | Kontent gate kontrakti qotadi |
| 2 | **ADR 0030** (data origin) ni tasdiqlash — `neytron_*` taqdiri, `imported` alohida origin'mi | Egasi + Archi | **P0** | North Star hisoblanadigan bo'ladi |
| 3 | **ADR 0044** (secrets) ni tasdiqlash — public overlay hardcode'ni ham qoplashi bilan | Egasi + Archi | **P0** | Prod parol hardcode yopiladi |
| 4 | **ADR 0036** (AI data boundary) ni tasdiqlash — AI Gateway modulmi yoki alohida servis (Q19) | Egasi + Archi | **P0** | `check_ai_boundary.py` kontrakti qotadi |
| 5 | **ADR 0042** (modul chegarasi) ni tasdiqlash — import allowlist + grandfather siyosati | Egasi + Archi | **P0** | `check_architecture.py` kontrakti qotadi |
| 6 | **ADR 0028** (judge privilege) qarori — A− guruhi, ijro Phase 1 | Egasi + Archi + Cody | **P0** | M2 boshlanishi uchun yo'l ochiladi |
| 7 | **A− guruhi va 3 triage tuzatishini tasdiqlash** (§3.1) | Egasi | **P0** | Triage rasman qabul qilinadi |
| 8 | **ADR tili qoidasi** (o'zbek lotin yoki ingliz) | Egasi | **P0** | 0028–0045 uslubi belgilanadi |

### B. Injenerlik amallari — qarorlar yopilgach

| # | Amal | Mas'ul rol | Shoshilinchlik | Kutilgan natija |
|---|---|---|---|---|
| 9 | **`neg_refsolution_gate`** ni `check_negative.py` ga qo'shish | Tessa | **P0** | `print('3 2 1')` regressiyasi abadiy ushlanadi |
| 10 | **Backup shifrlashni off-site'dan OLDIN** qilish | Rex | **P0** | 2026-09-17 PII hodisasi takrorlanmaydi |
| 11 | **`NSJAIL_REF` ni commit-SHA ga qotirish** | Cody | **P1** | "Pinned images" da'vosi haqiqatga aylanadi |

---

## ⚠️ 待完善 / 已知局限

- **Kod yozilmagan** — bu hisobot texnik aniqlashtirish; hech bir ADR fayli yaratilmagan.
- **Yakuniy qarorlar qabul qilinmagan** — 7 ta band egasi tasdig'ini kutadi (yuqorida NEEDS OWNER).
- **UNVERIFIED bandlar**: host cgroup versiyasi, seccomp/AppArmor profili, `.env.public` haqiqiy qiymatlari, `tests/security/run.sh` mavjudligi, author throughput (Q20), Redis cross-host auth/TLS, RAM tomoni limitlari, PITR sozlamasi.
- **Archi vs Cody kelishmovchiligi** rahbar tomonidan A− guruhi kiritish bilan yopildi — lekin bu **yangi taklif**, egasi tasdiqlashi kerak.
- **Blueprint'ning Phase 0 ro'yxatiga 3 tuzatish** kiritildi — bu ham tasdiq talab qiladi.

---

## 📚 数据来源 & 成员产出索引

- **Archi (System Architect)** — ADR triage (18 → A/A−/B/C), 5 ta decision-closure draft, Phase 0 texnik dizayn, ADR yozish tartibi. Manba: blueprint §4, §7, §11, §13, §17.3, §21–26; `apps/api/problems/models.py`, `apps/api/judging/verdicts.py`.
- **Cody (Code Reviewer)** — 13 topilma (8 🔴), FACT/ASSUMPTION ajratmasi. Manba: `docker-compose.yml`, `docker-compose.public.yml`, `services/judge-go/sandbox.go`, `services/judge-go/main.go`, `config/settings.py`, `.github/workflows/security.yml`.
- **Rex (SRE Engineer)** — 6 operability bandi, backup shifrlash tartibi, Telegram alerting dizayni, M1/M2/M10 deploy riski. Manba: `tools/backup.sh`, `.github/workflows/deploy.yml`, `compose/four-host/README.md`, `notifications/tasks.py`.
- **Tessa (Testing Expert)** — test qatlamlari, ref-solution harness, `neg_refsolution_gate`, readiness matritsasi R1–R10, Q20 o'lchovi, CI taqsimoti. Manba: `tools/check_negative.py`, `tools/check_verdict_codes.py`, `tests/`.
- **Docu (Technical Writer)** — ADR shabloni, indekslash formati, 5 runbook konturi, doc-debt jadvali, `check_docs.py` tuzoqlari, til ziddiyati. Manba: `docs/07-adr/`, `tools/check_docs.py`.
- **Zhen (Engineering Director)** — orkestratsiya, jamoa boshqaruvi, ADR 0028 bo'yicha kelishmovchilikni hal qilish, hisobotni birlashtirish.
- **Archi (System Architect, 2-sessiya)** — Implementation-Ready Gate (§9): gate validatsiyasi, 2 bo'shliq, 6 qaror uchun qulflangan acceptance criteria, scope freeze (WP0–WP6). Alohida fayl: `implementation-ready-gate-archi-2026-09-29.md`.

---

## Reviziya tarixi

| Rev | Sana | O'zgarish |
|---|---|---|
| rev.1 | 2026-09-29 | Birinchi yig'ish — 5 mutaxassis natijasi |
| rev.2 | 2026-09-29 | **Action List tuzatildi** (ADR 0036 va 0042 tushib qolgan edi). §9 Implementation-Ready Gate qo'shildi. Core card va TL;DR yangilandi |

---

> 本报告由工程保障团队 AI 协作生成，关键决策请由人类工程负责人复核。
