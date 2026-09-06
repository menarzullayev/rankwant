# 3. Market & Competitor Research

**STATUS:** locked (2026-09-06)

Bozor, raqobatchilar va RankWant positioning.

## Hujjatlar

| Fayl                                           | Mazmun                                      |
| ---------------------------------------------- | ------------------------------------------- |
| [competitor-summary.md](competitor-summary.md) | KEP vs RoboContest vs cp.uz — qisqa jadval  |
| [brand-discovery.md](brand-discovery.md)       | Nom qidiruv, RankWant + Qvant, availability |
| [positioning.md](positioning.md)               | SWOT va differensial                        |

## To'liq tahlillar (workspace root)

- [kep-uz-platform-analysis.md](../../../kep-uz-platform-analysis.md) — 102 REST endpoint, kepcoin, Aurora
- [robocontest-uz-platform-analysis.md](../../../robocontest-uz-platform-analysis.md) — ~197k user, Laravel+Inertia, robocoin
- cp.uz — [../../../cp-uz/](../../../cp-uz/) repo (learning, articles, seasons; OJ yo'q)

## Bozor xulosa (2026-09-06)

| Platform        | Kuch                                  | Zaif                    |
| --------------- | ------------------------------------- | ----------------------- |
| **RoboContest** | Eng katta jamoa, judge, obuna, mirror | Yopiq API               |
| **KEP**         | Ochiq API, gamification, kepcoin      | Kichikroq scale, Aurora |
| **cp.uz**       | O'zbek kontent, roadmap               | OJ/contest yo'q         |

**RankWant imkoniyati:** cp.uz darajasidagi o'qish chuqurligini **o'zimiz qurish** + RoboContest/KEP judge/contest + ochiq API + **RankWant/Qvant** brendi.

## Bozor hajmi

> ⚠️ Bu **kuzatilgan raqobatchi raqamlaridan chiqarilgan taxmin**, rasmiy statistika emas. Taxmin qilingan koeffitsientlar ochiq yozilgan — noto'g'ri chiqsa, qayta hisoblash oson.

**Kuzatilgan asos:** RoboContest ~197k ro'yxatdan o'tgan · KEP ~9k. RoboContest 10+ yil ichida shu darajaga yetgan va bozorda dominant — ya'ni bu O'zbekiston CP/informatika auditoriyasining **amalda ko'rsatilgan shifti**, nazariy TAM emas.

| Daraja  | Ta'rif                                                        | Taxmin      |
| ------- | ------------------------------------------------------------- | ----------- |
| **TAM** | O'zbekistonda CP/olimpiada bilan qiziqqan, ro'yxatdan o'tishga tayyor auditoriya | ~200–250k   |
| **SAM** | RankWant taklifi mos keladigan segment: chuqur o'zbek kontenti + OJ istaganlar, maktab B2B | ~40–70k     |
| **SOM** | 3 yilda realistik ulush (TAM ning ~10%)                       | ~20–25k     |

**North Star ga o'tkazish.** Ro'yxatdan o'tgan ≠ faol. OJ platformalarida haftalik faol ulush odatda **5–10%** (taxmin). Shu koeffitsient bilan:

| Yil | Ro'yxatdan o'tgan | Haftalik faol yechuvchi (North Star) |
| --- | ----------------- | ------------------------------------ |
| 1   | ~5k               | ~300–500                             |
| 2   | ~12k              | ~700–1 200                           |
| 3   | ~20–25k           | ~1 500–2 500                         |

**Nima uchun RoboContest ulushini olish emas.** 197k network effekti bilan to'g'ridan-to'g'ri raqobat 0 userli platforma uchun yutuqsiz. SAM ataylab tor: **o'zbek o'qish kontenti + OJ bir joyda** (hech kim bermayapti) va **maktab B2B** (Robo Judge rejasi isbotlagan, lekin to'yinmagan).

## Qulflash

2026-09-06: raqobatchi tahlili, brend (RankWant + Qvant), positioning va **bozor hajmi** tasdiqlandi.
Bog'liq qarorlar: [ADR-0003](../07-adr/0003-stack-django-next.md) stack · [ADR-0005](../07-adr/0005-content-strategy-own-content.md) kontent · [ADR-0006](../07-adr/0006-rating-model.md) reyting.
O'zgartirish = yangi ADR (`docs/07-adr/`).

## Keyingi qadam

`04-prd` lock → keyin `05-domain-model` va `08-technical-spec`.
