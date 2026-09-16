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
**live oyna tekshiruvi** → build (migrate bilan) → migrate →
`showmigrations` tasdiqi → `up -d --no-deps` → `check_deploy.sh`.
Qadamlar tartibi kodda, yodda emas.

Live oyna tekshiruvi alohida tekshiruv: `tools/check_deploy_window.py`
(chiqish 0 — bo'sh, 1 — faol contest bor, **2 — aniqlanmadi**).
⚠️ Uchinchi holat ataylab ajratilgan: «API javob bermadi» ni «0 ta» deb
o'qish yolg'on yashil berardi va aynan sayt yiqilganda — ya'ni tuzatish
deploy'i eng kerak bo'lgan paytda — darvoza eng ishonchsiz bo'lardi.

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

### `web` qachon qayta quriladi

`tools/deploy.sh` `web` ni **ataylab** qurmaydi — u faqat `apps/web/`
o'zgarganda kerak, sabab ikki xil:

1. `NEXT_PUBLIC_*` qiymatlari **build vaqtida** bundle'ga singadi, ya'ni
   `.env.public` o'zgarsa `up` yetarli emas — **qayta qurish** shart.
2. Next.js chiqishi siqilgan, shuning uchun `check_deploy.sh` uni fayl
   hash'i bilan emas, **build yorlig'i** (`org.rankwant.git-sha`) bilan
   solishtiradi.

⚠️ `apps/web/` da faqat **izoh** o'zgargan bo'lsa qayta qurish shart emas:
xatti-harakat bir xil, saytni bekorga uzish keraksiz. Bunday holda
`check_deploy.sh` «yorliqsiz image» deb ogohlantiradi — bu **xato emas**,
holat bayoni.

Qaror: `apps/web/` da kod o'zgarsa yoki `NEXT_PUBLIC_*` o'zgarsa —
`bash tools/deploy.sh` dan keyin qo'shimcha:

```bash
docker compose -p rankwant --env-file .env.public   -f docker-compose.yml -f docker-compose.public.yml   build web && docker compose -p rankwant --env-file .env.public   -f docker-compose.yml -f docker-compose.public.yml   up -d --no-deps web
```

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

✅ **Tiklash sinovi o'tdi: 2026-09-17** — `bash tools/backup.sh --restore-test`
17 MB dumpni **9 soniyada** tiklandi: jadvallar to'la, havolalar butun, jonli
bazaga tegilmadi (`restore_test` tashlandi). Ya'ni zaxira **haqiqiy** —
taxmin emas. Doktrina: *«tiklash sinovi o'tkazilmasa, backup yo'q»*.

⚠️ **Saqlash va chastota mos emas:** retention 30 kun (`RANKWANT_BACKUP_KEEP`),
jadval ham 30 kun → amalda **bitta nusxa** saqlanadi. Bitta yurish yiqilsa
**nol nusxa** qolishi mumkin. Yechim: `RANKWANT_BACKUP_KEEP=180`.

✅ **Tashqi nusxa ENDI BOR: Cloudflare R2** (2026-09-17 da qo'shildi va
o'lchandi). Har yurishdan keyin dump va MinIO arxivi `r2:<bucket>/backups`
ga yuklanadi va **hajm solishtiriladi** — «rclone exit 0» yetarli emas,
yarim yuklangan obyekt ham 0 qaytaradi.

```bash
bash tools/backup.sh              # lokal + R2 (kalitlar bo'lsa)
bash tools/backup.sh --offsite    # R2 majburiy: kalitlar bo'lmasa YIQILADI
bash tools/backup.sh --no-offsite # faqat lokal
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
