# 7. ADR (Architecture Decision Records)

**STATUS:** living — bu bosqich qulflanmaydi, qarorlar to'planib boradi

Muhim texnik va mahsulot qarorlari.

## Format

Har bir ADR:

- Muammo
- Variantlar
- Tanlov
- Sabab
- Oqibatlar

## Ro'yxat

| #                                                | Sarlavha                            | Holat                  |
| ------------------------------------------------ | ----------------------------------- | ---------------------- |
| [0001](0001-brand-rankwant-qvant.md)             | Platforma RankWant, coin Qvant      | **accepted**           |
| [0002](0002-qvant-economy.md)                    | Qvant iqtisodiyoti — yopiq loop     | **accepted**           |
| [0003](0003-stack-django-next.md)                | Stack — Django 5.2 LTS + DRF + Next | **accepted**           |
| [0004](0004-judge-engine.md)                     | Judge engine — o'z engine, bake-off | **accepted** (bake-off 2026-09-06: Go + nsjail, 14/14) |
| [0005](0005-content-strategy-own-content.md)     | Kontent strategiyasi — o'z kontent  | **accepted**           |
| [0006](0006-rating-model.md)                     | Reyting modeli — 4 reyting          | **accepted**           |
| [0007](0007-skills-uses-current-difficulty.md)   | Skills — joriy qiyinlikdan          | **accepted**           |
| [0008](0008-auth-session-plus-pat.md)            | Auth — session + PAT                | **accepted**           |
| [0009](0009-monorepo.md)                         | Monorepo                            | **accepted**           |
| [0010](0010-per-test-refs.md)                    | Job da har test uchun S3 havolasi   | **accepted**           |
| [0011](0011-competition-formats.md)              | Arena, Duel, Chempionat, Hakaton, Testlar | **accepted**       |
| [0012](0012-seven-difficulty-levels.md)          | Qiyinlik shkalasi — yetti daraja          | **accepted**       |
| [0013](0013-editorial-spoiler-gate.md)           | Yechim tahlili — spoyler darvozasi        | **accepted**       |
| [0014](0014-codeforces-handle-seed.md)           | Codeforces handle'i — tavsiya urug'i      | rejected           |
| [0015](0015-account-email.md)                    | Hisob xatlari — brendlangan, kuzatuvsiz   | **accepted**       |
| [0016](0016-signup-and-login.md)                 | Ro'yxat va kirish — 3 maydon, 3 provayder | **accepted** (sahifa tuzilishi 2026-09-15 da yangilandi: bitta sahifa, uch bo'lim) |
| [0017](0017-profile-and-settings.md)             | Profil va sozlamalar — KEP'dan ilhom      | **accepted**       |
| [0018](0018-titles-roles-achievements.md)        | Unvon, ism rangi, rollar, yutuqlar        | **accepted**       |
| [0019](0019-contest-certificates.md)             | Musobaqa sertifikatlari — QR, PDF         | **accepted**       |
| [0020](0020-hacking.md)                          | Hacking — bitta dvigatel, to'rtta siyosat | **accepted**       |
| [0021](0021-hack-reference-solution.md)          | Hack testining javobi — etalon yechimdan  | **accepted**       |
| [0022](0022-judge-languages.md)                  | Judge tillari — 35 til, tilga xos sandbox sozlamalari | **accepted** |
| [0023](0023-indexing-and-ai-crawlers.md)         | Indekslash — qidiruvga ochiq, AI kraulerlarga yopiq   | **accepted** |
| [0024](0024-user-competitor-parity-fields.md)    | User modeli — raqobatchilar bilan tenglik uchun 21 maydon (46 → 67) | **accepted** |
| [0025](0025-roles-groups.md)                     | Rollar — staff guruhlari (support/content/ops) va obyekt mualliflari | **accepted** |

## Qoidalar

- Locked bosqichni buzish = yangi ADR
- Rad etilgan variantlar ham saqlanadi (qayta muhokama oldini olish)

## Assumptions

1. **Jadvaldagi holatlar joriy.** Bu taxmin **2026-09-13 da buzilgani aniqlandi**:
   `0004` `proposed (bake-off)` deb turardi, holbuki
   [`09-development-plan`](../09-development-plan/README.md) bake-off gate'i
   2026-09-06 da yopilganini yozadi (g'olib Go + nsjail, 14/14). Holat
   tuzatildi — lekin sabab qayd etiladi: **holat qo'lda yangilanadi, ya'ni
   eskirishi mumkin.**
2. **5 bo'limli format yetarli.** Muammo · Variantlar · Tanlov · Sabab ·
   Oqibatlar — shu format barcha 20 ADR uchun qo'llaniladi.
3. **`rejected` ADR ham qiymatli.** ADR-0014 saqlanadi, chunki qayta muhokama
   oldini oladi.

## Open questions

1. **`Qaytarilishi` (reversibility) bo'limi — 20 tadan 0 tasida.** Qaysi qaror
   qaytarilishi mumkin, qaysi biri qaytarilmasligi hech qayerda yozilmagan.
   Holbuki qaytarilmas qaror boshqacha ehtiyot talab qiladi.
2. **`Tasdiq` (approval) bo'limi — 20 tadan 0 tasida.** Yuqori ta'sirli yoki
   qaytarilmas qarorlar uchun inson tasdig'i talab qilinadi, lekin hech bir ADR
   kim tasdiqlaganini yozmaydi.
3. **`Evidence` alohida bo'lim emas.** ADR-0004 da bake-off natijalari bor
   (o'lchovlar, sig'im hisoblari) — ya'ni dalil **mavjud**, lekin standart
   bo'lim sifatida ajratilmagan.

## Tasdiq

**Bosqich:** living — qulflanmaydi, qarorlar to'planib boradi.

Yuqori ta'sirli va qaytarilmas qarorlar uchun inson tasdig'i alohida
yozilishi kerak (yuqoridagi 2-band). Birinchi bunday yozuv — ADR-0024
(`**Approved by:**` qatori, 2026-09-18). Eskilaridan eng ustuvor nomzod `0004`
(qaytarilmas, xavfsizlik uchun kritik).
