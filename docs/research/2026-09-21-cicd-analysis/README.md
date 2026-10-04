# RankWant CI/CD — to'liq bosqichma-bosqich tahlil

> **Arxiv yozuvi.** Repoga 2026-10-04 da ko'chirildi; matn yozilgan kunidagi holatni aks ettiradi. Keyin o'zgargan: Security run 2026-09-21 da o'chirilgan, deploy poll'i `PT1M`, ikkinchi runner ishlayapti.

**Sana:** 2026-09-21 · **Manba:** repo konfiguratsiyasi + o'lchangan raqamlar
(`docs/research/2026-09-20-ship-timing/`, `2026-09-20-deploy-timing/`, Task Scheduler)
**Holat:** tahlil yozuvi — repo qoidasi emas. Amaldagi qoidalar: `CLAUDE.md`, `docs/10-operations/deploy-runbook.md`.

---

## 0. Bir qarashda — eng muhim fakt

Quvur **ikki muhitga bo'lingan**, va bu tasodif emas:

| Qism | Qayerda yuguradi | Nega |
|---|---|---|
| **CI / Security / Nightly** | GitHub-hosted `ubuntu-latest` | Public repo → daqiqalar $0, 20 parallel job |
| **Deploy** (`build` + `deploy` joblari) | **self-hosted** (`[self-hosted, rankwant]`) | Jonli Docker stack'ga tegadi — `docker compose`, tunnel, `.env.public` |

⚠️ **Muhim tushuncha:** `deploy.yml` workflow'i **production deploy qilmaydi**. U `workflow_dispatch` bilan qo'lda yuriladi, `vars.PUBLIC_ORIGIN != ''` va `confirm == 'deploy'` shartlarini talab qiladi — va repo'da 0 ta secret/variable bor, ya'ni job doim `skipped`. Sabab o'lchangan: runner konteyneri jonli `.env.public` ni ko'rmaydi (u `/work` volume'ida), `.env.public` dagi 29 kalitdan faqat 4 tasi qolardi — email zanjiri, Turnstile, OAuth, Cloudflare token jimgina yo'qolardi.

**Haqiqiy production yo'li:** host watcher → `tools/auto_deploy.sh` → `tools/deploy.sh`.
`deploy.yml` dagi `build → test → deploy` zanjiri — zaxira/qo'lda yo'l.

---

## 1. To'rt quvur va ularning trigger'lari

| Workflow | Trigger | Runner | Vaqt (o'lchangan) |
|---|---|---|---|
| `ci.yml` | `pull_request`, `push: main`, `workflow_call`, `workflow_dispatch` | hosted | docs 18–24 s · tools 59–76 s · web 103–140 s |
| `security.yml` | `push: main`, cron `0 3 * * *` | hosted | ~37–43 s |
| `nightly.yml` | cron `0 2 * * *`, manual | hosted | load 15 min cap · e2e 20 min cap · chaos 15 · compat 10 · coverage 8 |
| `deploy.yml` | **faqat** `workflow_dispatch` | self-hosted | build 10 min cap · deploy 10 min cap |
| `runner-selftest.yml` | manual | self-hosted (`rankwant-container`) | — |

**PR'da Security yo'q** (2026-09-18): har PR CI+Security juftligini yuritib, bitta runner navbatini ikki barobar oshirardi.

---

## 2. CI quvuri — job grafigi va bog'liqlik

```text
                    ┌──────────────────────────────┐
                    │ filter  (Path filter, 2 min) │   dorny/paths-filter
                    │  api web judge code tools    │   → 6 ta output
                    │  tools_node                  │
                    └───────────────┬──────────────┘
        ┌───────────────┬───────────┴────────┬──────────────────┐
        ▼               ▼                    ▼                  ▼
   ┌─────────┐    ┌──────────┐        ┌──────────┐      ┌──────────────┐
   │  api    │    │   web    │        │  judge   │      │  integrity   │
   │ 3 min   │    │  3 min   │        │  3 min   │      │   2 min      │
   │if: api  │    │if: web   │        │if: judge │      │ always()     │
   │         │    │  ||tools │        │          │      │              │
   └─────────┘    └──────────┘        └──────────┘      └──────────────┘
```

**Bog'liqlik qoidasi:** to'rttasi ham faqat `filter` ga `needs` qiladi — bir-biriga emas. Ya'ni **parallel**. Bu ataylab: ilgari `integrity` API/Web/Judge'ni kutardi va 7–11 s lik hujjat tekshiruvi pytest orqasida navbatda qolardi.

### 2.1 `filter` job — butun tezlikning kaliti

Faqat `dorny/paths-filter` ishlatadi, 6 ta output chiqaradi:

| Output | Glob | Nimani yoqadi |
|---|---|---|
| `api` | `apps/api/**` | api job |
| `web` | `apps/web/**` | web job (lint/typecheck/test/build) |
| `judge` | `services/**` | judge job |
| `tools` | `tools/**`, `.githooks/**` | web job (check suite) |
| `tools_node` | `tools/**/*.mjs`, `apps/web/package*.json` | web job ichida `npm ci` |
| `code` | `apps/** services/** tools/** tests/** docker-compose*.yml` | (keng) |

⚠️ `tools_node` ning mavjudligi sababi o'lchangan: Python-only `tools/` o'zgarishi (`check_decisions.py`, `deploy_timer.sh`) `npm ci` (14–20 s) to'lardi, holbuki u TypeScript ni umuman yuklamaydi.

### 2.2 `api` job — 3 daqiqa

Tartib: checkout → scaffold tekshiruvi → `setup-python` (pip cache) → `pip install -r requirements-dev.lock` → **ruff check + format** → **check_api_english** → **OpenAPI schema diff** → mypy cache → **mypy --show-traceback** → service host aniqlash → **makemigrations --check --dry-run**.

- Postgres 16 service container bilan (`ports: ['5432']` — GitHub host portini tanlaydi).
- **pytest bu yerda YO'Q** — Nightly `coverage` job'iga ko'chirilgan (2 min × 2 shard).
- OpenAPI diff ataylab shu jobda: alohida job bo'lsa pip+diff uchun (~15 s) runner slotini egallardi.

### 2.3 `web` job — 3 daqiqa, eng og'ir

Tartib (o'lchangan, main #182, 100 s):

| Qadam | s | Qachon ishlaydi |
|---|---|---|
| checkout + node setup | ~8 | doim |
| `npm ci` | 19–20 | web **yoki** tools_node |
| lint + typecheck (parallel `&` + `wait`) | 22 | faqat web |
| vitest | 2 | faqat web |
| check_i18n / email_locales / api_english | 3 | doim |
| i18n runtime (`.mjs`) | — | tools_node |
| **check_negative** (`NEGATIVE_JOBS=4`) | 30–32 | doim |
| `npm run build` | 8 | faqat web |

⚠️ Nega check suite aynan shu jobda: `check_i18n_runtime.mjs` `typescript` ni `apps/web/node_modules` dan o'qiydi — boshqa jobga ko'chirilsa `npm ci` takrorlanardi.

### 2.4 `judge` job — 3 daqiqa

Go: `gofmt -l` → `go vet` → `go build` → `go test`. Python: `pip install -e '.[dev]'` → ruff → mypy → pytest. Ikkalasi ham scaffold tekshiruvi bilan (yo'q bo'lsa `exit 0`).

### 2.5 `integrity` job — 2 daqiqa

`check_docs.py` → `check_confusables.py` → `check_contract.py` → `check_ordering.py` → **`check_decisions.py`** → `check_env_example.py`. `always()` bilan ishlaydi — filter yiqilsa ham.

### 2.6 `concurrency` — nozik qoida

```yaml
group: ci-${{ github.workflow }}-${{ github.ref }}
cancel-in-progress: ${{ github.event_name != 'workflow_call' }}
```

⚠️ `workflow_call` da bekor qilish **TAQIQLANGAN**: deploy `test` job'ini kutadi, bekor qilingan job `cancelled` qaytaradi → darvoza hech qachon boshlanmaydi va ketma-ket push'lar deploy'ni **jimgina** o'tkazib yuboradi.

---

## 3. Lokal darvoza (pre-push) — 4 soniya

`.githooks/pre-push` ataylab **tor**. Faqat o'zgargan qismlar ishlaydi:

| Shart | Tekshiruv |
|---|---|
| doim | `push_guard.py` — `main` ga to'g'ridan push yopiq, soxta muallif rad |
| `apps/api/**` | ruff check + format |
| `apps/web/**` yoki `tools/check_i18n` | check_i18n |
| `apps/api/**` yoki `tools/check_api_english` | check_api_english |
| `apps/web/**` yoki `tools/check_hardcoded` | check_hardcoded |
| `tools/deploy.sh` | `check_negative.py --serial decisions` (~10 s) |

⚠️ 2026-09-18 o'lchovi: **to'liq** hook (mypy + pytest + tsc + 153 salbiy test) Windows'da **5.8 daqiqa** edi, keyin CI yana ~4 daqiqa. Shuning uchun qisqartirilgan — qolgani CI da.

---

## 4. PR → merge → live: o'lchangan zanjir

| Bosqich | Odatiy | Manba |
|---|---|---|
| `git commit` | 1.3 s | #187 (hook yo'q) |
| `git push` + pre-push | 4.0–4.1 s | #187 |
| `gh pr create` | 3.9 s | #187 |
| `gh pr merge --squash` | 4.8 s | #187 |
| CI — docs-only | 18–24 s | #185, #186 |
| CI — tools | 59–76 s | #187 |
| CI — web | 103–140 s | #180, #182 |
| Security (main, parallel) | ~37 s | #187 |
| **Avto-deploy kutish** | **0–300 s** (o'lchangan ~5 min) | 16:00:21 CI yashil → 16:05:11 deploy |
| Deploy — issiq | **156 s (2.6 min)** | lokal o'lchov |
| Deploy — judge miss | **954 s (15.9 min)** | lokal o'lchov |
| Avto-deploy yurish (log) | 170 s | 16:05:11 → 16:08:01 |

**Happy-path yig'indi (kutishsiz):**

| Yo'l | Lokal | PR CI | Merge | Main CI | Deploy | Jami |
|---|---|---|---|---|---|---|
| Docs | 14 s | 20 s | 5 s | 22 s | 0 (kerak emas) | **~1 min** |
| Tools | 14 s | 59 s | 5 s | 76 s | 0 (obrazga tushmaydi) | **~2.6 min** |
| Web | 14 s | 110 s | 5 s | 110 s | 156 s | **~6.6 min** |
| Judge Dockerfile | 14 s | ~80 s | 5 s | ~80 s | **954 s** | **~19 min** |

---

## 5. Sekinlashuvlar — ta'sir × chastota tartibida

### ① `deploy.sh` image bake — **eng qimmat**
Issiq 87 s, judge miss **866 s**. O'lchangan qismlar (2026-09-20):
- Judge nsjail/apt qadamlari: 35 + 132 + 107 + 48 s
- **Judge export + unpack: 195.5 + 31.9 = 227.6 s**
- Web Next compile: ~23–29 s (parallel, lekin bake judge oxirini kutadi)

Bu **PR/merge emas, live** vaqtini yeydi.

### ② 5 daqiqalik watcher — **bekor qilinadigan kutish**
Task Scheduler: `RankWant Auto Deploy`, trigger `MSFT_TaskDailyTrigger`, `interval=PT5M`, `duration=P1D`. O'lchangan teshik: CI 16:00:21 da yashil, deploy 16:05:11 — ya'ni **~5 daqiqa** faqat kutish.

### ③ CI ikki marta
PR SHA va squash SHA — ikki xil commit, ikki marta to'liq to'plam. Tools: 59+76 s; web: 110+110 s.

### ④ `web` job ichidagi doimiy qismlar
`npm ci` 19–20 s + `check_negative` 30–32 s — tools-only PR'da ham.

### ⑤ Qizil CI + qayta push
#187 da +69 s mashina + odam vaqti. Oldini olish: lokal `check_negative.py decisions` (~10 s) pre-push da `tools/deploy.sh` o'zgarganda — bu **qo'shilgan** (2026-09-20).

### ⑥ `verify` — endi arzon
Ilgari qat'iy `sleep 10` edi. Endi `wait_health()`: 1 s interval bilan `docker exec` health so'rovi, `RANKWANT_VERIFY_WAIT=30`. Yutuq: 0–8 s har deploy.

### ⑦ Self-hosted navbat
`build`/`deploy` bitta self-hosted runner'da ketma-ket. Ikkinchi runner (`rankwant-ci-runner-2`) register qilinmagan → deploy navbati ketma-ket.

### ⑧ Security'da to'liq clone
`actions/checkout` + `fetch-depth: 0` (gitleaks butun tarixni ko'rishi kerak) — main push'da har safar.

---

## 6. GitHub-hosted'dan maksimal foyda — nima qilingan va nima qolgan

### Allaqachon optimallashtirilgan ✅

| Optimizatsiya | Yutuq |
|---|---|
| CI/Security/Nightly → `ubuntu-latest` (public repo) | daqiqalar $0, 20 parallel job |
| `dorny/paths-filter` + 6 output | keraksiz job umuman ishga tushmaydi |
| `tools_node` ajratilgan | Python-only tools PR'da `npm ci` yo'q → **14–20 s × 2** |
| Security PR'dan olib tashlangan | navbat ikki barobar qisqardi |
| Uch security tekshiruvi bitta jobda | 43 s ish 3 daqiqaga aylanmasin (GitHub to'liq daqiqaga yumalaydi) |
| `integrity` parallel (serial emas) | 7–11 s lik job pytest orqasida kutmaydi |
| pip / npm / mypy / `.next/cache` keshlari | install va compile qayta ishlamaydi |
| `concurrency` + `cancel-in-progress` (PR/push) | ketma-ket push eski runni bekor qiladi |
| Og'ir testlar Nightly'ga | PR CI 3 daqiqaga sig'adi |
| `PYTHONNOUSERSITE=1` | stray pytest pluginlari yuklanmaydi |
| Job timeout 1–3 min (build/deploy bundan mustasno) | osilib qolgan job runner'ni ushlab turmaydi |

### Hali qolgan imkoniyatlar ⚠️

| Imkoniyat | Kutilgan yutuq | Xavf |
|---|---|---|
| `deploy.yml` ni butunlay o'chirish (u baribir skipped) | navbatdan bitta workflow yo'qoladi | yo'q — lekin qo'lda zaxira yo'l kerak bo'lishi mumkin |
| Security'ni `main` push'da **docs-only** o'zgarishda o'tkazib yuborish | ~40 s × docs push | zaif — gitleaks tarixni ko'radi, lekin docs commitda sir qo'shilmaydi |
| `pip install` o'rniga `uv` (CI da) | 5–15 s har api job | lock fayl formati |
| Nightly `e2e` 20 min cap → shard'larga bo'lish | devor soati qisqaradi | murakkablik |
| `security.yml` `fetch-depth: 0` → shallow + alohida gitleaks job | clone vaqti | gitleaks tarixni ko'ra olmasligi mumkin |

**Nima optimallashtirib bo'lmaydi:** `actions/checkout` + `setup-*` + `npm ci` / `pip install` — bu quvurning "soliq"i. Kesish yo'li faqat ularni **kamroq ishga tushirish** (path filter) — va bu allaqachon qilingan.

---

## 7. PR merge'dan keyin deploy'ni maksimal tez qilish

### Mexanizm

```text
merge (squash) → main CI + Security yashil
                      │
                      ▼
        bash tools/kick_auto_deploy.sh        ← merge oxirida darhol
                      │  schtasks /run /tn "RankWant Auto Deploy"
                      ▼
        tools/auto_deploy.sh  (5 min tick ham bor)
          1. qulf (deploy.sh bilan bir xil) — band bo'lsa jim chiqadi
          2. DEPLOY_FREEZE tekshiruvi
          3. git fetch origin main
          4. worktree → origin/main (ff-only; dirty bo'lsa to'xtaydi)
          5. image_scope = deploy_scope.py --from-live --to TARGET
               → docs/tools = BO'SH = bake yo'q, JIM chiqadi
          6. all_up + check_deploy.sh → "ish yo'q" bo'lsa jim chiqadi
          7. backoff: shu SHA uchun 1800 s ichida urinilgan bo'lsa — chiqadi
          8. darvoza OLDINDAN: check_deploy_gate.py yopiq → exit 0, to'siq YO'Q
          9. record_attempt → deploy.sh --yes (RANKWANT_LOCK_HELD=1)
                      ▼
        tools/deploy.sh — 8 qadam
          gate → preflight → contest_window → build → dump → migrate
          → showmigrations → up → verify → prune
```

### Maksimal tezlik uchun nazorat ro'yxati

| # | Shart | Nega / tekshirish |
|---|---|---|
| 1 | **Merge'dan keyin darhol kick** | 5 min tick kutmaslik. `bash tools/kick_auto_deploy.sh` (Git Bash `MSYS_NO_PATHCONV=1` kerak — `/run` yo'lga aylanadi) |
| 2 | **Faqat CI yashil bo'lgach kick** | Darvoza main CI + Security `success` talab qiladi. Erta kick → `exit 0`, to'siq yo'q (2026-09-20 da tuzatilgan) — lekin vaqt yo'qoladi. `gh run watch` |
| 3 | **Deploy worktree toza** (`wt/deploy`) | Dirty bo'lsa `die` — `git status --porcelain --untracked-files=no` |
| 4 | **`wt/deploy` ff-only holatda** | Ajralib ketgan bo'lsa `die` (jimgina tuzatish yo'q — ataylab) |
| 5 | **`.env.public` mavjud** | `$LIVE_DIR/.env.public` = `cp/rankwant/.env.public`; worktree'da emas |
| 6 | **`DEPLOY_FREEZE` o'rnatilmagan** | Bo'lsa watcher `exit 0` — jim |
| 7 | **Faol contest yo'q** | `check_deploy_window.py` → exit 1 bo'lsa deploy to'xtaydi (qoida №1) |
| 8 | **Hech bir checkout'da dirty `docker-compose*.yml` yo'q** | Darvoza 3-qoidasi — deploy uni jimgina olib tashlaydi |
| 9 | **Deploy qulfi bo'sh** | Qulf band bo'lsa watcher **jim** `exit 0` qiladi — log'da sabab yo'q. `git-common-dir/rankwant-deploy.lock` |
| 10 | **Judge qayta qurilmasin** | `deploy_scope.py` faqat `services/judge-go` o'zgarganda qo'shadi. Compose/`deploy.sh` o'zgarsa — **hamma** servis (global path) |
| 11 | **C: > 15% bo'sh** | `prune_docker_disk.sh` har deploy'dan keyin; SHA teglar saqlanmaydi |
| 12 | **Backoff'ni bilish** | Deploy yiqilsa shu SHA uchun **1800 s** blok. Darhol qayta urinish: `rm -f ~/.rankwant-auto-deploy-state` |
| 13 | **Docs/tools PR = 0 deploy** | `deploy_scope.py` bo'sh doira qaytaradi va watcher **jim** chiqadi — bu normal, xato emas |

### Eng katta yutuq imkoniyati

**① Watcher intervali 5 min → 1 min.** FINDINGS §B da taklif qilingan, **hali qo'llanmagan** (o'lchandi: `interval=PT5M`). Kick bo'lmasa o'rtacha **~2.5 min** yutuq. Narxi: `check_deploy.sh` 5× tez-tez ishlaydi (docker inspect + fayl xeshlari) — arzon, lekin log shishadi.

**② Kick'ni avtomatlashtirish.** Hozir kick qo'lda/agent orqali. Uni `deploy.yml` ichidan chaqirish mumkin emas — hosted runner'da `schtasks` yo'q. Variant: kichik poller yoki `repository_dispatch` → host'da tinglovchi.

**③ `verify` va `prune`** allaqachon optimallashtirilgan (sleep 10 → health; prune faqat tasdiqdan keyin).

---

## 8. Xulosa — uchta raqam

1. **Lokal git — 14 soniya.** Kesishning hojati yo'q.
2. **Vaqt merge'dan keyin ketadi:** CI ikki marta (18–140 s × 2) + watcher kutishi (0–300 s) + `deploy.sh` (156 s issiq / **954 s** judge miss).
3. **Eng qimmat bitta narsa — judge image bake** (export+unpack 227 s). Undan keyin 5 daqiqalik watcher tick'i.

**Amaliy qoida:** docs/tools PR uchun deploy **umuman bo'lmaydi** (`deploy_scope.py` bo'sh) — kutish ham, bake ham yo'q. Web PR uchun ~2.6 min. Judge Dockerfile tegilsa — 16 min kutishga tayyor turing.
