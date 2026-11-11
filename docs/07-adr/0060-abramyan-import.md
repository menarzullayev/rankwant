# ADR 0060 — Abramyan importi: norasmiy masalalar, haqiqiy son solishtiruvi, til ustamasi, o'quv rejasi

**STATUS:** accepted
**Sana:** 2026-11-11
**Tasdiqlagan:** Saidakbar (owner) — 2026-11-11 ([qaror yozuvi](../decisions/2026-11-11-abramyan-import.md): 3 raund, 11 savol; [kontent qarori](../decisions/2026-11-11-content-and-archive.md): muallif ruxsati, norasmiy daraja, bepul o'quv rejasi)
**Ta'sir doirasi:** judge (`services/judge-go`, protokol), `problems` (`Problem`, `Language`), reyting va Qvant hisobi, arxiv ro'yxati, `content.Roadmap`, yangi import buyrug'i
**Dalil:** eksport paketi `D:\Linux\coding\abramyan-export\package\` (2026-11-11 o'lchandi): 1 100 masala, 19 bo'lim, 4 til (uz, ru, en, qq), 21 836 test (5.7 MB, eng katta fayl 4.1 KB), har masalaga Python namuna yechim; checker — aniq solishtiruv 742, haqiqiy son (ε = 1e-6) 358; File va Text bo'limlari — 150 masala; vaqt 1 000 ms, xotira 32 000 KB

## 1. Muammo

Platforma bu paketni bugun to'g'ri qabul qila olmaydi (kod va jonli baza o'lchandi):

1. **Judge'da haqiqiy son solishtiruvi yo'q.** Faqat aniq solishtiruv (`classify`) va muallif
   checker dasturi (`special`) bor. 358 masalaning javobi kasr son: `2.0` va `2` ni aniq solishtiruv
   rad etadi. Har masalaga bitta checker dasturini nusxalash 358 marta kompilyatsiya qilinadigan
   bir xil kod bo'lardi. Bundan tashqari `io_mode=both` va `special` birikmasi rad etiladi, chunki
   checker `output.txt` ni ko'rmaydi. Shu sababli File va Text bo'limlarining 33 masalasi umuman
   yo'lga qo'yilmasdi.
2. **Tilga xos xotira hisobga olinmaydi.** Ish chegarasi masala chegarasiga teng
   (`judging/services.py`). Til bo'yicha ustama faqat `ProblemLanguage` qatori bilan beriladi. Lekin
   har qanday `ProblemLanguage` qatori masalani shu tillar ro'yxatiga yopadi: ustama berish uchun har
   masalaga barcha 35 tilga qator yozish kerak bo'lardi.
3. **Norasmiy daraja yo'q.** Har nashr qilingan masala bir xil hisoblanadi: arxivda, yechilganlar
   sonida, reytingda va Qvant'da. 1 100 ta boshlang'ich masala arxiv statistikasini suyultirardi.
   Bundan tashqari har biri ommaviy raqam olardi.
4. **O'quv rejasi uchun tuzilma yo'q.** `content.Roadmap` da bo'lim, tarjima va alohida sahifa yo'q.
   `locale` ning `max_length` qiymati 2, ya'ni `kaa` sig'maydi.
5. **Nashr darvozasidan import o'ta olmaydi.** `checker_verified_at` va `LimitCalibration` import
   yo'lida yozilmaydi. KEP importi ham `save()` orqali nashr qiladi.

## 2. Qaror

### 2.1 Haqiqiy son solishtiruvi judge ichida

- Yangi tur `checker_type = "real"`. Bu dastur emas: judge uni ichida bajaradi.
- Bir masalaga bitta qiymat `Problem.real_tolerance` beriladi, standart `1e-6` (Robocontest
  checkeri bilan bir xil).
- Javob tokenlarga bo'linadi, tokenlar soni teng bo'lishi shart.
- Kutilgan token chekli son bo'lsa, yechim tokeni ham chekli son bo'lishi va
  `|y − x| ≤ ε · max(1, |x|)` shartini bajarishi kerak. Bu yerda `x` — hakam javobi.
- Boshqa tokenlar aniq solishtiriladi: Robocontest checkeri bunday tokenni rad etardi, bizda u matn
  sifatida tekshiriladi.
- `nan`, `inf` va o'n oltilik yozuv son hisoblanmaydi.
- Fayl rejimida (`both`, `file`) `output.txt` ham shu qoida bilan tekshiriladi. Shu sababli `real`
  va `both` birikmasi ruxsat etiladi.
- Bu tur `answer`, interaktiv va `scorer` bilan birikmaydi (saqlashda, tayyorlikda va nashr
  darvozasida rad etiladi).
- **Protokol:** eski judge noma'lum turni aniq solishtiruvga jimgina tushirib, to'g'ri javobga WA
  berardi. Shuning uchun `real` ishlatadigan ish protokolning keyingi versiyasini oladi va eski judge
  uni `IE` bilan rad etadi. Qolgan ishlar o'zgarmaydi.

### 2.2 Tilning xotira ustamasi — platforma darajasida

- `Language.memory_overhead_kb` maydoni qo'shiladi. Uning qiymati judge obrazida bo'sh dasturning
  o'lchangan eng katta xotirasidan (`PeakKB`) olinadi.
- Ishning chegarasi: masala chegarasi + til ustamasi.
- Ustama **barcha masalalarga** qo'shiladi, ya'ni chegaralarni faqat yumshatadi: hech kim yangi MLE
  olmaydi.
- `ProblemLanguage.memory_limit_kb` berilgan bo'lsa, ustama qo'shilmaydi: muallif shu tilning aniq
  chegarasini o'zi aytgan.
- Masala sahifasida masala chegarasi ko'rsatiladi. Til ustamasi yuborish panelida tanlangan til
  bilan birga ko'rsatiladi.
- **O'lchandi (2026-11-11)** — [yozuv](../research/2026-11-11-language-memory-overhead/README.md):
  35 til, 35 tadan yurish, p95 butun MB'ga yaxlitlangan (Julia 117, R 44, Scala 35, Java 21,
  Python 5, C++ 2). O'lchov judge'ning nuqsonini ochdi: MLE `memory.peak >= chegara` bilan
  berilardi, `memory.peak` esa sahifa keshini ham sanaydi. Endi MLE faqat kernel dasturni
  xotira uchun o'ldirganda (`oom_kill`) beriladi.

### 2.3 Norasmiy masalalar

- `Problem.is_official` maydoni qo'shiladi, standart qiymati `True`: mavjud masalalar o'zgarmaydi.
- Norasmiy masalaga **ommaviy raqam berilmaydi** (`code` bo'sh qoladi). Uning manzili va
  identifikatori — slug, ya'ni kitob kodi (`/problems/begin1`).
- Xodim masalani rasmiyga o'tkazganda unga keyingi raqam beriladi.
- Norasmiy masala yechilganda hisoblanadi: «yechildi» belgisi, o'quv rejasi progressi, seriya va
  faollik xaritasi.
- Hisoblanmaydi: reyting, Qvant, umumiy «yechilganlar» soni (profil maxraji ham), platforma sonlari
  va arxiv statistikasi.
- Arxivning standart ro'yxatida norasmiy masalalar ko'rinmaydi, ular filtr bilan ochiladi.
- Sayt qidiruvi ularni topadi: sarlavhada kitob kodi bor.
- Judge yaratgan ochiq masalalar ham shu darajada bo'ladi ([kontent qarori](../decisions/2026-11-11-content-and-archive.md) ⑤).
- **Amalga oshirishda aniqlangan chegaralar (2026-11-11):**
  - Seriya hisoblanadi, lekin norasmiy yechim bosqich mukofotini (7/30/365 kunlik Qvant)
    **to'lamaydi** (`streak.touch(reward=False)`). O'sha kuni keyinroq kelgan rasmiy yechim
    mukofotni oladi: mukofotlar kalit bilan yoziladi, qayta so'rash xavfsiz.
  - Activity reytingining «faol kun» qismi norasmiy urinishlarni sanamaydi. Uning seriya
    qismi esa seriyaning o'zi, ya'ni norasmiy kunlar u orqali bilvosita kiradi.
  - Kunlik kvestlar, marafon, yutuqlar, duel to'plami, tavsiyalar, «o'xshash masalalar»,
    mavzu sonlari va arxiv progressi faqat rasmiy masalalarni sanaydi.
  - Sitemap norasmiy sahifalarni ham oladi: ular ochiq sahifalar (`?tier=all`).
  - Arxiv ro'yxati `?tier=official` (standart), `unofficial` yoki `all` bo'ladi.

### 2.4 O'quv rejasi — `Roadmap` kengayadi

- Bo'limlar qo'shiladi: `RoadmapSection` (tartib, nom, tavsif) va `RoadmapStep.section`.
- Reja va bo'lim nomi hamda tavsifi sayt tillarida yoziladi. `locale` 3 belgigacha kengayadi
  (`kaa` sig'adi).
- Har reja o'z sahifasini oladi: bo'limlar, qadamlar, foydalanuvchi progressi va keyingi qadam
  ko'rsatiladi.
- Abramyan rejasi bitta: 19 bo'lim, 1 100 masala qadami. U **hammaga bepul**. Yon menyu o'zgarmaydi
  (21 band, 5 guruh), reja Traektoriya ichida turadi.

### 2.5 Import buyrug'i

`import_abramyan` buyrug'i manifestni o'qiydi va qoralama yozadi. U idempotent: slug bo'yicha
yangilaydi, ikkinchi yurish yangi qator yaratmaydi.

- **Matn:** asosiy til `uz`. `ru`, `en` va `kaa` (paketda `qq`) — `ProblemTranslation` qatorlari
  ([ADR-0058](0058-problem-translations.md)).
- **HTML → Markdown:** `<span class="math-tex">\( … \)</span>` ifodasi `$…$` ga aylanadi. Integer29
  rasmi o'z omborimizga ko'chiriladi, chunki tashqi havola yo'qolishi mumkin.
- **Sarlavha va slug:** sarlavha «Begin1. Kvadrat perimetri» shaklida, slug esa `begin1`.
- **Chegaralar:** vaqt 1 000 ms, xotira 64 MB va § 2.2 dagi til ustamasi.
- **Checker:** paketdagi `exact` → `standard`, `real_eps_1e-6` → `real` (§ 2.1).
- **Testlar va namunalar:** testlar o'zgarmaydi, namunalar `examples` dan olinadi.
- **Mavzular:** har bo'lim mavjud mavzularga bog'lanadi.
- **Qiyinlik:** agentning bahosi (800–3 500, qadami 100). Asosi bo'lim darajasi, unga namuna
  yechimning murakkabligi qo'shiladi. Egasi qiymatni keyin tuzatadi.
- **Manba va muallif:** manba — M. E. Abramyan, «Programming Taskbook» (muallif ruxsati bor).
  Muallif — egasining hisobi.
- **Tillar:** barcha faol tillar ochiq.
- **File va Text bo'limlari (150 masala):**
  - `io_mode=both` qilinadi.
  - Shartdagi moslashtirish gapi har tilda almashtiriladi: «komponentlar kirishda beriladi» o'rniga
    «`input.txt` faylida beriladi, natija `output.txt` ga yoziladi».
  - Namuna yechimlar fayl bilan qayta yoziladi, testlar o'zgarmaydi.
  - Egasi 150 × 4 matnning hammasini ko'radi.

### 2.6 Tekshiruv va nashr

- **Tekshiruv production judge'da, tunda o'tkaziladi** (egasi qarori). Har masalaning namuna yechimi
  haqiqiy checker bilan yuboriladi: hammasi `AC` bo'lishi shart.
- Har masalaga bitta salbiy yuborish ham boriladi: bo'sh chiqish `AC` olmasligi kerak, ya'ni testlar
  bo'sh javobni o'tkazib yubormaydi.
- Paketni tayyorlagan skript (`verify_local.py`) `1e-5` bilan solishtirgan, haqiqiy checker esa
  `1e-6` ishlatadi. Shu farq tufayli 358 masalaning tekshiruvi qayta o'tkazilishi shart.
- Bu tekshiruv nashr darvozasi (`checker_verified_at`, `LimitCalibration`) o'rnini bosadi va
  hisoboti `docs/research/` ga yoziladi.
- **Nashr:** 1 100 masala birga, agentning qiyinlik bahosi bilan nashr qilinadi. Ikki shart bor:
  tekshiruv yashil bo'lishi va egasi 150 × 4 matnni ko'rgan bo'lishi.

## 3. Oqibatlar

- `docs/05` (locked) dagi `Problem` ikki maydon oladi: `is_official` va `real_tolerance`.
  `Language` bitta maydon oladi: `memory_overhead_kb`. Bu ADR shu o'zgarishning asosi.
- Til ustamasi mavjud masalalarda ham Java, C# va boshqa runtime'li tillarga xotirani ko'paytiradi.
  Chegara qattiqlashmaydi.
- Profildagi «yechilganlar» soni va reyting Abramyan masalalarini sanamaydi. Seriya va faollik
  xaritasi ularni sanaydi: kichik masala bilan ham seriya uzilmaydi (egasi tanladi).
- Tekshiruv tunda production judge'da ~22 000 test yurishini oladi. Shu vaqt ichida foydalanuvchi
  yuborishlari navbatda kutadi.
- Qiyinlik baholari egasi ko'rmasdan nashr qilinadi. Keyin tuzatilsa, filtr va saralash natijalari
  siljiydi.

## 4. Rad etilgan variantlar

- Har bir masalaga checker dasturini nusxalash: 358 ta bir xil dastur bo'lardi va `both` bilan
  birikmasdi.
- Ustamani faqat Abramyan masalalariga `ProblemLanguage` qatorlari bilan berish: 38 500 qator
  kerak bo'lardi, yangi til qo'shilganda u hamma masalada yopiq qolardi.
- Norasmiy masalalarga umumiy ketma-ketlikdan raqam berish: rasmiy arxiv raqamlarida 1 100 talik
  bo'shliq paydo bo'lardi.
- Tekshiruvni alohida stack'da yoki CI'da o'tkazish (CTO tavsiyasi edi): egasi production judge'ni
  tanladi.

## 5. Bosqichlar (alohida PR'lar)

1. Judge: `real` solishtiruvi, protokol, bake-off holati va API tomoni (§ 2.1).
2. Tillarning xotira ustamasi: o'lchov va `Language.memory_overhead_kb` (§ 2.2).
3. Norasmiy daraja (§ 2.3).
4. O'quv rejasi: bo'limlar, tarjimalar, sahifa va progress (§ 2.4).
5. `import_abramyan`: File va Text matnlari, yechimlar, qiyinlik va mavzular (§ 2.5). Masalalar
   qoralama sifatida yoziladi.
6. Tunda production judge'da tekshiruv va egasining 150 × 4 ko'rigi, keyin hammasi birga nashr
   qilinadi (§ 2.6).
