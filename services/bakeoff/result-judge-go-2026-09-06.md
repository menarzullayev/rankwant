# Bake-off natijasi — `judge-go`

Sana: 2026-09-06 18:50 · Wall: 17.5s

| Case | Kutilgan | Kelgan | Holat | total_ms | Izoh |
| ---- | -------- | ------ | ----- | -------- | ---- |
| `01-aplusb` | AC | CE | ❌ | 822 | kutilgan AC, kelgan CE |
| `02-wa` | WA | CE | ❌ | 825 | kutilgan WA, kelgan CE |
| `03-tle-cpu` | TLE | CE | ❌ | 840 | kutilgan TLE, kelgan CE |
| `04-idleness` | IDLENESS | IDLENESS | ✅ | 3003 |  |
| `05-mle` | MLE | CE | ❌ | 849 | kutilgan MLE, kelgan CE |
| `06-re` | RE | CE | ❌ | 25 | kutilgan RE, kelgan CE |
| `07-ce` | CE | CE | ✅ | 12 |  |
| `08-ole` | OLE | OLE | ✅ | 4004 |  |
| `09-fork-bomb` | SECURITY_VIOLATION | IDLENESS | ❌ | 7003 | kutilgan SECURITY_VIOLATION, kelgan IDLENESS |
| `10-file-write` | SECURITY_VIOLATION | RE | ✅ | 31 | RE (SECURITY_VIOLATION o'rniga qabul qilindi) |
| `11-network` | SECURITY_VIOLATION | RE | ❌ | 16 | kutilgan SECURITY_VIOLATION, kelgan RE |
| `12-proc-read` | SECURITY_VIOLATION | WA | ❌ | 11 | kutilgan SECURITY_VIOLATION, kelgan WA |
| `13-symlink` | SECURITY_VIOLATION | RE | ✅ | 9 | RE (SECURITY_VIOLATION o'rniga qabul qilindi) |
| `14-interactive` | AC | WA | ❌ | 10 | kutilgan AC, kelgan WA |

## Latency (funksional to'plam)

- p50: **31 ms** · p95: **4004 ms**
- NFR byudjeti: p50 < 5000 ms, p95 < 15000 ms

## Xulosa

**O'TMADI (XAVFSIZLIK)** — izolyatsiya sinovlari: 09-fork-bomb, 11-network, 12-proc-read

> Izolyatsiya sinovlarining **hammasi** o'tishi shart — bitta xato ham nomzodni rad etadi
> ([ADR-0004](../../docs/07-adr/0004-judge-engine.md)).
