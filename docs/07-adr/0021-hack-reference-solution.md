# ADR-0021: Hack testining javobi — masalaning etalon yechimidan

**STATUS:** accepted (2026-09-16)
**Ta'siri:** [ADR-0020](0020-hacking.md) ni to'ldiradi;
[05-domain-model](../05-domain-model/README.md) 🔒 ga `ReferenceSolution` qo'shiladi

## Muammo

[ADR-0020](0020-hacking.md) hack dvigatelini tasdiqladi, lekin bitta bo'shliqni
ochiq qoldirdi: hacker yuborgan test uchun **to'g'ri javobni kim beradi?**

Oqim shunday: hacker kiritma yuboradi → validator uni tekshiradi → himoyachining
yechimi o'sha kiritmada ishga tushadi → chiqish **nimadir bilan** solishtiriladi.
O'sha «nimadir» — kutilgan javob — hozir yo'q: `TestCase` javoblari muallif
tomonidan oldindan tayyorlangan, hack testi esa yangi.

## Variantlar

1. **Hackerning o'z `AC` yechimi etalon bo'ladi.** Tekin: ADR-0020 ning
   2-tamoyili hackerdan o'sha masalani yechgan bo'lishni allaqachon talab
   qiladi, ya'ni «to'g'ri» deb hisoblangan kod bor.
2. **Masalaga etalon yechim qo'shiladi** — `ReferenceSolution`, `Validator`
   kabi majburiy darvoza.
3. **Checker javobsiz hal qiladi** — chiqishning o'zini tekshiradigan
   `special` checker.

## Tanlov

**2-variant — `ReferenceSolution`.** Hacking faqat `Validator` ham, etalon
yechim ham mavjud masalalarda ochiladi.

## Sabab

- **1-variant hujum yuzasini ochadi.** Hacker ataylab chekka holatda xato
  ishlaydigan yechim yuboradi, u testlardan o'tib `AC` oladi; keyin aynan
  o'sha chekka holatni hack testi qilib yuboradi. Etalon uning yechimi
  bo'lgani uchun «to'g'ri javob» xato bo'ladi va **to'g'ri ishlaydigan**
  himoyachi `HACKED` oladi. Hack tizimi o'zi qurolga aylanadi — bu
  ADR-0020 dagi «noto'g'ri test arzon, muvaffaqiyatsiz hack qimmat»
  rag'bat shaklining aynan teskarisi.
- **3-variant faqat kichik qismni qoplaydi.** Masalalarning ko'pchiligi
  `standard` checker bilan ishlaydi va u javobsiz hech narsa ayta olmaydi.
- **Sanoat amaliyoti shunday.** Polygon va Codeforces hack testini muallif
  yechimida yurgizib javob oladi.
- **Yangi tushuncha kirmaydi.** Shakli `Validator` bilan bir xil: model bor,
  staff yuklaydi, judge ishlatadi.

## Oqibatlar

- `problems.ReferenceSolution` qo'shiladi: `problem` (OneToOne), `language`,
  `source`, `updated_at` — `Validator` bilan bir xil naqsh, staff API va
  admin orqali boshqariladi.
- **Hack darvozasi ikkita:** masalada validator yoki etalon yechim bo'lmasa,
  hack so'rovi `400` va sababni qaytaradi. Jimgina o'chirilgan funksiya emas —
  ko'rinadigan holat.
- Etalon yechim **sandbox ichida** ishlaydi: kod bizniki, lekin kiritma
  ishonchsiz — validator bosqichi bilan bir xil sabab
  ([protocol.md](../../services/bakeoff/protocol.md) § «Kirish validatori»).
- Etalon yechim `TLE`, `RE` yoki `IE` bersa, hack **jazolanmaydi** va
  `IGNORED` bo'ladi: bu masala sozlamasining nuqsoni, hackerning aybi emas.
  Bunday holat staff uchun alert chiqaradi — aks holda masala jimgina
  «hack qilib bo'lmaydigan» bo'lib qolardi.
- KEP importi etalon yechimni olib kelmaydi (ochiq API'da yo'q), ya'ni
  import qilingan masalalarda hacking staff yechim yuklagunicha yopiq
  qoladi. Bu ataylab: yopiq holat noto'g'ri `HACKED` dan yaxshi.
