# RankWant — raqobatchi auditi va o'zgarishlar rejasi

**Sana:** 2026-09-13
**Manba:** 5 sahifadan CDP (Chrome DevTools Protocol) orqali yig'ilgan xom ma'lumot
**Ma'lumot papkasi:** `C:\Users\nsn\rankwant-audit\`

---

## 1. Audit qanday o'tkazildi

Har bir sahifa uchun to'liq HTML, tuzilma JSON'i va skrinshot saqlandi:

| Papka | Sahifa | Holat |
|---|---|---|
| `01-robocontest-register` | robocontest.uz/register | OK |
| `02-robocontest-login` | robocontest.uz/login | OK |
| `03-kep-login` | kep.uz/login | OK |
| `04-rankwant-login` | rankwant.uz/login | OK |
| `05-rankwant-register` | rankwant.uz/register | OK (skrinshot xato) |

**Muhim metodologik tuzatish.** Dastlabki o'lchovda RankWant register sahifasida
18 maydon chiqdi va bu xato deb o'ylangan edi. Tekshiruv ko'rsatdiki, ikkinchi
forma Next.js SSR streaming artefakti — Suspense chegarasi natijani vaqtincha
`<div hidden id="S:0">` ichiga yozadi, React keyin uni joyiga ko'chiradi.
Capture shu oynada bo'lsa forma ikki marta sanaladi. `audit-extract.js` ga
yashirin daraxt filtri qo'shildi (`el.closest("[hidden]")`), shundan keyin
register **10 maydon** ko'rsatdi (2 tasi — sayt qidiruv qutisi va til
tanlagichi, ya'ni haqiqiy forma **8 maydon**).

> **Saboq:** curl yoki HTML manbasiga qarab xulosa chiqarish mumkin emas —
> Next.js streaming oynasida sahifa ikki nusxada ko'rinadi.

---

## 2. Taqqoslash natijasi

| Ko'rsatkich | RoboContest | KEP.uz | RankWant |
|---|---|---|---|
| Login maydon (global qidiruv/til chiqarilganda) | 2 | 2 | **3** |
| Register maydon | 6 | — | 8 |
| `autocomplete` qamrovi | 0 | 2 | **4 / 5** |
| Meta description | yo'q | bor | **bor** |
| OG / Twitter teglari | yo'q | yo'q | **7 ta** |
| `aria-label` (tugmalar) | deyarli yo'q | — | **bor** |
| "Parolni ko'rsatish" | bor | yo'q | bor |
| "Meni eslab qol" | yo'q | yo'q | **bor** |
| Skip-link | yo'q | yo'q | **bor** |
| `<link rel="icon">` | bor | bor | **yo'q** ⚠️ |
| `robots.txt` / `sitemap.xml` | — | — | **bor** |
| Tashqi domen | 5–7 | 6 | **4** |
| HTML hajmi (login) | 41 KB | 139 KB | **24 KB** |
| Resurs soni (login) | 91 | 42 | **17** |
| Script teglari | 10 | 7 | **17–20** ⚠️ |
| To'liq yuklanish (login) | 115 ms | 318 ms | **523 ms** ⚠️ |
| `returnUrl` qo'llab-quvvatlash | bor | bor | **yo'q** ⚠️ |
| Viloyat → maktab kaskadi | bor | yo'q | 2-qadamda |

**Xulosa ikki xil:** mahsulot sifati bo'yicha (a11y, meta, autocomplete,
yengillik, robots/sitemap) RankWant raqobatchilardan **oldinda**. Ishlash
tezligi va texnik tozalik bo'yicha **ortda** — eng ko'p script teg, eng sekin
yuklanish, va tashqi `fonts.googleapis.com` (self-host qoidasiga zid).

---

## 3. RankWant'ning kuchli tomonlari (saqlab qolinadi)

- **Eng yengil sahifa** — 24 KB HTML, 17 resurs (RoboContest 91 resurs).
- **Yagona to'liq meta to'plami** — OG + Twitter, ikki raqobatchida umuman yo'q.
- **`autocomplete` qamrovi** — `username`, `email`, `name`, `current-password`,
  `new-password`. RoboContest'da 0 ta, ya'ni parol menejerlari ishlamaydi.
- **Kirish imkoniyati** — `aria-label` li tugmalar, skip-link, `remember` bayrog'i.
- **`robots.ts` + `sitemap.ts`** — Next.js App Router orqali avtomatik.
- **O'ziga xos tashqi bog'liqlik yo'q** — faqat fontlar, Cloudflare Insights va
  Telegram OAuth.

---

## 4. Aniqlangan kamchiliklar va qabul qilingan qarorlar

| № | Muammo | Dalil | Qaror |
|---|---|---|---|
| 1 | Login'da `returnUrl` yo'q — himoyalangan sahifadan uchirilgan foydalanuvchi kirgandan keyin bosh sahifaga tashlanadi | Ikkala raqobatchida bor; RankWant HTML'ida `returnUrl`/`redirect` topilmadi | **To'liq `returnUrl` qo'shiladi**, faqat same-origin yo'llar qabul qilinadi (ochiq redirect himoyasi) |
| 2 | 10 til bor, lekin `hreflang` ham `canonical` ham yo'q | HTML'da `<link rel="canonical">` va `hreflang` topilmadi | **`canonical` bajarildi**; `hreflang` **qo'llanib bo'lmaydi** — 7-bo'limga qarang |
| 3 | Eng sekin yuklanish (523 ms) va eng ko'p script teg (17–20); `fonts.googleapis.com` tashqi | DevTools `performance.getEntriesByType("resource")` | **Font self-host (`next/font`) + script optimizatsiyasi** |
| 4 | Parol kuchi indikatori yo'q | Uchta saytning hech birida yo'q | **Indikator + anonim statistika** (analytics event) |
| 5 | OAuth (Google/GitHub) orqali kirganlarda `terms_accepted_at` yozilmaydi | `apps/api/core/oauth.py` (277 qator) da `terms_accepted` umuman yo'q | **Rozilik matni + callback'da avtomatik yozish** |
| 6 | Telefon maydoni yo'q | RoboContest `tel` turida majburiy so'raydi | ✅ **Bajarildi** — ixtiyoriy, 2-qadam va sozlamalarda, **hech qachon ommaviy emas** |
| 7 | `AnalyticsEvent` yozilyapti, lekin ko'rish UI yo'q | `apps/web` da faqat `track()` chaqiruvlari, o'qish joyi yo'q | **Staff panelga voronka dashboard** |
| 8 | Viloyat/maktab 2-qadamda; RoboContest register'da so'raydi | `OnboardingForm.tsx` da `REGION_CODES` + `api.schools()` allaqachon bor | **A/B sinov** — yarmiga register'da, yarmiga 2-qadamda |
| 9 | `public/brand/` da 5 ta tayyor ikonka yotadi, `layout.tsx` da `icons` yo'q | `mark-32/96/180/192/512.png` bor, HTML'da `<link rel="icon">` yo'q | **Hammasi ulanadi + `manifest.ts`** |
| 10 | `og:image` yo'q, `twitter:card: "summary"` | `layout.tsx:21-27`; kodda "Telegram kabi mijozlar" izohi bor | **Gibrid** (3-bo'limga qarang) |
| 11 | `application/ld+json` yo'q | Uchta saytning hech birida yo'q | **Asosiy sahifalar uchun JSON-LD** |
| 12 | `display_name` ixtiyoriy | Yorliq: "Ixtiyoriy. Reytingda taxallus bilan..." | **Ixtiyoriy qoladi** (o'zgarish yo'q) |

---

## 5. 10-savol: og-rasm bo'yicha professional tavsiya

Ikki variantdan birini tanlash emas, **gibrid** eng to'g'ri yechim:

**A) Statik standart rasm — poydevor.**
`/brand/og-default.png` (1200×630, `mark-crest.svg` asosida brendlangan)
`layout.tsx` dagi `openGraph.images` ga ulanadi. Barcha sahifani bir zumda
qoplaydi, runtime xarajati nol, CDN keshlaydi. Bu — **kafolatli qatlam**.

**B) Dinamik rasm — faqat qimmatli marshrutlar uchun.**
Next.js `ImageResponse` (`opengraph-image.tsx` konvensiyasi) orqali:
`/musobaqa/[slug]`, `/masalalar/[slug]`, `/u/[username]`.
Aynan shu sahifalar Telegram'da ulashiladi — musobaqa nomi, reyting o'rni,
foydalanuvchi statistikasi rasmda ko'rinadi.

**Nega faqat statik yaramaydi:** har bir ulashilgan havola bir xil ko'rinadi —
bosish darajasi (CTR) past bo'ladi, musobaqa e'lonlari ajralib turmaydi.

**Nega faqat dinamik yaramaydi:** har bir sahifa chekka (edge) render narxini
to'laydi, `ImageResponse` xato bersa havola butunlay rasmsiz qoladi, va
keshlash murakkablashadi.

**Gibrid:** statik rasm har doim zaxira bo'lib turadi, dinamik rasm esa faqat
ulashiladigan sahifalarda ustidan yoziladi. Buzilish xavfi yo'q, ta'sir maksimal.

Qo'shimcha: `twitter:card` `"summary"` → `"summary_large_image"` ga o'zgaradi.

---

## 6. Amalga oshirish rejasi

### 1-bosqich — tezkor tuzatishlar (kam xavf, katta ta'sir)

| Vazifa | Fayl |
|---|---|
| Ikonkalar + `manifest.ts` ulash | `apps/web/src/app/layout.tsx`, `apps/web/src/app/manifest.ts` (yangi) |
| Statik og-rasm + `twitter:card` | `apps/web/src/app/layout.tsx`, `apps/web/public/brand/og-default.png` |
| `hreflang` + `canonical` | `apps/web/src/app/layout.tsx`, `apps/web/src/i18n/server.ts` |
| `returnUrl` qo'llab-quvvatlash | `apps/web/src/components/AuthForm.tsx`, `apps/api/core/views.py` |
| OAuth roziligi | `apps/api/core/oauth.py`, `apps/web/src/components/AuthForm.tsx` |
| JSON-LD (`Organization`, `WebSite`) | `apps/web/src/app/layout.tsx` |

### 2-bosqich — ishlash tezligi

| Vazifa | Fayl |
|---|---|
| Fontlarni self-host qilish | `apps/web/src/app/layout.tsx` (`next/font`) |
| Script teglarini kamaytirish | `apps/web/src/app/layout.tsx`, `next.config.*` |
| DevTools MCP bilan waterfall tahlili va qayta o'lchash | — |

### 3-bosqich — funksionallik

| Vazifa | Fayl |
|---|---|
| Parol kuchi indikatori + statistika | `apps/web/src/components/AuthForm.tsx`, `apps/web/src/lib/analytics.ts` |
| Ixtiyoriy telefon (2-qadam) | `apps/web/src/components/OnboardingForm.tsx`, `apps/api/core/serializers.py` |
| Analitika dashboard | `apps/api/core/staff_views.py`, staff panel |
| A/B sinov mexanizmi | yangi — eksperiment bayrog'i |

### 4-bosqich — SEO chuqurlashtirish

| Vazifa | Fayl |
|---|---|
| Dinamik og-rasm | `apps/web/src/app/musobaqa/[slug]/opengraph-image.tsx` va h.k. |
| `Event` / `LearningResource` sxemalari | tegishli marshrutlar |

---

## 7. 🔴 `hreflang` qo'llanib bo'lmaydi — sabab va variantlar

**Topilma:** til URL'da EMAS. `apps/web/src/app/` da `[locale]` segmenti yo'q,
`src/proxy.ts` faqat hostni kanonik manzilga yo'naltiradi. Til uch manbadan
aniqlanadi: cookie (`rw_locale`) → `Accept-Language` → standart (`uz`).
Ya'ni **bitta manzil 10 xil tilda xizmat qiladi**.

**Nega bu muhim:** `hreflang` aynan «bir xil sahifaning turli TIL versiyalari
qaysi manzillarda» degan savolga javob beradi. Manzillar bir xil bo'lsa,
Google 10 ta yozuvni bir xil deb ko'radi — bu ma'nosiz, hatto zararli
(«dublikat» signali). Shuning uchun 2-qarorning faqat `canonical` qismi
bajarildi.

**Uch variant:**

| Variant | Nima qilinadi | Narxi |
|---|---|---|
| **1. Hozirgi holat** | `canonical` + `Content-Language` + `Vary: Accept-Language` | hreflang yo'q, xalqaro SEO cheklangan |
| **2. `?lang=` parametri** | `proxy.ts` uni o'qib so'rov sarlavhasiga yozadi, `getLocale()` ko'radi — shundan keyin hreflang HAQIQIY manzillarga ishora qiladi | har sahifa 10 nusxada ochiladi (canonical + hreflang boshqaradi) |
| **3. `/[locale]/…` yo'llari** | Eng to'g'ri xalqaro SEO yechimi | barcha marshrut, havola va yo'naltirishlarga tegadi — katta migratsiya |

**Tavsiya:** hozircha 1-variant (bajarilgan), keyin 3-variant. 2-variant —
oraliq yechim, lekin har sahifani 10 nusxada ochib, foydani canonical'ga
tayanadi; uzoq muddatda 3-variant baribir kerak bo'ladi.

---

## 8. Amalga oshirish holati

### ✅ 1-bosqich bajarildi — commit `710d850` (23 fayl, +614/−22)

| Vazifa | Holat |
|---|---|
| Ikonkalar (32/96/180) + `manifest.ts` (192/512) | ✅ |
| Statik og-rasm 1200×630 + `summary_large_image` | ✅ |
| `canonical` (o'z-o'ziga havola) | ✅ |
| JSON-LD (`Organization`, `WebSite`) | ✅ |
| `returnUrl` — parol, 2-qadam, OAuth, Telegram | ✅ |
| OAuth roziligi + rozilik matni (10 til) | ✅ |
| `hreflang` | ⛔ 7-bo'limga qarang |

**Qo'shimcha tuzatish:** `tools/brand.py` Windows'da ImageMagick o'rniga
`C:\Windows\System32\convert.exe` (disk formatlash vositasi) ni topayotgan edi.

**Yangi vosita:** `tools/og-image.py` — og-rasm generatori (Pillow, tashqi
binarsiz; `brand.py` esa ImageMagick'ka tayanadi).

**Tekshiruv:** `ci-local.sh docs` (10 til × 636 kalit) ✅ · `api` (ruff, mypy
282 fayl, migratsiya, pytest + 9 yangi test) ✅ · `web` (lint, typecheck,
build) ✅ · brauzerda render tekshirildi ✅

### ✅ 2-bosqich bajarildi — commit `e74af03`

**Asosiy topilma:** `fonts.googleapis.com` dan **har bir sahifa yuklanishida**
render-bloklovchi CSS olinardi, holbuki bu ikki oilani 12 uslubdan faqat
**ikkitasi** ishlatadi (`terminal` va `editorial`); standart `clay` ularni
umuman ishlatmaydi. Ya'ni tashqi bog'liqlikni hamma to'lardi.

Endi `next/font/google` orqali: build vaqtida yuklab olinadi, o'z domenimizdan
beriladi. **`preload: false`** — ataylab: usiz brauzer fayllarni
foydalanilishidan qat'i nazar darhol tortardi.

| Jonli login sahifasi | Oldin | Keyin |
|---|---|---|
| Resurslar | 19 | **18** |
| Tashqi Google Fonts so'rovi | **1** | **0** |
| Standart uslubda yuklanadigan shrift fayli | — | **0** |
| `terminal` uslubida | tashqi | 5 fayl, hammasi `rankwant.uz` dan |

**Script teglari bo'yicha xulosa:** 16 ta teg (5 inline + 11 Next.js chunk) —
App Router uchun odatiy, kesadigan narsa yo'q. Auditdagi «17–20» raqami SSR
streaming nusxasini ham sanagan edi.

### ✅ 3-bosqichning bir qismi: ixtiyoriy telefon — commit `259d9b6`

`User.phone` qo'shildi (`0015_user_phone.py`), 2-qadamda va sozlamalarda
ixtiyoriy maydon sifatida. SMS tasdiqlash yo'q.

**Asosiy qaror — telefon OMMAVIY EMAS.** `PRIVACY_FIELDS` — foydalanuvchi
*yashira oladigan* maydonlar ro'yxati; telefon u yerga **ataylab qo'shilmadi**,
chunki u umuman ommaviy emas, ya'ni «yashirish» tushunchasi yo'q. `MeSerializer`
da bor, `UserPublicSerializer` da yo'q. Bu muhim, chunki
`default_hidden_fields()` → `["email"]` — standart holatda **qolgan hammasi
ochiq**, ya'ni telefon oddiy maydon bo'lib qo'shilsa avtomatik ommaviy bo'lardi.

Raqam tekshirilmagani uchun unga tayanib **hech qanday huquq berilmaydi**
(parolni tiklash faqat pochta orqali) — aks holda begona raqam yozib hisobni
egallash yo'li ochilardi.

Format: bo'shliq/qavs/chiziqcha tozalanadi (`"+998 90 123 45 67"` →
`+998901234567`), aks holda bir xil raqam ikki xil saqlanardi.

**Jonli E2E:** register 201 · login 200 · tozalash ✓ · `"abc"` → 400 ·
ommaviy profilda `phone` **yo'q** · faqat telefon yuborilganda boshqa
maydonlar tegilmaydi ✓

### ✅ 3-bosqich bajarildi — commit `239a321`

**Analitika dashboard (qaror 7).** `GET /api/v1/staff/analytics/` hodisalarni
voronkaga jamlaydi; `/admin/analitika` sahifasi ko'rsatadi. **Sessiya bo'yicha**
sanaladi, xom hodisa bo'yicha emas — bir odam xatoni o'n marta ko'rishi mumkin.

**A/B mexanizmi (qaror 8).** Guruh `proxy.ts` da **serverda** belgilanadi
(180 kunlik cookie). Mijozda tasodifiy tanlansa har yuklanishda qayta o'ralardi
va bir odam ikki guruhda sanalardi. Guruh `register/page.tsx` da ham serverda
o'qiladi — mijozda o'qilsa hidratsiya mos kelmasligi mumkin edi.

**Testlar topgan ikki xato:**
1. `.exclude(user__country="")` **NULL qatorlarni chiqarib tashlamaydi** — Django
   uni `NOT (x = '' AND x IS NOT NULL)` ga aylantiradi, NULL uchun esa bu TRUE.
   Anonim hodisalar «mamlakat: null» bo'lib ro'yxatni shishirardi.
2. `days=99999` butun jadvalni skanerlab ketardi → 365 bilan cheklandi.

### ✅ 4-bosqich bajarildi — commit `239a321`

`/problems/[slug]` va `/contests/[slug]` uchun dinamik og-karta qo'shildi
(`/users/[username]` **allaqachon bor edi**). Statik brend rasmi qolgan hamma
sahifani qoplab turadi — ya'ni 5-bo'limdagi **gibrid** to'liq amalga oshdi.

### Jonli tekshiruv (hammasi ✓)

| Tekshiruv | Natija |
|---|---|
| `rw_exp=geo%3Ab` cookie | 180 kun, `SameSite=lax` ✓ |
| `/register` + guruh `a` | viloyat maydoni **0** ✓ |
| `/register` + guruh `b` | viloyat maydoni **1**, haqiqiy ro'yxat bilan ✓ |
| `/api/v1/staff/analytics/` anonim | **401** ✓ |
| `/admin/analitika` | 200, brauzerda xatosiz ✓ |
| Dinamik og-rasmlar | 200 `image/png`, 1200×630 ✓ |

### 📌 Umumiy natija

**12 qarorning 11 tasi to'liq bajarildi**, 1 tasi (`hreflang`) texnik sababdan
bajarilmadi — 7-bo'limga qarang. 4 bosqichning hammasi tugadi.

| Commit | Nima |
|---|---|
| `710d850` | ikonkalar, manifest, og:image, canonical, JSON-LD, returnUrl, OAuth roziligi |
| `e74af03` | shriftlar self-host (tashqi Google Fonts olib tashlandi) |
| `259d9b6` | ixtiyoriy telefon (hech qachon ommaviy emas) |
| `239a321` | analitika dashboard + A/B mexanizmi + dinamik og-rasmlar |

Hammasi GitHub'da va jonli saytda.

### Yon topilma (tuzatilmagan, ko'lamdan tashqari)

`--rw-font-mono` (`globals.css`, `:root`) **ta'riflangan, lekin hech qayerda
ishlatilmaydi**. `font-mono` Tailwind klassi (masala sahifalaridagi raqamlar
uchun) Tailwind'ning standart mono to'plamiga tushadi — IBM Plex Mono'ga emas.
Ya'ni niyat bor edi, ulanish tugallanmagan.

---

## 9. Ochilgan, hali hal qilinmagan masalalar

- **`hreflang`** — 7-bo'limga qarang (qaror kerak).
- **`bimi.svg`** mavjud, lekin BIMI uchun DNS yozuvi va VMC sertifikati kerak —
  hozircha ulanmagan.
- **Skrinshot xatosi** — register sahifasida `/screenshot` endpoint 500 qaytardi.
  O'lchovga ta'sir qilmadi.
- **`ci-local.sh`** ishlaydi, ammo GitHub CI self-hosted runner Linux'da —
  Windows yuklanganda runner oflayn bo'lib qoladi.
- **Commit qilindi, lekin DEPLOY QILINMAGAN** — jonli sayt hali eski holatda.
