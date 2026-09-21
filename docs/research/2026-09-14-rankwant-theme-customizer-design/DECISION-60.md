# D60 — Accessibility alohida tab

**Sana:** 2026-09-21  
**Qaror:** A — ikki tab qoladi  
**Tanlangan variant:** `keep-a11y-tab`  
**CTO tavsiyasi:** A (qabul qilindi)

## Qaror

`Appearance | Accessibility` tablist saqlanadi. A11y Appearance
accordion’iga qo‘shilmaydi va faqat Settings’ga ko‘chmaydi.

D49 match a11y’ni (protan/tritan) shablon emas deb hisoblaydi — sirtlar
ajralgani shu mantiqqa mos.

## Trade-off

Ikki sirt. Mehmon a11y’ni panelda topadi (D1).

## Ta’sir

`Customizer.tsx` comment; `customizer-100.test.ts` D60. Tab o‘zgarmadi.
