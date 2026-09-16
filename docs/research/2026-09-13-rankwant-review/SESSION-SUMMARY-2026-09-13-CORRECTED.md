# Sessiya xulosasi — 2026-09-13 (SOURCE KODGA MOSLASHTIRILGAN)

> **Bu fayl nima.** Boshqa sessiyadagi agent yozgan xulosaning **tekshirilgan
> va tuzatilgan** nusxasi. Har da'vo `main` shoxobchasidagi haqiqiy source
> kod bilan solishtirildi.
>
> **Tekshiruv sanasi:** 2026-09-14, `main` = `33ea38f`
> **Asl hujjat qaysi holatni tasvirlagan:** `13c1d6d`…`ee1e0a4` (2026-09-13)
> **Ya'ni asl hujjat `main` dan ~97–102 commit orqada.**

---

## 0. ⚠️ ENG MUHIM TOPILMA: hujjat ikki refactor orqada

Asl hujjat auth manzillarini **o'zbekcha** deb tasvirlaydi
(`/kirish`, `TABS = ["kirish","royxat","parolni-tiklash"]`). **Bu endi
to'g'ri emas.** Hujjat yozilgandan keyin ikki commit ketma-ket o'tdi:

| Commit | Sana | Nima qildi |
|---|---|---|
| `2b649c3` | 2026-09-13 19:19 | `refactor(web): rename auth tab values to english` — `?tab=` **qiymatlari** inglizchaga |
| `0c4c34f` | — | `refactor(web): rename the auth routes to english` — **marshrut yo'llari** inglizchaga |

**Hozirgi haqiqat (source kod):**

```ts
// apps/web/src/lib/auth-tabs.ts
export const TABS = ["login", "register", "reset-password"] as const;
export const TAB_BAR: readonly TabId[] = ["login", "register"];
export const DEFAULT_TAB: TabId = "login";
```

| Savol | Asl hujjat | **Haqiqat (`33ea38f`)** |
|---|---|---|
| Kanonik manzil | `/kirish?tab=` | **`/login?tab=`** |
| `?tab=` qiymatlari | `kirish` · `royxat` · `parolni-tiklash` | **`login` · `register` · `reset-password`** |
| `/login` taqdiri | 307 → `/kirish` | **KANONIK sahifaning O'ZI** (117 qator) |
| `/register` | 307 → `/kirish` | 307 → **`/login?tab=register`** (28 qator) |
| `/reset-password` | 307 → `/kirish` | 307 → **`/login?tab=reset-password`** (44 qator) |
| `/parolni-tiklash` | qaytarilgan | **MAVJUD EMAS** |
| `/kirish` | kanonik | **MAVJUD EMAS** |
| `/qoshimcha-malumot` | 2-qadam | **`/onboarding`** |
| Xatdagi havola | `/kirish?tab=parolni-tiklash&token=` | **`/login?tab=reset-password&token=`** |

Ya'ni asl hujjatning **"eski manzillar"** deb ataganlari endi **kanonik**;
u **"kanonik"** deb atagan manzillar esa **o'chirilgan**.

---

## 1. ASOSIY MUHOKAMA MAVZULARI

### M1. Auth sahifalarini bitta manzilga birlashtirish — ✅ HAQIQAT, lekin slug boshqa

**Maqsad.** `Sign in` / `Sign Up` / `Reset password` uchta alohida sahifada
edi; "Reset password" tabi mobil rejimda (360px) ko'rinmasdi.

**O'lchov (asl hujjatdan, o'zgarmagan):** 360px da 10 tildan 9 tasida
kesilgan — `kk −115px`, `es −71px`, `ky −70px`, `tg −64px`, `en −23px`,
`uz −14px`; faqat `zh` sig'di.

**Sabab (kodda tasdiqlandi).** `AuthTabs` `grid-cols-3` bilan uchta teng
ustun yasaydi; har ustunga ~68px, "Parolni tiklash" esa 89px. Tailwind
`grid-cols-${n}` ni build vaqtida skanerlamaydi → ustun soni qo'lda.

**⚠️ TUZATILDI.** Kanonik manzil `/kirish` **EMAS** — **`/login`**
(`0c4c34f` dan keyin). `TABS` qiymatlari ham inglizcha.

**Shartnoma (kodda saqlangan, faqat slug o'zgardi):**
- `TABS` — **manzil shartnomasi**: hamma bo'lim haqiqiy, hech narsa
  chiqarilmaydi (xatdagi `?token=` havolalari uchun).
- `TAB_BAR` — faqat qatorda ko'rinadiganlari: `["login","register"]`.
- `DEFAULT_TAB = "login"`.

### M2. Ro'yxatdan o'tish maydonlari shartnomasi — ✅ TO'LIQ TO'G'RI

Kodda tasdiqlandi (`apps/api/core/serializers.py`):

```python
extra_kwargs = {
    "email":         {"required": True,  "allow_blank": False},
    "username":      {"required": False, "allow_blank": True, "validators": []},
    "display_name":  {"required": False, "allow_blank": True},
    "country":       {"required": False, "allow_blank": True},
    "region":        {"required": False, "allow_blank": True},
}
```

**Ildiz sabab (to'g'ri).** `username` modelda `unique=True` → DRF uni
`required=True, allow_blank=False` yasaydi; `validators: []` bunga
**tegmaydi** → 400.

**Qoida:** maydonni 1-qadamdan olib tashlash = **`required: False` +
`allow_blank: True`** — ikkalasi shart.

### M3. Eski manzillarning "hayotda qolishi" — ⚠️ YO'NALISHI TESKARI

**Asl hujjat:** "`/parolni-tiklash` yo'naltirish fayli yo'q edi".

**Haqiqat:** `/parolni-tiklash` **umuman mavjud emas** va bo'lishi ham
shart emas — `0c4c34f` uni butunlay olib tashladi. **Yo'naltirish
fayllari — `/register` va `/reset-password`.**

**Qimmatli qismi (saqlanadi).** Diagnostika qoidasi o'z kuchida: avval
**kodning O'ZI va'da qilganini** o'qish (izohlar, `TABS` kabi shartnoma
ro'yxatlari), keyin manbaga qarash. "Manbada route yo'q" — topilma, xulosa
emas.

**`AppShell` `BARE` ro'yxati tuzaqi (o'zgarmagan).** `redirect()` klientga
javob berishdan oldin `usePathname()` **eski** qiymatni ko'rsatadi → eski
manzil `BARE` dan chiqarilsa auth kartasi bir lahza yon panel bilan
chiziladi. **Eski manzillar `BARE` da TURADI.**

### M4. Anonimlashtirish — taxallus DARHOL bo'shaydi — ✅ TO'LIQ TO'G'RI

Kodda tasdiqlandi:

```
apps/api/core/account.py:25   PREFIX = "neytrino"
apps/api/core/account.py:33   def anonymize(user: User) -> None:
apps/api/core/account.py:69   UsernameHistory.objects.filter(user=user).delete()
apps/api/core/usernames.py:62 def reserved(name, *, exclude=None) -> bool:
                              → UsernameHistory.objects.filter(old_username__iexact=...)
```

`reserved()` aynan `UsernameHistory` dan o'qiydi, `anonymize` esa uni
**o'chiradi** → **90 kunlik bandlik himoyasi ishlamaydi**. Odam o'z
taxallusini **darhol** qayta olishi mumkin. Ochiq masala **O1** bo'lib qoladi.

### M5. `/parolni-tiklash` qaytarildi + ko'chish tugallandi — ⚠️ BEKOR QILINGAN

`3ee6d3c` da qilingan ish **`0c4c34f` bilan almashtirildi**: o'zbekcha
manzillar emas, **inglizcha manzillar** saqlandi. Hozir:

| Manzil | Xatti-harakat |
|---|---|
| `/login` | **kanonik sahifa** (`?tab=login` default) |
| `/register` | 307 → `/login?tab=register` |
| `/reset-password` | 307 → `/login?tab=reset-password` |
| `/onboarding` | 2-qadam sahifasi (avval `/qoshimcha-malumot`) |

**Email havolasi (kodda tasdiqlandi, `apps/api/core/emails.py`):**
```python
path="/login",
tab="reset-password",
```
ya'ni `https://rankwant.uz/login?tab=reset-password&token=…`.

**Saqlanadigan saboq:** `redirect()` = **307** (`?token=`/`?next=` o'tadi);
`permanentRedirect` (301) **ATAYLAB emas** — keshlanadi va qaytarib
bo'lmaydi.

### M6. Commit-by-concern — ✅ TO'G'RI

`git stash push --keep-index -- <fayllar>` + `ci-local.sh all`. Aralash
daraxtda ko'rinmaydigan bog'liqlik xatosi (`TS2307: Cannot find module
'@/components/auth/Turnstile'`) shu yo'l bilan ushlangan.

### M7. Fokus halqasi (WCAG 2.4.11) — ✅ TO'LIQ TO'G'RI

Kodda tasdiqlandi: `apps/web/src/components/ui/Button.tsx:23` da
`rw-focus-ring`; butun `apps/web/src/` bo'ylab **32 fayl** ishlatadi.
`--rw-accent-ink` `check_contrast.py` da `FOCUS_MIN` (3:1) bo'yicha
tekshiriladi. `:focus-visible` → **haqiqiy `Tab` harakati kerak**
(`element.focus()` yetmaydi).

### M8. Production avariyasi — bitta ildiz, uch belgi — ✅ TO'G'RI

| # | Belgi | Qatlam | Sabab |
|---|---|---|---|
| 1 | `/` → **500** | `api` runtime env | `ALLOWED_HOSTS = []` |
| 2 | `api` unhealthy | `web` runtime env | `NEXT_PUBLIC_API_BASE` = `localhost` |
| 3 | `/login?tab=register` → `Failed to fetch` | `web` **build/bundle** | bundle ichida `http://localhost:8000/api/v1` |

**Ildiz:** `docker compose` **`--env-file .env.public`** (va `-p rankwant`)
**siz** chaqirilgan. `.env.public` **mavjud** (1809 bayt, tasdiqlandi).

**Bundle qoidasi (o'zgarmagan, muhim):** `NEXT_PUBLIC_*` **build vaqtida**
bundle'ga singadi → `docker inspect .Config.Env` **ko'r**; `up` bilan
tuzatib bo'lmaydi, faqat **qayta qurish** kerak.

### M9. `check_deploy.sh` kuchaytirildi — ✅ TO'G'RI

Kodda tasdiqlandi: `tools/check_deploy.sh:223 env_check()` mavjud;
`DJANGO_ALLOWED_HOSTS`, `DJANGO_SECRET_KEY`, `CORS_ALLOWED_ORIGINS`,
`CSRF_TRUSTED_ORIGINS` tekshiriladi; `TEKSHIRILMADI` holati ham bor.

**Tuzoq (o'zgarmagan):** salbiy test ikki marta yolg'on o'tdi —
(a) public overlay bilan build qilsa bundle to'g'ri chiqadi, xato faqat
`docker-compose.yml` **yolg'iz** holida ko'rinadi; (b) **Docker build
cache** eski qatlamni qayta ishlatib xatoni yashiradi → `--no-cache` shart.

---

### M10. 🆕 CI/CD zanjiri (asl hujjatda YO'Q)

**Sabab:** asl hujjat yozilganda runner ishlamayotgan edi, ya'ni to'liq CI
hech qachon ko'rilmagan edi.

**Ikki qatlam uzilish ochildi:**

1. **`minio/minio` Docker Hub'dan o'chirilgan** → `pull access denied`.
   Kredensial ham, tarmoq ham emas — repozitoriyning o'zi yo'q.
   Tuzatildi: `quay.io/minio/minio:RELEASE.2025-04-22T22-12-26Z` (`9be94e3`).
2. **Smoke yuki shartnomadan uzilgan** → login `username` yuborardi, API
   `identifier` kutadi; register `terms_accepted` yubormasdi → **400**.
   Tuzatildi (`33ea38f`).

**Yangi qo'riqchi:** `tools/check_contract.py` ga `check_smoke_payloads()`
qo'shildi. `check_contract.py` funksiyalari (o'lchandi):
`check_login_contract`, `check_register_contract`, `check_tab_bar`,
**`check_smoke_payloads`** (yangi). Salbiy testlar o'tkazildi (exit 1).

**Yangi saboq:** tekshiruv o'z ko'rigidan tashqarida qolmasin — smoke yuki
`check_contract` ning ko'r nuqtasi edi.

### M11. 🆕 Muhit inventarizatsiyasi (asl hujjatda YO'Q)

**Ikkita mustaqil Docker engine bor:**

| | A: Docker Desktop | B: Ubuntu-24.04 ichida |
|---|---|---|
| Versiya | **29.7.2** | **29.1.3** |
| Socket | `npipe:////./pipe/dockerDesktopLinuxEngine` | `unix:///var/run/docker.sock` |
| Disk | `docker_data.vhdx` **39.93 GB** | `ext4.vhdx` **15.33 GB** |
| Nima ishlaydi | **RankWant live stack** + 6 konteyner | **GitHub runner (CI)** |

Ikkalasi ham **WSL2** ustida. `WslEngineEnabled: true`.

**⚠️ Ma'lumot xatari:** `rankwant_pgdata` va `rankwant_miniodata` —
Docker **volume**, ikkalasi `docker_data.vhdx` **ichida**. WSL olib
tashlansa **butun baza va fayl saqlovi yo'qoladi**.

---

## 2. QABUL QILINGAN QARORLAR

| # | Qaror | Holat |
|---|---|---|
| **Q1** | Uch bo'lim bitta manzilda | ✅ Bajarilgan — lekin manzil **`/login?tab=`** (asl hujjatda `/kirish?tab=`) |
| **Q2** | Reset tabdan olib tashlanadi, havola bo'lib qoladi | ✅ Bajarilgan — `TAB_BAR = ["login","register"]` |
| **Q3** | Register 1-qadamda faqat `email`, `password`, `password2`, `terms_accepted` (+ ixtiyoriy `marketing_opt_in`) | ✅ Bajarilgan, testlar bilan qulflangan |
| **Q4** | Eski auth manzillari saqlanadi, **307** bilan yo'naltiradi | ✅ Bajarilgan — lekin **yo'naltiruvchilar `/register` va `/reset-password`** (`/login` endi kanonik) |
| **Q5** | Xato topilganda avval kodning va'da berganini o'qish | ✅ Qabul qilingan |
| **Q6** | `docker compose` har chaqiruvda `-p rankwant --env-file .env.public` | ✅ Qabul qilingan, tekshiruv bilan qulflangan |
| **Q7** | Commit-by-concern, har biri mustaqil CI'dan o'tsin | ✅ Qo'llanilgan |
| **Q8** | `check_deploy.sh` uch qatlamni tekshiradi: kod, runtime env, build/bundle | ✅ Bajarilgan (`62786c8`, `ee1e0a4`) |
| **Q9** | 🆕 `check_contract.py` smoke yukini ham tekshiradi | ✅ Bajarilgan (`33ea38f`) |
| **Q10** | ⏸️ 🆕 **CI/CD to'xtatildi** (2026-09-14, foydalanuvchi qarori) | Yangi ish boshlanmaydi |

### OCHIQ MASALALAR

| # | Masala | Holat |
|---|---|---|
| **O1** | Anonimlashtirilgan taxallus darhol bo'shaydi | O'lchov bilan tasdiqlangan. Uch variant (A qoldirish / **B `ReservedUsername`** / C `neytrino_` ni band qilish). **Qaror YO'Q** |
| **O2** | ~~`/parolni-tiklash` ni `TABS` dan chiqarishmi?~~ | **ESKIRGAN** — manzilning o'zi yo'q. Yangi savol: `/register` va `/reset-password` qancha saqlanadi? **Belgilanmagan** |
| **O3** | `NEXT_PUBLIC_API_BASE` default'i | ⚠️ **TASDIQLANDI: hali ham bor** — `apps/web/Dockerfile:19` `ARG NEXT_PUBLIC_API_BASE=http://localhost:8000/api/v1`. Xato bo'lsa **jimgina buzuq bundle** yasaydi |
| **O4** | Anonimlashtirilgan ikki Telegram hisob (`NarzullayevS`, `NarzullayevS2`) | **Noma'lum** — foydalanuvchi javob bermagan |

---

## 3. BAJARILISHI LOZIM BO'LGAN VAZIFALAR

> Asl hujjatdagi V1–V7 tekshirildi. **V1 va V2 bajarilgan**, qolganlari
> o'z kuchida, marshrut nomlari tuzatildi. **V8 yangi va eng ustuvor.**

### V1. ~~`core.hooksPath` tasdiqlash~~ — ✅ **BAJARILGAN (tekshirildi)**

```
$ git config core.hooksPath
.githooks
```
`.githooks/pre-push` mavjud (5036 bayt, 2026-09-14 20:54). **Yopildi.**

### V2. ~~Self-hosted runner holati~~ — ✅ **BAJARILGAN (tekshirildi)**

Runner **o'rnatilgan va ishlayapti**: `/opt/actions-runner`, user `runner`,
unit `actions.runner.menarzullayev-rankwant.nsn-pc-rankwant` —
**active + enabled**. Push qilingan commitlar CI'dan o'tdi.
⚠️ Lekin **CI/CD endi muzlatilgan** (Q10) → bu yo'nalishda yangi ish yo'q.

### V3. O1 — anonimlashtirish variantini tanlash — 🟠 **OCHIQ**

- **Tavsif:** `apps/api/core/account.py` (`anonymize`) da
  `UsernameHistory` o'chirilishidan (69-qator) **oldin** eski nomni band
  qilib qo'yish. Tavsiya — **B**.
- **Ustuvorlik:** Medium (obro' o'g'irlash xatari)
- **Kutilayotgan natija:** `anonymize` dan keyin ham
  `usernames.reserved('<eski nom>')` → `True`
- **Tekshiruv:** sinov hisobi → anonimlashtirish → `reserved()` → `True`;
  **salbiy test** bilan (yozuvsiz holatda `False`)

### V4. `docs/` va `README` til siyosati — 🟡 **QISMAN**

- **O'lchandi:** `docs/README.md` — sarlavha inglizcha, **matn aralash**
  (o'zbekcha jumlalar bor).
- **Ustuvorlik:** Low · **Foydalanuvchi tasdig'i kerak** (katta hajmli amal)

### V5. Eski manzillar ↔ `proxy.ts` munosabatini qulflash — 🟢 **OCHIQ**

- **O'lchandi:** `apps/web/src/proxy.ts` **mavjud** (4518 bayt);
  eski manzillar unda **yo'q** (to'g'ri). Yo'naltirish faqat
  `app/<path>/page.tsx` da.
- **Ustuvorlik:** Low · **Kutilayotgan natija:** ro'yxat bitta joyda
  e'lon qilinadi yoki izohda ko'rsatiladi

### V6. `pytest-timeout` o'rnatish — 🟠 **OCHIQ (tasdiqlandi: yo'q)**

- **O'lchandi:** `requirements*.txt` / `pyproject.toml` da **topilmadi**.
- **Ustuvorlik:** Medium · **Kutilayotgan natija:** `pytest --timeout=60`
  bilan to'liq to'plam o'tadi

### V7. `check_contract.py` ga eski-manzil tekshiruvi — 🟠 **OCHIQ (nomlari tuzatildi)**

- **Tavsif:** `TABS` "buziladigan havolalar" deb e'lon qilgan har manzil
  uchun **yo'naltirish fayli mavjudligini** tekshirish.
- **⚠️ Tuzatish:** tekshiriladigan juftliklar endi
  **`/register` → `/login?tab=register`** va
  **`/reset-password` → `/login?tab=reset-password`**.
  `/login` — kanonik, ya'ni **fayl talab qilinmaydi**;
  `/kirish` va `/parolni-tiklash` **mavjud emas va kerak ham emas**.
- **Ustuvorlik:** Medium · **Tekshiruv:** **salbiy test SHART** — faylni
  o'chirib `exit 1` ni ko'rish

### V8. 🆕 🔴 **P0** — Postgres va MinIO zaxirasini olish

- **Tavsif:** `rankwant_pgdata` va `rankwant_miniodata` — Docker volume,
  ikkalasi `docker_data.vhdx` **ichida**. Zaxira **yo'q**.
- **Ustuvorlik:** 🔴 **P0 — eng qimmat ish**
- **Kutilayotgan natija:** `pg_dump` + MinIO mirror **vhdx tashqarisida**;
  tiklanish sinovi o'tkazilgan
- **Bog'liqlik:** WSL'ni o'chirishdan oldingi **majburiy shart**

---

## 4. Xatolar jadvali (asl hujjat → haqiqat)

| Asl hujjatda | Haqiqat (`33ea38f`) | Dalil |
|---|---|---|
| Kanonik `/kirish` | **`/login`** | `app/login/page.tsx` (117 qator), `DEFAULT_TAB="login"` |
| `TABS = ["kirish","royxat","parolni-tiklash"]` | **`["login","register","reset-password"]`** | `lib/auth-tabs.ts:19` |
| `/login` — eski, 307 beradi | **kanonik sahifa** | `app/login/page.tsx` |
| `/parolni-tiklash` qaytarilgan | **mavjud emas** | `ls app/` |
| `/qoshimcha-malumot` | **`/onboarding`** | `app/onboarding/page.tsx` |
| Xat: `/kirish?tab=parolni-tiklash` | **`/login?tab=reset-password`** | `core/emails.py:74-75` |
| V1 `core.hooksPath` o'lchanmagan | **`.githooks` — o'rnatilgan** | `git config core.hooksPath` |
| V2 runner yo'q | **o'rnatilgan, active+enabled** | `systemctl is-active` |
| V4 `docs/` tekshirilmagan | **aralash** (sarlavha EN, matn qisman UZ) | `docs/README.md` |
| V7 manzillar: `/login`,`/register`,`/parolni-tiklash` | **`/register`,`/reset-password`** | `app/*/page.tsx` |

**To'g'ri chiqqan da'volar:** M2 (register `extra_kwargs`), M4 (anonymize +
`reserved()`), M6 (stash usuli), M7 (`rw-focus-ring`, 32 fayl), M8 (uch
qatlam, `.env.public`), M9 (`env_check()`), O3 (`Dockerfile:19`),
V6 (`pytest-timeout` yo'q).

**Yetishmayotgan bo'limlar (qo'shildi):** **M10** (CI/CD: MinIO + smoke
yuki), **M11** (muhit: 2 Docker engine, WSL, ma'lumot xatari),
**Q9/Q10**, **V8**, **§0** (ikki refactor haqida ogohlantirish).

---

## 5. Keyingi sessiya uchun boshlang'ich nuqta

1. **Avval `main` HEAD ni o'lchang** — bu hujjat `33ea38f` da yozilgan.
   Marshrut nomlari yana o'zgargan bo'lishi mumkin.
2. **Eng qimmat ish — V8 (zaxira).** U WSL bo'yicha har qanday qarorning
   old sharti.
3. **CI/CD'ga tegmang** — muzlatilgan (Q10).
4. **O1 (anonimlashtirish)** — o'lchov bilan tasdiqlangan xavfsizlik
   kamchiligi, qaror kutilmoqda.
5. O'lchovsiz xulosa chiqarmang: har yangi tekshiruvga **salbiy test**
   o'tkazing.
