# CI Windows muhitida — sabab tahlili va tuzatish variantlari

Sana: 2026-09-14 · Repo: `menarzullayev/rankwant` (private) · Branch: `main`
Tekshiruv usuli: faqat o'qish (`gh api`, `git log`, `docker ps`). Kod tegilmadi.

---

## 0. Qisqa xulosa

CI Windows'da "buzilmagan". **Ishlaydigan runner yo'q** — o'lchandi:

```
gh api repos/menarzullayev/rankwant/actions/runners
→ total_count: 2
  nsn-pc-rankwant    os: Linux  status: offline  labels: [self-hosted, Linux, X64, rankwant]
  nsn-pc-rankwant-2  os: Linux  status: offline  labels: [self-hosted, Linux, X64, rankwant]
```

Ya'ni runner **Linux** sifatida ro'yxatdan o'tgan va hozir **oflayn**.
`runs-on: [self-hosted, rankwant]` shu ikkalasini kutadi → hech qachon
tayinlanmaydi → job `queued` bo'lib qoladi.

Ikkinchi, mustaqil xato: **`Deploy` workflow'i hech qachon ishga tushmagan**
(10 ta run, hammasi `startup_failure`, 0 job). Bu Windows'ga aloqasi yo'q —
fayl darajasidagi xato, `7c39b46` (2026-09-13 05:27) dan beri.

Uchta alohida muammo bor, ular bir-biriga o'xshamaydi:

| # | Muammo | Windows'ga bog'liqmi? | Og'irlik |
|---|---|---|---|
| 1 | Runner oflayn → hamma run `queued`/`cancelled` | Ha (runner Linux tomonida qolgan) | Bloklovchi |
| 2 | `Deploy` → `startup_failure` (ruxsat mos kelmaydi) | Yo'q | Bloklovchi |
| 3 | Workflow'lar Linux-ga qattiq bog'langan | Ha (Windows runner qo'shilsa yoriladi) | Oldindan aytilgan |

---

## 1. Dalillar (o'lchangan, taxmin emas)

### 1.1 Run tarixi — sinish nuqtasi aniq

```
gh run list --workflow=ci.yml --limit 30
2026-09-12T17:37:51Z  success     ← oxirgi HAQIQIY yashil
2026-09-12T17:57:34Z  failure     ← oxirgi haqiqiy yiqilish (mypy)
2026-09-12T20:28:53Z  cancelled   ┐
2026-09-13T10:57:58Z  cancelled   │ shu yerdan boshlab
2026-09-13T18:34:09Z  (queued)    ┘ HECH BIRI ISHLAMAGAN
```

### 1.2 "Cancel" ning sababi — concurrency, xato emas

```
gh run view 34774703553
ANNOTATIONS:
X Canceling since a higher priority waiting request for ci-CI-refs/heads/main exists
```

`ci.yml` da:

```yaml
concurrency:
  group: ci-${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: ${{ github.event_name != 'workflow_call' }}
```

Runner yo'q → run navbatda turadi. Har yangi push **o'sha guruhdagi**
navbatdagi runni bekor qiladi. 6–27 daqiqa — ish vaqti emas, **navbatda
kutish vaqti**. Ya'ni bu "cancel" — natija, sabab emas.

⚠️ Muhim: `cancel-in-progress` tufayli **haqiqiy yiqilish ham ko'rinmay
qoladi**. Runner qaytsa ham, tez ketma-ket push'larda oldingi run bekor
bo'ladi va siz faqat oxirgisini ko'rasiz.

### 1.3 `Deploy` — boshqa sinf xatosi

```
gh run list --workflow=deploy.yml --limit 30
→ 10 ta run, HAMMASI startup_failure (2026-09-13T10:57:59Z dan boshlab)
gh api .../actions/runs/34775028456/jobs → {"total_count":0,"jobs":[]}
gh run view 34775028456 → "This run likely failed because of a workflow file issue."
```

`startup_failure` + **0 job** = workflow **parse/validatsiya** bosqichida
yiqilgan. Runner oflayn bo'lsa natija `queued` bo'lardi, `startup_failure`
emas. Demak bu — fayl xatosi, runner holatidan mustaqil.

---

## 2. Sabab 1 — Self-hosted runner oflayn

**Nima bo'lgan:** runner Linux muhitida (`nsn-pc-rankwant`) ishlayotgan edi.
Windows'ga o'tilganda u ishga tushmaydi. GitHub'dagi yozuv qolgan, holat —
`offline`.

**Nima uchun bu "Windows CI muammosi" kabi ko'rinadi:** joblar
`queued` → keyin `cancel` bo'ladi. Yashil ham, qizil ham ko'rinmaydi —
"doim xato bilan tugayapti" taassuroti shundan.

**Tuzatish variantlari:**

| Variant | Nima qilinadi | Plyus | Minus |
|---|---|---|---|
| **A. WSL2 ichida Linux runner** (tavsiya) | WSL2 Ubuntu'ga `actions-runner` o'rnatiladi, Docker Desktop WSL integratsiyasi bilan | Workflow'lar **o'zgartirilmaydi** — ular Linux uchun yozilgan. `bash`, `services:`, `docker`, `systemctl` hammasi ishlaydi | WSL2 + `systemd=true` (`/etc/wsl.conf`) kerak; tunnel uchun `systemctl` shart |
| **B. Windows'da native runner** | `actions-runner` Windows'ga o'rnatiladi | Runner mashinada, WSL'siz | **Har workflow qayta yozilishi kerak** (§4 ga qarang). Eng qimmat yo'l |
| **C. GitHub-hosted `ubuntu-latest`** | `runs-on:` almashtiriladi | 15 daqiqada ishlaydi, runner boshqaruvi yo'q | Private repo → bepul 2000 daqiqa/oy; jonli stack'ka va lokal Docker volume'larga kirmaydi |
| **D. A/B ustiga label** | `runs-on: [self-hosted, rankwant, linux]` | Windows runner tasodifan Linux job'ini olmaydi | Yolg'iz o'zi muammoni hal qilmaydi |

**Tavsiya:** A + D. Workflow'lar Linux uchun yozilgan — ularni Windows'ga
ko'chirish (B) yangi xatolar manbai bo'ladi (ayniqsa `services:`, CRLF va
`systemctl`).

**Ishga tushganini tekshirish:**

```bash
gh api repos/menarzullayev/rankwant/actions/runners \
  --jq '.runners[] | "\(.name) \(.os) \(.status)"'
# ikkalasi "online" bo'lishi kerak
```

---

## 3. Sabab 2 — `Deploy` startup_failure (ruxsat mos kelmasligi)

**Qoida:** reusable workflow (`uses: ./.github/workflows/ci.yml`) chaqiruvchi
bergan ruxsatdan **faqat pasaytirishi** mumkin, **ko'tarolmaydi**. Caller'da
aniq `permissions:` bloki bo'lsa, ko'rsatilmagan HAR scope `none` bo'ladi.

`deploy.yml` (chaqiruvchi):

```yaml
permissions:
  contents: read
  actions: read      # ← pull-requests YO'Q → none
```

`ci.yml` (chaqiriluvchi):

```yaml
permissions:
  contents: read
  pull-requests: read   # ← none → read = KO'TARISH
```

Repo sozlamasi ham buni tasdiqlaydi:

```
gh api repos/menarzullayev/rankwant/actions/permissions/workflow
→ {"default_workflow_permissions":"read"}
```

`pull-requests: read` `ci.yml` da **bejiz emas** — `dorny/paths-filter`
PR'dagi o'zgargan fayllarni GitHub API'dan oladi (fayldagi izoh shuni
aytadi). Ya'ni ruxsatni olib tashlash mumkin emas — **chaqiruvchiga
qo'shish** kerak.

**Tuzatish (1 qator):** `deploy.yml` → `permissions:` blokiga qo'shing:

```yaml
permissions:
  contents: read
  actions: read
  pull-requests: read   # ci.yml shuni so'raydi (dorny/paths-filter)
```

Muqobil (torroq): faqat chaqiruvchi job'ga qo'yish —

```yaml
  test:
    name: Test — CI to'plami
    needs: build
    permissions:
      contents: read
      pull-requests: read
    uses: ./.github/workflows/ci.yml
```

**Tekshirish:** push → `gh run list --workflow=deploy.yml --limit 1`.
`startup_failure` o'rniga job'lar paydo bo'lishi kerak (`queued` bo'lsa ham
— bu allaqachon tuzatilganini bildiradi, chunki 0 job ≠ queued).

⚠️ Ikkilamchi nomzod (agar yuqoridagisi yordamasa): `deploy` job'idagi
`environment: name: ${{ github.event.inputs.environment || 'staging' }}`.
Tekshirish uchun vaqtincha `environment` blokini olib tashlab ko'ring.

---

## 4. Sabab 3 — Workflow'lar Linux-ga qattiq bog'langan

Bu **hozir** ishlamaydi degani emas — runner oflayn bo'lgani uchun bu
qatlam hali sinalmagan. Lekin **Windows'da native runner (B varianti)
qo'yilsa**, quyidagilarning har biri yoriladi:

| # | Nima | Nega Windows'da yoriladi | Tuzatish |
|---|---|---|---|
| 1 | `run:` bloklaridagi bash sintaksisi | Windows'da `run:` ning standart shell'i **`pwsh`** (PowerShell Core), Linux'da `bash -e`. `if [ -f x ]`, `$(id -u)`, `$PWD`, heredoc (`<<EOF`), `test -z` — PowerShell'da yo'q | `defaults: run: {shell: bash}` yoki har `run:` ga `shell: bash` (Git Bash bor). Yoki PowerShell'ga ko'chirish |
| 2 | `python3 tools/check_docs.py` | Windows'da `python3` **yo'q** — `actions/setup-python` `python.exe` qo'yadi | `python` yozilsin (yoki `py -3`) |
| 3 | `services: postgres / redis` | Windows runner'da **konteyner operatsiyalari qo'llab-quvvatlanmaydi** (Linux-only) | Linux runner (A varianti), yoki `docker run` bilan qo'lda ko'tarish |
| 4 | `docker run --user "$(id -u):$(id -g)"` | Windows'da UID/GID tushunchasi yo'q (Docker Desktop mapping qilmaydi) | `--user` ni olib tashlash |
| 5 | `-v "$PWD/tests/e2e:/e2e"` | Git Bash yo'lni MSYS uslubida o'giradi → Docker "path not found" | `MSYS_NO_PATHCONV=1` + Windows yo'l, yoki `${RUNNER_TEMP}` |
| 6 | `/tmp/schema.yml` (openapi job) | Windows'da `/tmp` = `C:\tmp`; Git Bash vositalari boshqa joyni ko'radi | `${RUNNER_TEMP}` |
| 7 | `systemctl start cloudflared` | Windows'da `systemctl` yo'q; cloudflared bu mashinada **xizmat emas** — scheduled task | Mavjud `RankWant Tunnel Monitor` vazifasi yoki `tools/handoff.ps1` |
| 8 | CRLF (`ruff format --check`, `gofmt -l`, `diff -u openapi/schema.yml`) | Windows checkout CRLF yozadi → "format buzilgan" yolg'on xatosi | `.gitattributes`: `* text=auto eol=lf` |
| 9 | `docker compose` | Docker Desktop + **Linux engine** shart; WSL integratsiyasi yoqilgan bo'lishi kerak | Docker Desktop sozlamasi |
| 10 | `$GITHUB_OUTPUT` ga `>>` bilan yozish | bash'da ishlaydi; PowerShell'da `$env:GITHUB_OUTPUT` | `shell: bash` bilan o'zi hal bo'ladi |

**Xulosa:** B varianti (native Windows runner) tanlansa, `ci.yml` +
`deploy.yml` + `nightly.yml` + `security.yml` — **to'rtalasi** qayta
yozilishi kerak. A varianti (WSL2 Linux runner) tanlansa — **hech biri**.

---

## 5. Yon topilma — pre-push hook o'rnatilmagan

```
git config core.hooksPath  →  (bo'sh)
```

`.githooks/pre-push` — to'liq lokal darvoza (ruff, ruff format, mypy,
pytest, typecheck, i18n, kontrast, OpenAPI schema diff). Lekin
`core.hooksPath` o'rnatilmagan → **u hech qachon ishlamaydi**.

Ya'ni "push'dan oldin tekshiriladi" degan himoya qatlami **e'lon qilingan,
lekin jonsiz**. CI yagona darvoza bo'lib qolgan — u esa oflayn.

**Tuzatish:**

```bash
git config core.hooksPath .githooks
```

Qo'shimcha: hook ichida `python3 tools/check_i18n.py` bor (§4/2 — Windows'da
`python3` yo'q). Git Bash'da u WorkBuddy'ning managed Python'i tufayli
topiladi, oddiy Windows muhitida topilmaydi → `python` ga o'zgartirilsin.

---

## 6. Tavsiya etilgan tartib

| Qadam | Amal | Fayl | Xavf |
|---|---|---|---|
| 1 | `deploy.yml` ga `pull-requests: read` | `.github/workflows/deploy.yml` | Yo'q (1 qator) |
| 2 | Runner'ni qaytarish (WSL2 Linux + `systemd=true`) | mashina | O'rtacha |
| 3 | Label qo'shish: `runs-on: [self-hosted, rankwant, linux]` | 4 workflow | Yo'q |
| 4 | `git config core.hooksPath .githooks` + hook'da `python3`→`python` | lokal config, `.githooks/pre-push` | Yo'q |
| 5 | `.gitattributes` `* text=auto eol=lf` | repo | Past (bir marta `git add --renormalize`) |
| 6 | (Agar B varianti tanlansa) §4 jadvalidagi 10 ta nuqta | 4 workflow | Yuqori |

1–2-qadamdan keyin CI yana haqiqiy natija bera boshlaydi. 3-qadamsiz
kelajakda Windows runner tasodifan Linux job'ini olib, tushunarsiz xato
beradi.

---

## 7. Boshqa sessiya bilan to'qnashuv — tekshirildi

**Ha, boshqa sessiya hozir ishlayapti.** Dalillar:

```
docker ps → rankwant-web-1   Up 28 seconds
            rankwant-api-1   Up 28 seconds (healthy)
            rankwant-worker-1 Up 28 seconds
            rankwant-beat-1  Up 28 seconds
            (postgres/redis 9 soat, judge 11 soat — qayta qurilmagan)

git status --short → 18 modified + 3 yangi fayl
  ?? apps/api/core/prefs.py
  ?? apps/api/core/migrations/0016_ui_prefs_v2.py
  ?? apps/api/tests/test_prefs.py
  M  apps/web/src/i18n/locales/{10 til}.ts
```

Ya'ni kimdir `ui_prefs_v2` ustida ishlayapti va hozir web/api/worker/beat
qayta qurilgan.

**Men nima qildim:** faqat o'qish — `git status/log`, `gh api`, `docker ps`.
`rankwant/` ichida **bitta fayl ham o'zgartirilmadi**.

**Nima qilsa to'qnashardi:**

| Amal | Nima buziladi |
|---|---|
| `bash tools/ci-local.sh` | Docker build — boshqa sessiya build'i bilan navbat/kesh to'qnashadi |
| `docker compose ... up/down` | `down -v` **jonli bazani o'chiradi**; `up --build` ularning konteynerlarini almashtiradi |
| `git commit` / `push` | Ularning tugallanmagan o'zgarishlari commit'ga tushib ketadi; push CI runini ochib, `cancel-in-progress` bilan ularnikini bekor qiladi |
| `tools/handoff.ps1` | Tunnelni ikkinchi marta ko'taradi (PID fayli almashadi) |
| `check_deploy.sh` | Faqat o'qiydi — xavfsiz, lekin hozir "eskirgan" deydi (ular qayta qurmoqda) |

**Xulosa:** bu sessiyada faqat tahlil qilindi. Tuzatishlarni qo'llash
(keyingi qadam) **boshqa sessiya ishini tugatgandan keyin** yoki alohida
`git worktree` / branch'da bajarilishi kerak — ayniqsa 1 va 4-qadam, chunki
ular `main` ga push qilishni talab qiladi va CI runini ochadi.
