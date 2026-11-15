# Rejalashtirilgan yo'nalishlar (RankWant platforma sifatida)

**Sana:** 2026-11-15. **Manba:** Saidakbar aka, bosh sahifa heroi va yo'nalishlar muhokamasi.
**Holat:** reja. Hech biri qurilmagan. Sayt ularni **ko'rsatmaydi** (hero qarori:
faqat tayyor yo'nalish ko'rinadi, `docs/decisions/2026-11-15-guest-hero.md`).

## Tartib

Avval **CP bo'limi** (sport dasturlash va olimpiada) tugatiladi; yangi yo'nalishlar
undan keyin. Egasi qarori (2026-11-15): tartib mezoni **oldindan belgilanmaydi** —
yo'nalishlar **qadamma-qadam** hal qilinadi. Quyidagi jadval — nomzodlar ro'yxati, navbat emas.

## Tuzilma

RankWant — platforma, umumiy hisob va Qvant. Joylashuv qoidasi (egasi tanlovi): **mohiyatiga
qarab aralash** — CP yadrosini kengaytiradigan yo'nalishlar asosiy `rankwant.uz` ning
bo'limi, mustaqil mavzular alohida subdomen (`science.rankwant.uz`, `games.rankwant.uz`, …).
Qaysi yo'nalish qayerga tushishi — yo'nalish boshlanganda aniqlashtiriladi; quyidagi
«Joylashuv» ustuni faqat egasi yoki hujjat aniq aytgan holatlarni ko'rsatadi.

## Nomzodlar

«Hajm» ustuni — **mening taxminim** (mavjud kod bazasiga nisbatan), o'lchov emas.

### Birinchi muhokamada aytilganlar

| # | Yo'nalish | Joylashuv | Holat |
|---|---|---|---|
| 1 | Fan bo'limi | alohida subdomen | reja |
| 2 | O'yinlar bo'limi | alohida subdomen | reja |
| 3 | O'z dasturlash tilimiz | belgilanmagan | reja |

### Egasi tanlagan qo'shimcha yo'nalishlar (16 ta, hammasi tanlandi)

| # | Yo'nalish | Guruh (hajm taxmini) | Nimaga tayanadi / nima yangi |
|---|---|---|---|
| 4 | Loyihaviy o'rganish | C — yangi infratuzilma | kurslar + loyiha sandbox'i |
| 5 | Veb va mobil mashqlar | C — yangi infratuzilma | yangi judge turi (brauzer sandbox) |
| 6 | Matematika | B — yangi mavzu | KaTeX va «javob» masala turi bor; isbot qo'lda tekshiriladi |
| 7 | Ma'lumotlar tahlili va AI/ML | C — yangi infratuzilma | hisoblash resursi, datasetlar |
| 8 | Botlar jangi | C — yangi infratuzilma | o'yin dvigateli + sandbox |
| 9 | Kiberxavfsizlik (CTF) | C — yangi infratuzilma | har masalaga konteyner; tahdid modeli A-1 xavfi |
| 10 | Kundalik topishmoq va puzzle | A — mavjud bazani kengaytiradi | Qvant vazifalari va streak |
| 11 | Jamoaviy ligalar | A — mavjud bazani kengaytiradi | chempionat va hakaton |
| 12 | Ish topish va intervyu | B — yangi mavzu | profil/reyting asosida rezyume, vakansiyalar |
| 13 | Mentorlik | B — yangi mavzu | xabar almashish, seanslar |
| 14 | Kompaniyalar uchun yollash testlari (B2B) | B — yangi mavzu | musobaqa va testlar |
| 15 | Maktab va universitet uchun LMS | A — mavjud bazani kengaytiradi | auditoriya (sinf) va kurslar |
| 16 | Mobil ilova | D — alohida mahsulot | yangi kod bazasi |
| 17 | Ochiq API va SDK | A — mavjud bazani kengaytiradi | shaxsiy tokenlar (ADR-0008); vision'da uzoq muddatli maqsad |
| 18 | Olimpiada tashkilotchilari vositalari | A — mavjud bazani kengaytiradi | musobaqa, mirror va hamkor musobaqalar |
| 19 | Muallif bozori | B — yangi mavzu | kurs studiyasi va to'lov bayrog'i bor; moderatsiya yangi |

## Cheklovlar

- **Vision (locked, 2026-09-06)** missiyasi faqat sport dasturlash va informatika
  olimpiadasi. Missiyani kengaytirish yangi ADR talab qiladi (`docs/07-adr/`).
- Tayyor bo'lmagan yo'nalish saytda ko'rsatilmaydi: dev-alpha'da haqiqiy foydalanuvchi
  yo'q, va'da halol bo'lishi kerak.
- Hozir haqiqiy foydalanuvchi 10 ta (30 kunda faoli 1 ta): B2B yo'nalishlar (14, 15, 18)
  uchun mijoz bo'lishi foydalanuvchi bo'lishiga bog'liq.

## Ochiq

Har yo'nalish boshlanishidan oldin: maqsad, auditoriya, joylashuv (bo'lim yoki subdomen),
birinchi MVP chegarasi va tayyor deb hisoblash mezoni alohida hal qilinadi.
