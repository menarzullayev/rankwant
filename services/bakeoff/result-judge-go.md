# Bake-off natijasi — `judge-go`

Sana: 2026-09-10 04:06 · Wall: 9.2s

| Case | Kutilgan | Kelgan | Holat | total_ms | Izoh |
| ---- | -------- | ------ | ----- | -------- | ---- |
| `01-aplusb` | AC | AC | ✅ | 1453 |  |
| `02-wa` | WA | WA | ✅ | 1132 |  |
| `03-tle-cpu` | TLE | TLE | ✅ | 1624 |  |
| `04-idleness` | IDLENESS | IDLENESS | ✅ | 3003 |  |
| `05-mle` | MLE | MLE | ✅ | 1159 |  |
| `06-re` | RE | RE | ✅ | 133 |  |
| `07-ce` | CE | CE | ✅ | 18 |  |
| `08-ole` | OLE | OLE | ✅ | 15 |  |
| `10-file-write` | SECURITY_VIOLATION | RE | ✅ | 27 | RE (SECURITY_VIOLATION o'rniga qabul qilindi) |
| `11-network` | SECURITY_VIOLATION | RE | ✅ | 26 | RE (SECURITY_VIOLATION o'rniga qabul qilindi); tarmoq bloklangan (moddiy tekshiruv) |
| `12-proc-read` | SECURITY_VIOLATION | RE | ✅ | 20 | RE (SECURITY_VIOLATION o'rniga qabul qilindi); /proc niqoblangan (moddiy tekshiruv) |
| `13-symlink` | SECURITY_VIOLATION | RE | ✅ | 22 | RE (SECURITY_VIOLATION o'rniga qabul qilindi) |
| `14-interactive` | AC | AC | ✅ | 11 |  |
| `09-fork-bomb` | SECURITY_VIOLATION | TLE | ✅ | 542 | TLE (SECURITY_VIOLATION o'rniga qabul qilindi) |

## Latency (funksional to'plam)

- p50: **27 ms** · p95: **1624 ms**
- NFR byudjeti: p50 < 5000 ms, p95 < 15000 ms

## Xulosa

**O'TDI**

> Izolyatsiya sinovlarining **hammasi** o'tishi shart — bitta xato ham nomzodni rad etadi
> ([ADR-0004](../../docs/07-adr/0004-judge-engine.md)).
