# Bake-off natijasi — `judge-go`

Sana: 2026-09-06 22:05 · Wall: 7.8s

| Case | Kutilgan | Kelgan | Holat | total_ms | Izoh |
| ---- | -------- | ------ | ----- | -------- | ---- |
| `01-aplusb` | AC | AC | ✅ | 890 |  |
| `02-wa` | WA | WA | ✅ | 858 |  |
| `03-tle-cpu` | TLE | TLE | ✅ | 1346 |  |
| `04-idleness` | IDLENESS | IDLENESS | ✅ | 3003 |  |
| `05-mle` | MLE | MLE | ✅ | 890 |  |
| `06-re` | RE | RE | ✅ | 122 |  |
| `07-ce` | CE | CE | ✅ | 21 |  |
| `08-ole` | OLE | OLE | ✅ | 16 |  |
| `10-file-write` | SECURITY_VIOLATION | RE | ✅ | 12 | RE (SECURITY_VIOLATION o'rniga qabul qilindi) |
| `11-network` | SECURITY_VIOLATION | RE | ✅ | 21 | RE (SECURITY_VIOLATION o'rniga qabul qilindi); tarmoq bloklangan (moddiy tekshiruv) |
| `12-proc-read` | SECURITY_VIOLATION | RE | ✅ | 13 | RE (SECURITY_VIOLATION o'rniga qabul qilindi); /proc niqoblangan (moddiy tekshiruv) |
| `13-symlink` | SECURITY_VIOLATION | RE | ✅ | 12 | RE (SECURITY_VIOLATION o'rniga qabul qilindi) |
| `14-interactive` | AC | AC | ✅ | 14 |  |
| `09-fork-bomb` | SECURITY_VIOLATION | TLE | ✅ | 542 | TLE (SECURITY_VIOLATION o'rniga qabul qilindi) |

## Latency (funksional to'plam)

- p50: **21 ms** · p95: **1346 ms**
- NFR byudjeti: p50 < 5000 ms, p95 < 15000 ms

## Xulosa

**O'TDI**

> Izolyatsiya sinovlarining **hammasi** o'tishi shart — bitta xato ham nomzodni rad etadi
> ([ADR-0004](../../docs/07-adr/0004-judge-engine.md)).
