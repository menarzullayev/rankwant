# D64 — panel importlari eager qoladi

**Sana:** 2026-09-21  
**Qaror:** C — keep-eager  
**Tanlangan variant:** `keep-eager`  
**CTO tavsiyasi:** C (qabul qilindi)

## Qaror

`AppearanceTab` va `A11yTab` statik import. `lazy()` / `next/dynamic` yo‘q.

D63: Appearance exclusive 139.1 KiB source ichida OverlayHost/Verdict
allaqachon sahifada; A11y 16.4 KiB chunkga arzimaydi.

## Trade-off

Birinchi ochilish sync. Har sahifa panel modulini to‘laydi. Homepage JS
bottleneck alohida o‘lchanganda qayta ochiladi.

## Ta’sir

`Customizer.tsx` comment; `customizer-100` D64 + no-lazy assert.
