# Bake-off natijasi — `judge-go`

Sana: 2026-09-06 21:20 · Wall: 7.6s

| Case | Kutilgan | Kelgan | Holat | total_ms | Izoh |
| ---- | -------- | ------ | ----- | -------- | ---- |
| `01-aplusb` | AC | AC | ✅ | 856 |  |
| `02-wa` | WA | WA | ✅ | 840 |  |
| `03-tle-cpu` | TLE | TLE | ✅ | 1326 |  |
| `04-idleness` | IDLENESS | IDLENESS | ✅ | 3002 |  |
| `05-mle` | MLE | MLE | ✅ | 858 |  |
| `06-re` | RE | RE | ✅ | 110 |  |
| `07-ce` | CE | CE | ✅ | 10 |  |
| `08-ole` | OLE | OLE | ✅ | 10 |  |
| `10-file-write` | SECURITY_VIOLATION | RE | ✅ | 10 | RE (SECURITY_VIOLATION o'rniga qabul qilindi) |
| `11-network` | SECURITY_VIOLATION | RE | ✅ | 16 | RE (SECURITY_VIOLATION o'rniga qabul qilindi); tarmoq bloklangan (moddiy tekshiruv) |
| `12-proc-read` | SECURITY_VIOLATION | RE | ✅ | 10 | RE (SECURITY_VIOLATION o'rniga qabul qilindi); /proc niqoblangan (moddiy tekshiruv) |
| `13-symlink` | SECURITY_VIOLATION | RE | ✅ | 13 | RE (SECURITY_VIOLATION o'rniga qabul qilindi) |
| `14-interactive` | AC | AC | ✅ | 10 |  |
| `09-fork-bomb` | SECURITY_VIOLATION | TLE | ✅ | 541 | TLE (SECURITY_VIOLATION o'rniga qabul qilindi) |

## Latency (funksional to'plam)

- p50: **16 ms** · p95: **1326 ms**
- NFR byudjeti: p50 < 5000 ms, p95 < 15000 ms

## Yuklama (30 parallel submit)

- Yakunlandi: 30/30
- p50: **841 ms** · p95: **869 ms**
- O'tkazuvchanlik: 1.2 submit/s

## Xulosa

**O'TDI**

> Izolyatsiya sinovlarining **hammasi** o'tishi shart — bitta xato ham nomzodni rad etadi
> ([ADR-0004](../../docs/07-adr/0004-judge-engine.md)).
