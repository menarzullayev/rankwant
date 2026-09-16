# Sessiya xaritasi — 2026-09-13 (SOURCE KODGA MOSLASHTIRILGAN)

> **Bu fayl nima.** Boshqa sessiyadagi agent yozgan "xarita"ning
> **tekshirilgan va tuzatilgan** nusxasi. Har da'vo `main` shoxobchasidagi
> haqiqiy source kod bilan solishtirildi.
>
> **Tekshiruv sanasi:** 2026-09-14, `main` = `33ea38f`
> **Xarita qaysi holatni tasvirlagan:** `9451591` atrofi (2026-09-13)
> **Ya'ni xarita `main` dan ~103–106 commit orqada.**

---

## 0. Xulosa: xarita mazmunan aniq, lekin uch joyda tor

Xarita **yaxshi yozilgan** — marshrut holati, `AppHeader` tekshiruvi,
`AuthProof` nuqsoni, `--rw-divider` tokeni — hammasi **kodda tasdiqlandi**.
Lekin:

| # | Muammo | Jiddiylik |
|---|---|---|
| **1** | **P2 juda tor** — 1 ta emas, **7 ta** xom-locale formatlash joyi bor; xarita bergan tekshiruv buyrug'i 6 tasini **ko'rmaydi** | 🔴 Yuqori |
| **2** | **"3 ta aloqasiz fayl"** — aslida **1 ta** qoldi (`tools/naming/`) | 🟠 O'rta |
| **3** | **`AppHeader.tsx` yo'li ko'rsatilmagan** — u `components/` da emas, **`layout/`** da | 🟡 Past |
| **4** | Lighthouse/bundle raqamlari **source'dan tekshirib bo'lmaydi** (repo'da baseline yo'q) | 🟡 Past |

---

## 1. MUHOKAMA QILINGAN MAVZULAR

### M1. Mobil A11y nosozligi — ✅ TO'LIQ TO'G'RI (kodda tasdiqlandi)

Kodda dalil topildi (`apps/web/src/layout/AppHeader.tsx:41-52`):

```tsx
{/* 40x40 — header'dagi boshqa tugmalar bilan bir o'lchamda.
    Ilgari bosiladigan maydon faqat ikonka kattaligida edi: 20x20,
    ya'ni WCAG 2.5.8 (AA) talab qilgan 24x24 dan ham kichik. */}
<button className="-ml-2.5 flex size-10 items-center justify-center …">
```

`size-10` = **40×40** ✅. Havola tagchizig'i ham qo'llangan:
`AuthForm.tsx` da 5 joyda `rw-accent-ink underline` (444, 451, 568, 638, 642).

⚠️ **LEKIN:** `AuthForm.tsx:374` da **`hover:underline`** qolgan:

```tsx
<Link href={"/login?tab=reset-password" as Route}
      className="text-theme-sm rw-accent-ink hover:underline">
  {t(locale, "auth.forgot")}
</Link>
```

Bu **qayta tekshirilishi kerak** — agar WCAG 1.4.1 talabi matn ichidagi
havolaga tegishli bo'lsa, bu joy tuzatilmagan.

### M2. Chrome DevTools MCP — ⚠️ raqam farqi

Xarita **28 tool** deydi; loyiha xotirasida (`MEMORY.md`) **29 tool**
yozilgan. Ikkalasi ham "server sog'lom" degan xulosaga olib keladi —
farq ahamiyatsiz, lekin raqam bir xil emas.

### M3. Performance — birinchi o'lchov — ⚠️ SOURCE'DAN TEKSHIRILMADI

Xarita raqamlari:

| | Oldin | Keyin |
|---|---|---|
| JS (sovuq kesh) | 293.8 kB | **204.9 kB** |
| LCP (Slow 4G, CPU 4×) | 765–885 ms | 1094 ms |
| Lighthouse | mobil 96 | **100** |

**Repo'da Lighthouse konfiguratsiyasi YO'Q** (`.lighthouserc*` — topilmadi).
Ya'ni o'lchovlar **qo'lda, Chrome DevTools MCP orqali** olingan va
**takrorlanadigan artefakt qolmagan**. Bu raqamlarni keyingi agent
**qayta o'lchashi kerak**, ishonib qabul qilmasligi kerak.

### M4. i18n bundle — ✅ TO'G'RI

Faqat aktiv til ketadi. `intlLocale()` `apps/web/src/i18n/messages.ts:197`
da eksport qilingan ✅.

⚠️ **Muhim aniqlik:** `intlLocale()` **hech qayerda to'g'ridan-to'g'ri
chaqirilmaydi** — u faqat `dateTime()` (209-qator) va `date()` (217-qator)
ichida ishlatiladi:

```
apps/web/src/i18n/messages.ts:213   return new Date(value).toLocaleString(intlLocale(locale));
apps/web/src/i18n/messages.ts:218   return new Date(value).toLocaleDateString(intlLocale(locale));
```

Ya'ni **21 joy** `dateTime()`/`date()` yordamchilariga o'tkazilgan
(`dateTime(` = 19, `date(` = 27 ta chaqiruv). Xom `intlLocale(locale)`
faqat **raqam** uchun kerak (sana uchun emas).

### M5. `/register` auditi — ⚠️ QAYTA TEKSHIRILISHI KERAK

Xarita o'zi ogohlantiradi: audit **eski** sahifa bo'yicha o'tkazilgan;
`/register` keyin qayta qurilgan. Hozir `/register` — **307 yo'naltiruvchi**
(28 qator), haqiqiy forma `/login?tab=register` da.

### M6. 20 savolli qaror sessiyasi — ✅ kodda izlari bor

`--rw-divider` tokeni **31 joyda** (`globals.css` da 8 ta palitra qiymati +
ishlatishlar) ✅ xarita "31 ajratgich" degan. `rw-divider` klassi
**26 faylda** ishlatiladi.

### M7. To'liqlik tekshiruvi — ✅ to'g'ri

`9451591` — "the separators the divider token missed" — `main` da ✅.

---

## 2. QABUL QILINGAN QARORLAR

| # | Qaror | Holat (tekshirildi) |
|---|---|---|
| **A** | Mobil a11y: havola tagchizig'i, Menu 40×40, rozilik takrori | ✅ Bajarilgan (`61d7826`) — ⚠️ `AuthForm.tsx:374` da `hover:underline` qolgan |
| **B** | i18n variant A: serverdan faqat aktiv til; `t()` imzosi o'zgarmadi | ✅ Bajarilgan (`a3ad23d`) |
| **C** | 20 ta qaror: token → layout → forma → kod | ✅ Bajarilgan (`dff7bff` + `9451591`) |

**Commitlar — hammasi `main` da tasdiqlandi:**

| Commit | `main` dan orqada | Sarlavha |
|---|---|---|
| `61d7826` | 106 | `fix(a11y,ux): mobile-only failures on the auth page` |
| `a3ad23d` | 105 | `perf(i18n): ship only the active locale, not all ten` |
| `dff7bff` | 104 | `fix(ui,i18n): dividers that never drew, an empty panel, and the form order` |
| `9451591` | 103 | `fix(ui): the separators the divider token missed` |

⚠️ **Xarita bir joyda noaniq:** "Uch bo'lim bitta manzilda (`3ee6d3c`)"
deb yozilgan. Aslida **`3ee6d3c` o'zbekcha manzillarga tegishli**; hozirgi
**inglizcha** manzillar keyinroq keldi (`2b649c3` — `?tab=` qiymatlari,
`0c4c34f` — marshrut yo'llari). Atributsiya aniq emas.

---

## 3. BAJARILISHI LOZIM BO'LGAN VAZIFALAR

### P1 — 🔴 Qaror kutmoqda: LCP savdosi

**Tavsif.** i18n refactor **−75 kB** berdi, lekin **+250 ms LCP** qildi
(qo'shimcha 10 kB HTML kritik yo'lda).

**⚠️ Tuzatish.** Bu savolning **o'zi** o'sha o'lchovlarga tayanadi, ular esa
repo'da **takrorlanadigan artefaktga ega emas** (M3). Avval **qayta
o'lchash** kerak, keyin qaror.

**Ustuvorlik:** 🔴 P1 · **Kutilayotgan natija:** qayta o'lchangan LCP +
aniq qaror (qabul / lug'atni kritik yo'ldan chiqarish).

### P2 — 🟠 **TUZATILDI: 1 ta emas, 7 ta joy**

**Xarita faqat `AuthProof.tsx:34` ni ko'rsatgan va
`rg "toLocaleString(locale)"` bilan tekshirishni taklif qilgan.
Bu buyruq 6 ta joyni KO'RMAYDI** (`toLocaleTimeString`/`toLocaleDateString`
boshqa nom, `(locale, {` esa boshqa naqsh).

**Xom locale bilan formatlash — TO'LIQ ro'yxat (o'lchandi):**

| # | Fayl:qator | Chaqiruv | Turi |
|---|---|---|---|
| 1 | `app/attempts/page.tsx:67` | `toLocaleTimeString(locale)` | sana |
| 2 | `app/calendar/page.tsx:42` | `toLocaleDateString(locale, { month: "short" })` | sana |
| 3 | `app/calendar/page.tsx:53` | `toLocaleTimeString(locale, {...})` | sana |
| 4 | `app/calendar/page.tsx:58` | `toLocaleString(locale, {...})` | sana |
| 5 | `components/ArenaPlayer.tsx:165` | `toLocaleTimeString(locale)` | sana |
| 6 | `components/auth/AuthProof.tsx:34` | `toLocaleString(locale)` | **raqam** |
| 7 | `components/DuelDetail.tsx:60` | `toLocaleTimeString(locale)` | sana |

**To'g'ri yechim turlicha:**
- **Sana** (1–5, 7) → `dateTime()` / `date()` yordamchilari
- **Raqam** (6) → `intlLocale(locale)` (xarita taklif qilgani — **to'g'ri**)

**To'g'ri tekshiruv buyrug'i:**
```bash
grep -rn "toLocaleString(locale\|toLocaleTimeString(locale\|toLocaleDateString(locale" apps/web/src/
# kutilgan: 0
```

**Ustuvorlik:** 🟠 P2 · **Kutilayotgan natija:** 3 tilda (`kaa`/`ky`/`tg`)
raqam va sana izchil.

### P2-b — 🟡 Admin paneldagi qotirilgan locale (xarita aytmagan)

```
components/admin/DuelsAdmin.tsx:73,153,161   toLocaleString(DEFAULT_LOCALE)
components/admin/PostsAdmin.tsx:98           toLocaleString("uz-UZ", {...})
components/admin/TournamentsAdmin.tsx:45     toLocaleString("uz-UZ", {...})
```

Bu **ataylab** bo'lishi mumkin (admin paneli o'zbekcha). Lekin **qaror
sifatida yozilmagan** — tekshirilsin.

### P2-c — 🟠 `AuthForm` bo'lish (#14) — ✅ raqam tasdiqlandi

`apps/web/src/components/AuthForm.tsx` = **751 qator** ✅ xarita to'g'ri.

⚠️ **Xarita ogohlantirishi o'rinli:** auth oqimi `13c1d6d` da qayta
qurilgan **va undan keyin yana ikki marta** (`2b649c3`, `0c4c34f`).
**Avval hozirgi kodni o'qing** — xaritadagi 688/751 raqamlari orasidagi
farq ham shundan.

**Ustuvorlik:** 🟠 P2 · **Kutilayotgan natija:** ~350 qator + 2 fokuslangan
fayl; to'ldirib-yuborish testi o'tadi.

### P3-15 — 🟡 Legacy JS: `browserslist` — ✅ tasdiqlandi: YO'Q

`apps/web/package.json` da `browserslist` **topilmadi** ✅ vazifa ochiq.
Kutilayotgan foyda: FCP/LCP **0 ms**, faqat hajm (24.9 kB).

### P3-16 — 🟡 RSC prefetch dublikatlari — 🟠 OCHIQ

3 ortiqcha so'rov. **Avval sababni aniqlash** (Next.js ichki xatti-harakati
bo'lishi mumkin) — xarita to'g'ri yondashuv ko'rsatgan.

### P3-6 — ⚪ Holati noma'lum

Eski sessiyadan: `sub` ni empirik tekshirish. **Tegilmagan.**

---

## 4. XATOLAR JADVALI (xarita → haqiqat)

| Xaritada | Haqiqat (`33ea38f`) | Dalil |
|---|---|---|
| P2: faqat `AuthProof.tsx:34` | **7 ta joy** xom locale bilan formatlaydi | `grep -rn "toLocale…(locale"` |
| Tekshiruv: `rg "toLocaleString(locale)"` → 0 | Bu naqsh **6 joyni ko'rmaydi** | `toLocaleTimeString`, `(locale, {` |
| "3 ta aloqasiz fayl: `requirements-dev.lock`, `uv.lock`, `tools/naming/`" | **Faqat `tools/naming/`** qoldi; ikki lock fayl **yo'q** | `ls`; `git status` → `?? tools/naming/` |
| `AppHeader.tsx:34` (yo'lsiz) | **`apps/web/src/layout/AppHeader.tsx:34`** | `find` — `components/` da emas |
| MCP "28 tool" | Loyiha xotirasida **29 tool** | `MEMORY.md` |
| "Uch bo'lim bitta manzil (`3ee6d3c`)" | Inglizcha manzillar keyinroq: `2b649c3` + `0c4c34f` | `git log --follow` |

**To'g'ri chiqqan da'volar (o'zgarmadi):**
`AppHeader.tsx:34` `pathname === "/login"` ✅ · `AuthProof.tsx:34` nuqsoni
✅ · `intlLocale` `@/i18n/messages` dan eksport ✅ · `AuthForm.tsx` = 751
qator ✅ · `--rw-divider` = 31 ✅ · `browserslist` yo'q ✅ ·
`/register` → `/login?tab=register` ✅ · Menu 40×40 ✅ ·
4 commit `main` da ✅.

**Tekshirib bo'lmaydiganlari:** JS 293.8→204.9 kB, LCP 765→1094 ms,
Lighthouse 96→100 — repo'da **baseline yoki konfiguratsiya yo'q**.

---

## 5. KEYINGI SESSIYA UCHUN BOSHLANG'ICH NUQTA

1. **Avval `main` HEAD ni o'lchang** — bu fayl `33ea38f` da yozilgan.
   Marshrutlar ikki marta ko'chirilgan, yana o'zgargan bo'lishi mumkin.
2. **P2 ni to'liq qamrovda bajaring** — 7 joy, va tekshiruv buyrug'ini
   yuqoridagi uchtalik naqsh bilan yozing (bittasi bilan emas).
3. **P1 uchun raqamlarni qayta o'lchang** — eski raqamlar artefaktsiz.
4. **`AuthForm.tsx:374`** dagi `hover:underline` ni ko'zdan kechiring.
5. O'lchovsiz xulosa chiqarmang: har yangi tekshiruvga **salbiy test**.
