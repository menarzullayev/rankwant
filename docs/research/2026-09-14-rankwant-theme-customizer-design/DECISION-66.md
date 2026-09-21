# D66 — oxirgi panel tab sessionStorage da

**Sana:** 2026-09-21  
**Qaror:** B — session-tab  
**Tanlangan variant:** `session-tab`  
**CTO tavsiyasi:** B (qabul qilindi)

## Qaror

Appearance / Accessibility ochiq tab `sessionStorage` kaliti `rw:cz-tab`.
Hisob/`ui_prefs` emas — bu chrome kursori, shablon identiteti emas (D49).
Umr D65 (`rw:cz-group`) bilan bir xil: shu brauzer tabi.

Noma’lum qiymat → `appearance`. Panel unmount bo‘lsa ham qayta ochilganda
oxirgi tab tiklanadi.

## Trade-off

Yangi tab/oyna Appearance dan boshlanadi. Private rejimda yozilmasa,
shu sessiya xotirasida listenerlar ishlaydi. Hisobga yozilmasa
qurilmalar aralashmaydi.

## Ta’sir

`tab-session.ts`, `Customizer.tsx`, `customizer-100`.
