# D51 — Kit oilalari select

**Sana:** 2026-09-21  
**Qaror:** B — 6 labeled select  
**Tanlangan variant:** `six-selects`  
**CTO tavsiyasi:** B (qabul qilindi)

## Qaror

Interfeysdagi kit oilalari chip devori emas, **olti** labeled
`SelectField` (Headless UI Combobox). Native `<select>` yo‘q — OS
paneli qorong‘i mavzuda oq chiqadi (`SelectField.tsx`).

Yozuvchi o‘zgarmaydi (D48). `/admin/kit` namuna.

## Trade-off

- Ochiq Interfeysda kit tab stop: 50 → 6.
- Variantlar qidiruvli listboxda; bir qarashda hammasi ko‘rinmaydi.
- `Dropdown` customizer bundle’iga kiradi.

## O‘lchov

Baseline: 50 `aria-pressed` chip (11+11+10+4+5+9).  
D51: `SelectField` × 6; kit `onClick={() => setAppearance({ …` yo‘q.
