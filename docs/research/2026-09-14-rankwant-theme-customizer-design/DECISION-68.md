# D68 — jonli first-load JS o‘lchovi

**Sana:** 2026-09-21  
**Qaror:** A — measure-live-js  
**Tanlangan variant:** `measure-live-js`  
**CTO tavsiyasi:** A (qabul qilindi)

## Qaror

Bundle o‘zgarmadi. Jonli mehmon homepage (`https://rankwant.uz/`) da
Resource Timing + Performance trace yozildi. `lazy()` yo‘q (D64).

## O‘lchov

| | |
|---|---|
| web SHA | `2ceb76a` (D66) |
| Qurilma | desktop, throttle yo‘q |
| Encoding | gzip |
| First-party script | 15 |
| Encoded | **331 407 B (323.6 KiB)** |
| Shundan Next chunk | 303 213 B (296.1 KiB) |
| `i18n/uz.js` | 28 194 B (27.5 KiB) |
| Decoded | 1 176 185 B (1148.6 KiB) |
| LCP | 192 ms (TTFB 75 + render 117) |
| CLS | 0.00 |
| DCL / load | 208 / 390 ms |

Eng katta chunk: `10fos77coexu8.js` 71.6 KiB gzip. Cloudflare beacon
encoded 0; 3rd-party main-thread 6 ms.

D63 Appearance exclusive 139.1 KiB — **UTF-8 manba**, gzip emas.
323.6 KiB gzip — butun homepage first-load, faqat customizer emas.

Batafsil: [FIRST-LOAD.json](./FIRST-LOAD.json).

## Trade-off

Lab desktop, Lighthouse mobile 4x emas. CF `HIT` immutable chunklarda
(hash), hajm baribir shu.

## Ta’sir

Faqat decision research. `Customizer.tsx` o‘zgarmadi.
