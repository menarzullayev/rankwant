# D63 — panel hajmini avval o‘lchash

**Sana:** 2026-09-21  
**Qaror:** A — measure-first  
**Tanlangan variant:** `measure-first`  
**CTO tavsiyasi:** A (qabul qilindi)

## Qaror

`lazy()` yo‘q. `AppShell` → `Customizer` → ikkala tab statik qoladi.
Baseline yozildi: `measure_panel_graph.py` + `PANEL-GRAPH.json`.

## O‘lchov (2026-09-21, `fa4c71a`)

Birlik: UTF-8 manba bayti, statik `import` grafi, `import type` tashqarida.
Bu webpack gzip emas — yuqori chegara.

| Qopqoq | Fayl | Bayt | KiB |
|---|---:|---:|---:|
| Shell (tablar follow qilinmagan) | 38 | 287 079 | 280.4 |
| AppearanceTab exclusive | 19 | 142 486 | 139.1 |
| A11yTab exclusive | 5 | 16 837 | 16.4 |
| Ikkala tab ulashgan exclusive | 4 | 14 304 | 14.0 |
| To‘liq Customizer grafi | 58 | 432 098 | 422.0 |

Qayta o‘lchash:

```text
python docs/research/2026-09-14-rankwant-theme-customizer-design/measure_panel_graph.py
```

## Cheklov

Exclusive ro‘yxatda `OverlayHost`, `Verdict`, `Status`, `Loading` bor —
ular sahifada allaqachon (AppShell / kit). `lazy(AppearanceTab)` 139 KiB
ning hammasini kechiktirmaydi. A11y 16 KiB — alohida split arzon.

CI `First Load JS` qatori bu yugurishda logda topilmadi.

## Trade-off

Har sahifa panel JS to‘laydi. Split D64 ga qoldi — endi raqam bor.

## Ta’sir

Faqat decision research. `Customizer.tsx` o‘zgarmadi.
