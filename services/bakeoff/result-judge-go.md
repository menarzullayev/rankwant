# Bake-off natijasi — `judge-go`

Sana: 2026-09-10 14:25 · Wall: 9.8s

| Case | Kutilgan | Kelgan | Holat | total_ms | Izoh |
| ---- | -------- | ------ | ----- | -------- | ---- |
| `01-aplusb` | AC | AC | ✅ | 1160 |  |
| `02-wa` | WA | WA | ✅ | 1189 |  |
| `03-tle-cpu` | TLE | TLE | ✅ | 1650 |  |
| `04-idleness` | IDLENESS | IDLENESS | ✅ | 3003 |  |
| `05-mle` | MLE | MLE | ✅ | 1188 |  |
| `06-re` | RE_SIGNAL | RE_SIGNAL | ✅ | 150 |  |
| `07-ce` | CE | CE | ✅ | 12 |  |
| `08-ole` | OLE | OLE | ✅ | 12 |  |
| `10-file-write` | SECURITY_VIOLATION | RE_EXIT | ✅ | 24 | RE_EXIT (SECURITY_VIOLATION o'rniga qabul qilindi) |
| `11-network` | SECURITY_VIOLATION | RE_EXIT | ✅ | 24 | RE_EXIT (SECURITY_VIOLATION o'rniga qabul qilindi); tarmoq bloklangan (moddiy tekshiruv) |
| `12-proc-read` | SECURITY_VIOLATION | RE_EXIT | ✅ | 24 | RE_EXIT (SECURITY_VIOLATION o'rniga qabul qilindi); /proc niqoblangan (moddiy tekshiruv) |
| `13-symlink` | SECURITY_VIOLATION | RE_EXIT | ✅ | 20 | RE_EXIT (SECURITY_VIOLATION o'rniga qabul qilindi) |
| `14-interactive` | AC | AC | ✅ | 13 |  |
| `15-java-compile` | AC | AC | ✅ | 336 |  |
| `16-re-exit` | RE_EXIT | RE_EXIT | ✅ | 43 |  |
| `17-pe` | PE | PE | ✅ | 410 |  |
| `18-wrong-test` | WRONG_TEST | WRONG_TEST | ✅ | 0 | judge_meta.total_ms yo'q — latency o'lchab bo'lmaydi |
| `09-fork-bomb` | SECURITY_VIOLATION | TLE | ✅ | 542 | TLE (SECURITY_VIOLATION o'rniga qabul qilindi) |

## Latency (funksional to'plam)

- p50: **150 ms** · p95: **1650 ms**
- NFR byudjeti: p50 < 5000 ms, p95 < 15000 ms

## Xulosa

**O'TDI**

> Izolyatsiya sinovlarining **hammasi** o'tishi shart — bitta xato ham nomzodni rad etadi
> ([ADR-0004](../../docs/07-adr/0004-judge-engine.md)).
