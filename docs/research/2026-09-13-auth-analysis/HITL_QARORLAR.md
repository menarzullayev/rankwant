# RankWant — Login/Register qaror sessiyasi (HITL)

**Sana:** 2026-09-13
**Metod:** Chrome DevTools MCP orqali 135 raqobatchi resursining auth sahifalari tahlili + 20 bosqichli inson-doirasidagi qaror sessiyasi
**Holat:** 20/20 qaror qabul qilindi

---

## A. Tahlil qamrovi (halol hisob)

| Daraja | Soni | Izoh |
|---|---|---|
| Brauzerda to'liq tekshirildi | 7 | AtCoder, CodeChef, LeetCode, HackerRank, HackerEarth, Kaggle, GeeksforGeeks |
| HTTP probe (forma topildi) | 56 | cses.fi, solved.ac, uoj.ac, kilonova.ro, judge.beecrowd.com, informatics.mccme.ru, acm.bsu.by, uva.onlinejudge.org, usaco.org, bubblecup.org, ipsc.ksp.sk ... |
| Topilmadi / bloklandi | 67 | Cloudflare to'liq blok (Codeforces), 15 sayt javobsiz, qolganlari SPA yoki nostandart auth yo'li |
| **Jami** | **130 origin** (135 resursdan, 5 tasi takroriy) | |

### Bloklovchi omillar
- **Codeforces** — Cloudflare "Just a moment..." to'liq sahifa challenge; avtomatlashtirish mumkin emas. O'zi topilma: auth yo'lida juda qattiq bot himoyasi.
- **Topcoder** — `/register` → 404. Registratsiya `accounts.topcoder.com` ga ko'chgan, `/register` yo'li buzuq.
- **codingcompetitions.withgoogle.com** — 404, loyiha yopilgan.
- **Eski sud tizimlari** — `acm.hdu.edu.cn`, `acmp.ru`, `dl.gsu.by`, `acm.timus.ru` — faqat HTTP yoki nostandart yo'l.
- 15 sayt umuman javob bermadi (contest.bayan.ir, contest.bsuir.by, marathon24.com, codedrills.io, solve.by ...).

### Kuzatilgan naqshlar (brauzerda tekshirilgan 7 sayt)

**OAuth provayderlari:** Google 5/7 · GitHub 3/7 · Facebook 2/7 · LinkedIn 2/7 · Apple 1/7 · X 1/7 · Yahoo 1/7

**Captcha:** Cloudflare Turnstile 5/7 · reCAPTCHA 1/7 · ko'rinmas 2/7
→ **Turnstile sanoat standarti bo'lib qolgan.**

**Confirm-password:** bor 3/7 (AtCoder, LeetCode, Codeforces) · yo'q 4/7

**Sahifa tuzilishi:**
- Alohida sahifalar: AtCoder, LeetCode, HackerRank, HackerEarth
- Bitta sahifa, ikki ustun: CodeChef
- Tab / identifikator: GeeksforGeeks (3 tab), Kaggle (2 tab + parolsiz birinchi ekran)

**E'tiborli topilmalar:**
- **Kaggle** birinchi ekranda **parol maydonini umuman ko'rsatmaydi** — faqat 4 identifikator tugmasi.
- **AtCoder** qoidalarni ochiq matnda yozadi (min 6, harflar+raqamlar) va har maydon ostida yordamchi matn beradi.
- **HackerRank** forma tepasida ijtimoiy dalil qo'yadi: "Home to 30 Million developers worldwide".
- **CodeChef** registr va kirishni bir sahifada yonma-yon qo'yadi, ikkita h1 sarlavha bilan.
- Raqobatchilarning **birortasida** rate-limit/lockout xabari topilmadi.
- Raqobatchilarning **birortasida** OAuth'dan tashqari zamonaviy parol kuchi to'sig'i yo'q.

---

## B. RankWant hozirgi holati (kod asosida)

| Jihat | Holat | Fayl |
|---|---|---|
| Sahifalar | `/login`, `/register` alohida | `apps/web/src/app/login/page.tsx`, `register/page.tsx` |
| Umumiy komponent | `AuthForm.tsx` (729 qator), `mode` propi | `apps/web/src/components/AuthForm.tsx` |
| Login maydonlari | `username`, `password`, remember-me, forgot link | AuthForm L315–432 |
| Register maydonlari | **9 ta:** email, parol, parol2, username, display_name, davlat, [region], terms, marketing | AuthForm L301–455 |
| Parol kuchi | Bor, lekin kodda ochiq: *"HECH NARSANI TO'SMAYDI"* | `lib/password.ts` |
| Server parol qoidasi | min 8, faqat-raqam emas, username-o'xshash emas, `CommonPasswordValidator` | server |
| OAuth | Google, GitHub, Telegram — **haqiqiy OIDC** | `apps/api/core/oauth.py:45` |
| Validatsiya vaqti | Live/debounced (400ms), username bandligi AbortController bilan | AuthForm L128–170 |
| Captcha | **Yo'q** | — |
| Rate-limit xabari | **Yo'q** | — |
| 2FA | **Yo'q** | — |
| Parolni tiklash | `/parolni-tiklash` (o'zbekcha slug) | `app/parolni-tiklash/page.tsx` |
| i18n | 639 kalit, 10 til; ~55 auth/reset kaliti | `i18n/locales/uz.ts` |
| Dizayn | 12 uslub + 6 `.dark`; `rw-shadow` auth'da **ishlatilmaydi** | `globals.css` |
| TODO/FIXME | Auth kodida **nol** | — |

---

## C. Qabul qilingan 20 qaror

### Blok 1 — Sahifa tuzilishi va kirish
| № | Qaror | Tanlov |
|---|---|---|
| 1 | Sahifa tuzilishi | **Tab almashtirish** — bitta `/kirish` sahifasi, 3 tab: Kirish / Ro'yxatdan o'tish / Parolni tiklash. `/login` va `/register` eski havolalari redirect |
| 1a | *(2026-09-13, qayta ko'rib chiqildi)* | **Qatorda 2 tab** — Kirish / Ro'yxatdan o'tish. Parolni tiklash **bo'lim bo'lib qoladi** (manzil, xatdagi token, `/reset-password` yo'naltirishi ishlaydi), lekin tablar qatoridan chiqarildi. Sabab — pastda |
| 2 | Birinchi element | **Parol yuqorida (hozirgi)** — maydonlar birinchi, OAuth pastda |
| 3 | Register maydonlari | **10+ ga qisqartirish** — username ham 2-qadamga ko'chiriladi. 1-qadam: email, parol, parol2, terms (+marketing) |
| 4 | Login identifikatori | **Username YOKI email** — bitta maydon, server tomonda tolerant qidiruv |

### Blok 2 — Parol siyosati
| № | Qaror | Tanlov |
|---|---|---|
| 5 | Parol kuchi | **Maslahat (hozirgi)** — ko'rsatkich qoladi, to'smaydi |
| 6 | Qoida yetkazish | **Har doim ko'rinadigan qoida matni** (AtCoder modeli) — maydon ostida bir joyda |
| 7 | Confirm-password | **Saqlansin** — parol2 qoladi, majburiy |
| 8 | Xato ko'rsatish | **Maydon tagidagi xato** — maydon ostida qizil matn + chegara |

### Blok 3 — Tashqi kirish va xavfsizlik
| № | Qaror | Tanlov |
|---|---|---|
| 9 | Bot himoyasi | **Cloudflare Turnstile** — ko'rinmas rejim |
| 10 | Telegram OAuth | **Asosiy tugma** — O'zbekiston uchun differensiator, raqobatchilarda yo'q |
| 11 | 2FA | **Keyinroq** — AccountSettings'da joy ajratiladi |
| 12 | Ishonch signallari | **Ijtimoiy dalil + huquqiy** — "X ta ishtirokchi" (shartli) + Terms/Privacy |

### Blok 4 — Xatolar va holatlar
| № | Qaror | Tanlov |
|---|---|---|
| 13 | Reset URL | **Faqat `/reset-password`** — o'zbekcha slug olib tashlanadi + 301 redirect |
| 14 | Band email | **Yo'naltiruvchi xabar** — "Bu email band. Kirish yoki parolni tiklash" + ikkala havola |
| 15 | Rate-limit | **Aniq xabar + taymer** — "5 daqiqadan keyin qayta urinib ko'ring". Raqobatchilarda yo'q → differensiator |
| 16 | Muvaffaqiyat | **Birinchi kirishda taklif** — "AtCoder/Codeforces akkauntingizni ulang"; keyingilarda to'g'ridan-to'g'ri o'tish |

### Blok 5 — Dizayn va tekshiruv
| № | Qaror | Tanlov |
|---|---|---|
| 17 | 12 uslub | **To'liq qo'llab-quvvatlash** — barcha 12 uslub + 6 dark |
| 18 | Panel | **Yagona markazlashgan karta** (`rw-panel`, LeetCode/AtCoder modeli) |
| 19 | i18n | **Barcha 10 tilga** tarjima |
| 20 | Tekshiruv | **To'liq + a11y audit** — 18 variant + Lighthouse + klaviatura + ekran o'quvchi |

---

## D. Implementatsiya rejasi

### D1. Yangi sahifa tuzilishi
```
apps/web/src/app/kirish/page.tsx          ← yangi (3 tab: kirish/royxat/reset)
apps/web/src/app/login/page.tsx           ← redirect(307) → /kirish?tab=kirish
apps/web/src/app/register/page.tsx        ← redirect(307) → /kirish?tab=royxat
apps/web/src/app/parolni-tiklash/page.tsx ← 301 → /reset-password
apps/web/src/app/reset-password/page.tsx  ← yangi
apps/web/src/app/qoshimcha-malumot/page.tsx ← kengaytiriladi (username + ism + davlat)
```
**Komponentlar:**
```
components/auth/AuthTabs.tsx      ← tab konteyner + URL sinxronizatsiya
components/auth/LoginForm.tsx     ← AuthForm'dan ajratiladi
components/auth/RegisterForm.tsx  ← AuthForm'dan ajratiladi
components/auth/ResetForm.tsx     ← mavjud, ko'chiriladi
components/auth/AuthAside.tsx     ← ijtimoiy dalil + huquqiy
components/auth/Turnstile.tsx     ← Cloudflare widget o'ram
components/AuthForm.tsx           ← o'chiriladi (yoki thin wrapper)
```

### D2. Register 1-qadam (4 maydon)
1. `email` (email, autoComplete=email, autoFocus)
2. `password` (min 8, autoComplete=new-password, ko'z tugmasi, kuch ko'rsatkichi)
3. `password2` (autoComplete=new-password)
4. `terms_accepted` (majburiy) + `marketing_opt_in` (ixtiyoriy)

**2-qadam** (`/qoshimcha-malumot`): `username` (3–30, bandlik tekshiruvi), `display_name`, `country`, `[region]` (geoVariant=b && UZ).

### D3. Login maydoni
`identifier` maydoni — label yangilanadi: `auth.usernameOrEmail`. Server: `Q(username=value) | Q(email__iexact=value)`.
`autoComplete="username"`, `autoFocus`.

### D4. Telegram tugmasi
`PROVIDER_ORDER = ["telegram", "google", "github"]` — Telegram birinchi, to'liq kenglik,
o'z brend rangida (`@telegram` hardcoded, token emas — mavjud naqd rang naqshiga mos).
Google/GitHub 2 ustunda pastda.

### D5. Yangi i18n kalitlari (10 tilga)
`auth.tabsLogin`, `auth.tabsRegister`, `auth.tabsReset`, `auth.usernameOrEmail`,
`auth.passwordRules`, `auth.passwordRuleLen`, `auth.passwordRuleNotNumeric`,
`auth.emailTaken`, `auth.emailTakenCta`, `auth.rateLimited`, `auth.rateLimitWait`,
`auth.socialProof`, `auth.socialProofJoin`, `auth.linkAccountFirst`, `auth.linkAccountSkip`,
`auth.turnstileHint`, `auth.termsAndPrivacy` (~17 yangi kalit → jami ~656).
⚠️ Karakalpak/ky/tg da `ǵ`, `á`, `ń`, `ı`, `ó`, `ú` ishlatilsin — nusxa ko'chirishni oldini olish uchun.

### D6. Tekshiruv tartibi
1. `python tools/check_i18n.py` — 10 til to'liqligi, uz bilan bir xil tarjima yo'qligi
2. Brauzerda 12 uslub × 6 dark = **18 variant**, `getComputedStyle` bilan o'lchash
   - `--rw-divider` ajratgichlari ko'rinishi (clay/neu da `--rw-line` transparent!)
   - `--rw-shadow` auth panelida qo'llanishi
   - Turnstile widget har uslubda o'qilishi
3. Lighthouse desktop + mobil
4. Klaviatura navigatsiyasi: tab tartibi, fokus halqasi (`rw-focus-ring`), Enter bilan yuborish
5. Ekran o'quvchi: `role="alert"` xabarlar, `aria-busy`, `aria-invalid`, label-input bog'lanishi
6. Salbiy test: formani ataylab buzib, har bir tekshiruv `exit 1` berishini ko'rish

### D7. Risklar
| Risк | Yumshatish |
|---|---|
| Slug o'zgarishi tashqi havolalarni buzadi | `/parolni-tiklash` uchun 301, `/login` `/register` uchun 307 |
| Register 2 qadamga bo'linishi tashlab ketishni oshirishi mumkin | 2-qadamda "O'tkazib yuborish" (`auth.skip` allaqachon bor) + progress ko'rsatkichi |
| Turnstile Cloudflare'ga bog'liqlik | Zaxira: xato bo'lsa captcha talab qilinmaydi, faqat rate-limit ishlaydi |
| 17 yangi kalit × 10 til = 170 tarjima | Tarjima ketma-ket, `check_i18n.py` CI'da ushlaydi |
| `AuthForm.tsx` bo'lishi regressiya keltirishi mumkin | Avval bo'lish + testlar, keyin UI o'zgarishlari |

---

## E. Keyingi qadam

Implementatsiyani boshlash uchun tayyor. Tavsiya etilgan tartib:

1. **D1 + D2** — sahifa tuzilishi va register qisqartirish (eng katta ta'sir)
2. **D3 + D4** — login identifikatori va Telegram tugmasi (tez g'alaba)
3. **D5** — i18n kalitlari
4. **D6** — 18 variant tekshiruvi
5. **D7** — risklarni yopish

Har bir qadamdan keyin tekshiruv o'tkaziladi, regressiya bo'lsa oldinga o'tilmaydi.

---

## F. Tekshiruv natijalari (D6 / D17 / D20)

**Sana:** 2026-09-13 · **Metod:** brauzerdagi haqiqiy render + CI tekshiruvchilari

### Variant soni — 24 EMAS, 18

`styles.ts` da `dual` bayrog'i bor; `dual: false` uslublar bitta muhitga
chizilgan (tema tugmasi ham ko'rsatilmaydi):

| | uslublar |
|---|---|
| `dual: true` (6) | dashboard, swiss, flat, material, editorial, brutal |
| `dual: false` (6) | terminal, glass, neu, clay, aurora, skeu |

To'g'ri hisob: **6 × 2 + 6 = 18 palitra**. `aurora-light`, `glass-light`
kabi muhitlar MAVJUD EMAS — ularni o'lchash yolg'on "FAIL" beradi.

### Natija

| Tekshiruv | Natija |
|---|---|
| Brauzerda 18 variant (`auth_style_sweep.js`) | **18/18 PASS** |
| Gradientli 2 uslub qo'lda (`check_gradient_styles.py`) | **11/11 juftlik o'tdi** |
| `check_contrast.py` (CI) | **432 matn rangi AA** |
| `check_i18n.py` (CI) | **10 til × 656 kalit to'liq** |

`glass` va `skeu` avtomatik o'lchanmaydi (`getComputedStyle` gradientning
bitta rangini qaytarmaydi) — shuning uchun ular qo'lda, har bir pog'ona
alohida tekshirildi. `skeu` tugmasi oq matnda **4.83:1 / 6.30:1**, ya'ni
`globals.css` izohidagi raqamlar bilan aynan mos.

### O'lchov metodidagi uchta tuzoq (takrorlanmasin)

1. **Tema — `dark` emas, `null`.** `THEME_INIT` da `if (t !== "light")
   add("dark")`, ya'ni qorong'i — STANDART. `localStorage.theme = "dark"`
   yozish shart emas; kalit O'CHIRILADI. Ilgari `PrefsSync` hisobdan
   `theme` ni qayta yozib, o'lchov `dk:false` bo'lib qolgan edi.
2. **Uslubni `dataset.style` bilan keyin almashtirib bo'lmaydi.**
   `getComputedStyle` eski qiymatni qaytaradi — sahifa qayta yuklanishi
   (yoki yangi iframe) SHART.
3. **`color(srgb .61 .61 .61)` — kanallar 0–1, `rgb()` da 0–255.**
   Uni `rgb()` deb o'qish `material-dark` chegarasini 6.91:1 o'rniga
   1.12:1 qilib ko'rsatgan edi. Faqat `parseColor()` ishlatilsin.

Uchinchisi ayniqsa xavfli: qiymat **o'qilgan** ko'rinadi, ya'ni hech
qanday xato bermaydi — shuning uchun salbiy test SHART (ataylab buzib,
skript `exit 1` berishini ko'rish).

### Xulosa

**Mahsulot kodida kontrast xatosi topilmadi.** Dastlabki 9 ta "yiqilgan"
variantning hammasi o'lchov xatosi edi: noto'g'ri tema kaliti, noto'g'ri
nishon foni (chegara maydonning O'Z foniga qarshi o'lchanishi kerak) va
`color(srgb)` sintaksisi. Kod tomoni — `globals.css` dagi
`--rw-field-line` / `color-mix(text 65%, field)` — ataylab va to'g'ri
qurilgan.

### A11y auditi (20-qaror) — TOPILGAN HAQIQIY NUQSONLAR

| Tekshiruv | Natija |
|---|---|
| Klaviatura tartibi | 17 ta fokuslanadigan element, tartib mantiqiy |
| Fokus halqasi — **BOSHIDA** | **17 dan 9 tasida halqa YO'Q edi** |
| Fokus halqasi — tuzatilgandan keyin | 17 dan 4 tasida yo'q (tuzatish doirasidan tashqari) |
| `aria-current` tab sinxronizatsiyasi | ✓ aktiv tabda `aria-current="page"` |
| Maydon yorliqlari | ✓ uchala maydonda `<label>` bor |
| `autocomplete` | ✓ `email`, `new-password`, `username`, `current-password` |
| `role="alert"` xatolar | ✓ mavjud |

**Tuzatilgan uchta nuqson:**

1. **`Button.tsx` — `rw-focus-ring` yo'q edi.** Bu bitta komponent butun
   ilovada ishlatiladi, ya'ni **har bir asosiy tugma** klaviatura fokusini
   ko'rsatmasdi. Tuzatish: `BASE` satriga `rw-focus-ring`.
2. **`SelectField.tsx` → `Checkbox` — halqa yo'q edi.** Shartlar roziligi
   va marketing kataklarida. Tuzatish: `<input>` ga `rw-focus-ring`.
3. **`AppFooter.tsx` — Terms/Privacy havolalarida halqa yo'q edi.**
   Tuzatish: ikkala havolaga `rw-focus-ring`.

Tasdiqlandi: `getComputedStyle` bilan o'lchandi — fokusda
`outline: rgb(124, 58, 237) solid 2px`, `:focus-visible: true`. Ilgari
faqat brauzerning `1px` standart halqasi chiqardi.

**Qolgan 4 tasi (doiradan tashqari, alohida ish):** skip-link, til
tanlagichi (`SELECT`) va sarlavhadagi ikkita «Sign in» havolasi.

### Takroriy huquqiy havolalar — tuzatilgan

`AuthProof` (12-qaror) `Terms`/`Privacy` ni chizardi, lekin ular allaqachon
**ikki** joyda bor edi: `AppFooter` (har sahifada, ADR-0016) va
`AuthForm` dagi `Legal()` (rozilik matni ichida). Natijada `/kirish` da
havolalar **4 marta** chiqardi (o'lchandi: `termsCount: 4`) va tab
tartibida ikki marta takrorlanardi.

Tuzatildi: `AuthProof` faqat ijtimoiy dalilni ko'rsatadi. Endi har tabda
aniq **2 ta** havola, ikkalasi ham footer'da.

### Lighthouse (D6.3 / D20)

| Sahifa | Qurilma | Accessibility | Best Practices | SEO |
|---|---|---|---|---|
| `/kirish?tab=kirish` | desktop | **100** | 100 | 100 |
| `/kirish?tab=royxat` | desktop | **100** | 100 | 100 |
| `/kirish?tab=royxat` | mobil | **100** | 100 | 100 |
| `/kirish?tab=parolni-tiklash` | desktop | **100** | 100 | 66 † |

**† SEO 66 — nuqson EMAS, ataylab.** Yagona yiqilgan audit
`is-crawlable`: parolni tiklash tabida
`<meta name="robots" content="noindex, nofollow">` turadi
(`kirish/page.tsx:65`). Parolni tiklash sahifasi qidiruvga
tushmasligi SHART — bu xavfsizlik talabi, SEO kamchiligi emas.
Xuddi shu naqsh `emailni-tasdiqlash` va `qoshimcha-malumot` da ham bor.
Kirish va ro'yxat tablarida `robots` umuman yo'q, ya'ni ular
indekslanadi.

Barcha 4 o'lchovda **Failed: 0** (faqat yuqoridagi bitta ataylab
qo'yilgan `noindex`).

### Yakuniy holat


| Tekshiruv | Natija |
|---|---|
| `ci-local.sh fast` | ✓ 65 md · shartnoma · 10 til × 656 kalit · 432 rang AA · gradient 11/11 |
| `ci-local.sh api` | ✓ ruff · mypy strict · migratsiya · pytest |
| `ci-local.sh web` | ✓ lint (0 xato) · typecheck · build |
| `ci-local.sh all` | ✓ **HAMMASI O'TDI (3 qadam)** |
| Brauzerda 18 palitra | ✓ 18/18 PASS |



---

## G. 1-qaror qayta ko'rib chiqildi — tablar qatori (2026-09-13)

### Muammo (foydalanuvchi xabari bilan topildi)

«Sign in / Sign Up / Reset password tablari bitta sahifada ekan. Reset password
tabi mobil rejimda to'liq ko'rinmayabdi.» — tasdiqlandi, va sabab **mobil emas** edi.

### O'lchov (brauzerda, haqiqiy render; iframe orqali aniq 320–414px)

`AuthTabs` `grid-cols-3` ishlatardi — uchta **teng** ustun. 360px ekranda har
ustunga ~68px tegadi, yozuvlar esa undan uzun. `truncate` matnni o'rtasidan
kesardi (`hidden` = kesilgan piksel):

| Til | `auth.tabReset` | 360px da kesildi |
|---|---|---|
| kk | Құпия сөзді қалпына келтіру | **−115px** |
| es | Restablecer contraseña | −71px |
| ky | Сырсөздү кайра коюу | −70px |
| tg | Барқарорсозии рамз | −64px |
| en | Reset password | −23px |
| uz | Parolni tiklash | −14px |
| ru | Сброс пароля | −17px |
| tr | Parolayı sıfırla | −13px |
| kaa | Paroldi tiklew | −11px |
| zh | 重置密码 | ✓ sig'adi |

**10 tildan 9 tasida kesilgan.** «Ro'yxatdan o'tish» esa 414px gacha ham
kesilardi — ya'ni nuqson faqat tiklash tabida emas edi.

### Qaror

Uchta teng ustun bilan buni **hal qilib bo'lmaydi**: yozuvlarni qisqartirish
yoki ikonka kerak bo'lardi, ikkalasi ham ma'no yo'qotadi (`uz` da «Parolni
tiklash» → «Tiklash» — noaniq). Shuning uchun:

1. `TAB_BAR = ["kirish", "royxat"]` — qatorda 2 ta qisqa, **barqaror** yozuv
   (`grid-cols-2`). Bular hech qaysi tilda kesilmaydi.
2. `TABS` **o'zgarmadi** — `parolni-tiklash` haqiqiy bo'lim bo'lib qoladi.
   `/reset-password?token=…` → `307` → `/kirish?tab=parolni-tiklash&token=…`
   (tekshirildi: **token saqlanadi**), ya'ni xatdagi havolalar ishlaydi.
3. Parolni tiklashni kirish formasidagi **«Parolni unutdingizmi?»** havolasi
   ochadi (`AuthForm.tsx:372`) — bu odam uni qidiradigan tabiiy joy.
4. `truncate` → o'ralish (`leading-snug`). 320px da o'zbekcha
   «Ro'yxatdan o'tish» 105px talab qiladi, ustunda 91px bor — endi ikki
   qatorga o'raladi, kesilmaydi.

### Tekshiruv natijasi

| Tekshiruv | Natija |
|---|---|
| 10 til × 5 en (320/360/375/390/414) | **50/50 kombinatsiya ✓ kesilish yo'q** |
| Eng kichik tegish maydoni | **44px** (WCAG 2.5.8) ✓ |
| `/reset-password?token=abc123` | `307` → token **saqlanadi** ✓ |
| `/login`, `/register` | `307` ✓ |
| `/kirish?tab=parolni-tiklash` | `200`, karta sarlavhasi «Parolni tiklash» ✓ |
| Faol tab belgisi | tiklash bo'limida `aria-current` **yo'q** — to'g'ri (u qatorda emas) |
| `check_contract.py` | yangi `check_tab_bar()` + **3 salbiy test** ✓ |
| `ci-local.sh all` | ✓ HAMMASI O'TDI |

### Kelajakda takrorlanmasligi uchun

`tools/check_contract.py` ga `check_tab_bar()` qo'shildi: `TAB_BAR` uzunligi
bilan `grid-cols-N` mos bo'lishi, har bir bo'lim uchun yozuv borligi va
`TABS` dan `parolni-tiklash` chiqarilmaganligi tekshiriladi. Uchala shart
salbiy test bilan tasdiqlandi (buzildi → `exit 1`, tiklandi → `exit 0`).

**Saboq:** yozuv uzunligiga bog'liq joylashuv (`grid-cols-N`) HAR TILDA
o'lchanishi kerak. O'zbekcha sig'sa ham, qoraqalpoqcha ikki barobar uzun
bo'lishi mumkin.

## H. 3-qaror buzilgan edi — ro'yxatdan o'tish ishlamayotgan edi (2026-09-13)

**Qanday topildi:** 3-qaror bo'yicha `username` 1-qadamdan 2-qadamga
ko'chirilgan edi, lekin uni API'da IXTIYORIY qilish unutilgan. Xato
foydalanuvchi veb-formani to'ldirganda yuzaga chiqdi:

```
POST /api/v1/auth/register/
{"email":"…","password":"…","terms_accepted":true,"marketing_opt_in":false,"turnstile_token":""}
→ 400 {"error":{"code":"invalid","message":"Kiritilgan ma'lumot noto'g'ri",
        "details":{"username":["Ushbu maydon to'ldirilishi shart."]}}}
```

Ya'ni **sayt orqali hech kim ro'yxatdan o'ta olmasdi**. Qaror qog'ozda
to'g'ri edi, kodda esa faqat yarmi bajarilgan.

### Ildiz sabab

`RegisterSerializer.extra_kwargs` da:

```python
"display_name": {"required": False, "allow_blank": True},   # ✓
"country":      {"required": False, "allow_blank": True},   # ✓
"region":       {"required": False, "allow_blank": True},   # ✓
"username":     {"validators": []},                         # ✗ yetarli emas
```

`username` model maydonida `unique=True` bor → DRF `ModelSerializer` uni
`required=True, allow_blank=False` qilib yasaydi. `validators: []` faqat
validatorlar ro'yxatini tozalaydi; `required` va `allow_blank` ga
tegmaydi. Konteyner ichida o'lchandi:

```
username       required=True  allow_blank=False    ← buzilgan
email          required=True  allow_blank=False    ← to'g'ri (pochta majburiy)
display_name   required=False allow_blank=True
country        required=False allow_blank=True
region         required=False allow_blank=True
```

### Nega uch qavat himoya ham ko'rmadi

| Qavat | Nega ko'rmadi |
| ----- | ------------- |
| `pytest` | mavjud testlar faqat `errors["email"]` ni tekshirardi. Ular `username` yubormasdan ham `is_valid()` `False` olardi va shu xatoga **hech qachon qaramagan** — xato to'g'ri javob ichida jimgina yonma-yon turgan |
| Qo'lda sinov | API'ni to'g'ridan-to'g'ri chaqirgan probe `username` yuborardi → `201`. Ya'ni sinov usuli xatoni yashirgan |
| `check_deploy.sh` | konteyner manbadan **eski emas** edi (sha256 bir xil) — nomuvofiqlik manbaning O'ZIDA edi, deploy'da emas |

**Saboq:** «maydonni olib tashlash» — bir tomonlama amal emas. Uni
iste'molchidan olib tashlash yetarli emas; ishlab chiqaruvchi tomon ham
uni **ixtiyoriy** deb bilishi kerak. Va `extra_kwargs` da `validators`
tozalash `required` ni o'zgartirmaydi — modeldan meros qolgan
`unique=True`/`blank=False` DRF maydoniga ko'chadi.

### Tuzatish

```python
"username": {"required": False, "allow_blank": True, "validators": []},
```

⚠️ Ikkala bayroq ham shart. `required: False` bo'lib `allow_blank: False`
qolsa, eski mijozning bo'sh satri «This field may not be blank» bilan rad
etiladi (o'lchandi — probe B).

### Qo'shilgan to'siqlar (uch joyda)

| Joy | Nima qiladi |
| --- | ----------- |
| `tools/check_contract.py::check_register_contract()` | web 1-qadamda yuboradigan maydonlarni o'qiydi va API ularning har biri uchun `required: False` + `allow_blank: True` talab qiladi. `extra_kwargs` **qavslar sanog'i** bilan o'qiladi (`_brace_block`) — ichma-ich lug'at sababli regex jimgina chala o'qirdi |
| `apps/api/tests/test_auth.py` | `test_username_siz_royxatdan_otish_ishlaydi`, `test_username_bolsh_qiymat_bilan_ham_ishlaydi`, `test_username_berilsa_saqlanadi` |
| `docs/10-operations/README.md` | nosozlik sinfi tavsifi («eskirgan konteyner EMAS») |

**Tekshiruv natijalari:**

| Tekshiruv | Natija |
|---|---|
| `check_contract.py` — 3 salbiy test | ✓ har biri `exit 1`, tiklanganda `exit 0`, fayl **bayt-bayt** tiklandi |
| Yangi 3 test — buzuq kodda | ✓ **FAIL** (aynan kutilganidek) |
| Yangi 3 test — tuzatilgan kodda | ✓ **PASS** |
| `ci-local.sh api` | ✓ 729 test, ruff + mypy + migratsiya |
| `ci-local.sh all` | ✓ HAMMASI O'TDI (3 qadam) |
| Brauzerda haqiqiy ro'yxatdan o'tish | ✓ `201` → avtomatik login → `/qoshimcha-malumot?welcome=1` |
| `check_deploy.sh` | ✓ 5/5 joyida |

### Ochiq savol — o'lchandi: o'chirilgan taxallus DARHOL bo'shaydi

`AccountDeleteSerializer` hisobni **anonimlashtiradi** (`account.anonymize`):
email `''`, parol ishlamaydigan, `is_active=False`, taxallus
`neytrino_<pk>`, `SocialAccount` va **`UsernameHistory` o'chiriladi.**

Dastlab «taxallus band qoladi» deb o'ylagan edim — **o'lchov buni rad
etdi.** Sinov hisobi bilan tekshirildi:

| Tekshiruv | Natija |
|---|---|
| `User.username == 'sinovdel'` qoldimi | **yo'q** (`neytrino_10460` ga almashgan) |
| `usernames.reserved('sinovdel')` | **`False`** |
| Tarixdagi oldingi nom (`'EskiNom'`) `reserved` | **`False`** |
| `UsernameHistory` yozuvlari | **0** (o'chirilgan) |

Ya'ni hisobini o'chirgan odamning taxallusi **darhol** bo'shaydi va uni
**istalgan kirmagan odam** egallab olishi mumkin — 90 kunlik bandlik
himoyasi ham ishlamaydi, chunki himoya aynan `UsernameHistory` ga tayanadi
(`usernames.reserved` o'sha jadvaldan o'qiydi) va u o'chiriladi.

**Nega bu muhim:** taxallus bu platformada kimlik — standings, profil
havolasi, musobaqa jadvallari unga bog'langan. O'chirilgan hisobning
obro'li taxallusini egallash — `usernames.py` boshidagi izohda
taqiqlangan stsenariy («yangi egasi eski egasining obro'si bilan
standings'da tura olardi»).

**Ziddiyat ildizi:** `anonymize` da `UsernameHistory` ni o'chirish
«eski taxalluslar odamni yangi nomiga bog'lab turadi» degan GDPR sababi
bilan qilingan. Lekin yon ta'siri — 90 kunlik bandlik ham yo'qoladi.
Ya'ni ikki maqsad bir jadvalga tayangan.

**Qaror kerak (uch variant):**

| Variant | Nima bo'ladi |
|---|---|
| A. Hozirgicha | o'chirilgan nom darhol erkin — obro' o'g'irlash mumkin |
| B. O'chirishdan oldin eski nomni 90 kunga band qilish | `UsernameHistory` o'rniga alohida `ReservedUsername` yozuvi (GDPR: odamga bog'lanmagan, faqat nom) |
| C. `neytrino_<pk>` ham 90 kun band | yuqoridagi bilan bir xil, lekin vaqtinchalik nom ham himoyalanadi |

**Tavsiya — B.** Bandlik yozuvi foydalanuvchiga bog'lanmaydi (`user` FK
o'rniga faqat nom + sana), ya'ni GDPR maqsadi saqlanadi, himoya esa
qaytadi.

* Pochta ham bo'shaydi (`email: ''`) — tekshirildi ✓ (o'sha pochta bilan
  yangi hisob ochish mumkin).
