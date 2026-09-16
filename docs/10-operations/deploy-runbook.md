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
⚠️ Kunlik vazifa (`RankWant Daily Backup`) sistema Git'ini ishlatadi —  
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

⚠️ **Quyidagi amallardan OLDIN zaxira majburiy:**

- VHDX siqish (`diskpart compact`) — Docker VHDX ichida tirik baza
- Docker Desktop'ni o'chirish / qayta o'rnatish
- compose `down -v`

---

## 7. Endpointlar xaritasi

228 yo'l / 335 operatsiya jadvali (domen bo'yicha, generatsiya qilinadi):

🔴 D1 — VHDX siqish (~60 GB, sizning elevated oynangiz)    keyinro

⚠️ `staff` domeni — 150 operatsiya (API ning **45%**). O'zgartirish  
kiritishda birinchi shu yerga qaraladi.
