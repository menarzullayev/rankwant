# 8.x — Web UI arxitekturasi (qatlam chegarasi)

**STATUS:** accepted (2026-09-24) · **Majburlanadi:**
`tools/check_features.py` (CI) · **Bog'liq:** [ADR-0009](../07-adr/0009-monorepo.md)

Bu hujjat `apps/web/src` ning qatlam qoidasini belgilaydi. Qoida — da'vo
emas: **`tools/check_features.py`** har PR da tekshiradi va buzilsa CI
yiqiladi.

## 1. Qatlamlar

```
apps/web/src/
├── app/          # Next.js App Router — marshrutlar, sahifalar (server)
├── features/     # Domen bo'yicha bo'lingan modullar (13 ta)
├── components/   # Global UI — domendan XABARDOR EMAS
├── layout/       # Ilova qobig'i — header, sidebar, banner
├── lib/          # Util, hook, tip — domendan XABARDOR EMAS
├── context/      # React Context (Session, Theme, …)
├── i18n/         # Lug'at va til
└── icons/        # Ikonka to'plamlari
```

**Oqim yo'nalishi bir tomonlama:** yuqori qatlam pastni biladi, past
qatlam yuqorini **bilmaydi**.

```
app  →  features  →  components/kit  →  components/ui
                 ↘  lib / context / i18n  ↗
```

## 2. To'rt qoida

### 2.1 Barrel — feature faqat `index.ts` orqali chiqadi

```ts
// ✅ to'g'ri
import { ProblemFilters } from "@/features/problems";

// ✗ xato — ichki tuzilma tashqariga oshkor
import { ProblemFilters } from "@/features/problems/components/ProblemFilters";
```

Sabab: `components/` ichidagi fayl nomi o'zgarsa, barrel tufayli
chaqiruvchilar tegilmaydi.

### 2.2 Feature → feature faqat ruxsat ro'yxati bilan

Kapling — bu qarz. Umumiy narsa pastga (`lib/`, `components/ui`) tushadi,
feature'lar orasida emas. Istisnolar `check_features.py` dagi
`ALLOWED_CROSS` da **sabab bilan** yozilgan:

| Juftlik | Sabab |
|---|---|
| `profile → account` | `PrivacyField` **tipi** (kod emas, tip oqimi) |
| `account → problems` | `Problem` **tipi** — marafon vazifalari |
| `contests/problems/hackathons → profile` | `UserTitle` tipi — `lib/identity` dan qayta eksport |
| `submissions → hackathons` | `HackPanel` — urinish sahifasiga singib ketgan |
| `account → auth` | `Turnstile` — xavfsizlik vidjeti |

### 2.3 Global qatlam feature'ni bilmaydi

`components/ui/Button.tsx` ichida `@/features/...` bo'lmasin. Bu
«pastdagi layer yuqoridagini bilmasin» — ya'ni bog'liqlik sikli
oldini oladi.

**Ikki istisno** (aniq fayl bo'yicha, sabab bilan):
- `lib/api/index.ts`, `lib/api/endpoints.ts` — `@/lib/api` **barqaror
  yuzasi** (ADR-0009 ruhi). Domen API'lari `features/<dom>/api/` da
  yashaydi, lekin chaqiruvchi uchun bitta import yo'li qoladi.
- `layout/HeaderActions.tsx` — qobiq vidjeti (`UpdatesBell`); feature o'z
  widgetini beradi, qobiq uni nom bilan chaqiradi.

### 2.4 Bir barrel mijoz va serverni aralashtirmasin ⚠️

Bu qoida **Next.js build yiqilishidan** tug'ildi:

```
You're importing a module that depends on "next/headers".
This API is only available in Server Components.
```

Sabab: `features/account/components/AuthForm.tsx` — `"use client"`, u
`@/features/auth` barrel'ini import qilardi. Barrel esa `AuthTabs` ni
qayta eksport qilardi — server komponenti (`@/i18n/server` →
`next/headers`). Natijada `next/headers` butun mijoz to'plamiga tortildi.

**Yechim:** runtime bo'yicha ikkita fayl.

| Fayl | Nima chiqadi | Kim import qiladi |
|---|---|---|
| `features/x/index.ts` | faqat `"use client"` | mijoz komponentlari |
| `features/x/server.ts` | server-only | server komponentlari (`page.tsx`) |

Hozir shunday ikkiga bo'lingan: **`auth`**, **`profile`**.

⚠️ Belgi **aniq**: `"use client"` yo'qligi o'zi server-only degani emas —
sof taqdimot komponenti ham belgisiz bo'ladi va ikkala tomonda xavfsiz.
Xavf faqat `next/headers`, `@/i18n/server`, `@/lib/api.server`,
`server-only` zanjiridan keladi. `check_features.py` aynan shuni qidiradi.

## 3. Umumiy narsaning uyi

Ko'p marta uchraydigan savol: *«bu narsa feature ichidami yoki globalda?»*

**Mezon:** boshqa **ikkita yoki undan ko'p** feature ishlatsa — global.

| Nima | Uy | Ilgari qayerda edi |
|---|---|---|
| `useAction`, `useLoad`, `describeError` | `lib/hooks/` | `features/account/.../section-kit.tsx` |
| `UserTitle`, `TitleBand` (tip) | `lib/identity.ts` | `features/profile/api/users.ts` |
| `Avatar`, `UserName`, `MarkerText`, `rankClass` | `components/ui/Identity/` | `features/profile/components/` |
| `TextArea`, `Select`, `Check` | `components/form/SettingsKit.tsx` | `section-kit.tsx` |
| `Status` (xato/saqlash qobig'i), `Hint` | `components/kit/Feedback.tsx` | `section-kit.tsx` |
| `VerifyBanner`, `WelcomeNotice`, `GeoNudge`, `ContestInvite` | `layout/banners/` | `features/account`, `features/contests` |

`section-kit.tsx` endi **yupqa qayta eksport** — o'z nusxasini yaratmaydi.

## 4. Tekshiruv

| Skript | Nima ushlaydi |
|---|---|
| `check_features.py` | 4 qoida — barrel, feature→feature, global→feature, client/server aralash |
| `check_imports.py` | har `@/` yo'l haqiqiy faylga ishorami (statik) |
| `check_design_tokens.py` | xom hex rang va `text-[Npx]` |
| `check_hardcoded.py` | qattiq yozilgan matn (i18n) |

Ikkalasi ham `.github/workflows/ci.yml` da ishlaydi.

⚠️ `check_features.py` faqat **statik import yo'lini** o'qiydi. Runtime
bog'liqlikni ko'rmaydi — u uchun test kerak (kelajakdagi ish).

## 5. Nega bu muhim

Bu qoidalar **o'lchov** bilan tug'ilgan, taxmin bilan emas:

- `check_features.py` ni yozganda **30 ta chegara buzilishi** topildi —
  hammasi haqiqiy edi (dublikat `Status`/`Loading`, feature'lar orasidagi
  bog'liqlik, global qatlamdan feature'ga murojaat).
- Buzilishlarni tuzatish **119 ta TypeScript xatosini 0 ga** tushirdi —
  ya'ni chegara intizomi kompilyatsiya bilan to'g'ridan-to'g'ri bog'liq.
- Client/server barrel qoidasi **haqiqiy build yiqilishidan** tug'ildi.
  `next build` o'tmaguncha qoidaga ishonib bo'lmaydi.
