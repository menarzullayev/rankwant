# 5 ta sayt — emoji va ikonkalar tahlili

**Sana:** 2026-09-15 · **Usul:** Playwright (headless Chromium 1440×1100) — har bir sayt
ochildi, lazy kontent uchun pastga surildi, DOM'dagi barcha **SVG ikonkalar**,
**icon-font elementlar** va **Unicode emoji** yig'ildi. Faqat o'lchangan narsa yozildi.

---

## 🔴 Birinchi va eng muhim topilma: EMOJI ISHLATILMAYDI

| Sayt | Unicode emoji |
|---|---|
| LeetCode (problemset) | **0** — faqat `©` (copyright belgisi) |
| LeetCode (profil) | **0** — faqat `©` |
| KEP.uz | **0** — faqat `©` |
| RoboContest | **0** — faqat `©` |
| CodeChef | **0** — faqat `©` |

Beshta saytning **hech birida** haqiqiy emoji yo'q. Sabab: emoji tizim shriftiga
bog'liq — Windows'da Segoe UI Emoji, macOS'da Apple Color Emoji, Android'da Noto.
Ya'ni bir xil belgi har qurilmada **boshqacha** ko'rinadi. Jiddiy platformalar
buning o'rniga **SVG ikonka** ishlatadi — u hamma joyda bir xil chiziladi.

⚠️ **Bitta istisno:** KEP.uz **Iconify orqali `twemoji`** to'plamidan foydalanadi
(1 ta ikonka) — bu emoji ning **SVG nusxasi**. Ya'ni emoji "hissi" saqlanadi,
lekin ko'rinish qurilmaga bog'liq emas. Bu to'g'ri yondashuv.

---

## 1. Har bir sayt qanday ikonka tizimini ishlatadi

| Sayt | Tizim | Aniqlangan to'plam | SVG | Icon-font |
|---|---|---|---|---|
| **LeetCode** | Font Awesome (SVG rejimi) | `fa-*` | 36 / 34 | 0 |
| **KEP.uz** | **Iconify** + MUI | `material-symbols` · **`mdi`** · `material-symbols-light` · `twemoji` · `flag` · `logos` | 25 | 8 |
| **RoboContest** | **Lucide** | `lucide-*` (100 %) | 56 | 0 |
| **CodeChef** | Font Awesome (font rejimi) + o'zi | `fa fa-clock-o` · `i-premium-icon` | 2 | 14 |

**Ikki xil texnologiya:**
- **SVG ikonka** (LeetCode, KEP, RoboContest) — har ikonka alohida `path`, to'liq
  nazorat, tree-shaking mumkin
- **Icon font** (CodeChef) — belgi kod orqali, eski usul; butun shrift fayli
  yuklanadi, `color` bilan bo'yaladi

⚠️ **LeetCode qiziq holat:** u Font Awesome'ni **SVG rejimida** ishlatadi
(`svg-inline--fa`) — ya'ni FA'ning dizayni, lekin SVG texnologiyasi. Bu ikki
yondashuvning eng yaxshisini oladi.

---

## 2. Kategoriyalar bo'yicha taqsimot

### 🧭 A. Navigatsiya (asosiy menyu va bo'limlar)

| Sayt | Ikonkalar |
|---|---|
| **LeetCode** | `fa-books` (Library) · `fa-swords` (Contest) · `fa-book-open-cover` · `fa-graduation-cap` (Study Plan) · `fa-circle-user` (Discuss) · `fa-chevron-right` |
| **KEP.uz** | `material-symbols` — Practice · Battles · Competitions |
| **RoboContest** | `book` (Masalalar) · `bot` (Urinishlar) · `medal` (Olimpiadalar) · `subscript` (Testlar) · `graduation-cap` (Kurslar) · `list-checks` (O'quv rejalari) · `library` (Algoritmlar) · `route` (Yo'l xaritasi) · `users` · `pen` (Bloglar) · `info` · `code` |
| **CodeChef** | matnli (ikonka yo'q) |

**Maqsad:** bo'lim ma'nosini bir qarashda yetkazish. Ikonka + matn — juftlik
standard. **RoboContest eng boy** — 12 ta bo'limning har biriga alohida ikonka.

### 📊 B. Reyting va statistika

| Sayt | Ikonkalar |
|---|---|
| **RoboContest** | `flame` (Masala ballari) · `circle-check` (Yechilgan masalalar) · `star` (Olimpiada reytingi) · `trophy` (**Robo Rank**) · `chart-no-axes-column` (Statistika, Dasturlash tillari) · `chart-line` (Reyting tarixi) |
| **KEP.uz** | `mdi` — reyting raqamlari yonida (1602, 1094300) |
| **LeetCode** | `fa-arrow-down-arrow-up` (saralash) · Highcharts grafikasi |
| **CodeChef** | Highcharts + `fa-clock-o` (vaqt) |

**Maqsad:** raqamni **rangli** kontekstga bog'lash. Diqqat: RoboContest har
ikonkaga **boshqa rang** bergan — `flame` to'q sariq, `circle-check` yashil,
`star` sariq. Bu raqamni tez ajratishga yordam beradi.

### 🏆 C. Yutuq va mukofot

| Sayt | Ikonkalar |
|---|---|
| **RoboContest** | `award` (Sertifikatni ko'rish) · `crown` (Sertifikatlar) · `shield-check` (Masalalar xaritasi) · `trophy` |
| **KEP.uz** | Achievement sahifasi — MUI + `mdi` |
| **LeetCode** | `fa-star` (yulduzcha) · **Badges 50** · daraja: *"Lazy idler \| Legendary Grandmaster"* |
| **CodeChef** | **5★** (yulduzcha — matn belgisi!) |

⚠️ **Qiziq farq:** CodeChef reyting darajasini **matn yulduzchasi** bilan
ko'rsatadi (`5★narzullayevme`) — bu Unicode belgi, ikonka emas. RoboContest esa
`trophy` va `crown` SVG ikonkalarini ishlatadi.

### 🔒 D. Status va holat

| Sayt | Ikonkalar | Ma'nosi |
|---|---|---|
| **LeetCode** | `fa-lock-keyhole` · `fa-lock` | Premium kontent qulflangan |
| **LeetCode** | `fa-check` | Yechilgan masala |
| **LeetCode** | bayroq SVG (United States) | Foydalanuvchi davlati |
| **KEP.uz** | `iconify--flag` (Uzbekistan) | Davlat |
| **KEP.uz** | `material-symbols-light` | Yengil holat belgisi |
| **CodeChef** | `i-premium-icon` | "Upgrade to Pro" |

**Maqsad:** **qulf** — pul to'lash kerakligini bildiradi (LeetCode Premium,
CodeChef Pro). **Bayroq** — davlatni matnsiz ko'rsatadi. Ikkalasi ham
universal: izoh kerak emas.

### 🔘 E. Tugma va amal (action)

| Sayt | Ikonkalar |
|---|---|
| **LeetCode** | `fa-magnifying-glass` (qidiruv) · `fa-filter` (filtr) · `fa-shuffle` (tasodifiy masala) · `fa-arrow-down-arrow-up` (saralash) · `fa-calendar` (kunlik masala) · `fa-ellipsis` (ko'proq) · `fa-mobile` (mobil ilova) |
| **RoboContest** | `panel-left-close` (yon panelni yig'ish) · `sun` (mavzu) · `globe` (til) · `share2` (ulashish) · `chevron-down` (ochish) |
| **KEP.uz** | `MuiSvgIcon` — Customize paneli |

**Maqsad:** matnli tugmani qisqartirish. **Faqat ikonka** bo'lgan tugmalarda
`aria-label` **shart** — aks holda ekran o'quvchi uni "tugma" deb o'qiydi, xolos.

### 👤 F. Foydalanuvchi va ijtimoiy

| Sayt | Ikonkalar |
|---|---|
| **RoboContest** | `house` (Profil) · `users` (Obuna bo'lish, 38 obunachi, 0 obuna, Ijtimoiy) · `heart-handshake` (Ijtimoiy ma'lumot) · `flag` (Faollik) |
| **LeetCode** | `fa-circle-user` · `fa-ellipsis` |
| **KEP.uz** | `mdi` — Skills, Activity, Contests, Challenges |

---

## 3. Qiyosiy jadval

| Mezon | LeetCode | KEP.uz | RoboContest | CodeChef |
|---|---|---|---|---|
| **To'plam** | Font Awesome (SVG) | Iconify (6 ta) + MUI | **Lucide** (yagona) | Font Awesome (font) + o'zi |
| **Ikonkalar soni** | 36 | 25 | **56** | 2 + 14 font |
| **Emoji** | yo'q | yo'q (lekin `twemoji` SVG bor) | yo'q | yo'q |
| **Icon font** | yo'q | yo'q (MUI ichida) | yo'q | **ha** (`fa fa-clock-o`) |
| **Yondashuv** | FA dizayni + SVG | eng aralash | **eng izchil** | eng eski |
| **Rangli ikonka** | qisman | ha | **ha — har ikonka rangli** | yo'q |
| **Bayroq** | ha (SVG) | ha (`flag`) | ha (`flag`) | yo'q (emoji bilan?) |
| **Grafika** | Highcharts | — | Chart.js (`ch-*`) | Highcharts |

---

## 4. Kuzatilgan naqshlar

### 1. Ikonka + matn — standart juftlik
Hech bir sayt faqat ikonkaga tayanmaydi (asosiy navigatsiyada). Ikonka **tez
tanib olish** uchun, matn **aniqlik** uchun. Faqat tugmalarda (qidiruv, filtr)
ikonka yolg'iz qoladi — u yerda ma'no universal.

### 2. Rang — ma'no tashuvchi
RoboContest har ikonkaga rang beradi: 🔥 to'q sariq (ball), ✅ yashil (yechilgan),
⭐ sariq (reyting), 🏆 asosiy rang (Robo Rank). Bu **raqamni tezroq o'qish**ga
yordam beradi — bir xil kulrang ikonkalar bilan bunday tezlik bo'lmaydi.

### 3. Qulf — biznes model belgisi
LeetCode `fa-lock-keyhole`, CodeChef `i-premium-icon` — ikkalasi ham
"bu yerda pul kerak" degani. Ikonka matndan tezroq ishlaydi va asabiylashtirmaydi.

### 4. Daraja — matn bilan, ikonka bilan emas
LeetCode: *"Legendary Grandmaster"* (matn). CodeChef: `5★` (Unicode belgi).
KEP.uz: `mdi` ikonkasi + raqam. **Yagona standart yo'q** — bu qaror brendga
bog'liq.

### 5. Lucide — eng izchil
RoboContest 56 ta ikonkaning **hammasini** bitta to'plamdan olgan. LeetCode
va KEP.uz aralash ishlatadi (FA + SVG, Iconify 6 ta to'plam + MUI). Aralash
yondashuv **chiziq qalinligi va burchaklarda nomuvofiqlik** beradi.

---

## 5. RankWant uchun xulosa

| Kuzatuv | Bizga tavsiya |
|---|---|
| Emoji ishlatilmaydi | ✅ Bizda ham yo'q — to'g'ri |
| Lucide eng izchil (RoboContest) | ⚠️ Bizda **41 ta qo'lda yozilgan** ikonka — to'plamga o'tish kerak |
| Rang — ma'no tashuvchi | 💡 Reyting ikonkalariga rang berish (hozir hammasi bitta rang) |
| Ikonka + matn juftligi | ✅ Bizda shunday |
| Qulf/bayroq universal | ✅ Bayroq bor, qulf kerak bo'ladi (Premium rejalar uchun) |

**Eng muhim saboq:** raqobatchilarning **uchtasi ham tayyor to'plam** ishlatadi
(Font Awesome, Iconify, Lucide) — qo'lda chizmaydi. Bizning 41 ta qo'lda
yozilgan ikonka **texnik qarz**: yangi ikonka kerak bo'lganda chizish kerak,
uslub almashtirilganda o'zgarmaydi.
