# Appearance moduli — bajarilgan ishlar (1–3 to'lqin)

**Sana:** 2026-09-15 · **Holat:** ✅ 9 ta feature bajarildi, jonli saytda
**Commit'lar:** `6f9c328` · `46f2749` · `c466abd` — hammasi `origin/main` da

---

## Bajarildi

| # | Feature | Commit | O'lchandi |
|---|---|---|---|
| 1 | **Aniq rang (HEX)** | `6f9c328` | `#0F62FE` → accent `#0155ef` · `#FF0000` → `#cb0000` · buzuq qiymat maydonni tiklaydi |
| 3 | **Qator balandligi / harf oralig'i** | `6f9c328` | ×1.4 → `--rw-text-3xl--line-height=1.68` · ×0.9 → `1.08` · tracking `0.06em` |
| 7 | **Animatsiya darajasi** | `6f9c328` | `system` / `full` / `mild` / `off` — `data-motion` to'g'ri yoziladi |
| 8 | **Eksport / import (JSON)** | `6f9c328` | 472 B fayl, `version=1`, 11 ta appearance + 4 ta a11y kaliti |
| 9 | **Kontent kengligi** | `6f9c328` | 1000 px → `main` 1000 px · 1800 px → 1340 px (viewport cheklovi) |
| 2 | **Shrift juftligi** | `46f2749` | `data-font-heading` + `--rw-font-display` alohida |
| 10 | **Lexend (o'qish shrifti)** | `46f2749` | `data-font=lexend` · `body` shrifti almashadi |
| 4 | **Karta uslubi** | `c466abd` | Odatiy · Chegara · Tekis · Yumshoq soya · Keskin burchak |
| 5 | **Fon naqshi** | `c466abd` | To'r · Nuqtalar · Diagonal · Tuman — `z-index: -1`, `pointer-events: none` |

**Qoldi:** #6 ikonka uslubi (outline/solid/duotone) — dizayn ishi, alohida sessiya.

---

## Yo'lda topilgan va tuzatilgan 4 ta nuqson

### 1. HEX → kulrang (`#636465`)
`rgbToHsl` to'yinganlikni **0–1** da qaytaradi, accent esa **0–100** kutadi.
`Math.round(0.888)` = `1` → ya'ni ko'k rang kulrang bo'lib chiqdi.
**Tuzatish:** `Math.round(s * 100)`.

### 2. Fon naqshi ko'rinmasdi (`rgba(0, 0, 0, 0)`)
Naqsh `--rw-line` bilan chizilgan edi, lekin u `clay` va `neu` uslublarida
**ataylab shaffof** (bu ikki uslub chegara o'rniga soya ishlatadi).
**Tuzatish:** `--rw-divider` — matn rangidan hosil qilinadi, barcha uslublarda 3:1 dan o'tadi.

### 3. `check_hardcoded` — 4 ta qattiq `"default"`
`?? "default"` to'rt faylda takrorlangan edi (`apply.ts`, `share.ts`, `Customizer.tsx`, `api.ts`).
**Tuzatish:** `DEFAULT_CARD` / `DEFAULT_PATTERN` konstantalari + `CardStyle` / `BgPattern` tipi.

### 4. `share.ts` maydonlarni yo'qotardi
`scale`, `navMode`, `navShape` (oldingi ishdan) va yangi maydonlar havola orqali
**umuman o'tmasdi**. **Tuzatish:** `KEYS` kengaytirildi, `encode`/`decode`/`import` to'ldirildi.

---

## Tekshiruv natijalari

| Tekshiruv | Natija |
|---|---|
| `npx tsc --noEmit` | ✅ 0 xato |
| `npm run lint` | ✅ 0 xato |
| `check_hardcoded.py` | ✅ 250 manba + 100 klient — qattiq matn yo'q |
| `check_i18n.py` | ✅ 10 til × **1394** kalit + 24 shablon oila |
| Pre-push darvozalari | ✅ 3 marta o'tdi |
| Jonli brauzer (har feature) | ✅ `pageerror` 0 |
| **Jonli sayt** (rankwant.uz) | ✅ 7 ta yangi bo'lim/matn HTML'da |

---

## Miqyos

- **3 to'lqin**, 9 ta feature
- **3 commit**, 68 fayl o'zgargan
- **+1348 qator** qo'shildi
- **10 tilga** 33 ta yangi kalit
- Har to'lqin: kod → i18n → 4 tekshiruv → jonli sinov → commit → push
