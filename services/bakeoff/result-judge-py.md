# Bake-off natijasi — `judge-py`

Sana: 2026-09-06 21:09 · Wall: 8.9s

| Case | Kutilgan | Kelgan | Holat | total_ms | Izoh |
| ---- | -------- | ------ | ----- | -------- | ---- |
| `01-aplusb` | AC | AC | ✅ | 846 |  |
| `02-wa` | WA | WA | ✅ | 819 |  |
| `03-tle-cpu` | TLE | TLE | ✅ | 1418 |  |
| `04-idleness` | IDLENESS | IDLENESS | ✅ | 2604 |  |
| `05-mle` | MLE | MLE | ✅ | 844 |  |
| `06-re` | RE | RE | ✅ | 121 |  |
| `07-ce` | CE | CE | ✅ | 31 |  |
| `08-ole` | OLE | OLE | ✅ | 14 |  |
| `10-file-write` | SECURITY_VIOLATION | RE | ✅ | 10 | RE (SECURITY_VIOLATION o'rniga qabul qilindi) |
| `11-network` | SECURITY_VIOLATION | RE | ✅ | 17 | RE (SECURITY_VIOLATION o'rniga qabul qilindi); tarmoq bloklangan (moddiy tekshiruv) |
| `12-proc-read` | SECURITY_VIOLATION | RE | ✅ | 10 | RE (SECURITY_VIOLATION o'rniga qabul qilindi); /proc niqoblangan (moddiy tekshiruv) |
| `13-symlink` | SECURITY_VIOLATION | RE | ✅ | 9 | RE (SECURITY_VIOLATION o'rniga qabul qilindi) |
| `09-fork-bomb` | SECURITY_VIOLATION | TLE | ✅ | 2104 | TLE (SECURITY_VIOLATION o'rniga qabul qilindi) |
| `14-interactive` | AC | — | 🔧 | — | hali yozilmagan — ADR-0004 da ochiq band |

## Latency (funksional to'plam)

- p50: **121 ms** · p95: **2104 ms**
- NFR byudjeti: p50 < 5000 ms, p95 < 15000 ms

## Yuklama (30 parallel submit)

- Yakunlandi: 30/30
- p50: **826 ms** · p95: **833 ms**
- O'tkazuvchanlik: 1.2 submit/s

## Xulosa

**O'TDI**

> Izolyatsiya sinovlarining **hammasi** o'tishi shart — bitta xato ham nomzodni rad etadi
> ([ADR-0004](../../docs/07-adr/0004-judge-engine.md)).
