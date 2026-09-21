# D65 — oxirgi accordion sessionStorage da

**Sana:** 2026-09-21  
**Qaror:** B — remember-last-group  
**Tanlangan variant:** `remember-last-group`  
**CTO tavsiyasi:** B (qabul qilindi)

## Qaror

Appearance ochiq guruhi `sessionStorage` kaliti `rw:cz-group`.
Hisob/`ui_prefs`/`localStorage` emas — bu shablon identiteti emas (D49).

Noma’lum qiymat → `look` (Shablonlar). Tab yopilganda panel unmount;
qayta ochilganda oxirgi guruh tiklanadi.

## Trade-off

Yangi tab/oyna Shablonlardan boshlanadi. Private rejimda yozilmasa,
shu sessiya xotirasida listenerlar ishlaydi.

## Ta’sir

`group-session.ts`, `AppearanceTab.tsx`, `customizer-100`.
