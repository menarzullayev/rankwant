# Sessiya natijasi — 31 naqsh implement qilindi

**Sana:** 2026-09-15 (kechki sessiya) · **Loyiha:** RankWant
**Buyruq:** *«Avval commit + deploy … undan keyin to'liq "Hammasini ketma-ket".
Men esa uxlashga ketaman. 8 soat ichida vazifalarni o'zing bajarishing kerak.»*

---

## 1. Bajarilgan ishlar

| # | Ish | Commit | Holat |
|---|---|---|---|
| 0 | Verdikt ko'rsatkichlari (10 tur) + deploy | `c9ae937` | ✅ |
| T1 | Verdikt kodlari 10 → **23** + rang guruhlari | `eb6c6ea` | ✅ |
| A | Holat tizimi (ok/warn/bad/info) — **10 variant** | `7983a19` | ✅ |
| B | Bo'sh holat va xato — **3 variant**, 8 sahifaga ulandi | `5b47869` | ✅ |
| C | Qidiruv/filtr/jadval — **8 naqsh** | `a509c5f` | ✅ |
| D | Yuklanish — **10 animatsiya**, Customizer'da tanlanadi | `b1aa851` | ✅ |
| T4 | `Verdict` ni **8 real nuqtaga** ulash + hidratsiya tuzatildi | `e664bdd` | ✅ |

**Jami:** 31 naqsh · 7 commit · hammasi push qilingan va deploy qilingan.

---

## 2. 🔴 Yo'lda topilgan va tuzatilgan to'rtta jiddiy xato

### 2.1 Verdikt kodlari mos emas edi (P0 bloker)

`apps/api/judging/verdicts.py` da **23 kod**, `lib/theme/verdict.ts` da **10**.
`verdictOf()` noma'lum kodni `PD` ga tushirardi, ya'ni **14 kod «Navbatda»
bo'lib ko'rinardi**: `RE_SIGNAL`, `RE_EXIT`, `WRONG_TEST`, `CHECKER_ERROR`,
`PARTIAL`, `SECURITY_VIOLATION`, `DENIAL_OF_JUDGEMENT`, …

`tsc` ham, `eslint` ham jim o'tardi — kalit oddiy `string`.
**Yechim:** 23 kod + 4 rang guruhi (`ok`/`warn`/`bad`/`neutral`) +
`tools/check_verdict_codes.py` (2 salbiy test bilan, hook'ga ulangan).
`neutral` guruhi muhim: `IE`, `WRONG_TEST`, `CHECKER_ERROR`,
`DENIAL_OF_JUDGEMENT` — infratuzilma nosozligi, **foydalanuvchi aybi emas**.

### 2.2 React hidratsiya xatosi (men kiritgan muammo)

Verdikt/holat/yuklanish — **HTML tuzilishini** o'zgartiruvchi birinchi
sozlamalar. Qolganlari faqat CSS atributini o'zgartiradi, ya'ni SSR va klient
bir xil HTML chizadi; bu uchtasi esa yo'q. Server standartni, klient
`localStorage` dagi tanlovni chizardi → **hidratsiya xatosi**.

O'lchandi: `verdictStyle=circle` bilan `/problems/<slug>/status` da chiqadi.
**Yechim:** `rw:markup` cookie — faqat shu uchtasi uchun, server o'qiydi.
Qolganlari cookie'ga tushmaydi (u har so'rovda yuboriladi).
Boot skript cookie'ni `localStorage` dan bir marta yozadi — eski
foydalanuvchilar bir yuklanishda o'tadi.

### 2.3 Ishchi daraxtda 683 fayl eski CRLF bilan qolgan edi

`.gitattributes` `eol=lf` talab qiladi, lekin fayllar `.gitattributes`
qo'shilishidan oldin olingan. Natijada **4 salbiy test yiqilardi**
(`parity/yetishmaydi`, `i18n/server yetishmaydi`, `i18n/runtime dedup`,
`email_locales`) — ular LF bilan langar izlaydi.
**Yechim:** 683 fayl `.gitattributes` bo'yicha qayta olindi.
Natija: **58/58 salbiy test** (avval 56/56, 4 tasi yiqilardi).

### 2.4 `check_docs.py` `.claude/` ni skanerlayotgan edi

`.claude/worktrees/` — `git worktree` nusxalari, ichida `tools/` ning o'zi bor.
O'sha nusxadagi `ADR-9999` misoli haqiqiy xato bo'lib ko'rinardi → darvoza
**doim qizil** (211 → 73 markdown). `.claude` istisnoga qo'shildi va
`.gitignore` ga ham yozildi.

---

## 3. Nima yaratildi

### Yangi fayllar (`rankwant/apps/web/src/`)

| Fayl | Vazifasi |
|---|---|
| `lib/theme/verdict.ts` | 23 verdikt kodi × rang guruhi, ikonka, i18n yorliq |
| `lib/theme/status.ts` | 4 holat (ok/warn/bad/info) + 10 variant |
| `lib/theme/loading.ts` | 10 yuklanish shakli |
| `components/ui/Verdict.tsx` | 10 variant + `auto` (responsive) |
| `components/ui/Status.tsx` | 10 variant + `auto` |
| `components/ui/EmptyState.tsx` | 3 shakl: `full` · `card` · `illustration` |
| `components/ui/Loading.tsx` | 10 animatsiya (sof CSS/SVG) |
| `components/ui/Segmented.tsx` | Guruh tugmalar — holat va navigatsiya rejimi |
| `icons/phosphor.tsx` | 43 ikonka, 5 xarita (generatsiya qilinadi) |
| `lib/prefs.ts` | `rw:markup` cookie — markup o'zgaruvchi sozlamalar |

### Yangi vositalar (`rankwant/tools/`)

| Fayl | Vazifasi |
|---|---|
| `gen-verdict-icons.mjs` | Ikonkalarni qayta yasash (tarmoqsiz) |
| `phosphor-verdict-icons.json` | Phosphor quyi to'plami (44 ikonka) |
| `check_verdict_codes.py` | API ↔ web ↔ ikonka ↔ 10 til mosligini tekshiradi |

### O'zgargan asosiy fayllar

- `Customizer.tsx` — **16 bo'lim** (verdict, status, loading qo'shildi)
- `globals.css` — `.rw-verdict*`, `.rw-status*`, `.rw-empty*`, `.rw-load*`
- `layout.tsx` — `data-status`, `data-loading`, cookie o'qish, boot skript
- `api.ts` · `apply.ts` · `share.ts` — uchta yangi sozlama
- `Table.tsx` — `SortHeader` (`aria-sort`, ilgari **umuman yo'q edi**)
- `SearchBox.tsx` — tozalash tugmasi, `Ctrl+K`, Escape
- `SolvedTab.tsx` — noto'g'ri `role="tablist"` → `Segmented`
- 8 sahifa — bo'sh holat komponenti
- 8 nuqta — `VerdictBadge` → `Verdict` (eski komponent o'chirildi)

---

## 4. Tekshiruv natijalari

| Darvoza | Natija |
|---|---|
| `tsc --noEmit` | 0 |
| `eslint src --max-warnings=0` | 0 |
| `check_i18n.py` | 10 til × **1487** kalit |
| `check_hardcoded.py` | 259 manba + 105 klient fayl |
| `check_contrast.py` | 772 matn rangi AA |
| `check_docs.py` | 73 markdown |
| `check_negative.py` | **58/58** |
| `check_verdict_codes.py` | API 23 · web 23 · ikonka 23 · 10 til |
| `check_ordering.py` · `check_locales_parity.py` · `check_contract.py` | 0 |

### Jonli tekshiruvlar (Playwright, `localhost:3000`)

| Nima | Natija |
|---|---|
| Verdikt 10 variant | 11/11 tugma, `data-verdict` to'g'ri, `pageerror` 0 |
| Guruh ranglari | AC yashil · WA/TLE qizil · PARTIAL sariq · WRONG_TEST kulrang |
| Noma'lum kod | `BOGUS_CODE` **xom ko'rinadi** (avval «Navdada» bo'lardi) |
| Holat 10 variant | 11/11, 4 holat har birida |
| Bo'sh holat | `/blog`, `/platform-roadmap` da `rw-empty-card`, 1px ramka |
| Yuklanish 10 variant | 10/10 harakatlanadi |
| **Harakat o'chganda** | animatsiya 0, **10/10 ko'rinadi** ✅ |
| Qidiruv | tozalash, `Ctrl+K`, Escape — hammasi ishlaydi |
| `Segmented` | `role="group"`, `aria-current="page"` |
| Verdikt real sahifada | 75 element → tanlovdan keyin 25 doira |
| **Hidratsiya** | `pageerror` **0** ✅ |

---

## 5. ⚠️ Keyingi sessiya uchun muhim ma'lumot

### Dev muhiti (yangi topilgan)

`localhost:3000` da API'ga ulanish **ishlamaydi** — standart
`API_BASE = http://localhost:8000/api/v1`, aslida API `:8301` da va
`ALLOWED_HOSTS` **`localhost` ni talab qiladi** (`127.0.0.1` EMAS → 400).

Ishlaydigan buyruq:
```bash
API_BASE_INTERNAL=http://localhost:8301/api/v1 \
NEXT_PUBLIC_API_BASE=http://localhost:8301/api/v1 \
npx next dev -p 3000
```

### Playwright

`~/AppData/Local/ms-playwright/` bo'shab qolgan — `channel: "chrome"` bilan
ishga tushiriladi. Modul:
`file:///C:/Users/nsn/.workbuddy-ai/binaries/node/workspace/node_modules/playwright/index.js`

### Ochiq qolgan

1. **10 ikonka to'plami tizimi** (D10–D12, D17) — hali kodga o'tmagan.
   Eng katta qolgan ish: `lib/theme/icon-packs.ts` + `icons/registry.tsx` +
   Customizer bo'limi + `tools/check_icons.py` (D12 qarori).
2. **~220 ikonka xaritasi** — hozir 48 tasi qoplangan (20 %).
3. **`Status`, `Loading`, `EmptyState` real sahifalarga ulanmagan** —
   komponentlar tayyor va Customizer'da ko'rinadi, lekin sahifalar hali
   eski ko'rinishlardan foydalanadi. Bu ataylab: avval foydalanuvchi
   tanlashi kerak edi, keyin ulash.
4. **D13–D16 va D20** — dashboardlardan tanlov (`patterns.html`, `scope.html`).
5. **`check_negative.py`** — yangi tekshiruvlar (`check_verdict_codes.py`,
   status/loading i18n) uchun salbiy testlar qo'shilmagan (verdict uchun 2 ta bor).
6. `.claude/worktrees/` — 3 ta eski agent worktree, tozalash mumkin.

---

## 6. Sessiya davomida saqlangan saboqlar

- **`--rw-line` `clay`/`neu` da `transparent`** → ko'rinadigan chegara doim
  `--rw-divider` (ikki marta urdi: avval fon naqshi, keyin verdikt ramkasi).
- **`.gitignore` dagi yalang'och `data/`** qoidasi `tools/data/` ni yutadi.
- **Markup o'zgartiruvchi sozlama** cookie talab qiladi — `localStorage`
  yetmaydi (SSR ko'rmaydi).
- **Yangi tekshiruv = salbiy test.** `check_verdict_codes.py` buzilishni
  tutishi o'lchandi.
- **Ikkinchi `next dev` ishga tushmaydi** — `.next` band. Eski jarayonni
  `Get-NetTCPConnection -LocalPort 3000 | Stop-Process -Force` bilan o'ldiring.
