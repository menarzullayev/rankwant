# Secrets rotation runbook

**STATUS:** draft (2026-09-29) — WP4 (D5) wiring va fail-fast bajarildi;
**rotation hali bajarilmagan** (tartib qulflangan).
**Manba:** [ADR-0044](../../07-adr/0044-secrets-management.md) · D5
**Til qoidasi:** Hujjat **o'zbek (lotin)**. Texnik atama, fayl yo'li va kod **inglizcha**.

> Bu runbook **faqat tartib va buyruqlarni** yozadi. U o'zi rotation
> qilmaydi: D5 qaroriga ko'ra rotation **wiring → fail-fast dan KEYIN**
> bajariladi, va hozirgi bosqichda ataylab **to'xtatilgan**.

---

## 0. Tartib — QULFLANGAN (D5)

Uch bosqich **ketma-ket**, orasidan sakrab bo'lmaydi:

| # | Bosqich | Holat | Nima qiladi |
|---|---|---|---|
| 1 | **Wiring** | ✅ bajarildi | Compose sirlari env'ga o'tdi (`${VAR:?}`), `.env.example` yangilandi |
| 2 | **Fail-fast** | ✅ bajarildi | `config/settings.py` `SECRET_KEY` yo'q/bo'sh bo'lsa `ImproperlyConfigured` |
| 3 | **Rotation** | ⛔ **keyin** | Sir qiymatlarini almashtirish — quyidagi bo'limlar |

**Nega bu tartib.** Rotation wiring'dan oldin bajarilsa eski sir hali ham
compose ichida hardcode bo'lib qoladi — ya'ni yangi qiymat hech narsani
o'zgartirmaydi. Fail-fast'dan oldin bajarilsa bo'sh qiymat jimgina
dev-default'ga tushib ketadi va production'ga o'sha default chiqadi. Shu
sababli **avval qiymat manbai env bo'lishi, keyin qiymat almashtirilishi**
shart ([ADR-0044](../../07-adr/0044-secrets-management.md) §4).

---

## 1. Sir inventari — qayerdan o'qiladi

| Sir | Manba (env kalit) | Compose iste'molchisi | Qiymat turi |
|---|---|---|---|
| Postgres paroli | `POSTGRES_PASSWORD` | `docker-compose.yml` (`postgres`, `api`, `worker`, `beat`, `migrate`) | erkin matn |
| MinIO root paroli | `MINIO_ROOT_PASSWORD` | `docker-compose.yml` (`minio`) | erkin matn |
| S3 sir kaliti | `S3_SECRET` | `docker-compose.yml` (`api`, `worker`, `beat`, `migrate`) | erkin matn |
| Django imzo kaliti | `DJANGO_SECRET_KEY` | `docker-compose.yml` + `docker-compose.public.yml` (`api`, `worker`, `beat`, `migrate`) | ≥ 50 belgi, tasodifiy |
| Handoff ko'prigi | `R2_ACCESS_KEY_ID` · `R2_SECRET_ACCESS_KEY` | `tools/handoff.sh` / `handoff.ps1` | Cloudflare R2 token |
| Email zanjiri | `BREVO_API_KEY` · `MAILJET_SECRET_KEY` · `RESEND_API_KEY` · `MAILERSEND_API_KEY` | `core.mailer` (worker) | provayder kaliti |
| Ijtimoiy kirish | `GOOGLE_CLIENT_SECRET` · `GITHUB_CLIENT_SECRET` · `TELEGRAM_CLIENT_SECRET` · `TELEGRAM_BOT_TOKEN` | `apps/api` auth | OAuth kaliti |
| Tunnel / R2 | `CLOUDFLARE_API_TOKEN` | `cloudflared` · R2 | API token |

Qiymat manbai (fayl nomi va kalit) uchun
[deploy-runbook.md §2](../deploy-runbook.md) ga qarang. **Bu runbookda
qiymat yozilmaydi** — faqat kalit nomi.

⚠️ Compose endi `${VAR:?}` bilan o'qiydi: kalit **o'rnatilmagan yoki bo'sh**
bo'lsa `docker compose` interpolyatsiyada **to'xtaydi** (jimgina dev qiymat
bilan ko'tarilmaydi). Bu wiring bosqichining o'lchangan natijasi (§4).

---

## 2. Rotation oldidan — majburiy tekshiruvlar

Rotation — **faqat Saidakbar aka (owner) aniq tasdig'i bilan** bajariladi.
Boshlashdan oldin:

```bash
# 1. Live contest oynasi bo'sh bo'lsin — rotation servisni qayta ko'taradi.
python tools/check_deploy_window.py          # 0 — bo'sh, 1 — faol contest bor

# 2. Joriy zaxira olingan va tiklanadigan bo'lsin (rotation = volume emas, lekin
#    parol almashsa bazaga qayta ulanadi).
bash tools/backup.sh --restore-test

# 3. Darvoza yashil bo'lsin.
python tools/check_decisions.py
```

⚠️ **Bazani qayta yaratish (`docker compose down -v`) TALAB QILINMAYDI.**
Rotation — env qiymatini almashtirib servisni qayta ko'tarish, volume'ni
o'chirish emas. Volume o'chirilsa ma'lumot yo'qoladi (§6 rollback).

---

## 3. Rotation tartibi — sir bo'yicha

Har bir sir uchun umumiy qadamlar: **yangi qiymat → env'ga yozish → servisni
qayta ko'tarish → tasdiq**.

### 3.1 `DJANGO_SECRET_KEY`

Almashtirilsa **hamma sessiya, CSRF va PAT bekor bo'ladi** — foydalanuvchilar
qaytadan kiradi. Buni oldindan e'lon qiling.

```bash
# Yangi kalit (≥ 50 belgi)
python -c "import secrets; print(secrets.token_urlsafe(64))"
# .env.public (yoki CI secret) dagi DJANGO_SECRET_KEY ni almashtiring, keyin:
docker compose -p rankwant --env-file .env.public \
  -f docker-compose.yml -f docker-compose.public.yml up -d --no-deps api worker beat
```

### 3.2 `POSTGRES_PASSWORD`

Parol **baza ichida ham** o'zgarishi kerak — env'ni almashtirish yakka o'zi
yetmaydi.

```bash
# 1. Baza ichida parolni almashtiring (yangi qiymat env'ga yozilgandan keyin).
docker compose -p rankwant exec postgres \
  psql -U rankwant -c "ALTER USER rankwant WITH PASSWORD '<yangi>';"
# 2. .env.public dagi POSTGRES_PASSWORD ni almashtiring.
# 3. api/worker/beat/migrate ni qayta ko'taring (yangi DATABASE_URL).
docker compose -p rankwant --env-file .env.public \
  -f docker-compose.yml -f docker-compose.public.yml up -d --no-deps api worker beat
```

⚠️ Tartib muhim: avval `ALTER USER`, keyin env. Aks holda konteynerlar eski
parol bilan qayta ulanib `FATAL: password authentication failed` oladi.

### 3.3 `MINIO_ROOT_PASSWORD` va `S3_SECRET`

MinIO root paroli **`docker-compose.yml` da** o'qiladi; MinIO uni faqat
**birinchi ishga tushirishda** volume'ga yozadi. Volume mavjud bo'lsa yangi
qiymat **qo'llanmaydi** — qo'lda `mc admin user` bilan almashtiriladi.

```bash
docker compose -p rankwant exec minio \
  mc admin user add local rankwant '<yangi-s3-secret>'
docker compose -p rankwant exec minio \
  mc admin policy attach local readwrite --user rankwant
# keyin .env.public dagi S3_SECRET (va MINIO_ROOT_PASSWORD) ni almashtiring
docker compose -p rankwant --env-file .env.public \
  -f docker-compose.yml -f docker-compose.public.yml up -d --no-deps api worker beat
```

⚠️ `S3_SECRET` — ilovaning S3 klienti ishlatadigan kalit; u MinIO ichidagi
foydalanuvchi kaliti bilan **bir xil** bo'lishi shart.

### 3.4 Provayder kalitlari (email · OAuth · Cloudflare)

Bu sirlar **provayder panelida** almashtiriladi, so'ng env'ga ko'chiriladi:

| Sir | Provayder amali |
|---|---|
| `BREVO_API_KEY` · `MAILJET_SECRET_KEY` · `RESEND_API_KEY` · `MAILERSEND_API_KEY` | panelda yangi API key → eskisini o'chirish |
| `GOOGLE_CLIENT_SECRET` · `GITHUB_CLIENT_SECRET` | OAuth App'da client secret qayta generatsiya |
| `TELEGRAM_BOT_TOKEN` | BotFather `/revoke` |
| `CLOUDFLARE_API_TOKEN` | Cloudflare → API Tokens → Roll |

Kaliti yo'q provayder email zanjiridan **jimgina tushib qoladi**
([deploy-runbook.md §2](../deploy-runbook.md)) — shuning uchun yangi qiymat
qo'yilgach zanjirni tekshiring.

---

## 4. Wiring va fail-fast — o'lchangan dalil (2026-09-29)

Rotation bosqichining old sharti — quyidagi o'lchovlar **yashil** bo'lishi.

| Tekshiruv | Buyruq | Natija |
|---|---|---|
| Hardcode sir yo'q | `grep -nE 'PASSWORD: dev' docker-compose.yml` + `grep -n 'devdevdev' docker-compose.yml` | 0 natija |
| Env'siz prod zanjiri yiqiladi | `docker compose --env-file /dev/null -f docker-compose.yml config` | exit ≠ 0 (`required variable ... is missing a value`) |
| Fail-fast | `pytest apps/api/tests/test_settings_secrets.py` | 3/3 passed |
| `security.yml` yoqilgan | `grep -c 'if: false' .github/workflows/security.yml` | 0 |
| Gate | `python tools/check_decisions.py` | `✓ 59 ta qaror kodda amalda` |

**Security workflow topgan natijalar (2026-09-29):**

| Asbob | Ko'lam | Natija |
|---|---|---|
| gitleaks | 895 commit | **sir topilmadi** (no leaks found) |
| pip-audit | `apps/api/requirements.lock` | **ma'lum zaiflik yo'q** (No known vulnerabilities found) |
| npm audit | `apps/web` (audit-level=high) | **0 zaiflik** (found 0 vulnerabilities) |

---

## 5. Tasdiq (rotation tugagach)

| Tekshiruv | Buyruq | Kutilgan |
|---|---|---|
| Servis sog'lom | `curl -s -o /dev/null -w '%{http_code}' http://localhost:8301/api/v1/health/` | `200` |
| Baza ulanadi | `docker compose -p rankwant logs --tail=50 api` | `password authentication` xatosi yo'q |
| Konteyner joriy kodda | `bash tools/check_deploy.sh` | exit 0 |
| Handoff ko'prigi | `bash tools/handoff.sh status` | R2 o'qiladi (R2 kaliti almashtirilgan bo'lsa) |

⚠️ Rotation'dan keyin `check_deploy.sh` **majburiy** — env o'zgarishi
konteynerni qayta yaratdi, ya'ni eskirgan obraz qolishi mumkin.

---

## 6. Rollback

Rotation qaytarilishi **env qiymatini qaytarish** bilan boshlanadi:

| Sir | Rollback |
|---|---|
| `DJANGO_SECRET_KEY` | eski qiymatni `.env.public` ga qaytarib, `up -d --no-deps api worker beat` |
| `POSTGRES_PASSWORD` | eski qiymatga `ALTER USER`, so'ng env — tartib §3.2 bilan bir xil |
| `MINIO_ROOT_PASSWORD` · `S3_SECRET` | `mc admin user` bilan eski kalitni tiklash, so'ng env |
| Provayder kalitlari | provayder panelida eski kalitni qayta yoqish (agar hali o'chirilmagan bo'lsa) |

⚠️ **Baza dump'i zaxira emas, agar rotation paytida ma'lumot yozilgan bo'lsa.**
Dump — vaqt kesimi ([deploy-runbook.md §6](../deploy-runbook.md)). Rotation
paytida yangi yozuvlar paydo bo'lsa, dump'ga qaytish ularni yo'qotadi. Shu
sababli rotation **live contest tashqarisida** va qisqa oynada bajariladi.

⚠️ **Volume'ni o'chirmang.** `docker compose down -v` rotation rollback'i
emas — u ma'lumotni butunlay yo'q qiladi.

---

## 7. Bog'liq hujjatlar

- [ADR-0044 — Secrets management](../../07-adr/0044-secrets-management.md) — D5 qarori va qulflangan tartib.
- [ADR-0043 — Backup / PITR / DR](../../07-adr/0043-backup-pitr-dr.md) — zaxira va tiklash chegarasi.
- [deploy-runbook.md](../deploy-runbook.md) — env kalitlari va deploy tartibi (§2 · §6).
- [10-operations README](../README.md) — operatsion hujjatlar indeksi.
