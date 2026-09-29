# RankWant — QA Verification (Batch 1: WP0 · WP5 · WP6)

**Sana**: 2026-09-29
**Muallif**: Software Company — QA Engineer (Edward)
**Rol**: Mustaqil, adversarial tekshiruv (Engineer'ning o'z-o'zini tasdiqlashi qabul qilinmadi)
**Tekshirilgan partiya**: WP0 (yakuni) · WP5 (AI boundary) · WP6 (architecture boundary)
**Muhit**: Windows + Git Bash; `python` = WorkBuddy Python 3.13.12; `pytest` = Windows Python 3.12.10 (Linux `.venv` Windows'da ishlamaydi — pastda)
**Repo holati**: `main` · HEAD `462e327` (o'zgarmagan) · hech qanday commit qilinmadi

> Bu fayl faqat **o'lchangan** natijalarni yozadi. Har da'vo ostida yurgizilgan buyruq va uning chiqishi bor. O'lchovsiz "yaxshi" xulosasi yo'q.

---

## 1. Tekshirilgan da'volar jadvali

| # | Da'vo | Tekshiruv buyrug'i | Kutilgan | Haqiqiy | Hukm |
|---|---|---|---|---|---|
| A1 | `check_ai_boundary.py` yashil | `python tools/check_ai_boundary.py` | exit 0 | exit 0 (1 fayl) | PASS |
| A2 | AI gate model importini tutadi | 6 mutatsiya `apps/api/ai/__init__.py` ga | exit 1 | 6/6 exit 1 | PASS |
| A3 | AI gate `DATABASE_URL` ni tutadi | mutatsiya `os.environ.get("DATABASE_URL")` | exit 1 | exit 1 | PASS |
| A4 | AI gate testdata o'qishni tutadi | mutatsiya `open("testdata/x.json")` va `Path("fixtures/a.json").read_text()` | exit 1 | ikkalasi exit 1 | PASS |
| A5 | `check_architecture.py` yashil | `python tools/check_architecture.py` | exit 0 | exit 0 (20 app, 111 import) | PASS |
| A6 | Ratchet: yangi import | `blog/views.py` ga `from judging.models import Attempt` | exit 1 | exit 1 ("YANGI buzilish") | PASS |
| A7 | Ratchet: o'chirilgan yozuv | allowlist'dan mavjud yozuvni olib tashlash | exit 1 | exit 1 (stale/new) | PASS |
| A8 | Ratchet: o'lik yozuv | allowlist'ga yo'q import qo'shish | exit 1 | exit 1 ("MAVJUD EMAS") | PASS |
| A9 | Allowlist soni 111 | mustaqil AST qayta sanash | 111 | 111 (to'plamlar aynan teng) | PASS |
| B1 | To'liq salbiy to'plam | `python tools/check_negative.py` | exit 1, faqat licence | exit 1; 335 test, 1 qizil = licence | PASS |
| B2 | `neg_ai_boundary` qizil beradi | `python tools/check_negative.py neg_ai_boundary` | 3/3, exit 0 | 3/3, exit 0 | PASS |
| B3 | `neg_architecture` qizil beradi | `python tools/check_negative.py neg_architecture` | 2/2, exit 0 | 2/2, exit 0 | PASS |
| B4 | `check_docs.py` yashil | `python tools/check_docs.py` | exit 0 | exit 0 (196 fayl) | PASS |
| B5 | `check_security_boundary.py` yashil | `python tools/check_security_boundary.py` | exit 0 | exit 0 | PASS |
| B6 | api testlar | `pytest tests/test_ai_boundary.py tests/test_architecture_boundary.py` | 4 passed | 4 passed | PASS |
| C1 | `deploy.yml` chaqiruvi majburiy | `deploy.yml` 216-240 qatorlar | majburiy | majburiy (quyida) | PASS |
| C2 | `deploy.yml` o'zgarmagan | `git diff HEAD -- .github/workflows/deploy.yml` | bo'sh | bo'sh | PASS |
| C3 | Reconciliation §4 siyosati | `phase0-reconciliation-table` §4 | 5 element | 5/5 bor | PASS |
| C4 | Reconciliation qatorlari | jadval §2 | qaror to'ldirilgan | 10/10 to'ldirilgan | PASS |
| C5 | `docker-compose.yml` o'zgarmagan | `git diff HEAD -- docker-compose.yml` | bo'sh | bo'sh | PASS |
| C6 | Migratsiya yaratilmagan | `git status` da `migrations/` yo'q | yo'q | yo'q | PASS |
| C7 | `ai/` da Django skeleti yo'q | `ls apps/api/ai/` · `grep ai settings.py` | yo'q | faqat `README.md`, `__init__.py` | PASS |
| C8 | AI runtime kodi yo'q | `apps/api/ai/` ko'zdan kechirish | yo'q | yo'q (LLM/provider/prompt/endpoint yo'q) | PASS |
| C9 | Yangi commit yo'q | `git log --oneline -1` | `462e327` | `462e327` | PASS |
| D1 | Guruh nomi uslubi | `CASES` registri | mos | 30 guruh `neg_`siz, 2 yangi `neg_`li | 🟡 |

**Jami**: 25 da'vo — 24 PASS, 1 🟡 (kosmetik, bloklamaydi). Bloklovchi qizil yo'q.

---

## 2. Topilmalar (jiddiylik bo'yicha)

| # | Jiddiylik | Topilma | Tavsiya |
|---|---|---|---|
| F1 | 🟡 | `check_ai_boundary.py` `from <app> import models` va `from . import models` ko'rinishidagi importni **o'tkazib yuboradi** (exit 0). `_is_model_import` faqat `module == "models"` yoki `module.endswith(".models")` ni tekshiradi; `ImportFrom` da `node.module` `None`/`problems` bo'ladi, import qilingan nom (`models`) esa tekshirilmaydi. `from problems import models` — bu `problems.models` ni HAQIQATAN yuklaydi (DB sxemasiga bog'laydi). | `tools/check_ai_boundary.py` `ImportFrom` shoxobchasiga qo'shimcha: `level > 0` bo'lsa yoki `node.module` app bo'lsa — `alias.name == "models"` ni ham tutish. Bu **bloklovchi emas**: bugun AI kodi yo'q, gate bugungi repo'da yashil. |
| F2 | 🟡 | Guruh nomlanishi nomuvofiq: mavjud 30 guruh `neg_` prefiksisiz (`deploy_window`, `after_reboot`, `runner_report`), yangi 2 guruh esa `neg_ai_boundary` / `neg_architecture`. | Kelajakda `ai_boundary` / `architecture` ga o'tkazish (registr `CASES` da nom o'zgartirilsa bo'ldi — funksiya nomlari `neg_` li qolsa ham bo'ladi). **Funktsiyaga ta'sir yo'q**: registr to'g'ri ulangan, guruh yakka chaqirilganda ishlaydi. |
| F3 | 🟡 | `litsenziya/nazorat` (licence_inventory) yagona qizil. Sabab — `apps/web/package.json` + `package-lock.json` dagi **oldindan mavjud** drift (recharts va uning bog'liqliklari). Bu **Engineer ishi emas** (quyida isbotlangan). | Engineer'ga emas — `apps/web` egasiga. Yangi bog'liqlik `packages.tsv` ga qo'shilishi kerak. |

**Jiddiylik izohi**: 🔴 (bloklovchi) topilma yo'q. 🟠 (o'rtacha) yo'q. Faqat 🟡 (kosmetik / kelajakdagi mustahkamlash).

---

## 3. WP0 / WP5 / WP6 mezon holati

| WP | Mezon | Holat | Dalil |
|---|---|---|---|
| WP0 | ① Reconciliation artefakti mavjud | PASS | `deliverables/software-company/phase0-reconciliation-table-2026-09-29.md` mavjud; `check_docs.py` exit 0 |
| WP0 | ② Har nomuvofiqlik uchun qaror | PASS | §2 jadvali 10 qator; "Yozilgan qaror" va "Qaror manbasi" ustunlari 10/10 to'ldirilgan |
| WP0 | ③ §24 tie-break qoidasi | PASS | §1 «Tie-break qoidasi (D2)» — 4 qadam (mezon → owner qarori → §24 → blueprint) |
| WP0 | ④ Migration/deploy siyosati | PASS | §4: forward-only · deploy-oldi dump · contest oynasida deploy yo'q · `check_deploy_window.py` majburiy · rollback qaydi — 5/5 |
| WP0 | O'lchov: `check_deploy_window` deploy'da majburiy | PASS | `deploy.yml:218` qadam, `:230` chaqiruv; `continue-on-error` yo'q, step `if:` yo'q, shu qadamda or-true yo'q |
| WP5 | Gate mavjud + yashil | PASS | `tools/check_ai_boundary.py` exit 0 |
| WP5 | Mutatsiya → qizil (o'lik emas) | PASS | 6/6 mutatsiya exit 1 (mustaqil yasaldi); `neg_ai_boundary` 3/3 |
| WP5 | `DATABASE_URL` yo'q | PASS | mutatsiya exit 1; joriy kod toza |
| WP5 | Monolit modul (Django app emas) | PASS | `apps/api/ai/` da `models.py`/`migrations/`/`apps.py` yo'q; `settings.py` `INSTALLED_APPS` da `ai` yo'q |
| WP5 | Runtime test | PASS | `pytest tests/test_ai_boundary.py` 2 passed |
| WP6 | Gate + allowlist mavjud | PASS | `tools/check_architecture.py` + `tools/architecture-allowlist.txt` |
| WP6 | Gate yashil | PASS | exit 0; 20 app · 111 import · allowlist 111 |
| WP6 | Yangi import → qizil | PASS | `blog/views.py` mutatsiyasi exit 1; `neg_architecture` 2/2 |
| WP6 | Ratchet (faqat qisqaradi) | PASS | o'lik yozuv exit 1; o'chirilgan yozuv exit 1; mustaqil sanash = 111 |

**Umumiy**: WP0 PASS · WP5 PASS (🟡 mustahkamlash tavsiyasi bilan) · WP6 PASS.

---

## 4. Muhim dalillar (so'zma-so'z)

**A2/A3/A4 — mustaqil mutatsiya** (Engineer'ning salbiy testiga tayanilmadi; har safar `__init__.py` asl holatiga qaytarildi):

```text
PASS | exit=1 | model_import_from_app   | 'from problems.models import Problem'
PASS | exit=1 | model_import_module     | 'import problems.models'
PASS | exit=1 | model_import_relative   | 'from .models import X'
PASS | exit=1 | database_url_env        | os.environ.get("DATABASE_URL")
PASS | exit=1 | testdata_open           | 'open("testdata/x.json")'
PASS | exit=1 | testdata_path_read_text | Path("fixtures/a.json").read_text()
PASS | exit=1 | django_db_import        | 'from django.db import connection'
PASS | exit=1 | import_django_contrib   | 'import django.contrib.auth.models'
PASS | exit=1 | model_import_alias      | 'import problems.models as pm'
MISS | exit=0 | from_app_import_models  | 'from problems import models'   <-- F1
RESTORED_EXACT=True
```

```text
MISS | exit=0 | from_import_models_relative | 'from . import models'      <-- F1
restored bytes identical: True  has_cr: False
```

**A6/A7/A8/A9 — ratchet va mustaqil sanash**:

```text
(a) yangi import  -> exit=1  'blog/views.py:judging.models'          restored=True
(b) yozuv o'chirildi -> exit=1 'arena/services.py:quizzes.models'    restored=True
(c) o'lik yozuv   -> exit=1  'nonexistent/probe.py:contests.models'  restored=True
(d) mustaqil sanash: apps=20  independent_violations=111  allowlist=111
    independent==allowlist: True   (yangi=[]  o'lik=[])
```

**B1 — to'liq salbiy to'plam** (335 test, 1m13s):

```text
  ✓ ai/model importi: buzuq holatni tutdi (exit 1)
  ✓ ai/DATABASE_URL: buzuq holatni tutdi (exit 1)
  ✓ ai/testdata: buzuq holatni tutdi (exit 1)
  ✓ arxitektura/yangi import: buzuq holatni tutdi (exit 1)
  ✓ arxitektura/ratchet: o'lik allowlist yozuvi tutildi (exit 1)

1/335 salbiy test YIQILDI — tekshiruv o'lik bo'lishi mumkin:
  - litsenziya/nazorat: `--check` exit 1
  + qo'shilgan: node/web/reselect
  + qo'shilgan: node/web/tiny-invariant
  + qo'shilgan: node/web/victory-vendor
  `python tools/licence_inventory.py`
NEG_EXIT=1
```

**F3 isboti — qizil bizning ishimizdan emas** (`git stash` ISHLATILMADI):

- `git diff HEAD -- apps/web/package.json` → `+ "recharts": "^3.10.1"` (bitta qator).
- `git diff HEAD --stat` faqat 6 fayl: `.github/workflows/ci.yml`, `apps/web/next-env.d.ts`, `apps/web/package-lock.json`, `apps/web/package.json`, `docs/research/README.md`, `tools/check_negative.py`.
- Yiqilgan paketlar (`reselect`, `tiny-invariant`, `victory-vendor`) — **recharts** ning bog'liqliklari; `grep recharts docs/research/2026-09-21-licence-inventory/packages.tsv` → 0 yozuv.
- Ya'ni qizil **oldindan mavjud** `apps/web` driftidan (sessiya boshida ham ` M` edi) kelib chiqadi, `tools/` yoki `apps/api/` o'zgarishidan EMAS.

**B6 — pytest**:

```text
platform win32 -- Python 3.12.10, pytest-9.1.1
django: version: 5.2.17, settings: config.settings (from ini)
collected 4 items
tests/test_ai_boundary.py ..                                             [ 50%]
tests/test_architecture_boundary.py ..                                   [100%]
4 passed in 0.74s
```

Izoh: `apps/api/.venv` — **Linux venv** (`.venv/bin/python` 0 baytli symlink; `home=/usr/bin`), Windows'da ishlamaydi. Windows'da pytest yo'q. Shuning uchun venv'ning sof-Python paketlari Windows Python 3.12 ga ulandi (`PYTHONPATH`, `-p no:hypothesispytest` — hypothesis `_native` Linux moduli yo'q). Bu — **muhit** cheklovi, repo nuqsoni emas.

**C1 — `deploy.yml` majburiyligi** (aniq qatorlar):

```text
218:      - name: Live contest window        <- qadam nomi
228:        run: |                           <- step-level `if:` YO'Q, `continue-on-error` YO'Q
229:          set +e
230:          python3 tools/check_deploy_window.py   <- chaqiruv
231:          code=$?
232:          set -e
233:          if [ "$code" -eq 1 ]; then
234:            echo "::error::An active contest/arena is running — deploy stopped"
235:            exit 1
236:          fi
```

`grep 'continue-on-error' deploy.yml` → 0. `grep '|| true' deploy.yml` → faqat 122, 130, 341 (boshqa qadamlar: docker prune/images), shu qadamda emas. Ya'ni chaqiruv **majburiy**.

---

## 5. Routing qarori

**Routing: NoOne** (bloklovchi tuzatish talab qilinmaydi).

- WP0 · WP5 · WP6 ning barcha qabul mezonlari **PASS**.
- Yagona qizil (`licence_inventory`) — **oldindan mavjud** `apps/web` drifti (F3); Engineer'ning o'zgarishlariga aloqasiz.
- **Qo'shimcha (bloklamaydigan) tavsiya — Engineer**: `tools/check_ai_boundary.py` ga F1 ni (ya'ni `from <app> import models` va `from . import models` ni tutishni) qo'shish. Bu kelajakdagi (Phase 3) kod uchun mustahkamlash; bugungi repo'ga ta'sir qilmaydi.
- QA tomonda tuzatiladigan test kodi **yo'q** — yozgan testlarim/qo'shimcha probe'lar to'g'ri ishladi.

---

## 6. Qaytarilgan vaqtinchalik o'zgarishlar tasdiqi

Barcha mutatsiyalar asl holatiga qaytarildi:

- `apps/api/ai/__init__.py` — 1165 bayt, LF, `git` da o'zgarmagan (untracked, asl holida).
- `apps/api/blog/views.py` — 890 bayt, LF; `git diff HEAD` bo'sh.
- `tools/architecture-allowlist.txt` — 5169 bayt, LF; 111 yozuv; `# jami: 111`.
- Vaqtinchalik probe fayllar (`_neg_probe*`) qolmadi; `apps/api/ai/__pycache__` tozalandi.
- **Oshkora izoh**: birinchi mutatsiya harnessim Python `write_text` orqali LF ni CRLF ga aylantirgan edi (3 fayl). Har biri LF ga qaytarildi; `grep -qU $'\r'` bilan tasdiqlandi. `core.autocrlf=true` bo'lgani uchun `git diff` buni ko'rsatmasdi — shuning uchun bayt darajasida tuzatildi.

**Yakuniy holat** — `git status` kutilgan to'plamga mos:

```text
 M .github/workflows/ci.yml          (Engineer — CI'ga 2 qadam)
 M apps/web/next-env.d.ts            (oldindan mavjud)
 M apps/web/package-lock.json        (oldindan mavjud)
 M apps/web/package.json             (oldindan mavjud)
 M docs/research/README.md           (boshqa ish)
 M tools/check_negative.py           (Engineer — 2 salbiy guruh)
?? apps/api/ai/  apps/api/tests/test_ai_boundary.py
?? apps/api/tests/test_architecture_boundary.py
?? deliverables/  tools/architecture-allowlist.txt
?? tools/check_ai_boundary.py  tools/check_architecture.py
```

`git diff HEAD --stat` → 6 fayl, 508(+)/3(-) — men ishga kirishishdan oldingi holat bilan bir xil. Hech qanday vaqtinchalik o'zgarish qolmadi.

---

**STATUS:** QA verification batch 1 (WP0 · WP5 · WP6) — **YAKUNLANDI**. 25 da'vo: 24 PASS, 1 🟡 (F1, bloklamaydi). WP0 PASS · WP5 PASS · WP6 PASS. Routing: **NoOne** (qo'shimcha, bloklamaydigan tavsiya — Engineer'ga F1). Vaqtinchalik o'zgarish qolmadi.
