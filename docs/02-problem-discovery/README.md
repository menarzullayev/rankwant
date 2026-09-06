# 2. Problem Discovery

**STATUS:** locked (2026-09-06)

## Target users

| Segment                     | Ehtiyoj                                          |
| --------------------------- | ------------------------------------------------ |
| **O'rta maktab o'quvchisi** | DTM/informatika, olimpiada tayyorgarlik, reyting |
| **Universitet talabasi**    | ICPC, sport CP, jamoa                            |
| **O'qituvchi / murabbiy**   | Sinf, musobaqa, progress kuzatuv                 |
| **Mustaqil o'rganuvchi**    | Masala arxivi, virtual contest, streak           |
| **Tashkilot**               | Mirror musobaqa, rasmiy olimpiada infratuzilmasi |

## Pain points (hozirgi bozor)

1. **RoboContest** — kuchli, lekin API yopiq (Inertia); integratsiya qiyin.
2. **KEP.uz** — ochiq REST, lekin kichikroq jamoa (~9k); Aurora white-label cheklovlari.
3. **cp.uz** — ajoyib o'zbek **o'qish** kontenti, lekin **OJ/musobaqa yo'q**.
4. **Fragmentatsiya** — o'qish bir joyda, yechish boshqa joyda; olimpiada tarixi va maqola-masala bog'lanishi zaif.
5. **Motivatsiya** — faqat reyting yetmaydi; coin/quest/streak (KEP/RoboContest isbotlagan) kerak.

## Use cases (asosiy)

1. Masalani o'qish → custom test → submit → verdict.
2. Virtual yoki live contest — ACM/ICPC scoring.
3. Mirror: Prezident maktabi, Al-Xorazmiy va b. rasmiy format.
4. O'qituvchi: 30 o'quvchi, uy vazifasi masalalari, cheat panel.
5. Maqoladan masalaga o'tish — o'z o'qish kontenti ichida (Phase 2).
6. Qvant: kunlik vazifa bajarish → do'konda cover/streak freeze.

## North Star

**Haftalik faol yechuvchi (WAS)** — bir hafta ichida kamida **1 ta AC** olgan unikal foydalanuvchilar soni.

Nega aynan shu:

- **Sifat bilan tuzatilgan** — bo'sh yoki spam submitlarni hisoblamaydi, ya'ni «mahsulot qiymat berdimi» degan savolga javob beradi
- **MVP birinchi kunidan** o'lchanadi — qo'shimcha infra talab qilmaydi
- Skills reytingi bilan bir xil hodisadan oziqlanadi ([ADR-0006](../07-adr/0006-rating-model.md)) — ya'ni mahsulot va metrika bir yo'nalishga qaraydi

Hisoblash: `COUNT(DISTINCT user_id)` — `attempt.verdict = AC` bo'lgan, `created_at` oxirgi 7 kun ichida.

## Input metrikalar (voronka)

| Bosqich       | Metrika                              | Maqsad (misol)  |
| ------------- | ------------------------------------ | --------------- |
| Aktivatsiya   | Ro'yxatdan o'tish → birinchi AC      | < 7 kun median  |
| Odat          | Hafta-2 qaytish (WAS retention)      | > 30%           |
| Chuqurlashish | Contest registration → participation | > 60%           |
| Kengayish     | O'qituvchi sinflari                  | pilot 5+ maktab |
| Retention     | Qvant quest completion (Phase 1+)    | kunlik 30%+ DAU |

**Operatsion** (North Star emas): kunlik submit hajmi — judge sig'imini rejalashtirish uchun.

## Non-goals (hozircha)

- KEP duels/arena/hackathon to'liq nusxasi
- Crypto/USDT sovrin (ADR kerak)
- cp.uz security audit/fix (alohida scope)

## Qulflash

2026-09-06: target user, pain point, use case va **North Star** tasdiqlandi.
Kontent strategiyasi — [ADR-0005](../07-adr/0005-content-strategy-own-content.md) (cp.uz bog'liqlik emas).
O'zgartirish = yangi ADR (`docs/07-adr/`).

## Keyingi qadam

`03-market-research` — positioning va raqobatchi tahlilini yakunlash → `04-prd` feature ro'yxati.
