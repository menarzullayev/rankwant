# ADR-0002: Qvant iqtisodiyoti — yopiq loop, kosmetik sink

**STATUS:** accepted (2026-09-06) · **amalga oshirildi** Sprint 5 da — scope ataylab tor, kengaytirish = yangi ADR

## Muammo

Qvant qanday topiladi va sarflanadi? Bu shunchaki gamification detali emas: [ADR-0006](0006-rating-model.md) dagi **Activity reyting formulasi** `bajarilgan_quest` ga tayanadi, ya'ni quest ta'rifi aniqlanmasa reyting ham aniqlanmaydi.

## Raqobatchi modellari (ADR talab qilgan solishtirish)

| Jihat        | **KEP — kepcoin**                                                        | **RoboContest — robocoin**                                          |
| ------------ | ------------------------------------------------------------------------ | -------------------------------------------------------------------- |
| Topish       | daily task, daily question/trick/fact (+like), streak                    | quest: `daily`, haftalik, yutuq (7/30/365 kun streak), profil, olimpiada |
| Sarflash     | streak freeze, **yechimni ochish** (`solutionKepcoinValue`), contest yaratish (`purchase-create`) | **obuna chegirmasi** (`coinPrices`, checkout'da)                     |
| Model        | **yopiq loop** — qiymat faqat platforma ichida                           | **pulga bog'langan** — coin obuna narxini tushiradi                  |
| Interfeys    | `/my-kepcoin/`, `/kepcoin-earns/`, `/kepcoin-spends/`                    | `/robocoin` — 3 tab: quest / do'kon / balans o'zgarishlari            |

## Variantlar

1. **KEP uslubi** — yopiq loop, kontent va funksiya ochish
2. **Robo uslubi** — obuna chegirmasi (coin ↔ pul)
3. **Yopiq loop, faqat kosmetik sink** — coin hech qanday mahsulot qiymatini qulflamaydi
4. Minimal — faqat balans + admin grant

## Tanlov

**Variant 3 — yopiq loop, faqat kosmetika va qulaylik.**

## Sabab

Ikkala raqobatchi modelida ham RankWant uchun aniq ziddiyat bor:

- **KEP ning «yechimni ochish» mexanikasi [ADR-0005](0005-content-strategy-own-content.md) ga zid.** O'zbek kontenti bizning differensiatorimiz; o'z editorialimizni Qvant devori ortiga qo'yish o'sha differensiatorni **o'zimiz zaiflashtirish** demak.
- **Robo ning obuna chegirmasi** obuna daromadini to'g'ridan-to'g'ri yeydi va Qvant'ga real pul qiymatini beradi — [02 non-goals](../02-problem-discovery/README.md) dagi chegaraga yaqinlashadi va emissiyani qattiq nazorat qilishni talab qiladi.

Kosmetik sink esa: mahsulot qiymatini kamaytirmaydi, daromadga tegmaydi, regulyatsiya masalasi yo'q — va KEP/Robo ikkalasida ham isbotlangan.

## Earn (manbalar) — Phase 1

| Hodisa                                   | Qvant | Cheklov                          |
| ---------------------------------------- | ----- | -------------------------------- |
| Kunlik quest: kuniga kamida 1 masala¹    | +10   | kuniga 1 marta                   |
| Kunlik quest: kuniga ≥3 AC               | +15   | kuniga 1 marta                   |
| Contest tugatish (rated)                 | +30   | contest boshiga                  |
| Haftalik marafon yakunlash               | +100  | haftada 1 marta                  |
| Streak yutug'i — 7 kun                   | +50   | har 7 kunlik bosqichda           |
| Streak yutug'i — 30 kun                  | +250  | bir marta / davr                 |
| Streak yutug'i — 365 kun                 | +2000 | bir marta / davr                 |
| Profil to'ldirish                        | +50   | **bir marta**, umrbod            |

¹ ADR «kunning masalasi» degan edi. Masala-of-the-day funksiyasi PRD da yo'q,
shuning uchun quest «kuniga kamida bitta masala» sifatida amalga oshirildi.
Kunlik masala qo'shilsa, quest o'sha masalaga bog'lanadi — mukofot va davr o'zgarmaydi.

**Anti-farm qoidalari** (majburiy):

- Faqat **birinchi AC** ball beradi — qayta yechish 0
- Kunlik maksimal emissiya **100 Qvant** (streak yutuqlari bundan tashqari)
- Contest bekor qilinsa yoki rejudge natijasi o'zgarsa — Qvant qaytariladi
- Barcha o'zgarish `QvantTransaction` ledgerida saqlanadi, balans hech qachon to'g'ridan-to'g'ri yozilmaydi

Faol foydalanuvchi taxminan: **~25 Qvant/kun → ~950 Qvant/oy**.

## Spend (sink) — Phase 1 minimal do'kon

| Narsa                    | Narx | Izoh                        |
| ------------------------ | ---- | --------------------------- |
| Streak freeze (1 kun)    | 200  | takroriy, asosiy sink       |
| Avatar ramka             | 500  | bir marta / turi            |
| Profil cover             | 800  | bir marta / turi            |
| Username badge / rang    | 1500 | bir marta / turi            |

## Kengaytirish — ataylab QOLDIRILGAN

Quyidagilar **rad etilmadi**, keyinroq alohida ADR bilan ko'rib chiqiladi:

| Sink                       | Nega hozir emas                                              |
| -------------------------- | ------------------------------------------------------------ |
| Funksiya ochish (virtual contest yaratish, rejudge, filtr) | Bepul rejani sun'iy cheklash xavfi — avval obuna modeli kerak |
| ~~Kontent ochish (yechim/editorial)~~ | **Hal qilindi:** [ADR-0013](0013-editorial-spoiler-gate.md) — spoyler darvozasi, paywall emas |
| Obuna chegirmasi           | Daromadga ta'siri o'lchanmagan; narx modeli hali yo'q        |
| Real pul / USDT konversiyasi | v1 da out of scope; **alohida ADR + huquqiy tahlil** shart   |

## Faza — earn va spend BIRGA

Avvalgi reja earn'ni Phase 1 ga, do'konni Phase 2 ga qo'ygan edi. Bu o'zgartirildi: **sarflab bo'lmaydigan valyuta motivatsiya bermaydi**, aksincha ishonchni yo'qotadi. Minimal do'kon (4 narsa) Phase 1 ga ko'chirildi; Phase 2 do'konni **kengaytiradi** (mavsumiy narsalar).

## Xavf

| Xavf                        | Mitigatsiya                                                       |
| --------------------------- | ----------------------------------------------------------------- |
| **Sink quriydi** — 4 narsa ~3 oyda sotib olinadi | Phase 2 da mavsumiy katalog; streak freeze takroriy sink bo'lib qoladi |
| Emissiya inflyatsiyasi      | Kunlik 100 Qvant limiti + ledger monitoringi                      |
| Quest farming               | Faqat birinchi AC; rejudge da qaytarish                           |

## Oqibatlar

- `04-prd`: P1-5 kengaytirildi, **P1-8 minimal do'kon** qo'shildi; P2-4 «do'kon» → «do'kon kengaytirish»
- `05-domain-model`: `QvantWallet`, `QvantTransaction`, `QvantQuest`, `ShopItem` — Phase 1
- [ADR-0006](0006-rating-model.md) Activity formulasi endi to'liq aniq: `bajarilgan_quest` = yuqoridagi kunlik quest'lar
- Qvant **balansi** reytingga ta'sir qilmaydi (faqat quest soni) — xarid reytingni tushirmaydi

## Bog'liq hujjatlar

- [0005-content-strategy-own-content.md](0005-content-strategy-own-content.md)
- [0006-rating-model.md](0006-rating-model.md)
- [../04-prd/README.md](../04-prd/README.md)
