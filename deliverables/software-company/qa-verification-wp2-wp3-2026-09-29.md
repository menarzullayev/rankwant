# QA Verification — WP2 (verdict taxonomy) va WP3 (data origin) — adversarial

**Sana:** 2026-09-29
**Tekshiruvchi:** Buffy (mustaqil QA — Workbuddy credit tugashi sababli yarim qolgan `qa-wp2` / `qa-wp3` ishini davom ettirdi)
**Repo:** rankwant · **HEAD:** `4c85e96` (WP3) ← `1d0d70d` (WP2) — ikkalasi ham origin/main'da YO'Q (`ahead 2, behind 35`), PR ochilmagan
**Usul:** mustaqil, adversarial. Engineer da'volari o'lchandi: bu mashinada **birinchi marta** pytest haqiqatan yurgizildi (venv `rm -rf` + `uv venv --python 3.12` + `uv pip install -r requirements-dev.lock` bilan qayta qurildi — eski `.venv` WSL'dan qolgan 0-bayt fayllar edi).

---

## 1. WP2 — Verdict taxonomy (D11B · M10)

| # | Da'vo | Buyruq | Haqiqiy natija | Hukm |
|---|---|---|---|---|
| WP2① | 4 o'lik kod hujjatlangan | `pytest tests/test_verdict_taxonomy.py::TestDeadCodesDocumented` | **5/5 yashil** — `verdicts.py` da har kod yonida `O'LIK` izohi; `docs/08-technical-spec/verdict-taxonomy-dead-codes.md` mavjud | **PASS** |
| WP2② | M10 migratsiya bajariladi | `pytest ...TestM10Migration` | **3/3 yashil** — batch ishlaydi, teskari yo'nalish bor | **PASS** (kod) / **SHARTLI** (ma'lumot — §2.3) |
| WP2③ | `RE_SIGNAL`/`RE_EXIT` split + i18n qayta yozilmagan | `python tools/check_verdict_codes.py` | `API 24 kod · web 24 · ikonka 24 · 10 til — mos ✓`, exit 0 | **PASS** |
| — | taxonomy fayllari git diff | `git show 1d0d70d --stat` | faqat 4 fayl: verdicts.py, migratsiya, test, hujjat — shipped split'ga tegilmagan | **PASS** |

### 2.3 🔴 Bloklovchi topilma (M10 mohiyatan no-op)

`Attempt` modelida **`details` maydoni YO'Q** — telemetriya `judge_meta` JSONField'da (`apps/api/judging/models.py`, `judge_meta` qatori). Judge esa `signal`/`exit_code` kalitlarini hech qanday natijaga yozmaydi: signal/exit kodidan verdict **faqat classify bosqichida** hisoblanadi (`services/judge-go/judge.go`, `classify` funksiyasi oxiri — `ExitCode >= 128 → RE_SIGNAL`, aks holda `RE_EXIT`).

Natija: `details` yo'q ⇒ heuristika **har doim** default `RE_SIGNAL` ga tushadi. 18 163 tarixiy qatorning barchasi bir xil qiymat oladi — signal/exit **ajratilmaydi**. Migratsiya yiqilmaydi va testlar yashil, chunki testlar ham xuddi shu mavjud bo'lmagan maydon ustida mock bilan ishlaydi.

**Kod migration'ning o'zi toza** (batch 1000, iterator, teskari yo'nalish bor). Muammo — heuristika manbasi: `details` o'rniga `judge_meta` dan foydalanish kerak bo'lar edi (va `judge_meta` da ham signal kaliti hozir yo'q — WP7'da judge_meta'ga `signal`/`exit_code` yozish kerak bo'ladi).

**Tavsiya (yangi qaror yo'q, ish tuzatish):** migratsiyani `judge_meta` ni o'qishga o'tkazish yoki saqlanib qolgan eski `RE` qatorlar qayerdan olinishini qayta ko'rish. Eng halol variant — heuristika yo'qligini ochiq tan olib, teskari migratsiya bilan birga qoldirish va M10'ni faqat "eski RE → RE_SIGNAL (no'lchangan default)" deb hujjatlash. Lekin bu **egasi qarori** — chunki D11B "ajratish" deb atalgan, amalda esa ajratish bo'lmayapti.

---

## 2. WP3 — Data origin (D9 · M3)

| # | Da'vo | Buyruq | Haqiqiy natija | Hukm |
|---|---|---|---|---|
| WP3① | `origin` ustuni + enum | `pytest tests/test_origin.py::TestUserOrigin` | **5/5 yashil** (SQLite, `DATABASE_URL`siz) | **PASS** |
| WP3② | `Attempt.origin` YO'Q | `test_attempt_origin_is_absent` | yashil — modelda yo'q | **PASS** |
| WP3③ | North Star SQL `origin='real'` bilan ishlaydi | `tools/check_metrics.py --self-test` + manba o'qish | SQL to'g'ri yozilgan; **jonli DB'da sinov O'TKAZILMADI** (psycopg2 dev-venv'da yo'q, pastda §3.2) | **SHARTLI** |
| WP3④ | Backfill audit raqami | `pytest ...TestBackfillOrigin` | **2/5 YIQILDI** — `capsys.stdout` atributi yo'q | **FAIL** |
| WP3⑤ | `imported` alohida qiymat | `test_imported_is_separate_value` | yashil | **PASS** |
| WP3⑥ | Seed user soni o'lchangan (U2) | — | **HECH QAYERDA o'lchanmagan** (10 000 / 10 001 / 10 068) | **FAIL — ish qolgan** |
| — | ruff (3 yangi fayl) | `ruff check` + `ruff format --check` | **5 xato + 2 fayl formatlanishi kerak** | **FAIL** (CI `api` job buni push'da ushlaydi) |
| — | `makemigrations --check` | `manage.py makemigrations --check --dry-run` | `No changes detected` | **PASS** |
| — | `check_negative.py neg_check_metrics` | `python tools/check_negative.py neg_check_metrics` | **3/3 o'tkazib yuborildi** — `DATABASE_URL` yo'q (CI web job'ida ham yo'q!) | **SHARTLI — darvoza CI'da so'q** |

---

## 3. 🔴 Bloklovchi va 🟠 muhim topilmalar

### 3.1 🔴 WP2/WP3 testlari 3/10 YIQILDI — Engineer va birinchi QA ikkalasi ham yurgizmagan

```
FAILED tests/test_origin.py::TestBackfillOrigin::test_backfill_audit       — capsys.stdout yo'q
FAILED tests/test_origin.py::TestBackfillOrigin::test_backfill_dry_run     — capsys.stdout yo'q
FAILED tests/test_verdict_taxonomy.py::TestCheckVerdictCodes::test_i18n_parity_all_locales — ModuleNotFoundError: tools
```

Ikkala ildiz ham **import modelida**:
- `test_origin.py` `call_command(stdout=capsys.stdout)` yozgan — pytest `CaptureFixture`da `readouterr()` bor, `stdout` yo'q. `capsys.readouterr().out` o'rnini ishlatish kerak (va natijani `readouterr` dan keyin o'qish).
- `test_verdict_taxonomy.py` `from tools.check_verdict_codes import …` — repo ildizi `sys.path`da emas, `tools/` paket ham emas (`__init__.py` yo'q). Yechim: `sys.path.insert(0, str(ROOT / "tools"))` + `import check_verdict_codes`, yoki testni subprocess sifatida yuritish.

⚠️ Sabab zanjiri: venv buzuq edi (0-bayt python) ⇒ hech kim pytestni yurgiza olmadi ⇒ "yashil" da'volar **yurgizilmagan** kodga asoslandi. Bu — batch2 hisobotida ham qayd etilgan muhit cheklovi, lekin uning oqibati (yiqilgan testlar push qilinmoqda) qayd etilmagan edi.

⚠️ CI'da `api` job faqat ruff/mypy/OpenAPI/makemigrations yurgizadi — **pytest Nightly'ga ko'chirilgan** (`pr_skips_heavy_ci`). Ya'ni bu testlar push qilinsa, Nightly'gacha hech kim ko'rmaydi.

### 3.2 🟠 CI'da `check_metrics.py` rankwant_test bo'sh bazasida yiqiladi

`ci.yml:203-206` (`api` job): `DATABASE_URL=…/rankwant_test` bilan `python3 tools/check_metrics.py`. Lekin:
1. **`manage.py migrate` CI'da umuman yuritilmaydi** — `rankwant_test`da `core_user` jadvali bo'lmaydi ⇒ `psycopg2.errors.UndefinedTable` ⇒ **exit 1**.
2. Bo'sh bazada `total = 0` ⇒ `errors.append("Bazada umuman foydalanuvchi yo'q")` ⇒ **exit 1** (birinchi push'da).

Demak bu qadam push qilingan **birinchi PR'ning CI'sini qizaradi**. Kerak: (a) qadam oldidan `manage.py migrate` + seed, yoki (b) qadamni `--self-test` rejimida yuritish, yoki (c) metrics jonli/nightly stack'ga qaratsin. Hozircha qadamni o'chirib qo'ymaslik — uni tuzatish kerak (o'chirish AC WP3③ ni o'ldiradi).

### 3.3 🟠 Salbiy metrik testlar CI'da doim SKIP bo'ladi

`neg_check_metrics` guruhining barcha 3 testi `DATABASE_URL` talab qiladi, `metrics_precondition` esa uni bo'lmagan holda **"o'tkazib yuborildi"** deb yozadi. CI **web** job'ida (`check_negative` yuritiladigan joy) `DATABASE_URL` yo'q. Ya'ni "salbiy test majburiy" qoidasi bu guruh uchun **hech qachon bajarilmaydi**. Kerak: precondition'ga CI'da Postgres service ulash yoki guruhni api job'ga ko'chirish (migrate'dan keyin).

### 3.4 🟡 Past (bloklamaydi)

- `psycopg2` dev-lock'da **yo'q** (faqat prod `requirements.lock`da) ⇒ dev muhitda `check_metrics.py` `ImportError` beradi. Agar 3.2'da (a) tanlansa, `psycopg2-binary`ni `requirements-dev.txt`ga qo'shish kerak.
- `backfill_origin.py` `is_password_usable` import qiladi — to'g'ri; lekin `create_user(password="")` yo'llari bilan `make_password(None)` farqi testda nozik: `make_password(None)` ishlatiladigan parol yaratadi (usable!) — testdagi `imported1` klasifikatsiyasi faqat `terms_accepted_at is None` + parol **bo'sh satr** bo'lgani uchun tutadi ("" → `is_password_usable("")` False). Mo'ljallangan holat bilan mos — lekin sinovdan o'tmagan bo'lgani uchun buni o'zim tekshirdim: logika to'g'ri, test yiqilishining sababi shundan qat'iy nazar `capsys`.
- WP3⑥ (U2 seed user soni) hujjatda ham, skriptda ham o'lchov yo'q — bu **ish birligi emas**, "evidence gate" — lekin AC lock'da WP3⑥ qatorida turibdi. Qolgan ish sifatida qayd qilindi.

---

## 4. Verdict

| WP | Mezonlar | Natija |
|---|---|---|
| **WP2** | ① PASS · ② PASS (kod) / SHARTLI (ma'lumot: M10 no-op) · ③ PASS | 🟡 **SHARTLI** — M10 heuristikasi `details`ni o'qiydi, maydon yo'q ⇒ **egasi qarori kerak** (§2.3) |
| **WP3** | ①②⑤ PASS · ③ SHARTLI (jonli DB'da sinovlanmagan + CI qadami qizaradi) · ④ **FAIL** (testlar yiqiladi) · ⑥ **ishlanmagan** (U2) | 🔴 **FAIL** — push qilishdan OLDIN 3 ta test va ruff tuzatilishi shart |

### Push'dan oldin majburiy tuzatishlar (men keyingi qadamda qilaman — Saidakbar aka tasdiqlasa)

1. `test_origin.py`: `capsys.stdout` → `capsys.readouterr()` (2 joy).
2. `test_verdict_taxonomy.py`: `tools` importini subprocess yoki `sys.path` bilan tuzatish.
3. Ruff: 5 xato + format (3 fayl).
4. `ci.yml` api job'dagi `check_metrics.py` qadamini migrate/seed bilan ishlaydigan qilib tuzatish (yoki `--self-test`ga o'tkazish va jonli o'lchovni Nightly'ga qo'yish) — 3.2 bo'yicha.
5. M10 heuristikasi uchun **Saidakbar akadan qaror**: `details` → `judge_meta` o'tkazilsinmi yoki default ajratishsiz hujjatlanadimi?

### Qolgan ish (WP2/WP3'dan keyin)

- **U2** — seed user aniq soni (WP3⑥)
- **U1 + WP7** — bake-off protokoli tayyor (`u1-bakeoff-protocol-2026-09-29.md`); bloklovchi: `tests/security/check_compose.py:55-56` privileged talabi WP7'da yangilanishi shart.

---

## 5. Muhit haqida yozuv (keyingi agentga)

`apps/api/.venv` 2026-09-23 da WSL'da yaratilgan va Windows'da 0-bayt python fayllari qoldirgan. Bu venv **o'chirildi va Windows uchun qayta qurildi** (`uv venv .venv --python 3.12` + `uv pip install -r requirements-dev.lock -p .venv`). Dual-boot protokoli bo'yicha agar keyin Linux'ga o'tilsa, venv'ni u yerda ham qayta qurish kerak bo'ladi — yoki ikki tizimli muhit uchun venv'ni umuman repo ichidan tashqariga ko'chirish alohida qaror.

---

## 6. CTO qarorlari ijrosi (2026-09-29, ikkinchi bosqich) — BAJARILDI

Owner tavsiyaviy qarorlarni tanladi: «CTO tavsiyaviy qarorlarini tanlab o'zing bajar». Uchtasi ham bajarildi va har biri **o'lchandi**:

### Q-1. M10 heuristikasi → `judge_meta` (o'lchov bilan qaror)

**Yangi fakt (jonli baza):** `SELECT count(*) FROM judging_attempt WHERE verdict='RE'` = **0** (jami attempt = 5, hammasi `AC`). Hujjatlardagi **18 163 raqami joriy bazaga tegishli emas** — hujjatdan hujjatga ko'chgan. Migratsiya deploy'da **no-op** bo'ladi va bu endi NORMATIV holat sifatida yozildi.

**Bajarilgan tuzatishlar:**
- Heuristika `details` (bunday maydon YO'Q) → `judge_meta` (mavjud JSONField) ga ko'chdi.
- Umumiy manba: `apps/api/judging/migrations/_m10_heuristic.py` — migratsiya va testlar bitta funksiyani chaqiradi (aynan bir xil mantiq kafolati).
- `verdict-taxonomy-dead-codes.md` ga ikkala o'lchangan cheklov yozildi (judge signal yozmaydi + 18 163 raqami eskirgan).

### Q-2. Testlar + ruff — tuzatildi va kuchaytirildi

- `test_origin.py`: `capsys.stdout` (bunday atribut yo'q) → `capsys.readouterr()`.
- `test_verdict_taxonomy.py`: `from tools.…` importi → `sys.path` + `importlib` (funksiya ichida, yo'lni qaytaradi).
- **Qo'shimcha topilma (clasifikator):** demo markeri sifatida email domen qoidasi (`@example.com`) OLIB TASHLANDI — o'lchandi: `seed_stress.py` neytronlarni EMAIL'SIZ yaratadi, hech bir yozuv domenga tayanmaydi; eski qoida real user'ni (`@example.com` manzilli) demo'ga aylantirardi.
- **mypy strict:** 9 xato (TextChoices taqqoslash) → `.value` orqali — `Success: no issues found in 4 source files`.
- Yakuniy holat: **pytest 21/21 · ruff toza · format toza · makemigrations `No changes detected` · OpenAPI byte-identical.**

### Q-3. CI metrics qadami — uch qatlamli tuzatish (o'lchandi)

**Yangi topilmalar (jonli o'lchovsiz ko'rinmasdi):**
1. `import psycopg2` — bunday paket YO'Q (lock'da faqat `psycopg` v3) ⇒ CI'da qadam ImportError bilan yiqilardi. → `psycopg` ga o'tkazildi.
2. CI'da `manage.py migrate` umuman yuritilmasdi ⇒ `core_user` jadvali bo'lmasdi. → `Migrate the test database` qadami qo'shildi (migratsiyalar shu zaharda birinchi marta haqiqiy Postgres'da yuridi: OK).
3. **Migratsiya raqamlari to'qnashuvi:** lokal WP3 `0026_user_origin` yaratgan, lekin origin/main'da `0026` allaqachon `0026_client_log` (jonli bazada ham shu) ⇒ merge'da graf vilqalanardi. → Fayllar `0027_user_origin` / `0028_backfill_origin` ga ko'chirildi (dependencies moslashtirildi, `makemigrations --check` toza).
4. `--allow-empty` bayrog'i (bo'sh test bazasi = NORMA), lekin **darvoza kuchaytirildi**: endi `North Star = 0` ham (bo'sh bo'lmagan bazada) xato — mutatsiyalar ma'noli bo'lishi uchun.
5. `neg_check_metrics` salbiy testlari: langarlar buzilgan edi (ko'p qatorli langar topilmadi) va `psycopg2` tufayli umuman SKIP bo'lar edi. Endi precondition bo'sh bazani o'zi seed qiladi (1 ta `real` user) va mutatsiyalar bayroqsiz yuradi. **O'lchandi: 3/3 ✓** (`wrong origin` exit 1, `impossible` exit 1, `nazorat` exit 0).

### Umumiy salbiy to'plam holati

`python tools/check_negative.py` → **339/340**. Yagona qizil — `litsenziya/nazorat`: `licence_inventory.py --check` drift (recharts/package-lock o'sgan, #244 dan beri generator yuritilmagan) — **bu WP2/WP3 doirasidan tashqari, ilgari mavjud** (`licence_inventory.py` o'zgarmagan). Generatorni yurgizish alohida kichik PR.

### Qolgan cheklov (deploy bosqichiga)

Jonli `rankwant` bazasida yangi migratsiyalar (`core 0027/0028`, `judging 0008`) hali qo'llanmagan — ular keyingi **deploy** bilan boradi (`tools/deploy.sh` migratsiyani o'zi yuritadi). WP3③ dalili uchun deploy'dan keyin `tools/check_metrics.py` jonli bazada yuritilishi kerak (974k foydalanuvchi — raqam u yerda chiqadi).
