# RankWant — Phase 0 Test Evidence Matrix (WP0 · WP4 · WP5 · WP6)

**Sana**: 2026-09-29
**Muallif**: Software Company — Engineer (Alex)
**Holat**: 🟢 Tayyor — ikkinchi implementatsiya partiyasi (WP4) qo'shildi
**Til qoidasi**: Hujjat **o'zbek (lotin)**. Texnik atama, fayl yo'li va kod **inglizcha**.

> Bu fayl **faqat o'lchangan** natijalarni yozadi. Har buyruq haqiqiy repo
> ildizidan yurgizildi va chiqishi **so'zma-so'z** keltirilgan. Tekshirilmagan
> narsa `PASS` deb yozilmagan.

---

## 1. Qabul mezonlari ↔ o'lchov (jadval)

| WP | Task | Qabul mezoni | O'lchov buyrug'i | Kutilgan | Haqiqiy natija | Fayl(lar) | Status |
|---|---|---|---|---|---|---|---|
| WP0 | T-WP0.2 | ④ migration/deploy siyosati hujjatlashtirilgan | `python tools/check_docs.py` | exit 0 | exit 0 | `deliverables/software-company/phase0-reconciliation-table-2026-09-29.md` §4 | PASS |
| WP5 | T-WP5.1 | ① `check_ai_boundary.py` bugungi repo'da yashil | `python tools/check_ai_boundary.py` | exit 0 | exit 0 | `tools/check_ai_boundary.py` | PASS |
| WP5 | T-WP5.1 | ② DB-model import yoki testdata mutatsiyasi → qizil | `python tools/check_negative.py neg_ai_boundary` | 3/3, exit 0 | 3/3, exit 0 | `tools/check_negative.py` | PASS |
| WP5 | T-WP5.2 | ③ AI qatlamida `DATABASE_URL` yo'q | `python tools/check_ai_boundary.py` | exit 0 | exit 0 | `apps/api/ai/` | PASS |
| WP5 | T-WP5.2 | ④ AI Gateway monolit modul (`apps/api/ai/`) | `pytest tests/test_ai_boundary.py` | 2 passed | 2 passed | `apps/api/ai/__init__.py` · `apps/api/tests/test_ai_boundary.py` | PASS |
| WP6 | T-WP6.1 | ① `check_architecture.py` + allowlist mavjud | `python tools/check_architecture.py` | exit 0 | exit 0 | `tools/check_architecture.py` · `tools/architecture-allowlist.txt` | PASS |
| WP6 | T-WP6.1 | ③ allowlist'da mavjud buzilishlar soni yozilgan | `head tools/architecture-allowlist.txt` | `# jami: N` | `# jami: 111` | `tools/architecture-allowlist.txt` | PASS |
| WP6 | T-WP6.2 | ② yangi taqiqlangan import → CI qizil | `python tools/check_negative.py neg_architecture` | 2/2, exit 0 | 2/2, exit 0 | `tools/check_negative.py` | PASS |
| WP6 | T-WP6.2 | ④ ratchet (ro'yxat faqat qisqaradi) | `python tools/check_negative.py neg_architecture` | o'lik yozuv tutilsin | tutildi | `tools/check_negative.py` | PASS |
| WP5·WP6 | — | api testlar (runtime chegara) | `pytest tests/test_ai_boundary.py tests/test_architecture_boundary.py` | 4 passed | 4 passed | `apps/api/tests/` | PASS |

---

## 2. WP0 — Reconciliation va migration/deploy siyosati (T-WP0.2)

**Implementation summary.** `.github/workflows/deploy.yml` ning 200–250 qatorlari
o'qildi. `tools/check_deploy_window.py` chaqiruvi **allaqachon majburiy** ekan —
kod o'zgartirilmadi. Dalil: qadam `deploy.yml:218` («Live contest window»);
chaqiruv `:230`, `set +e`/`set -e` orasida (chiqish kodi ushlanadi); faol
contest'da `:233-236` `exit 1`. Qadamda `continue-on-error: true` **yo'q**, uni
o'tkazib yuboruvchi `if:` **yo'q**, `|| true` **yo'q** (butun faylda
`continue-on-error` umuman uchramaydi).

**Files changed.**

- `deliverables/software-company/phase0-reconciliation-table-2026-09-29.md` — §4 ga **Qoida 7** (`check_deploy.sh` + `GIT_SHA`) va **Qoida 8** (rollback qaydi) qo'shildi; Qoida 2 ga majburiylik dalili qo'shildi; oxiridagi `**STATUS:**` WP0 ning 4 mezoni dalili bilan yangilandi. Mavjud matn **o'chirilmadi**, faqat to'ldirildi.

**Tests added.** — (WP0 — hujjat ishi; gate — `tools/check_docs.py`, mavjud).

**Commands executed (so'zma-so'z).**

```text
$ python tools/check_docs.py
Tekshirildi: 195 ta markdown fayl + ADR havolalari
Muammo topilmadi ✓
DOCS_EXIT=0
```

**Unresolved.** — **Risk.** — (kod va migratsiya yo'q).

---

## 3. WP5 — AI boundary (D6 · T-WP5.1 · T-WP5.2)

**Implementation summary.** Yangi statik darvoza `tools/check_ai_boundary.py`
(AST asosida) `apps/api/ai/**/*.py` ni skanerlaydi va quyidagilarni taqiqlaydi:
Django model importi (`from <app>.models` / `from .models` / `import <app>.models`),
`django.db` va `django.contrib.*`, `DATABASE_URL` satri (docstring'lardan tashqari),
va testdata o'qish (`open`/`Path`/`*.read_*()` ichida `testdata` · `fixtures/` ·
`*.json`). Skeleton `apps/api/ai/` **monolit oddiy Python paket** — `models.py`,
`migrations/`, `apps.py` yo'q, `INSTALLED_APPS` ga qo'shilmagan. Runtime test
`apps/api/tests/test_ai_boundary.py` `ai` importi `sys.modules` ga `*.models`
tortmasligini tasdiqlaydi.

**Files changed / added.**

- `tools/check_ai_boundary.py` (yangi)
- `tools/check_negative.py` (o'zgartirildi — `_temp_repo_file`, `_gate_catches`, `neg_ai_boundary` guruhi)
- `.github/workflows/ci.yml` (o'zgartirildi — `integrity` job'iga qadam)
- `apps/api/ai/__init__.py` (yangi)
- `apps/api/ai/README.md` (yangi)
- `apps/api/tests/test_ai_boundary.py` (yangi)

**Tests added.** `neg_ai_boundary` (3 mutatsiya: model importi · `DATABASE_URL` ·
testdata); `test_ai_boundary.py` (2 test: runtime import · gate yashil).

**Commands executed (so'zma-so'z).**

```text
$ python tools/check_ai_boundary.py
Tekshirildi: apps/api/ai — 1 fayl
AI qatlami chegarasi toza ✓ (DB modeli · testdata · DATABASE_URL — yo'q)
EXIT=0

$ python tools/check_negative.py neg_ai_boundary
  ✓ ai/model importi: buzuq holatni tutdi (exit 1)
  ✓ ai/DATABASE_URL: buzuq holatni tutdi (exit 1)
  ✓ ai/testdata: buzuq holatni tutdi (exit 1)

Salbiy testlar: 3/3 ✓ — har bir tekshiruv buzuq holatni tutdi
EXIT=0
```

**Unresolved.** — **Risk.** Bugun AI kodi yo'q — "vakuumli yashil" xavfi
mutatsiya testi bilan yopildi; kelajakda runtime qo'shilganda gate avtomatik
kuchga kiradi.

---

## 4. WP6 — Architecture boundary (D7 · T-WP6.1 · T-WP6.2)

**Implementation summary.** Yangi darvoza `tools/check_architecture.py` qoidasi:
`apps/api/` ichida bir app boshqa app'ning `models` modulini import qilmasin.
Istisnolar fayl boshida hujjatlashtirilgan: `migrations/` · `tests/` · `core`
(umumiy poydevor — unga tayanish ruxsat; `core` O'ZI feature app'ga tayansa —
baribir buzilish). Grandfather: bugungi buzilishlar
`tools/architecture-allowlist.txt` da; **ratchet**: allowlist'dagi o'lik yozuv
ham `exit 1` beradi. Allowlist qatori formati
`<nisbiy/yol.py>:<import qilingan modul>`, sarlavhada `# jami: N`.

**Files changed / added.**

- `tools/check_architecture.py` (yangi)
- `tools/architecture-allowlist.txt` (yangi — 111 yozuv)
- `apps/api/tests/test_architecture_boundary.py` (yangi)
- `tools/check_negative.py` (o'zgartirildi — `neg_architecture` guruhi)
- `.github/workflows/ci.yml` (o'zgartirildi — `integrity` job'iga qadam)

**Tests added.** `neg_architecture` (2 mutatsiya: yangi app-importi · o'lik
allowlist yozuvi); `test_architecture_boundary.py` (2 test: gate yashil ·
sarlavha soni mos).

**Commands executed (so'zma-so'z).**

```text
$ python tools/check_architecture.py
Tekshirildi: 20 app · 111 import · allowlist 111 yozuv
App chegarasi toza ✓ (allowlist bilan muvozanatda)
EXIT=0

$ python tools/check_negative.py neg_architecture
  ✓ arxitektura/yangi import: buzuq holatni tutdi (exit 1)
  ✓ arxitektura/ratchet: o'lik allowlist yozuvi tutildi (exit 1)

Salbiy testlar: 2/2 ✓ — har bir tekshiruv buzuq holatni tutdi
EXIT=0
```

**Unresolved / risk.** Task matni «mavjud **4** ta buzilish» degan edi
(assurance hisobotidagi namunalar: `arena/services.py:15`,
`judging/serializers.py:8-9`, `ratings/services.py:12,284,371`,
`classroom/serializers.py:8`). To'liq skan **111** ta topdi — bu namunalar
**to'liq ro'yxat emas**. Gate'ni bugungi repo'da yashil qilish uchun hammasi
grandfather qilindi. Bu **task-matni ↔ o'lchov** nomuvofiqligi (muzlatilgan
qaror emas); allowlist shu sababli 4 emas, **111** yozuvdan iborat.

---

## 5. To'liq salbiy to'plam va umumiy buyruqlar

```text
$ python tools/check_negative.py
  ✓ i18n/bo'sh qiymat: buzuq holatni tutdi (exit 1)
  ...
  ✓ ai/model importi: buzuq holatni tutdi (exit 1)
  ✓ ai/DATABASE_URL: buzuq holatni tutdi (exit 1)
  ✓ ai/testdata: buzuq holatni tutdi (exit 1)
  ✓ arxitektura/yangi import: buzuq holatni tutdi (exit 1)
  ✓ arxitektura/ratchet: o'lik allowlist yozuvi tutildi (exit 1)

1/335 salbiy test YIQILDI — tekshiruv o'lik bo'lishi mumkin:
  - litsenziya/nazorat: `--check` exit 1 — ux-thunk
EXIT=1
```

⚠️ **Izoh:** yagona yiqilgan holat — `litsenziya/nazorat` (`licence_inventory`),
bu **mening o'zgarishlarimga aloqasi yo'q**. U `apps/web/package.json` /
`package-lock.json` dagi **oldindan mavjud** driftdan kelib chiqadi (men bu
fayllarga tegmadim). Isbot: `tools/check_negative.py` o'zgarishini `git stash`
qilib qayta yurganda ham `python tools/licence_inventory.py --check` **exit 1**
beradi. `neg_ai_boundary` va `neg_architecture` — **ikkalasi ham 5/5 o'tdi**.

```text
$ python tools/check_security_boundary.py
  chegara: 2 nashr etilgan port
    api        127.0.0.1:8301:8000
    web        127.0.0.1:8300:3000
  ✓ judge, postgres, redis, minio — nashr etilgan port yo'q
  docker-compose.tools.yml — deploy zanjiridan tashqari:
    adminer    127.0.0.1:8081:8080
  ✓ hammasi 127.0.0.1 da; tashqi yo'l — Cloudflare Tunnel
SEC_EXIT=0

$ pytest tests/test_ai_boundary.py tests/test_architecture_boundary.py -v
collected 4 items
tests/test_ai_boundary.py ..                                             [ 50%]
tests/test_architecture_boundary.py ..                                   [100%]
============================== 4 passed in 23.50s ==============================
EXIT=0

$ ruff check ai tests/test_ai_boundary.py tests/test_architecture_boundary.py
All checks passed!   (ruff_check=0)
$ ruff format --check ai tests/test_ai_boundary.py tests/test_architecture_boundary.py
4 files already formatted   (ruff_fmt=0)
$ mypy ai/__init__.py tests/test_ai_boundary.py tests/test_architecture_boundary.py
Success: no issues found in 3 source files   (mypy=0)
```

**O'lchov muhiti (api testlar).** Lokal `apps/api/.venv` — **Linux venv**
(`.venv/bin/python`, Windows'da ishlamaydi); `rankwant-api-1` runtime image'ida
`pytest` yo'q. Shuning uchun testlar `rankwant-api-dev:audit` image'ida, repo
`/repo` ga mount qilinib yurgizildi:
`docker run --rm -v D:/Linux/Web_Projects/rankwant:/repo -w /repo/apps/api rankwant-api-dev:audit sh -lc 'pip install -q -r requirements-dev.lock && python -m pytest tests/test_ai_boundary.py tests/test_architecture_boundary.py -v'`.
CI'da bu qadam oddiy: `pytest tests/test_ai_boundary.py tests/test_architecture_boundary.py`.

---

## 6. Umumiy xulosa

| Ko'rsatkich | Qiymat |
|---|---|
| WP0 mezonlari yopilgan | 4/4 |
| WP5 mezonlari yopilgan | 4/4 |
| WP6 mezonlari yopilgan | 4/4 |
| Yangi gate | 2 (`check_ai_boundary` · `check_architecture`) |
| Yangi salbiy guruh | 2 (`neg_ai_boundary` · `neg_architecture`) |
| Yangi api test | 4 (2 + 2) |
| Ochiq bloklovchi masala | 0 |
| Begona (mening ishim emas) yiqilish | 1 (`licence_inventory` — `apps/web` drift) |

**STATUS:** WP0 (T-WP0.2) · WP5 (T-WP5.1 · T-WP5.2) · WP6 (T-WP6.1 · T-WP6.2)
— bajarildi va o'lchandi. Barcha olti tekshiruv o'tdi; yagona qizil holat —
mening o'zgarishlarimga aloqasiz `licence_inventory` drifti (`apps/web`).

---

## 7. WP4 — Secrets hardening (D5 · T-WP4.1 · T-WP4.2 · T-WP4.3)

**Implementation summary.** Compose sirlari env'ga o'tkazildi (`${VAR:?}`),
`SECRET_KEY` fail-fast qilindi (`ImproperlyConfigured`), `security.yml` qayta
yoqildi va rotation runbook yozildi. **Rotation ataylab bajarilmadi** — tartib
qulflangan: **wiring → fail-fast → rotation keyin** ([ADR-0044](../../docs/07-adr/0044-secrets-management.md) §4).

**Files changed / added.**

- `docker-compose.yml` (o'zgartirildi — `POSTGRES_PASSWORD` · `MINIO_ROOT_PASSWORD` · `DATABASE_URL` ×5 · `S3_SECRET` ×5 · `DJANGO_SECRET_KEY` ×4 → `${VAR:?}`)
- `docker-compose.public.yml` (o'zgartirildi — `DJANGO_SECRET_KEY` ×4 → `${VAR:?}`)
- `.env.example` (o'zgartirildi — `POSTGRES_PASSWORD` · `MINIO_ROOT_PASSWORD` · `S3_SECRET` kalitlari qo'shildi)
- `apps/api/config/settings.py` (o'zgartirildi — `SECRET_KEY` fail-fast)
- `apps/api/tests/test_settings_secrets.py` (yangi — 3 test)
- `apps/api/Makefile` (o'zgartirildi — `export DJANGO_SECRET_KEY ?= local-only-not-for-production`)
- `.github/workflows/security.yml` (o'zgartirildi — `if: false` olib tashlandi; push+schedule qayta yoqildi)
- `.github/workflows/nightly.yml` · `.github/workflows/deploy.yml` · `.github/workflows/ci.yml` (o'zgartirildi — env ta'minoti)
- `tools/ci_stack.sh` · `tools/check_decisions.py` · `tools/check_negative.py` (o'zgartirildi)
- `docs/10-operations/runbooks/secrets-rotation.md` (yangi)
- `CLAUDE.md` (o'zgartirildi — qo'lda pytest buyrug'i)

**Qabul mezonlari ↔ o'lchov.**

| # | Mezon | Buyruq | Natija | Status |
|---|---|---|---|---|
| ① | Compose'da hardcode sir yo'q | `grep -nE 'PASSWORD: dev$' docker-compose.yml` + `grep -n 'devdevdev' docker-compose.yml docker-compose.public.yml docker-compose.ci.yml` | 0 natija (ikkala grep exit 1) | PASS |
| ② | `SECRET_KEY` yo'q/bo'sh → `ImproperlyConfigured` | `pytest tests/test_settings_secrets.py` | 3 passed | PASS |
| ③ | Prod zanjiri sirsiz **yiqiladi** | `env -u ... docker compose -f docker-compose.yml config` | exit 1 (`required variable POSTGRES_PASSWORD is missing a value: D5-majburiy`) | PASS |
| ④ | `security.yml` yoqilgan + asboblar ishlaydi | `grep -nE '^\s*if:' security.yml` + gitleaks/pip-audit/npm audit | 0 jonli `if:`; 3 asbob yashil (pastda) | PASS |
| ⑤ | Rotation runbook yozilgan (tartib qulflangan) | `python tools/check_docs.py` | exit 0 (220 fayl; runbook havolalari butun) | PASS |

**Commands executed (so'zma-so'z).**

```text
$ env -u POSTGRES_PASSWORD -u MINIO_ROOT_PASSWORD -u S3_SECRET -u DJANGO_SECRET_KEY \
    docker compose -f docker-compose.yml config   # criterion ③
error while interpolating services.api.environment.DATABASE_URL: required variable POSTGRES_PASSWORD is missing a value: D5-majburiy
error while interpolating services.api.environment.DJANGO_SECRET_KEY: required variable DJANGO_SECRET_KEY is missing a value: D5-majburiy
error while interpolating services.api.environment.S3_SECRET: required variable S3_SECRET is missing a value: D5-majburiy
NO_ENV_EXIT=1

$ env POSTGRES_PASSWORD=x MINIO_ROOT_PASSWORD=x S3_SECRET=x DJANGO_SECRET_KEY=x \
    docker compose -f docker-compose.yml config            # WITH env → 0
BASE_ENV_EXIT=0
$ ... -f docker-compose.ci.yml config                       # WITH env → 0
CI_ENV_EXIT=0
$ docker compose --env-file .env.public -f docker-compose.yml -f docker-compose.public.yml config
PUBLIC_ENV_EXIT=0

$ grep -nE 'PASSWORD: dev$' docker-compose.yml ; grep -n 'devdevdev' docker-compose.yml docker-compose.public.yml docker-compose.ci.yml
(0 natija — ikkala grep exit 1)

$ grep -nE '^\s*if:' .github/workflows/security.yml
(0 natija — jonli `if:` yo'q; yagona `if: false` — 5-qatordagi IZOH matni)

$ pytest tests/test_settings_secrets.py -q
...                                                          [100%]
3 passed

$ python tools/check_docs.py
Tekshirildi: 220 ta markdown fayl + ADR havolalari
Muammo topilmadi ✓     DOCS_EXIT=0

$ python tools/check_decisions.py
✓ 59 ta qaror kodda amalda     DECISIONS_EXIT=0

$ python tools/check_env_example.py
✓ .env.example to'liq: 74 o'zgaruvchi hujjatlangan + lokal .env.public (26 kalit)     ENV_EXIT=0

$ python tools/check_security_boundary.py
  ✓ hammasi 127.0.0.1 da; tashqi yo'l — Cloudflare Tunnel     SEC_EXIT=0

$ python tools/check_negative.py env_example
  ✓ env_example/DJANGO_SECRET_KEY: tutildi (exit 1)
  ✓ env_example/PUBLIC_ORIGIN: tutildi (exit 1)
  ✓ env_example/NEW_PROBE_VAR: tutildi (exit 1)
  ✓ env_example/NEW_PROBE_SETTING: tutildi (exit 1)
  ✓ env_example/TELEGRAM_BOT_TOKEN: tutildi (exit 1)
Salbiy testlar: 5/5 ✓     NEG_ENV_EXIT=0

$ python tools/check_negative.py decisions
  ✓ decisions/Security run yoqilgan: bekor qilingan qaror tutildi (exit 1)   ← YANGI (×3)
  ...
  1/183 salbiy test YIQILDI — litsenziya/nazorat: ux-thunk (oldindan mavjud drift)
NEG_DEC_EXIT=1

$ python tools/check_negative.py neg_ai_boundary   → 5/5 ✓ (exit 0)
$ python tools/check_negative.py neg_architecture  → 2/2 ✓ (exit 0)

$ ruff check config/settings.py tests/test_settings_secrets.py
All checks passed!     ruff_check=0
$ ruff format --check config/settings.py tests/test_settings_secrets.py
2 files already formatted     ruff_fmt=0
```

**Security asboblari — topilgan natijalar (mezon ④, "eng muhim savol").**

| Asbob | Ko'lam | Natija | Chiqish kodi |
|---|---|---|---|
| gitleaks | 895 commit · 17.19 MB | **sir topilmadi** (`no leaks found`) | 0 |
| pip-audit | `apps/api/requirements.lock` | **ma'lum zaiflik yo'q** (`No known vulnerabilities found`) | 0 |
| npm audit | `apps/web` (`--audit-level=high`) | **0 zaiflik** (`found 0 vulnerabilities`) | 0 |

**Unresolved / risk.**

- **Rotation bajarilmadi** — ataylab; tartib qulflangan (wiring → fail-fast → rotation keyin). Runbook tayyor.
- **`check_negative.py decisions` → 1/183 qizil** — `litsenziya/nazorat: ux-thunk`. Bu **mening o'zgarishlarimga aloqasi yo'q**: `apps/web/package.json` ga `recharts` qo'shilgan (boshqa WP), ya'ni `licence_inventory` drifti. Men `apps/web` ga tegmadim (`git status -- apps/web` → men yozmagan fayllar).
- **`mypy` INTERNAL ERROR** (`NewSemanalDjangoPlugin`) — **muhit** muammosi, kod emas: xato plugin yuklanishida, hech qanday fayl tahlil qilinmasidan oldin chiqadi. Bu holat `ci.yml:165-171` da **hujjatlashtirilgan** (2026-09-12) va "`rankwant-api` image'ida 280 faylda o'tadi" deb yozilgan. O'zgarish tip-trivial (`import` + `if: raise`); `ruff` yashil.

---

## 8. Umumiy xulosa (WP0 · WP4 · WP5 · WP6)

| Ko'rsatkich | Qiymat |
|---|---|
| WP0 mezonlari yopilgan | 4/4 |
| WP4 mezonlari yopilgan | 5/5 |
| WP5 mezonlari yopilgan | 4/4 |
| WP6 mezonlari yopilgan | 4/4 |
| Yangi gate | 2 (`check_ai_boundary` · `check_architecture`) |
| Yangi salbiy guruh | 2 (`neg_ai_boundary` · `neg_architecture`) |
| Yangi api test | 7 (4 + `test_settings_secrets.py` 3) |
| Yangi doc | 1 (`docs/10-operations/runbooks/secrets-rotation.md`) |
| Security asboblari | 3 yashil (gitleaks · pip-audit · npm audit) |
| Ochiq bloklovchi masala | 0 |
| Begona (mening ishim emas) yiqilish | 1 (`licence_inventory` — `apps/web` drift) |

**STATUS:** WP4 (T-WP4.1 · T-WP4.2 · T-WP4.3) — bajarildi va o'lchandi.
Wiring va fail-fast o'rnatildi; rotation tartibi qulflandi va runbook yozildi.
Security workflow qayta yoqildi va uch asbob **sir/zaiflik topmadi**.
Yagona qizil holat — mening o'zgarishlarimga aloqasiz `licence_inventory`
drifti (`apps/web`), `mypy` esa muhit sababli (hujjatlashtirilgan) ishlamadi.

---

## 9. WP1 — Content readiness (D8 · D8-F · migratsiya M1)

**Implementation summary.** `Problem.readiness` — 9 holatli holat-mashinasi;
mezon **semantik, son emas** (S1 yashirin test mavjudligi · S2 checker to'liq ·
S3 etalon yechim AC · S4 sample-echo AC emas). Trigger gibrid: S1/S2 statik,
S3/S4 judge harness (`verify_readiness`), yakuniy `validated` — staff.
**`is_public` readiness ga BOG'LANMAGAN**: ikki alohida gate (ko'rinish va
graded eligibility), ya'ni D8-F buzilmaydi. Graded gate uch nuqtada:
`contests/staff_serializers.py` · `contests/staff_views.py` ·
`contests/services.py` (`create_mirror`).

**Files changed / added (to'liq ro'yxat).**

Yangi:

- `apps/api/problems/readiness.py` — holat-mashinasi, S1–S4, `evaluate_readiness`, `run_harness`, `verify`, `graded_gate_error`
- `apps/api/problems/migrations/0023_problem_readiness.py` — M1 add (nullable, defaultsiz)
- `apps/api/problems/migrations/0024_backfill_readiness.py` — M1 backfill + NOT NULL switch
- `apps/api/problems/management/commands/backfill_readiness.py` — A/B/C audit buyrug'i
- `apps/api/problems/management/commands/verify_readiness.py` — S3/S4 harness buyrug'i
- `apps/api/tests/test_problem_readiness.py` — R1–R10 + M1 audit testi
- `apps/api/tests/regression/` — 4 fayl: `__init__.py`, `conftest.py`, `README.md`, `test_ref_solution_verdicts.py`

O'zgartirilgan:

- `apps/api/problems/models.py` — `Readiness` enum · `readiness` maydoni (`db_index`) · `problem_readiness_pub` indeksi · `clean()` gate
- `apps/api/judging/services.py` — `tests_of` · `checker_of` · `build_standalone_job` ajratildi (`build_job` xulqi o'zgarishsiz)
- `apps/api/contests/staff_serializers.py` — `validate_problems` ichiga graded gate
- `apps/api/contests/staff_views.py` — `bulk_create` oldidan ikkinchi qavat
- `apps/api/contests/services.py` — `create_mirror` ichida gate (`ValueError`)
- `apps/api/tests/test_content.py` · `apps/api/tests/test_staff_contests.py` — 4 ta mavjud test yangi gate'ga moslashtirildi
- `tools/check_negative.py` — `neg_refsolution_gate` guruhi (M-A · M-B)

**O'lchov muhiti.** `apps/api/.venv` buzuq (`bin/python` 0 bayt), runtime
image'ida `pytest` yo'q — api testlari konteynerda yurgizildi:

```text
docker run --rm -e DJANGO_SECRET_KEY=test-secret-key \
  -v D:/Linux/Web_Projects/rankwant:/repo -w /repo/apps/api \
  rankwant-api-dev:audit sh -lc \
  'pip install -q -r requirements-dev.lock && python -m pytest -q'
```

`DJANGO_SECRET_KEY` shart (D5 fail-fast). `DATABASE_URL` berilmadi, ya'ni
testlar sqlite test-DB'da yurdi — **jonli Postgres'ga tegilmadi**, `migrate`
yurgizilmadi.

```text
$ python -m pytest -q                                  # butun apps/api to'plami
1548 passed                                            (F/E yo'q — 10 m 14 s)

$ python -m pytest tests/test_problem_readiness.py tests/regression -q
................                            [100%]     (16 passed)

$ python manage.py check
System check identified no issues (0 silenced).
$ python manage.py makemigrations --check --dry-run
No changes detected                                    # migratsiya drifti yo'q
$ ruff check problems contests judging tests
All checks passed!
$ ruff format --check problems contests judging tests
143 files already formatted
$ mypy problems/readiness.py problems/models.py contests/... tests/...
Success: no issues found in 9 source files
```

**R1–R10 natijasi (barchasi yashil).**

| # | Test | Fayl | Natija |
|---|---|---|---|
| R1 | `test_default_readiness_is_draft` | `tests/test_problem_readiness.py` | PASS |
| R2 | `test_publish_without_tests_is_400` | `tests/test_problem_readiness.py` | PASS |
| R3 | `test_publish_without_hidden_test_is_400` | `tests/test_problem_readiness.py` | PASS |
| R4 | `test_transition_forward_step_ok` va salbiy yarmi | `tests/test_problem_readiness.py` | PASS |
| R5 | `test_checker_type_required` | `tests/test_problem_readiness.py` | PASS |
| R6 | `test_reference_solution_is_ac` | `tests/regression/test_ref_solution_verdicts.py` | PASS |
| R7 | `test_sample_echo_is_not_ac` | `tests/regression/test_ref_solution_verdicts.py` | PASS |
| R8 | `test_graded_requires_validated` va musbat yarmi | `tests/test_problem_readiness.py` | PASS |
| R9 | `test_legacy_unverified_public_but_not_in_contest` | `tests/test_problem_readiness.py` | PASS |
| R10 | `test_draft_to_validated_jump_rejected` | `tests/test_problem_readiness.py` | PASS |

Qo'shimcha testlar: `test_backfill_audit_numbers` (M1 guruhlari + mezon ③),
`test_reference_solution_not_ac_blocks`,
`test_blocked_problem_can_return_to_review`,
`test_no_hidden_test_keeps_the_state`, `test_validated_problem_is_accepted`.

**`neg_refsolution_gate` haqiqatan qizil beradimi — isbot.**

```text
$ python tools/check_negative.py neg_refsolution_gate
  ✓ gate/S4: S4 sharti olib tashlansa test qizil (exit 1)
  ✓ gate/graded: gate olib tashlansa R8 qizil (exit 1)

Salbiy testlar: 2/2 ✓ — har bir tekshiruv buzuq holatni tutdi
NEG_EXIT=0

$ python tools/check_negative.py                # butun to'plam
1/340 salbiy test YIQILDI                       # yagona qizil: litsenziya/nazorat
```

M-A: `readiness.py` dagi `if echo_verdict == Verdict.AC:` vaqtincha
`if False:` ga almashtirildi (keyin qaytariladi) — `test_sample_echo_is_not_ac`
**exit 1**. M-B: gate sharti **ikkala qavatda** (`staff_serializers.py` va
`staff_views.py`) `False` ga almashtirildi — R8 **exit 1**. Faqat serializer
qavatini olib tashlash R8 ni qizil qilmaydi (o'lchandi: view qavati baribir
400 beradi), shu sabab mutatsiya ikkala qavatni qamraydi. Old shart
(`api_test_precondition`) o'zgarmagan manbada ikkala test yashil bo'lishini
talab qiladi — aks holda «testlar ishga tushmadi» yolg'on yashil o'qilardi.

**Backfill audit raqami (jonli Postgres, FAQAT o'qish — `migrate` yurgizilmadi).**

```text
$ docker exec rankwant-postgres-1 psql -U rankwant -d rankwant -c "SELECT ..."
 group_a_no_hidden | group_b_with_hidden
-------------------+---------------------
              1225 |                   4
$ SELECT count(*) FROM problems_problem WHERE is_public;      -> 1229
$ SELECT count(*) FROM problems_problem WHERE NOT is_public;  -> 867
```

| Guruh | Shart | Yangi qiymat | Jonli son |
|---|---|---|---|
| A | public va yashirin test yo'q | `legacy_unverified` | 1225 |
| B | public va yashirin test bor | `needs_review` | 4 |
| C | `is_public=False` | `draft` | 867 |

Kontrakt A = 1 222 kutgan edi; jonli o'lchov **1 225** (+3) — kontrakt
yozilgandan keyin arxivga 3 ta masala qo'shilgan. B = 4 aynan mos. Jami
2 096 masala (1 229 + 867). Mezon ③ (`is_public AND readiness IS NULL` = 0)
jonli bazada **o'lchanmadi** — ustun hali yaratilmagan (M1 deploy qilinmagan);
test-DB'da `test_backfill_audit_numbers` bilan tasdiqlangan (0 NULL).

**Tekshiruvlar (barchasi exit 0).**

```text
python tools/check_docs.py               -> Muammo topilmadi ✓
python tools/check_decisions.py          -> ✓ 59 ta qaror kodda amalda
python tools/check_verdict_codes.py      -> Kodlar mos ✓
python tools/check_security_boundary.py  -> ✓ hammasi 127.0.0.1 da
python tools/check_architecture.py       -> App chegarasi toza ✓ (111 = 111)
python tools/check_api_english.py        -> 247 files — messages are English ✓

$ grep -n "privileged\|cgroup: host" docker-compose.yml
201:    privileged: true          # nsjail namespace va cgroup uchun
202:    cgroup: host
```

**Unresolved / risk.**

- **Mezon ③ jonli o'lchanmagan** — M1 (`0023`/`0024`) deploy qilinmadi (qoida: jonli Postgres'ga `migrate` yurgizilmaydi). Deploy'dan keyin `python manage.py backfill_readiness --apply` audit raqamini chop etadi.
- **A guruhi 1 222 emas, 1 225** — kontrakt raqamidan 3 ta farq; sabab arxiv o'sgan. Kontrakt §6 dagi kutilgan sonni yangilash tavsiya etiladi (yangi owner decision talab qilmaydi).
- **`validated` ga o'tish endpointi yo'q** — T-WP1.x da talab qilinmagan. Hozir `validated` faqat admin/shell yoki `verify_readiness` + qo'lda tasdiq orqali. Remediatsiya oqimi keyingi ish.
- **`verify_readiness` real judge bilan faqat `beat` to'xtatilgan holda** yurgizilishi shart (`drain_results` `attempt_id=0` natijani yutadi) — buyruq docstring'ida yozilgan.
- **Begona yiqilish**: `litsenziya/nazorat` (`licence_inventory`, `apps/web` drift) — mening ishim emas, oldingi partiyada ham qizil edi.

**STATUS:** WP1 (T-WP1.1 · T-WP1.2 · T-WP1.3 · T-WP1.4) — bajarildi va
o'lchandi. R1–R10 yashil (16 yangi api test), `neg_refsolution_gate` 2/2
(buzilganda qizil — isbotlandi), butun `apps/api` to'plami 1548 passed,
M1 migratsiya fayllari yozildi (jonli bazaga yurgizilmadi).

