# D58 — Content width faqat slider

**Sana:** 2026-09-21  
**Qaror:** B — slider only  
**Tanlangan variant:** `slider-only`  
**CTO tavsiyasi:** B (qabul qilindi)

## Qaror

Interfeys Content width **interval**: `1000–1800` px, `step=100`, joriy
px yozuvi. 9 raqamli chip olib tashlandi.

D51 katalog qoidasi: 2–5 variant chip (D53), katalog SelectField.
Width oila emas — named 3–5 chip yangi shartnoma bo‘lardi.

## Trade-off

Snap tugmalari yo‘q. Slider `step={WIDTH_STEP}` baribir 100 px
panjara.

## Ta’sir

`AppearanceTab.tsx` `WidthSection`; `WIDTH_STEPS` o‘chirildi.
`customizer-100.test.ts` D58.
