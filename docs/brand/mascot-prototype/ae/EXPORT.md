# After Effects → Lottie (Bodymovin) — Crest Spirit

Bu prototip papkasidagi `lottie/*.json` fayllar **qo'lda yozilgan soddalashtirilgan** namunalar.
Production sifatida AE dan eksport qilish tartibi:

## 1. Tayyorgarlik

1. `crest-spirit.svg` ni Illustrator/Figma orqali AE ga import qiling (shape layers).
2. Qatlamlar: `outer`, `body`, `goal-dot`, `goal-glow` (alohida precomp tavsiya etiladi).
3. Kompositsiya: **512×512** yoki **1024×1024** (veb uchun 512 yetarli, `@2x` PNG emas).

## 2. Animatsiya (namuna timeline)

| Kadr | Harakat |
|------|---------|
| 0–45 | `goal-dot` scale 100% → 115%, position +5px yuqoriga (ease in-out) |
| 0–45 | `spirit-body` scale Y 100% → 98% (nafas) |
| Qvant rejimi | alohida komp: orbit rotation 0°→360° (4 s loop) |

**Cheklov:** brend qoidasi — flat vector, gradient/glow minimal; `goal-glow` opacity ≤ 25%.

## 3. Bodymovin eksport

1. [Bodymovin](https://aescripts.com/bodymovin/) yoki [LottieFiles AE plugin](https://lottiefiles.com/plugins/after-effects).
2. Sozlamalar:
   - **Glyphs / fonts:** yo'q (faqat shakl)
   - **Images:** yo'q
   - **Hidden layers:** skip
   - **Guided layers:** skip
3. Eksport: `lottie/crest-spirit-ae.json` (mavjud prototipni almashtirish yoki yonma-yon).
4. [LottieFiles preview](https://lottiefiles.com/preview) yoki `mascot-review.html` da tekshiring.

## 4. RankWant integratsiya eslatmalari

- `lottie-web` ~60 KB — hozir `apps/web` da yo'q (D62 qarori).
- `check_contrast.py` Lottie ichidagi hexlarni avtomatik o'qimaydi — ranglar `#44A0FC`, `#102038`, `#1074DC` dan chetlanmasin.
- `data-motion=off|reduce` → statik birinchi kadr (`goToAndStop(0)`).
- SSR: faqat client komponent (`"use client"` + dynamic import).
