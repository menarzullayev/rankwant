# Appearance moduli — qo'shish mumkin bo'lgan 10 ta feature

**Sana:** 2026-09-15 · **Asos:** RankWant'ning amaldagi 39 sozlamasi + kep.uz bilan
o'lchangan solishtirish (`REPORT.md`).

**Hozirgi holat:** 12 uslub · 8 shablon · 14 tus + 2 slider · 5 shrift · 4 o'lcham +
shkala zichligi · 3 zichlik · navigatsiya (2 rejim × 3 shakl) · qulaylik tab'i
(rang ajratish, harakat, katta maydon, kuchli fokus) · undo · tasdiqli reset ·
ulashish havolasi · shaxsiy shablon (5/2) · kontrast nazorati (AA).

---

## 1. Aniq rang kiritish (HEX / rang tanlagich)

**Maqsad:** hozir rang faqat **14 ta tayyor tus** va **hue/sat slider** orqali
tanlanadi. Brend rangini (masalan `#0F62FE`) aniq qo'yish imkoni yo'q.

**Foydalanuvchiga qiymati:** o'z brendini platformaga ko'chira oladi — bu
"o'ynash" emas, **haqiqiy moslashtirish**. Korporativ mijozlar uchun hal qiluvchi.

**Murakkablik:** 🟢 **past** — `hue/sat` allaqachon `hsl()` ga aylanadi; HEX ni
o'qib `hue/sat` ga o'girish va aksincha yetarli. Kontrast nazorati (D11) o'z
kuchida qoladi.

---

## 2. Shrift juftligi (sarlavha va matn alohida)

**Maqsad:** hozir bitta shrift butun sahifaga. Aslida sarlavha va matn uchun
**ikki xil shrift** ishlatish — tipografikaning asosiy usuli.

**Foydalanuvchiga qiymati:** "Editorial" uslubida serif sarlavha + sans matn
kabi sifatli kombinatsiyalar. Hozir uslub buni o'zi tanlaydi, foydalanuvchi
aralasholmaydi.

**Murakkablik:** 🟡 **o'rta** — `AppearancePrefs.font` ni `{ heading, body }` ga
ajratish kerak; `--rw-font` va `--rw-font-display` tokenlari **allaqachon bor**
(o'lchandi), ya'ni CSS tomoni tayyor. Prefs sxemasi va 10 til tarjimasi yangilanadi.

---

## 3. Qator balandligi va harf oralig'i

**Maqsad:** tipografiya shkalasida o'lcham bor, lekin **satr balandligi** va
**harf oralig'i** sozlanmaydi — ular uslubda qotib qolgan.

**Foydalanuvchiga qiymati:** uzoq matn o'qiydiganlar uchun hal qiluvchi
(disleksiya, charchoq). kep.uz da ham yo'q — bizda **birinchi** bo'lardi.

**Murakkablik:** 🟢 **past** — `typography.ts` da `lineHeight` va
`letterSpacing` allaqachon har daraja uchun mavjud; faqat ko'paytirgich qo'shish.

---

## 4. Karta uslubi (radius · soya · chegara)

**Maqsad:** kep.uz da `Card Style` (Outline/Corners/Glow) bor, lekin
**ishlamaydi** (o'lchandi — faqat `data-*` yoziladi). Bizda umuman yo'q.

**Foydalanuvchiga qiymati:** kontent bloklarining "og'irligi" ni boshqarish —
ma'lumot zich bo'lgan sahifalarda chegara, "havodor" sahifalarda soya.

**Murakkablik:** 🟡 **o'rta** — `rw-surface` tokenlari bor, lekin kartalar
klasslari butun kod bo'ylab tarqalgan. Avval token joriy qilish kerak.

---

## 5. Fon naqshi (to'g'ri ishlaydigan)

**Maqsad:** kep.uz da 5 ta variant bor (None/Grid/Dots/Diagonal/Mesh) va
**hech biri ishlamaydi**. Biz to'g'ri qilib qo'ysak — raqobatdosh ustunlik.

**Foydalanuvchiga qiymati:** sahifa "bo'sh" ko'rinmaydi; brend hissi kuchayadi.

**Murakkablik:** 🟡 **o'rta** — `body::before` ga `background-image` (SVG pattern
yoki gradient), `opacity` past, kontent ustida turmasligi kerak. Kontrast
tekshiruvi (`check_contrast.py`) yangi fonni ham qamrab olishi shart.

---

## 6. Ikonka uslubi (outline · solid · duotone)

**Maqsad:** hozir ikonkalar bitta uslubda qotib qolgan.

**Foydalanuvchiga qiymati:** "Neo-brutalizm" va "Glassmorphism" uslublari
qalin/solid ikonkalar bilan ancha yaxshi ko'rinadi.

**Murakkablik:** 🔴 **yuqori** — 20+ ikonkaning ikkinchi varianti kerak
(`icons/index.tsx` hozir bitta to'plam). Bu **dizayn ishi**, kod emas.

---

## 7. Animatsiya darajasi (to'liq · o'rtacha · minimal)

**Maqsad:** hozir `motion: system | reduce` — ya'ni "hammasi" yoki "hech narsa".

**Foydalanuvchiga qiymati:** o'rtacha daraja — o'tishlar qoladi, lekin
"chaqqon" effektlar o'chadi. Ko'pchilik uchun eng qulay nuqta.

**Murakkablik:** 🟢 **past** — `data-motion` atributi bor; `full | mild | off`
qiymatlarini qo'shish va CSS'da `[data-motion="mild"]` bloki.

---

## 8. Ko'rinishni eksport/import qilish (JSON fayl)

**Maqsad:** hozir ulashish faqat **havola** orqali (`?style=flat`). Fayl bilan
ko'chirish yo'q.

**Foydalanuvchiga qiymati:** jamoada ko'rinishni almashish; qurilmadan qurilmaga
o'tkazish; zaxira nusxa. Jamoaviy ish uchun muhim.

**Murakkablik:** 🟢 **past** — `share.ts` da `decodeAppearance`/`shareUrl`
**allaqachon bor**; JSON ga o'rash va fayl yuklab olish yetarli.

---

## 9. Kontent kengligi (sahifa max-width)

**Maqsad:** hozir `max-w-[1400px]` qotib qolgan.

**Foydalanuvchiga qiymati:** katta monitorda tor (o'qish uchun qulay) yoki keng
(jadval uchun qulay) — ish turiga qarab.

**Murakkablik:** 🟢 **past** — bitta CSS o'zgaruvchisi + `AppShell` dagi klass.

---

## 10. Disleksiya uchun qulay shrift

**Maqsad:** `A11yPrefs` da rang ajratish va harakat bor, lekin **o'qish
qiyinchiligi** yo'q.

**Foydalanuvchiga qiymati:** disleksiyasi bor foydalanuvchi platformadan
foydalana oladi. Bu **inklyuziya** — kep.uz da ham yo'q.

**Murakkablik:** 🟡 **o'rta** — OpenDyslexic yoki Lexend shriftini qo'shish
(web font, ~50 KB), `data-font` ga qiymat, harf oralig'ini kengaytirish.

---

## Umumiy jadval

| # | Feature | Qiymat | Murakkablik |
|---|---|---|---|
| 1 | Aniq rang (HEX) | korporativ moslashtirish | 🟢 past |
| 2 | Shrift juftligi | tipografik sifat | 🟡 o'rta |
| 3 | Qator balandligi / tracking | o'qish qulayligi | 🟢 past |
| 4 | Karta uslubi | kontent "og'irligi" | 🟡 o'rta |
| 5 | Fon naqshi | brend hissi | 🟡 o'rta |
| 6 | Ikonka uslubi | uslub bilan uyg'unlik | 🔴 yuqori |
| 7 | Animatsiya darajasi | nozik nazorat | 🟢 past |
| 8 | Eksport / import | jamoaviy ish | 🟢 past |
| 9 | Kontent kengligi | ish turiga moslash | 🟢 past |
| 10 | Disleksiya shrifti | inklyuziya | 🟡 o'rta |

**Tez g'alaba (tez + arzon):** 1 · 3 · 7 · 8 · 9 — beshtasi ham past murakkablikda.
