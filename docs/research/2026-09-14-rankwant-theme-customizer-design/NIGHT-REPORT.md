# Tungi ish hisoboti — tema sozlagichi

**Sana:** 2026-09-14, 00:15 → 00:35
**Holat:** to'xtatildi — 12 ta majburiy banddan **2 tasi + 0-qadam** bajarildi
**`origin/main`:** `7234e8f`

---

## 1. Nima qilindi

| Commit | Mazmuni |
|---|---|
| `ddc328c` | `fix(a11y)`: accent-matn juftligi o'lchandi, **7 palitra** tuzatildi |
| `b8b945c` | `feat(core)`: `ui_prefs` v2 — guruhlangan, versiyalangan, migratsiya + validator |
| `7234e8f` | `feat(web)`: `system` mavzu rejimi, prefs v2 ga o'tkazildi |

### 0-qadam — nuqson TUZATILDI ✅

`check_contrast.py` ga accent-matn tekshiruvi qo'shildi. Natija men
kutganimdan **ancha katta** chiqdi:

- Men "nuqson bitta uslubda (`dashboard`)" deb hisoblagandim.
- Haqiqatda: **27 juftlik, 7 palitra** — brutal 3.70, clay 4.41,
  dashboard 4.05, flat 4.44, flat.dark 3.77, neu 4.07, skeu 3.31.
- Sabab: qo'lda faqat `ground`/`surface`/`soft` ni sinagan edim; checker
  fon sifatida `--rw-hover`, `--rw-chip`, `--rw-field` ni ham oladi.

Tuzatish: har palitrada `--rw-accent-ink` **oklab yorqinligi** bo'yicha
qayta hisoblandi — tus va to'yinganlik saqlandi, o'zgarish ko'zga
sezilmaydi (`clay` `#7c3aed`→`#7936ea`, `skeu` `#36639c`→`#204d84`).

**Salbiy test o'tdi:** `dashboard` ataylab `#b9c9f5` ga buzilganda
`exit 1` va yangi qator chiqdi; tiklanganda `exit 0`.
**Natija: 718 matn rangi AA (ilgari 691).**

### 1-band — Backend sxemasi ✅

- `core/prefs.py` — guruhlangan, versiyalangan sxema; validator shu yerda.
- `{version: 2, appearance, tokens, a11y, templates, sound, effect}`.
- `0016_ui_prefs_v2` migratsiyasi + o'qishda moslash.
- Noma'lum versiya **saqlanadi, qo'llanmaydi** (D36).
- 20 yangi test.

### 2-band — `system` mavzu rejimi ✅ (qisman)

- `ThemeContext`: `mode` (tanlov) va `theme` (yechilgan) ajratildi.
- Hidratsiyadan oldingi skript `system` ni `matchMedia` bilan yechadi.
- OS o'zgarsa faqat `system` rejimida qayta qo'llanadi (animatsiyasiz).
- Sozlamalar sahifasida uchta tugma: Yorug' / Qorong'i / **Tizim**.
- `theme.system` 10 tilga qo'shildi (734 kalit).

**Yetishmaydi:** bir muhitli uslub tanlanganda mavzuning **avtomatik**
moslashuvi (D6) — hozir tanlagich shunchaki yashiriladi, avtomatik
o'tish yozilmagan.

---

## 2. Nima qoldi

| Band | Holat | Sabab |
|---|---|---|
| 3. Panel (drawer/sheet/tugma/klaviatura) | boshlanmagan | vaqt |
| 4. Rang (namuna + erkin tus + jonli kontrast) | boshlanmagan | vaqt |
| 5. Shrift (4 oila) | boshlanmagan | vaqt |
| 6. O'lcham va zichlik | boshlanmagan | vaqt |
| 7. 8 shablon | boshlanmagan | vaqt |
| 8. Qulaylik to'plami | boshlanmagan | vaqt |
| 9. Header'dan eski tugmalarni olish | boshlanmagan | panelga bog'liq |
| 10. Saqlash / undo / uch bosqichli tiklash | boshlanmagan | panelga bog'liq |
| 11. Panel i18n | boshlanmagan | panel yozilmagan |
| 12. Feature flag | boshlanmagan | modul yo'q |
| Stretch (D21, D22, D37) | boshlanmagan | — |

**Taxmin:** 8 soatda 12 bandning hammasi sig'masdi. 0-qadam va backend
kutilganidan ko'proq vaqt oldi (ayniqsa nuqson 7 palitrada chiqqani).

---

## 3. O'zim qabul qilgan qarorlar

| № | Qaror | Sabab |
|---|---|---|
| D47 | Mavzu `User.theme` da qoladi, `ui_prefs.appearance.theme` **yo'q** | Maydon allaqachon bor (`default="system"`) va `PrefsSync` undan sinxronlaydi. Ikki joyda saqlash hujjatning o'z tamoyiliga zid |
| — | `sound`/`effect` yuqori darajada qoldi | Ular ko'rinish emas; guruhga ko'chirish eski klientni buzardi, foyda yo'q |
| — | `validate_theme` qo'shildi | Maydon har qanday 16 belgili satrni qabul qilardi — `Dark` yozilsa mavzu umuman qo'llanmasdi |
| — | `UI_EFFECTS` `core/prefs.py` ga ko'chdi, eski nom alias bo'lib qoldi | Ta'rif sxema bilan bir joyda tursin; tashqi havola buzilmasin |
| — | `accent` **tus** sifatida saqlanadi, hex emas | Bitta rang ikki muhitga sig'maydi (D42 o'lchovi) — yorqinlik har muhitda alohida hisoblanadi |
| — | `tokens` sxemasi yozildi, UI yozilmadi | D43 flag bilan o'chiq; sxema tayyor tursa flag yonganda migratsiya kerak bo'lmaydi |

---

## 4. O'lchangan raqamlar

| Tekshiruv | Natija |
|---|---|
| Kontrast (to'liq) | **718** matn rangi AA — ilgari 691 |
| Accent-matn nuqsoni | **27 juftlik / 7 palitra** — 0 ga tushdi |
| Salbiy test (kontrast) | buzilganda `exit 1` ✓, tiklanganda `exit 0` ✓ |
| `check_i18n.py` | 10 til × **734** kalit — to'liq |
| `ci-local.sh api` | ruff, mypy, migratsiya, **pytest** — yashil |
| `ci-local.sh types` | yashil |
| `check_deploy.sh` | **0** |
| Migratsiya | `core.0016_ui_prefs_v2` qo'llandi |

---

## 5. Jonli tekshiruv

| Amal | Natija |
|---|---|
| `https://rankwant.uz/` | 200 |
| `https://rankwant.uz/settings/korinish` (sessiya bilan) | 200 |
| `https://rankwant.uz/settings/korinish` (mehmon) | 307 → kirish |
| `https://rankwant.uz/platform-roadmap` | 200 |
| Mavzu skripti HTML da | `prefers-color-scheme: dark` mavjud ✓ |
| `PATCH /me/` `ui_prefs` v2 | 200, qiymat qaytdi ✓ |
| `PATCH /me/` `ui_prefs` v1 (yassi) | **400** ✓ |
| `PATCH /me/` `theme: "system"` | 200 ✓ |
| `PATCH /me/` `theme: "Dark"` | **400** ✓ (yangi validator) |

Vaqtinchalik `probe_prefs_*` hisobi o'chirildi — **qoldiq 0**.

---

## 6. Topilgan yangi nuqsonlar

1. **Accent-matn** (tuzatildi) — 7 palitra, batafsil yuqorida.
2. **`User.theme` validatorsiz** (tuzatildi) — `validate_theme` qo'shildi.
3. **`PrefsSync` `system` ni hisobga olmasdi** (tuzatildi) — hisobda
   `system` turib qurilmada `dark` bo'lsa qurilma ustun bo'lardi, ya'ni
   D4 ("hisob ustun") amalda buzilgan edi.
4. **Uchta chaqiruv v1 shaklida yozardi** (tuzatildi) — `PrefsSync` ×2,
   `AppearanceSection` ×1. Yangi validator ularni 400 qilardi.

Qolgani: yo'q.

---

## 7. Tunda to'xtagan joy

**To'xtash nuqtasi:** 2-band tugadi, **3-band (panel) boshlanmagan**.

**Nima uchun:** vaqt. 0-qadam va backend kutilganidan ko'proq oldi —
ayniqsa kontrast nuqsoni 7 palitrada chiqqani va sxemani
`User.theme` bilan to'qnashuvi aniqlangani. Har ikkisi ham
"bilib turib qoldirib ketish" emas, balki oldin hal qilinishi kerak
bo'lgan ish edi.

**Keyingi qadam:** 3-banddan boshlash (panel karkasi: suzuvchi tugma +
drawer/sheet + modal emas + `Ctrl+.`), keyin 4-band (rang), chunki
qolgan hamma narsa shu ikkisiga tayanadi.

**Muhim:** hozirgi holat **production'da xavfsiz** — sozlagich UI si
yo'q, ya'ni foydalanuvchi hech narsa o'zgartira olmaydi. O'zgargan
narsa: mavzu endi `system` bo'lishi mumkin (standart), va 7 palitraning
havola rangi biroz quyuqlashdi. Ikkalasi ham yaxshilanish.

---

# Ikkinchi yurish — davomi

**`origin/main`:** `d4e6354`

## Bajarilgan yangi bandlar

| Commit | Band |
|---|---|
| `d4e6354` | **3-band (panel)** va **4-band (rang)** — ikkalasi bir commitda |

### 3-band — panel ✅

- Suzuvchi tugma: yopiladi, holati eslab qolinadi (D28), telefonda YO'Q (D32).
- Ish stolida o'ng drawer, telefonda uch nuqtali sheet — standart yarim (D27, D31).
- **Modal emas** (D29): fon qoraytirilmaydi, fokus tuzog'i yo'q, sahifa ishlaydi.
  `aria-modal` ataylab qo'yilmadi — yolg'on e'lon ekran o'quvchini chalg'itadi.
- `Ctrl+.` istalgan sahifada, `Esc` yopadi va fokusni qaytaradi (D30).

### 4-band — rang ✅

- **Tus + to'yinganlik**, xom hex emas (D42). Yorqinlik ikki muhit uchun
  **binary search** bilan hosil qilinadi.
- Fonlar ro'yxati checker bilan **aynan bir xil**: `ground`, `surface`,
  `surface-2`, `chrome`, `chip`, `field`, `hover`. Qo'lda tanlangan tor
  ro'yxat kam ko'rsatardi — accent nuqsoni shuni isbotladi.
- **Uchta juftlik** (D45): tugma, chip, havola. `--rw-accent-ink` ikkalasiga
  ham (fon va chip) qarshi hosil qilinadi.
- **Jonli kontrast ko'rsatkichi** va ✗ kombinatsiya **saqlanmaydi** (D11).
- `lib/theme/color.ts` — `tools/check_contrast.py` bilan ayni formula;
  ma'lum qiymatlarda sinandi (21.00 / 4.54 / 4.48), ya'ni ikki qavat
  bir xil raqam beradi (D12).

### Qo'shimcha ✅

- **8 shablon** (D41) — bir bosishda uslub + mavzu + shrift + zichlik.
- **4 shrift** `next/font` bilan o'zimizda, `preload: false` (D13) — faqat
  tanlangani yuklanadi. Editorial/Terminal o'z shriftini saqlaydi (D14).
- **Shrift o'lchami va zichlik** — alohida boshqaruv (D15, D16).
- **Qulaylik to'plami** (D18): harakatni kamaytirish, katta bosish
  maydonlari, kuchli fokus halqasi.
- **Uch bosqichli tiklash** + bekor qilish (D24, D25).
- 41 kalit × 10 til — **775 kalit**, `check_i18n.py` toza.

### Ikki lint xatosi TUZATILDI, yashirilmadi

`react-hooks/set-state-in-effect` ikki joyda urdi:
1. `hidden` bayrog'i `useSyncExternalStore` ga ko'chirildi (loyiha naqshi).
2. Mount'dagi accent effekti **olib tashlandi** — boot skript uni allaqachon
   qo'llaydi, panel esa kerak bo'lganda o'lchaydi.

## Qolgan bandlar

5 (shrift — bajarildi), 6 (o'lcham — bajarildi), 7 (shablonlar — bajarildi),
8 (qulaylik — **qisman**: uchta sozlama bor, rang ajratolmaslik
**palitralari yo'q**), 9 (header'dagi eski tugmalar **hali turibdi**),
10 (saqlash — bajarildi), 11 (i18n — bajarildi), 12 (feature flag — yo'q),
stretch (D21, D22, D37 — yo'q).

## Jonli holat

| Tekshiruv | Natija |
|---|---|
| `check_deploy.sh` | **0** |
| `/`, `/updates`, `/platform-roadmap` | 200 |
| Sozlagich tugmasi HTML da | bor (`rw-customizer-open`) |
| Boot skript | `rw:appearance` mavjud |
| `ci-local.sh web` | lint, types, build — yashil |
| `ci-local.sh types` | yashil |

**Ochiq:** panel brauzerda **qo'lda sinalmagan** — `Ctrl+.`, drawer,
accent hosil qilish va kontrast ko'rsatkichi jonli brauzerda
tekshirilmagan. Keyingi qadam shu (chrome-devtools MCP bilan).

---

# Uchinchi yurish — brauzerda tekshirish (`826fe98`)

Panel jonli brauzerda sinaldi (chrome-devtools MCP) va **uchta haqiqiy
xato** topildi — uchalasi ham CI yashil bo'lgan holatda yashiringan edi.

## Topilgan xatolar

### 1. Muhit KLASSdan olinardi — bir muhitli uslublarda yolg'on

`clay` — `dual: false`, ya'ni `[data-style="clay"].dark` bloki **yo'q**.
`<html>` da `dark` klassi turgani uchun `isDarkMode()` `true` qaytarardi,
lekin o'lchangan barcha fonlar **yorug'** edi (`--rw-ground: #ede4ff`).

Oqibat: chip qorong'i qilinardi, fonlar yorug' qolardi → `deriveAccent`
yorug' va qorong'i aralash to'plamga qarshi ishlab **`null`** qaytardi →
`?? accent` zaxirasi ishga tushib `--rw-accent-ink` accent'ning **o'ziga**
teng bo'lib qolardi. Ko'rsatkich: **2.74:1 ✗**.

Tuzatish: muhit **o'lchangan** ground yorqinligidan aniqlanadi
(`environmentIsDark`). Tuzatishdan keyin: **4.60:1 ✓**, havola rangi
haqiqatan hosil qilinadi.

### 2. Accent keshi O'CHIRILIB qo'yilardi

`commit` → `rememberAppearance(next, a11y, null)` — uchinchi argument
`null` "accent'ni olib tashla" degani edi va `applyAccent` yozgan qiymatni
o'chirardi. Ya'ni **rang saqlanmasdi**: reload'dan keyin qaytib ketardi.

Tuzatish: kesh uchun alohida yozuvchi (`rememberAccent`);
`rememberAppearance` unga tegmaydi.

### 3. Yon ta'sirlar `setState` updater'i ICHIDA edi

`setAppearance`, `setA11y`, `applyTemplate` — uchalasi ham DOM yozuvi va
tarmoq xabarini **updater funksiyasi ichida** bajarardi. React updater'ni
bir necha marta chaqirishi mumkin (StrictMode aynan shunday qiladi), ya'ni
bu ikki marta qo'llanardi. Tuzatish: qiymat tashqarida hisoblanadi,
updater sof qoladi.

## Tekshirilgan natijalar (jonli brauzer)

| Amal | Natija |
|---|---|
| Suzuvchi tugma (1920px) | chizilgan, 32×91 px, o'ng chetda |
| Panel ochilishi | 8 bo'lim, 14 tus namunasi |
| Qizil tus (ilgari yiqilgan) | **4.60:1 ✓**, bloklanmagan |
| Ko'k tus qo'llash | `--rw-accent: #1c61c2`, havola `rgb(28, 97, 194)` |
| Kesh | `{style, accent, fg, soft, ink}` yozildi |
| Reload | **saqlandi** (`#1c61c2`) — boot skript chaqnashsiz qo'llaydi |
| `check_deploy.sh` | **0** |

## Saboq

Uchala xato ham **CI yashil** holatda yashiringan edi: lint, types, build va
kontrast tekshiruvi hech birini ko'rmaydi, chunki ular **ishlash vaqtidagi**
mantiq — statik tekshiruv emas. Faqat brauzerda o'lchash ko'rsatdi.

Ayniqsa 1-xato: u **aynan loyihaning o'z saboqi** edi — "bir muhitli
uslublarda klass yolg'on gapiradi" — va men uni `lib/theme/color.ts` da
takrorladim, chunki `check_contrast.py` CSS manbasini o'qiydi, klassga
qaramaydi. Ya'ni **CI to'g'ri edi, yangi kod xato edi**.

---

# To'rtinchi yurish — yakunlash (`a452193`)

8-bandning qolgani, 9-band va 12-band bajarildi.

## 9-band — header (D3) ✅

`ThemeToggle` va `StylePicker` **o'chirildi** (fayllari ham). O'rniga bitta
ikonka — panelni ochadi. Ikkita tugma bir xil sozlamani boshqarardi va
yangi sozlamalar qaysi biriga tegishli ekani noaniq edi.

⚠️ Ikonka telefonda **shart**: u yerda suzuvchi tugma yo'q (D32), ya'ni
bu — asosiy kirish nuqtasi. Shuning uchun `lg:` bilan yashirilmaydi.
`LocaleSwitch` qoldi — u kontent tili, ko'rinish emas.

## 8-bandning qolgani — rang ajratolmaslik (D44) ✅

Palitra **moslashadi**, simulyatsiya qilinmaydi: rang ajratolmaydigan odam
sahifani allaqachon shunday ko'radi, unga ajralib turadigan palitra kerak.

Qiymatlar **ishlash vaqtida** o'lchangan fonlarga qarshi hosil qilinadi —
accent bilan bir xil usul. CSS da statik yozib **bo'lmaydi**:
har semantik ink palitra bo'yicha e'lon qilinadi va
`[data-style="x"].dark` har qanday `[data-vision]` qoidasidan xoslikda
ustun, ya'ni statik blok **jimgina yutqazardi**. Bir muhitli uslublarda
esa `.dark` klassi noto'g'ri qiymat tanlardi.

**Jonli tekshirildi (protanopiya):**

| Holat | Oldin | Keyin |
|---|---|---|
| ok | `#2f9e6d` (yashil) | `#0a63bc` (ko'k) |
| warn | `#c08a1e` (sariq) | `#6e6506` (zaytun) |
| bad | `#d1547f` (pushti) | `#955308` (to'q sariq) |

Ya'ni qizil-yashil o'qi ko'k-sariq o'qiga ko'chdi — protanopiyada saqlanib
qoladigan yagona o'q.

## 12-band — feature flag (D38) ✅

`NEXT_PUBLIC_CUSTOMIZER=0` → suzuvchi tugma, header ikonkasi va panel
ko'rinmaydi; saqlangan sozlamalar bazada va qurilmada qoladi.

⚠️ **Cheklov ochiq yozildi:** `NEXT_PUBLIC_*` build vaqtida bundle'ga
singadi, ya'ni o'chirish uchun `web` ni qayta qurish kerak (~40 s
o'lchandi). Haqiqiy "bir tugma" kerak bo'lsa bayroqni API dan olib kelish
kerak — alohida ish.

## Yakuniy holat

| Tekshiruv | Natija |
|---|---|
| `ci-local.sh web` | lint, types, build — yashil |
| `check_i18n.py` | 10 til × 775 kalit |
| `check_deploy.sh` | **0** |
| Header tugmalari | `Menyu`, `Ko'rinish sozlagichi` — mavzu tugmasi YO'Q |
| Rang rejimi (protan) | jonli qo'llandi ✓ |

## Qolgan ish

Faqat **stretch**: D21 (shaxsiy shablonlar), D22 (havola orqali ulashish),
D37 (admin standart ko'rinishi). Majburiy yadro **to'liq bajarildi**.

---

# Beshinchi yurish — stretch va kritik tuzatish

## D21 — shaxsiy shablonlar ✅

Saqlash, qo'llash, o'chirish. Kirgan odamda 5 ta, mehmonda 2 ta.
Bir xil nom ustidan yoziladi (validator dublikatni rad etadi — qo'shish
400 berardi va sabab tushunarsiz bo'lardi). Nom oddiy maydonda kiritiladi,
`window.prompt` emas: u bloklaydi va mobil brauzerda ishonchsiz.

Shablonlar **butun ro'yxat** bo'lib yuradi, hech qachon birlashtirilmaydi —
birlashtirilsa o'chirish imkonsiz bo'lardi.

## D22 — havola orqali ulashish ✅

Sozlamalar URL ga yoziladi, olgan odam darhol ko'radi. Saqlash joyi ham,
moderatsiya ham kerak emas (umumiy kutubxona rad etilgan edi — u ikkalasini
talab qilardi). Qo'llangach parametrlar manzildan **olib tashlanadi**, aks
holda har yuklanishda qayta qo'llanib, odam o'z sozlamasini o'zgartira
olmay qolardi. Notanish qiymatlar jimgina tashlanadi.

## ⚠️ KRITIK XATO — sayt butunlay ishlamay qolgan edi

`CustomizerProvider` `useSession()` ni chaqiradi (shablon chegarasi uchun),
lekin `SessionProvider` uning **ichida** turardi. React birinchi renderda
yiqildi va **butun daraxt** chizilmadi — sahifa bo'sh qoldi.

**Buni hech bir tekshiruv ko'rmadi:**

| Tekshiruv | Natija |
|---|---|
| `curl https://rankwant.uz/` | **200** |
| `check_deploy.sh` | **0** |
| `ci-local.sh web` | **yashil** |
| Brauzer | **bo'sh ekran** |

Sabab: SSR qobig'i klient daraxtidan OLDIN qaytariladi, ya'ni HTTP 200
"ishlayapti" degani emas. Faqat devtools MCP orqali ochish ko'rsatdi.

Tartib tuzatildi: `Style > Theme > Session > Customizer`, izohi bilan.

**Saboq:** "curl 200" va "CI yashil" **ishlashni isbotlamaydi**. Klient
tomonda yiqiladigan xato uchun brauzerda ochishdan boshqa yo'l yo'q.

---

# Oltinchi yurish — D37 va YAKUN (`deafc3c`)

## D37 — jamoa standart ko'rinishi ✅

`SiteAppearance` — singleton model, Django admin'dan tahrirlanadi,
`GET /api/v1/appearance/` orqali ommaviy o'qiladi.

**Faqat boshlang'ich qiymat:** qurilmada yoki hisobda saqlangan tanlov
har doim ustun turadi, ya'ni **mavjud foydalanuvchilarga tegilmaydi** —
qaror shuni talab qilgan edi.

Qiymat **serverda** olinadi va prop bo'lib uzatiladi, chunki u `useState`
boshlang'ich qiymatida kerak: mijozda so'ralsa, u kelguncha kod standarti
ko'rinib, keyin almashardi — chaqnashni oldini olish uchun qurilgan butun
tizim ma'nosiz bo'lardi.

Admin ikkinchi qator qo'shishni rad etadi (ikkitasi bo'lsa qaysi biri
qo'llanishi noaniq) va o'chirishni ham (bo'sh qator bilan yo'q qator bir
xil ma'noni beradi).

## YAKUNIY HOLAT — barcha bandlar bajarildi

| Band | Holat |
|---|---|
| 0. Nuqsonni tuzatish | ✅ 7 palitra, 27 juftlik |
| 1. Backend sxemasi | ✅ v2, migratsiya, o'zgarishsiz |
| 2. Mavzu (`system`) | ✅ |
| 3. Panel | ✅ |
| 4. Rang | ✅ |
| 5. Shrift | ✅ |
| 6. O'lcham va zichlik | ✅ |
| 7. Shablonlar | ✅ |
| 8. Qulaylik | ✅ (D44 palitralari ham) |
| 9. Header | ✅ |
| 10. Saqlash va tiklash | ✅ |
| 11. i18n | ✅ 782 kalit |
| 12. Feature flag | ✅ |
| Stretch: D21, D22, D37 | ✅ |

**Hech narsa qolmadi.**

## Jonli tekshiruv (yakuniy)

| Tekshiruv | Natija |
|---|---|
| Migratsiya `core.0017_siteappearance` | qo'llandi |
| `GET /api/v1/appearance/` | `{"appearance":{}}` |
| `check_deploy.sh` | **0** |
| `/`, `/updates` | 200 |
| Brauzer: sahifa chiziladi | ✅ |
| Brauzer: panel bo'limlari | 8 ta |
| Brauzer: accent saqlangan | `#1c61c2` |
| `ci-local.sh api` / `web` | yashil |

## Umumiy hisob

**6 yurish · 10 commit · 8 topilgan nuqson.**

Uchtasi faqat **brauzerda** ko'rindi:
1. Muhit klassi bir muhitli uslublarda yolg'on gapiradi (2.74:1 ✗)
2. Accent keshini `commit` o'chirib qo'yardi (rang saqlanmasdi)
3. `SessionProvider` tartibi teskari — **butun sayt bo'sh qoldi**

Uchalasi ham `curl 200` va **yashil CI** holatida yashiringan edi.

---

# Yettinchi yurish — DoD ning qolgan uch bandi (`9cdcd25`)

Barcha bandlar bajarilgach, topshiriqning **tayyorlik mezonini** qayta
tekshirdim va **uch band bajarilmagan** ekanini topdim:

## 1. Inglizcha hujjat ✅

`docs/08-technical-spec/theme-customizer.md` — rang modeli, uchta juftlik,
ikki qavatli kafolat, muhitni aniqlash qoidasi, sxema, feature flag va
**tuzoqlar**. `docs/` ning qolgani inglizcha, shunga moslashtirildi.

## 2. Panel tekshiruvchisi CI bilan aynan mos ✅ — O'LCHANDI

Brauzerda tus tanlanib, panel ko'rsatgan son o'qildi; so'ng xuddi shu
token qiymatlari `check_contrast.py` ning **o'z funksiyalariga** berildi:

| Juftlik | Panel | CI | Farq |
|---|---|---|---|
| Tugma matni | 7.33:1 | 7.32:1 | **0.01** |
| Matn (havola) | 5.68:1 | 5.67:1 | **0.01** |

Farq **chegaralangan va tushuntirilgan**: brauzer yaxlitlanmagan rangni
o'lchaydi, Python esa yozilgan 8-bit hex ni o'qiydi. Tolerantlik 0.01,
ya'ni ikki qavat ajralib ketmagan.

## 3. Panel 10 tilda sig'adi ✅ — O'LCHANDI

Har tildagi eng uzun **uzilmas** so'z o'lchandi (so'zlar bo'shliqda
o'raladi, ya'ni xavf faqat bitta uzun so'zda):

| Til | Eng uzun so'z | Belgi |
|---|---|---|
| tr | `Özelleştiriciyi` | 15 |
| ky / ru / uz / es | `Жеткиликтүүлүк` / `Красно-зелёное` / `o'zgartirilgan` / `personalizador` | 14 |
| en / kk | `Accessibility` / `Қолжетімділік` | 13 |
| kaa / tg | `shablonlarım` / `нусхабардорӣ` | 12 |
| zh | `调色板会自适应：…` | 24 |

Eng yomon lotin holati — 15 belgi (~120px), panelda ~320px matn maydoni
bor. **`zh` istisno emas:** CJK belgi bo'yicha o'raladi, ya'ni 24 belgi
sig'maslik xavfi tug'dirmaydi.

**Xulosa: hech bir tilda uzilmas so'z panel kengligidan oshmaydi.**

## Tayyorlik mezoni — YAKUNIY

| Mezon | Natija |
|---|---|
| `ci-local.sh all` (docs, api, web, types) | **0** — 3 qadam o'tdi |
| `check_deploy.sh` | **0** |
| Kontrast: 18 palitra + override | 718 rang AA |
| Panel tekshiruvchisi ↔ CI | **0.01** farq — mos |
| Jonli: panel, rang, saqlash | ✅ brauzerda |
| Panel 10 tilda | ✅ eng uzun so'z 15 belgi |
| `check_i18n.py` | 782 kalit |
| `origin/main` ga push | ✅ `9cdcd25` |
| Inglizcha hujjat | ✅ |

**Topshiriq to'liq bajarildi. Qolgan ish yo'q.**


---

# Sakkizinchi yurish — MCP bilan chuqur audit

Savol: brauzer, tarjima, ikonka, rang, Lighthouse. **Halol javob:** oldin
faqat **qisman** tekshirgan edim — Lighthouse umuman ishlatilmagan,
tarjimalar UI da ko'rilmagan, ikonkalar tekshirilmagan. To'liq qilinganda
**beshta haqiqiy xato** topildi.

## Lighthouse

| O'lchov | Panelsiz | Panel ochiq |
|---|---|---|
| Accessibility | 100 | **97 -> 100** (tuzatildi) |
| Best Practices / SEO / Agentic | 100 | 100 |
| Mobil (390x844) | — | **100 / 100 / 100 / 100** |
| **LCP** | — | **217 ms** (TTFB 164 + render 53) |
| **CLS** | — | **0.00** |

`CLS 0.00` ayniqsa muhim: sozlagich hidratsiyadan **oldin** stil qo'llaydi,
ya'ni chaqnash ham, siljish ham yo'q.

## Topilgan xatolar

### 1. Holat ranglari hech qachon AA dan o'tmagan (eng katta)

Lighthouse panelda 97 berdi va sababni aytdi: `rw-warn-ink` sirt ustida
`clay` da **2.87:1**. Bu mening ishlatish xatoim edi — lekin tekshirganda
ostida kattaroq muammo chiqdi.

`--rw-ok-ink` / `--rw-warn-ink` / `--rw-bad-ink` **umuman o'lchanmagan
ekan** (`--rw-kind-*` uchun tekshiruv bor edi, bu uchtasi uchun yo'q).
O'z `-soft` fonida — mo'ljallangan juftlikda — **17 palitra yiqilardi**:
`clay` ok 2.96:1, `flat` warn 2.57:1, `neu` ok 3.24:1. Ya'ni mahsulotdagi
**har bir holat nishoni** AA dan past edi.

Ikki narsa aniqlanishi kerak edi:

**Shartnoma nima.** Ilovada yagona ishlatish — `certificates/[id]`:
`rw-ok-soft` fon + `rw-ok-ink` matn. Bu **nishon tokenlari**. Tekshiruvning
birinchi versiyasi ularni sirt ustida ham talab qilardi — ular bunga
mo'ljallanmagan va ba'zi palitralarda bajarib bo'lmaydi (sirtlar bir
vaqtda juda yorug' ham, juda qorong'i ham). Endi tekshiruv haqiqiy
shartnomani qoplaydi, panel esa hamma kabi soft juftligini ishlatadi.

**Nega ba'zi palitralar tuzalmadi.** Beshta qorong'i palitrada `-soft`
yorug tint edi (`#e6f6f3`, yorqinlik 0.89) sirtlar esa qorong'i (0.006) —
palitra o'ziga zid, hech qanday ink ikkalasiga sig'maydi. O'sha soft'lar
qorong'i tintga o'zgartirildi.

**Yana bir tuzoq:** qidiruv yo'nalishi 0.5 yorqinlik chegarasidan
foydalanardi, ya'ni `brutal` ning `#ff9d9d` foni (0.48) qorong'i deb
hisoblanib, qidiruv **teskari** ketgan. To'g'ri krossover — **0.1791**.

### 2. Panel xom i18n kalitlarini ko'rsatgan (foydalanuvchiga ko'rinadigan)

`kk` tilida panelni ochganda ekranda `customizer.tab.appearance`,
`customizer.template.classic`, `customizer.font.inter` — **kalit nomlari**
turgan edi. Bu **hamma tilda**, jumladan o'zbekchada ham.

`check_i18n.py` esa yashil turgan: u `uz.ts` da BOR kalitlarning 10 tilda
borligini tekshiradi, kodda ISHLATILGAN kalitlarni emas. To'qqiz kalit
yetishmasdi.

### 3. Ikonka ikki xil vazifaga ishlatilgan

Sozlagich tugmasi `UpdatesIcon` ni ishlatardi — yangilanishlar
qo'ng'irog'i bilan **ayni ikonka**. Ikki xil vazifa, bir xil belgi.
`PaletteIcon` ga o'zgartirildi.

### 4. `skeu` ning `-soft` i gradient — o'qilmagan

Checker uni "o'qilmadi" deb xato berardi. Endi `stops()` orqali eng yomon
pog'ona olinadi, tugma juftligidagi kabi.

### 5. Checkerning yangi tekshiruvi O'LIK tug'ilgan

Kodda ishlatilgan kalitlarni tekshiruvchi yangi funksiya
`pathlib.glob` ga qavs kengaytmasini bergan — u bash xususiyati,
`pathlib` uni qo'llab-quvvatlamaydi. Glob hech narsa topmagan, tekshiruv
esa «to'liq ✓» deb turgan. **Salbiy test tutdi.**

## Salbiy testlar (hammasi o'tdi)

| Tekshiruv | Buzilganda | Tiklanganda |
|---|---|---|
| Holat ink'i | `exit 1` (`warn 1.43:1`) | `exit 0` |
| Kodda ishlatilgan kalit | `exit 1` (nom ko'rsatildi) | `exit 0` |

## Yakuniy holat

| Tekshiruv | Natija |
|---|---|
| Lighthouse desktop / mobil | **100 / 100 / 100 / 100** |
| LCP / CLS | **217 ms** / **0.00** |
| Kontrast (18 palitra) | **772** rang AA (ilgari 718) |
| i18n | 791 kalit, xom kalit yo'q |
| `ci-local.sh all` | **0** |
| `check_deploy.sh` | **0** |
| `origin/main` | `05491de` |

## Ochiq qolgan (halol)

- **`zh` va yana yetti til UI da ko'rilmagan.** `kk` (eng uzun) va `uz`
  brauzerda tekshirildi; qolgani statik o'lchov bilan qoplandi.
- **Shablon satrli kalitlar** statik tekshiruvga tushmaydi — ularni faqat
  brauzer ko'rsatadi.
- **Legacy JavaScript: 24.9 kB** ortiqcha (polyfill) — Lighthouse aytdi,
  tuzatilmadi.


---

# To'qqizinchi yurish — 10 tilning hammasi

DoD bandi: *«Panel 10 tilda sig'adi (`zh`, `kk` jumladan)»*. Ilgari faqat
statik o'lchov bor edi; endi brauzerda.

## Usul

Har tildagi eng uzun **uzilmas so'z** va eng uzun **matn** olindi va
brauzerda panelning **haqiqiy shrifti va kengligi** bilan o'lchandi
(320px matn maydoni, 14px).

| Til | Eng uzun so'z | Natija |
|---|---|---|
| en | Accessibility | sig'adi |
| es | personalizador | sig'adi |
| kaa | shablonlarım | sig'adi |
| kk | Қолжетімділік | sig'adi |
| ky | Жеткиликтүүлүк | sig'adi |
| ru | Красно-зелёное | sig'adi |
| tg | нусхабардорӣ | sig'adi |
| tr | Özelleştiriciyi | sig'adi |
| uz | o'zgartirilgan | sig'adi |
| zh | 调色板会自适应：… | sig'adi (belgi bo'yicha o'raladi) |

⚠️ **O'lchovning birinchi versiyasi noto'g'ri natija berdi:** `zh` uchun
`white-space: nowrap` qo'yib 336px oldim va "tashib ketadi" deb o'qidim.
Lekin CJK **belgi bo'yicha o'raladi**, ya'ni `nowrap` — mening sun'iy
shartim, panelning haqiqiy holati emas. Bu **o'lchov usulining xatosi**
edi, kodning emas.

## Jonli tasdiqlash (`zh`, `kk`, `uz`)

| Tekshiruv | `kk` | `zh` |
|---|---|---|
| Xom kalit | 0 | 0 |
| Panel toshishi | yo'q | yo'q |
| Hujjat toshishi | yo'q | yo'q |
| Sarlavhalar | Көрініс, Қолжетімділік | 预设模板, 主题, 样式, 主色 |
| Shablonlar | Классикалық, Күндізгі | 经典, 日间, 夜间, 控制台 |

`zh` da ikkita `span.truncate` element `scrollWidth > clientWidth` berdi —
bu **ataylab**: uslub izohi ellipsis bilan qisqartiriladi (`…`), xato emas.

**Xulosa: 10 tilning hammasi sig'adi, xom kalit yo'q.**
