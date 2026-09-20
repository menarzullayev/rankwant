# Deploy runbook

**STATUS:** draft (2026-09-16) — production tajribasidan yozildi.  
[README](README.md) dagi "runbook'lar production tajribasidan keyin" bandi  
shu fayl bilan yopiladi.

⚠️ Bu hujjat **bitta mashinadagi preview** uchun (`rankwant.uz`, Cloudflare  
Tunnel orqali). To'rt hostli production topologiyasi README'da.

---

## 0. Tezkor kartochka

| Narsa           | Qiymat                                                          |
| --------------- | --------------------------------------------------------------- |
| Loyiha prefiksi | `-p rankwant`                                                   |
| Compose fayllar | `-f docker-compose.yml -f docker-compose.public.yml`            |
| Env fayl        | `--env-file .env.public`                                        |
| Web             | **8300**                                                        |
| API             | **8301**                                                        |
| Tunnel          | `tools/monitor.ps1`, PID `.handoff/cloudflared.pid`             |
| Zaxira          | `"C:\Program Files\Git\bin\bash.exe" -lc ".../tools/backup.sh"` |
| Avtomatik deploy | `tools/auto_deploy.sh`, vazifa `RankWant Auto Deploy` (1 daqiqa) |
| Muzlatish kaliti | `DEPLOY_FREEZE=1` — deploy'ni to'xtatadi (qulfni ham olmaydi)   |
| Rollback        | kerakli commitni `deploy.sh` bilan qayta qurish (SHA teg saqlanmaydi) |
| O'lchov         | `tools/measure_deploy.sh` (`--warm` / `--cold`); TIMER qatorlari     |

To'liq `COMPOSE` o'zgaruvchisi (har bo'limda shu ishlatiladi):

```bash
docker compose -p rankwant --env-file .env.public \
  -f docker-compose.yml -f docker-compose.public.yml
```

---

## 1. Deploy tartibi — migration **AVVAL**, alohida qadamda

```bash
# 1. Qurish — `migrate` HAM KIRISIN
$COMPOSE build api worker beat migrate web

# 2. Migration — alohida qadam, deploy'dan OLDIN
$COMPOSE run --rm migrate

# 3. Tekshirish — `migrate` chiqishiga ishonmang
$COMPOSE run --rm api python manage.py showmigrations contests hacks

# 4. Ko'tarish
$COMPOSE up -d --wait

# 5. Ishlab turgan kod manbadan eskimi?
bash tools/check_deploy.sh          # «ESKIRGAN» = hamma servisni qayta qurish
```

### ⚠️ Nega `migrate` alohida

`migrate` — mustaqil compose servisi (`build: ./apps/api`), ya'ni **o'z  
obrazi bor**. Faqat `build api worker beat` qilinsa `migrate` qurilmaydi va  
eski obraz bilan yuradi → yangi migration fayllarini ko'rmaydi.

**Alomat (2026-09-16):** 6 ta migration qo'llanmagan, lekin  
`run --rm migrate` *"No migrations to apply"* deydi. Sabab aynan eski obraz.

✅ **Qoida:** `check_deploy.sh` «ESKIRGAN» ko'rsatsa, faqat api/worker/beat  
emas — **barcha** servisni (migrate ham) qayta quring. Tasdiq faqat  
`showmigrations` orqali.

### 🔴 `git push` = deploy EMAS — deploy qo'lda

`deploy.yml` dagi `deploy` job **doim `skipped`** bo'ladi:

```yaml
if: >-
  ${{
    (github.ref == 'refs/heads/main' || github.event_name == 'workflow_dispatch')
    && vars.PUBLIC_ORIGIN != ''
  }}
```

Repo'da **0 ta variable/secret** bor, ya'ni `vars.PUBLIC_ORIGIN` bo'sh →
shart bajarilmaydi. Bu **ataylab** shunday (izohda yozilgan): sozlanmagan
deploy har push'da qizil X berib, haqiqiy nosozliklarni yashirardi.

⚠️ **Natijasi (2026-09-16 da o'lchandi):** push'dan keyin CI to'liq yashil
bo'ladi, lekin konteynerlar **eski kodda qoladi**. Sayt 200 ko'rsatadi —
chunki u ishlayapti, shunchaki **eski kod bilan**.

Shu sababli `check_deploy.sh` — push'dan keyingi **majburiy** qadam, va
haqiqiy deploy yuqoridagi §1 qadamlarini qo'lda bajarish demakdir.

⚠️ Yana bir tuzoq: push'dagi yugurishning *boshqa* job'i yiqilsa (masalan
`Bake-off — validator case'lari`), `deploy` undan ham oldin o'tkazib
yuboriladi. Yashil CI ≠ deploy bo'lgan.

### ✅ Qaror (2026-09-16): deploy **qo'lda** qoladi

Bu ataylab tanlangan yo'l — «hali sozlanmagan» emas. Sabab **o'lchandi**:

| # | To'siq | Dalil |
| - | ------ | ----- |
| 1 | **CI runner produksiya engine'ida emas** | Jonli stack — Docker Desktop engine'i (A), image `rankwant-api:latest`. Runner — WSL Ubuntu ichidagi alohida engine (B), image `rankwant/api:<sha>`. Ya'ni job o'z stack'ini **B** da ko'taradi: 8300/8301 band → `up` yiqiladi, yoki parallel stack paydo bo'ladi va unga hech kim yo'naltirmagan. |
| 2 | **Workflow'da migration qadami YO'Q** | `deploy.yml` `up -d --build --wait` ni chaqiradi, xolos. Migration'li release'da sxema orqada qolardi (§1 ga zid). |
| 3 | **Environment himoyasi yo'q** | `gh api .../environments` → **0 ta**. Ya'ni required reviewer qo'yilmagan: avtomatik deploy **live contest paytida ham** ketardi — qoida №1 buzilardi. |
| 4 | **Sirlar yo'q** | `DJANGO_SECRET_KEY` (secret) + `DJANGO_ALLOWED_HOSTS`, `PUBLIC_ORIGIN`, `NEXT_PUBLIC_API_BASE` (variable). |

⚠️ Ya'ni job'ni «yoqish» uchun avval 2 va 3-to'siqlar yopilishi shart;
1-to'siq esa **topologiya** masalasi — uni faqat engine'larni
birlashtirish yoki runner'ni A ga ko'chirish hal qiladi.

**Shu sababli qo'lda yo'l birinchi darajali qilib qo'yildi:**

```bash
bash tools/deploy.sh          # interaktiv tasdiq bilan
bash tools/deploy.sh --yes    # tasdiqsiz
bash tools/deploy.sh --check  # hech narsani o'zgartirmaydi
```

`tools/deploy.sh` — §1 tartibining bajariladigan ko'rinishi: old shartlar →
**live oyna tekshiruvi** → `deploy_scope.py` (docs/tools — bake yo'q; judge
faqat `services/judge-go` o'zgaganda) → kerakli obrazlar → migrate (faqat
api doirasida) → `showmigrations` → `up -d --no-deps` → **health** (api/web,
`sleep 10` emas) → `check_deploy.sh`.
Qadamlar tartibi kodda, yodda emas.

Live oyna tekshiruvi alohida tekshiruv: `tools/check_deploy_window.py`
(chiqish 0 — bo'sh, 1 — faol contest bor, **2 — aniqlanmadi**).
⚠️ Uchinchi holat ataylab ajratilgan: «API javob bermadi» ni «0 ta» deb
o'qish yolg'on yashil berardi va aynan sayt yiqilganda — ya'ni tuzatish
deploy'i eng kerak bo'lgan paytda — darvoza eng ishonchsiz bo'lardi.

### Qaror (2026-09-17): agentlar yashil `main` ni deploy qiladi

Agentlar production'ni so'ramasdan deploy qiladi, lekin faqat `main` CI
yashil bo'lsa (`CLAUDE.md` § Saidakbar aka qarorlari). `tools/deploy.sh`
buni o'zi ta'minlaydi — hamma narsadan oldin:

- **Qulf** — `<git common dir>/rankwant-deploy.lock`; barcha worktree'lar
  uni bo'lishadi, ya'ni ikki agent bir vaqtda deploy qila olmaydi. Qulf
  band bo'lsa skript egasini (pid, vaqt, commit) ko'rsatib to'xtaydi.
  Deploy yiqilgan joyda (elektr) qulf qolsa, jarayon yo'qligini tekshirib
  `rm -rf` bilan olib tashlanadi.
- **Darvoza** — `tools/check_deploy_gate.py`: HEAD GitHub'dagi `main` bilan
  bir xil, shu commit'ning oxirgi `CI` va `Security` run'lari `success`, va
  hech bir checkout'da commit qilinmagan `docker-compose*.yml` yo'q
  (chiqish 0 — mumkin, 1 — yo'q, **2 — o'lchanmadi**, deploy baribir to'xtaydi).
  Uchinchi shart 2026-09-17 dagi holatdan keyin qo'shildi: jonli stack asosiy
  checkout'dagi commit qilinmagan compose bilan qayta yaratilgan edi (Turnstile
  kalitlari va yumshatilgan `register` throttle'i o'sha faylda), worktree'dan
  qilinadigan deploy esa commit qilingan compose bilan quradi va ularni jimgina
  olib tashlagan bo'lardi. Darvoza to'xtatsa: o'zgarishni commit qiling (PR) yoki
  qaytaring.
  Darvoza ishlayotgan paytda o'chirilgan worktree o'tkazib yuboriladi: yo'q
  papkada deploy olib tashlaydigan narsa yo'q. 2026-09-18 da boshqa agent
  o'z worktree'sini aynan shu oraliqda o'chirgan va darvoza `exit 2` bergan edi.
  Papka bor-u, git uni o'qiy olmasa, darvoza avvalgidek to'xtaydi.
- `--skip-ci-gate` darvozani o'tkazib yuboradi — faqat Saidakbar akaning
  aniq ruxsati bilan.

### Qaror (2026-09-19): deploy **to'liq avtomatik** — host watcher

Ega qarori (HITL: 1 savol, 4 variant → «to'g'ridan-to'g'ri to'liq avtomatik»,
`required reviewer` **yo'q**). Mexanizm — **host watcher**, GitHub Actions
**emas**, va sabab o'lchandi:

| To'siq | Dalil (2026-09-19) |
| ------ | ------------------ |
| Runner jonli `.env.public` ni ko'rmaydi | runner mount'lari: faqat `/work` volume + `docker.sock` + `_diag`; `/run/desktop/mnt/host/c/` → `No such file or directory` |
| `.env.public` da **29** kalit, workflow **4** tasini yozadi | workflow `up` i jonli konteynerlarni 4 kalitli env-fayl bilan qayta yaratadi ⇒ email zanjiri, Turnstile, Cloudflare token, OAuth, `THROTTLE_REGISTER` **jimgina yo'qoladi** |
| Runner'da `gh` **yo'q** | `command -v gh` → `gh YOQ` (ikkala runner'da) ⇒ `check_deploy_gate.py` har doim `exit 2` |

Shuning uchun `deploy.yml` **qo'lda qoladi** (`workflow_dispatch` +
`confirm: deploy`; `tools/check_decisions.py` → `deploy_manual_only`
o'zgarmaydi). Avtomatlashtirish — host'da, chunki `deploy.sh`, `gh`,
`.env.public`, `docker` va Task Scheduler o'sha yerda va hammasi o'lchangan.

**Zanjir** (har daqiqada, `tools/auto_deploy.sh`):

```
qulf → DEPLOY_FREEZE → git fetch origin main → worktree'ni --ff-only
     → deploy_scope.py (jonli yorliq ↔ origin/main)
        bo'sh + stack tirik → bake yo'q (docs/tools)
     → drift bormi?  (konteynerlar tirikmi + check_deploy.sh)
        yo'q  → JIM chiqadi
        bor   → qayta urinish to'sig'i (30 daqiqa)
              → darvoza OLDINDAN tekshiriladi
                 yopiq → urinish YOZILMAYDI, to'siq ham qo'yilmaydi
              → urinish yoziladi → tools/deploy.sh --yes  (RANKWANT_DEPLOY_SCOPE)
                 qulf → darvoza(main CI) → oyna → tanlangan obraz
                 → (api bo'lsa) pg_dump → migrate → showmigrations
                 → up → health → check_deploy.sh
                 → prune (SHA teglar, dangling, builder)
```

⚠️ **Yopiq darvoza — nosozlik emas, shuning uchun to'siq ham qo'yilmaydi.**
Darvoza `main` CI hali yugurib turganda ham yopiq bo'ladi. O'sha holat
nosozlik deb hisoblansa, SHA 30 daqiqaga bloklanadi: deploy 1 daqiqa o'rniga
30 daqiqada keladi va log yolg'on «deploy YIQILDI» deydi. O'lchandi
2026-09-20 18:10:06Z — PR #192 18:09:36 da merge bo'ldi, CI hali yugurar edi;
CI `main` da ~70 s yuradi, yurish esa har daqiqada, ya'ni deyarli har merge
shu yo'lga tushadi. Endi watcher darvozani **urinishdan oldin**
tekshiradi va yopiq bo'lsa sababini logga yozib chiqadi (jim qolmaydi:
2026-09-18 da 3 ta PR shu sabab soatlab jonli chiqmagan).
`tools/deploy.sh` o'z darvozasini baribir yurgizadi — u yagona haqiqat
manbai, watcher'ning tekshiruvi esa tayyorlik savoli: «hozir urinishga
arziydimi?». `tools/check_decisions.py` → `deploy_automation_is_safe` (8-shart)
shuni qo'riqlaydi.

Merge oxirida watcher poll'ini kutmang (1 daqiqa) — darvoza baribir yashil main:

```bash
bash tools/kick_auto_deploy.sh
# yoki: schtasks /run /tn "RankWant Auto Deploy"
```

### Poll oralig'i — 1 daqiqa (o'lchandi 2026-09-21)

Vazifa har daqiqada yuradi (`PT1M`), ilgari 5 daqiqa edi: merge'dan keyin
deploy eng yomon holatda **1 daqiqada** boshlanadi (ilgari 5 daqiqada).
Umuman kutmaslik kerak bo'lsa — yuqoridagi `kick_auto_deploy.sh`.

⚠️ **30 soniya texnik jihatdan mumkin emas.** Task Scheduler takrorlash
oralig'ining eng kichigi — **1 daqiqa**; `PT30S` ni XML sxemasi rad etadi.
O'lchandi (2026-09-21, ikkala scheduling engine'da ham bir xil):

```text
The task XML contains a value which is incorrectly formatted or out of
range.(31,27):Interval:PT30S
```

⚠️ **Ustma-ust tushish yo'q.** Vazifada `MultipleInstancesPolicy=IgnoreNew`
— oldingi yurish tugamaguncha yangi nusxa ochilmaydi, ya'ni deploy 5
daqiqaga cho'zilsa ham yurishlar to'planib qolmaydi. Tick narxi ~2.0–2.3 s
(asosan `git fetch`), ya'ni 1 daqiqalik poll'da ish yuki ~3.5%.

⚠️ **Bu sozlama faqat host'da** — repo'da vazifani yaratuvchi skript yo'q.
Qayta o'rnatish yoki tekshirish uchun:

```powershell
# Joriy holat (interval, IgnoreNew, action):
Get-ScheduledTask -TaskName "RankWant Auto Deploy" |
  Select-Object -ExpandProperty Triggers |
  Select-Object @{n='interval';e={$_.Repetition.Interval}},
                @{n='duration';e={$_.Repetition.Duration}}

# Interval'ni o'zgartirish (vazifa XML'i orqali; PT1M — eng kichigi):
$xml = Export-ScheduledTask -TaskName "RankWant Auto Deploy"
$new = $xml -replace '<Interval>PT5M</Interval>', '<Interval>PT1M</Interval>'
Register-ScheduledTask -TaskName "RankWant Auto Deploy" -Xml $new -Force
```

⚠️ XML'da `<UseUnifiedSchedulingEngine>false</UseUnifiedSchedulingEngine>`
yozish hech narsani o'zgartirmaydi — xizmat uni baribir `true` ga
normallashtiradi (o'lchandi 2026-09-21).

⚠️ **Log o'sishi.** Sog'lom tick aynan **1 qator** yozadi
(`obrazga tushmaydi — bake yo'q`), ya'ni 5 daqiqalik poll'da ~288 qator/kun,
1 daqiqalikda ~1 440 qator/kun. O'lchandi (2026-09-21): qator ~**72 bayt** ⇒
**~100 KB/kun (~37 MB/yil)**. Fayl `.handoff/auto-deploy.log` hozir 2.04 MB
va **aylantirilmaydi** — rotatsiya alohida qaror.

✅ **Tekshirildi (2026-09-21).** Log'dagi ketma-ket tick'lar (UTC):
`20:25:05` (eski 5 daqiqalik) → `20:28:03` → `20:29:03` → `20:30:03` — ya'ni
aniq **1 daqiqa** oraliq, har tick 1 qator. Vazifa: `interval=PT1M`,
`MultipleInstances=IgnoreNew`, `ExecutionTimeLimit=PT1H`, `LastTaskResult=0`.

⚠️ **Deploy alohida worktree'dan** yuriladi (`C:/Users/nsn/project/wt/deploy`),
asosiy checkout'dan **emas**: u yerda agentlarning commit qilinmagan tahriri
bo'ladi va deploy uni jimgina build qilib jonli chiqarardi. Env-fayl asosiy
checkout'da qoladi — **nusxa ko'chirilmaydi** (ikkinchi nusxa jimgina ajralib
ketadi), ikki bosqichda uzatiladi:

| Bosqich | O'zgaruvchi | Nima beriladi |
|---|---|---|
| Watcher → `deploy.sh` | `RANKWANT_AUTO_DEPLOY_ENV` | env-faylning **absolyut** yo'li (standart `$LIVE_DIR/.env.public`) |
| `deploy.sh` → `backup.sh` | `RANKWANT_ENV_FILE` | `deploy.sh` o'zi `$ENV_ABS` ga aylantirib uzatadi |

⚠️ `.env.public` worktree'da **bo'lmaydi** — u `.gitignore` da (`.env.*`).
Shu sabab `RANKWANT_AUTO_DEPLOY_ENV` shart: usiz watcher `die` qiladi
(«env-fayl topilmadi»). Tekshirish: `bash tools/auto_deploy.sh --status`
`env-fayl` va `env mavjudmi` qatorlarini chiqaradi.

⚠️ **Drift JONLI holatdan aniqlanadi**, worktree `HEAD` dan emas: merge bo'lib
deploy yiqilgan bo'lsa worktree allaqachon `origin/main` da bo'ladi, ya'ni
`HEAD` bilan solishtirish driftni **abadiy** qoldirardi. 2026-09-19 da sayt
`main` dan **4 commit orqada** edi va buni faqat `check_deploy.sh` ko'rsatdi.

⚠️ **`check_deploy.sh` yakka o'zi yetarli emas:** konteyner YO'Q bo'lganda ham
u `0` qaytaradi (`missing` hisoblagichi faqat xabar uchun, `exit 1` esa
`stale`/`envbad` da). Shuning uchun watcher tiriklikni **o'zi** tekshiradi
(`all_up`). `tools/check_decisions.py` → `deploy_automation_is_safe` shuni
qo'riqlaydi.

### Birinchi haqiqiy yurish topgan ikki nosozlik (2026-09-19)

Zanjir `main` ga qo'shildi, unit tekshiruvlari yashil edi (`check_decisions`
26/26, salbiy testlar 70/70) — **va shunga qaramay avtomatik deploy hech qachon
ishlamasdi**. Ikkalasi ham faqat zanjir BUTUN yurganda ko'rinadi, ya'ni unit
darajasida ushlanmaydi. Ikkalasi ham tuzatildi va endi qo'riqlanadi.

| # | Nosozlik | O'lchangan dalil | Tuzatish |
|---|---|---|---|
| 1 | **Watcher o'zini bloklaydi** — qulfni o'zi oladi, `deploy.sh` esa AYNAN o'sha qulfni so'raydi | `✗ boshqa deploy ishlayapti (auto-deploy pid 1303, 2026-09-19 01:38 UTC)` | watcher qulfni **topshiradi**: `RANKWANT_LOCK_HELD=1`; `deploy.sh` `mkdir`/`trap` ni o'tkazib yuboradi |
| 2 | **Yolg'on drift** — vazifa muhitida `check_deploy.sh` «eskirgan» deydi | qo'lda: `Hamma konteyner joriy kodda` (exit 0); vazifada: `3 konteyner eskirgan` (exit 1) | watcher `exec 0</dev/null`; `check_deploy.sh` → `sha256sum "$src" < /dev/null` |

**2-nosozlikning sababi** (Git Bash'ga xos, uch soat qidirildi):

```
sha256sum: failed to set file descriptor text/binary mode: Bad file descriptor
```

`sha256sum` ishga tushishda stdin fd ni sozlaydi (`_setmode`). `Task Scheduler`
→ `conhost.exe --headless` farzandga stdin **bermaydi** (fd yopiq), `sha256sum`
yiqiladi va **hech narsa chiqarmaydi**. `check_deploy.sh:161` da `2>/dev/null`
bor, ya'ni xato yashirinadi va `shash` bo'sh qoladi → «farq qiladi» →
`stale++` → `exit 1`. `</dev/null` — yaroqli fd, xato yo'qoladi. Tekshirish:

```bash
cd <repo> && bash tools/check_deploy.sh 0<&-   # yopiq stdin — AVVAL exit 1, ENDI exit 0
```

⚠️ **Umumiy saboq:** stdin yopiq muhitda MSYS coreutils jim yiqilishi mumkin.
Watcher endi `exec 0</dev/null` bilan boshlanadi, ya'ni butun zanjir
(`deploy.sh`, `backup.sh`, `docker`) yaroqli stdin oladi.

⚠️ **Qaror dalilsiz qabul qilinmasin.** Birinchi versiya shunchaki `drift` deb
yozardi — nima uchun ekani ko'rinmasdi. Endi watcher `check_deploy.sh` ning
muammoli qatorlarini (`ESKIRGAN|MUHIT|TEKSHIRILMADI|YO'Q`) logga chiqaradi.

**Boshqarish:**

```bash
bash tools/auto_deploy.sh --status     # holat: HEAD, main, jonli SHA, env-fayl
bash tools/auto_deploy.sh --dry-run    # qarorni ko'rsatadi, hech narsa qilmaydi
DEPLOY_FREEZE=1 bash tools/deploy.sh   # muzlatish (skript 1 bilan chiqadi)
bash tools/rollback.sh --list          # SHA teglar saqlanmaydi (qolganlari)
# Kodni qaytarish: deploy worktree'da kerakli commit + bash tools/deploy.sh --yes
# Sxema: <backup dir>/pg-deploy-*.sql.gz — qo'lda

bash tools/kick_auto_deploy.sh                    # merge oxirida (schtasks)
schtasks /run /tn "RankWant Auto Deploy"          # vazifani darhol yurgizish
tail -f .handoff/auto-deploy.log                  # watcher logi
rm -f ~/.rankwant-auto-deploy-state               # 30 daqiqalik to'siqni olib tashlash
rm -rf .git/rankwant-deploy.lock                  # ESKIRGAN qulf (egasi yo'q bo'lsa)
```

⚠️ To'siq (`~/.rankwant-auto-deploy-state`) yozuvi `SHA epoch` ko'rinishida.
Yolg'on nosozlikdan keyin uni o'chirish xavfsiz — u faqat qayta urinish
chastotasini cheklaydi, deploy qaroriga ta'sir qilmaydi.

⚠️ **Rollback migratsiyani qaytarmaydi.** Django'da «orqaga» migratsiya yo'q
va uni avtomatik yurgizish sxemani buzardi. Kod — kerakli commitni qayta
qurish (`tools/deploy.sh`); SHA obraz teglari **saqlanmaydi** (2026-09-20,
disk). Sxema — faqat deploy oldidagi dump (`<backup dir>/pg-deploy-*.sql.gz`),
**qo'lda**.
Bu cheklov ataylab: jimgina yarim rollback — eng yomon holat.

### Deploy vaqtini o'lchash

Ha, jarayon boshidan oxirigacha o'lchanadi. `tools/deploy.sh` har
bosqichda `TIMER finish name=… sec=…` yozadi (`time.perf_counter`).
Sovuq qurilish — `--no-cache`. Ishlab turgan `:latest` ni `rmi -f`
qilish yoki `compose down` / `volume prune` — **emas** (preview yoki
Postgres ketadi).

```bash
bash tools/measure_deploy.sh --plan
bash tools/measure_deploy.sh --warm --yes
bash tools/measure_deploy.sh --cold --yes
```

Hisobot `.handoff/deploy-timing/` ostida. Bosqichlar va nima qimmat:
[deploy-timing tadqiqoti](../research/2026-09-20-deploy-timing/README.md).

⚠️ **Docker daemon (bir martalik).** `tools/docker-daemon.json` ni
`%USERPROFILE%\.docker\daemon.json` ga qo'ying: builder GC 5 GB, json-file
10m×3. O'zgarish **Docker Desktop qayta ishga tushganda** kuchga kiradi
(qisqa sayt tanaffusi). Compose'dagi `logging:` qayta yaratilgan
konteynerlarga darhol tushadi, daemon restart'siz.

⚠️ **Tunnel avtomatik deploy'ning qo'lida emas.** Konteyner runner'da
`systemd` yo'q; tunnel — Windows fayl jarayoni (`tools/handoff.ps1` +
`RankWant Tunnel Monitor`). Deploy faqat `https://rankwant.uz/` ni tekshira
oladi, tiklay olmaydi.

---

## 2. Env o'zgaruvchilari

Qiymatlar yozilmaydi — faqat kalit nomlari va vazifasi. Asl fayllar  
gitignore'da: `.env.public` (asosiy) va `.env.handoff` (ikkita tizim  
orasidagi ko'prik).

### Asosiy (`.env.public`)

| Kalit                  | Vazifasi                                                                                  |
| ---------------------- | ----------------------------------------------------------------------------------------- |
| `DJANGO_SECRET_KEY`    | Django imzolari. Bo'sh bo'lsa API umuman ko'tarilmaydi                                    |
| `DJANGO_ALLOWED_HOSTS` | ⚠️ Bo'sh bo'lsa har so'rov **400**. `localhost` yozilishi shart — `127.0.0.1` rad etiladi |
| `PUBLIC_ORIGIN`        | Tashqi manzil (`https://rankwant.uz`). CSRF va havolalar shunga qarab yasaladi            |
| `CLOUDFLARE_API_TOKEN` | Tunnel va R2 uchun                                                                        |

### Email zanjiri (`core.mailer`)

`EMAIL_CHAIN` · `EMAIL_FROM` · `EMAIL_FROM_NAME` · keyin har provayder uchun  
juft kalit: `BREVO_API_KEY`/`BREVO_FROM` · `MAILJET_API_KEY`/  
`MAILJET_SECRET_KEY`/`MAILJET_FROM` · `RESEND_API_KEY`/`RESEND_FROM` ·  
`MAILERSEND_API_KEY`/`MAILERSEND_FROM`.

⚠️ **Kaliti yo'q provayder zanjirdan tushib qoladi va jimgina o'tkazib  
yuboriladi** — email ketmaydi, xato ko'rinmaydi. `worker` ga ham kerak:  
yuborish so'rov ichida emas, fon rejimida yuradi.

### Ijtimoiy kirish (ADR-0016)

`GOOGLE_CLIENT_ID`/`GOOGLE_CLIENT_SECRET` · `GITHUB_CLIENT_ID`/  
`GITHUB_CLIENT_SECRET` · `TELEGRAM_CLIENT_ID`/`TELEGRAM_CLIENT_SECRET` ·  
`TELEGRAM_BOT_TOKEN`/`TELEGRAM_BOT_USERNAME`.

⚠️ Kaliti yo'q provayder `/auth/providers/` ro'yxatiga tushmaydi va uning  
tugmasi **umuman chizilmaydi** — bu xato emas, loyihalashtirilgan xulq.

### Handoff (`.env.handoff`, ikki tizim orasidagi ko'prik)

`R2_ACCOUNT_ID` · `R2_ACCESS_KEY_ID` · `R2_SECRET_ACCESS_KEY` ·  
`R2_BUCKET` (standart `rankwant-handoff`).

⚠️ R2 so'rovlari **imzolangan** — mashina soati noto'g'ri bo'lsa o'tmaydi  
(qarang: §4, reboot).

---

## 3. Deploydan keyin tekshiruv

```bash
curl -s -o /dev/null -w "%{http_code}\n" https://rankwant.uz/     # 200
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8300/   # 200
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8301/api/v1/health/

PY="$(bash tools/pick-python.sh)"
$PY tools/check_ci_disk.py      # CI tozalashi joyida
$PY tools/check_negative.py     # 66/66
$PY tools/check_icons.py        # 9 to'plam × 226 kalit
```

| Alomat                                      | Sabab               | Yechim                                      |
| ------------------------------------------- | ------------------- | ------------------------------------------- |
| sayt **503**, origin `:8300` → 200          | tunnel o'lgan       | `powershell -File tools/monitor.ps1`        |
| `:8300` → **000**, konteyner `Up`/`healthy` | port ko'prigi (§4)  | Docker Desktop to'liq restart               |
| sayt 200, lekin eski kod                    | image yangilanmagan | `bash tools/check_deploy.sh` → qayta qurish |

### `web` ham `deploy.sh` da (2026-09-17 dan)

Qaror (Saidakbar aka, 2026-09-17): `tools/deploy.sh` `web` ni ham boshqa
servislar bilan birga quradi va ko'taradi. Ilgari u ataylab tashqarida edi,
va har web o'zgarishidan keyin qo'shimcha qo'lda qadam kerak bo'lardi; deploy
esa oxirida web qatori «ESKIRGAN» bilan qizil tugardi (#49 va #50
deploy'larida o'lchandi).

- `NEXT_PUBLIC_*` qiymatlari **build vaqtida** bundle'ga singadi. Skript
  compose'ga `--env-file .env.public` beradi, ya'ni ular deploy'ning o'zida
  to'g'ri singadi. `.env.public` dagi `NEXT_PUBLIC_*` o'zgarsa ham oddiy
  `bash tools/deploy.sh` yetarli: bunda `up` emas, qayta qurish kerak, skript
  esa baribir quradi.
- Next.js chiqishi siqilgan, shuning uchun `check_deploy.sh` web'ni fayl
  hash'i bilan emas, **build yorlig'i** (`org.rankwant.git-sha`) bilan
  solishtiradi. Deploy tasdig'idan keyin bundle manzilini ham tekshiradi
  (`bundle API: https://rankwant.uz/api/v1`).

### Nega `check_deploy.sh` ga salbiy test yo'q

`tools/check_negative.py` — **sof Python** tekshiruvlar uchun
(`check_*.py`); u Docker va ishlab turgan stack'ni talab qilmaydi, shuning
uchun CI'da arzon. `check_deploy.sh` esa aksincha: konteynerlar, image'lar
va ularning ichidagi fayllar kerak.

Uni `check_negative.py` ga tiqish ikki narsani buzardi: test to'plami
Docker'siz umuman ishlamay qolardi va har CI yugurishi 30-60 s
sekinlashardi.

**Buning o'rniga:** mantiq **haqiqiy holatda** tasdiqlandi — 2026-09-16 da
o'zgartirilgan 17 faylni aynan topdi (`arena/views.py` hash'i
`c385aecd…` ↔ `1548467d…`), holbuki eski mantiq «joriy kodda» derdi.
Qo'lda takrorlash: bitta faylni o'zgartirib (qayta qurmasdan)
`bash tools/check_deploy.sh` → «ESKIRGAN» chiqishi kerak.

**Istisno (2026-09-17):** web va judge **yorlig'i** bo'yicha qaror Docker'siz
hisoblanadi (`label_state`: yorliqdan beri build konteksti — `apps/web`,
`services/judge-go` — o'zgarganmi). U `--label-state` kirish nuqtasi orqali
`check_negative.py deploy_check` da sandbox repo'da sinaladi. Konteyner ichidagi
fayl hash'lari esa baribir jonli stack'ni talab qiladi.

---

## 4. Ma'lum xatolar — hammasi o'lchangan (2026-09-16)

### 4.1 `backup.sh` PortableGit'da ishlamaydi

**Alomat:** `couldn't find env file: C:\c\Users\nsn\project\cp\rankwant\.env.public`

**Sabab:** agent shell'i PortableGit ishlatadi; u MSYS yo'l konvertatsiyasini  
noto'g'ri bajaradi — `/c/Users/...` → `C:\c\Users\...` (disk harfi ikki marta).

**Yechim:**

```powershell
& "C:\Program Files\Git\bin\bash.exe" -lc "/c/Users/nsn/project/cp/rankwant/tools/backup.sh"
```

⚠️ `MSYS_NO_PATHCONV=1` **yordam bermaydi** (tekshirildi). Muvaffaqiyatsiz  
urinish `*.sql.gz.part` (0 MB) qoldiradi — ularni o'chirish kerak.  
⚠️ Rejali vazifa (`RankWant Monthly Backup`) sistema Git'ini ishlatadi —  
u ishlaydi. Muammo faqat agent shell'ida.

### 4.2 `wsl --shutdown` dan keyin port ko'prigi buziladi

**Alomat:** konteynerlar `Up` va `healthy`, ichida HTTP 200, lekin  
tashqaridan `127.0.0.1:8300` → **000**. Sayt 503.

**Sabab:** Windows ↔ WSL port ko'prigi. Monitor noto'g'ri tashxis qo'yishi  
mumkin ("konteyner ishlayapti, ichkarida ham javob yo'q") — aslida uning o'z  
probi ham o'tmagan.

**Yechim:** `docker compose up -d` **yordam bermaydi**. Faqat Docker  
Desktop'ni to'liq qayta ishga tushirish:

```powershell
Get-Process | ? { $_.ProcessName -match "^Docker Desktop$" } | Stop-Process -Force
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
# ~60 soniya kutish
```

### 4.3 `check_ci_disk.py` `UnicodeEncodeError`

**Alomat:** Windows konsolida `✔`/`✖` gliflari tufayli tekshiruv yiqiladi.

**Yechim (ildiz sabab):** `tools/_console.py` dagi `force_utf8()` —  
konsol kodirovkasini UTF-8 ga majburlaydi.  
⚠️ Glifni o'chirish — simptomni davolash, `force_utf8()` esa sababni.

### 4.4 VHDX o'sadi, kichraymaydi

**Alomat:** WSL ichida 20 GB bo'shashtirildi, C: ga atigi 3 GB qaytdi —  
`ext4.vhdx` hajmi hatto **o'sdi**.

**Sabab:** ichidagi bloklar bo'shaydi, lekin VHDX fayli o'z-o'zidan  
kichraymaydi.

**Yechim:** `wsl --shutdown` → `diskpart` bilan `compact vdisk`.  
⚠️ Bu Docker Desktop'ni ham o'chiradi → sayt va CI ~10 daqiqa to'xtaydi.  
⚠️ Siqishdan oldin **zaxira majburiy** (§5).

---

## 5. Reboot / elektr uzilishi

O'lchangan xulq (ikki marta kuzatilgan):

| Nima bo'ladi                  | Izoh                                                  |
| ----------------------------- | ----------------------------------------------------- |
| Konteynerlar o'zi tiklanadi   | `restart: unless-stopped`                             |
| **Tunnel o'ladi**             | `cloudflared` — foydalanuvchi jarayoni → sayt **503** |
| Monitor 5 daqiqada tiklaydi   | `StartWhenAvailable: True`, `NextRun` sikli           |
| Soat orqada qoladi (CMOS)     | R2 imzolangan so'rovlar o'tmaydi → `UNMEASURED`       |
| `w32time` o'zini sinxronlaydi | bir necha daqiqa                                      |

✅ **Reboot'dan keyin sayt ~5 daqiqagacha yopiq turadi — bu loyihalashtirilgan  
xulq, nosozlik emas.** Shoshilib qo'lda aralashish shart emas; monitor o'zi  
qaytaradi. Agar darhol kerak bo'lsa: `powershell -File tools/monitor.ps1`.

⚠️ Monitor `UNMEASURED` yozganda **ataylab hech narsa qilmaydi** (handoff  
qoidasi) — u o'lchay olmagan holatda ko'r-ko'rona harakat qilmaydi.

---

## 6. Zaxira — 🔴 eng katta xavf

Baza va media **Docker volume ichida**: `rankwant_pgdata`,  
`rankwant_miniodata`. Tashqi zaxira yo'q.

```powershell
& "C:\Program Files\Git\bin\bash.exe" -lc "/c/Users/nsn/project/cp/rankwant/tools/backup.sh"
```

Natija: `C:\Users\nsn\backups\rankwant\` da `pg-*.sql.gz` va  
`minio-*.tar.gz`.

⚠️ **Chastota — oylik** (`RankWant Monthly Backup`, `DaysInterval = 30`,
keyingi yurish 2026-10-16) → **RPO ≤ 30 kun**. 2026-09-17 gacha bu yerda
«kunlik» deb yozilgan edi — haqiqat boshqa edi, o'lchandi va tuzatildi.

✅ **Tiklash sinovi o'tdi: 2026-09-17** — 17 MB dump **9 soniyada** tiklandi:
jadvallar to'la, havolalar butun, jonli bazaga tegilmadi (`restore_test`
tashlandi). Ya'ni zaxira **haqiqiy** — taxmin emas.

✅ **Endi sinov HAR yurishda avtomatik** (2026-09-17 dan). Log qatorida
`restore=ok|skip|YIQILDI`; `YIQILDI` bo'lsa skript ham yiqiladi.
O'chirish: `RANKWANT_BACKUP_RESTORE_TEST=off`. Doktrina: *«tiklash sinovi
o'tkazilmasa, backup yo'q»* — shuning uchun u endi eslab qolishga tayanmaydi.

⚠️ **Saqlash va chastota mos emas:** retention 30 kun (`RANKWANT_BACKUP_KEEP`),
jadval ham 30 kun → amalda **bitta nusxa** saqlanadi. Bitta yurish yiqilsa
**nol nusxa** qolishi mumkin. Yechim: `RANKWANT_BACKUP_KEEP=180`.

**Tashqi nusxa — O'CHIQ** (Saidakbar aka qarori, 2026-09-17: zaxira faqat
lokal). Kod bor: `--offsite` bilan dump va MinIO arxivi `r2:<bucket>/backups`
ga yuklanadi va **hajm solishtiriladi** — «rclone exit 0» yetarli emas,
yarim yuklangan obyekt ham 0 qaytaradi. Yoqish faqat egasining tasdig'i bilan
(yoqilsa shifrlash shart — dump'da foydalanuvchi ma'lumoti bor).

```bash
bash tools/backup.sh              # faqat lokal (standart)
bash tools/backup.sh --offsite    # R2 — faqat tasdiq bilan; kalitlar bo'lmasa YIQILADI
bash tools/backup.sh --no-offsite # faqat lokal (aniq)
```

Kalitlar `.env.handoff` da (`R2_*`), rclone esa **konteynerda** ishlaydi
(`rclone/rclone:1.75`) — host'ga hech narsa o'rnatilmaydi.

⚠️ Log qatorida `r2=` **holatni** ko'rsatadi va u to'rt xil bo'ladi:
`ok` (yuklandi) · `skip` (`--no-offsite`) · `YOQ` (kalit yo'q) · `fail`.
Faqat `fail` nolga teng bo'lmagan kod beradi — lekin `skip`/`YOQ` ni ham
«ok» deb o'qib bo'lmaydi, aks holda offsite yo'qligi ko'rinmay qolardi.

⚠️ **Quyidagi amallardan OLDIN zaxira majburiy:**

- VHDX siqish (`diskpart compact`) — Docker VHDX ichida tirik baza
- Docker Desktop'ni o'chirish / qayta o'rnatish
- compose `down -v`

---

## 7. Endpointlar xaritasi

228 yo'l / 335 operatsiya jadvali (domen bo'yicha, generatsiya qilinadi):

⚠️ `staff` domeni — 150 operatsiya (API ning **45%**). O'zgartirish  
kiritishda birinchi shu yerga qaraladi.
