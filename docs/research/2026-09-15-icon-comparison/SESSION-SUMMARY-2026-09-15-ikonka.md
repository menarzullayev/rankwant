# Sessiya xulosasi — Ikonka tizimi va verdikt ko'rsatkichlari

**Sana:** 2026-09-15 · **Loyiha:** RankWant (`C:\Users\nsn\project\cp\rankwant`)
**Maqsad:** keyingi sessiya shu hujjatdan bevosita davom eta olishi uchun to'liq kontekst.

---

## 1. Muhokama qilingan asosiy mavzular

| # | Mavzu | Asosiy mazmun |
|---|---|---|
| 1 | **RankWant Appearance moduli** | 14 bo'limga yetdi. kep.uz bilan solishtirildi; ikkita bo'shliq yopildi: navigatsiya tizimi va erkin shrift diapazoni. |
| 2 | **Navigatsiya tizimi** | `sidenav`/`topnav` + 3 shakl (`default`/`slim`/`stacked`), mobil drawer, `role="menubar"`, strelka/Home/End/Escape navigatsiyasi. |
| 3 | **Erkin shrift diapazoni** | 75–150 % slayder, 8 qadam × 4 qiymat (o'lcham, satr balandligi, og'irlik, harf oralig'i). Yagona manba: `lib/theme/typography.ts`. |
| 4 | **Ikonka inventarizatsiyasi** | 79 sahifa + 40+ komponent skanerlandi → **~220 ikonka nuqtasi**, **48 tasi mavjud** = **20 % qoplama**. |
| 5 | **Ikonka to'plamlari** | 238+ Iconify to'plami o'rganildi; 18 ta batafsil solishtirildi; litsenziyalar (MIT/ISC/Apache-2.0/CC0). |
| 6 | **Animatsiyali ikonkalar** | 4 texnologiya: SVG `<animate>`, Motion (framer-motion), Lottie, Rive. |
| 7 | **5 sayt tahlili** | LeetCode (Font Awesome SVG), kep.uz (Iconify 6 to'plam + MUI), RoboContest (Lucide), CodeChef (Font Awesome font) — emoji va ikonka ishlatilishi kategoriyalarga ajratildi. |
| 8 | **Verdikt ko'rsatkichlari** | 10 xil vizual variant ishlab chiqildi va **kodda amalga oshirildi**. |
| 9 | **Platforma sohalari** | Holat ikonkalari, bo'sh holat/xato, qidiruv/filtr/jadval, yuklanish animatsiyasi — har biri uchun variantlar tayyorlandi. |
| 10 | **20 qaror sessiyasi** | human-in-the-loop: CTO tavsiyasi + foydalanuvchi qarori, 5 to'lqin. |

---

## 2. Qabul qilingan qarorlar

### To'lqin 1–2 (D1–D8) — asos va yo'nalish

| # | Qaror |
|---|---|
| D1 | Uslub: **Outline + Solid + Duotone** (uch uslub) |
| D2 | Hajm: 41 emas, **~220 nuqta** — to'liq inventarizatsiya qilindi |
| D3 | O'lchamlar: **16 / 20 / 24 / 32** px |
| D4 | Nomlash: **semantik kalit + mapping** |
| D5 | ⚠️ **Bitta emas, 5–10 ta to'plam** |
| D6 | ⚠️ **Foydalanuvchi o'zi tanlaydi**, brend logotiplari alohida |
| D7 | Verdikt uchun **10 variant** web sahifada ko'rsatilsin |
| D8 | Markdown panel — **to'liq** |

### To'lqin 3 (D9–D12) — verdikt va to'plamlar

| # | Qaror | Holat |
|---|---|---|
| D9 | Verdikt: **barcha 10 tur** (①–⑩) | ✅ **kodda** |
| D10 | **10 to'plam**: Lucide · Phosphor (Outline/Solid/Duotone) · Heroicons (Outline/Solid) · Tabler · Simple Icons · Bootstrap · Remix | ✅ |
| D11 | Tanlash: **Appearance bo'limi + jonli namuna; standart Lucide** | ✅ |
| D12 | Qoplama: **semantik kalit + xarita + build tekshiruvi**; asosiy to'plamdan **olmaslik** (hozircha) | ✅ |

### To'lqin 4 (D13–D16) — ⏳ tanlov kutilmoqda

Foydalanuvchi 4/4 javobda: *«Variantlarni web dashboardda taqdim qil, tanlayman»*.
→ `icon-comparison/patterns.html` yasaldi (36 bo'lim, 56 namuna, 9 animatsiya).

| # | Soha | Variantlar |
|---|---|---|
| D13 | Holat ikonkalari (ok/warn/bad/info) | 10 |
| D14 | Bo'sh holat va xato ekranlari | 8 (×2 holat) |
| D15 | Qidiruv / filtr / jadval | 8 |
| D16 | Yuklanish animatsiyasi | 10 · *«ehtimol Customizer'da tanlanadi»* |

### To'lqin 5 (D17–D20) — texnik

| # | Qaror | Holat |
|---|---|---|
| D17 | Yetkazish: **tanlangan to'plamni dinamik yuklash** (standart bundle ichida) | ✅ |
| D18 | Kalit sxemasi: **`domen.ob'ekt.holat`** (`verdict.accepted`, `nav.dashboard`) | ✅ |
| D19 | Mobil: **o'lcham o'zgarmaydi** (24px), faqat matn qisqaradi | ✅ |
| D20 | Qamrov: **CTO tavsiyasi ①** — interfeys almashadi, verdikt va brend qat'iy | ⏳ tanlov |

---

## 3. Bajarilishi lozim bo'lgan vazifalar

### 🔴 T1 — Verdikt kod qoplamasini to'ldirish · **P0 · BLOKER**

**Tavsif.** `apps/api/judging/verdicts.py` da **23 ta** verdikt kodi bor, yangi
`apps/web/src/lib/theme/verdict.ts` da esa faqat **10 ta**. `verdictOf()` noma'lum
kodni `PD` ga tushiradi, ya'ni quyidagi **14 kod hozir «Pending» bo'lib ko'rinadi**:

`PENDING` · `RUNNING` · `RE_SIGNAL` · `RE_EXIT` · `PARTIAL` · `WRONG_TEST` ·
`SKIPPED` · `COMPILE_TIMEOUT` · `IDLENESS` · `SECURITY_VIOLATION` ·
`CHECKER_ERROR` · `TESTING_ABORTED` · `RATE_LIMITED` · `DENIAL_OF_JUDGEMENT`

Bundan tashqari `verdict.ts` dagi `PD` kaliti API'da **yo'q** (API `PENDING` ishlatadi).
Eski `components/VerdictBadge.tsx` da muhim falsafa bor: **kulrang = infratuzilma
nosozligi, foydalanuvchi aybi emas** — yangi palitrada bu yo'q.

**Ustuvorlik:** P0 — komponentni sahifalarga ulashdan **oldin** bajarilishi shart.

**Kutilayotgan natija:** `verdict.ts` 23 kodni qamraydi; har bir kodda rang guruhi
(yashil/sariq/qizil/kulrang) va i18n kaliti bor; notanish kod **xom kod** bo'lib
ko'rinadi (yolg'on «Pending» emas). Tasdiq: `verdictOf("WRONG_TEST")` → «Masala
testi yaroqsiz», `verdictOf("XYZ")` → xom `XYZ`.

---

### 🔴 T2 — Commit + push + deploy · **P0**

**Tavsif.** Butun verdikt ishi lokal: 21 o'zgargan fayl, 5 yangi fayl, commit
qilinmagan; `rankwant.uz` ga deploy qilinmagan. Yo'qolish xavfi bor.

**Ustuvorlik:** P0 — deploy **xavfli amal**, foydalanuvchi tasdig'i kerak.

**Kutilayotgan natija:** o'zgarishlar `main` ga push qilingan, pre-push darvozalari
yashil, `rankwant.uz` da «Natija ko'rinishi» bo'limi ko'rinadi (11 tugma).

---

### 🔴 T3 — D13–D16 va D20 variantlarini tanlash · **P0**

**Tavsif.** `patterns.html` (36 bo'lim) va `scope.html` (4 qamrov × 6 to'plam) dan
foydalanuvchi variantlarni tanlashi kerak. Agent buni mustaqil hal qila olmaydi.

**Ustuvorlik:** P0 — keyingi implementatsiya shunga bog'liq.

**Kutilayotgan natija:** D13–D16 va D20 yopiladi; tanlangan variantlar kodga
o'tkazish uchun aniq ro'yxat bo'ladi.

---

### 🟠 T4 — `Verdict` komponentini real sahifalarga ulash · **P1**

**Tavsif.** Yangi `Verdict` komponenti **faqat Customizer namunasida** ishlatiladi.
Real sahifalarda hali eski `VerdictBadge` turadi — **7 fayl, 8 nuqta**:

`app/attempts/page.tsx:62` · `app/problems/page.tsx:274` ·
`app/problems/[slug]/stats/page.tsx:95` · `app/problems/[slug]/status/page.tsx:140` ·
`components/ArchiveSidebar.tsx:188` · `components/profile/AttemptsTab.tsx:120` ·
`components/SubmitPanel.tsx:618, 764`

⚠️ `SubmitPanel` da `isPending()` ham ishlatiladi (polling uchun) — uni saqlash kerak.

**Ustuvorlik:** P1 — T1 dan keyin.

**Kutilayotgan natija:** 8 nuqta `Verdict` ga o'tadi, `VerdictBadge` o'chiriladi
(yoki yupqa moslashtiruvchi qatlam qoladi), foydalanuvchi tanlagan ko'rinish
haqiqiy jadvallarda ko'rinadi.

---

### 🟠 T5 — 10 to'plam tizimini kodga o'tkazish · **P1**

**Tavsif.** `lib/theme/icon-packs.ts` (to'plam reyestri), `icons/registry.tsx`
(semantik kalit → to'plam bo'yicha ikonka), Customizer'da «Ikonka to'plami»
bo'limi, `AppearancePrefs.iconPack`, SSR skript, havola/JSON eksport.

**Ustuvorlik:** P1 — eng katta vazifa.

**Kutilayotgan natija:** foydalanuvchi Appearance'da 10 to'plamdan birini tanlaydi;
tanlov localStorage + havola + JSON orqali saqlanadi; standart — Lucide.

---

### 🟠 T6 — ~220 ikonka xaritasini to'ldirish · **P1**

**Tavsif.** Hozir 48 ikonka qoplangan (20 %). Qolgan ~172 nuqta uchun semantik
kalit kerak (D18 sxemasi: `domen.ob'ekt.holat`), so'ng har bir to'plamda nom
topilishi kerak.

**Ustuvorlik:** P1 — T5 bilan parallel.

**Kutilayotgan natija:** `ICON-INVENTORY.md` dagi 220 nuqta kalit bilan
belgilangan; har bir kalit kamida standart to'plamda mavjud.

---

### 🟠 T7 — `tools/check_icons.py` · **P1**

**Tavsif.** D12 qarori: xarita to'liq bo'lmasa **build yiqilishi** kerak. Skript
har bir semantik kalitni har bir to'plamda tekshiradi va yetishmaganini
hisobot qiladi. `check_negative.py` ga salbiy test qo'shiladi.

**Ustuvorlik:** P1 — T5/T6 bilan bir vaqtda.

**Kutilayotgan natija:** `python tools/check_icons.py` → 0; ataylab ikonka
o'chirilsa → RC≠0 va aniq xabar.

---

### 🟡 T8 — D13–D16 tanlangan variantlarni kodga o'tkazish · **P2**

**Tavsif.** T3 yakunlangach: holat ikonkalari tizimi (`status.ts`), bo'sh holat
komponenti (`EmptyState.tsx`), qidiruv/filtr/jadval ikonkalari, yuklanish
animatsiyalari. Animatsiya tanlansa — `prefers-reduced-motion` majburiy.

**Ustuvorlik:** P2 — T3 ga bog'liq.

**Kutilayotgan natija:** har bir soha uchun bitta qayta ishlatiladigan komponent;
10 tilga kalitlar; kontrast va salbiy testlar yashil.

---

### 🟡 T9 — Dinamik yuklash (D17) · **P2**

**Tavsif.** Standart to'plam asosiy bundle ichida, qolgani `import()` bilan
alohida bo'lak. Almashishda yuklanish holati ko'rsatiladi.

**Ustuvorlik:** P2 — T5 dan keyin.

**Kutilayotgan natija:** birinchi yuklanish hajmi standart to'plam bilan bir xil
qoladi; boshqa to'plam tanlansa, faqat o'sha bo'lak yuklanadi.

---

### ⚪ T10 — Kichik tozalash ishlari · **P3**

**Tavsif.**
(a) `rankwant/.claude/` git'da kuzatilmayapti (`?? .claude/`) — `git worktree`
papkasi; `.gitignore` ga qo'shish kerakmi, hal qilinsin.
(b) `--rw-line` → `--rw-divider` auditi: `clay`/`neu` uslublarida `--rw-line`
**`transparent`**, ya'ni u bilan yozilgan chegaralar ko'rinmaydi. `Customizer.tsx`
da 19 ta, boshqa komponentlarda ham ko'p. Har biri ataylabmi — tekshirilsin.
(c) `.tmp-verdict/` (10 MB) — kerak bo'lmasa o'chirilsin yoki `icon-comparison/tools/` ga ko'chirilsin.

**Ustuvorlik:** P3.

**Kutilayotgan natija:** `git status` toza; ko'rinmaydigan chegaralar yo'q;
vaqtinchalik fayllar tartibga solingan.

---

## Ilova — muhim fayllar

| Fayl | Vazifasi |
|---|---|
| `apps/web/src/lib/theme/verdict.ts` | 10 verdikt × kod/rang/ikonka/nom/izoh (T1 da 23 ga chiqadi) |
| `apps/web/src/components/ui/Verdict.tsx` | Bitta komponent, 10 variant + `auto` |
| `apps/web/src/icons/verdict-icons.tsx` | Phosphor (MIT) 10 ikonka — generatsiya qilinadi |
| `apps/web/src/components/VerdictBadge.tsx` | **Eski** komponent — T4 da almashtiriladi |
| `apps/api/judging/verdicts.py` | **Haqiqiy** 23 kod manbasi |
| `tools/gen-verdict-icons.mjs` + `tools/phosphor-verdict-icons.json` | Ikonkalarni qayta yasash |
| `tools/check_docs.py` | `.claude/` istisnosi qo'shildi (bu sessiyada) |
| `icon-comparison/DECISIONS-20.md` | 20 qaror jadvali |
| `icon-comparison/patterns.html` | D13–D16 variantlari (36 bo'lim) |
| `icon-comparison/scope.html` | D20 qamrov variantlari (6 to'plam jonli) |
| `icon-comparison/verdict-implemented.html` | Verdikt implementatsiyasi (manbadan yasaladi) |
| `.tmp-verdict/gen-*.mjs` | Dashboard generatorlari |

## Ilova — tekshirilgan holat

| Darvoza | Natija |
|---|---|
| `npx tsc --noEmit` | 0 |
| `npx eslint src --max-warnings=0` | 0 |
| `tools/check_i18n.py` | 10 til × **1427** kalit |
| `tools/check_hardcoded.py` | 253 manba + 101 klient fayl |
| `tools/check_contrast.py` | 772 matn rangi AA |
| `tools/check_docs.py` | 73 markdown (tuzatildi) |
| `tools/check_negative.py` | 42/42 |
| `tools/check_locales_parity.py` | 10 til × 3 ro'yxat |
| Jonli test (Playwright, `localhost:3000`) | 11/11 variant, `pageerror` 0 |

> **Eslatma:** `~/AppData/Local/ms-playwright/` bo'shab qolgan — Playwright
> `channel: "chrome"` bilan ishga tushiriladi (tizim Chrome).
