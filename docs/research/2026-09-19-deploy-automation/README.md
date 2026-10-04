# Deploy'ni avtomatlashtirish — taklif

> **Arxiv yozuvi.** Repoga 2026-10-04 da ko'chirildi; matn yozilgan kunidagi holatni aks ettiradi. Taklif: amalda B varianti (host watcher) qurildi; matndagi GitHub Actions tavsiyasi va SHA teg rejasi eskirgan (SHA teglar 2026-09-20 da bekor qilingan).

**Sana:** 2026-09-19 · **Repo:** `rankwant` · **Holat:** taklif, qaror kutilmoqda

---

## 0. Qisqa javob

**Avtomatik deploy — bu trigger'ni almashtirish emas, zanjirni to'ldirish.**
`deploy.yml` ni `workflow_dispatch` dan `push` ga o'tkazish bir qatorda bajariladi,
lekin bugun u **buzuq deploy** beradi: workflow'da migratsiya qadami yo'q,
`check_deploy.sh` tasdiqi yo'q, rollback yo'q, sirlar umuman qo'yilmagan.

Taklif uch qismdan iborat:

| # | Qism | Nima qilinadi |
|---|------|---------------|
| 1 | **Bitta implementatsiya** | Deploy qadamlari YAML'da **takrorlanmaydi** — `tools/deploy.sh --yes` chaqiriladi. Xuddi `ci.yml` `workflow_call` bilan qayta ishlatilgani kabi. |
| 2 | **Zanjirni to'ldirish** | Migratsiyadan oldin zaxira · SHA teg (rollback uchun) · `tools/rollback.sh` · kuchaytirilgan oyna tekshiruvi · deploy muzlatish kaliti. |
| 3 | **Trigger** | `workflow_run` — `CI` `main` da `success` bilan tugagach. `push` emas: CI ikki marta yugurmasin, tartib kafolatli bo'lsin. |

⚠️ **Asosiy ogohlantirish:** avtomatik rollback'siz avtomatik deploy — bu **yaxshilanish emas, pasayish**.
Qo'lda deploy'da odam xatoni ko'radi va to'xtatadi; avtomatikda buni faqat kod qiladi.
Shu sababli 1 va 2-qism **trigger'dan oldin** bajarilishi shart.

---

## 1. Hozirgi holat — o'lchangan (2026-09-19)

### 1.1 Jonli sayt `main` dan orqada

| Nima | Qiymat |
|---|---|
| Jonli `git-sha` (`api`, `web`, `judge`) | `74929e80ad62facad30741029740d413201fbf04` |
| Jonli build vaqti | `2026-09-18T22:35:28Z` |
| GitHub `main` (`origin/main`) | `28aacb9` |
| **Orqada qolgan commit** | **4 ta** — `6486cd6`, `a870741`, `3bcf66a`, `28aacb9` |

Ya'ni `#106`, `#107`, `#108`, `#109` merge bo'lgan, lekin **saytda yo'q**.
Sayt 200 qaytaradi, chunki u **ishlayapti** — shunchaki eski kod bilan.
Buni faqat `bash tools/check_deploy.sh` ko'rsatadi.

**Bu — avtomatlashtirishning eng kuchli dalili:** qo'lda qadam bir kunda 4 ta commit
hajmida yig'ilib qoladi va hech qanday signal bermaydi.

### 1.2 GitHub tomonidagi sozlamalar — bo'sh

| Tekshiruv | Buyruq | Natija |
|---|---|---|
| Environment'lar | `gh api repos/:owner/:repo/environments --jq .total_count` | **`0`** |
| Variable'lar | `gh variable list` | **bo'sh** |
| Secret'lar | `gh secret list` | **bo'sh** |
| `main` himoyasi | `gh api .../branches/main/protection` | **404 — himoyalanmagan** |

Natijasi: `deploy.yml` dagi `deploy` job har doim `skipped` — sharti
`vars.PUBLIC_ORIGIN != ''`, qiymat esa yo'q.

### 1.3 Runner — topologiya to'sig'i YOPILDI

| Runner | Holat | Teglar |
|---|---|---|
| `runner-1` | online | `self-hosted, Linux, X64, rankwant, rankwant-container` |
| `runner-2` | online | `self-hosted, Linux, X64, rankwant, rankwant-container` |

Ikkisi ham **jonli stack bilan bir Docker engine'ida** (`docker ps` da
`rankwant-ci-runner` yonma-yon turadi). Ya'ni 2026-09-16 dagi «job o'z stack'ini
boshqa engine'da ko'taradi» to'sig'i **endi yo'q** — bu avtomatlashtirishning
old sharti bajarildi.

⚠️ Ikki runner borligi degani: `concurrency` guruhi va `deploy.sh` dagi fayl qulfi
**majburiy** — aks holda ikki deploy bir vaqtda ketadi.

### 1.4 Zaxira — 2 kunlik, migratsiyadan oldin emas

| Nima | Qiymat |
|---|---|
| Vazifa | `RankWant Monthly Backup` — **Ready** (oyiga 1 marta, `KEEP=95`) |
| Oxirgi nusxa | `pg-20260917-203248.sql.gz` (17.2 MB), `minio-20260917-203248.tar.gz` (7.6 MB) |
| Sana | **2026-09-17 20:32** — ya'ni 2 kun oldin |
| `nightly.yml` da zaxira job'i | **yo'q** (cron `0 2 * * *`; job'lar: `load`, `e2e`, `chaos`, `compatibility`) |

**Cheklov:** avtomatik deploy istalgan paytda migratsiya yuboradi, zaxira esa
oyiga bir marta olinadi. Migratsiya buzsa — 30 kungacha orqaga qaytish kerak bo'ladi.

### 1.5 Rollback — mavjud emas

`deploy.yml` oxirida shunday izoh bor:

```
# `down` is ABSENT ON PURPOSE: this is the live stack — tearing
# it down would take the site down. Use the rollback job if needed.
```

`grep -rn "rollback" .github/ tools/` → **faqat 2 ta izoh qatori**, **job yo'q**.
Izoh mavjud bo'lmagan narsaga ishora qiladi — bu jimgina chalg'itadigan yolg'on.

### 1.6 🔴 Uchta yangi to'siq — runner tomonida o'lchandi

Bular taklif yozilgandan **keyin** o'lchandi va rejani o'zgartiradi.

**(a) Runner jonli `.env.public` ni ko'rmaydi.** Ikkala runner ham `/work`
Docker volume'ida ishlaydi; host repo (`<repo>`)
konteynerga ulanmagan:

```
$ docker inspect rankwant-ci-runner-2 --format '{{range .Mounts}}{{.Source}} -> {{.Destination}}{{"\n"}}{{end}}'
/var/lib/docker/volumes/rankwant-ci-work-2/_data -> /work (rw)
<host>/ci-runner-diag-2 -> /home/runner/_diag (rw)
/var/run/docker.sock -> /var/run/docker.sock (rw)
```

`/run/desktop/mnt/host/c/` ham ochilmagan:

```
$ docker exec rankwant-ci-runner-2 bash -lc 'ls /run/desktop/mnt/host/c/'
ls: cannot access '/run/desktop/mnt/host/c/': No such file or directory
```

**(b) `.env.public` da 29 kalit bor, workflow esa 4 tasini yozadi.**

```
$ grep -o '^[A-Z_]*=' .env.public | tr -d '=' | wc -l
29
```

Workflow'ning Configuration qadami faqat `DJANGO_SECRET_KEY`,
`DJANGO_ALLOWED_HOSTS`, `PUBLIC_ORIGIN` (+ `NEXT_PUBLIC_API_BASE`) yozadi.
`up` jonli konteynerlarni **runner'ning env-fayli** bilan qayta yaratadi ⇒
email zanjiri (Mailjet · Brevo · Resend · MailerSend), Turnstile, Cloudflare
token, Google/GitHub/Telegram OAuth va `THROTTLE_REGISTER` **jimgina yo'qoladi**.

**(c) Runner'da `gh` yo'q.** `check_deploy_gate.py` `gh run list` ni chaqiradi:

```
$ docker exec rankwant-ci-runner-2 bash -lc 'command -v gh || echo "gh YOQ"'
gh YOQ
```

Ya'ni workflow ichida `tools/deploy.sh` chaqirilsa, darvoza **har doim**
`exit 2` beradi va deploy to'xtaydi. (Ikkala runner'da ham yo'q.)

⚠️ **Xulosa:** «trigger'ni yoqish» bu mashinada yetarli emas. Runner'ni qayta
sozlash (bind mount + `gh` o'rnatish) yoki boshqa mexanizm kerak — §2.2.

---

## 2. Vositalar — qaysi mos, qaysi mos emas

| Yondashuv | Vosita | Bahosi |
|---|---|---|
| **A. GitHub Actions `workflow_run` + `tools/deploy.sh`** | mavjud stek | ✅ **TAVSIYA.** Runner bor, `ci.yml` bor, `deploy.sh` allaqachon `--yes` bayrog'ini avtomatlashtirish uchun yozgan. Yangi infratuzilma kerak emas. |
| B. Watchtower (yangi obrazni avtomatik tortib ko'tarish) | Docker | ❌ **MOS EMAS.** Migratsiya qilmaydi, `NEXT_PUBLIC_*` build vaqtida singadi (qayta qurish kerak), oyna darvozasi yo'q. Loyiha allaqachon yozib qo'ygan ikki xato rejimini aynan takrorlaydi. |
| C. GitOps (Argo CD / Flux) | Kubernetes | ❌ **MOS EMAS.** Bitta mashina + Compose uchun ortiqcha og'irlik; foyda nol. |
| D. Webhook + kichik listener (`deploy.sh` ni GitHub webhook orqali chaqirish) | custom | ⚠️ **KERAKSIZ.** Actions va runner allaqachon bor; yangi xizmat = yangi nosozlik nuqtasi. |
| E. Cron + `git pull && bash tools/deploy.sh --yes` (Windows Task Scheduler) | mavjud | ⚠️ **ZAXIRA VARIANT.** Eng sodda, lekin CI darvozasi va concurrency yo'q. Actions ishlamay qolsa — shu yo'l. Baribir `deploy.sh` ga tayanadi. |
| F. `docker compose up --build` (systemd timer) | Docker | ❌ Migratsiya, tasdiq va oyna tekshiruvi yo'q — bugungi `deploy.yml` ning xatosi. |

**Xulosa:** yangi vosita kerak emas. Mavjud `tools/deploy.sh` — yagona haqiqat manbai,
Actions esa uni **chaqiruvchi**. Ikki nusxa bo'lmasin — bu loyihaning allaqachon
qabul qilgan tamoyili (`ci.yml` `workflow_call` bilan shunday qilingan).

### 2.2 Mexanizm tanlovi — Actions yoki host watcher?

Ega **«to'liq avtomatik»** ni tanladi (2026-09-19). Mexanizm esa o'lchovga qarab
tanlanadi — §1.6 dagi uchta to'siqdan keyin:

| | A. GitHub Actions (`workflow_run`) | B. **Host watcher** (Task Scheduler) |
|---|---|---|
| Jonli `.env.public` | ❌ ko'rinmaydi — 29 kalitni GitHub'ga ko'chirish yoki bind mount kerak | ✅ o'sha faylning o'zi |
| Darvoza (`gh`) | ❌ runner'da `gh` yo'q | ✅ host'da bor |
| Tunnel (Windows) | ❌ `systemd` yo'q | ✅ `handoff.ps1` / `monitor.ps1` ni chaqira oladi |
| Yangi GitHub sozlamasi | environment + 1 secret + 3 variable | **kerak emas** |
| CI darvozasi | `workflow_run` bilan tabiiy | `check_deploy_gate.py` bilan |
| Registratsiya | runner'ni qayta qurish | mavjud naqsh |

Mavjud registratsiya naqshi o'lchandi:

```
RankWant Tunnel Monitor :: MSFT_TaskDailyTrigger ::
  conhost.exe --headless "C:\Program Files\Git\bin\bash.exe"
  -lc "powershell.exe -NoProfile -ExecutionPolicy Bypass -File ...\tools\monitor.ps1"
  last=09/19/2026 05:20:00 result=0
```

⇒ **Tavsiya: B (host watcher).** Sabab: bu mashinaning topologiyasida u
**o'lchangan ishlaydigan** qismlardan yig'iladi (`deploy.sh`, `gh`, `.env.public`,
`docker`, Task Scheduler), Actions yo'li esa runner'ni qayta qurishni va 29 kalitni
GitHub'ga ko'chirishni talab qiladi — ya'ni **ikkinchi haqiqat manbai** paydo bo'ladi.
Loyiha bu saboqni allaqachon yozgan (`backup.sh` izohi: ikki nusxa jimgina ajralib
ketadi — `runner-keepalive.ps1` va `runner_keepalive.ps1` bilan bir marta shunday bo'lgan).

⚠️ Host watcher'ning o'z cheklovi: **mashina o'chiq bo'lsa deploy ham to'xtaydi.**
Lekin bu mashinada jonli stack ham, runner ham, tunnel ham o'sha mashinada — farq yo'q.


### 2.1 Nega bugungi `deploy.yml` ni yoqish yetarli emas

Workflow'dagi `deploy` job bilan `tools/deploy.sh` ni yonma-yon qo'ysak:

| Qadam | `deploy.yml` (deploy job) | `tools/deploy.sh` |
|---|---|---|
| Build | `api web judge` | `api worker beat judge web **migrate**` |
| Migratsiya | ❌ **yo'q** | ✅ `migrate` → keyin `showmigrations` tasdiqi |
| Ko'tarish | `up -d --build --wait` | `up -d --no-deps` (qurilgan obrazdan) |
| Kod joriyligi tasdiqi | ❌ **yo'q** | ✅ `check_deploy.sh` |
| Qulf | faqat `concurrency` | ✅ fayl qulfi (barcha worktree'lar bo'ylab) |

Ya'ni workflow **kuchsizroq**: u migratsiyasiz ko'taradi (sxema orqada qoladi) va
«deploy tugadi» deb yashil beradi, konteyner esa eski kodda bo'lishi mumkin.
Bugun uni yoqish — 2026-09-16 dagi xatoni takrorlash.

---

## 3. Shartlar — to'siqlar va ularning holati

| # | To'siq | Holat (2026-09-19) | Yechim |
|---|---|---|---|
| 1 | Runner jonli engine'da emas | ✅ **Yopildi** (2026-09-17) | — |
| 2 | Workflow'da migratsiya qadami yo'q | 🔴 **Ochiq** | `tools/deploy.sh --yes` chaqirish |
| 3 | Environment himoyasi yo'q (`environments = 0`) | 🔴 **Ochiq** | `production` environment yaratish |
| 4 | Secret/variable yo'q (1 secret + 3 variable) | 🔴 **Ochiq** | `DJANGO_SECRET_KEY` (secret); `DJANGO_ALLOWED_HOSTS`, `PUBLIC_ORIGIN`, `NEXT_PUBLIC_API_BASE` (variable) |
| 5 | Rollback job yo'q (izoh uni «bor» deb ko'rsatadi) | 🔴 **Ochiq** | `tools/rollback.sh` + job |
| 6 | Migratsiyadan oldin zaxira olinmaydi | 🔴 **Ochiq** (topildi shu sessiyada) | `deploy.sh` ga `pg_dump` qadami |
| 7 | SHA teg rollback uchun yetarli emas | 🔴 **Ochiq** | `deploy.sh` da `rankwant/<svc>:<sha12>` teg |
| 8 | Muzlatish kaliti yo'q | 🔴 **Ochiq** | `DEPLOY_FREEZE` variable |
| 9 | Oyna «aniqlanmadi» (exit 2) — qo'lda rejimda ogohlantiradi | ⚠️ **Qayta ko'rilishi kerak** | §5.3 |

---

## 4. Qadamlar zanjiri — avtomatik, tartib bilan

### 4.1 Trigger — host watcher (tavsiya etilgan mexanizm)

```powershell
# RankWant Auto Deploy — har 5 daqiqada (RankWant Tunnel Monitor bilan bir naqsh)
conhost.exe --headless "C:\Program Files\Git\bin\bash.exe" -lc
  "tools/auto_deploy.sh >> <logs>\auto-deploy.log 2>&1"
```

`tools/auto_deploy.sh` — yupqa qobiq, hamma og'ir ish `deploy.sh` da:

1. **Qulf** — band bo'lsa chiqadi (0 bilan), chalg'itmaydi.
2. `git -C <deploy worktree> fetch origin main`
3. `HEAD == origin/main` → **ish yo'q, chiqadi**. (Har 5 daqiqada `fetch`, lekin
   deploy faqat o'zgarish bo'lganda.)
4. `tools/check_deploy_gate.py` — main CI + `Security` yashil, dirty compose yo'q
5. `DEPLOY_FREEZE` → to'xta
6. `tools/deploy.sh --yes` — qolgan hammasi

⚠️ **Deploy alohida worktree'da** (`<deploy worktree>`), asosiy
checkout'da emas: aks holda agentning commit qilinmagan tahriri jimgina build'ga
tushadi. `deploy.sh` ga `RANKWANT_ENV_FILE` qo'llab-quvvatlashi kerak — env-fayl
asosiy checkout'da qoladi (29 kalit), kod esa worktree'dan quriladi.

**Nega Actions emas:** §2.2 va §1.6 — runner jonli `.env.public` ni ko'rmaydi va
unda `gh` yo'q. Actions'ni ishlatish uchun runner'ni qayta qurish va 29 kalitni
GitHub'ga ko'chirish kerak bo'lardi.


### 4.2 Zanjir

```
   CI (main) tugadi
        │
        ├── success emas ──► [A] Ogohlantirish job: «main qizil — deploy to'xtadi»
        │                        (jim qolmasin: 2026-09-18 da 3 ta PR shu sabab
        │                         soatlab jonli chiqmagan)
        │
        └── success ─────────► [B] Deploy job
                                    │
   1. Deploy muzlatish kaliti ──────┤ DEPLOY_FREEZE=1 → TO'XTA
   2. Deploy darvozasi ─────────────┤ check_deploy_gate.py
        HEAD == origin/main, `CI` + `Security` yashil,
        hech bir checkout'da commit qilinmagan compose yo'q
   3. Live contest oynasi ──────────┤ check_deploy_window.py
        exit 1 → TO'XTA (qoida №1) · exit 2 → §5.3 ga qarang
   4. tools/deploy.sh --yes ────────┤
        a. qulf (barcha worktree'lar bo'ylab)
        b. old shartlar (docker, .env.public)
        c. build: api worker beat judge web migrate
        d. ── YANGI: migratsiyadan oldin pg_dump ──
        e. migrate  →  showmigrations == 0 tasdiqi
        f. ── YANGI: SHA teg (rollback uchun) ──
        g. up -d --no-deps api worker beat judge web
        h. check_deploy.sh → «Hamma konteyner joriy kodda»
   5. Health ───────────────────────┤ 30 × 5 s, 127.0.0.1:8301 (Host sarlavhasi bilan)
   6. Smoke ────────────────────────┤ submit → Redis → judge → verdict
   7. Tashqi tekshiruv ─────────────┤ https://rankwant.uz/ → 200
   8. ── YANGI: tasdiq yiqilsa ─────► [C] Rollback job (oldingi SHA)
   9. Xulosa + eski obrazlarni tozalash
```

### 4.3 Har bir to'xtatish nuqtasi — ataylab

| Nuqta | To'xtasa nima bo'ladi | Nega shunday |
|---|---|---|
| Muzlatish | Deploy umuman boshlanmaydi | Ega contest paytida bir so'z bilan to'xtata olsin — workflow tahrirlamasdan |
| Darvoza | Deploy boshlanmaydi | Faqat `main` + yashil CI. Merge ≠ deploy ≠ sayt yangilandi |
| Oyna (exit 1) | Deploy boshlanmaydi | Qoida №1: verdict/standings o'zgarishi musobaqa natijasini buzadi |
| `migrate` | `up` gacha to'xtaydi | Sxema orqada qolgan stack — jimgina buzilgan sayt |
| `showmigrations != 0` | `up` gacha to'xtaydi | `migrate` chiqishiga ishonib bo'lmaydi (eski obraz ham «No migrations» deydi) |
| `check_deploy.sh` | Deploy **muvaffaqiyatsiz** hisoblanadi | «Yashil» ning yagona haqiqiy tasdiqi |
| Tashqi tekshiruv | Rollback ishga tushadi | Sayt ochilmasa — deploy foydasiz |

---

## 5. Cheklovlar va xavflar

### 5.1 Tunnel — runner uni boshqara olmaydi 🔴

`deploy.yml` dagi Tunnel qadami buni allaqachon tan olgan: konteyner runner'da
`systemd` **yo'q**, tunnel esa Windows tomonida `tools/handoff.ps1` +
`RankWant Tunnel Monitor` vazifasi bilan boshqariladi (PID fayli orqali).

**Natija:** avtomatik deploy tashqi ochilishni **kafolatlay olmaydi**.
U faqat `https://rankwant.uz/` ni tekshirib, ochilmasa ogohlantira oladi.
Tunnelni tiklash — `RankWant Tunnel Monitor` ning ishi (u har 5 daqiqada yuradi).

### 5.2 `NEXT_PUBLIC_*` build vaqtida singadi 🔴

`web` obrazini **qayta qurish** shart, `restart` yaramaydi. `deploy.sh` `web` ni
`SERVICES` ro'yxatiga allaqachon kiritgan — avtomatik yo'l ham **aynan shu skriptni**
chaqirgani uchun bu tuzoq qaytmaydi.

### 5.3 Oyna tekshiruvi «aniqlanmadi» (exit 2) — qayta ko'rish kerak ⚠️

Bugungi mantiq (`check_deploy_window.py`):

- `exit 0` — oyna bo'sh
- `exit 1` — faol contest → **taqiqlanadi**
- `exit 2` — API javob bermadi → `deploy.sh` **ogohlantiradi va davom etadi**

Bu qaror **qo'lda** rejim uchun to'g'ri: odam o'tiribdi, u tasdiqlaydi.
Avtomatik rejimda odam yo'q — ya'ni `exit 2` **jimgina** «davom et» ga aylanadi.

Muammo: tekshiruv `https://rankwant.uz/api/v1` ga uradi, sayt yiqilgan bo'lsa javob
yo'q → `exit 2` → va aynan o'sha paytda tuzatish deploy'i **eng kerak**.
Lekin contest paytida API beqaror bo'lsa ham `exit 2` bo'ladi va deploy o'tib ketadi.

**Taklif:** tekshiruvga **lokal origin zaxirasini** qo'shish. Tashqi manzil javob
bermasa — `http://127.0.0.1:8301/api/v1/` ni `Host: rankwant.uz` sarlavhasi bilan
so'rash (bu ishlashi o'lchangan). Uch holat:

1. Tashqi javob berdi → javob haqiqiy.
2. Tashqi yo'q, **lokal javob berdi** → javob haqiqiy (tunnel muammosi, deploy emas).
3. Ikkisi ham yo'q → stack yiqilgan → **deploy davom etadi** (u tuzatish).

Ya'ni `exit 2` faqat «stack butunlay yiqilgan» holatida qoladi — va o'shanda davom
etish **to'g'ri**. Boshqa hollarda oyna haqiqatan o'lchanadi.

### 5.4 Qolgan cheklovlar

| # | Cheklov | Ta'siri |
|---|---|---|
| 1 | **Bitta mashina** — hammasi bitta Docker engine'da | Avtomatik deploy = avtomatik nosozlik. Rollback majburiy |
| 2 | **Ikki agent bir mashinada** | Fayl qulfi (`<git common dir>/rankwant-deploy.lock`) — CI va qo'lda deploy to'qnashmasin |
| 3 | **`concurrency` faqat Actions ichida** | Qo'lda `deploy.sh` ni ushlamaydi — shu sabab fayl qulfi kerak |
| 4 | **Runner queue** — 2 runner, lekin bitta mashina | Uzoq `nightly` yugurishi deploy'ni navbatda ushlab turishi mumkin |
| 5 | **Disk** | Har deploy yangi obraz quradi. Tozalash bor, lekin `docker builder prune` butun engine bo'ylab — jonli kesh ham nomzod |
| 6 | **`staging` mavjud emas** | `deploy.yml` da `staging` tanlovi bor, lekin alohida staging stack **yo'q**. Amalda u faqat «`seed_demo` ni yugurtma» degani |
| 7 | **`main` himoyalanmagan** | 404 — ya'ni `main` ga to'g'ridan-to'g'ri push mumkin. Avtomatik deploy sharoitida bu xavf: tekshirilmagan commit jonli chiqadi |
| 8 | **Zaxira oyiga 1 marta** | Migratsiya buzsa — 30 kungacha yo'qotish |

---

## 6. Bajarish rejasi (ega qarori: to'liq avtomatik)

⚠️ Ega **to'liq avtomatik** ni tanladi. Lekin «rollback keyinroq qo'shiladi» degani
«rollback kerak emas» degani emas: **birinchi avtomatik deploy rollback va
migratsiya zaxirasisiz ketmasligi kerak.** Shuning uchun tartib shunday —
rollback va zaxira **birinchi PR'da**, trigger **ikkinchisida**.

### PR 1 — zanjirni to'ldirish (trigger hali qo'lda qoladi)

| # | Ish | Fayl |
|---|---|---|
| 1 | Migratsiyadan oldin `pg_dump` qadami | `tools/deploy.sh`, `tools/backup.sh` (`--dump-only`) |
| 2 | SHA teg (`rankwant/<svc>:<sha12>`) build'dan keyin | `tools/deploy.sh` |
| 3 | `tools/rollback.sh <sha>` — oldingi tegdan qaytarish | yangi fayl |
| 4 | `DEPLOY_FREEZE` kaliti | `tools/deploy.sh` |
| 5 | `RANKWANT_ENV_FILE` — env-fayl asosiy checkout'da qolsin | `tools/deploy.sh` |
| 6 | Oyna tekshiruviga lokal origin zaxirasi | `tools/check_deploy_window.py` |
| 7 | Qarorni registrga yozish | `CLAUDE.md` |
| 8 | Darvoza + salbiy testlar | `tools/check_decisions.py`, `tools/check_negative.py` |

**Tasdiq:** rollback **ataylab yiqitib** sinovdan o'tkaziladi; `pg_dump` fayli
paydo bo'ladi; `showmigrations` 0 beradi; hamma darvoza yashil.

### PR 2 — trigger

`tools/auto_deploy.sh` + `RankWant Auto Deploy` vazifasi (5 daqiqa, mavjud naqsh).
Deploy worktree: `<deploy worktree>`.

**Tasdiq:** bitta haqiqiy merge → sayt SHA'si `main` bilan teng
(`bash tools/check_deploy.sh`). Va **salbiy test:** `main` yashil bo'lmasa yoki
faol contest bo'lsa — deploy **yugurmasligi**.

### Birinchi haqiqiy deploy

Hozir sayt `74929e8` da, `main` esa `28aacb9` — ya'ni **4 commit orqada**.
Trigger yoqilgach birinchi deploy aynan shu 4 commitni olib keladi.

---

## 7. Qaror — yozib qo'yildi

**Ega qarori (2026-09-19): «To'g'ridan-to'g'ri to'liq avtomatik».**
Variantlar orasidan eng tez yo'l tanlandi: `required reviewer` **qo'yilmaydi**,
ya'ni merge → sayt.

Oqibatlari — yozib qo'yiladi, chunki keyin «nega shunday» degan savol qaytadi:

1. Qoida №1 (live contest) ni endi **faqat kod** ushlaydi —
   `check_deploy_window.py`. Odam ko'z bilan tekshirmaydi.
2. Rollback va migratsiya zaxirasi **birinchi PR'da** qo'shilishi shart (§6),
   aks holda birinchi nosozlikda orqaga yo'l qolmaydi.
3. Host watcher yo'lida GitHub `environment` **umuman kerak emas** — ya'ni
   `environments = 0` to'sig'i o'z-o'zidan yo'qoladi.


---

## 8. Foydalanilgan dalillar

| Tekshiruv | Buyruq |
|---|---|
| Environment soni | `gh api repos/:owner/:repo/environments --jq .total_count` → `0` |
| Variable / secret | `gh variable list`, `gh secret list` → bo'sh |
| `main` himoyasi | `gh api repos/:owner/:repo/branches/main/protection` → 404 |
| Jonli SHA | `docker inspect rankwant-api-1 --format '{{index .Config.Labels "org.rankwant.git-sha"}}'` |
| Runner'lar | `gh api repos/:owner/:repo/actions/runners` |
| Oxirgi zaxira | `Get-ChildItem $env:USERPROFILE\backups\rankwant` |
| Rollback izlari | `grep -rn "rollback" .github/ tools/` |
| Zaxira jadvali | `Get-ScheduledTask` → `RankWant Monthly Backup` = Ready |
