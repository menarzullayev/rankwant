# services/judge-go — bake-off nomzod A

**Go worker + nsjail** (Apache-2.0). [ADR-0004](../../docs/07-adr/0004-judge-engine.md) bake-off.

## Qoidalar

- **Pull** protokoli — navbatdan ish tortadi; kiruvchi port yo'q
- Tarmoq: Redis ✅ · S3 ✅ · API/DB ❌ · internet ❌
- DB credential **yo'q**

Sinov to'plami va o'tish sharti: [09 § Sprint 0.5](../../docs/09-development-plan/README.md)
