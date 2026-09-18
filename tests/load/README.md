# tests/load — k6

test-strategy.md § 7–10.

```bash
k6 run -e SCENARIO=load   tests/load/main.js   # kutilayotgan yuklama
k6 run -e SCENARIO=spike  tests/load/main.js   # contest boshlanishi
k6 run -e SCENARIO=stress tests/load/main.js   # sig'imdan oshirish
k6 run -e SCENARIO=soak -e SOAK_DURATION=12h tests/load/main.js
```

## Chegaralar (04-prd NFR)

| Metrika | Chegara |
| ------- | ------- |
| Sahifa p95 | < 1000 ms |
| Standings p95 | < 300 ms |
| Xato darajasi | < 1% |
| Judge p50 / p95 | < 5 s / < 15 s |

## Ma'lum sig'im

[ADR-0004](../../docs/07-adr/0004-judge-engine.md) o'lchovi: bitta host'da
8 worker ≈ **8 submit/s**. Spike NFR (50 submit/s) uchun 6–8 judge host
yoki kompilyatsiya keshi kerak.

**Sahifa ochilishi alohida chegara** (2026-09-17, local origin, CF yo'q):
50 VU `GET /` p95 657 ms ✅; 100 VU p95 1.65 s ❌; xato 0%. 1000 bir
vaqtdagi tashrif shu `web` da NFR ni yiqitadi. Yozuv:
[docs/research/2026-09-17-homepage-load/REPORT.md](../../docs/research/2026-09-17-homepage-load/REPORT.md).
`main.js` hozir API o'qish + standings; bosh sahifa skripti repo tashqarida
(`cp/research/2026-09-17-homepage-load/rw-home-load.js`).
