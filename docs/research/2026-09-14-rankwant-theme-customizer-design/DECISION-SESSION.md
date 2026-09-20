# RankWant — Tema sozlagichi: qaror sessiyasi

**Sana:** 2026-09-13
**Ishtirokchi:** Saidakbar aka (qarorlar), WB (tahlil va savollar)
**Maqsad:** to'liq funksional tema sozlagichini loyihalash — 20 bosqichli
savol-javob, har bosqichda qabul qilingan qarorlar qayd etilgan.

**Kirish nuqtasi:** raqobatchi `kep.uz` dagi "Customize" panelini brauzerda
tekshirish + mavjud kod bazasini o'rganish. Kep.uz paneli — MUI asosidagi
tema sozlagichi (313 px o'ng drawer, 10 bo'lim, `localStorage` da saqlaydi,
pullik to'siq yo'q). U bizning talablarimizning **torroq** varianti: bizda
to'liq token tizimi va hisobga bog'langan saqlash allaqachon bor.

---

## 0. Hozirgi poydevor — nima bor, nima yo'q

Sozlagich NOLDAN qurilmaydi. Tekshirilgan holat:

| Nima | Qayerda | Holat |
|---|---|---|
| 12 uslub, `dual` bayrog'i | `apps/web/src/layout/styles.ts` | bor |
| 18 palitra (6 dual × 2 + 6 yakka) | `globals.css` `[data-style]` bloklari | bor |
| `--rw-*` token tizimi | `globals.css` | bor |
| Mavzu (light/dark) | `context/ThemeContext.tsx` | bor, **`system` yo'q** |
| Uslub konteksti | `context/StyleContext.tsx` | bor |
| Hisobga saqlash | `core.User.ui_prefs` (JSONField) | bor |
| Kalitlar oq ro'yxati | `core/serializers.py` `validate_ui_prefs` | **faqat `style`/`sound`/`effect`** |
| Qurilma nusxasi | `lib/prefs.ts` + `context/PrefsSync.tsx` | bor |
| Kontrast tekshiruvi | `tools/check_contrast.py` | bor, 18 palitra |
| Shriftlar | `next/font/google` — IBM Plex Mono/Serif | bor, 2 oila |
| Header boshqaruvlari | `ThemeToggle`, `StylePicker` | bor |

**Ya'ni yetishmayotgan narsa:** foydalanuvchi paneli, rang/shrift/zichlik
sozlamalari, shablonlar, sxema versiyalash va `validate_ui_prefs` ni
kengaytirish.

**Muhim kuchlanish (butun sessiyaning o'zagi):** loyihada kontrast CI
tekshiruvi 18 palitrani **sanab chiqadi**. Foydalanuvchi rangni o'zgartira
boshlasa, bu kafolat matematik jihatdan imkonsiz bo'lib qoladi — chunki
kombinatsiyalar soni cheksiz. Har bir rang va token qarori shu sababdan
kelib chiqadi.

---

## 1-bosqich — Qamrov va kirish nuqtasi

**Savol:** sozlagich qayerda turadi va kim foydalanadi?

- **D1.** Suzuvchi tugma **+** `/settings/ko'rinish` sahifasi. Tugma — tez
  sinash uchun, sahifa — batafsil sozlash va tushuntirish uchun.
- **D2.** Hamma foydalanadi, lekin saqlash farqli: **mehmon qurilmada**
  (`localStorage`), **kirgan odam hisobda**. Bu `PrefsSync` ning mavjud
  naqshi va o'zgartirish talab qilmaydi.

**Nega:** mehmonni chetlab o'tish "nega bu tugma o'chiq?" savolini
tug'diradi; kirgan odamga esa hisob orqali saqlash kerak.

---

## 2-bosqich — Mavjud boshqaruvlar va ziddiyat qoidasi

- **D3.** Header'dagi mavzu va uslub tugmalari **olib tashlanadi** — hammasi
  bitta sozlagichda. **Til tugmasi qoladi** (u ko'rinish emas, kontent tili).
- **D4.** Ziddiyatda **hisob ustun**, qurilma nusxasi — faqat hidratsiyadan
  oldin chaqnashni oldini oluvchi **kesh**, qaror qabul qilmaydi.

**Oqibat:** `ThemeToggle` va `StylePicker` fayllari o'chiriladi;
`PrefsSync` soddalashadi (hozir uslub uchun hisob, til uchun qurilma ustun —
endi hammasi hisob ustun, til bundan mustasno bo'lib qoladi).

---

## 3-bosqich — Mavzu modeli va bir muhitli uslublar

- **D5.** **`system` rejimi qo'shiladi** va **standart holat** bo'ladi (hozir
  standart — `dark`). OS sozlamasi `matchMedia` bilan jonli kuzatiladi.
- **D6.** Bir muhitli uslub (Terminal/Glass/Neu/Clay/Aurora/Skeu) tanlansa,
  mavzu **avtomatik** o'sha uslubning muhitiga o'tadi; mavzu tanlagichi
  o'chadi va yonida sabab yoziladi («bu uslub faqat qorong'i»).

**Nega:** 12 uslubning 6 tasi `dual: false`, shu jumladan **standart uslub
`clay`**. Buzuq holat (yorug' mavzu + faqat-qorong'i uslub) umuman yuzaga
kelmasligi kerak. Hozir `ThemeToggle` bunday uslublarda o'zini yashirardi —
bu ishlaydi, lekin sababni aytmaydi.

---

## 4-bosqich — Rang modeli va kontrast kafolati ⭐

**Bu sessiyaning eng muhim qarori.**

- **D7.** Tayyor namunalar (12–16 ta) **+ erkin rang rejimi**. Erkin rang
  faqat kontrast tekshiruvidan o'tgan variant sifatida qabul qilinadi.
- **D8.** `--rw-accent-fg` (rang ustidagi matn) qora/oq orasidan
  **yorqinlik bo'yicha avtomatik hisoblanadi**. Namuna ro'yxati esa
  oldindan filtrlanadi.

**Nega shunday:** kep.uz faqat 8 ta tayyor namuna beradi — bu tasodif emas,
kontrastni kafolatlashning eng oson yo'li. Lekin "o'z brendimning rangini
qo'yaman" degan talab qoladi. Ink ni hisoblash esa kafolatni **matematik**
qiladi: foydalanuvchi nima tanlasa ham matn o'qiladi.

**Oqibat:** panelda yorqinlik hisobi va kontrast hisobi kerak — bu
`check_contrast.py` dagi matematikaning **brauzerdagi nusxasi** bo'ladi
(6-bosqich).

---

## 5-bosqich — Tokenlar doirasi va rangning uslubga bog'lanishi

- **D9.** **To'liq token to'plami** (~40 ta `--rw-*`) ochiladi — alohida
  "kuchli rejim" bo'limi sifatida.
- **D10.** Rang **uslubga bog'liq**: har uslub o'z rangini eslab qoladi;
  uslub almashganda unga mos rang avtomatik qo'llanadi.

**⚠️ Oqibat va xavf:** D9 tavsiya etilgan "uchta token" variantidan **kattaroq
majburiyat**. 40 token × foydalanuvchi kombinatsiyasi kontrastni oldindan
sanab bo'lmaydi. Shuning uchun 6-bosqichdagi himoya **majburiy**, ixtiyoriy
emas. Agar himoya ishlamasa, a11y kafolati butunlay yo'qoladi.

**Nega D10 to'g'ri:** uslub o'z palitrasini olib yuradi (Terminal yashil
matnli, Aurora gradientli). Uslubdan mustaqil rang "Terminal + och sariq"
kabi mos kelmaydigan holat yaratardi.

---

## 6-bosqich — Kuchli rejim himoyasi va CI ning yangi roli

- **D11.** 40 token alohida **"Kuchli rejim"** bo'limida. Har token yonida
  **jonli kontrast ko'rsatkichi** (✓ AA / ✗). ✗ kombinatsiyani **saqlash
  bloklanadi** va sabab aytiladi.
- **D12.** Kafolat **ikki qavatli**: (1) CI 18 palitrani o'z holida
  tekshirishda davom etadi; (2) sozlagich panelida **ayni matematika**
  brauzerda ishlaydi va har o'zgarishni darhol tekshiradi.

**Nega bloklash:** ogohlantirib ruxsat berish "o'qib bo'lmaydigan interfeys"
holatini yaratadi va uni keyin jamoa tuzatishi kerak bo'ladi. Bloklash esa
xatoni **paydo bo'lishidan oldin** to'xtatadi.

**Nega ikki qavat:** CI statik kombinatsiyalarni, panel esa dinamik
(foydalanuvchi) kombinatsiyalarni qoplaydi. Biri ikkinchisini almashtira
olmaydi.

---

## 7-bosqich — Shriftlar va uslub tipografiyasi

- **D13.** 4 oila: **Inter, Plus Jakarta Sans, Roboto, DM Sans** — hammasi
  `next/font` bilan **o'zimizda** saqlanadi, `preload: false` (faqat
  tanlangani yuklanadi). Tashqi so'rov yo'q, LCP nazoratda, maxfiylik
  saqlanadi.
- **D14.** O'z tipografiyasi bor uslublar (Editorial — serif, Terminal —
  monospace) **o'z shriftini saqlaydi**; foydalanuvchi shrifti faqat
  **neytral** uslublarga ta'sir qiladi. Panelda izoh ko'rsatiladi.

**Oqibat:** build hajmi ~150–250 KB oshadi. Editorial/Terminal da shrift
tanlagichi o'chadi (mavzu tanlagichi kabi — D6 bilan bir xil naqsh).

---

## 8-bosqich — O'lcham va zichlik

- **D15.** Ikki **alohida** boshqaruv: (1) shrift o'lchami — ildiz
  `font-size` shkalasi; (2) zichlik — bo'shliq shkalasi.
- **D16.** **Qat'iy qadamlar:** shrift 90 / 100 / 110 / 120%, zichlik 3 qadam.
  Erkin slider yo'q.

**Nega ajratildi:** "katta shrift" va "ko'p joy" — har xil ehtiyoj. Ko'p
odam matnni kattalashtirmasdan bo'shliqni xohlaydi (va aksincha).

**Nega qat'iy:** erkin slider saytni sinovdan o'tmagan holatlarga tushiradi
(150% da yon menyu va jadvallar buziladi) va kontrast o'lchovlarini
ma'nosiz qiladi.

---

## 9-bosqich — Qulaylik (a11y) to'plami

- **D17.** Rang ajratolmaslik uchun **palitra MOSLASHADI** (simulyatsiya
  emas): holat ranglari (to'g'ri/noto'g'ri, reyting, nishon) **shakl va
  naqsh** bilan ham ajralib turadigan variantga o'tadi.
- **D18.** Uchta qo'shimcha: **harakatni kamaytirish**, **katta bosish
  maydonlari (44×44)**, **kuchli fokus halqasi**.

**Muhim farq:** kep.uz "Vision Mode" rang ajratolmaslikni **simulyatsiya**
qiladi (protanopiya, deuteranopiya va h.k.) — bu **dizayner** uchun foydali,
lekin rang ajratolmaydigan **foydalanuvchi** uchun foydasiz: u buni
allaqachon shunday ko'radi. Unga palitraning **moslashgani** kerak. Biz
ikkinchisini tanladik.

**Nega shakl/naqsh ham:** rang yagona tashuvchi bo'lsa, moslashtirilgan
palitra ham yetarli emas — WCAG 1.4.1 (rang yagona ma'no tashuvchi
bo'lmasin) talabi shu.

---

## 10-bosqich — «Tayyor shablon» nima degani

- **D19.** Shablon = **nomlangan to'plam**: uslub + mavzu + rang + shrift +
  zichlik. Bir bosishda hammasi qo'llanadi. Keyin qo'lda o'zgartirilsa
  «o'zgartirilgan» deb belgilanadi.
- **D20.** **6–8 ta jamoa shabloni** (har biri o'lchangan) **+ shaxsiy
  shablonlar** (faqat o'ziga ko'rinadi).

**Nega to'liq to'plam:** agar shablon faqat uslub bo'lsa, u 12 ta mavjud
uslubdan farq qilmaydi va "shablon" so'zi ma'nosiz bo'lardi.

**Nega 6–8:** har biri qo'lda o'lchanadi (kontrast, 10 til, mobil) — ko'p
shablon nazoratsiz qoladi.

---

## 11-bosqich — Shaxsiy shablonlar: saqlash va ulashish

- **D21.** Kirgan odamda **hisobda** (`ui_prefs`), **5 tagacha**, nomi bilan.
  Mehmonda **qurilmada, 2 tagacha**.
- **D22.** **Havola orqali ulashish**: shablon sozlamalari URL da
  (`?style=terminal&accent=…`). Moderatsiya kerak emas, saqlash joyi ham
  talab qilmaydi.

**Nega limit:** `ui_prefs` — bitta JSONField; cheksiz ro'yxat uni
boshqarib bo'lmaydigan hajmga olib chiqadi.

**Nega havola (kutubxona emas):** umumiy kutubxona moderatsiya, spam va
kontrast nazorati masalasini qo'shadi — bu alohida loyiha hajmi. Havola esa
o'sha ehtiyojning 80% ini moderatsiyasiz qondiradi.

---

## 12-bosqich — Real vaqtda ko'rish va saqlash modeli

- **D23.** Har o'zgarish **darhol butun sahifada** ko'rinadi (token
  almashtirish orqali). Panel yopilganda ham qoladi — "ko'rish" va "qo'llash"
  bir xil amal.
- **D24.** Har o'zgarish **avtomatik saqlanadi** + **«Bekor qilish»**
  tugmasi oxirgi o'zgarishni qaytaradi.

**Nega:** "Saqlash" tugmasi bo'lsa, odam sinab ko'rib panelni yopadi va
hammasi qaytadi — bu asabiy holat. Avtomatik saqlash + undo esa
"qo'rqmasdan sinab ko'rish" imkonini beradi.

**Texnik asos:** loyiha to'liq token asosida (`--rw-*`), ya'ni
`document.documentElement.style.setProperty()` bilan qayta render
qilmasdan almashtirish mumkin — bu arzon va tez.

---

## 13-bosqich — «Tiklash» nimani anglatadi

- **D25.** **Uch bosqichli tiklash:** (1) «Oxirgi o'zgarishni bekor qil» —
  darhol, tasdiqsiz; (2) «Shablon holatiga qaytar» — joriy shablonning
  boshlang'ich holati; (3) «Zavod sozlamalari» — hammasi, **tasdiq oynasi**
  bilan.
- **D26.** Zavod standarti **`clay` + `system`** bo'lib qoladi. `styles.ts`
  dagi `dashboard` izohidagi eskirgan «Hozirgi» so'zi **olib tashlanadi**.

**Topilgan ziddiyat:** `DEFAULT_STYLE = "clay"`, lekin `dashboard` izohi
«Hozirgi — yumshoq kartalar» deb yozilgan. Ikkalasi bir vaqtda to'g'ri
bo'la olmaydi — izoh eskirgan.

**Nega uch bosqich:** bitta tugma bo'lsa, bitta xato rangni qaytarish uchun
ham butun ko'rinish yo'qoladi.

---

## 14-bosqich — Panel shakli va suzuvchi tugma

- **D27.** Ish stolida **o'ngdan chiquvchi drawer**, telefonda **pastdan
  chiquvchi sheet**. Bitta komponent, ikki ko'rinish.
- **D28.** Suzuvchi tugma **yopiladi** va yopilgani **eslab qolinadi**;
  qaytarish uchun sozlamalar sahifasi va `Ctrl+.`.

**Nega tugma yopiladi:** doimiy suzuvchi element sahifaning o'ng chetidagi
kontent va tugmalarni to'sib qo'yadi (kep.uz da shunday — 29×114 px joy
doim band). Yopish imkoniyati bu muammoni hal qiladi.

---

## 15-bosqich — Panel modal bo'ladimi

- **D29.** **Modal emas**: fon qoraytirilmaydi, fokus tuzog'i yo'q, sahifa
  ochiq va ishlaydigan qoladi. `Esc` yopadi, fokus tugmaga qaytadi.
- **D30.** Klaviatura: `Ctrl+.` ochadi/yopadi, `Esc` yopadi, `Tab` panel
  ichida aylanadi, fokus halqasi panel ichida ham ko'rinadi.

**Nega modal emas:** sozlagichning butun ma'nosi — **sahifani ko'rish**.
Fokus tuzog'i va qoraytirilgan fon sahifani ko'rishni qiyinlashtiradi.
Kep.uz modal qiladi — biz ongli ravishda boshqacha tanladik.

**Oqibat:** `aria-modal` ishlatilmaydi; panel `role="dialog"` emas, balki
`role="complementary"` yoki `region` + `aria-label` bo'ladi. Bu a11y
jihatidan to'g'riroq — modal bo'lmagan panel modal deb e'lon qilinsa,
ekran o'quvchi foydalanuvchini chalg'itadi.

---

## 16-bosqich — Mobil xatti-harakati

- **D31.** **Uch nuqtali sheet**: yopiq / yarim (ekranning ~55%) / to'liq.
  **Standart — yarim**, ya'ni sahifaning tepasi ko'rinib turadi.
- **D32.** Telefonda **suzuvchi tugma yo'q** — kirish header'dagi kichik
  ikonka va sozlamalar sahifasidan.

**Nega yarim standart:** telefonda o'zgarishni ko'rish uchun sahifa
ko'rinib turishi shart. To'liq ekran sheet "real vaqtda ko'rish" va'dasini
mobil'da bajarilmaydigan qiladi.

**Nega suzuvchi tugma yo'q:** tor ekranda suzuvchi elementlar (yuqoriga
tugma, kelajakdagi chat) bilan to'qnashadi.

---

## 17-bosqich — Ma'lumot modeli

- **D33.** `ui_prefs` **guruhlangan va versiyalangan**:
  `{version: 2, appearance: {...}, tokens: {...}, a11y: {...}}`. Har guruh
  o'z validatoriga ega.
- **D34.** Shaxsiy shablonlar `ui_prefs` **ichida** ro'yxat sifatida.

**Hozirgi holat:** `validate_ui_prefs` faqat `style` (regex `[a-z-]{1,20}`),
`sound` (bool), `effect` (ro'yxatdan) ni qabul qiladi. 40 token + shrift +
zichlik + a11y + shablonlar bu whitelist ga sig'maydi.

**Nega versiya:** kelajakda sxema o'zgaradi (masalan yangi token qo'shiladi).
Versiyasiz har o'zgarish orqaga moslikni qo'lda ushlab turishni talab qiladi.

**Nega alohida jadval emas:** shablon hisob bilan birga kelishi kerak va
bitta so'rovda yuklanadi. Alohida jadval yangi model + API + admin talab
qiladi — 5 ta shablon uchun ortiqcha.

---

## 18-bosqich — Mavjud sozlamalarni ko'chirish

- **D35.** **Ikkalasi:** (1) bir martalik Django ma'lumot migratsiyasi
  v1 → v2; (2) **o'qishda ham moslash** — qurilmadagi eski nusxa yoki eski
  klient v1 yuborsa ham to'g'ri o'qiladi.
- **D36.** Noma'lum (kelajakdagi yoki buzilgan) versiya **saqlanadi**, lekin
  **qo'llanmaydi** — standart holat ko'rsatiladi.

**Nega ikkalasi:** faqat baza migratsiyasi yetarli emas — `localStorage` da
eski shakl yotadi va hidratsiyadan oldin u o'qiladi. Tanilmasa, bir
yuklanishda eski ko'rinish chaqnaydi.

**Nega saqlanadi:** yangi klient yozgan sozlamani eski klient o'chirib
qo'ymasligi kerak. Aks holda odam yangi qurilmaga qaytganda sozlamasi
jimgina yo'qoladi — qaytarib bo'lmaydigan yo'qotish.

---

## 19-bosqich — Jamoa nazorati va favqulodda o'chirish

- **D37.** Admin «standart ko'rinish» belgilaydi (uslub + mavzu + shablon).
  **Yangi** foydalanuvchi shuni ko'radi; **mavjudlarga tegilmaydi**.
- **D38.** **Feature flag** bor (`is_enabled`) — updates va roadmap
  modullaridagi bilan bir xil naqsh. O'chirilsa kirish nuqtalari ko'rinmaydi,
  saqlangan sozlamalar bazada qoladi.

**Nega mavjudlarga tegilmaydi:** ular allaqachon o'z tanlovini qilgan.
Majburlash "mening sozlamamni kimdir o'zgartirdi" degan ishonchsizlik
tug'diradi.

---

## 20-bosqich — Chiqarish va chiqish mezoni

- **D39.** **Bir marta chiqariladi** (fazalarga bo'linmaydi).
- **D40.** Chiqish mezoni — **texnik + foydalanish**:
  - kontrast: 18 palitra **va** override qatlami 100%;
  - sozlama saqlanishi 100% (hisob ↔ qurilma);
  - panel 10 tilda sig'adi (`zh` 4 belgi, `kk` 27 belgi — eng uzun);
  - panel ochilishi < 100 ms;
  - kuchli rejimda ✗ kombinatsiya saqlanmaydi;
  - foydalanish: 2 hafta ichida ≥15% foydalanuvchi kamida bir marta
    o'zgartiradi.

**⚠️ Xavf (D39 dan kelib chiqadi):** "bir marta chiqarish" kuchli rejimning
kontrast muammolarini oddiy sozlamalar bilan **birga** chiqaradi. Ushbu
hujjatda D9 (to'liq token to'plami) va D39 (bir marta chiqarish) eng katta
xavf juftligi. Yumshatish: D11 bloklovchi kontrast tekshiruvi va D38 feature
flag — nuqson topilsa modul bir tugma bilan o'chiriladi.

---

## Qarorlar yig'indisi

| № | Qaror |
|---|---|
| D1 | Suzuvchi tugma + `/settings/ko'rinish` sahifasi |
| D2 | Hamma foydalanadi; mehmon qurilmada, kirgan hisobda saqlaydi |
| D3 | Header'dagi mavzu/uslub tugmalari olib tashlanadi, til qoladi |
| D4 | Hisob ustun; qurilma nusxasi faqat kesh |
| D5 | `system` mavzu rejimi qo'shiladi va standart bo'ladi |
| D6 | Bir muhitli uslub mavzuni avtomatik moslaydi, tanlagich o'chadi |
| D7 | Tayyor namunalar + erkin rang (kontrastdan o'tsa) |
| D8 | `--rw-accent-fg` yorqinlik bo'yicha avtomatik hisoblanadi |
| D9 | To'liq token to'plami (~40) "kuchli rejim" sifatida ochiladi |
| D10 | Rang uslubga bog'liq; uslub almashsa mos rang qo'llanadi |
| D11 | Kuchli rejimda jonli kontrast ko'rsatkichi; ✗ saqlash bloklanadi |
| D12 | Kafolat ikki qavatli: CI (18 palitra) + panelda jonli tekshiruv |
| D13 | 4 shrift oilasi, `next/font` bilan o'zimizda, faqat tanlangani yuklanadi |
| D14 | Editorial/Terminal o'z shriftini saqlaydi |
| D15 | Shrift o'lchami va zichlik — alohida boshqaruvlar |
| D16 | Qat'iy qadamlar: shrift 90–120%, zichlik 3 qadam |
| D17 | Rang ajratolmaslikda palitra moslashadi (simulyatsiya emas) + shakl/naqsh |
| D18 | Uchta a11y sozlamasi: harakat, bosish maydoni, fokus halqasi |
| D19 | Shablon = uslub + mavzu + rang + shrift + zichlik |
| D20 | 6–8 jamoa shabloni + shaxsiy shablonlar |
| D21 | Shaxsiy: hisobda 5 ta, mehmonda qurilmada 2 ta |
| D22 | Shablon havola orqali ulashiladi (URL parametrlari) |
| D23 | O'zgarish darhol butun sahifada ko'rinadi |
| D24 | Avtomatik saqlash + «Bekor qilish» |
| D25 | Uch bosqichli tiklash (undo / shablon / zavod) |
| D26 | Zavod standarti `clay` + `system`; `dashboard` izohi tuzatiladi |
| D27 | Ish stolida drawer, telefonda bottom sheet |
| D28 | Suzuvchi tugma yopiladi va holati eslab qolinadi |
| D29 | Panel modal emas — sahifa ochiq qoladi |
| D30 | `Ctrl+.` / `Esc` / `Tab`, fokus halqasi ko'rinadi |
| D31 | Uch nuqtali mobil sheet, standart — yarim |
| D32 | Telefonda suzuvchi tugma yo'q |
| D33 | `ui_prefs` guruhlangan va versiyalangan (`version: 2`) |
| D34 | Shaxsiy shablonlar `ui_prefs` ichida |
| D35 | Migratsiya + o'qishda moslash |
| D36 | Noma'lum versiya saqlanadi, qo'llanmaydi |
| D37 | Admin standart ko'rinishni belgilaydi; mavjudlarga tegilmaydi |
| D38 | Feature flag (kill switch) |
| D39 | Bir marta chiqariladi (fazalarga bo'linmaydi) |
| D40 | Chiqish mezoni: texnik + foydalanish |
| D41 | 8 jamoa shabloni: Klassik, Kun, Tun, Konsol, Jurnal, Fokus, Yumshoq, Aurora |
| D42 | Erkin rang = tus + to'yinganlik; yorqinlik muhit bo'yicha hisoblanadi |
| D43 | Kuchli rejim flag bilan o'chiq chiqadi; tekshiruvchi CI bilan mos kelgach yonadi |
| D44 | `--rw-accent-fg` formulasi; kafolat diapazondan keladi, ink tanlovidan emas |
| D45 | Uchta accent juftligi hosil qilinadi (tugma, chip, havola) |
| D46 | `check_contrast.py` accent-matn juftligini ham o'lchashi shart (topilgan nuqson) |
| D47 | Mavzu `User.theme` da qoladi; `ui_prefs.appearance.theme` YO'Q |
| D48 | Kit oilalarini musobaqachi Interfeys yozadi; `/admin/kit` namuna |
| D49 | Shablon kit oilalarini ham identitetga oladi; apply tiklaydi |
| D50 | Layout chrome shaxsiy; APP-8 rad — match/apply nav/size ni olmasin |
| D51 | Kit oilalari Interfeysda 6 ta `SelectField`; chip devori yo'q |
| D52 | Accent gate: AA matni faqat o'lchangan ratio da; APP-9 yopildi |
| D53 | Interfeys layout chip qoladi; kit SelectField (D51) |

### D47 — mavzu ikki joyda saqlanmaydi (amalga oshirishda aniqlangan)

D33 sxemasi `appearance` ichida `theme` ni ko'rsatgan edi. Amalga oshirishda
ma'lum bo'ldi: **`User.theme` allaqachon alohida maydon**
(`CharField(max_length=16, default="system")`) va `PrefsSync` uni o'sha
yerdan sinxronlaydi.

Ikki joyda saqlash hujjatning **o'z tamoyiliga** zid: "bir xil ma'no ikki
joyda — ziddiyat manbai" (D33 variantlarini solishtirganda aynan shu sabab
bilan alohida maydon rad etilgan edi). Shuning uchun:

- `User.theme` — **yagona manba**, `light` / `dark` / `system`.
- `ui_prefs.appearance` — faqat `style`, `accent`, `font`, `size`, `density`.
- Serializerga `validate_theme` qo'shildi: maydon ilgari **har qanday**
  16 belgili satrni qabul qilardi, ya'ni klient `Dark` yoki `system `
  yozsa jimgina saqlanardi va hech qanday mavzu qo'llanmasdi.

**Bonus:** maydonning standarti allaqachon `system`, ya'ni D5 (system —
standart) uchun baza o'zgarishi kerak emas edi; faqat frontend uni
tanlash imkonini bermasdi.

### D48 — kit-oila yozuvchisi (2026-09-21)

**Tanlov:** A — musobaqachi Interfeys. CTO B ni tavsiya qilgan edi
(`/admin/kit` yozadi); egasi A ni tanladi.

CUST-100 playground va 226 ikonka galereyasini `/admin/kit` ga olib
chiqdi, lekin Interfeys hali olti oilani yozadi. A shu yozuvchini
chegaraga aylantiradi:

| Sirt | Yozadi | O‘qiydi |
|---|---|---|
| Appearance → Interfeys | `verdictStyle` `statusStyle` `loadingStyle` `overlayStyle` `formStyle` `iconPack` | ha |
| `/admin/kit` | yo‘q | namuna (joriy pref bilan) |
| Shablon (D19, D49 da kengaydi) | apply defaultlarni yozadi | match solishtiradi |

**O‘lchandi (2026-09-21, `origin/main` `806bdd7`):** Interfeysda 50
kit-oila chip. `KitPlayground.tsx` da `setAppearance` / `useCustomizer`
yo‘q.

**Keyin:** D49 shablon identitetini kengaytirdi.

Batafsil: [DECISION-48.md](./DECISION-48.md).

### D49 — shablon kit identiteti (2026-09-21)

**Tanlov:** B — shablon kengayadi. D19 uslub+mavzu+rang+shrift+zichlik
qoladi; kit oilalari qo‘shiladi.

Sakkizta jamoa shabloni bitta `TEMPLATE_KIT_DEFAULTS` ni ulashadi.
`templateAppearance` apply da 6 kalitni tiklaydi; `matchTemplate`
solishtiradi. `undefined` kalit default deb o‘qiladi.

**O‘lchov:** D19-tor da `dashboard + circle` → `classic`. D49 da → `null`.
Apply Klassik → match `classic`.

nav / karta / naqsh / o‘lcham / kenglik matchda yo‘q — D50 buni qoida qildi.

Batafsil: [DECISION-49.md](./DECISION-49.md).

### D50 — layout chrome shaxsiy (2026-09-21)

**Tanlov:** A — layout shaxsiy. Shablon = D19 + kit (D49).
`TEMPLATE_LAYOUT_KEYS` apply/matchga kirmaydi.

APP-8 (nav/card ni matchga qo‘sh) **rad**.

**O‘lchov:** `dashboard + topnav + size 120` → `classic`. Apply Klassik
→ layout saqlanadi.

Batafsil: [DECISION-50.md](./DECISION-50.md).

### D51 — kit oilalari select (2026-09-21)

**Tanlov:** B — 6 labeled select. Native `<select>` emas: `SelectField`
(`Dropdown` / Combobox) — qorong'i mavzuda OS paneli oq chiqadi.

Yozuvchi D48: Interfeys. Boshqaruv: 50 chip → 6 tab stop (input).
Variantlar listboxda, ochilmaguncha tab tartibida emas. Demo `inert`.

Batafsil: [DECISION-51.md](./DECISION-51.md).

### D52 — accent gate ikki xabar (2026-09-21)

**Tanlov:** A — ikki xabar, Apply ikkalasida ham blok.
`accentGateKind`: `ground_unreadable` / `contrast_unreachable` /
`aa`. «Fails AA (4.5:1)» faqat o‘lchangan ratio da.

APP-9 yopildi.

Batafsil: [DECISION-52.md](./DECISION-52.md).

### D53 — layout chip qoladi (2026-09-21)

**Tanlov:** A. 2–5 variantli layout oilalari chip; kit katalogi select.

Batafsil: [DECISION-53.md](./DECISION-53.md).

---

## Ochiq savollar — HAL QILINDI

### S1. 8 jamoa shabloni

**D41.** Klassik, Kun, Tun, Konsol, Jurnal, Fokus, Yumshoq, Aurora.

| Shablon | Uslub + mavzu | Shrift | Zichlik | Kimga |
|---|---|---|---|---|
| Klassik | dashboard + system | IBM Plex | qulay | Standart |
| Kun | flat + light | Inter | qulay | Kunduzi |
| Tun | material + dark | Inter | qulay | Kechki o'qish |
| Konsol | terminal + dark | mono (o'z) | zich | Dasturchilar |
| Jurnal | editorial + light | serif (o'z) | qulay | Uzun matn |
| Fokus | swiss + light | Roboto | zich | Imtihonga tayyorgarlik |
| Yumshoq | clay + light | DM Sans | qulay | Maktab o'quvchilari |
| Aurora | aurora + dark | Plus Jakarta | qulay | Namoyish |

Uchta bir muhitli uslubning hammasi kirdi → D6 shablon darajasida ham
ishlaydi. `glass`, `neu`, `skeu`, `brutal` shablon olmadi (yakka uslub
sifatida qoladi). Rang har biri uchun o'sha uslubning o'z accent'i (D10).

### S2. Erkin rang chegaralari

**D42.** Foydalanuvchi **tus + to'yinganlik** tanlaydi (xom hex emas).
Tizim yorqinlikni har muhit uchun o'zi hisoblaydi:

- yorug' muhit: eng yorqin nuqta, `L ≤ 0.1733`
- qorong'i muhit: eng quyuq nuqta, `L ≥ 0.2160`

Ikkala hosil qilingan rang panelda **jonli** ko'rsatiladi (sariq yorug'
muhitda `#777700` — zaytun — bo'ladi; odam buni saqlashdan oldin ko'rishi
kerak).

**O'lchandi:** 12 tus × 3 to'yinganlik × 2 muhit = **72 holat, 0
muvaffaqiyatsizlik**. Ya'ni har qanday tus ikkala muhitga ham keltiriladi.

**Nega tus, rang emas:** yorug' fon `L ≤ 0.1733`, qorong'i fon esa
`L ≥ 0.2160` talab qiladi — bu oraliqlar **kesishmaydi**, ya'ni bitta rang
ikki muhitga sig'maydi. Dizayn tizimining o'zi ham har muhitga alohida
accent yozadi (`#476dc7` yorug', `#7ea4ff` qorong'i).

### S3. D9 + D39 xavfi

**D43.** Bir chiqarish qoladi (D39 buzilmaydi), lekin kuchli rejim
**flag bilan O'CHIQ** chiqadi. Flag faqat panel tekshiruvchisi
`check_contrast.py` bilan 18 palitrada **aynan bir xil raqam** bergandan
keyin yonadi.

**Nega:** accent yo'li matematik xavfsiz (S2 va S4). Xavf qolgan ~30
tokenda (`--rw-ground`, `--rw-surface`, `--rw-text`, `--rw-line`…) va
asosiy xarajat **UI emas, tekshiruvchi**: u har nishonni **to'g'ri
qo'shnisiga** qarab o'lchashi kerak (chegara — maydonning o'z foni, karta
emas). Bu qoidalar loyihada bir marta xato o'lchangan.

### S4. Rang ajratolmaslik

**D44 (palitra).** Tusni almashtirish + o'sha xavfsiz yorqinlik hisobi:

| Rejim | ok | warn | bad |
|---|---|---|---|
| protan/deutan (qizil-yashil yo'qoladi) | ko'k 210 | sariq 55 | to'q sariq 32 |
| tritan (ko'k-sariq yo'qoladi) | yashil 140 | magenta 320 | qizil 10 |

**O'lchandi:** 12 rangning hammasi AA — 4.50–4.52:1 (yorug' va qorong'i).

**D45 (achromatopsiya).** Rang ma'no tashiy olmaydi: yorug' fonda uchta
holatning qo'shni yorqinlik qadamlari orasida eng kattasi **1.63:1** —
ajratib bo'lmaydi. Shuning uchun bu rejim **shakl + matn** ga o'tadi:
har holatga belgi (✓ / ! / ✕) va matn yorlig'i.

**Muhim:** shakl/matn qatlami **rejim emas, doimiy talab** (WCAG 1.4.1).
Rang ajratolmaslik palitralari faqat qolgan rangli yuzalarni tuzatadi.
10 ta `rw-kind-*` nishonida matn yorlig'i allaqachon bor — ular 1.4.1 ni
bajaradi; CB rejimida ular 4 guruhga (ok/neytral/warn/bad) yig'iladi,
chunki protanopiyada `fixed` (yashil) va `breaking` (qizil) bir xil
ko'rinadi.

### S5. `--rw-accent-fg` formulasi

**D46.** Formula:

```
lin(c) = c ≤ 0.03928 ? c/12.92 : ((c+0.055)/1.055)^2.4
L      = 0.2126·R + 0.7152·G + 0.0722·B
ink    = L_accent < 0.1791 ? oq : quyuq ink
```

**Muhim noziklik — kafolat inkdan emas, diapazondan keladi:**

| Ink | Krossover | Eng yomon holat |
|---|---|---|
| oq / **toza qora** `#000000` | L = 0.1791 | **4.58:1** ✓ |
| oq / **fon rangi** `#0b0d12` | L = 0.1882 | **4.41:1** ✗ |

Loyiha qorong'i mavzuda ink sifatida `#0b0d12` ni ishlatadi (toza qora
emas) — bu o'zi kafolatni buzadi. Lekin **D42 diapazonlari krossoverdan
qochadi**, shuning uchun amalda xavfsiz:

- yorug' diapazon `L ≤ 0.1733` → oq ink → eng yomon **4.70:1** ✓
- qorong'i diapazon `L ≥ 0.2160` → `#0b0d12` ink → eng yomon **4.92:1** ✓

**Ya'ni:** diapazon olib tashlansa (masalan kuchli rejimda foydalanuvchi
accent'ni to'g'ridan-to'g'ri yozsa), kafolat 4.41:1 ga tushadi va **toza
qora** ishlatish shart bo'ladi.

**D45 (uchta juftlik).** Bitta emas, **uchta** accent juftligi hosil
qilinadi:

| Juftlik | Qayerda | Nimadan |
|---|---|---|
| `--rw-accent` + `--rw-accent-fg` | to'ldirilgan tugma | ink formuladan |
| `--rw-accent-soft` + `--rw-accent-ink` | rangli chip | ikkalasi tusdan |
| `--rw-accent-ink` + `--rw-ground`/`--rw-surface` | havola matni | S2 diapazoni |

`--rw-accent-ink` **ikkalasiga ham** sig'ishi kerak → qat'iyrog'i
tanlanadi.

### ⚠️ Topilgan nuqson — TUZATILDI (2026-09-14)

`tools/check_contrast.py` **to'rt pog'onali matn zinapoyasini**
(`--rw-text`, `--rw-text-2`, `--rw-muted`, `--rw-faint`) va **tugma
juftligini** (`--rw-accent-fg` / `--rw-accent`) o'lchaydi. `--rw-accent-ink`
faqat `FOCUS_TOKEN` sifatida ishlatiladi — ya'ni **fokus halqasi uchun
(3:1)**, matn sifatida emas.

**Birinchi hisobim bu nuqsonni KICHIK ko'rsatdi** — men faqat
`ground`/`surface`/`soft` ni sinab, "nuqson bitta uslubda (`dashboard`)"
deb xulosa qilgandim. Tekshiruv qo'shilganda ma'lum bo'ldi: checker fon
sifatida `--rw-hover`, `--rw-chip`, `--rw-field` kabilarni ham oladi va
**18 palitradan 7 tasi yiqiladi**, 27 juftlikda:

| Palitra | Eng yomon | Tuzatilgandan keyin |
|---|---|---|
| brutal | 3.70:1 | 4.60:1 |
| clay | 4.41:1 | 4.61:1 |
| dashboard | 4.02:1 | 4.62:1 |
| flat | 4.44:1 | 4.60:1 |
| flat.dark | 3.77:1 | 4.62:1 |
| neu | 4.03:1 | 4.63:1 |
| skeu | 3.31:1 | 4.60:1 |

**Tuzatish:** `--rw-accent-ink` har palitrada oklab yorqinligi bo'yicha qayta
hisoblandi — **tus va to'yinganlik saqlandi** (havola rangi accent bo'lib
qolishi kerak), faqat yorqinlik o'zgardi. O'zgarish vizual sezilmaydi
(masalan `clay`: `#7c3aed` → `#7936ea`; `dashboard`: `#4470e6` → `#3c66dc`).

**Salbiy test:** `dashboard` ning qiymati ataylab `#b9c9f5` ga buzuлganda
tekshiruv `exit 1` berdi va yangi qator chiqdi
(`accent matni … 1.58:1`); tiklanganda `exit 0`.

**Natija:** 718 matn rangi AA dan o'tadi (ilgari 691).

**Saboq:** "nuqson bitta uslubda" degan xulosa **o'lchov metodim** tor
bo'lganidan edi, kod emas. Checker fon ro'yxatini to'liq oladi — qo'lda
sanab chiqish uni har doim kam ko'rsatadi.

**Nega bu sozlagichga tegishli:** panelning jonli tekshiruvchisi shu
juftlikni qamramasa, foydalanuvchilar ayni nuqsonni **masshtabda**
yaratadi. Endi checker qamraydi.

**O'lchov usuli tekshirildi:** formula ma'lum qiymatlarda sinandi —
`#000000`/`#ffffff` = 21.00, `#767676`/`#ffffff` = 4.54 (AA chegarasi),
`#777777`/`#ffffff` = 4.48. Ya'ni raqamlar to'g'ri.

---

## Keyingi qadam

Barcha 5 ochiq savol hal qilindi (D41–D46). Amalga oshirishdan oldin
faqat bitta ish qoldi: **`dashboard` palitrasidagi accent-matn nuqsonini
tuzatish** va `check_contrast.py` ni shu juftlikka kengaytirish — aks
holda sozlagich nuqsonni takrorlaydi.


---

## Amalga oshirish tartibi (D39 "bir marta" bo'lsa ham ichki ketma-ketlik)

0. **Nuqsonni tuzatish (sozlagichdan OLDIN):** `check_contrast.py` accent-matn
   juftligini o'lchasin, `dashboard` ning `--rw-accent-ink` quyultirilsin.
   Aks holda sozlagich mavjud nuqsonni masshtabda takrorlaydi.
1. **Backend:** `validate_ui_prefs` guruhlangan sxema + versiya +
   migratsiya (D33, D35, D36).
2. **Poydevor:** `ThemeContext` ga `system` (D5), bir muhitli uslub
   avtomatikasi (D6), token override qatlami (D23).
3. **Panel:** drawer + mobil sheet (D27, D31), modal emas (D29),
   klaviatura (D30), suzuvchi tugma (D28, D32).
4. **Rang:** namunalar + erkin rejim + ink hisobi (D7, D8) + jonli kontrast
   va bloklash (D11, D12).
5. **Shrift va o'lcham:** 4 oila (D13, D14), o'lcham/zichlik (D15, D16).
6. **A11y to'plami:** palitra moslashuvi + shakl/naqsh (D17), uchta sozlama
   (D18).
7. **Shablonlar:** 6–8 jamoa + shaxsiy (D19–D22).
8. **Kuchli rejim:** 40 token (D9, D10) — eng oxirida, chunki u eng xavfli.
9. **Jamoa:** admin standarti (D37), feature flag (D38).
10. **Tekshiruv:** `check_contrast.py` kengaytirish (override qatlami),
    10 til sig'ish testi, `check_deploy.sh`.

---

**Keyingi qadam:** ochiq savollarga javob berish (ayniqsa 1, 2 va 3) va
keyin amalga oshirishni boshlash.
