# RankWant — animatsion maskot tizimi: imkoniyatlar tahlili

**STATUS:** tadqiqot · qaror kutilmoqda (HITL)
**Sana:** 2026-10-05
**Metod:** hujjat emas — **kod o'lchandi**. Har da'vo ostidagi fayl/qiymat shu
yozuv yozilgan kunda repo'dan o'qildi. Raqamlar bilan zid keladigan hujjat
gapi bu yerda ishlatilmaydi (an'ana: `deliverables/product-strategy/` dagi
uch raqam kodga zid chiqqan — `MEMORY.md` § «Hujjat raqamini kodga qarshi
tekshirish»).

Bu yozuv **tirik hujjat emas**. Yozilgan kundagi holat. Amaldagi qoidalar
[`docs/08-technical-spec/`](../../08-technical-spec/README.md) va
[`docs/07-adr/`](../../07-adr/README.md) da; zid kelsa — ular ustun.

---

## 0. Qisqa javob (avval xulosa)

**Ha, qilish mumkin — lekin aynan bizning darvozalarimiz shaklini belgilaydi.**

Uchta o'lchov bu savolni «dizayn masalasi»dan **«arxitektura masalasi»**ga
aylantiradi:

| O'lchangan fakt | Qiymat | Nima anglatadi |
| --- | --- | --- |
| Web'da animatsiya kutubxonasi | **0 ta** (`apps/web/package.json`) | Bugun hamma harakat — CSS `@keyframes`. Har yangi runtime byudjetdan ovqat yeydi |
| Harakat darajalari | **4 ta**: `system` · `full` · `mild` · `off` (+eski `reduce`) | Maskot animatsiyasi shu darvozadan o'tishi shart — va bu **texnik talab**, did masalasi emas |
| Uslub × palitra | **12 uslub** → 7 tasi ikki muhitli ⇒ **19 palitra** | Bitta maskotni 19 marta chizib bo'lmaydi. Rang **token**dan kelishi kerak |

**Tavsiya (bir qatorda):** maskot **inline SVG + CSS `@keyframes`** bo'lsin,
rangi `var(--rw-*)` tokendan olinsin, geometriyasi **locked Crest** dan
tug'ilsin, va birinchi integratsiya nuqtasi — mavjud `EmptyState`
`illustration` varianti. Lottie/Rive **hozircha rad** (sabablari §6.3 da —
ular 2026-09-15 dagi ikonka qaroridagi uch sababning aynan o'zi).

---

## 1. Hozirgi holat — o'lchandi, taxmin emas

### 1.1. Nima bor

| Narsa | Qayerda | Holat |
| --- | --- | --- |
| Crest (grafik belgi) | `docs/brand/mark-crest.svg` | **locked candidate** — geometriya raqamlarda yozilgan |
| Barcha format generatori | `tools/brand.py` | Bitta SVG → favicon, PWA, BIMI, OG, email sarlavhasi |
| Brend qabul darvozasi | [`LOCK-GATE.md`](../../brand/LOCK-GATE.md) | **open** — Crest + Wordmark hali qulflanmagan |
| Bo'sh holat shakli | `apps/web/src/components/ui/EmptyState.tsx` | 3 variant: `full` · `card` · **`illustration`** |
| Yuklanish animatsiyasi | `apps/web/src/lib/theme/loading.ts` | **10 variant**, foydalanuvchi tanlaydi |
| Verdikt ikonkalari | `tools/gen-verdict-icons.mjs` | Generatsiya qilinadi |
| OG rasm generatori | `tools/og-image.py` | Bor |
| **Quyosh tizimi SVG to'plami** | `planets/` — 10 fayl | **Bor, lekin kodda 0 marta ishlatilgan** |

### 1.2. Nima yo'q

- **Animatsiya kutubxonasi yo'q.** `framer-motion` / `motion` / `lottie-web` /
  `gsap` — hech biri `apps/web/package.json` da emas. Bugungi harakat: CSS
  `@keyframes` + `transition` (`theme.css`, `kit.css`, `form-families.css`).
- **Maskot yo'q.** `Avatar.tsx` — foydalanuvchi rasmi yoki bosh harf, xolos.
- **Illyustratsiya aktivi yo'q.** `illustration` varianti katta och doira +
  **ikonka** chizadi (`EMPTY_ICONS` registridan), chizilgan qahramon emas.
- **`planets/` bog'lanmagan.** 10 ta tayyor SVG (sun, merkuriy… pluton,
  1.7–3.7 KB) repoda yotibdi va **na kodda, na hujjatda bir marta ham
  havola qilinmagan**. Bu — bepul, o'z mavzusiga ega xom ashyo.

### 1.3. Crest geometriyasi — maskotning tug'ilish nuqtasi

`docs/brand/mark-crest-params.md` dan o'lchangan (1024×1024 kanvas):

```
Nuqta (circle)      cx=420.5  cy=206.76  r=44.1   ← «maqsad / want»
Chap cho'qqi uchi   (420.0, 294.5)                ← baland cho'qqi
O'ng cho'qqi uchi   (649.0, 396.5)                ← ~80% balandlik
Vodiy               (559.0, 501.5)
Nuqta ↔ cho'qqi     ≈ 43.6 px bo'shliq
Kontur qalinligi    ≈ 36 px
```

**Konsept allaqachon yozilgan:** «ikki cho'qqi + tepadagi mustaqil nuqta
(maqsad / «want»)». Ya'ni brend o'zi **qahramon va uning maqsadini** chizib
qo'ygan. Maskotni noldan o'ylab topish shart emas — **nuqta jonlanishi**
kerak. Bu §3.1 dagi asosiy qahramon g'oyasining poydevori.

---

## 2. Qattiq cheklovlar — maskot shu devorlar orasida yashaydi

Bu bo'lim — eng muhimi. Har band **o'lchangan**, har biri darvoza bilan
majburlangan. Maskot dizayni shularni birinchi kundan hisobga olishi kerak,
keyin «tuzatish» qimmat.

### 2.1. Harakat darvozasi (eng nozik joy)

`apps/web/src/app/theme.css` da harakat **to'rt pog'ona**:

```css
[data-motion="off"], [data-motion="reduce"] {
  animation-duration: 0.001ms !important;
  animation-iteration-count: 1 !important;
  transition-duration: 0.001ms !important;
}
[data-motion="mild"] * { transition-duration: 120ms !important; }
[data-motion="mild"] [class*="animate-"],
[data-motion="mild"] [class*="rw-pulse"] { animation: none !important; }
```

⚠️ **Ikkita amaliy tuzoq — aynan shu yerda:**

1. `mild` darvozasi **faqat nom bo'yicha** ushlaydi: `[class*="animate-"]` yoki
   `[class*="rw-pulse"]`. Ya'ni maskot animatsiya klassini `rw-mascot-walk`
   deb nomlasangiz, u `mild` foydalanuvchisida **hamon qimirlaydi** — va buni
   hech bir test ushlamaydi. **Qoida:** maskot animatsiya klasslari
   `animate-` bilan boshlansin (yoki nomida `rw-pulse` bo'lsin).
2. `off`/`reduce` bloki `animation-*` ni o'chiradi — lekin **SVG SMIL
   (`<animate>`)** bu CSS xossasi emas. Ya'ni SMIL bilan qilingan maskot
   `off` foydalanuvchisida ham aylanib turaveradi. SMIL tanlansa,
   `svg.pauseAnimations()` ni qo'lda chaqirish **shart** (§6.2).

Ustiga, `theme.css` da `@media (prefers-reduced-motion: reduce)` bloki bor va
u **klasslarni birma-bir sanaydi** (`rw-load-arc`, `rw-load-dots i`, …).
Sabab izohda yozilgan: OS sozlamasi atributsiz holatda ham hurmat qilinishi
shart. **Ya'ni yangi maskot animatsiyasining har bir klassini o'sha ro'yxatga
ham qo'shish kerak** — aks holda OS'da «harakatni kamaytir» tanlagan
foydalanuvchi maskotni harakatlanib ko'radi.

> **Xulosa:** maskotning har bir pozasi uchun **statik muqobil** bo'lishi
> shart. Harakat — qo'shimcha qatlam, asos emas. Bu aynan mavjud yuklanish
> naqshining mantig'i: `[data-motion="reduce"] .rw-load-dots i { opacity: .8 }`
> — harakat o'chdi, **shakl qoldi**.

### 2.2. Kontrast darvozasi

`tools/check_contrast.py` — **19 palitra**, WCAG AA 4.5:1, jumladan
`--rw-accent-fg` matni `--rw-accent` foni ustida (2026-09-13 da aynan shu
juftlik `clay` da 4.23:1 bo'lib Lighthouse'ni yiqitgan). 2026-10-05 da
`clay` qorong'i palitrasi qo'shilgach juftliklar soni **610 → 635** bo'ldi.

**Natija:** maskot rangi **tokendan** olinishi kerak, xom hex'dan emas.
`fill="var(--rw-accent)"` — 19 palitrada avtomatik to'g'ri. `fill="#5b8cff"`
— 18 palitrada yolg'on.

### 2.3. Bundle byudjeti

`tools/check_bundle_budget.py` — `apps/web/.next/static` dagi haqiqiy gzip
hajmni o'lchaydi: `js_gzip`, `css_gzip` va `chunk_max`. Izohda sabab aniq:
«`next build` hech qachon YIQILMAYDI… byudjet faqat foydalanuvchi internetida
bilinadi». Ya'ni **300 KB kutubxona qo'shsangiz, build yashil chiqadi** —
darvozagina ushlaydi.

Har qanday runtime (Lottie ~60 KB, Rive ~100 KB, Motion ~30 KB) shu byudjetdan
yeydi. Byudjetni ko'tarish mumkin (`--write`), lekin sabab izohda qoladi.

### 2.4. SSR

Next.js 16 + React 19, RSC. Lottie va Rive **faqat klientda** ishlaydi.
`ANIMATED-SOURCES.md` buni ikonkalar uchun aynan shu sabab bilan rad etgan:
«Lottie/Rive klient tomonida ishlaydi — bizning SSR naqshimizga zid».
Inline SVG + CSS esa serverda ham to'g'ri chiziladi.

### 2.5. Til va matn

10 tilli interfeys, `tools/check_i18n.py` + `check_locales_parity.py` +
`check_hardcoded.py` darvozalari. **Maskot matn tashimasligi kerak** — matn
kerak bo'lsa, u i18n kaliti orqali o'tadi (masalan `mascot.empty.hint`).
Bu, ayni paytda, yaxshi dizayn: qahramon tilsiz gapiradi.

### 2.6. Brend qulfi

`LOCK-GATE.md` — Crest + Wordmark qulflanmaguncha «locked» emas, va brend
o'zgarishi `CLAUDE.md` dagi qarorlar jadvaliga **yangi qator** + Saidakbar
aka tasdig'i + `tools/check_decisions.py` yozuvi talab qiladi. **Maskot —
yangi brend aktivi**, ya'ni u ham shu yo'ldan o'tadi.

Ustiga, `docs/brand/README.md` dagi naqsh: **bitta manba SVG → generator
skript → hamma format**. Logotip uchun bu ataylab shunday qilingan, sababi
yozilgan: «kimdir bittasini unutsa, sayt ikki xil belgi ko'rsatib turardi».
Maskot ham **xuddi shu naqshda** bo'lishi kerak, aks holda ertami-kechmi
drij paydo bo'ladi.

---

## 3. Maskot turlari — nima yaratish mumkin

Quyidagi yetti tur **mahsulot lahzalariga** bog'langan, «chiroyli bo'lsin»
degan umumiy istakka emas. Har biri uchun: nima uchun, qayerda, qaysi mavjud
narsaga tayanadi.

### 3.1. ① Asosiy qahramon — «Nuqta»

**G'oya:** Crest'dagi **mustaqil nuqta** (cx 420.5, cy 206.76, r 44.1) jonlanadi
va cho'qqilarni zabt etadi. Cho'qqi — reyting, nuqta — maqsad.

**Nima uchun bu eng to'g'ri tanlov:**

| Sabab | Dalil |
| --- | --- |
| Geometriyasi **qulflangan** | `mark-crest-params.md` da raqamlarda yozilgan — yangi brend qarori kerak emas |
| Hikoyasi mahsulot bilan **bir xil** | «cho'qqiga chiqish» = 16 pog'onali narvon (ADR-0027) |
| Tilsiz | 10 tilda bir xil ishlaydi |
| Miqyoslanadi | Nuqta — doira: 16px da ham o'qiladi (LOCK-GATE A1 mezoniga mos) |
| Brend ikkiligi saqlanadi | RankWant qahramoni ≠ Qvant tangasi (principle #4) |

**Ism — brend qarori.** Nomzodlar: **Nuqta** (yetakchi) · Cho'qqi · Yulduz.
Yakuniy tanlov Saidakbar akaniki (§12, D1).

### 3.2. ② Holat maskotlari

Bitta qahramon, turli holatlar. Mavjud `EmptyState` shakllariga to'g'ridan-to'g'ri
o'tiradi:

| Holat | Mavjud shakl | Maskot pozasi |
| --- | --- | --- |
| Bo'sh ro'yxat | `full` / `card` | Nuqta qo'l silkitadi |
| 404 | `illustration` | Nuqta adashgan xaritaga qaraydi |
| Xato / 500 | `illustration` | Nuqta yelka qisadi |
| Muvaffaqiyat | `illustration` | Nuqta cho'qqida turadi |
| Onboarding | `illustration` | Nuqta qo'lini uzatadi |

Bu **eng arzon** kirish nuqtasi: `EmptyState` allaqachon 10+ sahifada
ishlatiladi (`contests`, `arena`, `blog`, `learn`, `algorithms`, `hackathons`,
`platform-roadmap`, `DataState`, `ProblemEditorialPanel`, `ProblemStatsPanel`).

### 3.3. ③ Verdikt maskotlari

**Eng yuqori emotional qaytish.** Verdikt — platformaning hissiy cho'qqisi:
`AC` da quvonch, `WA` da umid, `TLE` da sabr.

⚠️ **Diqqat:** verdikt ikonkalari allaqachon **generatsiya qilinadi**
(`tools/gen-verdict-icons.mjs`, `phosphor-verdict-icons.json`) va verdikt
kodlari `tools/check_verdict_codes.py` bilan qulflangan. Ya'ni maskot ularni
**almashtirmaydi** — ustiga qo'shiladi va mavjud taksonomiyaga bo'ysunadi
(`docs/08-technical-spec/verdict-taxonomy-dead-codes.md`).

### 3.4. ④ Daraja (tier) maskotlari — kuchli retention

ADR-0027 — **16 pog'onali narvon**. G'oya: Nuqta har pog'onada **o'zgaradi**
(yangi shakl, yangi kuch, yangi aksessuar). Bu «evolyutsiya» mexanikasi:

```
1–4 pog'ona    oddiy nuqta
5–8 pog'ona    iz qoldiradi (trail)
9–12 pog'ona   yorug'lik chiqaradi
13–16 pog'ona  yulduzga aylanadi
```

**Narxi:** 16 × pozalar to'plami — bu **kontent yuki**, va u shu turdagi eng
qimmat qism. Shuning uchun taklif: **4 ta «davr»** (har biri 4 pog'onani
qoplaydi), 16 ta alohida emas. Keyin kengaytirish mumkin.

### 3.5. ⑤ Qvant / streak maskotlari

Qvant iqtisodiyoti + streak — retention mexanikasi. Nuqta tanga bilan
munosabatda: tanga ushlaydi, strekni «isitadi». Bu tur **gamifikatsiyani
ko'rinadigan** qiladi. ADR-0002 (pul = faqat ledger) **buzilmaydi** — maskot
shunchaki ko'rsatuvchi, yozuvchi emas.

### 3.6. ⑥ Yutuq maskotlari

ADR-0018 — unvonlar, rollar, yutuqlar. Har yutuqqa Nuqtaning kichik
medali/pozasi. `UserTitle` / `TitleBand` komponentlari allaqachon bor —
maskot ularning **vizual hamrohi** bo'ladi.

### 3.7. ⑦ Platformadan tashqari: Telegram sticker to'plami

**Eng arzon tarqatish kanali.** Telegram to'plami — bepul, `@rankwant`
kanaliga tabiiy mos, web byudjetiga **0 KB** qo'shadi. Brend `t.me/rankwant`
allaqachon rasmiy (`CLAUDE.md` 2026-09-19 qarori). Bu tur alohida dizayn
ishini talab qiladi, lekin texnik integratsiya talab qilmaydi — sof foyda.

---

## 4. Uslub variantlari — 12 uslub × 19 palitra muammosi

Bu — loyihaning **eng katta texnik tuzog'i**. 12 uslub bor
(`apps/web/src/layout/styles.ts`):

| Guruh | Uslublar | Muhit |
| --- | --- | --- |
| Ikki muhitli (7) | `dashboard` · `swiss` · `flat` · `material` · `editorial` · `brutal` · `clay` | light + dark |
| Bir muhitli (5) | `terminal` (qorong'u) · `glass` · `neu` (yorug') · `aurora` · `skeu` | bitta |

⇒ **19 palitra**. Agar har uslubga alohida chizilgan maskot kerak bo'lsa:
19 palitra × 5 poza × 4 daraja ≈ **380 ta aktiv**. Bu boshqarib bo'lmaydigan
son — va `tools/brand.py` naqshiga ham sig'maydi.

### Uch strategiya

| # | Strategiya | Aktiv soni | Narx | Tavsiya |
| --- | --- | --- | --- | --- |
| **A** | **Bitta neytral shakl + token rang** | ~20 | Past | ✅ **birinchi** |
| **B** | Uslubga moslashuvchi «kostyum» | ~380 | Yuqori | ⚪ keyin, 3–4 uslub uchun |
| **C** | Ikonka-uslub (mavjud `illustration` ichida) | ~5 | Eng past | ✅ arzon boshlanish |

**A strategiyasi nega ishlaydi:** shakl bitta qoladi, rang esa
`var(--rw-accent)` / `var(--rw-ground)` / `var(--rw-text)` dan keladi. Uslub
almashganda maskot **o'zi** moslashadi — chunki 19 palitraning hammasi shu
tokenlarni e'lon qiladi. Bu `check_contrast.py` bilan ham uyg'un: kontrast
token darajasida allaqachon o'lchangan, ya'ni maskot meros oladi.

**B strategiyasi (keyinroq, tanlab):** faqat eng ko'p ishlatiladigan
uslublar uchun. Taxminiy ustuvorlik: `clay` (zavod uslubi, D57) ·
`dashboard` · `terminal` · `editorial`. Har biri uchun «kostyum»:

| Uslub | Kostyum g'oyasi |
| --- | --- |
| `clay` | yumshoq, katta radius, yumshoq soya |
| `brutal` | qalin qora kontur, tekis to'ldirish, soya yo'q |
| `terminal` | blok-belgilar, monospace panjara, scanline |
| `aurora` | gradient yorug'lik, glow |
| `neu` | botiq/bo'rtiq relef, past kontrast |
| `glass` | shaffof panel, orqadagi fon ko'rinadi |

### Muhim dizayn eslatmasi

RankWant auditoriyasi — **o'rta maktab o'quvchisidan ICPC talabasigacha**
([`docs/01-vision/README.md`](../../01-vision/README.md)). Ya'ni maskot
**bolalarcha bo'lmasligi** kerak, aks holda universitet segmenti uni
«o'yinchoq» deb qabul qiladi. Ohang: **chaqqon va rag'batlantiruvchi**,
«kawaii» emas. Bu chegara — §11 dagi asosiy risk.

---

## 5. Dizayn usullari — qanday chizish

### 5.1. Vektor (SVG) — yagona to'g'ri javob

| Usul | Mos? | Sabab |
| --- | --- | --- |
| **Qo'lda SVG** (Figma/Inkscape → `path`) | ✅ | Manba bitta fayl, `tools/brand.py` naqshiga mos |
| **Rastr (PNG/AI generator)** | ⚠️ | Faqat qoralama uchun. `belgi-generated/` tajribasi: JPEG, shaffoflik yo'q, 16px da 101 xil rang |
| **Ikonka registridan yig'ish** | ⚠️ | Tez, lekin «qahramon» chiqmaydi |
| **3D (Blender → render)** | ❌ | 19 palitra uchun qayta render; byudjetga sig'maydi |

**Qurilish qoidalari (Crest'dan meros):**

1. Kanvas va `viewBox` — Crest kabi (1024 tizimi) yoki 24/32px ikonka to'ri.
2. Ranglar — **faqat** `var(--rw-*)` tokenlar; xom hex yozilmaydi
   (`check_design_tokens.py` xom hex'ni ushlaydi).
3. Geometriya parametrlari **hujjatga** yoziladi (`mark-crest-params.md`
   naqshi) — «nega shunday ko'rinadi» savoliga javob faylda qolsin.
4. Silhouette testi: **16 / 24 / 32 px** da taniladimi (LOCK-GATE A1/A2 mezoni).

### 5.2. Pozalar to'plami (pose sheet)

Har maskot uchun minimal to'plam: `neutral` · `success` · `fail` ·
`thinking` · `celebrate`. Besh poza — 10+ sahifani qoplaydi.

### 5.3. Nomlash va saqlash

`docs/brand/` naqshiga mos: manba `docs/brand/mascot-nuqta.svg` (yoki
`apps/web/public/mascot/`), hosilalar — generator skript orqali. **Qo'lda
tahrirlanmaydi.**

---

## 6. Animatsiya usullari — beshta yo'l, o'lchangan

### 6.1. Taqqoslash

| # | Usul | Format | Runtime | Interaktiv | SSR | Kontrast o'lchanadimi | Holat |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | **Inline SVG + CSS `@keyframes`** | SVG + CSS | **0 KB** | ⚠️ cheklangan | ✅ | ✅ token orqali | ✅ **tavsiya** |
| 2 | Inline SVG SMIL (`<animate>`) | SVG | 0 KB | ❌ | ✅ | ✅ | ⚠️ harakat darvozasi ushlamaydi |
| 3 | **Motion** (`motion` / framer-motion) | React | ~30 KB | ✅ hover/scroll | ⚠️ klient | ✅ | ⚪ interaktiv qahramon uchun |
| 4 | Lottie | JSON | ~60 KB | ⚠️ qisman | ❌ klient | ❌ | ❌ hozircha rad |
| 5 | Rive | `.riv` | ~100 KB | ✅ state machine | ❌ klient | ❌ | ❌ hozircha rad |

### 6.2. ① Inline SVG + CSS — asosiy tavsiya

**Nima uchun:** runtime 0 KB (bundle byudjetiga tegmaydi), serverda chiziladi
(SSR buzilmaydi), rangi CSS `var()` orqali keladi (19 palitra avtomatik,
`check_contrast.py` bilan uyg'un), va harakat darvozasi bilan **to'g'ri**
bog'lanadi — agar klass `animate-` bilan boshlansa.

**Naqsh:**

```css
/* theme.css — mavjud darvozaga ulanadi */
.rw-mascot { fill: var(--rw-accent); }
.rw-mascot-blink { animation: rw-mascot-blink 4s ease-in-out infinite; }

@media (prefers-reduced-motion: reduce) {
  .rw-mascot-blink { animation: none !important; }   /* ← klassni sanash shart */
}
```

### 6.3. ④⑤ Nima uchun Lottie/Rive hozircha rad

2026-09-15 da ikonkalar uchun aynan shu savol ko'rildi va javob
[`ANIMATED-SOURCES.md`](../2026-09-15-icon-comparison/ANIMATED-SOURCES.md) da
yozilgan. Uch sabab — va uchtasi ham **maskotga ham tegishli**:

| Sabab | Ikonkada | Maskotda |
| --- | --- | --- |
| Runtime og'irligi | 46 KB to'plam uchun 60–100 KB juda ko'p | 0 KB (SVG) vs 60–100 KB (runtime) |
| **Kontrast o'lchanmaydi** | `check_contrast.py` rangni o'qiy olmaydi | **Aynan shu** — 19 palitra qo'lda tekshiriladi |
| SSR | Klient tomonida | Klient tomonida |

**Farq bor:** maskot ikonkadan **kam uchraydi** (bitta sahifada bitta),
shuning uchun runtime narxi oqlanishi mumkin edi. Lekin «kontrast
o'lchanmaydi» sababi **kuchida qoladi** — va bu bizning eng qimmat
darvozamiz. Shuning uchun: **faqat bitta hero lahza** uchun, agar kelajakda
byudjet aniq oshirilsa va kontrast qo'lda o'lchansa.

### 6.4. ② SMIL haqida ogohlantirish

SMIL `<animate>` **CSS animatsiya emas**. Ya'ni `[data-motion="off"]` bloki
uni to'xtatmaydi. Ishlatilsa, `prefers-reduced-motion` va
`data-motion` ni **JS bilan** tekshirib `svg.pauseAnimations()` chaqirish
kerak. Bu qo'shimcha murakkablik — §6.2 yo'li soddaroq.

### 6.5. Harakat darajalari xaritasi

Har poza uchun qaysi darajada nima bo'lishi **oldindan** belgilanadi:

| Daraja | Maskot xatti-harakati |
| --- | --- |
| `full` | To'liq: nafas olish, ko'z qisish, sakrash, iz qoldirish |
| `mild` | Faqat holat o'zgarishi (poza almashinuvi), dekorativ harakat yo'q |
| `off` / `reduce` | **Statik poza** — shakl qoladi, harakat yo'q |
| `system` | OS qarori: `prefers-reduced-motion` bo'lsa → statik |

### 6.6. Qo'shimcha o'lchov — Lottie va Rive prototipi (2026-10-05)

Yuqoridagi xulosa **da'vo** edi. Keyin uch yo'l **haqiqatan qurilib o'lchandi**
(`prototypes/mascot-lab/`). Natija xulosani o'zgartirmadi, lekin **sababini**
aniqlashtirdi — va bittasi kutilmagan chiqdi.

**a) Lottie qo'lda yozildi va chizildi.** After Effects'siz ham Lottie — bu JSON.
Maskot uchun 3 qatlamli animatsiya qo'lda yozildi: cho'qqilar (2 path), nuqta
(ellips, 3 s bob), ko'zlar (2 ellips, miltillash). Headless `jsdom` da
tekshirildi: **10 `<g>`, 7 shakl, 5 to'ldirilgan, 1 stroke, 90 kadr, 3.00 s** —
ya'ni JSON haqiqatan chiziladi, «yashil» degan gap emas.

| Yo'l | Runtime (gzip) | Asset |
| --- | --- | --- |
| SVG + CSS | **0 B** | ≈ 1 200 B |
| Lottie (`lottie_svg`) | **62 260 B** | 3 467 B (628 B gzip) |
| Rive (`@rive-app/canvas`) | **496 256 B** | 58 792 B (namuna `.riv`) |

**b) Rive ning narxi kutilganidan 8× katta.** `rive.js` yolg'iz **52 761 B**
gzip, lekin unga `rive.wasm` ham kerak: **443 495 B** gzip (1 192 331 B xom).
Jami **496 256 B** — Lottie'dan **~8×**, SVG'dan **~500×**. Wasm ni inline ham,
tree-shake ham qilib bo'lmaydi: u alohida so'rov. Bu raqam 2026-09-15 dagi
ikonka tahlilida yo'q edi (u yerda faqat ~100 KB deb yozilgan) — **o'sha
hujjatdagi raqam kam baholangan**.

**c) Kutilmagan topilma — kontrast argumenti YUTMAYDI.** Muzlatilgan clay
rangi (`#7c3aed`) 19 palitrada WCAG 3:1 ga urildi. Natija:

| O'lchov | Natija |
| --- | --- |
| Muzlatilgan `#7c3aed` yiqiladi | **2 / 19** (flat·dark 2.33, glass·single 2.44) |
| Palitraning **o'z** `--rw-accent` i yiqiladi | **2 / 19** (brutal·light 2.44, skeu·single 2.60) |

Ya'ni **hisob teng** — kontrast bilan Lottie'ni ayblab bo'lmaydi. Haqiqiy dalil
**moslashuv**: muzlatilgan rang palitraning o'z accent'idan o'rtacha **140**
(maks. **273**, `brutal`) RGB masofada. Shakl to'g'ri, rang begona: terminal'da
yashil fonda binafsha, brutal'da sariq fonda binafsha. **Bitta palitrada to'g'ri,
18 tasida begona.**

> Bu — `MEMORY.md` dagi qoidaning amaliy isboti: *hujjat = gipoteza, kod =
> haqiqat*. Dastlabki da'vo («kontrast yiqiladi») o'lchovda **kuchsiz** chiqdi;
> kuchli dalil boshqa o'qda edi.

**d) Harakat darvozasi — eng jiddiy nuqson, jonli isbotlandi.** Labda
`data-motion="off"` tanlansa: SVG maskot CSS darvozasi bilan **to'xtaydi**, lekin
**Lottie va Rive hamon o'ynaydi**. Sabab: ular CSS animatsiya emas — o'z
dvigateli. Ya'ni §2.1 dagi darvoza **runtime bilan kelgan harakatni umuman
ko'rmaydi**. Buni tuzatish uchun har player uchun alohida JS hook kerak
(`prefers-reduced-motion` ni tinglab, `pause()` chaqirish). Bu — a11y nuqsoni
bo'lardi: «harakatni kamaytir» tanlagan foydalanuvchi hamon harakat ko'rardi.

**e) Yo'l-yo'lakay topilgan bo'shliq.** `--rw-accent` ning o'z `--rw-ground`
ustidagi nisbati ikki palitrada 3:1 dan past: `brutal`·light **2.44**,
`skeu`·single **2.60**. `tools/check_contrast.py` bu juftlikni tekshirmaydi —
u `--rw-accent-fg` ↔ `--rw-accent` juftligini va matn zinapoyalarini ko'radi.
Alohida qaror talab qiladi.

**f) 3D — rad etildi, o'lchov bilan.** Labda maskot 16/24/32/64 px da
chizildi: vektor shaklni saqlaydi. Brend qoidasi (`LOCK-GATE` A1: belgi 16px da
tanilishi shart) vektorni talab qiladi; 3D render 16px da yumshoq dog' bo'ladi,
har o'lcham uchun qayta render va 19 palitra uchun qayta sozlash talab qiladi.
**Yutuq 16px da ko'rinmaydi, narxi esa ko'rinadi.**

**Natija:** §6 dagi tavsiya o'zgarmadi, lekin endi **dalil bilan** turadi:
SVG + CSS (0 KB) asosiy yo'l; Lottie — faqat bitta hero lahza uchun va palitra
qulflangan bo'lsa; Rive — 496 KB narxini oqlaydigan interaktiv holat mashinasi
kerak bo'lsagina; 3D — yo'q.

---

## 7. Vositalar va texnologiyalar

### 7.1. Chizish

| Vosita | Narx | Nima uchun |
| --- | --- | --- |
| **Inkscape** | bepul (GPL) | SVG tug'ma, `path` boshqaruvi, repoga toza chiqadi |
| Figma | bepul / $ | Jamoa bilan variant tanlash, prototip |
| Penpot | bepul (ochiq) | Figma muqobili, o'z-o'zida joylash |
| Blender | bepul | Faqat 3D kerak bo'lsa (tavsiya etilmaydi) |

### 7.2. Animatsiya

| Vosita | Format | Qayerda ishlatiladi |
| --- | --- | --- |
| **Qo'lda CSS keyframes** | CSS | ✅ asosiy yo'l |
| SVGator | SVG+CSS/JS | Eksport SVG+CSS bo'lsa ✅; JS runtime kerak bo'lsa ❌ |
| After Effects + Bodymovin | Lottie JSON | ⚠️ §6.3 cheklovlari |
| Rive Editor | `.riv` | ⚠️ §6.3 cheklovlari |

### 7.3. Repodagi mavjud qurollar (qayta ishlatiladi)

| Qurol | Vazifasi |
| --- | --- |
| `tools/brand.py` | Bitta SVG → favicon/PWA/BIMI/OG — maskot ham shu naqshda |
| `tools/og-image.py` | OG rasm generatori — maskotni shu yerga qo'shish |
| `tools/gen-verdict-icons.mjs` | Verdikt ikonkalari — maskot pozalari shunga ulanadi |
| `tools/check_contrast.py` | 19 palitra AA — maskot rang darvozasi |
| `tools/check_design_tokens.py` | Xom hex'ni ushlaydi — token majburlaydi |
| `tools/check_bundle_budget.py` | Runtime narxini ushlaydi |
| `tools/check_i18n.py` | Matn kalitini majburlaydi |

**Ya'ni:** yangi vosita deyarli kerak emas. Kerak bo'lgani — **yangi darvoza**
(maskot qabul ro'yxati, LOCK-GATE naqshida).

---

## 8. Integratsiya yo'llari — aniq nuqtalar

Har nuqta: qayerga, nima uchun, qanday shart bilan.

| # | Nuqta | Fayl | Nima qo'shiladi | Shart |
| --- | --- | --- | --- | --- |
| 1 | **Bo'sh holat** | `apps/web/src/components/ui/EmptyState.tsx` | `illustration` variantiga ixtiyoriy `mascot` prop | Eng arzon. 10+ sahifa darhol qamrab olinadi |
| 2 | **Yangi komponent** | `apps/web/src/components/ui/Mascot.tsx` (yangi) | `pose` + `size` + `decorative` proplari | `aria-hidden` standart (Avatar/EmptyState naqshi) |
| 3 | **404 / xato** | `apps/web/src/app/not-found.tsx` (tekshirilsin) | `illustration` + maskot | Statik poza |
| 4 | **Onboarding / landing** | `apps/web/src/app/page.tsx` | Bitta hero lahza | Byudjet tekshiriladi |
| 5 | **Verdikt sahifasi** | verdikt ikonka registri | Poza: AC/WA/TLE | `check_verdict_codes.py` buzilmaydi |
| 6 | **Profil / unvon** | `UserTitle`, `TitleBand` (`lib/identity.ts`) | Yutuq pozasi | ADR-0018 ga mos |
| 7 | **OG rasm** | `tools/og-image.py` | Maskot `og-default.png` da | Statik PNG (ijtimoiy tarmoq animatsiya ko'rsatmaydi) |
| 8 | **Favicon / PWA** | `tools/brand.py` | Maskot mark varianti | **Crest qulfi** — LOCK-GATE bilan to'qnashmasin |
| 9 | **Email sarlavhasi** | `tools/brand.py` → `mark-96.png` | Maskot emailda | ⚠️ Email klientlar animatsiya ko'rsatmaydi — **faqat statik** |
| 10 | **Telegram sticker** | repo tashqarisi | Sticker to'plami | Web byudjeti 0 KB |

**Tavsiya etilgan tartib:** 1 → 2 → 3 → 7 → 10 → 5 → 6 → 4 → 8 → 9.
Ya'ni eng arzon va eng xavfsizidan boshlab, brend qulfiga tegadiganlar (8, 9)
**oxirida**.

---

## 9. Jonlantirish bosqichlari — ishlab chiqarish quvuri

Yetti bosqich. Har bosqichda **chiqish sharti** bor — keyingisiga o'tish
uchun oldingisi yopilishi kerak.

| # | Bosqich | Ish | Chiqish sharti |
| --- | --- | --- | --- |
| 1 | **Tushuncha** | Qahramon kim, nega, qayerda ishlatiladi | Brend qarori + ism (§12 D1) |
| 2 | **Qoralama** | Qo'lda eskiz, silhouette testi 16/24/32/64px | 16px da taniladi (LOCK-GATE A1 mezoni) |
| 3 | **Vektor qurish** | Manba SVG + geometriya parametrlari hujjatda | `check_design_tokens.py` toza — 0 xom hex |
| 4 | **Pozalar** | `neutral` · `success` · `fail` · `thinking` · `celebrate` | 5 poza bir uslubda izchil |
| 5 | **Harakat spetsifikatsiyasi** | Har poza × har daraja (`full`/`mild`/`off`) | `off` da **statik poza** bor |
| 6 | **Darvozadan o'tkazish** | Kontrast (19 palitra) · bundle · token · a11y · i18n (matn yo'q) | `check_contrast.py` + `check_bundle_budget.py` yashil |
| 7 | **Integratsiya** | Komponent + generator skript + `CLAUDE.md` qaror qatori | `check_decisions.py` yozuvi + salbiy test |

⚠️ **5-bosqich — eng ko'p e'tibordan chetda qoladigan joy.** Harakat odatda
«oxirida qo'shiladi». Bu yerda esa u **shartnoma**: har poza uchun statik
muqobil §2.1 dagi darvozaga mos yozilishi kerak.

---

## 10. Yo'l xaritasi — bosqichlar (muddat emas, hajm)

**Faza 1 — Poydevor (arzon, xavfsiz)**

1. Brend qarori: qahramon + ism (§12 D1, D2).
2. Manba SVG + geometriya hujjati.
3. `Mascot.tsx` komponenti + `EmptyState` integratsiyasi (nuqta 1, 2).
4. Qabul ro'yxati — LOCK-GATE naqshida (`docs/brand/mascot-gate.md`).

**Faza 2 — Ko'rinish**

5. 5 poza + harakat spetsifikatsiyasi.
6. 404 / xato / onboarding (nuqta 3, 4).
7. OG rasm + Telegram sticker to'plami (nuqta 7, 10).

**Faza 3 — Chuqurlik (ixtiyoriy, o'lchovdan keyin)**

8. Verdikt pozalari (nuqta 5) — mavjud taksonomiyaga ulanadi.
9. Yutuq / unvon pozalari (nuqta 6) — ADR-0018 bilan.
10. Tier evolyutsiyasi — **4 davr**, 16 ta alohida emas (§3.4).
11. Favicon/PWA/email (nuqta 8, 9) — **Crest qulfi yopilgach**.

⚠️ Faza 3 **faqat Faza 1–2 o'lchangan natija bergach** boshlanadi. Sabab:
`MEMORY.md` da yozilgan tartib — **ishonch → ishlab chiqarish → o'lchov → AI →
B2B**. Maskot — «o'lchov»dan keyingi qatlam, undan oldin emas.

---

## 11. Xavflar va rad etilgan variantlar

### Xavflar

| # | Xavf | Nega jiddiy | Yumshatish |
| --- | --- | --- | --- |
| R1 | **Ohang xatosi** — maskot bolalarcha chiqadi | Auditoriya universitet/ICPC talabasini ham o'z ichiga oladi; ular «o'yinchoq» platformadan ketadi | Chaqqon-uslub, «kawaii» emas; HITL tasdiq |
| R2 | **19 palitra portlashi** | 19 × poza × daraja — boshqarib bo'lmaydi | A strategiyasi (§4): token rang |
| R3 | **Harakat darvozasi buzilishi** | `mild` faqat `animate-` ni ushlaydi; SMIL umuman ushlanmaydi | Nomlash qoidasi + `prefers-reduced-motion` ro'yxatiga qo'shish |
| R4 | **Bundle byudjeti** | Runtime qo'shilsa build yashil qoladi, foydalanuvchi internetida bilinadi | SVG+CSS (0 KB); runtime faqat o'lchov bilan |
| R5 | **Brend drij** | Maskot Crest'dan uzilsa, ikki xil brend til paydo bo'ladi | Bitta manba SVG + generator (`tools/brand.py` naqshi) |
| R6 | **Crest qulfi bilan to'qnashuv** | Crest hali **locked candidate** — favicon/PWA o'zgarishi qulfni kechiktiradi | Nuqta 8, 9 ni **oxiriga** qoldirish |
| R7 | **Kontent yuki** | 16 tier × poza = doimiy dizayn talabi | 4 davrga jamlash |
| R8 | **Diqqat chalg'ishi** | O'quv mahsulotida bezak asosiy ishni bosib ketadi | Maskot `aria-hidden`, matn tashimaydi, statik muqobili bor |

### Rad etilgan variantlar

| Variant | Nega rad |
| --- | --- |
| Lottie/Rive ni **hozir** qo'shish | Kontrast o'lchanmaydi + SSR + runtime (§6.3) |
| 3D render qilingan maskot | 19 palitra uchun qayta render; byudjetga sig'maydi |
| AI rastr generator bilan yakuniy aktiv | `belgi-generated/` tajribasi: shaffoflik yo'q, 16px da 101 rang |
| Har uslubga alohida qahramon | 12 ta mustaqil brend — boshqarib bo'lmaydi |
| 16 tier uchun 16 ta alohida maskot | Kontent yuki; 4 davr yetarli |
| Qvant tangasini qahramon qilish | Brend ikkiligini buzadi (principle #4) |

---

## 12. Qarorlar talab qilinadi (Saidakbar aka)

Bularsiz Faza 1 boshlanmaydi. Har biri — **HITL qarori**, agent o'zi
tanlamaydi (`CLAUDE.md` § «Saidakbar aka qarorlari»).

| # | Savol | Variantlar | Tavsiya |
| --- | --- | --- | --- |
| **D1** | Qahramon kim va ismi nima? | Nuqta (Crest nuqtasi) · Cho'qqi · boshqa | **Nuqta** — geometriyasi qulflangan |
| **D2** | Uslub strategiyasi? | A (neytral+token) · B (kostyum) · C (ikonka) | **A**, keyin tanlab B |
| **D3** | Birinchi integratsiya nuqtasi? | Bo'sh holat · 404 · onboarding | **Bo'sh holat** — eng arzon |
| **D4** | Animatsiya runtime ruxsati? | Faqat SVG+CSS · Motion ham · Lottie/Rive ham | **Faqat SVG+CSS** |
| **D5** | Maskot = yangi brend aktivi — qabul ro'yxati bormi? | LOCK-GATE naqshida yangi ro'yxat · mavjud LOCK-GATE ga qo'shish | **Yangi ro'yxat** (`docs/brand/mascot-gate.md`) |
| **D6** | Tier evolyutsiyasi? | 16 pog'ona · 4 davr · hozircha yo'q | **4 davr**, Faza 3 da |

---

## 13. Manbalar — o'lchangan fayllar

Bu yozuvdagi har raqam quyidagilardan o'qildi (2026-10-05):

| Da'vo | Manba |
| --- | --- |
| Animatsiya kutubxonasi yo'q | `apps/web/package.json` |
| Harakat darajalari va darvoza selektorlari | `apps/web/src/app/theme.css` (≈1300, 1820–1950) |
| 12 uslub, 7 ikki muhitli | `apps/web/src/layout/styles.ts` |
| Bo'sh holat 3 shakli | `apps/web/src/components/ui/EmptyState.tsx` |
| Yuklanish 10 varianti | `apps/web/src/lib/theme/loading.ts` |
| Crest geometriyasi | [`docs/brand/mark-crest-params.md`](../../brand/mark-crest-params.md) |
| Brend naqshi va generator | [`docs/brand/README.md`](../../brand/README.md) |
| Brend qabul darvozasi | [`docs/brand/LOCK-GATE.md`](../../brand/LOCK-GATE.md) |
| 19 palitra, AA | `tools/check_contrast.py` |
| Bundle byudjeti | `tools/check_bundle_budget.py` |
| Lottie/Rive tahlili (ikonkalar) | [`ANIMATED-SOURCES.md`](../2026-09-15-icon-comparison/ANIMATED-SOURCES.md) |
| 16 pog'onali narvon | [`ADR-0027`](../../07-adr/0027-ladder-16-tiers.md) |
| Unvon / yutuq | [`ADR-0018`](../../07-adr/0018-titles-roles-achievements.md) |
| Auditoriya | [`docs/01-vision/README.md`](../../01-vision/README.md) |
| `planets/` ishlatilmaydi | `grep -rn "planets" apps/web/src docs` → 0 natija |
| Lottie/Rive hajmlari, kontrast 2/19, masofa 140 | `prototypes/mascot-lab/` (lab + `mascot.lottie.json`) |
| Lottie chizilishi (7 shakl, 3.00 s) | headless `jsdom` + `lottie-web/build/player/lottie_svg` |
| Rive runtime hajmi | `curl` + `gzip -9`: `rive.js` 52 761 B, `rive.wasm` 443 495 B |

### Yo'l-yo'lakay topilgan ikki kichik nuqson

1. **`tools/check_contrast.py` docstring'i eskirgan.** U hali «12 uslub,
   oltitasida qorong'u varianti — jami 18 palitra» deydi. Kod bo'yicha esa
   `clay` 2026-10-05 da `dual: true` bo'ldi (CLAUDE.md o'sha kuni yozilgan),
   ya'ni **7 ta ikki muhitli, 5 ta bir muhitli ⇒ 19 palitra**. O'lchov kodda
   to'g'ri, izohda emas.

2. **`--rw-accent` ↔ `--rw-ground` juftligi tekshirilmaydi.** O'lchandi: ikki
   palitrada 3:1 dan past — `brutal`·light **2.44**, `skeu`·single **2.60**.
   `check_contrast.py` `--rw-accent-fg` ↔ `--rw-accent` juftligini va matn
   zinapoyalarini ko'radi, accent'ning sahifa zaminidagi holatini emas. Bu
   juftlik amalda uchraydi (accent rangli katta sarlavha, tugma, maskot) —
   alohida qaror talab qiladi.

---

## 14. Yakuniy javob — bir jadvalda

| Savol | Javob |
| --- | --- |
| **Qanday dizayn usuli?** | Vektor SVG, geometriyasi Crest'dan, rangi tokendan |
| **Qanday animatsiya usuli?** | Inline SVG + CSS `@keyframes`; harakat darvozasi bilan bog'langan |
| **Kerakli vositalar?** | Inkscape (chizish) · mavjud repo qurollari (generator, darvozalar) · yangi: bitta qabul ro'yxati |
| **Texnologiyalar?** | React 19 + Next 16 (bor) · CSS (bor) · **yangi runtime yo'q** |
| **Integratsiya yo'llari?** | 10 nuqta; birinchisi — `EmptyState` `illustration` |
| **Maskot turlari?** | 7 ta: qahramon · holat · verdikt · tier · Qvant/streak · yutuq · sticker |
| **Uslub variantlari?** | 3 strategiya; A (neytral+token) birinchi, B (kostyum) tanlab |
| **Jonlantirish bosqichlari?** | 7 bosqich, har birida chiqish sharti |

**Bir gapda:** RankWant maskotni **allaqachon ko'tarib yuradi** — u Crest'dagi
nuqta. Qolgani — uni jonlantirish, va buni qilishning eng arzon, eng xavfsiz
va brendga eng sodiq yo'li **SVG + CSS**, bitta manba va tokendan rang olish.

---

*Keyingi qadam: §12 dagi D1–D6 bo'yicha Saidakbar aka qarori. Qaror
bo'lmasa, Faza 1 boshlanmaydi — bu ataylab shunday.*
