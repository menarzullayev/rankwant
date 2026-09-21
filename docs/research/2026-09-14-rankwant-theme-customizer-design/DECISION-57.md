# D57 — Zavod ko‘rinish clay qoladi

**Sana:** 2026-09-21  
**Qaror:** A — zavod clay  
**Tanlangan variant:** `keep-clay-factory`  
**CTO tavsiyasi:** B (rad — egasi A ni tanladi)

## Qaror

`DEFAULT_APPEARANCE.style` **clay** qoladi. Classic (dashboard + D49
kit) zavod emas.

Yumshoq shablon = clay + light + `dm-sans`. Zavod = clay + `font: null`
+ comfortable + system. Hech qaysi D19+D49 shablon match qilmaydi —
«Template modified» yangi mehmonda **to‘g‘ri** signal.

## Trade-off

Birinchi ochilishda banner doim. Clay tanlov emas, zavod. Classic
bosilganda match qiladi (D49, o‘lchandi).

## Ta’sir

`CustomizerContext.tsx` comment; `templates.test.ts` D57.
Default qiymat o‘zgarmadi.
