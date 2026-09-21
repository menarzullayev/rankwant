# D62 — overlay/form cookie’ga kirmaydi

**Sana:** 2026-09-21  
**Qaror:** A — CSS-only  
**Tanlangan variant:** `keep-css-only`  
**CTO tavsiyasi:** A (qabul qilindi)

## Qaror

`rw:markup` faqat `v` / `s` / `l` / `p` (verdict, status, loading, iconPack).
Overlay va form `html[data-overlay]` / `html[data-form]` — first-paint
localStorage dataset. Cookie kalitlari `o=` / `f=` yo‘q.

## Sabab

Cookie hidratsiya uchun: verdict/status/loading/icon React daraxtini
o‘zgartiradi. Overlay/form CSS token. Cookie kengaysa non-default overlay
mehmonida bosh sahifa keshi `private` bo‘ladi, HTML daraxti tuzalmaydi.

## Trade-off

SSR overlay/form default chizadi; klient first-paint skripti dataset
qo‘yadi. FOUC faqat overlay/form chrome’da, hidratsiya xatosi emas.

## Ta’sir

`prefs.ts` `MarkupPrefs`, first-paint cookie yozuvi, `apply.ts`,
`markup-cookie.test.ts`.
