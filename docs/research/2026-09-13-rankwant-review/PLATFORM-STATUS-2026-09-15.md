# RankWant — platforma holati (2026-09-15, 00:12)

> **Manba:** faqat shu sessiyada **o'lchangan** ma'lumot. Oldingi sessiyalar
> arxivlangan. Taxmin qilingan joyi belgilangan.
> **`main` = `33ea38f`** · lokal = origin · ishchi daraxt: 1 ta o'zgarish (`tools/naming/`)

---

## 1. JORIY HOLAT

### ✅ Ishlaydi (o'lchandi)

| Qism | Dalil |
|---|---|
| **Live stack** | 15 konteyner; `api`, `postgres`, `redis` **healthy**; `web`, `worker`, `beat`, `judge`, `minio` Up |
| **Sayt jonli** | canonical 1 · manifest 1 · icon 1 · og:image 2 · JSON-LD 2 (`Organization`, `WebSite`) |
| **Shriftlar** | tashqi `fonts.googleapis` so'rovi **0** |
| **A/B cookie** | `rw_exp=geo%3Aa; Max-Age=15552000; SameSite=lax` |
| **Dinamik og-rasm** | 3 tasi ham **200 image/png** |
| **Auth manzillari** | kanonik `/login?tab=`; `TABS=["login","register","reset-password"]`, `TAB_BAR=["login","register"]` |
| **Register shartnomasi** | `extra_kwargs` da `username/display_name/country/region` → `required:False + allow_blank:True` |
| **i18n qamrovi** | 247 faylda 0 qattiq satr; 10 til × 1345 kalit; `check_negative` 40/40 |
| **Statik tekshiruvlar** | `check_docs` · `check_contract` · `check_ordering` — uchtasi **RC=0** |
| **Deploy tekshiruvi** | `check_deploy.sh` 3 qatlam: kod · runtime env · **bundle** (`env_check` 223-qator) |
| **Git** | `core.hooksPath` = `.githooks` ✓ |

### 🟡 Chala / qisman

| Qism | Holat |
|---|---|
| **CI/CD** | ⏸️ **To'xtatilgan** (foydalanuvchi qarori). `33ea38f` run'i **`cancelled`** — smoke tuzatish **CI'da tasdiqlanmagan** |
| **Runner** | **offline** — WSL distro yana o'lgan (takrorlanadigan muammo) |
| **`AuthForm.tsx`** | 751 qator — login+register bitta faylda (bo'lish kutilgan) |
| **A11y** | `AuthForm.tsx:374` da `hover:underline` qolgan (WCAG 1.4.1) |
| **Sana/son formati** | **7 ta joy** xom `locale` bilan (`toLocale*String(locale` ) |
| **`docs/` tili** | `README.md` o'zbekcha; `docs/README.md` **aralash** |

### ❌ Nuqson / xato (o'lchandi)

| # | Nuqson | Dalil |
|---|---|---|
| **B1** | **Anonimlashtirish taxallusni DARHOL bo'shatadi** | `account.anonymize()` `UsernameHistory` ni o'chiradi, `usernames.reserved()` aynan undan o'qiydi → 90 kunlik himoya ishlamaydi |
| **B2** | `AuthProof.tsx:34` — `stats.users.toLocaleString(locale)` | `kaa`/`ky`/`tg` ICU'da yo'q → AQSh formati |
| **B3** | `--rw-font-mono` o'lik | faqat `globals.css:144` da ta'riflangan, havola **0** |
| **B4** | JSON-LD: `Event` + `LearningResource` **yo'q** | jonli saytda faqat `Organization` + `WebSite` |
| **B5** | `hreflang` yo'q | jonli = **0**; `alternates` faqat `canonical` |
| **B6** | `NEXT_PUBLIC_API_BASE` default `localhost` | `apps/web/Dockerfile:19` — xato bo'lsa jimgina buzuq bundle |

### ⚠️ Xatar

| # | Xatar | Daraja |
|---|---|---|
| **R1** | 🔴 **Zaxira YO'Q.** `rankwant_pgdata` + `rankwant_miniodata` — Docker volume, `docker_data.vhdx` **ichida**. WSL o'chirilsa baza ketadi | **eng yuqori** |
| **R2** | 🟠 `C:` da **12.5 GB** bo'sh / 299.2 GB; WSL vhdx'lar **64.22 GB** | yuqori |
| **R3** | 🟠 WSL beqaror → runner `offline` → CI `cancelled` | yuqori |
| **R4** | 🟡 4 ta tasodifiy test konteyneri ishlab turibdi (`hopeful_dewdney` …) | past |

### 🧱 Texnik qarz

| # | Qarz | Holat |
|---|---|---|
| **D1** | `pytest-timeout` o'rnatilmagan | tasdiqlandi: yo'q |
| **D2** | `browserslist` yo'q (legacy JS 24.9 kB) | tasdiqlandi: yo'q |
| **D3** | `check_contract.py` da **eski-manzil tekshiruvi yo'q** | V7 ochiq |
| **D4** | `MEMORY.md` **12 340 belgi** — kontekstga qisqarib yuklanadi | o'rta |
| **D5** | RSC prefetch dublikatlari (3 ortiqcha so'rov) | sabab aniqlanmagan |

---

## 2. OCHIQ NUQTALAR

| # | Muammo | Ust. | Murak. | Bog'liqlik | Yechim yo'li |
|---|---|---|---|---|---|
| **T1** | **Postgres + MinIO zaxirasi yo'q** (R1) | 🔴 Yuqori | Past | yo'q — boshqa hamma narsadan oldin | `pg_dump` + MinIO mirror **vhdx tashqarisiga**; tiklanish sinovi |
| **T2** | **B1** anonimlashtirish (obro' o'g'irlash) | 🔴 Yuqori | O'rta | **qaror kerak** (A/B/C) | Variant B: `anonymize` da `UsernameHistory` o'chirishdan **oldin** foydalanuvchisiz `ReservedUsername` yozuvi |
| **T3** | **B2** 7 ta xom-locale formatlash | 🟠 O'rta | Past | yo'q | sana → `dateTime()`/`date()`; son → `intlLocale()`. **Tekshiruv 3 ta naqshni qamrasin** |
| **T4** | **D3** eski-manzil tekshiruvi (V7) | 🟠 O'rta | O'rta | `check_contract.py` | Har eski manzil (`/register`, `/reset-password`) uchun `page.tsx` mavjudligi; **salbiy test shart** |
| **T5** | **B4** `Event` + `LearningResource` JSON-LD | 🟠 O'rta | Past | `generateMetadata` bor | `contests/[slug]`, `problems/[slug]` ga qo'shish |
| **T6** | **B5** `hreflang` | 🔴 Qaror | O'rta | **qaror kerak** (A/B/C) | Tarjimalar faqat interfeys qatlami — faqat to'liq tarjima qilingan sahifalarda halol |
| **T7** | **B6** `Dockerfile` build-arg default | 🟠 O'rta | Past | `apps/web/Dockerfile` | `localhost` o'rniga **build'ni yiqitadigan** default |
| **T8** | **`Vary` qo'shish** (3.3) | 🟠 O'rta | O'rta | ⚠️ Next.js allaqachon yozadi | **Qayta yozish EMAS** — mavjud qiymatga `Accept-Language` **qo'shish** + `Content-Language` |
| **T9** | **D1** `pytest-timeout` | 🟡 O'rta-past | Past | yo'q | `pytest --timeout=60` bilan to'liq to'plam |
| **T10** | **`AuthForm` bo'lish** (751 qator) | 🟡 O'rta-past | O'rta | avval hozirgi kodni o'qish | `useAuthFields` + `LoginFields`/`RegisterFields` |
| **T11** | **B3** `--rw-font-mono` | 🟢 Past | Past | vizual qaror | yoki ulash, yoki o'chirish |
| **T12** | **D2** `browserslist` | 🟢 Past | Past | FCP/LCP 0 ms | qo'shish (faqat hajm) |
| **T13** | **`docs/` + `README` inglizcha** | 🟢 Past | O'rta | **foydalanuvchi tasdig'i** | ko'p faylli amal |
| **T14** | **`bimi.svg` DNS + VMC** | 🟢 Past | Yuqori | tashqi xizmat, pul | fayl bor; DNS/sertifikat tashqi |
| **T15** | **A11y** `AuthForm.tsx:374` | 🟡 O'rta-past | Past | WCAG 1.4.1 | `hover:underline` → `underline` (tekshirish kerak) |
| **T16** | **R2** disk bosimi | 🟠 O'rta | Past | ⚠️ `prune --volumes` **taqiqlanadi** | cache/image tozalash; `Optimize-VHD` |
| **T17** | **D5** RSC prefetch | 🟢 Past | O'rta | sabab noma'lum | avval **sababni** aniqlash |
| **T18** | **O4** 2 ta Telegram hisob | ⚪ Noma'lum | — | foydalanuvchi javobi | — |

---

## 3. BOSQICHMA-BOSQICH REJA

### 0-bosqich — darhol (bloklovchi)

**T1: zaxira.** Boshqa hech narsadan oldin.
- **Kutilgan natija:** `pg_dump` + MinIO mirror `C:\Users\nsn\backups\` da; tiklanish sinovi o'tgan
- **Tekshirish:** dump fayli ochiladi, jadval soni to'g'ri; `docker_data.vhdx` dan tashqarida
- **⚠️ Xatar:** `docker system prune --volumes` — **ISHLATILMAYDI** (volumelar o'chadi)

### 1-bosqich — parallel, bir kunda

| Vazifa | Kim bilan parallel |
|---|---|
| **T3** (7 ta locale) | **T5** (JSON-LD) · **T9** (`pytest-timeout`) |
| **T7** (`Dockerfile` default) | **T11** (`--rw-font-mono`) · **T12** (`browserslist`) |

- **T3 tekshirish:** `grep -rn "toLocaleString(locale\|toLocaleTimeString(locale\|toLocaleDateString(locale" apps/web/src/` → **0**
- **T5 tekshirish:** jonli `/contests/[slug]` da `"@type":"Event"` ko'rinadi
- **T7 tekshirish:** `--env-file` siz qurilganda build **yiqiladi** (jimgina buzuq bundle emas)
- **T9 tekshirish:** `pytest --timeout=60` to'liq o'tadi

### 2-bosqich — qarorga bog'liq

**T2 (anonimlashtirish)** va **T6 (hreflang)** — ikkalasi **qaror kutadi**.
- Parallel bajarish mumkin: biri backend (`account.py`), biri frontend (`layout.tsx`)
- **T2 tekshirish:** anonimlashtirish → `reserved('<eski nom>')` → **True**; salbiy test → yozuvsiz holatda **False**
- **T6 qaror:** A) hozirgicha · B) `?lang=` · C) `/[locale]/…`

### 3-bosqich — qolganlari

**T4** (`check_contract` eski-manzil) → **T8** (`Vary` qo'shish) → **T10** (`AuthForm` bo'lish) → **T15** (a11y) → **T16** (disk) → **T13** (`docs`) → **T17** (RSC) → **T14** (BIMI)

- **T4 tekshirish:** `/register/page.tsx` o'chirilsa → `exit 1`
- **T8 tekshirish:** `Vary` da **ham** `Accept-Language`, **ham** Next.js qiymatlari turibdi
- **T10 tekshirish:** ~350 qator + 2 fayl; to'ldirib-yuborish testi o'tadi

### ⏸️ To'xtatilgan

**CI/CD** — foydalanuvchi qarori. Yangi ish boshlanmaydi.
Lekin: `33ea38f` run'i **`cancelled`** — smoke tuzatish tasdiqlanmagan.
Qayta ishga tushganda birinchi qadam: `gh run list` + runner `online` ekanini tekshirish.

---

## 4. ⚠️ SHU SESSIYADA YETISHMAYOTGAN MA'LUMOT

Quyidagilar **o'lchanmagan** — keyingi sessiya ularni o'lchashi kerak:

| # | Noma'lum | Nega muhim | Qanday o'lchash |
|---|---|---|---|
| **G1** | **`33ea38f` CI natijasi** | smoke tuzatish tasdiqlanmagan — run `cancelled` | runner onlayn qiling, `gh run list` |
| **G2** | **pytest to'plami natijasi** | testlar yashilmi — noma'lum | `CELERY_EAGER=1 pytest` |
| **G3** | **Lighthouse raqamlari** | repo'da baseline ham, `.lighthouserc*` ham **yo'q** | qo'lda o'lchash + artefakt saqlash |
| **G4** | **Bundle hajmi** | 293.8→204.9 kB da'vosi artefaktsiz | `next build` + `.next` o'lchash |
| **G5** | **`pgdata` hajmi** | zaxira hajmini bilish kerak | `docker exec … du -sh /var/lib/postgresql/data` |
| **G6** | **Judge / bake-off natijalari** | submission→verdict yo'li ishlayaptimi | smoke'ning verdict qismi |
| **G7** | **Web build/lint holati** | `tsc`, `eslint`, production build | `ci-local.sh web` |
| **G8** | **`docs/` to'liq til audit** | qaysi fayllar o'zbekcha | har faylni ko'zdan kechirish |
| **G9** | **T2/T6 qarori** | ikkala vazifa bloklangan | foydalanuvchi javobi |
| **G10** | **O4 (2 Telegram hisob)** | tiklash kerakmi | foydalanuvchi javobi |
| **G11** | **RSC prefetch sababi** | Next.js ichki xatti-harakati bo'lishi mumkin | tarmoq logini tahlil qilish |
| **G12** | **4 ta tasodifiy konteyner nima** | ular kimga tegishli | `docker inspect` |

---

## 5. ENG MUHIM UCHTA QADAM

1. **T1 — zaxira.** Arzon, tez, qaytarib bo'lmaydigan yo'qotishning oldini oladi.
2. **T2 — anonimlashtirish.** O'lchov bilan tasdiqlangan xavfsizlik kamchiligi; qaror kutyapti.
3. **T3 — 7 ta locale.** Eng arzon "haqiqiy xato" tuzatishi; tekshiruv buyrug'i 3 naqshli bo'lsin.
