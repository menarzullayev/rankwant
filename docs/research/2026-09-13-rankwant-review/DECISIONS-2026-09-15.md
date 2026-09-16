# Qarorlar konsolidatsiyasi — 2026-09-15 (HITL sessiyasi)

> Human-in-the-loop sessiya natijasi. 9 ta savol, 9 ta qaror.
> `main` = `33ea38f` · oldingi sessiyalar arxivlangan.
> Belgilar: ✅ qabul · ⚠️ CTO tavsiyasidan farq · 🔴 yuqori ustuvorlik

---

## Jadval

| # | Nuqta | Qaror | Ust. | Keyingi qadam |
|---|---|---|---|---|
| **1** | **T1 — Zaxira** | ✅ **A** — hozir, `pg_dump` + MinIO mirror + **tiklanish sinovi** | 🔴 | `docker exec` orqali dump; vhdx tashqarisiga; sinov |
| **2** | **T2 — Anonimlashtirish** | ⚠️ **C** — `UsernameHistory` saqlash (`user=None`) | 🔴 | FK nullable migratsiya; `anonymize()` dan delete olib tashlash |
| **3** | **T6 — `hreflang`** | ✅ **A** — hozircha qo'llamaslik | 🔴 | Kontent tarjimasi kelganda C (`/[locale]/…`) ga qaytish |
| **4** | **O4 — Telegram hisoblar** | ✅ **A** — Telegram orqali qayta kirish; qatorlar **o'chirilmaydi** | ⚪ | Yangi hisob ochiladi; eski reyting qaytmaydi |
| **5** | **T13 — Hujjat tili** | ✅ **B** — faqat ildiz `README.md` inglizcha | 🟢 | 1 fayl; texnik atamalar qo'lda tekshiriladi |
| **6** | **T7 — Build arg** | ✅ **A** — `NEXT_PUBLIC_API_BASE` **majburiy (fail-fast)** | 🟠 | `Dockerfile:19` — bo'sh default + tekshiruv |
| **7** | **T16 — Disk** | ✅ **A** — faqat **build cache** (21.24 GB, ACTIVE=0) | 🟠 | T1 dan keyin; `docker builder prune`; **volumelar EMAS** |
| **8** | **G1 — `33ea38f`** | ✅ **B** — **lokal** tasdiqlash (`ci-local.sh`) | 🟠 | Runner'ga tegilmaydi — pauza buzilmaydi |
| **9** | **Qolgan 9 ta** | ✅ **B** — nuqsonlar + arzon qarz | — | T3 · T5 · T8 · T11 · T12 · T4 |

---

## Batafsil

### 1. T1 — Zaxira ✅ A
**Qaror:** to'liq zaxira + **tiklanish sinovi**.
**Nega:** zaxiraning qiymati faylda emas, tiklanishda.
**Tekshirish:** dump ochiladi, jadval soni to'g'ri, fayl `docker_data.vhdx` dan **tashqarida**.
**⚠️ Tartib:** avval zaxira → keyin T16 (disk tozalash).

### 2. T2 — Anonimlashtirish ⚠️ C (CTO tavsiyasi B edi)
**Qaror:** `UsernameHistory` qatorlarini o'chirmaslik, `user=None` qilib saqlash.
**Nega C to'g'ri ham:** eng kichik diff — `reserved()` (`usernames.py:64-68`) **o'zgarmaydi**, yangi model kerak emas.
**⚠️ Amalga oshirishda hisobga olish kerak:**
- `UsernameHistory.user` hozir `on_delete=CASCADE`, **nullable emas** → migratsiya kerak
- Jadvalning **ikkita** vazifasi bor: eski havolani yo'naltirish + 90 kun bandlik. `user=None` qatorlar **havola yo'naltirishda yetim** bo'ladi — `__str__` va boshqa ishlatilishlarni tekshirish shart
- `anonymize()` da `SocialAccount` o'chirilishi **qoladi** (Telegram UID bo'sh qolishi kerak)
**Tekshirish:** anonimlashtirish → `reserved('<eski nom>')` → **True**; salbiy test — yozuvsiz holatda **False**.
**⚠️ Faqat kelajak uchun** — allaqachon anonimlashtirilgan 4 ta hisob qamrab olinmaydi.

### 3. T6 — `hreflang` ✅ A
**Qaror:** hozircha qo'llamaslik.
**Nega:** tarjima faqat interfeys qatlami; kontent (masala matni, blog) tarjima qilinmagan → `hreflang` yolg'on va'da.
**Qaytish sharti:** kontent tarjimasi → **C** (`/[locale]/…`).

### 4. O4 — Telegram hisoblar ✅ A
**Qaror:** Telegram orqali qayta kirish; 4 ta `neytrino_*` qator o'chirilmaydi.
**O'lchov:** 4 ta qator (10457, 10452, 10451, 10395) — barchasi `email=''`, `is_active=False`, parol ishlamaydi. **`UsernameHistory` jami 0** — eski nomlar bazada yo'q.
**Nega ishlaydi:** `SocialAccount` o'chirilgan → Telegram UID bo'sh → yangi hisob ochiladi.
**⚠️ Eski reyting/yutuqlar qaytmaydi.**

### 5. T13 — Hujjat tili ✅ B
**Qaror:** faqat ildiz `README.md` inglizcha.
**O'lchov:** `README.md` o'zbekcha; `docs/` 55 fayl, **52 tasida** o'zbekcha.
**⚠️ Xotira tuzatish:** `MEMORY.md` da "`docs/` inglizcha ✅" — **noto'g'ri**, tuzatish kerak.
**Keyin:** B qiymati ko'rilgach, C ga o'tish masalasi qayta ko'riladi.

### 6. T7 — Build arg ✅ A
**Qaror:** `Dockerfile:19` — bo'sh default + majburiy tekshiruv (fail-fast).
**O'lchov:** compose **har doim** build-arg beradi (`docker-compose.yml:119`, `docker-compose.public.yml:100`) → Dockerfile default faqat direct `docker build` da ishlaydi. Hech bir workflow direct build qilmaydi → **hech narsa buzilmaydi**.
**⚠️ Bu M8 ning asl sababini yopmaydi** — u `docker-compose.yml:119` dagi `localhost` fallback. Asosiy himoya `check_deploy.sh`.

### 7. T16 — Disk ✅ A
**Qaror:** faqat build cache.
**O'lchov:** Build Cache 23.72 GB, **ACTIVE=0**, reclaimable **21.24 GB**. Images atigi 702 MB, volumelar 157 MB.
**Natija:** `C:` 12.5 GB → **~34 GB**. Xavf nol, downtime yo'q.
**⛔ Taqiqlanadi:** `prune --volumes` (`rankwant_pgdata` o'chadi).

### 8. G1 — `33ea38f` ✅ B
**Qaror:** lokal tasdiqlash (`ci-local.sh`).
**Nega:** runner onlayn qilish = CI ishi → sizning pauza qaroringizni buzadi.
**⚠️ Xavf:** WSL'da `docker compose build` **SIGBUS** berishi mumkin (CI'da yo'q, native ext4).

### 9. Qolgan 9 ta ✅ B — nuqsonlar + arzon qarz
**Bajariladi:** T3 (7 ta locale) · T5 (JSON-LD) · T8 (`Vary`) · T11 (`--rw-font-mono`) · T12 (`browserslist`) · T4 (`check_contract` eski-manzil).
**Keyinga:** T10 (`AuthForm` bo'lish) · T14 (BIMI — pul) · T17 (RSC prefetch — sabab noma'lum).
**⚠️ T8 eng nozik:** `Vary` **qayta yozilmasin** — Next.js allaqachon yozadi; faqat `Accept-Language` **qo'shilsin**.
**⚠️ T3:** tekshiruv **3 ta naqshni** qamrashi shart (`toLocaleString/TimeString/DateString(locale`).

---

## Bajarish tartibi (qarorlardan keyin)

| Bosqich | Ish | Eslatma |
|---|---|---|
| **1** | **T1 — zaxira + tiklanish sinovi** | bloklovchi; boshqa hamma narsadan oldin |
| **2** | **T16 — build cache tozalash** | faqat T1 dan keyin |
| **3** | **G1 — `ci-local.sh` bilan tasdiqlash** | runner'ga tegilmaydi |
| **4** | Parallel: **T3 · T5 · T11 · T12** | arzon, mustaqil |
| **5** | **T8** (`Vary`) → **T4** (`check_contract`) | T8 nozik; T4 salbiy test bilan |
| **6** | **T2** (anonimlashtirish) | migratsiya + yetim-qator tekshiruvi |
| **7** | **T7** (`Dockerfile`) + **T13** (`README.md`) | kichik, mustaqil |

---

## Ochiq qolgan (qaror kutmaydi, shunchaki keyinga)

| # | Nima | Holat |
|---|---|---|
| **T10** | `AuthForm` 751 qatorni bo'lish | keyinga — foydalanuvchiga ko'rinmaydi |
| **T14** | `bimi.svg` DNS + VMC | keyinga — tashqi xizmat va pul |
| **T17** | RSC prefetch sababi | keyinga — sabab noma'lum |
| **T6** | `hreflang` | kontent tarjimasini kutadi |
| **T15** | `AuthForm.tsx:374` `hover:underline` | T10 bilan birga tekshiriladi |
| **G2–G12** | O'lchanmagan ma'lumotlar | `PLATFORM-STATUS-2026-09-15.md` §4 |

---

## ⚠️ CTO tavsiyasidan farqlar

| Nuqta | CTO tavsiyasi | Sizning qaroringiz | Izoh |
|---|---|---|---|
| **T2** | B — yangi `ReservedUsername` | **C** — `UsernameHistory` saqlash | C ham to'g'ri; faqat yetim-qator xavfini amalga oshirishda tekshirish kerak |

---

## BAJARISH HOLATI (2026-09-15, 02:00)

8 ta commit (`89aa524`…`8835477`), push qilindi, **deploy qilindi**.
`check_deploy.sh` → **RC=0** ("Hamma konteyner joriy kodda").

### Jonlida tasdiqlandi

| Tekshiruv | Natija |
|---|---|
| Migratsiya `0018` bazada | ✅ |
| `core_usernamehistory.user_id is_nullable` | ✅ **YES** |
| `/contests/poyga-musobaqa` → `"@type":"Event"` | ✅ yaroqli JSON |
| `/problems/a-plus-b` → `"@type":"LearningResource"` | ✅ yaroqli JSON |
| Har ikki blokda `<` qochirilgan | ✅ |
| `/` · `/login` · `/problems/a-plus-b` | ✅ 200 |
| Zaxira (dump 17.7 MB + MinIO 7.6 MB) | ✅ joyida |

### ⛔ T8 — bloklandi, SABABI ANIQLANDI

`Vary` ni ilova ichida qo'shish imkonsiz (Next.js 16 almashtiradi;
`proxy.ts:57-92` da uch yondashuv o'lchov bilan rad etilgan).

**Tashqi yechim ham hozir yopiq:**

- Sayt Cloudflare orqasida (`CF-Ray`, `Server: cloudflare`,
  `CF-Cache-Status: DYNAMIC`) — ya'ni Transform Rule nazariy ishlardi
- Lekin `.env.public` dagi `CLOUDFLARE_API_TOKEN` faqat **1 ta zona
  ko'radi: `bugvector.uz`**. `rankwant.uz` **boshqa akkauntda** →
  `GET /zones?name=rankwant.uz` → `result: []`

**Yo'llar:** (1) `rankwant.uz` zonasi uchun alohida token; (2) Cloudflare
dashboard'dan qo'lda Transform Rule; (3) old proxy.

**Hozir xavfsiz:** `Cache-Control: private, no-store` → hech qanday umumiy
kesh saqlamaydi. Xavf faqat keshlash yoqilganda paydo bo'ladi.

### ⚠️ Deploy sabog'i: `migrate` — alohida image

`api worker beat web` qurib `up -d` qilgach sayt 200 edi, lekin migratsiya
**qo'llanmadi** (`No migrations to apply`, `0017` da to'xtagan,
`user_id NOT NULL`). Sabab: `migrate` — compose'da alohida servis, o'z
image'i bilan; u qurilmadi. Bu holda T2 runtime'da yiqilardi.
To'g'ri tartib: `build … migrate` → `up -d …` → `up migrate` →
`django_migrations` dan o'qib tasdiqlash.

### Ochiq

T10 · T14 · T15 · T17 · T6 · **T8** (tashqi yechim, token kerak)
| **T6** | A — hozircha yo'q | **A** ✅ | mos |
| **T7** | A — fail-fast | **A** ✅ | mos |
| **T9** | B — nuqsonlar + arzon qarz | **B** ✅ | mos |
