# Pre-Pipeline — Idea Selection

**STATUS:** ⚠️ **RETROAKTIV** — 2026-09-13 da yozildi.

Bu hujjat **o'sha paytda yozilmagan**. RankWant Project Alpha
pipeline'idan **oldin** boshlangan: `docs/README.md` ning o'zi aytadi —
*"RankWant — raqobatchi benchmark + aniq brend bilan boshlangan."*

Ya'ni tanlov **bo'lgan**, lekin hujjatlashtirilmagan. Quyidagi mazmun
**mavjud hujjatlardan tiklandi** — har bir da'vo manbasi ko'rsatilgan.
O'ylab topilgan narsa yo'q.

## Nima uchun kerak

Framework Stage 01 dan **oldin** shu bosqichni talab qiladi:

> *Human approval required before an idea enters Stage 01.*

Hujjat bo'lmasa, butun 10 bosqichli zanjir **asossiz** ko'rinadi: nima uchun
aynan shu mahsulot, nima rad etilgan, qanday mezon bilan. Zanjirning boshini
yopish uchun yozildi.

## Tanlov mezonlari (tiklandi)

RankWant'ning o'z hujjatlaridan chiqadigan mezonlar:

| # | Mezon | Manba |
|---|---|---|
| 1 | **O'lchanadigan bo'shliq** — raqobatchilarda yo'q narsa | `03/README.md` — cp.uz'da OJ yo'q, fragmentatsiya |
| 2 | **Kirish nuqtasi** — 0 user bilan boshlash mumkinmi | `03/README.md` — "197k network effekti bilan to'g'ridan-to'g'ri raqobat yutuqsiz" |
| 3 | **Global nom** — mahalliy bozordan chiqish mumkinmi | `03/brand-discovery.md` — "Mahalliy nom… global scale uchun tor" |
| 4 | **Mudofaa qilinadigan farq** — nusxa olinmasin | `01-vision` principle #1 — "Clone emas, benchmark" |
| 5 | **Huquqiy xavfsizlik** | `01-vision` principle #6 — "Aurora/KEP kodini nusxalamaslik" |

## Ko'rib chiqilgan variantlar

### 1. Raqobatchi tanlovi — qaysi platformani benchmark qilish

Manba: [`03-market-research/competitor-summary.md`](../03-market-research/competitor-summary.md)

| Nomzod | Kuch | Zaif | Qaror |
|---|---|---|---|
| **RoboContest** | ~197k user, to'liq mahsulot xaritasi | API yopiq (Inertia) | **Benchmark: mahsulot xaritasi** |
| **KEP.uz** | Ochiq REST (~102 endpoint), kepcoin, 4 reyting | Kichikroq (~9k), Aurora cheklovi | **Benchmark: API shape + reyting modeli** |
| **cp.uz** | O'zbek o'qish kontenti, roadmap | **OJ/musobaqa yo'q** | **Benchmark: kontent chuqurligi** |

**Tanlov: uchtasi ham — har biri boshqa qatlam uchun.** To'liq nusxa emas
(`competitor-summary.md` → "Nusxalamaymiz").

### 2. Brend va nom tanlovi

Manba: [`03-market-research/brand-discovery.md`](../03-market-research/brand-discovery.md)

Bu eng to'liq hujjatlashtirilgan qism — 30 nom skanerdan o'tkazilgan.

| Variant | Sabab rad etildi |
|---|---|
| `SolveUz`, `YechLab`, `Bosqly` | Mahalliy nom — global scale uchun tor |
| `OlympIQ` / `@olympiq` | Telegram band; `olympiq.com/.app` faol |
| `rankwantcoin`, `rankvantcoin` | Og'ir (13 harf), brend takrori |
| `Teniq`, `Nexa` | Telegram'ning 5-harf qoidasi / band |

**Tanlov: RankWant + Qvant.** RankWant — "Rank Want" (motivatsion, slogan
o'zi ishlaydi); Qvant — 5 harf, kvant/STEM nuansi, platformadan alohida "olam".

**Yakuniy tanlov juftlik orasida:** `RankWant` vs `Rankvant` (professionalroq
yozuv, zaxira) → **RankWant** tanlandi, *"motivatsiya ochiqroq"*.

### 3. Mahsulot shakli

Manba: [`02-problem-discovery/README.md`](../02-problem-discovery/README.md)

| Variant | Qaror |
|---|---|
| Faqat OJ (masala banki + judge) | Yetarli emas — reyting motivatsiyasi yetmaydi |
| Faqat contest | Yangi platforma uchun bo'sh arxiv bilan ishlamaydi |
| Faqat o'qish kontenti | cp.uz shu — lekin **OJ yo'q** |
| **OJ + contest + reyting + (keyin) o'qish kontenti** | ✅ **Tanlandi** |

Sabab: 02 dagi 4-og'riq — *"Fragmentatsiya — o'qish bir joyda, yechish
boshqa joyda"*. RankWant ikkalasini birlashtiradi.

### 4. Boshqa soha g'oyalari

⚠️ **Bu qism tiklanmadi.** Repo'da, `rankwant-audit/` da yoki `cp/` da
CP'dan tashqari ko'rilgan g'oyalar haqida **birorta yozuv yo'q**.

Foydalanuvchi bu kategoriyani tanladi, ya'ni bunday variantlar **bo'lgan** —
lekin ularning mazmuni hujjatlashtirilmagan va men uni o'ylab topa olmayman.

**To'ldirilishi kerak:** qaysi sohalar ko'rilgan, nima uchun rad etilgan.

## Tanlangan g'oya

**RankWant** — O'zbek va global sport dasturlash platformasi: reyting
xohlaganlar uchun judge, musobaqa va o'qish, **Qvant** mukofotlari bilan.

To'liq: [`01-vision/README.md`](../01-vision/README.md).

## Evidence

| Da'vo | Manba |
|---|---|
| Raqobatchilar tarkibi va farqi | `03/competitor-summary.md` (2026-09-06) |
| Nom skaneri, 30 nom, 16 Tier A | `03/brand-discovery.md` — `handlechecker` natijasi |
| Domen/handle holati | `03/brand-discovery.md` — 2026-09-06 kechasi |
| cp.uz'da OJ yo'qligi | `02/README.md` §3 |

⚠️ Raqamli da'volar (`~197k`, `~9k`) **tekshirib bo'lmaydi** — manba
fayllari repo'da yo'q, Linux bo'limida qolgan
([`03/README.md`](../03-market-research/README.md) ga qarang).

## Assumptions

1. **Tanlov jarayoni bo'lgan, lekin yozilmagan** — retroaktiv hujjat shu
   taxminga qurilgan. Agar aslida tanlov bo'lmagan bo'lsa, hujjat qayta
   yozilishi kerak.
2. **Brend tanlovi to'liq hujjatlashtirilgan** — `brand-discovery.md` 30 nom
   skanerini ko'rsatadi, ya'ni bu qism ishonchli.
3. **Mahsulot shakli tanlovi bilvosita** — 02 dagi og'riqlardan chiqarildi,
   alohida "shakl tanlovi" yozuvi yo'q.

## Open questions

1. **Boshqa soha g'oyalari** — qaysilari ko'rilgan va nima uchun rad etilgan?
2. **Tanlov sanasi** — eng qadimgi yozuv 2026-09-06 (`03` lock), lekin
   ishlab chiqish undan oldin boshlangan ko'rinadi.
3. **Raqobatchi raqamlari** — Linux'dagi ikki fayl ko'chirilgach tekshiriladi.

## Tasdiq

**Tasdiq:** Saidakbar Narzullayev — Repo owner / maintainer, 2026-09-13.

Bu tasdiq **hujjatning retroaktiv ekanini** va undagi mazmun mavjud
manbalardan tiklanganini qabul qiladi — yangi qaror emas, mavjud qaror
yozib qo'yilishi.

⚠️ **4-variant (boshqa soha g'oyalari) to'ldirilmaguncha hujjat to'liq emas.**
