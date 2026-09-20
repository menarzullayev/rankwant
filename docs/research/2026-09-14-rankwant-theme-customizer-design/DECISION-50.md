# D50 — Layout chrome shaxsiy

**Sana:** 2026-09-21  
**Qaror:** A — layout shaxsiy  
**Tanlangan variant:** `keep-layout-personal`  
**CTO tavsiyasi:** A (qabul qilindi)

## Qaror

Jamoa shabloni = D19 (uslub + mavzu + rang + shrift + zichlik) + D49
(kit oilalari). Quyidagilar **shaxsiy** qoladi — apply tiklamaydi,
match solishtirmaydi:

`navMode`, `navShape`, `card`, `pattern`, `fontHeading`, `size`,
`scale`, `lineHeight`, `tracking`, `width`.

APP-8 («matchTemplate to‘liq emas — nav/card qo‘sh») **rad** etildi:
bu maydonlar shablon scope’ida emas, tuzatilishi kerak emas.

## Sabab

D49 kit yolg‘onini yopdi. Layout chrome ni ham snapshot qilish Klassik
bosishda sidenav/width/size ni o‘g‘irlar edi (D15/D16). D19 buni hech
qachon va’da qilmagan.

## Trade-off

Banner nav/o‘lcham o‘zgarishini yashiradi. Bu endi xato emas — qoida.

## Ta’sir

- `TEMPLATE_LAYOUT_KEYS` + `templates.test.ts`
- APP-8 yopildi (`docs/research/2026-09-18-appearance-audit/BOARD.md`)

## O‘lchov

`dashboard + topnav + size 120` → match `classic` (baseline ham, D50
ham). Apply Klassik → layout qiymatlari saqlanadi.
