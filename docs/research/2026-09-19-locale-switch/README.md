# Til tanlash bo'limi — tahlil, baho va tanlov nuqtalari

> **Arxiv yozuvi.** Repoga 2026-10-04 da ko'chirildi; matn yozilgan kunidagi holatni aks ettiradi. Amaldagi qarorlar `CLAUDE.md` jadvalida.

**Sana:** 2026-09-19 · **Manba:** jonli prod stek (`:8300`), konteyner `7121012` = HEAD
**Usul:** hamma raqam o'lchandi (brauzer DOM + tarmoq + server javoblari + kod). Taxmin yo'q.
**Oldingi hujjat:** `rankwant/docs/research/2026-09-14-rankwant-theme-customizer-design/I18N-STACK-ANALYSIS.md`
(10 qaror o'sha yerda qabul qilingan; bu hujjat ularning **natijasini** baholaydi)

---

## 0. Qisqa javob

1. **10 ta qaror bajarilgan va ishlaydi** — 10 til, **1599 kalit**, 0 yetishmaydi, 0 bo'sh;
   xatlar ham 10 tilda to'liq. Til aniqlash, guruhli ro'yxat, klaviatura, ekran o'quvchi —
   hammasi o'lchandi va to'g'ri.
2. **P1 xato topildi, tuzatildi va `main` ga birlashtirildi** (PR **#104** → `7fd8b05`,
   2026-09-19): tilni almashtirib, keyin **qaytib** o'sha tilga o'tilsa brauzerdagi lug'at
   yo'qolardi va sahifa **38 ta xom kalit** ko'rsatardi (`nav.problems`, `locale.switchLabel`,
   …). Sabab aniqlandi, haqiqiy sichqoncha va klaviatura bilan qayta ishlandi; tuzatish **A**
   varianti bo'yicha qilindi va **qoida + salbiy test + drift qo'riqchisi** bilan
   mustahkamlandi — batafsil §2.6.
3. **Almashtirish tezligi:** ekranda darhol (16 ms), lekin to'liq qo'llanishi
   Slow 4G da **1.63 s** (yangi til) / **0.91 s** (keshdagi til). Lug'at **oldindan
   yuklanmaydi** — har yangi til ~70–102 KB yuklaydi.
4. **10-qaror bajarildi** (HITL qarori T3-a + T3-c, 2026-09-19). O'lchov paytida belgi
   **8 joydan faqat 2 tasida** chizilardi. Endi hamma joyda chiziladi va sharti **bitta
   joyda** (`ContentName`); ustiga **teskari nuqson** ham topildi va tuzatildi — `nameInfo`
   `uz` ni ham qaytish deb hisoblagani uchun **o'zbekcha sahifaning o'zida ham `uz` belgisi**
   chiqardi. Tanlash ro'yxati endi qamrovni **tanlashdan oldin** aytadi. Batafsil §3/T3.
5. **Qolgan eng katta imkoniyat:** til URL da yo'q (`/en/…`) — havola ulashib bo'lmaydi,
   `hreflang` yo'q, SEO yo'q. Bu 3-qaror bo'yicha "oxirgi navbat" edi; navbat amalda tugadi.

---

## 1. Hozirgi holat — o'lchangan

| Nima | Holat | Dalil |
|---|---|---|
| Tillar soni | 10 (`uz, kaa, ru, en, kk, ky, tg, tr, zh, es`) | `messages.ts` `LOCALES` |
| UI kalitlari | **1599 × 10** — yetishmaydigan 0, bo'sh 0 | `tools/check_i18n.py` ✓ (o'lchov paytida 1595 edi; `#103` 4 ta qo'shdi) |
| Manba bilan bir xil satrlar | `kaa` 135, `en` 65, `tr` 49, `es` 40, `zh` 27, `kk/ky/tg` 25, `ru` 24 | qardosh so'z + brend (`Reyting`, `Balans`, `Qvant`) — **nuqson emas** |
| Xat matnlari | **18 satr × 10 til — to'liq** | `tools/check_email_locales.py` ✓ |
| Parite tekshiruvi | `10 til × 3 ro'yxat — mos ✓` | `tools/check_locales_parity.py` ✓ |
| Til aniqlash | `ru-RU`→`ru`, `zh-CN`→`zh`, `de-DE`→`uz` | jonli `Accept-Language` sinovi |
| `q=` koeffitsienti | hisobga olinadi, `*` tashlanadi | `server.ts:32` |
| Ustunlik | cookie (tanlov) → `Accept-Language` → standart | `server.ts:74` |
| «Avtomatik» | birinchi variant, aniqlangan til qavsda: `Automatic · English` | o'lchandi |
| Guruhli ro'yxat | 3 guruh, `role="group"` + tarjima qilingan `aria-label` | a11y daraxti: «Основные», «Региональные», «Широкий охват» |
| Klaviatura | `↑ ↓ Home End Enter Space Esc Tab` + 700 ms type-ahead + fokus qaytishi | kod + qo'lda sinov |
| `aria-label` | ko'rinadigan matnni o'z ichiga oladi (WCAG 2.5.3) | `Русский — Russian (ru) — Выберите язык` |
| Tor ekran (320px) | tugma **75px**, toshish **0**, kod ko'rinadi (`ru`) | qurilma emulyatsiyasi |
| Keng ekran | tugma **165px**, to'liq nom | o'lchandi |
| Lug'at fayli | alohida, `immutable`, 1 yil kesh; 70–102 KB | `cache-control: public, max-age=31536000` |
| Barcha lug'atlar | **849 652 B (~830 KB)** | 10 ta fayl yig'indisi |
| Sahifa HTML | 65 546–67 124 B (tilga qarab deyarli bir xil) | o'lchandi |
| `Vary: Accept-Language` | **yo'q** — Next.js 16 o'chirib tashlaydi | `proxy.ts:59` + jonli javob sarlavhalari |
| Kesh xavfi | hozir yo'q: `Cache-Control: private, no-cache, no-store` | o'lchandi |

**Xulosa:** tanlagichning o'zi (UI, a11y, guruhlar, optimistik qiymat) — yaxshi holatda.
Muammolar **atrofida**: lug'at yuklanishi, zaxira shaffofligi, URL va kesh.

---

## 2. P1 xato (✅ tuzatildi — `7fd8b05`) — til almashtirib qaytganda lug'at yo'qoladi

### 2.1. Nima bo'ladi

Foydalanuvchi tilni almashtiradi, keyin **o'sha tilga qaytadi** — sahifa xom kalitlarga to'ladi.

Haqiqiy kiritish (sichqoncha bosishi + klaviatura `↑`/`Enter`) bilan qayta ishlandi:

| Qadam | Til | Registr | Xom kalit | Tugma yozuvi |
|---|---|---|---|---|
| Sahifa yuklandi | `ru` | `[ru]` | 0 | `Русский — Russian` |
| → `中文` (birinchi tashrif) | `zh` | `[zh]` | **0** ✅ | `中文 — Chinese` |
| → `Español` (birinchi tashrif) | `es` | `[es]` | **0** ✅ | `Español — Spanish` |
| → **qaytib** `中文` | `zh` | **`[]`** | **23** ❌ | `中文 — Chinese` |

Konsol (prod kodining o'z yozuvi):

```
i18n: dictionary for locale "zh" is not registered — rendering the key instead   [38 marta]
```

Ekranda ko'ringan xom kalitlar: `nav.skipToContent`, `nav.problems`, `nav.attempts`,
`nav.quizzes`, `nav.articles`, `nav.roadmap`, `nav.algorithms`, `nav.classroom`,
`nav.contests`, `nav.arena`, … (23 xil matnda, 38 xil kalit jurnalda).
`aria-label` ham buziladi: `中文 — Chinese (zh) — locale.switchLabel` — ekran o'quvchi
ham xom kalitni o'qiydi.

**Qoida:** *birinchi* tashrif ishlaydi; **qaytish har doim buziladi**.
Sahifa yangilanmaguncha (F5) o'zi tiklanmaydi — 3 daqiqadan keyin ham tekshirildi.

### 2.2. Sabab zanjiri (kod)

Ikki modul bir-biriga zid faraz qiladi:

1. `LocaleProvider.tsx:63` — `useEffect(() => evictOtherLocales(locale), [locale])`
   → til o'zgarganda **boshqa barcha lug'atlar registrdan o'chiriladi**.
2. `LocaleProvider.tsx:15–36` — `loading` Map **URL bo'yicha va'da (promise)** saqlaydi
   va uni **hech qachon tozalamaydi**.

Qaytishda:

```
hasMessages("zh")            → false          (1-qadam o'chirgan)
loadDictionary("zh", url)    → loading'da bor → ALLAQACHON HAL QILINGAN va'da
                             → <script> QAYTA KIRITILMAYDI
                             → registr bo'sh qoladi → t() xom kalit qaytaradi
```

Ya'ni **eviction "qayta yuklash mumkin" deb faraz qiladi, kesh esa "bir marta yuklanadi"
deb faraz qiladi.** Ikkisi birga ishlamaydi.

### 2.3. Nega hech bir tekshiruv tutmadi

| Tekshiruv | Nega o'tkazib yubordi |
|---|---|
| `tsc` | tip to'g'ri — bu ish vaqti holati, tip xatosi emas |
| `eslint` (`rules-of-hooks`) | shartli `use()` ni **tutmadi** — `LocaleProvider.tsx:60–62` da `use()` `if` ichida; ESLint 0 xato berdi |
| `check_i18n.py` | kalitlarning **mavjudligini** tekshiradi, **yuklanishini** emas |
| `check_locales_parity.py` | fayllar paritetini tekshiradi, brauzer registrini emas |
| qo'lda sinov | bir marta almashtirib qo'yiladi — **qaytish** sinalmaydi |

**Sabab:** tekshiruvlarning hammasi statik yoki bir yo'nalishli. Bu xato faqat
**ketma-ketlikda** (A→B→A) paydo bo'ladi.

### 2.4. Qo'shimcha kuzatuv

Bir marta (avvalgi sinovda) konsolda React xatosi ham chiqdi:

```
Uncaught Error: Minified React error #467
→ to'liq matni: "Update hook called on initial render. This is likely a bug in React."
```

Toza takrorlashda **chiqmadi**, ya'ni barqaror emas. Eng ehtimoliy sabab — `LocaleProvider.tsx:60–62`
dagi **shartli `use()`**: `hasMessages` o'zgarganda hook chaqiruvlari soni o'zgaradi, bu
React qoidalarini buzadi. **Bu faraz, isbotlangan emas** — dev build'da tekshirish kerak.
Alohida qayd: ESLint bu buzilishni tutmaydi, ya'ni unga alohida salbiy test kerak.

### 2.5. Tuzatish variantlari

| # | Variant | Afzalligi | Kamchiligi | Xavf |
|---|---|---|---|---|
| **A** | `loading` keshini eviction bilan **sinxronlash** — evict qilinganda o'sha tilning va'dasi ham o'chiriladi | Ildiz sababni yopadi; xotira chegaralangan qoladi; o'zgarish kichik | Ikki modul orasidagi bog'lanish oshkor bo'ladi (import yo'nalishi) | Past |
| **B** | `evictOtherLocales` ni **butunlay olib tashlash** | Eng oddiy; kesh va eviction ziddiyati yo'qoladi | Xotira o'sadi: har tashrif ~70–102 KB; 10 til = **~830 KB** | Past, lekin mobil uchun xotira |
| **C** | **Barcha 10 lug'atni oldindan yuklash**, shartli `use()` ni olib tashlash | Aqliy model eng sodda; `use()` shartli bo'lmaydi (#467 ham yopiladi) | Har tashrifda **~830 KB** yuklanadi — Slow 4G da qabul qilib bo'lmaydi | O'rta |
| **D** | Har chizishda registrni tekshirib **qayta kiritish** (himoya qatlami) | Har qanday kelajakdagi eviction xatosini ham yopadi | Ildizni tuzatmaydi; "davolash" emas, "niqoblash" | Past |

**CTO tavsiyasi: A.** Sabab: xato aynan ikki farazning ziddiyatidan kelib chiqqan, ya'ni
**aynan shu ziddiyatni** yo'q qilish kerak. A — eng kichik to'g'ri o'zgarish, xotira
chegarasi saqlanadi (mobil uchun muhim: 830 KB emas, bitta lug'at) va C kabi
tarmoq narxini oshirmaydi. **D ni A ustiga qo'shimcha qilib qo'yish** tavsiya etiladi —
arzon himoya qatlami sifatida, lekin **A o'rniga emas**.

**Majburiy:** tuzatishdan keyin `tools/check_negative.py` ga **salbiy test** qo'shiladi
(A→B→A ketma-ketligi), aks holda qoida "o'lchanmagan" hisoblanadi.

### 2.6. Holat — tuzatildi va birlashtirildi

**A varianti** amalga oshirildi (Saidakbar aka tanlovi, 2026-09-19).

| Nima | Natija |
|---|---|
| Kod | `LocaleProvider.tsx` — `keepOnly(keep)` **ikkala** keshni birga tozalaydi; va'da keshi til bo'yicha kalitlangan; registrga hech narsa yozmagan lug'at bir marta yangi manzil bilan qayta so'raladi |
| A/B (haqiqiy brauzer) | **eski kod:** `en → zh → es → zh` → registr `[]`, sahifa yiqildi. **yangi kod:** `zh → ru → zh → ru → zh`, so'ng `ru → zh → es → zh → en` → registr har doim joriy til, xom kalit **0**, konsolda xato yo'q |
| Qoida | `check_decisions.py` → `dictionary_survives_return` (`lug'at qaytishda saqlanadi`) |
| Salbiy test | `check_negative.py` → `neg_decisions_dictionary_cache_unsynced` — qo'lda sinaldi: buzilgan holatda `exit 1` + qoida nomi |
| CI | salbiy testlar **182/182 ✓**, `check_decisions.py` `✓ 22 ta qaror`, lint + typecheck `exit=0` |
| Merge | PR **#104** squash → `7fd8b05` (`main`, 2026-09-19) |

**Qo'shimcha saboq (CI nosozligi):** yangi qoida `check_decisions.py` ga **yangi fayl**
o'qitdi, salbiy test sandbox'i esa uni nusxalamadi → **aloqasi yo'q ikki** trial-label testi
`exit 2` berdi (`Qarorlarni o'qib bo'lmadi`). Sandbox ro'yxati skriptdagi yo'llarning qo'lda
nusxasi edi, ya'ni **drift manbai**. Tuzatildi va ustiga qo'riqchi qo'shildi:
`neg_decisions_sandbox_covers_reads` — `check_decisions.py` ning o'z kodidan `read(...)`
yo'llarini o'qib, qamralmaganini **lokalda fayl nomi bilan** aytadi.

**Qolgan:** **D** varianti (himoya qatlami) ataylab qo'shilmadi — A ildizni yopadi, D esa
ildizni tuzatmaydi. #467 farazi hamon **isbotlanmagan** (§2.4); shartli `use()` ga tegilmadi
(qamrovdan tashqari).

---

## 3. Takliflar — variantlar, afzallik/kamchilik, UX ta'siri

### T1. Almashtirish tezligi: lug'atni oldindan yuklash

**O'lchandi (Slow 4G, jonli stek):**

| Holat | Ekranda | To'liq qo'llanishi | Tarmoq |
|---|---|---|---|
| Yangi til (masalan `zh`) | 16 ms | **1630 ms** | lug'at 70 785 B + RSC 7 973 B |
| Keshdagi til (masalan `ru`) | 16 ms | **911 ms** | faqat RSC 8 143 B |
| Localhost | 15 ms | 47 ms | — |

Ya'ni **birinchi almashtirish ~0.7 s ni faqat lug'at yuklashga sarflaydi.**
Hozir lug'at faqat **tanlangandan keyin** so'raladi — oldindan yuklash yo'q.

| # | Variant | Afzalligi | Kamchiligi | UX ta'siri |
|---|---|---|---|---|
| T1-a | `IntentLink` naqshidek **hover/fokusda** lug'atni oldindan yuklash | Ro'yxatni ochgan odam uchun almashtirish ~0.9 s ga tushadi; qo'shimcha kod kam; mavjud naqsh bor | Foydalanuvchi ro'yxatni ochib tanlamasa — behuda trafik (~70 KB) | O'rta-yuqori: "sekin" degan taassurot yo'qoladi |
| T1-b | Ro'yxat **ochilganda** barcha 10 lug'atni yuklash | Har qanday tanlov darhol | **~830 KB** — mobil uchun og'ir | Yuqori, lekin trafik narxi katta |
| T1-c | Faqat **eng ko'p tanlanadigan 3 tilni** oldindan yuklash | Arzon, ta'siri katta | "qaysi 3 tasi" — taxmin; boshqalari sekin qoladi | O'rta |
| T1-d | Hech narsa qilmaslik | 0 xarajat | Har yangi til 0.7 s kutadi | — |

**CTO tavsiyasi: T1-a.** Sabab: naqsh loyihada allaqachon bor (`IntentLink.tsx` —
hover/fokus/touch da oldindan yuklash), ya'ni yangi arxitektura o'ylab topilmaydi.
"Befuda trafik" xavfi kichik: ro'yxatni ochgan odam deyarli har doim tanlaydi.

**✅ Qaror (S3, 2026-09-19): Saidakbar aka T1-d ni tanladi — hech narsa qilmaymiz.**
Ya'ni CTO tavsiyasi (T1-a) **qabul qilinmadi**: prefetch qo'shilmaydi, kod o'zgarmaydi,
~0.7 s kutish qabul qilinadi. Kelajakda kimdir (yoki agent) o'z tashabbusi bilan
prefetch qo'shmasligi kerak — bu **ataylab rad etilgan** taklif. Agar qaytarilsa, yangi
HITL savoli bilan.

---

### T2. Tor ekranda ko'rsatish

**O'lchandi (320px, qurilma emulyatsiyasi):** tugma **75px**, toshish **0**, kod ko'rinadi
(`ru`). Keng ekranda to'liq nom, tugma **165px**. Kod **kichik harfda** — `KAA` 3px toshardi.

**🆕 Qo'shimcha o'lchov (`6486cd6` — `#105` + `#106` birlashtirilgandan keyin, `zh` lug'ati):**
`#105` bayroqni nom oldiga qo'ydi va shu bilan **eski nuqsonni ko'rinadigan qildi**.

**320×800×2 (qurilma emulyatsiyasi):**

| Ko'rsatkich | Qiymat |
|---|---|
| Panel (listbox) | `left = -44`, `right = 212`, `width = 256` (`w-64` + `right-0`) |
| Chapga toshish | **44 px** ✗ |
| O'ngga toshish / sahifa toshishi | **0 px** ✓ / **0 px** ✓ |
| **Barcha 11 variantning bayrog'i** (`<svg>`) | `left = -32 … right = -11` — **hammasi** ekrandan tashqarida ✗ |
| Nom qirqilishi (`truncate`) | **0 ta** — `Qaraqalpaqsha` chip bilan ham sig'adi (`scrollWidth = clientWidth = 147`) |
| Qamrov chipi (`名称 uz`) | `left = 152 … right = 200` — to'liq ko'rinadi ✓ |
| Trigger tugmasi | faqat **bayroq + `zh`** (to'liq nom `hidden … sm:block`, 273-satr) |
| Konteyner | `overflow-x: visible` |

**Chegara o'lchandi:** 360×800×2 da `left = -4` (toshish 4 px, bayroq `left = 8` — **ko'rinadi**).
Model: `panel.left = trigger.right − 256`, `flag.left = panel.left + 12`. Ya'ni bayroq
`panel.left ≥ −12` bo'lganda ko'rinadi → **~352 px dan pastda barcha bayroqlar yo'qoladi**.
Sabab: trigger'ning o'ng cheti 320px da atigi `212`, panel esa undan **256px chapga** osiladi.

Geometriya **o'zgarmagan** — `#105` dan oldingi o'lchovda ham aynan `left = -44` edi. Ya'ni
nuqson **eski**, lekin `#105` bayroqni chap chetga surgani uchun endi **ko'rinadi**.
Bu `#106` doirasidan **tashqarida** (PR tavsifida shunday qayd etilgan) — tuzatish shu
bo'limning (T2 / S4) qarori.

**Muhim:** `#105` T2-b ni **allaqachon yetkazgan** — panelda endonim ko'rsatiladi
(`Qaraqalpaqsha`, `中文`, `Русский`) va hech biri qirqilmaydi. Ya'ni S4 ning «nima
ko'rsatamiz» qismi amalda hal bo'lgan; **ochiq qolgan yagona savol — geometriya** (chapga
44 px toshish) va **trigger'ning tor ekranda kod ko'rsatishi** (`zh`, endonim emas).

Muammo: xitoylik foydalanuvchi tor ekranda **`zh`** ko'radi, `中文` emas. Kod — ishora,
lekin o'z tili emas.

| # | Variant | Afzalligi | Kamchiligi | UX ta'siri |
|---|---|---|---|---|
| T2-a | Hozirgi: til **kodi** | 0 toshish; o'lchangan | `zh`, `kaa` — tanilmasligi mumkin | Past (ro'yxat ochilganda to'liq nom ko'rinadi) |
| T2-b | **Endonim** (`中文`, `Русский`) | O'z tili — eng tabiiy | `Qaraqalpaqsha` uzun → toshish xavfi (o'lchanmagan) | O'rta-yuqori |
| T2-c | **Bayroq** + kod | Tez tanib olish | Bayroq ≠ til (`ru` — bir necha davlat); `kaa`/`tg` uchun noaniq | O'rta, chalkashlik xavfi |
| T2-d | Faqat **globus** ikonkasi | Eng toza; 0 toshish | "qaysi tildaman" yo'qoladi — eng ko'p so'raladigan savol (9-qaror) | Past |

Eslatma: `country-flag-icons` loyihada **bor** (`components/ui/CountryFlag.tsx`, lazy import) —
T2-c texnik jihatdan tayyor. Lekin til ≠ davlat, shu sababli ehtiyot kerak.

**CTO tavsiyasi: T2-b, o'lchov sharti bilan.** Sabab: kod (`zh`) foydalanuvchining o'z
tilida emas, endonim esa aynan o'z tili — ya'ni "qaysi tildaman" savoliga to'g'ri javob.
Lekin **avval eng uzun endonim** (`Qaraqalpaqsha`) 320px da o'lchanishi shart; toshsa —
`max-w` + `truncate` yoki T2-a ga qaytish.

**🆕 Qo'shimcha shart (o'lchovdan kelib chiqdi):** T2-b ni tanlash **panel geometriyasini
tuzatishni ham o'z ichiga olishi kerak** — aks holda yangi (uzunroq) endonimlar aynan
ko'rinmaydigan chap chetda turadi. Uch yo'l bor, biri tanlanishi kerak:

| Yo'l | Nima qiladi | Xavfi |
|---|---|---|
| Panelni o'ngga surish (`right-0`) | Chap toshish 0 bo'ladi | Tor ekranda tugmadan uzoqlashadi |
| Panelni toraytirish (`max-w`) | 256px dan kichik | Uzun endonim qirqiladi → `truncate` kerak |
| Tor ekranda **to'liq kenglik** | Eng qulay, mobil-naqsh | Keng ekran dizaynidan farq qiladi |

### T2 — holat: bajarildi (2026-09-19, HITL S4, PR #107)

Saidakbar aka **«Geometriya + endonim trigger»** ni tanladi. Amalga oshirishda yana bir
o'lchov shart bo'ldi: kodning o'zida (101–112-satr) 2026-09-18 dagi o'lchov yozilgan —
to'liq nom bilan tugma 165 px bo'lib header **15/59 px** toshgan, shuning uchun tor ekranda
**kod** ko'rsatilgan edi. Ya'ni endonimni qaytarishdan oldin **qayta o'lchash** kerak edi.

**Cheklovsiz endonim (320 px) — yana toshadi:**

| Endonim | Tugma | Header toshishi |
|---|---|---|
| `中文` | 82 px | 0 ✓ |
| `Русский` · `English` · `Тоҷикӣ` · `Español` · `Қазақша` | 104–116 px | 0 ✓ |
| `Кыргызча` | 123 px | **+6 px** ✗ |
| `O'zbekcha` | 124 px | **+7 px** ✗ |
| `Qaraqalpaqsha` | 149 px | **+29 px** ✗ |

Header'da bo'sh joy **yo'q**: o'ng guruh `min-w-0` bilan allaqachon siqilgan
(320 px da 223 px). **48 px** chegarada barcha o'nta endonim ≤ **117 px**, toshish **0**,
**7 tasi to'liq** ko'rinadi.

| Nima | O'lchov / natija |
|---|---|
| Trigger | endonim **har kenglikda**; `max-w-[3rem] truncate` + `sm:max-w-[7.5rem]`. Kod faqat `aria-label` da (WCAG 2.5.3 saqlanadi — DOM matni to'liq, `truncate` faqat vizual) |
| Panel sharti | **ekran kengligiga emas, haqiqiy joylashuvga**: `rect.right < PANEL_W + PANEL_GAP` (264 px). Sabab: nuqson `w-64` (256 px) trigger chetidan sig'maganda yuzaga keladi, aniq 320 px da emas |
| Panel xatti-harakati | tor: `fixed` + ochilishda o'lchangan `top`, chap/o'ngdan 8 px; keng: hozirgidek `absolute right-0 w-64`. Oyna o'lchami o'zgarsa panel **yopiladi** (koordinata eskirishi mumkin) |
| Qayta o'lchov 320×800×2 | `fixed`, `left 8 / right 312`, `w 304`, toshish **0**, bayroqlar **11/11**, qirqilgan nom **0** |
| Qayta o'lchov 360×800×2 | `fixed`, `left 8 / right 352`, `w 344`, toshish **0**, bayroqlar **11/11** |
| Qayta o'lchov 1280×900 | `absolute`, inline style **yo'q**, `right = trigger.right` — **o'zgarmagan** |
| Qo'riqchi | `mobile_header_fits_narrow_screen` **qayta yozildi** (yorliq: `tor ekran 320 px ga sig'adi`) + 3 yangi salbiy test; `✓ 23 ta qaror`, salbiy to'plam **190/190 ✓** |
| Registr | `CLAUDE.md` 46-qatori ikkala o'lchov bilan yangilandi (eski tanlov sababi saqlanib) |

⚠️ **Muhim:** bu qaror **2026-09-18 dagi tanlovni qaytaradi** — endi tor ekranda ham kod
emas, endonim ko'rsatiladi. Kelajakda «kod qaytarish» qo'riqchi tomonidan **tutladi**
(salbiy test: `neg_decisions_locale_code_restored`).

---

### T3. Qamrov shaffofligi — 10-qaror tugallanishi

**O'lchandi:** zaxira (fallback) **8 joyda** ishlaydi, lekin belgi **2 joyda** ko'rsatiladi:

| Fayl | Zaxira ishlaydi | `uz` belgisi |
|---|---|---|
| `components/profile/AboutTab.tsx` | ✅ | ✅ |
| `components/profile/TopicStrength.tsx` | ✅ | ✅ |
| `app/problems/page.tsx` | ✅ | ❌ |
| `components/ArchiveSidebar.tsx` | ✅ | ❌ |
| `components/profile/ActivityTabs.tsx` | ✅ | ❌ |
| `components/settings/SkillsSection.tsx` | ✅ | ❌ |

Jonli tasdiq: `zh` sahifasida «Boshlang'ich yo'l» va «Tezlik — sessiya serverda o'qiladi»
o'zbekcha ko'rinadi — **hech qanday belgisiz**. Ya'ni 10-qaror ("zaxira ishlatish joyida
belgilanadi") amalda **25% bajarilgan**.

| # | Variant | Afzalligi | Kamchiligi | UX ta'siri |
|---|---|---|---|---|
| T3-a | Qolgan **6 joyga ham** `uz` belgisini qo'yish | Qaror to'liq bajariladi; izchil | 6 ta joyni tahrirlash; ba'zi joyda dizayn tor | Yuqori — halollik tiklanadi |
| T3-b | Belgi **faqat birinchi uchragan joyda**, keyin takrorlanmaydi | Vizual shovqin kam | "nega bu yerda bor, u yerda yo'q" — tushunarsiz | O'rta |
| T3-c | Tanlash **ro'yxatida** ko'rsatish: `中文 — Chinese · kontent uz` | Odam tanlashdan **oldin** biladi | Ro'yxat matni uzayadi (tor ekranda muammo) | O'rta-yuqori |
| T3-d | Almashtirilgandan keyin **bir martalik xabar** | Ko'rinadigan, bir marta | Yo'qoladi; keyin yana adashtiradi | O'rta |
| T3-e | Hech narsa (hozirgi holat) | 0 ish | Foydalanuvchi o'zbekchani tarjima deb o'ylaydi | Salbiy |

**CTO tavsiyasi: T3-a + T3-c birga.** Sabab: T3-a — qabul qilingan qarorning
bajarilmagan qismi, ya'ni "yaxshilanish" emas, **qarz**. T3-c esa uni eng arzon joyda —
tanlov paytida — oldini oladi. T3-d yolg'iz yetarli emas: xabar yo'qoladi, belgi qoladi.

### T3 — holat: bajarildi (2026-09-19, HITL)

Saidakbar aka **T3-a + T3-c** ni tanladi. Amalga oshirishda **teskari nuqson** ham topildi.

| Nima | O'lchov / natija |
|---|---|
| Teskari nuqson (yangi) | `nameInfo` `uz` uchun ham `locale: null` qaytarardi, ya'ni **o'zbekcha sahifada ham `uz` chipi** chiqardi. Unit test buni tutdi: `localNameInfo(skill, "uz").locale` → `null` (`expected null to be 'uz'`) |
| Qamrov manbai | `CONTENT_NAME_LOCALES = ["uz", "ru", "en"]` + `hasContentNames()` — qaysi til qaytish berishi **bitta joydan** olinadi |
| Belgi sharti | `ContentName` (JSX) va `contentNameText` (native `<option>`) — shart sakkizta chaqiruv joyida takrorlanmaydi |
| T3-c o'lchovi (jonli, 320×800×2, `zh`) | 11 variant: **7 belgili** (kaa, kk, ky, tg, tr, zh, es), **4 belgisiz** (avtomatik, uz, ru, en) — aynan qamrovsiz yettisi. Ro'yxat toshishi **0 px**, sahifa toshishi **0 px** |
| Til matni | Yangi kalit `locale.contentUz` 10 tilga qo'shildi; uzun izoh uchun mavjud `content.uzOnly` ishlatiladi (qattiq yozilgan matn **0**) |
| Qo'riqchi | `check_decisions.py` → `content_coverage_visible` (`✓ 23 ta qaror`) + **7 salbiy test**; salbiy to'plam **189/189 ✓** |
| Tarjimon varaqlari | `--prefix ""` bilan qayta yaratildi (1600 kalit); `check_i18n.py` ✓ 10 × 1600 |
| Boshqa darvozalar | vitest **69/69 ✓**, lint + typecheck `exit=0`, `check_hardcoded` ✓, `check_contrast` ✓ 772 rang, `next build --webpack` ✓ |
| **Birlashtirildi** | **PR #106 → `main` = `6486cd6`** (2026-09-18T22:43:22Z, 28 fayl, +412/−43). `#105` bilan to'qnashuv `LocaleSwitch.tsx` da rebase orqali hal qilindi — ikkala o'zgarish saqlandi |
| Merge'dan keyingi qayta tekshiruv | `✓ 23 ta qaror kodda amalda`; `check_i18n` **10 × 1600 + 26 shablon oila** ✓; `check_hardcoded` **291 manba + 111 klient fayl** ✓; `main` CI + Security ✓ |

**O'lchanmagan:** belgining o'zi (chip) ma'lumotli sahifada ko'z bilan tasdiqlanmadi — dev
serverda API yo'q (`/problems` → server xatosi), jonli stekda esa mavzu ro'yxati bo'sh.
Shartni **unit test** qotiradi (`locale === null`), ya'ni chip shundan kelib chiqadi.

---

### T4. Ro'yxatda qidiruv maydoni

Hozir 11 variant (1 «Avtomatik» + 10 til) — qidiruvsiz ham boshqariladi, guruhlar yordam beradi.

| # | Variant | Afzalligi | Kamchiligi | UX ta'siri |
|---|---|---|---|---|
| T4-a | Qidiruv **yo'q** (hozirgi) | Sodda; 11 variant uchun yetarli | Til soni oshsa ishlamaydi | Hozir: yetarli |
| T4-b | Type-ahead **kengaytirish** (hozir bor, 700 ms) | Allaqachon ishlaydi; 0 UI qo'shiladi | Faqat klaviaturada; mobil uchun emas | O'rta |
| T4-c | **Ko'rinadigan** qidiruv maydoni | 30+ tilga tayyor; mobil uchun ham | 11 variant uchun ortiqcha; a11y ishi qo'shiladi | Hozir: past |

**CTO tavsiyasi: T4-a (hozircha).** Sabab: 11 variantda qidiruv — ortiqcha murakkablik.
Type-ahead (T4-b) allaqachon bor va bepul. Qidiruvni **til soni 15 dan oshganda** qo'shish
to'g'ri — buni qaror nuqtasi sifatida qoldirish kerak, hozir emas.

---

### T5. Til URL da (`/en/…`) — eng katta ochiq imkoniyat

3-qaror: "prefiks kerak — lekin oxirgi navbatda, standart til prefikssiz". Navbat amalda tugadi.

**O'lchandi:** `hreflang` yo'q; `canonical: "./"`; til faqat cookie'da.

Nima yo'qoladi: havolani ulashib bo'lmaydi ("mana bu sahifani ruscha ko'r"), qidiruv
tizimlari til variantlarini bilmaydi, `hreflang` yo'q, orqaga/oldinga tugmasi tilni
qaytarmaydi, bir sahifani ikki tilda ochib bo'lmaydi.

| # | Variant | Afzalligi | Kamchiligi | UX ta'siri |
|---|---|---|---|---|
| T5-a | To'liq `/en/…` marshrutlash | Ulashish, SEO, `hreflang`, til bo'yicha kesh | Eng qimmat: har marshrut ko'chadi; kesh/`Vary` bog'liqligi | Yuqori |
| T5-b | `?lang=en` **query** (prefiks emas) | Arzon; havola ulashiladi; marshrutlar tegmaydi | SEO foydasi kam; "chiroyli" emas | O'rta |
| T5-c | Faqat **`hreflang`** qo'shish (URL o'zgarmaydi) | Arzon; SEO qisman yaxshilanadi | Havola hali ham tilni saqlamaydi | Past-o'rta |
| T5-d | Hozircha **kechiktirish** | 0 xavf | Imkoniyat ochilmaydi | — |

**CTO tavsiyasi: T5-b (keyin T5-a).** Sabab: T5-a kesh arxitekturasiga tegadi, kesh esa
hozir **o'chiq** (`no-store`) — ya'ni T5-a ning katta qismi behuda bo'lardi. `Vary` muammosi
(`proxy.ts:59`) hal bo'lmaguncha to'liq prefiksga o'tish xatarli. `?lang=` esa bugun
ulashish muammosini yopadi va T5-a ga to'sqinlik qilmaydi.

**✅ Qaror (S5, 2026-09-19): Saidakbar aka T5-b ni tanladi** — `?lang=en` query, prefiks emas.

⚠️ **Bajarishda hal qilinishi shart bo'lgan uch nuqta** (savol matnida ham aytilgan):

1. **Parametr saqlanishi.** `?lang=ru` bilan kelgan odam ichki havolani bosganda parametr
   yo'qoladi (server cookie'ga, u ham bo'lmasa `Accept-Language` ga qaytadi). Ya'ni yoki
   har bir ichki havola parametrni olib yurishi, yoki birinchi tashrifda **cookie
   qo'yilishi** kerak. Ikkinchisi arzon, lekin `rw_locale=auto` markeri bilan
   aralashmasligi shart (qaror: cookie — odamning O'ZI tanlagani).
2. **`canonical` va `hreflang`.** Hozir `canonical: "./"` — `?lang=` bilan bu har xil
   variantni **bir xil** deb e'lon qiladi, ya'ni SEO foydasi nolga tushadi. hreflang
   faqat alohida URL talab qiladi, ya'ni T5-b da u ham `?lang=` URL'lariga bog'lanadi.
3. **Kesh.** Kesh yoqilganda `?lang=` ham `Vary`/kalit masalasini keltiradi — `proxy.ts:59`
   bilan bir vaqtda hal qilinishi kerak.

### T5 — holat: bajarildi (PR #108)

**S5b qarori (2026-09-19): cookie yangilanadi.** Uch nuqta quyidagicha yopildi:

1. **Parametr saqlanishi — cookie yozish bilan.** Proxy `?lang=<kod>` ni ko'rsa qiymatni
   **ikki joyga** yozadi: so'rov sarlavhasiga (joriy javob shu tilda chiziladi) va
   `rw_locale` cookie'siga (keyingi so'rovlar ham shu tilda). Shu sababli ichki
   havolalarni o'zgartirish **shart emas**.
2. **`canonical` — o'lchandi, allaqachon toza.** `canonical: "./"` query'ni **tashlab
   yuboradi**: `/about?lang=ru` javobida `<link rel="canonical" href="…/about">` — ya'ni
   `?lang=` variantlari **bir xil** deb e'lon qilinadi va SEO foydasi **nol**
   (kutilganidek). Bu T5-a (prefiks) ishining dalili: foyda faqat alohida URL bilan
   keladi.
3. **Kesh** — ochiq qoldi, lekin o'tkirlashdi: bitta path endi bir necha URL.
   `docs/08-technical-spec/i18n-precedence.md` ga qayd etildi.

**Ustunlik tartibi (kodda):** `?lang=` → cookie → `Accept-Language` → `uz`. Sof funksiya:
`apps/web/src/i18n/resolve.ts` → `resolveLocale()`; proxy `next/headers` ni import qila
olmaganidan uch nom `apps/web/src/i18n/locale-params.ts` da yagona manbada.

**O'lchandi — `curl` (lokal, `next dev --webpack`, `/about`):**

| So'rov | Natija |
|---|---|
| `?lang=ru` (cookie yo'q) | `set-cookie: rw_locale=ru; Max-Age=31536000; SameSite=lax`; `<html lang="ru">`; `<title>Как это работает · RankWant</title>`; `/i18n/ru.js` |
| cookie `rw_locale=ru` | `<html lang="ru">` |
| `?lang=xx` + cookie `uz` | `<html lang="uz">` — notanish qiymat sahifani bo'shatmaydi |
| `?lang=ru` + cookie `uz` | `<html lang="ru">` — **havola qurilmadan ustun** |
| cookie yo'q + `Accept-Language: ru-RU,ru;q=0.9` | `<html lang="ru">` |

**O'lchandi — haqiqiy brauzer** (izolyatsiya qilingan kontekst, toza cookie):

| Qadam | URL | cookie | `documentElement.lang` | `<title>` |
|---|---|---|---|---|
| `/about?lang=ru` ga kirish | `…/about?lang=ru` | `rw_locale=ru` | `ru` | ruscha |
| **ichki havola** `/about` bosildi | `…/about` | `rw_locale=ru` | `ru` | ruscha |
| tanlagichdan **English** | `…/about` | `rw_locale=en` | `en` | inglizcha |
| tanlagichdan **«Avtomatik»** | `…/about` | `rw_locale=auto` | `en` | inglizcha |

Ikkinchi qator — S5b ning butun ma'nosi: parametrsiz keyingi sahifa ham ruscha qoldi,
ya'ni **hech bir ichki havola o'zgartirilmadi**.

**Yo'l-yo'lakay topilgan va tuzatilgan nuqson (o'lchov bilan):** birinchi urinishda
tanlagich `router.replace()` ni **yolg'iz** chaqirardi. Natija: URL va kontent almashdi,
lekin `document.documentElement.lang` **`ru` bo'lib qoldi** (kontent inglizcha!). Sabab:
soft navigatsiya faqat sahifa segmentini yangilaydi, ildiz layout keshlangan qoladi —
`<html lang>` esa ildizda chiziladi. Nazorat o'lchovi (parametrsiz yo'l, u yerda
`router.refresh()` ishlaydi) atributni to'g'ri yangiladi, ya'ni nuqson aynan shu
shoxobchada edi. Tuzatish: `replace()` + `refresh()` birga. **WCAG 3.1.1** — noto'g'ri
`lang` ekran o'quvchini xato ovozga o'tkazadi, ya'ni bu kosmetik emas.

⚠️ **Yo'l-yo'lakay topilgan tuzoq (hujjatlashtirildi):** `NextResponse.next()`
`request.headers` ni **chaqiruv paytida** ko'chiradi (`next@16.3.4`, `response.js:128`),
ya'ni `?lang=` sarlavhasi javob yaratilishidan **oldin** yozilishi shart. Aks holda
sahifa cookie tilida chiziladi va xususiyat «bir so'rov kechikib ishlaydi» — yashil
ko'rinadi, aslida buzuq. `tools/check_decisions.py` endi **tartibni** tekshiradi, faqat
mavjudligini emas.

**Darvozalar:** `✓ 24 ta qaror` (yangi qoida: `locale_travels_in_the_url`); salbiy
testlar **194/194** (4 tasi yangi); unit testlar **80/80** (11 tasi yangi:
`tests/unit/locale-resolve.test.ts`); lint, `tsc`, `check_docs`, `check_i18n`
10 × 1600, `check_hardcoded` 291+111, `check_contrast` 772, `next build --webpack` —
yashil.

---

### T6. Hisob bilan sinxronizatsiya

Kod bor: `announcePrefs({ locale })` → `PrefsSync` → `ui_prefs.locale`.
Ustunlik qoidasi: **qurilma ustun** (4-qaror, ataylab chetlanish).
**O'lchanmagan:** ikkinchi qurilmada haqiqatan qo'llanadimi (jonli sinov kerak).

| # | Variant | Afzalligi | Kamchilik | UX ta'siri |
|---|---|---|---|---|
| T6-a | Hozirgi: qurilma ustun, hisob urug' | «Avtomatik» ishlaydi; kutilmagan almashtirish yo'q | Ikkinchi qurilmada til boshqa bo'lishi mumkin | O'rta |
| T6-b | Hisob ustun | Izchil | «Avtomatik» ma'nosiz bo'ladi; 2-qaror buziladi | Salbiy |
| T6-c | Sozlamalarda **ko'rinadigan** tanlov ("Til: qurilma/hisob") | Oshkora; foydalanuvchi boshqaradi | Yangi UI; yangi holat | O'rta |

**CTO tavsiyasi: T6-a, lekin avval o'lchash.** Sabab: qoida qabul qilingan va hujjatlashtirilgan;
lekin "ishlayapti" deyish uchun ikkinchi qurilma sinovi kerak. O'lchovsiz T6-c ga o'tish —
ertaga.

### T6 — holat: bajarildi (qaror, kod o'zgarmadi)

**✅ Qaror (S6, 2026-09-19): Saidakbar aka T6-a ni tanladi** — hozirgi xatti-harakat
**yakuniy**, ko'rinadigan tanlov (T6-c) **qurilmaydi**.

Savol uch variant bilan berildi: ① o'lchov avval (CTO tavsiyasi), ② **T6-a** — o'zgartirmaslik,
③ T6-c — sozlamalarda ko'rinadigan tanlov. Ega **② ni tanladi**, ya'ni CTO tavsiyasining
birinchi yarmi (o'lchovni oldinga qo'yish) ham rad etildi: ikkinchi qurilma sinovi
**o'lchanmagan holda qoladi**.

Natija:
- **Kod o'zgarmaydi** — yangi UI, yangi holat, yangi `check_decisions` qoidasi yo'q.
- `docs/08-technical-spec/i18n-precedence.md` ga **yozib qo'yildi**: egaga T6-c
  **taklif qilingan va rad etilgan**, ya'ni kelajakda agent «yaxshilash» sifatida
  ustunlik tanlovini qo'shmasligi kerak. Bu — shu qoidaning «orqaga qaytarilmasin»
  yozuvi (registrda alohida qatori yo'q, qoida hujjatda yashaydi).
- ⚠️ Ochiq qoladi: hisob urug'i ikkinchi qurilmada haqiqatan ishlaydimi — endi bu
  **ataylab** o'lchanmagan (qaror shuni qabul qildi), lekin kelajakda o'lchansa natija
  **hisobot qilinadi, darhol o'zgartirilmaydi**.

---

### T7. RTL tayyorgarligi

Hozirgi 10 tilning **hammasi chapdan o'ngga** (`uz, kaa, ru, en, kk, ky, tg, tr, zh, es`).
Ya'ni RTL bugun **muammo emas**. Kelajakda `ar`/`fa`/`he` qo'shilsa kerak bo'ladi:
`dir="rtl"`, mantiqiy CSS xossalari (`margin-inline` va h.k.), ro'yxat ochilish tomoni.

**CTO tavsiyasi: hech narsa qilmaslik, lekin qayd etish.** Sabab: ishlatilmaydigan
imkoniyatga kod yozish — xarajat. Yangi RTL til qo'shilganda alohida ish sifatida olinadi.

---

## 4. UX ta'siri — taqqoslash

| Taklif | Kimga ta'sir qiladi | Chastota | Jiddiylik | Narx | Ustuvorlik |
|---|---|---|---|---|---|
| **P1 tuzatish** (A) | Har bir qaytgan foydalanuvchi | Har almashtirishda | **Juda yuqori** — sahifa buziladi | Kichik | **1** |
| **T3-a** zaxira belgisi (6 joy) | 7/10 til foydalanuvchisi | Kontent sahifalarida | Yuqori — noto'g'ri til | Kichik | **2** |
| **T1-a** prefetch | Har bir almashtiruvchi | Har yangi tilda | O'rta — 0.7 s kutish | Kichik | **3** |
| **T2-b** endonim | Mobil foydalanuvchilar | Doimiy | O'rta — o'z tilini ko'rmaydi | Kichik (o'lchov shart) | **4** |
| **T5-b** `?lang=` | Yangi tashrifchilar | Ulashganda | O'rta — SEO/ulashish | O'rta | **5** |
| **T3-c** qamrov ro'yxatda | Tanlov paytida | Har tanlovda | O'rta | Kichik | **6** |
| **T6-c** sozlamalarda | Ko'p qurilmali | Kam | Past | O'rta | **7** |
| **T4-c** qidiruv | 30+ til bo'lsa | — | Hozir yo'q | O'rta | **8** |
| **T7** RTL | RTL til qo'shilsa | — | Hozir yo'q | Katta | **9** |

---

## 5. Tanlov nuqtalari (keyingi sessiyalar navbati)

Har biri — bitta savol, bir-birini istisno qiluvchi variantlar, CTO tavsiyasi bilan.
Tartib ataylab shunday: keyingi savol oldingisiga tayanadi.

| # | Savol | Nimani hal qiladi | Holat |
|---|---|---|---|
| **S1** | P1 xatoni **qanday** tuzatamiz (A/B/C/D)? | Butun bo'limning ishlashini | ✅ **Hal qilindi** — A tanlandi, `7fd8b05` ga birlashtirildi (§2.6) |
| **S2** | Zaxira belgisini **qanday** ko'rsatamiz (T3-a/b/c/d)? | 10-qarorning bajarilishi | ✅ **Hal qilindi** — T3-a + T3-c tanlandi, bajarildi va **birlashtirildi** (`#106` → `6486cd6`, §3/T3) |
| S3 | Lug'atni **oldindan yuklaymizmi** va qanday (T1-a/b/c)? | Almashtirish tezligi | ✅ **Hal qilindi** — **T1-d** tanlandi: **hech narsa qilmaymiz**. Hozirgi xatti-harakat saqlanadi; ~0.7 s kutish qabul qilindi, prefetch qo'shilmaydi (kod o'zgarmaydi) |
| S4 | Tor ekranda **nima** ko'rsatamiz va panelni **qanday** joylaymiz (T2-a/b/c/d + geometriya)? | Mobil UX | ✅ **Hal qilindi** — «Geometriya + endonim trigger» tanlandi va bajarildi (**PR #107**, `fix/locale-narrow-switch`). Trigger endonimni har kenglikda ko'rsatadi (`max-w-[3rem]` chegarasi bilan), panel tor ekranda viewport'ga bog'lanadi. Qayta o'lchandi: 320/360 px da toshish **0**, bayroqlar **11/11**, qirqilgan nom **0**; 1280 px o'zgarmagan (§3/T2) |
| S5 | Tilni **URL ga** chiqaramizmi va qaysi shaklda (T5-a/b/c/d)? | Ulashish, SEO | ✅ **Hal qilindi va bajarildi** — **T5-b** (`?lang=en`) tanlandi va **PR #108** da amalga oshirildi. Sabab: kesh hozir o'chiq (`no-store`) va `Vary` muammosi ochiq — prefiksning katta qismi hozir behuda bo'lardi. Bajarishda: ① cookie yoziladi (S5b), ② `canonical` o'lchandi — query'ni tashlaydi, ya'ni SEO foydasi nol (T5-a dalili), ③ kesh ochiq qoldi (§3/T5) |
| **S5b** | `?lang=` **qanday saqlanadi** — cookie yangilanadimi yoki har havola parametr olib yuradimi? | Ulashishning ishlashi | ✅ **Hal qilindi va bajarildi** — «**cookie yangilanadi**» tanlandi (**PR #108**). Proxy qiymatni so'rov sarlavhasiga (joriy javob) va cookie'ga (keyingi so'rovlar) yozadi — ichki havolalar o'zgarmaydi. Brauzerda o'lchandi: `?lang=ru` → `/about` havolasi bosilganda ham ruscha qoldi. Yo'l-yo'lakay `router.replace()` yolg'izligi `<html lang>` ni eski qoldirishi topildi va tuzatildi (§3/T5) |
| S6 | Hisob/qurilma ustunligi **ko'rinadigan** bo'lsinmi (T6-a/c)? | Ko'p qurilma | ✅ **Hal qilindi** — **T6-a** tanlandi: hozirgi xatti-harakat yakuniy, ko'rinadigan tanlov **qurilmaydi**, ikkinchi qurilma o'lchovi **ataylab o'lchanmagan holda qoladi**. Kod o'zgarmadi; qaror `i18n-precedence.md` ga «taklif qilindi va rad etildi» deb yozildi (§3/T6) |

**Navbat tugadi** — S1…S6 ning hammasi hal qilindi. Qolgan ishlar (§3/T5, §6) qaror emas,
**bajarish** ishlari: `hreflang`, `canonical` mosligi, kesh/`Vary` arxitekturasi, deploy.

---

## 6. O'lchanmagan va cheklovlar

- ✅ **`Qaraqalpaqsha` endonimi 320px da toshadimi — O'LCHANDI (`6486cd6`):** toshmaydi,
  qirqilmaydi. Eng uzun endonim chip bilan ham `scrollWidth = clientWidth = 147` px;
  panelda 11 variantning **hech biri** `truncate` bo'lmadi. Ya'ni T2-b texnik jihatdan
  to'siqsiz (§3/T2).
- ✅ **Panel nuqsoni — TUZATILDI (PR #107, `a870741`):** 320px da panel chapga 44 px
  toshib, **barcha 11 bayroq** ekrandan tashqarida qolardi; chegara ~352 px edi. Sabab
  `w-64` + `right-0` (trigger o'ng cheti 320px da `212`). Endi tor ekranda panel
  viewport'ga bog'lanadi; qayta o'lchandi — toshish **0**, bayroqlar **11/11**.
- ✅ **`canonical` — O'LCHANDI (PR #108):** `canonical: "./"` query'ni **tashlaydi**
  (`/about?lang=ru` → `href="…/about"`), ya'ni `?lang=` variantlari bir xil deb e'lon
  qilinadi va SEO foydasi nol. Bu **xato emas, dalil**: foyda faqat alohida URL
  (T5-a, prefiks) bilan keladi.
- ⚠️ **`hreflang` hali yo'q** — T5-b da u ham `?lang=` URL'lariga bog'lanadi, ya'ni
  `canonical` bilan birga hal qilinishi kerak (ochiq).
- ⚠️ **Soft navigatsiyada `<html lang>` eskirib qolishi** — topildi va tuzatildi
  (PR #108): `router.replace()` yolg'iz chaqirilganda ildiz layout keshlangan qoladi va
  atribut eski tilda qolaveradi (kontent yangi tilda!). Endi `replace()` + `refresh()`
  birga. **WCAG 3.1.1** — bu kosmetik emas.
- `[o'lchanmagan]` **`?lang=` jonli stekda** — hozircha faqat lokalda o'lchandi
  (`next dev --webpack`). Jonli origin'ga chiqqach qayta o'lchash kerak (deploy
  qo'lda, hali yugurtirilmagan).
- `[o'lchanmagan]` **`?lang=` ma'lumotga boy sahifada** (masalan `/problems`) — o'lchov
  `/about` da (statik, API'siz) bajarildi.
- `[o'lchanmagan]` **React #467 ning sababi** — shartli `use()` faraz qilindi, dev build'da
  tasdiqlanishi kerak. Toza takrorlashda chiqmadi.
- `[o'lchanmagan — ataylab]` **Hisob sinxronizatsiyasi** ikkinchi qurilmada haqiqatan
  ishlaydimi. S6 qarori (T6-a) shuni **qabul qildi**: o'lchov oldinga qo'yilmaydi va
  ko'rinadigan tanlov qurilmaydi. Kelajakda o'lchansa — natija **hisobot qilinadi**,
  darhol o'zgartirilmaydi (`docs/08-technical-spec/i18n-precedence.md`).
- `[o'lchanmagan]` **`Vary` sarlavhasi** kesh yoqilganda muammo beradimi — hozir `no-store`
  tufayli yashiringan; kesh yoqilishi bilan o'lchash shart.
- `[o'lchanmagan]` **Ekran o'quvchi** bilan haqiqiy sinov (faqat a11y daraxti tekshirildi).
- `[cheklov]` Barcha o'lchovlar **localhost** prod stekda (`:8300`) — real internet
  kechikishi Slow 4G emulyatsiyasi bilan modellashtirildi, haqiqiy mobil tarmoq bilan emas.
- `[cheklov]` Brauzer oynasi 320px dan pastga tushmadi — 320px **qurilma emulyatsiyasi**
  bilan o'lchandi, haqiqiy qurilmada emas.

---

## Ilova. Qayta ishlab chiqarish buyruqlari

```bash
# Jonli manba HEAD bilan mos ekanini tekshirish
git log --oneline -1
docker inspect rankwant-web-1 --format '{{index .Config.Labels "org.rankwant.git-sha"}}'

# Til aniqlash
curl -s http://127.0.0.1:8300/ -H "Accept-Language: ru-RU,ru;q=0.9" | grep -o 'lang="[a-z-]*"' | head -1

# Vary va kesh
curl -s -D - -o /dev/null http://127.0.0.1:8300/ | grep -i "^vary\|^cache-control"
curl -s -D - -o /dev/null http://127.0.0.1:8300/i18n/uz.js | grep -i "^cache-control"

# To'liqlik
python tools/check_locales_parity.py     # 10 til × 3 ro'yxat — mos
python tools/check_email_locales.py      # 18 satr × 10 til — to'liq

# P1 ni brauzerda takrorlash (chrome-devtools MCP):
#   1. sahifani yuklash        → registry = [joriy til]
#   2. A tilga o'tish          → ishlaydi
#   3. B tilga o'tish          → ishlaydi
#   4. A tilga QAYTISH         → registry = [] , 38 xom kalit  ← XATO
#   o'lchash: self.__rwMessages.size
```
