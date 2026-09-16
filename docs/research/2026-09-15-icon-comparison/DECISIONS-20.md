# RankWant — Ikonka tizimi: 20 qaror

**Sana:** 2026-09-15 · **Usul:** human-in-the-loop (CTO tavsiyasi + foydalanuvchi qarori)
**Holat:** 20/20 savol berildi · **20 tasi qaror qilindi** · ochiq savol yo'q
**Yangilangan:** 2026-09-16 — D13–D16 va D20 yopildi (D20 = **①**)

---

## To'lqin 1 — Asos (D1–D4)

| # | Savol | Qaror | Holat |
|---|---|---|---|
| **D1** | Ikonka uslubi | **Outline + Solid + Duotone** — uch uslub, bitta emas | ✅ |
| **D2** | Nechta ikonka kerak | «41 ta emas, ancha ko'p» → **to'liq inventarizatsiya** qilindi: **~220 nuqta** (48 tasi qoplangan = 20 %) | ✅ |
| **D3** | O'lchamlar | **16 / 20 / 24 / 32** px | ✅ |
| **D4** | Nomlash | **Semantik kalit + mapping** (kod kalitni biladi, to'plamni emas) | ✅ |

**Inventarizatsiya natijasi:** 79 sahifa va 40+ komponent skanerlandi →
**48 mavjud ikonka**, **~220 kerak**. Ya'ni **qoplama 20 %**.

---

## To'lqin 2 — Yo'nalish o'zgardi (D5–D8)

| # | Savol | Qaror | Holat |
|---|---|---|---|
| **D5** | Nechta to'plam | ⚠️ *«Atigi 2 dona emas — 5-10 ta»* | ✅ |
| **D6** | Brend ikonkalari | ⚠️ *«Foydalanuvchiga tanlov berilsin, 3-4 xil uslubda, Simple Icons + logos»* | ✅ |
| **D7** | Verdikt ko'rinishlari | *«10 xil variantni web sahifada ko'rmoqchiman»* → `verdicts.html` | ✅ |
| **D8** | Markdown panel | **To'liq panel** | ✅ |

### 🔑 Ikki muhim burilish
1. **Bitta to'plam emas — 5–10 ta to'plam.** Ya'ni ikonka to'plami **foydalanuvchi sozlamasi** bo'ladi.
2. **Foydalanuvchi o'zi tanlaydi** — 3–4 xil uslubda, brend logotiplari alohida.

---

## To'lqin 3 — Verdikt va to'plamlar (D9–D12)

| # | Savol | Qaror | Holat |
|---|---|---|---|
| **D9** | Verdikt turlari | **Barcha 10 tasini** (①–⑩) | ✅ **kodda** |
| **D10** | To'plamlar ro'yxati | **10 ta**: Lucide · Phosphor (Outline/Solid/Duotone) · Heroicons (Outline/Solid) · Tabler · Simple Icons · Bootstrap Icons · Remix Icon | ✅ |
| **D11** | Tanlash usuli | **Appearance bo'limi + jonli namuna; standart — Lucide** | ✅ |
| **D12** | Qoplama kafolati | **Semantik kalit + xarita + build tekshiruvi.** Yetishmagan ikonka asosiy to'plamdan **olinmasin** (hozircha). Vizual tekshirib, keyin qaror | ✅ |

### D9 natijasi — kodda bajarildi
`components/ui/Verdict.tsx` — **bitta komponent, 10 variant + `auto`**.
Ma'lumot `lib/theme/verdict.ts` dan (10 verdikt × kod/rang/ikonka/nom/izoh).

| # | id | Ko'rinish | Qayerda |
|---|---|---|---|
| ① | `badge` | rangli nishon + kod | zich jadval |
| ② | `plain` | faqat ikonka, rangsiz | eng izchil ro'yxat |
| ③ | `icon` | ikonka + kod | urinishlar |
| ④ | `full` | ikonka + to'liq nom | masala sahifasi |
| ⑤ | `circle` | to'ldirilgan doira | mobil |
| ⑥ | `dot` | nuqta + kod | log ro'yxati |
| ⑦ | `box` | ramkali kvadrat | ikonka paneli |
| ⑧ | `bar` | chap chiziq + nom | ogohlantirish |
| ⑨ | `percent` | ikonka + kod + foiz | baholash |
| ⑩ | `card` | katta ikonka + izoh | natija kartasi |
| — | `auto` | ekranga qarab: ⑤ → ③ → ④ | **standart** |

---

## To'lqin 4 — Platforma sohalari (D13–D16) · ✅ bajarildi

Saidakbar aka barcha to'rttasiga bir xil javob berdi:
*«Variantlarni web dashboardda taqdim qil, tanlayman»*.

→ **`icon-comparison/patterns.html`** yasaldi (36 bo'lim, 56 namuna, 9 animatsiya).

| # | Savol | Variantlar | Holat |
|---|---|---|---|
| **D13** | Holat ikonkalari (ok/warn/bad/info) | **10 variant** tanlandi | ✅ **kodda** |
| **D14** | Bo'sh holat va xato ekranlari | **3 variant** tanlandi (`full`/`card`/`illustration`) | ✅ **kodda** |
| **D15** | Qidiruv, filtr, jadval | **8 naqsh** tanlandi | ✅ **kodda** |
| **D16** | Yuklanish animatsiyasi | **10 variant**, Customizer'da tanlanadi | ✅ **kodda** |

---

## To'lqin 5 — Texnik (D17–D20) · ✅ bajarildi

| # | Savol | Qaror | Holat |
|---|---|---|---|
| **D17** | 2200 ikonkani qanday yetkazamiz | **Tanlangan to'plamni dinamik yuklash** — standart (Lucide) asosiy bundle ichida, qolgani alohida bo'lak. Birinchi yuklanish yengil qoladi | ✅ |
| **D18** | Kalit nomlash | **`domen.ob'ekt.holat`** — `verdict.accepted`, `nav.dashboard`, `status.warning` | ✅ |
| **D19** | Mobil moslashuv | **O'lcham o'zgarmaydi** (24px hamma joyda), faqat matn qisqaradi | ✅ |
| **D20** | To'plam almashsa nima o'zgaradi | **① — interfeys almashadi, verdikt va brend QAT'IY** | ✅ **tanlandi** |

### D20 — to'rt qamrov varianti
| # | Qamrov | O'zgaradi | Qat'iy |
|---|---|---|---|
| ① | Interfeys almashadi, verdikt va brend qat'iy | nav · amallar · holat | verdikt · brend |
| ② | Interfeys + verdikt | nav · amallar · holat · verdikt | brend |
| ③ | Hammasi | hammasi | — |
| ④ | Faqat navigatsiya va tugmalar | nav · amallar | holat · verdikt · brend |

**Tanlandi: ①.** Saidakbar aka 2026-09-16 da `scope.html` dan shu variantni tanladi.

Sabab: qo'llanma, yordam sahifalari va video darsliklar verdikt belgisiga tayanadi —
u o'zgarsa hamma foydalanuvchida boshqacha ko'rinadi. Brend logotiplari (Telegram,
GitHub, Instagram) ham qat'iy: ularni o'zgartirish brend siyosatini buzardi.

**Amaliy natija:** ikonka to'plami almashganda **nav · amallar · holat** o'zgaradi;
**verdikt · brend** o'zgarmaydi. Registr shu qoidani bilishi shart.

---

## Umumiy holat

**20/20 qaror yopilgan.** Kodga o'tkazish bajarildi (V2, V3, T1).

| Yo'nalish | Holat |
|---|---|
| Verdikt tizimi (10 variant) | ✅ **kodda, testdan o'tgan** |
| Ikonka inventarizatsiyasi (~220 nuqta) | ✅ **bajarildi — 226 kalit** |
| To'plamlar ro'yxati (10 ta) | ✅ **kodda** (`icon-packs.ts`) |
| Tanlash mexanizmi (Appearance) | ✅ **kodda** (Customizer bo'limi) |
| Qoplama tizimi (kalit + xarita + build) | ✅ **kodda** — 9 to'plam × 226 kalit |
| Yetkazish (dinamik yuklash) | ✅ **kodda** (`registry.tsx`) |
| Nomlash sxemasi | ✅ **kodda** (19 domen) |
| Mobil moslashuv | ✅ **kodda** |
| Holat / bo'sh holat / qidiruv / animatsiya | ✅ **kodda** (D13–D16) |
| Qamrov (D20) | ✅ **tanlandi — ①** |
| Kodga o'tkazish | ✅ **bajarildi** — ilova registrdan chizadi |

### Natija (o'lchandi)

| Ko'rsatkich | Qiymat |
|---|---|
| Kalitlar | **248** (226 interfeys + 22 brend) |
| To'plamlar | **9** (+ Simple Icons brend uchun) |
| Qoplama | **9/9 to'plamda 226/226** |
| Generatsiya qilingan komponent | **1369** |
| Hajm | 784 KB xom · **183 KB gzip** |
| Ilovadagi o'tkazilgan fayl | **24** (49 ikonka o'rni) |
| Darvozalar | 10/10 · salbiy test **64/64** |

**To'liq katalog:** `ICON-CATALOGUE.md` (har kategoriya, har kalit, 9 to'plamdagi
nomi). Generatsiya qilinadi: `tools/gen-catalogue.mjs`.

### Muhim: brend **qat'iy** (D20 ①)

Dasturlash tillari (12) va ijtimoiy tarmoqlar (10) — **logotip**. Ular
registrda **yo'q** va `lib/tech-icons.tsx` da yashaydi (Simple Icons).
Phosphor'da Python belgisi yo'q — shuning uchun bu ajratish majburiy.

### Keyingi qadam

1. ~~`patterns.html` va `scope.html` dan variantlarni tanlash~~ → ✅
2. ~~Verdikt ishini commit + push + deploy~~ → ✅
3. ~~10 to'plam tizimini kodga o'tkazish (V2)~~ → ✅ `a96f451`
4. ~~226 kalitni to'ldirish (V3)~~ → ✅ `608f95a`
5. ~~Registrni ilovaga ulash (T1)~~ → ✅ `da9b6a9`
6. Qolgan: dinamik yuklashni production'da o'lchash (T2) · Customizer
   galereyasi (T3) · eski `icons/index.tsx` ni iste'foga chiqarish (T5)

---

*Manbalar: `icon-comparison/` (7 dashboard), `ICON-CATALOGUE.md`,
`ICON-INVENTORY.md`, `ICON-PACK-FEATURE.md`, `LIBRARIES.md`,
`SITES-ANALYSIS.md`, `ANIMATED-SOURCES.md`.*
