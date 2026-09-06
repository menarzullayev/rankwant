# services/judge-go — bake-off nomzod A

**Go worker + [nsjail](https://github.com/google/nsjail)** (Apache-2.0).
[ADR-0004](../../docs/07-adr/0004-judge-engine.md) bake-off · shartnoma: [../bakeoff/protocol.md](../bakeoff/protocol.md)

## Nega nsjail

- **Apache-2.0** — copyleft majburiyati yo'q ([ADR-0003](../../docs/07-adr/0003-stack-django-next.md) yopiq kod qaroriga mos)
- **cgroup v2 native** (`--use_cgroupv2`) — isolate'dagi GRUB `systemd.unified_cgroup_hierarchy=0` hack'i kerak emas
- Google saqlaydi, namespace + seccomp-bpf + cgroups

## Qoidalar

- **Pull** — `BRPOP rankwant:judge:jobs`; kiruvchi port ochilmaydi
- `DATABASE_URL` berilsa worker **ishga tushmaydi** (`main.go` da qattiq tekshiruv) —
  [06-architecture](../../docs/06-architecture/README.md) 🔒 xavfsizlik chegarasi
- `SIGTERM` da navbatni bo'shatib chiqadi (graceful drain)

## Fayllar

| Fayl | Mas'uliyat |
| ---- | ---------- |
| `protocol.go` | job/result tuzilmalari — judge-py bilan **bir xil** |
| `sandbox.go` | nsjail chaqiruvi, cgroup v2 dan CPU/RSS o'lchash |
| `judge.go` | kompilyatsiya, testlar, verdict klassifikatsiyasi |
| `buffer.go` | chegaralangan chiqish buferi → OLE |
| `main.go` | Redis pull sikli |

## O'lchash — muhim nuqta

`time_ms` **CPU vaqti** (cgroup `cpu.stat` → `usage_usec`), wall clock emas.
Sabab: judge host yuklangan bo'lsa wall clock adolatsiz TLE beradi → reyting ishonchsiz bo'ladi.

Wall chegarasi CPU chegarasidan **3× kattaroq** qo'yiladi; farqi `IDLENESS` ni ochib beradi
(dastur kutib qoldi, sikl aylanmadi — `04-idleness` case).

## Ishga tushirish

```bash
make build && make run          # local (nsjail o'rnatilgan bo'lishi kerak)
make docker                     # yoki konteynerda
```

Konteyner **privileged** yoki kamida `--cap-add=SYS_ADMIN --cgroupns=host` bilan ishlaydi —
namespace va cgroup v2 yozish uchun.
