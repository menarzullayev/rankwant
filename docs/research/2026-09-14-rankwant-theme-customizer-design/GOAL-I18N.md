# /goal — i18n stekini qarorlar bo'yicha tugatish

Quyidagi matnni `/goal` ga bering.

---

## Vazifa

RankWant'ning tarjima va til tanlash stekini 10 ta qabul qilingan qaror
bo'yicha tugat. Hozir stek **ishlaydi**, lekin uchta jimgina nuqsoni bor:
`t()` lug'at topilmasa kalit nomini qaytaradi, xatlar 10 tildan 3 tasida,
va bir xil URL turli til qaytaradi (`Vary` siz). Bularni yop, keyin
tanlagichni qayta yoz.

**Birinchi qadam — o'qi, keyin boshla:**

- `rankwant-theme-customizer-design/I18N-STACK-ANALYSIS.md` — **to'liq
  tahlil va 10 qaror**. Har band shu yerdan olinadi, o'zingdan qaror
  qo'shma.
- `~/.workbuddy-ai/MEMORY.md` va `rankwant/.workbuddy-ai/memory/MEMORY.md`
  — til siyosati va doimiy qoidalar.
- `PLAYBOOK.md` — deploy, tekshirish tartibi, o'lchash usullari.

---

## Qat'iy qoidalar (buzilmaydi)

1. **O'lchov taxmindan ustun.** Har da'vo yonida dalil turi bo'lsin:
   `[o'lchandi]` (raqam bilan), `[kod]`, `[o'lchanmagan]`. "Ishlayapti"
   deb yozish uchun o'lchov kerak.
2. **Har yangi tekshiruvga SALBIY TEST shart.** Qiymatni ataylab buz,
   `exit 1` ni ko'r, tiklа, `exit 0` ni ko'r. Salbiy testsiz tekshiruv
   **o'lik tug'ilishi mumkin** — bu loyihada ikki marta shunday bo'lgan
   (`pathlib.glob` qavsni qo'llamagani uchun).
3. **Klient tomonda yiqiladigan xato uchun brauzerda ochish shart.**
   `curl 200` + yashil CI **isbot emas** — SSR qobig'i klient daraxtidan
   oldin qaytariladi. Sahifa bo'sh ko'rinsa birinchi qadam — konsol.
4. **Deploydan keyin `bash tools/check_deploy.sh`** — `0` bo'lsin.
   Konteyner eski build'da qolishi mumkin, CI buni ko'rmaydi.
5. **Til siyosati:** muloqot va hisobot — o'zbekcha; kod, buyruq, izoh,
   commit — inglizcha. Interfeys matni — **"siz"**.
6. **Commit — Conventional Commits**, inglizcha, sabab bilan.
7. **`docs/` — inglizcha.** Repo hujjati o'zbekcha yozilmaydi.
8. **Jonsiz e'lon qoldirma:** kodda chaqirilmaydigan tekshiruv,
   ishlatilmaydigan sozlama, o'rnatilmagan hook — olib tashla yoki ishlat.

---

## Ish tartibi

Tartib **ataylab shunday** — har band oldingisiga tayanadi. Sakrab
o'tilmаydi.

### 1. `t()` — jimgina yutishni to'xtat (qaror 6)

`i18n/messages.ts`. Hozir: `registry.get(locale)?.[key] ?? key`.

- **Dev:** lug'at topilmasa **xato otilsin** (`throw`).
- **Prod:** kalit qaytsin (ko'rinadigan, xabar qilinadigan) **+ bir marta
  `console.error`**.
- **`uz` zaxirasi QO'SHILMAYDI** — 34 kB turadi va bugni yashiradi.
- `errorText()` ham xuddi shu yo'ldan o'tsin (u ham `registry` ni
  to'g'ridan-to'g'ri o'qiydi).

**Tekshiruv:** dev'da mavjud bo'lmagan til bilan `t()` chaqirilsa yiqilsin;
prod rejimida kalit qaytsin va jurnalga yozilsin. Ikkalasiga ham salbiy
test.

### 2. `registry` ni chegarala (A2)

`registerMessages()` faqat aktiv tilni saqlasin — `Map` o'sib ketmasin.
Yoki bir yozuvli bo'lsin, yoki eski yozuv o'chirilsin.

**Tekshiruv:** 10 marta til almashtirib, `registry.size` ni o'lcha.
`[o'lchandi]` bilan raqam yoz.

### 3. Tanlagichning orqaga sakrashini tuzat (qaror 7)

`layout/LocaleSwitch.tsx`. Hozir `value={locale}` server propidan keladi,
ya'ni tanlov darhol orqaga qaytadi (o'lchandi: 250 ms `zh`).

- Mahalliy optimistik `useState` — tanlangan til **darhol** ko'rinadi.
- Kutish belgisi (`pending`).
- **Arxitektura tegmaydi:** server yangilanishi qoladi.

**Tekshiruv (brauzer):** `zh` → `ru` tanla, **darhol** `ru` ko'rinishini
tasdiqla (avval `zh` edi). O'lchov raqami bilan.

### 4. `color-scheme` va o'lcham (qaror 8, qism)

Hozir `color-scheme: normal` — qorong'i UI da native ro'yxat **oq**
chiqadi (o'lchandi). O'lcham 118×28, shrift 12px; header'dagi boshqa
tugmalar 40×40.

**Tekshiruv (brauzer):** qorong'i mavzuda `color-scheme` `dark` bo'lsin;
o'lcham 40px balandlikka kelsin.

### 5. Xatlar — tranzaksion 7 til (qaror 5)

`core/email_text.py`. Hozir faqat `uz`/`ru`/`en`; zaxira **jimgina** `uz`
(o'lchandi).

- Avval **tranzaksion** xatlar: email tasdiqlash, parol tiklash,
  ro'yxatdan o'tish. Bularsiz odam tizimga kira olmaydi.
- Zaxira **o'lchanadigan** bo'lsin — til yetishmasa log/hisoblagichga
  yozilsin, jimgina o'tilmasin.
- `gettext` ga **o'tilmaydi** — sabab `email_text.py` ning o'z izohida.

**Tekshiruv:** har til uchun xat matni o'zbekcha **emasligini** tekshir;
zaxira ishlaganda log yozilishini salbiy test bilan ko'rsat.

### 6. Custom listbox (qaror 8, 9)

`LocaleSwitch` native `<select>` dan **custom listbox** ga o'tadi.

⚠️ **Native bepul bergan narsa endi qo'lda yoziladi.** Bularsiz bu band
**a11y regressiyasi** bo'ladi:

- `role="listbox"` / `role="option"` / `aria-selected` / `aria-expanded`
- Klaviatura: `↑` `↓` `Home` `End` `Enter` `Space` `Esc`, fokus halqasi
- **Type-ahead** — harf bosilsa mos variantga sakrash
- Fokus yopilganda **ochgan tugmaga qaytishi**
- Tashqariga bosish va `Esc` bilan yopilish
- **Mobil OS tanlagichi yo'qoladi** → alohida touch-sheet
- Yopiq holatda joriy til ekran o'quvchiga **e'lon qilinishi**

Ro'yxat mazmuni (qaror 9): **endonim + inglizcha nom** (`O'zbekcha —
Uzbek`), **mintaqa guruhi** (asosiy / mintaqa / keng qamrov),
**«Avtomatik» birinchi** va joriy aniqlangan tilni ko'rsatsin
(`Avtomatik (English)`). **Qidiruv yo'q** — 10 variant sig'adi.

Ekran o'quvchi nomi ham tarjima qilinsin: hozir qat'iy `"Til / Language"`.

**Tekshiruv:** Lighthouse `Accessibility` **100** bo'lib qolsin (hozir
100). Brauzerda klaviatura bilan to'liq o'tib chiq: `Tab` → `Enter` →
`↑↓` → `Enter`, fokus qaytishi. Mobil viewport'da sheet ochilsin.

### 7. Zaxirani ishlatish joyida belgila (qaror 10)

Tanlagichda qamrov nishoni **qo'yilmaydi**. Zaxira sodir bo'lgan joyda
belgilanadi: mavzu/ko'nikma nomi boshqa tilda ko'rsatilganda kichik `uz`
belgisi yoki izoh.

**Tekshiruv (brauzer):** `zh` da mavzu nomi yonida belgi ko'rinsin.

### 8. Qolgan xatlar — 7 tilning to'liq qamrovi (qaror 5)

5-banddan keyin qolgan xatlar (bildirishnomalar va h.k.).

**Tekshiruv:** `email_text.py` da 10 tilning hammasi borligini skript bilan
tekshir; salbiy test bilan.

### 9. Ustunlik qoidasini yoz (qaror 4)

Til uchun **qurilma (cookie) ustun**; hisob — cookie'siz qurilma uchun
urug' va **xat tili** manbai. Bu D4 (mavzu: hisob ustun) dan **ataylab
chetlanish**.

⚠️ Qoidani **kod izohi va hujjat sifatida yoz** — aks holda keyingi
o'qigan odam buni "D4 buzilgan" deb tuzatadi va qurilma tanlovini
yo'qotadi.

### 10. `Vary` va «Avtomatik» varianti (qaror 2)

- `Vary: Accept-Language` qo'shilsin. Bugun `no-store` bo'lgani uchun
  zararsiz — **kesh yoqilsa bir zumda zaharlash xatosi** (bir xil URL
  turli til qaytaradi: o'lchandi, `en`/`ru`/`zh`/`ky`).
- «Avtomatik» varianti tanlagichga qo'shilsin (6-bandda).

**Tekshiruv:** `curl -D -` da `Vary` sarlavhasida `Accept-Language` bor.

### 11. O'lik sozlamani olib tashla (A6)

`config/settings.py`: `USE_I18N=True` + `LocaleMiddleware` yoqilgan,
lekin `locale/` katalogi yo'q va **birorta `gettext` chaqiruvi yo'q**.
`LANGUAGES` — 3 til, holbuki `User.Locale` — 10.

Yoki olib tashla, yoki nima uchun kerakligini yoz. Jonsiz qoldirma.

### 12. `intlLocale` va kontent nomlari (A9, A10)

- `kaa`/`ky`/`tg` uchun sana formati `uz` ga tushadi — **hujjatlashtir**
  (nima uchun, va foydalanuvchi nimani ko'radi).
- `topicName()` / `localName()` faqat `uz`/`ru`/`en` biladi — qolgan 7 til
  o'zbekcha ko'radi. Bu **kontent ishi** (145 ta mavzu); hozircha 7-bandda
  belgi qo'yiladi, to'liq tarjima alohida ish sifatida yozilsin.

### 13. `check_i18n.py` bo'shlig'i (A12)

Shablon satrli kalitlar (`t(locale, \`customizer.template.${id}\`)`)
statik tekshirilmaydi. Ma'lum dinamik oilalar uchun ro'yxatni tekshir
(masalan `customizer.template.*` ning barcha `id` lari mavjudmi).

---

## Tayyorlik mezoni

| Mezon | Talab |
|---|---|
| `bash tools/ci-local.sh all` | **0** |
| `bash tools/check_deploy.sh` | **0** |
| Lighthouse (desktop, panel ochiq) | Accessibility **100** |
| Lighthouse (mobil) | **100** |
| `check_i18n.py` | toza, xom kalit yo'q |
| Kontrast | `check_contrast.py` **0** |
| Xatlar | 10 tilning hammasi (yoki tranzaksion 10 + qolgani hujjatlashtirilgan) |
| Tanlagich | orqaga sakramaydi (brauzerda o'lchandi) |
| Custom listbox | klaviatura, type-ahead, mobil sheet, ekran o'quvchi |
| Har yangi tekshiruv | **salbiy test bilan** |
| `origin/main` ga push | ✅ |

---

## To'xtash sharti

**To'xta va so'ra, agar:**

- Qaror tahlilga zid chiqsa (masalan 6-band `uz` zaxirasini talab qilsa).
- Biror band boshqa qarorni bekor qilishi aniqlansa.
- Custom listbox a11y ni Lighthouse 100 dan tushirsa va yechim topilmasa.
- Vaqt tugasa — **o'zingcha davom etma**, qolganini hisobotda yoz.

**Vaqt tugaganda:** bajarilganini commit qil, `origin/main` ga push qil,
ochiq bandlarni hisobotda aniq yoz. Yarim ishni "bajarildi" deb
belgilama.

---

## Hisobot (o'zbekcha, 7 bo'lim)

1. **Nima qilindi** — commit'lar jadvali (hash + mazmun).
2. **Nima qoldi** — band bo'yicha, sabab bilan.
3. **O'zim qabul qilgan qarorlar** — tahlilda yo'q edi, lekin kerak
   bo'ldi.
4. **O'lchangan raqamlar** — oldin/keyin.
5. **Jonli tekshiruv** — har amal va natijasi.
6. **Topilgan yangi nuqsonlar** — tuzatilgani va qolgani.
7. **Qayerda to'xtadim va nima uchun** — keyingi qadam.

⚠️ Hisobda **"o'lchandi"** va **"taxmin"** aralashmasin. O'lchanmagan
narsani `[o'lchanmagan]` deb belgila.

---

## Oxirgi eslatma

Bu ishning eng qimmat saboqi ikki marta takrorlandi: **yashil natija
buzuq holatni o'tkazishi mumkin**. Bugun `check_i18n.py` 791 kalitni
"to'liq" deb tasdiqlagan edi, holbuki panel ekranda **kalit nomlarini**
ko'rsatardi. Shuning uchun har yangi tekshiruvga salbiy test, va har
klient tomonidagi o'zgarishga brauzer tekshiruvi **shart**.
