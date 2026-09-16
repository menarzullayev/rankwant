# Tarjima steki — chuqur tahlil va 10 bosqichli savol sessiyasi

**Sana:** 2026-09-14 · **Holat:** tahlil yakunlandi, qarorlar kutilmoqda
**Usul:** kod o'qish + **o'lchov** (brauzer, curl, skript). Har da'vo
yonida dalil turi ko'rsatilgan: `[o'lchandi]`, `[kod]`, `[o'lchanmagan]`.

---

## 1-qism. Stek xaritasi

| Qatlam | Fayl | Vazifa |
|---|---|---|
| Til ro'yxati | `i18n/messages.ts` | `LOCALES`, `LOCALE_NAMES`, `t()`, `fill()`, `dateTime()` |
| Lug'atlar | `i18n/locales/*.ts` (10) | `Record<MessageKey, string>` |
| Server aniqlash | `i18n/server.ts` | cookie → `Accept-Language` → standart |
| Server uzatish | `i18n/messages.server.ts` | faqat aktiv tilni tanlaydi |
| Klient konteksti | `i18n/LocaleProvider.tsx` | til + lug'atni ro'yxatga oladi |
| Tanlagich | `layout/LocaleSwitch.tsx` | `<select>` + cookie + `router.refresh()` |
| Hisobga yozish | `context/PrefsSync.tsx` | cookie ↔ `User.locale` |
| Backend | `core/models.py` (`User.Locale`) | 10 til |
| Xat matnlari | `core/email_text.py` | **3 til** |
| Django i18n | `config/settings.py` | `USE_I18N`, `LANGUAGES` (**3 til**) |
| Tekshiruv | `tools/check_i18n.py` | to'liqlik + (yangi) ishlatilish |

---

## 2-qism. Topilgan muammolar

### 🔴 A1. `registry` — global mutable yagona nusxa, jimgina kalit qaytaradi

```ts
const registry = new Map<string, Record<string, string>>();
export function t(locale, key) {
  return registry.get(locale)?.[key] ?? key;   // ← jimgina KALIT
}
```

`[kod]` `registerMessages()` render paytida yozadi; lug'at **faqat aktiv
til** uchun keladi. Ya'ni `t()` boshqa til bilan chaqirilsa yoki lug'at
hali ro'yxatga olinmagan bo'lsa — **ekranga kalit nomi chiqadi**.

Tip kafolati (`Record<MessageKey, string>`) faqat **lug'at ichida** kalit
to'liqligini ta'minlaydi, **lug'atning ro'yxatga olinganini emas**.

⚠️ **Bu aynan bugun topilgan xatoning ildizi** (`customizer.tab.appearance`
va yana 8 kalit xom holda ko'ringan edi). O'shanda men kalitlarni
qo'shish bilan tuzatdim — lekin **jimgina yutish mexanizmi joyida qoldi**.

### 🔴 A2. `registry` hech qachon kichraytirilmaydi

`[kod]` Har til almashtirishda yangi lug'at (`~40–50 kB`) `Map` ga
qo'shiladi. `router.refresh()` modulni qayta baholamaydi, ya'ni eski
lug'atlar qoladi. 10 marta almashtirsa — **~450 kB** xotirada.

### 🔴 A3. Til almashtirish to'liq server aylanishini talab qiladi

`[kod]` + `[o'lchandi]` `Cache-Control: private, no-cache, no-store`.
Ya'ni har almashtirish — butun sahifaning qayta chizilishi. Klientda
lug'at almashtirish yo'li yo'q.

### 🔴 A4. Select "orqaga sakraydi"

`[o'lchandi]` `zh` → `ru` tanlanganda:

| Payt | Select qiymati |
|---|---|
| oldin | `zh` |
| `change` dan **darhol** | **`zh`** ← qaytib ketdi |
| 250 ms keyin | `ru` |

Sabab: `value={locale}` server propidan keladi va u yangilanmaguncha eski
qiymat turadi. **Sakrash oynasi = server aylanish vaqti** — lokalda
250 ms, sekin tarmoqda bir necha soniya bo'ladi.

### 🔴 A5. Xatlar 10 tildan faqat 3 tasida

`[o'lchandi]` `core/email_text.py` da til kalitlari: `uz` 18 ta, `ru` 18
ta, `en` 18 ta. **`kaa`, `kk`, `ky`, `tg`, `tr`, `zh`, `es` — YO'Q.**

```python
return {key: values.get(locale, values[DEFAULT_LOCALE]) ...}   # jimgina uz
```

Ya'ni tilni `zh` ga qo'ygan odam **o'zbekcha xat oladi** va buni hech
qayerda ko'rmaydi.

### 🔴 A6. Backend'da til ro'yxati ikki xil va biri o'lik

`[kod]` `User.Locale` — **10 til** ✓ · `settings.LANGUAGES` — **3 til**.
`USE_I18N=True` + `LocaleMiddleware` yoqilgan, lekin `locale/` katalogi
yo'q va **birorta `gettext` chaqiruvi yo'q** → bu sozlama **hech narsa
qilmaydi** (loyihaning o'z qoidasi: jonsiz e'lon bo'lmasin).

### 🔴 A7. Bir xil URL — turli til, `Vary` siz

`[o'lchandi]` `GET /` turli `Accept-Language` bilan:

| Sarlavha | `lang` | Tugma |
|---|---|---|
| `en-US` | `lang="en"` | Sign in |
| `ru-RU` | `lang="ru"` | Войти |
| `zh-CN` | `lang="zh"` | 登录 |
| `ky-KG` | `lang="ky"` | Кирүү |

`Vary: rsc, next-router-state-tree, …, Accept-Encoding` — **`Accept-Language`
YO'Q**. Bugun zarari yo'q, chunki `no-store`; lekin **keshlash yoqilsa
bir zumda kesh-zaharlash xatosiga aylanadi**: rus foydalanuvchining
sahifasi inglizga beriladi.

### 🟠 A8. URL da til yo'q

`[kod]` Til faqat cookie'da. Natijada: havolani ulashib bo'lmaydi (oluvchi
o'z tilida ochadi), xatcho'p saqlanmaydi, `hreflang` yo'q, qidiruv tizimi
faqat bitta variantni indekslaydi.

### 🟠 A9. Uch tilda sana formati o'zbekcha

`[kod]` `intlLocale()` `kaa`/`ky`/`tg` ni ICU topmasa `uz` ga tushiradi.
Ya'ni qoraqalpoq, qirg'iz va tojik foydalanuvchisi **o'zbekcha sana
formatini** ko'radi. (Bu ataylab — jimgina `en-US` bo'lishidan yaxshi —
lekin foydalanuvchiga aytilmaydi.)

### 🟠 A10. Kontent nomlari 3 tilda

`[kod]` `topicName()` / `localName()` faqat `uz`/`ru`/`en` ustunlarini
biladi. Qolgan **7 til** mavzu va ko'nikma nomlarini **o'zbekcha** ko'radi.

### 🟠 A11. Cookie va hisob — ikki manba, qarama-qarshi qoida

`[kod]` Til uchun: `getLocale()` **cookie** ni o'qiydi; `PrefsSync` cookie
bo'lmasa hisobdan yozadi, bo'lsa hisobni cookie bilan **yangilaydi** →
**qurilma ustun**. Mavzu uchun esa **hisob ustun** (D4). Ya'ni bitta
sozlamalar tizimida ikki xil qoida.

### 🟡 A12. `check_i18n.py` bo'shlig'i (bugun yopildi)

`[kod]` Ilgari u faqat `uz.ts` da **bor** kalitlarning 10 tilda borligini
tekshirardi. **Kodda ishlatilgan** kalitlarni tekshirmasdi — shu sababli
9 kalit yetishmasligi sezilmagan. Bugun qo'shildi.
**Qolgan bo'shliq:** shablon satrli kalitlar (`customizer.template.${id}`)
statik tekshirilmaydi.

---

## 3-qism. Header'dagi til tanlagich — UI/UX bahosi

Hozirgi holat: **native `<select>`**, 10 ta `option`, endonimlar.

| # | Kamchilik | Dalil |
|---|---|---|
| B1 | **Native `<select>`** — ro'yxatni bezash mumkin emas | `appearance: auto` `[o'lchandi]` |
| B2 | **Qorong'i UI da ro'yxat OQ** — `color-scheme` yo'q | `color-scheme: normal` (qorong'i mavzuda ham) `[o'lchandi]` |
| B3 | **Orqaga sakraydi** (A4) | 250 ms `zh` ga qaytdi `[o'lchandi]` |
| B4 | **O'lchami 118×28, shrift 12px** — header'dagi boshqa tugmalar 40×40 | `[o'lchandi]` |
| B5 | **Ekran o'quvchi nomi `"Til / Language"`** — tarjima qilinmagan, `zh` foydalanuvchisiga o'zbekcha/inglizcha o'qiladi | `[o'lchandi]` |
| B6 | **Ikonka yo'q, "joriy til" belgisi yo'q** — ikonkalar qatorida forma maydoni bo'lib ko'rinadi | `[kod]` |
| B7 | **"Avtomatik" varianti yo'q** — bir marta tanlangach `Accept-Language` aniqlash **butunlay o'chadi** va qaytish yo'li yo'q | `[kod]` |
| B8 | **Yuklanish belgisi yo'q** — faqat `disabled`, u ham qisqa | `[o'lchandi]` |
| B9 | **Faqat endonim** — `中文`, `Қазақша`, `Тоҷикӣ`. Lotin o'qiydigan odam o'z tilini topa olmasligi mumkin; inglizcha nom ham, mintaqa guruhi ham yo'q | `[o'lchandi]` |
| B10 | **To'liq tarjima taassuroti** — holbuki 7 tilda xat va kontent nomlari o'zbekcha (A5, A10) | `[kod]` |
| B11 | **Tartib izohsiz** — `uz, kaa, ru, en, kk, ky, tg, tr, zh, es`: asosiy to'rtlik birinchi, lekin `en` 4-o'rinda, `zh`/`es` oxirida; alifbo ham, mintaqa ham emas | `[kod]` |
| B12 | **Kontrast yaxshi** | 6.71:1 (yorug'), 7.17:1 (qorong'i) `[o'lchandi]` — ✅ muammo emas |

---

## 4-qism. 10 bosqichli AskQuestion sessiyasi

Har bosqichda **bitta** savol. Tartib ataylab shunday: har keyingi savol
oldingisining javobiga tayanadi, ya'ni 1-bosqich javobsiz 5-bosqichni
hal qilib bo'lmaydi.

| # | Savol | Nimani hal qiladi | Tayanch |
|---|---|---|---|
| 1 | Til ro'yxati **10 ta qoladimi** yoki qisqartiriladimi? | Butun sessiyaning ko'lami | A5, A6, A10 |
| 2 | `Accept-Language` bo'yicha **avtomatik aniqlash** qoladimi? | A7 (kesh xatari) va B7 (qaytish yo'li) | A7 |
| 3 | Til **URL da** bo'ladimi (`/en/…`)? | A8 — ulashish, SEO, `hreflang` | A8 |
| 4 | Cookie va hisob to'qnashsa **qaysi biri ustun**? | A11 — mavzu bilan bir xil qoidami? | A11 |
| 5 | **Xatlar**: 7 tilni tarjima qilamizmi yoki tanlagichni 3 tilga tushiramizmi? | A5 — eng katta nomuvofiqlik | A5 |
| 6 | `t()` **jimgina kalit qaytarishi** qoladimi, yoki `uz` zaxirasi + ishlab chiqishda ogohlantirish qo'shamizmi? | A1 — xatoning ildizi | A1 |
| 7 | Til almashtirish **to'liq qayta yuklash** bo'lib qoladimi yoki klientda lug'at almashtiriladimi? | A3, A4, B3 | A3, A4 |
| 8 | Boshqaruv **native `<select>`** bo'lib qoladimi yoki o'zimizning ro'yxatmi? | B1, B2, B4 | B1, B2 |
| 9 | Ro'yxat **mazmuni**: endonim yolg'izmi, +inglizcha nom, mintaqa guruhi, qidiruv? "Avtomatik" varianti? | B7, B9, B11 | B7, B9 |
| 10 | **Qisman tarjima** foydalanuvchiga aytiladimi (xat/kontent qamrovi)? | B10, A9, A10 | B10 |

### Nega bu tartib

- **1–2** — ko'lam. Ro'yxat qisqarsa, 5/9/10 savollari o'zgaradi.
- **3–4** — arxitektura. URL sxemasi va ustunlik qoidasi keyingi hamma
  narsaga ta'sir qiladi (SEO, kesh, hisob sinxroni).
- **5–6** — backend va asosiy kutubxona. Ikkalasi ham ma'lumot
  yo'qotishiga olib keladigan jimgina zaxiralar haqida.
- **7–8** — frontend arxitekturasi va boshqaruv turi.
- **9–10** — sof UI/UX va halollik.

---

## Ilova. O'lchanmagan, lekin tekshirilishi kerak

- `[o'lchanmagan]` Xatlar haqiqatan o'zbekcha keladimi — `zh` hisob bilan
  sinab ko'rilmagan (kod shuni ko'rsatadi).
- `[o'lchanmagan]` `registry` xotirasi amalda qancha o'sadi — 10 marta
  til almashtirib o'lchash kerak.
- `[o'lchanmagan]` Native select popup'i qorong'i mavzuda haqiqatan oq
  chiqadimi — `color-scheme: normal` shuni ko'rsatadi, lekin popup
  skrinshoti olinmagan (native popup DOM emas).


---

## 5-qism. Sessiya qarorlari (10/10 bajarildi)

| # | Savol | Qaror | Tavsiyaga mos? |
|---|---|---|---|
| 1 | Til ro'yxati | **10 til qoladi + to'liq tarjima** | ✅ |
| 2 | Avto-aniqlash | **Qoladi + `Vary` + «Avtomatik» varianti** | ✅ |
| 3 | URL sxemasi | **Prefiks kerak — lekin oxirgi navbatda, standart til prefikssiz** | tavsiya asosida (alohida tasdiq yo'q) |
| 4 | Ustunlik | **Qurilma ustun + qoida ataylab chetlanish sifatida yoziladi** | ✅ |
| 5 | Xatlar | **7 til qo'shiladi, tranzaksion birinchi, zaxira o'lchanadigan** | ✅ |
| 6 | `t()` zaxirasi | **Dev yiqiladi, prod jurnalga; `uz` zaxirasi yo'q** | ✅ |
| 7 | Almashtirish | **Optimistik qiymat + kutish belgisi; arxitektura tegmaydi** | ✅ |
| 8 | Boshqaruv | **Custom ro'yxat (listbox)** | ❌ tavsiyadan chetlanish |
| 9 | Ro'yxat mazmuni | **Endonim + inglizcha, guruhli, «Avtomatik» birinchi, qidiruvsiz** | ✅ |
| 10 | Qamrov | **Zaxira ishlatish joyida belgilanadi** | ✅ |

### 8-bosqich chetlanishining majburiyatlari

Custom listbox tanlangani uchun **native bepul bergan narsa endi qo'lda
yoziladi**. Bularsiz 8-qaror regressiya bo'ladi:

- `role="listbox"` / `role="option"` / `aria-selected` / `aria-expanded`
- Klaviatura: `↑` `↓` `Home` `End` `Enter` `Space` `Esc`, fokus halqasi
- **Type-ahead** (harf bosilsa mos variantga sakrash)
- Fokus yopilganda **ochgan tugmaga qaytishi**
- Tashqariga bosish / `Esc` bilan yopilish
- **Mobil OS tanlagichi yo'qoladi** → alohida touch-sheet kerak
- Yopiq holatda joriy til ekran o'quvchiga **e'lon qilinishi**

### Ish tartibi (qarorlardan kelib chiqadi)

| Navbat | Ish | Nega shu navbatda |
|---|---|---|
| 1 | `t()` dev/prod rejimi (6) | Eng arzon, ildiz sabab |
| 2 | Optimistik qiymat (7) | Arzon, ko'rinadigan bug |
| 3 | Xatlar: tranzaksion 7 til (5) | Foydalanuvchi oqimini to'sadi |
| 4 | `color-scheme` + o'lcham (8) | Bir qatorlik, ko'rinadigan nuqson |
| 5 | Custom listbox (8, 9) | Qimmat — a11y majburiyatlari bilan |
| 6 | Zaxira belgisi (10) | 5 dan keyin mantiqiy |
| 7 | Xatlar: qolgan 7 til (5) | Tranzaksiondan keyin |
| 8 | Ustunlik qoidasini yozish (4) | Hujjat ishi |
| 9 | `Vary` + «Avtomatik» (2) | Kesh xatari — kesh yoqilgunga qadar xavfsiz |
| 10 | URL prefiksi (3) | Eng qimmat, eng katta o'zgarish |
