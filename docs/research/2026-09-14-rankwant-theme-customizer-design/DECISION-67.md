# D67 — Tiklash chrome kursorni tozalamaydi

**Sana:** 2026-09-21  
**Qaror:** A — reset-prefs-only  
**Tanlangan variant:** `reset-prefs-only`  
**CTO tavsiyasi:** A (qabul qilindi)

## Qaror

Tiklash (D25) faqat appearance / a11y pref tokenlarini zavod + D37 ga
qaytaradi. `rw:cz-tab` va `rw:cz-group` qoladi. Suzuvchi tugma
`rw:customizer-hidden` ham qoladi.

## Trade-off

Qulaylik ochiq holda Tiklash qilinsa, panel Qulaylikda qoladi — tokenlar
zavod, chrome kursor o‘sha joyda. Bu “panel-IA reset” emas.

## Ta’sir

`ResetRow.tsx` (izoh), `customizer-100`. `resetAll` o‘zgarmadi.
