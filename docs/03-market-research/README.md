# 3. Market & Competitor Research

**STATUS:** locked (2026-09-06)

Bozor, raqobatchilar va RankWant positioning.

## Hujjatlar

| Fayl                                           | Mazmun                                      |
| ---------------------------------------------- | ------------------------------------------- |
| [competitor-summary.md](competitor-summary.md) | KEP vs RoboContest vs cp.uz — qisqa jadval  |
| [brand-discovery.md](brand-discovery.md)       | Nom qidiruv, RankWant + Qvant, availability |
| [verdicts.md](verdicts.md)                     | Verdikt turlari — bizda, raqobatchilarda, takliflar |
| [positioning.md](positioning.md)               | SWOT va differensial                        |

## To'liq tahlillar — ⚠️ repo'da YO'Q, Linux bo'limida qolgan

Bu ikki fayl **Linux o'rnatilmasida** (`/home/nsn/project/cp/` atrofida —
`INDEX.md` dagi `/home/nsn/...` yo'llariga qarang), Windows nusxasida emas.

Windows'da qidirildi va **topilmadi**: workspace (chuqurlik cheklovisiz),
`C:\Users\nsn` (depth 7), `C:\` (depth 5), Desktop/Downloads/Documents/OneDrive,
`project.zip`. Handoff eksporti ham ularni olmaydi — u faqat `pg.sql.gz` va
`minio.tar.gz` ni tashiydi.

- `kep-uz-platform-analysis.md` — 102 REST endpoint, kepcoin, Aurora
- `robocontest-uz-platform-analysis.md` — ~197k user, Laravel+Inertia, robocoin
- cp.uz — `cp-uz/` repo (learning, articles, seasons; OJ yo'q)

⚠️ **Quyidagi bozor hajmi raqamlari shu ikki faylga tayanadi va hozir
TEKSHIRIB BO'LMAYDI.** Fayllar Linux'dan ko'chirilgach qayta tekshiriladi.

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

## Assumptions

Bozor hajmi bo'limi o'zi ogohlantiradi (*"kuzatilgan raqobatchi raqamlaridan
chiqarilgan taxmin, rasmiy statistika emas"*) — bu quyidagilar shu taxminning
tarkibiy qismlari.

1. **TAM ≈ 200–250k.** RoboContest'ning `~197k` ro'yxatdan o'tgan soni
   *"O'zbekiston CP/informatika auditoriyasining amalda ko'rsatilgan shifti"*
   deb olinadi. Ya'ni **bir raqobatchining 10+ yildagi natijasi = bozor shifti**
   degan taxmin.
2. **Haftalik faol ulush 5–10%.** North Star prognozi shu koeffitsientga
   tayanadi (`1-yil ~300–500`, `3-yil ~1 500–2 500`).
3. **Maktab B2B to'yinmagan.** *"Robo Judge rejasi isbotlagan, lekin
   to'yinmagan"* — ya'ni talab bor, lekin raqobatchi uni qondirmagan.
4. **Raqamlar manbasi repo'dan tashqarida.** `~197k`, `~9k`, `102 endpoint`,
   `1477 masala` — hammasi `kep-uz-platform-analysis.md` va
   `robocontest-uz-platform-analysis.md` dan, va **bu fayllar repo'da yo'q**.

## Open questions

1. **Ikki tahlil fayli repo'ga ko'chiriladimi?** Hozir butun bozor hajmi
   repo ichidan **tekshirib bo'lmaydi**. Bu eng muhim ochiq savol.
2. **`Substitutes` tahlili yo'q.** Global platformalar (`Codeforces`,
   `AtCoder`) `verdicts.md` da faqat verdikt kodlari uchun uchraydi. O'zbek
   o'quvchisi uchun eng katta o'rinbosar — Codeforces (bepul, global reyting).
   Offline repetitor va maktab to'garagi ham tahlil qilinmagan.
3. **Narx modeli.** *"RankWant narxlari PRD/ADR dan keyin"* — yo'nalish yo'q.
4. **Voyaga yetmaganlar ma'lumotlari.** Mahsulot maktab o'quvchilariga
   qaratilgan (02 dagi 1-segment), lekin butun `docs/` bo'ylab `GDPR`,
   "shaxsiy ma'lumot" yoki "voyaga yetmagan" bo'yicha birorta yozuv yo'q.
   SWOT `Threats` da faqat *"Coin/regulyatsiya (real pul sovrin)"* bor.

## Qulflash

**Tasdiq:** Saidakbar Narzullayev — Repo owner / maintainer, 2026-09-06.

2026-09-06: raqobatchi tahlili, brend (RankWant + Qvant), positioning va **bozor hajmi** tasdiqlandi.
Bog'liq qarorlar: [ADR-0003](../07-adr/0003-stack-django-next.md) stack · [ADR-0005](../07-adr/0005-content-strategy-own-content.md) kontent · [ADR-0006](../07-adr/0006-rating-model.md) reyting.
O'zgartirish = yangi ADR (`docs/07-adr/`).

## Keyingi qadam

`04-prd` lock → keyin `05-domain-model` va `08-technical-spec`.
