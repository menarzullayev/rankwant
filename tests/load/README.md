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
yoki kompilyatsiya keshi kerak — sahifa yuklamasi bu chegaraga tegmaydi,
faqat submit oqimi tegadi.
