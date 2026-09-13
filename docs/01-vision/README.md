# 1. Vision

**STATUS:** locked (2026-09-06)  
**Platforma:** RankWant  
**Valyuta:** Qvant

## Mission

Sport dasturlash va informatika olimpiadasi iqtidorini **reyting, musobaqa va o'qish** orqali o'stirish — O'zbekiston va global auditoriya uchun zamonaviy CP platformasi.

## Vision

**RankWant** — reyting xohlaganlar uchun joy: masala yechish, musobaqada qatnashish, o'z darajasini ko'rish va yuqoriga chiqish.

**Qvant** — platforma ichidagi mukofot va iqtisodiyot tilida qisqa, esda qolarli birlik (KEP → kepcoin, RoboContest → robocoin analogiyasi, lekin alohida brend).

## Kim uchun

| Segment                     | Nima uchun RankWant                                                  |
| --------------------------- | -------------------------------------------------------------------- |
| **O'rta maktab o'quvchisi** | DTM/informatika va olimpiada tayyorgarlik, reyting, virtual musobaqa |
| **Universitet talabasi**    | ICPC, sport CP, jamoa, ochiq arxiv                                   |
| **O'qituvchi / murabbiy**   | Sinf, uy vazifasi masalalari, progress (keyingi fazalar)             |
| **Mustaqil o'rganuvchi**    | Masala banki, custom test, streak va Qvant mukofotlari               |
| **Tashkilot**               | Mirror musobaqa va rasmiy olimpiada infratuzilmasi (keyingi fazalar) |

Birinchi to'lqin: **O'zbekiston** CP/olimpiada iqtidorlari. Nom va UI global; kontent va mirror — mahalliy kuch.

## Nima qiladi

RankWant — **online judge + musobaqa + reyting** platformasi:

- Masalani o'qish, kod yuborish, verdict olish (AC/WA/TLE…)
- Live va virtual contest (ACM/ICPC uslubi)
- Foydalanuvchi profili va reyting — qanday ball olinganini ko'rish
- **Qvant** — vazifa, streak va do'kon orqali retention (boshlang'ich fazadan keyin)
- Kelajakda: o'z o'qish kontenti (maqola, roadmap), o'qituvchi sinfi, ochiq API

**Emas:** faqat statistika agregator (CoderSTAT), yoki KEP/Robo UI nusxasi. **cp.uz** — alohida loyiha; RankWant unga bog'liq emas.

## Tagline

| Til | Platforma                                      | Qvant (coin)                              |
| --- | ---------------------------------------------- | ----------------------------------------- |
| uz  | RankWant — reyting xohlaganlar uchun           | Qvant toping. Reytingda ko'taring.        |
| ru  | RankWant — для тех, кому нужен рейтинг         | Зарабатывай Qvant. Поднимайся в рейтинге. |
| en  | RankWant — where drive for rank meets practice | Earn Qvant. Climb the ranks.              |

## Long-term goals

1. **To'liq OJ** — ko'p tilli judge, contest, virtual/mirror musobaqalar (RoboContest/KEP darajasi).
2. **O'zbek kontent ustunligi** — o'z maqola, mavzu roadmap va masala izohlari (o'zbek tilida chuqur o'qish + yechish bir joyda).
3. **O'qituvchi/B2B** — sinflar, maktab/universitet judge rejasi.
4. **Qvant iqtisodiyoti** — retention + monetizatsiya (obuna, do'kon, quest); real pul sovrinlari — ehtiyotkor, keyinroq ADR.
5. **Ochiq API** — mobile va uchinchi tomon integratsiyasi (KEP REST yo'li yoki hibrid).

## Product principles

1. **Clone emas, benchmark** — raqobatchilardan pattern o'rganish, o'z engine va UX.
2. **Reyting aniq** — foydalanuvchi qanday ball olganini tushunadi (yashirin algoritm emas).
3. **O'zbek + global** — UI til, masala va kontent; nomlar global eshitiladi.
4. **Brend ikkiligi** — platforma (RankWant) va coin (Qvant) alohida, lekin bir hikoya.
5. **Fazali MVP** — judge + contest + user avval; gamification va shop keyin.
6. **Huquqiy xavfsizlik** — Aurora/KEP kodini nusxalamaslik; DMOJ/custom yoki litsenziyali engine.

## Brend qisqacha

| Element     | Qiymat                                                                 |
| ----------- | ---------------------------------------------------------------------- |
| Asosiy nom  | RankWant                                                               |
| O'qilish    | «Rank Want» — reyting xohlayman                                        |
| Coin        | Qvant (5 harf, kvant/quant/STEM nuansi)                                |
| Rad etilgan | `rankwantcoin`, `@olympiq`, juda mahalliy nomlar (SolveUz, YechLab, …) |

**Brend risklari (kuzatish):** `@qvant` Telegram band — rasmiy handle `@qvantcoin`. Tashqi nomlar **Kvants** (crypto/gamification) va **Kuant** (DeFi) fonetik yaqin; CP kontekstida «Qvant» + «RankWant» juftligi farqlaydi. `qvant.com` band; `.uz` / `qvantcoin.*` hozircha bo'sh (2026-09-06).

Batafsil: [../03-market-research/brand-discovery.md](../03-market-research/brand-discovery.md)

## Muvaffaqiyat metrikalari (vision darajasi)

- DAU/MAU va kunlik submit soni
- Contest qatnashuv va tugatish foizi
- Maktab/universitet sinflari (B2B)
- Qvant aylanmasi (retention signal)
- Masala arxivi o'sishi (o'zbek + xalqaro)

## Strategic assumptions

Matnda yozilgan, lekin taxmin sifatida belgilanmagan da'volar. Har biri
tekshirilishi mumkin — tekshirilgach shu ro'yxatdan chiqadi.

1. **Birinchi bozor — O'zbekiston.** *"Birinchi to'lqin: O'zbekiston CP/olimpiada iqtidorlari"* — ya'ni mahalliy auditoriya yetarli hajmda va mahsulot shundan boshlanadi. **Tekshirish:** 03 dagi bozor hajmi.
2. **Nom global, kontent mahalliy.** *"Nom va UI global; kontent va mirror — mahalliy kuch"* — ya'ni o'zbek tilidagi kontent raqobat ustunligi bo'ladi.
3. **RankWant + Qvant juftligi farqlanadi.** Brend risklari bo'limi fonetik yaqin nomlarni sanaydi (Kvants, Kuant) — ya'ni chalkashlik **bo'lmaydi** degan taxmin.
4. **Beshta segment bitta mahsulot bilan qondiriladi.** `Kim uchun` jadvalidagi 5 segment Phase 0 da bir xil funksiyalar bilan xizmat qilinadi.
5. **O'zbek kontenti yetarli hajmda yoziladi.** Goal #2 (o'z maqola + roadmap) resurs talab qiladi — kim yozishi taxmin qilingan, lekin yozilmagan.

## Open questions

1. **Domen va handle.** *"`qvant.com` band; `.uz` / `qvantcoin.*` hozircha bo'sh (2026-09-06)"*, `@qvant` Telegram band → rasmiy handle `@qvantcoin`. Qaysi domen olinadi va qachon? Hozircha ochiq.
2. **Asosiy segment qaysi?** 5 segment teng sanalgan. Vision "birinchi to'lqin" ni aytadi, lekin bitta segmentni **asosiy** deb belgilamaydi (02 da ham bir xil bo'shliq).
3. **B2B qachon?** O'qituvchi/maktab "keyingi fazalar" deb belgilangan — aniq faza yo'q.
4. **Real pul sovrinlari.** *"ehtiyotkor, keyinroq ADR"* deyilgan — yo'nalish hali yo'q.

## Qulflash

**Tasdiq:** Saidakbar Narzullayev — Repo owner / maintainer, 2026-09-06.

2026-09-06: **RankWant + Qvant** tasdiqlandi. Platforma motivatsion brend; coin alohida va qisqa. O'zgartirish = yangi ADR (`docs/07-adr/`).

**Lock kuni aniqlashtirilgan qarorlar** (vision matni o'zgarmadi, sabab hujjatlashtirildi):

- Kontent strategiyasi — [ADR-0005](../07-adr/0005-content-strategy-own-content.md): cp.uz bog'liqlik emas, o'z kontent (goal #2)
- Reyting modeli — [ADR-0006](../07-adr/0006-rating-model.md): 4 reyting, fazali ochilish (principle #2, #5)

**Keyingi bosqich:** `02-problem-discovery` 🔒 → `03-market-research` → `04-prd` MVP scope.
