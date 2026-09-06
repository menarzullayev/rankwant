# Bake-off natijasi — `judge-go`

Sana: 2026-09-06 21:14 · Wall: 7.6s

| Case | Kutilgan | Kelgan | Holat | total_ms | Izoh |
| ---- | -------- | ------ | ----- | -------- | ---- |
| `01-aplusb` | AC | AC | ✅ | 831 |  |
| `02-wa` | WA | WA | ✅ | 826 |  |
| `03-tle-cpu` | TLE | TLE | ✅ | 1333 |  |
| `04-idleness` | IDLENESS | IDLENESS | ✅ | 3003 |  |
| `05-mle` | MLE | MLE | ✅ | 869 |  |
| `06-re` | RE | RE | ✅ | 110 |  |
| `07-ce` | CE | CE | ✅ | 19 |  |
| `08-ole` | OLE | OLE | ✅ | 12 |  |
| `10-file-write` | SECURITY_VIOLATION | RE | ✅ | 11 | RE (SECURITY_VIOLATION o'rniga qabul qilindi) |
| `11-network` | SECURITY_VIOLATION | RE | ✅ | 17 | RE (SECURITY_VIOLATION o'rniga qabul qilindi); tarmoq bloklangan (moddiy tekshiruv) |
| `12-proc-read` | SECURITY_VIOLATION | RE | ✅ | 9 | RE (SECURITY_VIOLATION o'rniga qabul qilindi); /proc niqoblangan (moddiy tekshiruv) |
| `13-symlink` | SECURITY_VIOLATION | RE | ✅ | 9 | RE (SECURITY_VIOLATION o'rniga qabul qilindi) |
| `09-fork-bomb` | SECURITY_VIOLATION | TLE | ✅ | 542 | TLE (SECURITY_VIOLATION o'rniga qabul qilindi) |
| `14-interactive` | AC | — | 🔧 | — | hali yozilmagan — ADR-0004 da ochiq band |

## Latency (funksional to'plam)

- p50: **110 ms** · p95: **1333 ms**
- NFR byudjeti: p50 < 5000 ms, p95 < 15000 ms

## Yuklama (30 parallel submit)

- Yakunlandi: 30/30
- p50: **836 ms** · p95: **839 ms**
- O'tkazuvchanlik: 1.2 submit/s

## Xulosa

**O'TDI**

> Izolyatsiya sinovlarining **hammasi** o'tishi shart — bitta xato ham nomzodni rad etadi
> ([ADR-0004](../../docs/07-adr/0004-judge-engine.md)).
