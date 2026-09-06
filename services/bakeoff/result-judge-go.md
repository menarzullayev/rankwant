# Bake-off natijasi — `judge-go`

Sana: 2026-09-06 20:26 · Wall: 13.6s

| Case | Kutilgan | Kelgan | Holat | total_ms | Izoh |
| ---- | -------- | ------ | ----- | -------- | ---- |
| `01-aplusb` | AC | AC | ✅ | 856 |  |
| `02-wa` | WA | WA | ✅ | 834 |  |
| `03-tle-cpu` | TLE | TLE | ✅ | 2837 | time_ms=2001 — wall clock o'lchanayotganga o'xshaydi, CPU emas |
| `04-idleness` | IDLENESS | IDLENESS | ✅ | 3003 |  |
| `05-mle` | MLE | MLE | ✅ | 889 |  |
| `06-re` | RE | RE | ✅ | 115 |  |
| `07-ce` | CE | CE | ✅ | 16 |  |
| `08-ole` | OLE | OLE | ✅ | 2004 |  |
| `10-file-write` | SECURITY_VIOLATION | RE | ✅ | 10 | RE (SECURITY_VIOLATION o'rniga qabul qilindi) |
| `11-network` | SECURITY_VIOLATION | RE | ✅ | 16 | RE (SECURITY_VIOLATION o'rniga qabul qilindi); tarmoq bloklangan (moddiy tekshiruv) |
| `12-proc-read` | SECURITY_VIOLATION | RE | ✅ | 9 | RE (SECURITY_VIOLATION o'rniga qabul qilindi); /proc niqoblangan (moddiy tekshiruv) |
| `13-symlink` | SECURITY_VIOLATION | RE | ✅ | 11 | RE (SECURITY_VIOLATION o'rniga qabul qilindi) |
| `09-fork-bomb` | SECURITY_VIOLATION | TLE | ✅ | 3004 | TLE (SECURITY_VIOLATION o'rniga qabul qilindi) |
| `14-interactive` | AC | — | 🔧 | — | hali yozilmagan — ADR-0004 da ochiq band |

## Latency (funksional to'plam)

- p50: **834 ms** · p95: **3003 ms**
- NFR byudjeti: p50 < 5000 ms, p95 < 15000 ms

## Yuklama (30 parallel submit)

- Yakunlandi: 30/30
- p50: **846 ms** · p95: **855 ms**
- O'tkazuvchanlik: 1.2 submit/s

## Xulosa

**O'TDI**

> Izolyatsiya sinovlarining **hammasi** o'tishi shart — bitta xato ham nomzodni rad etadi
> ([ADR-0004](../../docs/07-adr/0004-judge-engine.md)).
