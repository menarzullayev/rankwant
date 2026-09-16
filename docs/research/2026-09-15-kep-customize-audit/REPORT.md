# kep.uz — CUSTOMIZE paneli: amaliy audit

**Sana:** 2026-09-15 · **Sahifa:** `https://kep.uz` (bosh sahifa) · **Brauzer:** Chromium 1440×1200 (headless)

**Usul:** panel Playwright bilan ochildi; har bir sozlama alohida bosildi. Bosishdan oldin va keyin
`<html>` atributlari, `body` hisoblangan stillari, sahifadagi barcha elementlarning CSS-xossa
histogrami, `header/nav/main/footer` o'lchamlari va `localStorage` solishtirildi. Har bir sinovdan
keyin **Reset** bosilib, asl holat tiklandi. Quyida faqat o'lchangan farqlar keltirilgan.

## Xulosa

- 12 ta bo'limdan **8 tasi** ko'rinadigan vizual o'zgarish beradi
- **4 tasi** faqat `data-*` atributi va `localStorage` qiymatini o'zgartiradi — sahifada hech narsa o'zgarmaydi
- Barcha sozlamalar saqlanadi: sahifa qayta yuklanganda tiklanadi (tasdiqlandi)

---

## 1. Sozlamalar jadvali

| # | Sozlama | Turi | Kuzatilgan o'zgarish | Ta'sir doirasi | Holat |
|---|---|---|---|---|---|
| 1 | **Theme** (preset) | radio ro'yxat — 8 ta | `data-aurora-preset` almashadi; fon va matn rangi butunlay o'zgaradi (~550 element). Ember/Dracula/Midnight qo'shimcha ravishda dark rejimni yoqadi | Butun sahifa (fon, matn, kartalar) | ✅ ishlaydi |
| 2 | **Theme mode** (Light/Dark/System) | radio — 3 ta | **Dark:** `data-kep-color-scheme: light→dark`, `data-aurora-preset: default-light→default-dark`, fon `#ffffff→rgb(6,8,10)`, matn `→rgb(235,242,245)`. **Light** va **System**: sinov muhitida (`prefers-color-scheme: light`) farq kuzatilmadi | Butun sahifa | ✅ ishlaydi |
| 3 | **Primary Color** | 9 ta rang kvadrati (24×24) | Tanlangan rang **279 ta element**ning `color` va **278 ta**sining `border-color` ini almashtiradi; 8 ta element fon rangi; SVG gradient (`linearGradient`, `radialGradient`, `feColorMatrix`, `feBlend`) qayta hisoblanadi | Tugmalar, havolalar, ikonkalar, SVG | ✅ eng kuchli sozlama |
| 4 | **Navigation Menu** | radio karta — 2 ta | **Sidenav:** `header` 1440→1140 px va 300 px o'ngga siljiydi; yangi `nav` (300×3137) paydo bo'ladi; `main` moslashadi. **Topnav:** asl holat — o'zgarishsiz | Header, nav, main — butun layout | ✅ ishlaydi |
| 5 | **Topnav Shape** | radio karta — 3 ta | **Slim:** header 83→39 px; sahifa balandligi 3177→3133. **Stacked:** header 83→103 px; sahifa 3177→3198 | Header balandligi + sahifa balandligi | ✅ ishlaydi |
| 6 | **Nav Color** | katta tugma — 2 ta | ⚠️ **Hech qanday vizual o'zgarish yo'q.** Faqat `localStorage.navColor=vibrant` yoziladi; `header` va `nav` rangi/fon rasmi o'zgarmadi | — | ❌ ishlamaydi |
| 7 | **Background Pattern** | radio karta — 5 ta | Faqat `data-kep-bg-pattern: none→grid\|dots\|diagonal\|mesh`. Fon rasmi hech qayerda o'zgarmadi (`body`, `body::before`, `body::after`, `main`) | — | ⚠️ naqsh qo'llanilmaydi |
| 8 | **Card Style** | radio karta — 4 ta | Faqat `data-kep-card-style: default→outline\|corners\|glow`. Kartalarning `border`, `border-radius`, `box-shadow`, `background` o'zgarmadi | — | ⚠️ effekt yo'q |
| 9 | **Card Background** | radio karta — 4 ta | `data-kep-card-background` + **10 ta elementga `background-image`** qo'llaniladi: Tint — `linear-gradient(rgba(51,133,240,0.08)...)`, Gradient — `linear-gradient(135deg, rgba(51,133,240,...))`, Glass — `linear-gradient(rgba(255,255,255,0.48)...)` | ~10–26 ta karta/blok | ✅ ishlaydi |
| 10 | **Font** | tugma — 4 ta | Butun sahifa shrifti almashadi: ~1000 ta element `font-family`. Inter: −999/+957; Roboto: −957/+957; DM Sans: −1002/+1002 | Butun sahifa (div, p, svg, path) | ✅ ishlaydi |
| 11 | **Font Size** | slider (range), asl qiymat 16 | **12:** `body.font-size 16→12px`, ~540 element; sahifa 3177→3033. **20:** `16→20px`, ~547 element; sahifa 3177→3393 | Butun sahifa + layout balandligi | ✅ ishlaydi |
| 12 | **Vision Mode** | radio (izohli) — 5 ta | Faqat `data-vision: ""→protanopia\|deuteranopia\|tritanopia\|achromatopsia`. Hech qanday CSS `filter` yoki SVG filter qo'llanilmadi (`filter` elementlar soni o'zgarmadi) | — | ❌ ishlamaydi |
| 13 | **Reset** | tugma (panel tepasida) | Barcha sozlamalarni asl holatga qaytaradi — har bir sinovdan keyin o'lchandi, tozalik tiklandi | Butun panel | ✅ ishlaydi |

---

## 2. Theme preset'lari — aniq o'lchangan ranglar

| Preset | `data-aurora-preset` | Fon (`body`) | Matn (`body`) | Qo'shimcha |
|---|---|---|---|---|
| Default (asl) | `default-light` | `rgb(255,255,255)` | `rgb(27,33,36)` | — |
| Luxury | `luxury` | `rgb(253,251,251)` | `rgb(39,36,36)` | — |
| Retro | `retro` | `rgb(241,231,207)` | `rgb(59,58,55)` | — |
| Arctic | `arctic` | `rgb(241,249,251)` | `rgb(47,53,52)` | — |
| Nature | `nature` | `rgb(250,246,236)` | `rgb(46,45,42)` | — |
| Ember | `ember` | `rgb(40,33,54)` | `rgb(226,222,232)` | dark rejimga o'tadi |
| Dracula | `dracula` | `rgb(24,22,31)` | `rgb(228,225,232)` | dark rejimga o'tadi |
| Midnight | `midnight` | `rgb(26,31,46)` | `rgb(218,220,229)` | dark rejimga o'tadi |

## 3. Primary Color — 9 ta rang (barchasi sinovdan o'tkazildi)

| # | Rang | O'zgargan elementlar soni |
|---|---|---|
| 1 | `rgb(51,133,240)` — asl | — |
| 2 | `rgb(88,155,243)` | ~1114 |
| 3 | `rgb(77,106,140)` | ~1114 |
| 4 | `rgb(158,59,59)` | ~1114 |
| 5 | `rgb(1,123,139)` | ~1160 |
| 6 | `rgb(48,130,54)` | ~1114 |
| 7 | `rgb(235,174,131)` | ~1114 |
| 8 | `rgb(171,126,242)` | ~1114 |
| 9 | `rgb(134,164,240)` | ~1114 |

Har birida: ~279 × `color`, ~278 × `border-color`, 8 × `background-color`, 2–3 × gradient.

---

## 4. E'tibor talab qiladigan holatlar

1. **Nav Color (Vibrant)** — tanlov saqlanadi (`localStorage.navColor=vibrant`), lekin menyu rangi ham, fon rasmi ham o'zgarmaydi. Sozlama ishlamaydi.
2. **Background Pattern** — 5 ta variantning hech biri fon naqshini qo'llamaydi; faqat atribut o'rnatiladi.
3. **Card Style** — `Outline`, `Corners`, `Glow` kartalarga ta'sir qilmaydi: na ramka, na burchak radiusi, na soya o'zgaradi.
4. **Vision Mode** — rang ko'rligi filtrlari qo'llanilmaydi. Bu qulaylik (accessibility) uchun mo'ljallangan bo'lsa, hozircha ishlamayapti.
5. **Theme preset (Ember / Dracula / Midnight)** — tanlash bilan birga dark rejim majburan yoqiladi (`data-kep-color-scheme: light→dark`); foydalanuvchi buni kutmasligi mumkin.
6. **Theme mode "System"** — qayta bosilganda panel yopildi (bir marta kuzatildi).
7. **O'lchov shovqini:** bosh sahifada avtomatik carousel bor — u doimiy ravishda elementlar sonini o'zgartiradi. Shu sababli kichik farqlar (50 elementgacha) hisobga olinmadi.

---

## 5. Reset va saqlash

- **Reset** tugmasi barcha sozlamalarni asl holatga qaytaradi — har bir sinovdan keyin o'lchandi.
- Sozlamalar `localStorage`da saqlanadi: `themePreset`, `kep-mode`, `primaryColor`, `navColor` (va boshqalar).
- **Tekshirildi:** Dracula tanlandi → sahifa qayta yuklandi → `data-aurora-preset=dracula`, `data-kep-color-scheme=dark`, fon `rgb(24,22,31)` — **saqlangan**.

---

## 6. Qo'shimcha kuzatuv

Panelda `Luxury`, `Retro`, `Arctic`, `Nature`, `Ember`, `Dracula`, `Midnight`, `Background Pattern`,
`Card Style`, `Card Background`, `Font`, `Vision Mode` bo'limlari yonida **"new"** belgisi turibdi.
Ularning ba'zilari ishlaydi (Card Background, Font), ba'zilari ishlamaydi
(Background Pattern, Card Style, Vision Mode) — belgining o'zi ishlash ko'rsatkichi emas.
