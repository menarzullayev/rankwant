# D61 — Tartib va Interfeys ajraladi

**Sana:** 2026-09-21  
**Qaror:** B — ikki accordion  
**Tanlangan variant:** `split-layout-kit`  
**CTO tavsiyasi:** B (qabul qilindi)

## Qaror

Appearance beshta guruh: Shablonlar / Rang / Matn / **Tartib** / **Interfeys**.

- Tartib (`layout`): `navMode`, `navShape`, `width`, `card`, `pattern` (D50/D53/D58).
- Interfeys (`system`): oltita kit `SelectField` (D48/D51).

Yopiq guruh unmount (CUST-100). D60 ikki tab o‘zgarmaydi.

## Sabab

D48 kit yozuvini Interfeysga qo‘ydi; D50 layout ni shaxsiy qildi. Bitta ochiq unit ikkala domenni mount qilardi. Ajratish unmount chegarasini domen bilan moslashtiradi.

## Trade-off

Beshinchi guruh — yana bitta sarlavha va 10 til kaliti. Ichki disclosure (C) ochiq Interfeysda kitni baribir daraxtga kiritardi.

## Ta’sir

`chrome.ts` `GROUPS`, `AppearanceTab.tsx`, `customizer.group.layout` (10 til), `customizer-100.test.ts`.
