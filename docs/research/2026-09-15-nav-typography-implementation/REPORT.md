# Navigatsiya tizimi va erkin tipografiya — bajarilgan ish

**Sana:** 2026-09-15 · **Loyiha:** RankWant (`apps/web`) · **Holat:** ✅ to'liq ishlaydi

kep.uz dagi ikki bo'shliq yopildi: **navigatsiya tizimi** (Sidenav/Topnav + shape +
responsive + holatlar) va **moslashuvchan tipografiya** (type scale + erkin diapazon).

---

## 1. Yangi va o'zgartirilgan fayllar

| Fayl | Holat | Vazifasi |
|---|---|---|
| `src/lib/theme/typography.ts` | **yangi** | Type scale — yagona manba. 8 daraja (xs…4xl), har biri: o'lcham · satr balandligi · og'irlik · harf oralig'i. Erkin diapazon 75–150 %, zichlik 0.90–1.15, `clampSize`/`clampScale` himoyasi, `TEXT_STYLES` tayyor uslublar |
| `src/layout/nav-config.ts` | **yangi** | `NavMode` (sidenav/topnav), `NavShape` (default/slim/stacked), balandlik konstantalari, `clampNavMode`/`clampNavShape`, `topnavShapeClass` |
| `src/layout/AppTopNav.tsx` | **yangi** | Topnav komponenti: guruh dropdown, burger, mobil drawer, `AppHeader` tugmalari |
| `src/layout/AppShell.tsx` | o'zgardi | Sidenav ↔ Topnav almashinuvi; chap chegara faqat sidenav'da |
| `src/context/SidebarContext.tsx` | o'zgardi | `openMobileSidebar` qo'shildi |
| `src/lib/theme/apply.ts` | o'zgardi | `applyTypography()` chaqiriladi; `data-nav` / `data-nav-shape` yoziladi |
| `src/components/customizer/Customizer.tsx` | o'zgardi | 3 ta yangi bo'lim: **Navigatsiya** · **Panel shakli** · **Shrift o'lchami (slider)** |
| `src/lib/api.ts` | o'zgardi | `AppearancePrefs` ga `scale`, `navMode`, `navShape` |
| `src/context/CustomizerContext.tsx` | o'zgardi | `DEFAULT_APPEARANCE` yangi maydonlar bilan |
| `src/app/layout.tsx` | o'zgardi | SSR inline script: chegara + `data-nav`/`data-nav-shape` |
| `src/i18n/locales/*.ts` (10 til) | o'zgardi | 14 ta yangi kalit |

---

## 2. Navigatsiya tizimi

### Rejimlar
- **Sidenav** — chap panel. 260 px (kengaytirilgan) / 86 px (yig'ilgan), sichqoncha
  ustiga kelganda vaqtincha kengayadi. **kep.uz da bu holat yo'q** — bizda bor.
- **Topnav** — ustki panel. `AppHeader` o'rnini oladi (ikkita header bo'lmasin):
  qidiruv, bildirishnoma, til, hisob — hammasi uning ichida.

### Shakllar (o'lchandi)
| Shakl | Balandlik | Burchak |
|---|---|---|
| Odatiy | **83 px** (mobil 65 px) | 26 px (yumaloq) |
| Yupqa | **39 px** | 0 px (keskin) |
| Qavatma-qavat | **103 px** (mobil 88 px) | 0 px |

kep.uz da shape **faqat balandlik** (83/39/103) — bizda burchak ham.

### Holatlar
| Holat | Qanday ishlaydi |
|---|---|
| **hover** | `rw-hover-bg` — har band uchun |
| **active** | `aria-current="page"` + `menu-item-active`; guruh sarlavhasi ham faollashadi |
| **collapsed** | Sidenav 260 ↔ 86 px, ikonka-rejimida nuqta-indikator |
| **dropdown** | Guruh bosilganda ochiladi; tashqariga bosish / `Esc` / sahifa almashish bilan yopiladi |
| **burger** | Faqat `lg` dan kichik ekranda; mavjud `SidebarContext` ni ishlatadi |

### Responsive (o'lchandi)
| Ekran | Header | Burger | Guruhlar | Drawer |
|---|---|---|---|---|
| 375 px | 65 px | ko'rinadi | 5 | ochiladi (21 havola) |
| 768 px | 65 px | ko'rinadi | 5 | ochiladi (21 havola) |
| 1440 px | 83 px | yashirin | 5 | — |

---

## 3. Erkin tipografiya

- **8 daraja:** `xs` 0.75 rem · `sm` 0.875 · `base` 1 · `lg` 1.125 · `xl` 1.25 ·
  `2xl` 1.5 · `3xl` 1.875 · `4xl` 2.25 — hammasi **`rem`**, ya'ni ildizga ergashadi.
- **Har daraja uchun 4 qiymat:** o'lcham · satr balandligi (1.6 → 1.1) · og'irlik
  (400 → 700) · harf oralig'i (0 → −0.025 em).
- **Erkin diapazon:** slider **75 % dan 150 % gacha**, 5 % qadam. Tez tanlash uchun
  90 / 100 / 110 / 120 % tugmalari qoldi.
- **Zichlik:** `scale` 0.90–1.15 — qadamlar orasidagi nisbatni o'zgartiradi
  (`base` qotib qoladi, shuning uchun sahifa siljimaydi).
- **Mavjud tokenlar ham yangilanadi:** `--text-theme-xs/sm/xl`, `--text-title-sm/md`
  qayta yoziladi — ya'ni eski `text-theme-sm` ishlatgan yuzlab joy ham ergashadi.

### O'lchandi
| Slider | root | body | h1 | `.text-theme-sm` |
|---|---|---|---|---|
| 75 % | 12 px | 12 px | 18 px | 10.5 px |
| 100 % | 16 px | 16 px | 30 px | 14 px |
| 125 % | 20 px | 20 px | 30 px | 17.5 px |
| 150 % | 24 px | 24 px | 36 px | 21 px |

---

## 4. Tekshiruv natijalari

| Tekshiruv | Natija |
|---|---|
| `npx tsc --noEmit` | ✅ 0 xato |
| `npm run lint` | ✅ 0 xato |
| `npm run build` | ✅ muvaffaqiyatli (16 sahifa) |
| Jonli brauzer — panel ochilishi | ✅ 9 ta bo'lim |
| Jonli brauzer — Topnav almashinuvi | ✅ `aside` yo'qoladi, header 1440 px |
| Jonli brauzer — 3 ta shape | ✅ 39 / 83 / 103 px |
| Jonli brauzer — tipografiya | ✅ 12 / 16 / 20 / 24 px |
| Jonli brauzer — responsive | ✅ 375 · 768 · 1440 |
| Jonli brauzer — `pageerror` | ✅ 0 ta |
| **Salbiy test** — buzilgan qiymat | ✅ `size:9999 → 150 %`, `-500 → 75 %`, `"katta" → 16 px` |

---

## 5. Yo'l-yo'lakay topilgan va tuzatilgan 3 ta nuqson

### 1. `nav.main` kaliti yo'q edi — sahifa butunlay qulardi
`AppTopNav` da `t(locale, "nav.main")` ishlatildi, kalit esa qo'shilmagan edi.
`t()` kalitni **tip bilan tekshirmaydi** (`key: string`), shuning uchun typecheck
ushlamadi. Brauzerda esa butun daraxt qulab, `aside` ham, `header` ham yo'qoldi:
```
PAGEERROR: Error: i18n: key "nav.main" missing from the "uz" dictionary
```
**Tuzatildi:** 10 tilga `nav.main` qo'shildi.

### 2. SSR inline script chegarasiz edi — sahifa o'qib bo'lmas holga kelardi
`layout.tsx` dagi `APPEARANCE_INIT` `size` ni to'g'ridan-to'g'ri yozardi. Buzilgan
`localStorage` (`size: 9999`) ildiz shriftini **1599.84 px** ga chiqarib, sahifani
buzardi.
**Tuzatildi:** chegara SSR scriptning o'zida ham qo'yildi (75–150 %, 5 % qadam) +
`data-nav`/`data-nav-shape` qo'shildi. Izohda ogohlantirish: qiymatlar
`typography.ts` bilan mos bo'lishi shart.

### 3. Dev serverda hidratsiya ishlamasdi — `127.0.0.1` ≠ `localhost`
Sinov `127.0.0.1:3000` orqali o'tkazilganda tugma bosilardi-yu, hech narsa
o'zgarmasdi (`aria-expanded="false"` qolaverardi), konsolda esa:
```
WebSocket connection to 'ws://127.0.0.1:3000/_next/hmr?id=...' failed:
Error during WebSocket handshake: net::ERR_INVALID_HTTP_RESPONSE
```
`localhost:3000` bilan konsol xatolari **0** bo'ldi va panel ochildi.
**Saboq:** dev serverni har doim `localhost` orqali sinash kerak.

---

## 6. Nima qo'shilmadi (ochiq)

- `scale` (shkala zichligi) uchun panelda **slider yo'q** — funksiya tayyor
  (`clampScale`, `applyTypography` uni qo'llaydi), lekin UI tugmasi qo'shilmadi.
- Topnav'da **klaviatura navigatsiyasi** (strelkalar bilan guruhlar orasida yurish)
  yo'q — `Esc` va tashqariga bosish ishlaydi.
- `AppSidebar` ga shape ta'sir qilmaydi (ataylab: shape — yuqori panelning shakli).
