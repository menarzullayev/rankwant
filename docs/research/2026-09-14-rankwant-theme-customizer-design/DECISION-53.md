# D53 — Layout chip qoladi

**Sana:** 2026-09-21  
**Qaror:** A — layout chip  
**Tanlangan variant:** `keep-layout-chips`  
**CTO tavsiyasi:** A (qabul qilindi)

## Qaror

Interfeysda `navMode`, `navShape`, `card`, `pattern` **chip** qoladi
(2–5 variant). Kit oilalari SelectField (D51). Ikki naqsh ataylab.

## Trade-off

Nav/top ochiq qoladi; UI bir xil emas.

## O‘lchov

`LAYOUT_CHIP_KEYS` × 4 `onClick` chip; `SelectField` hali 6 (faqat kit).
