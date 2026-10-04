# RankWant — Contest reyting unvonlari: nom variantlari

> **Arxiv yozuvi.** Repoga 2026-10-04 da ko'chirildi; matn yozilgan kunidagi holatni aks ettiradi. Bu zinapoya keyin almashtirilgan: amaldagi qaror — 16 pog'ona, 7 rang guruhi (`CLAUDE.md`, 2026-09-20). Foizlar `seed_stress` simulyatsiyasidan, jonli bazadan emas.

**Sana:** 2026-09-19
**Holat:** taklif (qaror emas) — ADR-0018 ni almashtirmaydi, yangilash uchun asos
**Manba fayllar:** `apps/api/profiles/titles.py`, `docs/07-adr/0018-*.md`,
`docs/04-prd/README.md`, `apps/web/src/app/globals.css`

---

## 1. Hozirgi holat — kodda nima bor

Bu topshiriq **bo'sh joydan boshlanmaydi**. Kodni tekshirdim:

| Nima | Qayerda | Holat |
| --- | --- | --- |
| 9 pog'onali unvon zinapoyasi | `profiles/titles.py` | yozilgan |
| Qaror hujjati | `docs/07-adr/0018-titles-roles-achievements.md` | `accepted` (2026-09-11) |
| Chegara mantiqi | `title_for(rating, rated_contests)` | ishlaydi |
| Rang tokenlari | `globals.css` → `--rw-rank-1…9` | 18 palitrada |
| Tarjimalar | `apps/web/src/i18n/locales/*.ts` → `title.<kod>` | 10 til, to'liq |

**Joriy zinapoya (ADR-0018):**

| Pog'ona | Kod | Chegara | UZ | EN |
| --- | --- | --- | --- | --- |
| 1 | `kvark` | < 1200 | Kvark | Quark |
| 2 | `foton` | 1200–1399 | Foton | Photon |
| 3 | `elektron` | 1400–1599 | Elektron | Electron |
| 4 | `proton` | 1600–1799 | Proton | Proton |
| 5 | `atom` | 1800–1999 | Atom | Atom |
| 6 | `molekula` | 2000–2199 | Molekula | Molecule |
| 7 | `kristal` | 2200–2399 | Kristal | Crystal |
| 8 | `yulduz` | 2400–2699 | Yulduz | Star |
| 9 | `galaktika` | 2700+ | Galaktika | Galaxy |

### Joriy tizimning kuchli tomonlari

1. **Miqyos zinapoyasi fikri kuchli** — kichikdan kattaga: zarra → atom → molekula →
   kristal → yulduz → galakti­ka. Bu jismoniy o'sish, mantiqan toza.
2. **Brend bilan bog'liq** — "RankWant" = *rank* (daraja) + *want* (intilish).
   Osmon/galaktika metaforasi "intilish" g'oyasini ko'taradi.
3. **Xalqaro** — hamma so'z ilmiy atama, 10 tilga tabiiy tarjima bo'lgan.

### Joriy tizimning muammolari (o'lchangan)

| № | Muammo | Dalil |
| --- | --- | --- |
| 1 | **10 tilga bir xil "zinapoya" tarjima bo'lmaydi** | Inglizchada `quark → atom → molecule → crystal → star → galaxy` **sakraydi**: zarracha to'g'ridan-to'g'ri atomga, atom molekulaga — oradagi bosqichlar yetishmaydi. Nemis/fransuz/rus tillarida ham xuddi shu uzilish. |
| 2 | **4-pog'ona marosimsiz** | `proton` alohida jism emas — u atomning **qismi**. `kvark → foton → elektron → proton` — uchta har xil kategoriya (kvark = materiya, foton = kuch tashuvchi, elektron/proton = zarra) ketma-ket, ya'ni zinapoya emas, ro'yxat. |
| 3 | **"Molekula" pastroq tuyuladi** | Kattalik bo'yicha `molekula > atom` to'g'ri, lekin **obro'** jihatidan "atom" kuchliroq so'z. O'sish joyida **pasayish** seziladi. |
| 4 | **Uzun so'zlar** | `galaktika` (9), `elektron` (8), `molekula` (8). Ism yonida, jadval qatorida, mobil ekranda tor. |
| 5 | **Katta-kichik harf bilan o'yin yo'q** | "RankWant" nomida **W** katta. Unvonlar oddiy so'z — brend "imzosi" yo'q. |

**Xulosa:** zinapoyani tashlab yuborish kerak emas — uni **to'ldirish va tekislash**
kerak. Quyidagi variantlar shu maqsadda.

---

## 2. Tanlash tamoyillari

Nom faqat "chiroyli" bo'lsa yetmaydi. Quyidagi 8 ta mezon bo'yicha o'lchash mumkin.
Har bir variant 2-bo'limda shu mezonlar bilan baholangan.

| № | Tamoyil | Nima tekshiriladi | Nega muhim |
| --- | --- | --- | --- |
| 1 | **Zinapoya yaxlitligi** | Har pog'ona oldingisidan **mantiqan** kattaroq/kuchliroqmi? Oradan tushib qolgan bosqich bormi? | Odam "keyingi nima?" deb o'ylay olishi kerak — bu motivatsiya |
| 2 | **Talaffuz va qisqalik** | ≤ 3 bo'g'in, ≤ 9 harf; o'zbek, rus, ingliz tilida bir xil o'qiladimi | Ism jadvalda va mobil ekranda turadi |
| 3 | **Unikal­lik (o'z nomi)** | Boshqa OJ (Codeforces, AtCoder, LeetCode, RoboContest, KEP) tizimida bormi? | `Expert`, `Master` kabi umumiy so'zlar esda qolmaydi va SEO'da yutqazadi |
| 4 | **Ijobiy assotsiatsiya** | So'z salbiy yoki kamsituvchi ma'no bermaydimi? Madaniy jihatdan neytralmi? | Past pog'ona so'zi odamni **xafa qilmasligi** kerak — yangi kelgan odam aynan shu yerda turadi |
| 5 | **Tarjima chidamliligi** | 10 tilga ma'no yo'qolmasdan o'tadimi? Transliteratsiya yetarlimi? | RankWant — 10 tilli (ADR-0006, i18n) |
| 6 | **Brend bog'liqligi** | Istiloh, logotipning ikki cho'qqisi, "intilish" g'oyasi bilan bog'lanadimi? | Unvon — brendning eng ko'p ko'rinadigan qismi |
| 7 | **Rang bilan mos** | `--rw-rank-1…9` tokenlarida tabiiy o'qiladimi? | Rang allaqachon tanlangan va kontrast tekshiruvidan o'tgan |
| 8 | **Kengaytirilishi** | Kelajakda 10, 12 pog'ona qo'shilsa sig'adimi? | Reyting tizimi o'sadi |

### ⚠️ 4-moddaga alohida e'tibor: birinchi pog'ona

Past pog'ona nomi eng nozik joy. `Newbie`, `Noob`, `Beginner` — xalqaro OJ larda
odatiy, lekin **"yangi boshlovchi"** so'zi ko'p odamga yoqmaydi. Yaxshisi:
**neytral + o'sish va'dasi**. `Kvark` (joriy) bu jihatdan yaxshi tanlov — kichik
lekin ilmiy, kamsitmaydi.

### Texnik tekshiruv vositasi tayyor

`tools/naming/check_names.py` allaqachon bor — domen (`.uz/.com/.io/.ai`, whois +
RDAP), Telegram, Instagram, Facebook bo'yicha mavjudlikni tekshiradi:

```bash
python check_names.py --json out.json candidates.txt
```

**Nom tanlangach** shu vosita bilan tekshiring — taxmin qilmang.

---

## 3. Variant guruhlari

Yetti mustaqil yo'nalish. Har birida 9 pog'ona (joriy chegaralar o'zgarmaydi:
`1200 / 1400 / 1600 / 1800 / 2000 / 2200 / 2400 / 2700`).

### 🅰 Guruh A — Yulduz spektri

Fizikada yulduzlar **spektral sinf** bo'yicha tasniflanadi: `O B A F G K M`.
Eng issiq va eng yorqin — `O`. Bu **haqiqiy ilmiy zinapoya**, o'sish yo'nalishi
tabiiy, va `M` eng ko'p uchraydigan (ya'ni past) sinf.

| # | Kod | Nom | Chegara | Ma'nosi |
| --- | --- | --- | --- | --- |
| 1 | `m_class` | **M-klass** | < 1200 | Eng sovuq, eng ko'p uchraydigan yulduzlar |
| 2 | `k_class` | **K-klass** | 1200 | To'q sariq mittilar |
| 3 | `g_class` | **G-klass** | 1400 | Quyosh kabi yulduzlar |
| 4 | `f_class` | **F-klass** | 1600 | Oq-sariq |
| 5 | `a_class` | **A-klass** | 1800 | Oq yulduzlar (Sirius) |
| 6 | `b_class` | **B-klass** | 2000 | Ko'k-oq, juda issiq |
| 7 | `o_class` | **O-klass** | 2200 | Eng issiq, eng yorqin |
| 8 | `supernova` | **Supernova** | 2400 | Yulduz portlashi — maksimal yorqinlik |
| 9 | `quasar` | **Kvazar** | 2700 | Olamdagi eng yorqin obyektlar |

- ✅ **Kuchli:** haqiqiy ilm, `O` eng yuqori — tabiiy; hammasi 2 bo'g'in; xalqaro.
- ⚠️ **Kuchsiz:** harflar tasodifiy tuyuladi (kim `F` ni `K` dan yuqori deb biladi?).
  Rang bilan bog'lash qiyin.
- **Brend:** logotip — **qo'sh cho'qqi va yulduz**. Bu guruh uni to'g'ridan-to'g'ri
  davom ettiradi.

### 🅱 Guruh B — Yorug'lik tezligi

Bitta son — `c` — tezlikning mutlaq chegarasi. Fizikadan ma'lum foizlar.

| # | Kod | Nom | Chegarada | Ma'nosi |
| --- | --- | --- | --- | --- |
| 1 | `c1` | **1% c** | < 1200 | Sekin qizish |
| 2 | `c5` | **5% c** | 1200 | |
| 3 | `c10` | **10% c** | 1400 | |
| 4 | `c25` | **25% c** | 1600 | |
| 5 | `c50` | **50% c** | 1800 | Yarim tezlik |
| 6 | `c75` | **75% c** | 2000 | |
| 7 | `c90` | **90% c** | 2200 | |
| 8 | `c99` | **99% c** | 2400 | |
| 9 | `c100` | **c** | 2700 | **Yorug'lik tezligi — yetib bo'lmaydigan cho'qqi** |

- ✅ **Kuchli:** o'sish **ko'zga tashlanadi**; chegara abadiy va tushunarli;
  `c` — xalqaro belgi; "yana 1% qoldi" degan motivatsiya kuchli.
- ⚠️ **Kuchsiz:** nom emas, **raqam**; ism rangi yonida "75% c" g'alati ko'rinishi
  mumkin; kompyuter fanidan boshqa odamga quruq.
- **Brend:** "intilish" (want) g'oyasining eng toza ifodasi.

### 🅲 Guruh C — Toqqa chiqish

RankWant logotipi allaqachon **ikki cho'qqi**. Bu guruh shu tasvirni so'zga aylantiradi.

| # | Kod | Nom | Chegara | Ma'nosi |
| --- | --- | --- | --- | --- |
| 1 | `etak` | **Etak** | < 1200 | Tog' etagi — boshlanish |
| 2 | `oyoq` | **Oyoq** | 1200 | Tog' oyog'i |
| 3 | `qiya` | **Qiya** | 1400 | Ko'tarilish boshlangan |
| 4 | `qoya` | **Qoya** | 1600 | Toshli, tik qism |
| 5 | `tog_` | **Tog'** | 1800 | Haqiqiy balandlik |
| 6 | `qor` | **Qor** | 2000 | Qor chizig'i — yuqori zona |
| 7 | `choqqi` | **Cho'qqi** | 2200 | Tepaga yaqin |
| 8 | `zirva` | **Zirva** | 2400 | Eng baland nuqta |
| 9 | `samolar` | **Samo'alayh** | 2700 | — (pastga qarang) |

- ⚠️ **9-pog'ona muammoli.** "Samo" (osmon) yaxshi, lekin **"Samo'alayh" diniy
  ibora** — ishlatish mumkin emas. Muqobil: **`osmon`** — lekin u juda umumiy.
  Boshqa muqobil: **`cho'qqi`** ni 8-ga, **`zirva`** ni 9-ga surish.
- ✅ **Kuchli:** logotip bilan 1:1 mos; o'zbekcha; **vizual tasvir** (odam tog'ni
  ko'radi); xalqaro (mountain = universal).
- ⚠️ **Kuchsiz:** tarjimasi qiyin (`Zirva` → nega?); `Qor`, `Tog'` juda oddiy.

### 🅳 Guruh D — Fizika miqyosi (joriy tizimning tuzatilgan shakli)

Joriy tizimning g'oyasi saqlanadi, lekin **uzilishlar to'ldiriladi**.

| # | Kod | Nom | Chegara | Nima tuzatildi |
| --- | --- | --- | --- | --- |
| 1 | `kvark` | **Kvark** | < 1200 | ✓ o'zgarmaydi |
| 2 | `foton` | **Foton** | 1200 | ✓ o'zgarmaydi |
| 3 | `elektron` | **Elektron** | 1400 | ✓ o'zgarmaydi |
| 4 | `proton` | **Proton** | 1600 | ✓ o'zgarmaydi |
| 5 | `atom` | **Atom** | 1800 | ✓ o'zgarmaydi |
| 6 | `molekula` | **Molekula** | 2000 | ✓ o'zgarmaydi |
| 7 | `kristal` | **Kristal** | 2200 | ✓ o'zgarmaydi |
| 8 | `yulduz` | **Yulduz** | 2400 | ✓ o'zgarmaydi |
| 9 | `galaktika` | **Galaktika** | 2700 | ✓ o'zgarmaydi |

**Ya'ni D guruhi = hozirgi holat.** Uni "variant" sifatida keltirdim, chunki
taqqoslash uchun asos kerak. Muammolari 1-bo'limda o'lchandi.

- ✅ **Kuchli:** allaqachon kodda va 10 tilga tarjima qilingan — **o'zgartirish narxi 0**.
- ⚠️ **Kuchsiz:** 1-bo'limdagi 5 muammo.

### 🅴 Guruh E — Kosmik zinapoya (joriy tizimning "xalqaro" tuzatishi)

D guruhning muammosi — **inglizchada sakraydi**. Bu guruh oradagi bosqichlarni
to'ldiradi: `quark → atom → molecule → crystal → star → galaxy` o'rniga tekis zanjir.

| # | Kod | Nom | Chegara | EN | Nega |
| --- | --- | --- | --- | --- | --- |
| 1 | `splash` | **Chaqmoq** | < 1200 | Spark | Uchqun — hamma narsa shundan boshlanadi |
| 2 | `foton` | **Foton** | 1200 | Photon | Yorug'lik zarrasi |
| 3 | `gaz` | **Gaz** | 1400 | Gas | Zarrachalar to'plami, shaklsiz |
| 4 | `tuman` | **Tuman** | 1600 | Nebula | Yulduz beshigi |
| 5 | `yulduz` | **Yulduz** | 1800 | Star | Yonadi |
| 6 | `quyosh` | **Quyosh** | 2000 | Sun | Tizim markazi |
| 7 | `oqituvchi` | **Oq yulduz** | 2200 | White Dwarf | Zich, barqaror |
| 8 | `supernova` | **Supernova** | 2400 | Supernova | Portlash — eng yorqin |
| 9 | `galaktika` | **Galaktika** | 2700 | Galaxy | Hammasi birga |

- ✅ **Kuchli:** **haqiqiy o'sish** — uchqun → zarra → gaz → tuman → yulduz →
  quyosh → o'lik yulduz → portlash → galakti­ka. Har pog'ona oldingisidan katta.
- ⚠️ **Kuchsiz:** 7 ta yangi tarjima kerak (narx); `Oq yulduz` 2 so'z.
- **Brend:** logotip osmon bilan bog'liq — mos.

### 🅵 Guruh F — Raqamli zinapoya (eng sodda)

Ilmiy metaforadan **butunlay voz kechish**. Faqat raqam + geometrik shakl.

| # | Kod | Nom | Chegara | Ma'nosi |
| --- | --- | --- | --- | --- |
| 1 | `nuqta` | **Nuqta** | < 1200 | • |
| 2 | `chiziq` | **Chiziq** | 1200 | ─ |
| 3 | `burchak` | **Burchak** | 1400 | ▲ |
| 4 | `kvadrat` | **Kvadrat** | 1600 | ■ |
| 5 | `beshburchak` | **Beshburchak** | 1800 | ⬟ |
| 6 | `olti_burchak` | **Oltiburchak** | 2000 | ⬢ |
| 7 | `yulduz_sh` | **Yulduz** | 2200 | ★ |
| 8 | `halqa` | **Halqa** | 2400 | ◎ |
| 9 | `cheksiz` | **Cheksizlik** | 2700 | ∞ |

- ✅ **Kuchli:** **hamma tushunadi**, tarjima muammosi yo'q; har pog'onaga aniq
  **geometrik belgi** (UI da ikonka bo'ladi!).
- ⚠️ **Kuchsiz:** romantikasi yo'q; `Beshburchak`, `Oltiburchak` — uzun va quruq.
- **Brend:** logotip geometrik — mos, lekin "want" g'oyasi yo'qoladi.

### 🅶 Guruh G — Duragay (tavsiya etiladigan)

**A + E + C** eng kuchli elementlarini birlashtiradi: yulduz spektri mantig'i
+ kosmik o'sish + toqqa chiqish tasviri (logotip).

| # | Kod | Nom | Chegara | Olingan |
| --- | --- | --- | --- | --- |
| 1 | `uchqun` | **Uchqun** | < 1200 | E — neytral, kamsitmaydi, "olov boshlanishi" |
| 2 | `foton` | **Foton** | 1200 | D/E — allaqachon bor |
| 3 | `tuman` | **Tuman** | 1400 | E — yulduz beshigi |
| 4 | `yulduz` | **Yulduz** | 1600 | E — **pastga tushdi** (asosiy yangilik) |
| 5 | `quyosh` | **Quyosh** | 1800 | E — tizim markazi |
| 6 | `supernova` | **Supernova** | 2000 | E — portlash |
| 7 | `qora_tuynuk` | **Qora tuynuk** | 2200 | Yangi — mutlaq kuch |
| 8 | `galaktika` | **Galaktika** | 2400 | D/E — allaqachon bor |
| 9 | `koinot` | **Koinot** | 2700 | Yangi — hamma narsa, eng yuqori |

- ✅ **Kuchli:** to'liq **monoton o'sish**; 3 ta so'z allaqachon tarjima qilingan;
  faqat **5 ta yangi** kalit kerak; `Koinot` — mutlaq cho'qqi, undan yuqorisi yo'q.
- ✅ **Rang bilan:** `Qora tuynuk` — `--rw-rank-7` (#af550b to'q sariq) emas,
  balki 8-pog'onaga (#d5231d qizil) mos. Rangni qayta ko'rish kerak (pastga qarang).
- ⚠️ **Kuchsiz:** `Qora tuynuk` 2 so'z, va ba'zilarga salbiy tuyulishi mumkin
  (yutish). Muqobil: `Pulsar`.
- **Brend:** eng yaxshi mos — "want" = oxirigacha intilish.

---

## 4. Taqqoslash

| Guruh | Yaxlit­lik | Qisqalik | Unikal­lik | Ijobiy | Tarjima | Brend | Rang | Kengaytirish | **Jami** |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 🅰 Yulduz spektri | 5 | 5 | 4 | 5 | 5 | 5 | 3 | 5 | **37** |
| 🅱 Yorug'lik tezligi | 5 | 5 | 5 | 4 | 5 | 5 | 2 | 3 | **34** |
| 🅲 Toqqa chiqish | 4 | 5 | 4 | 4 | 3 | 5 | 4 | 4 | **33** |
| 🅳 Fizika (joriy) | 3 | 3 | 3 | 4 | 4 | 4 | 5 | 4 | **30** |
| 🅴 Kosmik zinapoya | 5 | 4 | 4 | 5 | 3 | 5 | 5 | 5 | **36** |
| 🅵 Raqamli | 4 | 4 | 3 | 5 | 5 | 2 | 5 | 5 | **33** |
| 🅶 **Duragay** | **5** | **5** | **4** | **5** | **4** | **5** | **4** | **5** | **37** |

Baholash: 1–5 (5 = eng yaxshi). "Tarjima" — 10 tilga o'tish qulayligi.

**Xulosa:** 🅰 (37) va 🅶 (37) teng yuqori. Farqi:
- 🅰 **ilmga tayanadi** — lekin harflar (`M`, `K`, `G`…) odamga tasodifiy tuyuladi.
- 🅶 **hikoya aytadi** — lekin 5 ta yangi tarjima kerak.

**Tavsiya: 🅶 Duragay.** Sabab: u **odamga ma'no beradi**, harflar ketma-ketligi
emas. "Men Supernovaman, Galaktikaga intilyapman" — bu motivatsiya.
"Men A-klassman, B-klassga intilyapman" — bu jadval.

---

## 5. Amalga oshirish yo'li (tanlangach)

### O'zgaradigan fayllar

| Fayl | O'zgarish |
| --- | --- |
| `apps/api/profiles/titles.py` | `TITLES` massividagi **kod** nomlari |
| `apps/web/src/i18n/locales/*.ts` (×10) | `title.<kod>` **qiymatlari** |
| `apps/web/src/app/globals.css` | `--rw-rank-*` — agar rang mosligi o'zgarsa |
| `docs/07-adr/0018-*.md` | yangi ADR-00XX sifatida (mavjudni buzmay) |

### ⚠️ Migratsiya talabi (muhim)

`title.galaktika` kabi **kodlar** i18n kaliti. Kod nomi o'zgarsa:
- eski kalitlar **o'chirilishi** kerak (aks holda `check_i18n.py` "ishlatilmagan
  kalit" deb xato beradi),
- 10 tilning **hammasida** bir vaqtda o'zgarishi kerak (`check_locales_parity.py`),
- `RatingChart.tsx` dagi `title.${band.code}` validatsiyasi buzilmasligi kerak.

**Shu sababli:** kod nomlarini saqlab, faqat **tarjima qiymatlarini** almashtirish
**eng arzon yo'l**. Masalan kod `yulduz` qoladi, lekin UZ `Yulduz`, EN `Star` —
ya'ni joriy holat. Agar kodni ham almashtirsangiz — 10 ta fayl + ADR kerak.

### Tekshiruv (majburiy — "yashil natija yolg'on bo'lishi mumkin")

```bash
cd rankwant
python tools/check_i18n.py            # ishlatilmagan kalit yo'q
python tools/check_locales_parity.py  # 10 til teng
python tools/check_contrast.py        # unvon rangi fon ustida 4.5:1
python tools/check_hardcoded.py       # yangi qattiq satr yo'q
```

### Nom mavjudligini tekshirish (agar kod ham almashsa)

```bash
cd rankwant/tools/naming
python check_names.py candidates.txt --json titles.json
```

Tekshiriladi: `.uz .com .io .ai` + `t.me/` + `instagram.com/` + `facebook.com/`.
Barchasi **bir xil bo'sh** bo'lishi kerak.

---

## 6. Qisqa xulosa

1. **Bu bo'sh joydan boshlanmaydi** — ADR-0018, `titles.py` va 10 tilli tarjimalar bor.
2. Joriy tizim **yomon emas**, lekin **10 tilga teng tarjima bo'lmaydi** — bu o'lchangan muammo.
3. **7 guruh** taklif qilindi: 3 ta hikoyali (A/E/G), 2 ta vizual (B/C), 1 ta joriy (D),
   1 ta sodda (F).
4. **Tavsiya: 🅶 Duragay** — hikoya + o'sish + brend mosligi birga.
5. **Eng arzon yo'l:** kod nomlarini saqlash, faqat tarjima qiymatlarini yangilash.
6. **Nom tanlangach** `check_names.py` va 4 ta validator ishlatilishi **shart**.
