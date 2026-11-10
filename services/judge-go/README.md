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

Konteyner **privileged emas** (ADR-0046, 2026-11-10). Compose'dagi sozlama:
`cap_drop: [ALL]`, `cap_add: [SETUID, SETGID, SETFCAP]`, `seccomp.json`
(Docker standarti + nsjail uchun 6 syscall), `no-new-privileges`,
`systempaths=unconfined`, `apparmor=unconfined` va `JUDGE_USERNS=1`.

`JUDGE_USERNS=1` bo'lsa binar ikki bosqichda ishlaydi (`userns.go`):

1. **launcher** — PID 1, root sifatida boshlanadi: worker'ni yangi user, mount
   va cgroup namespace'da ishga tushiradi (id map'ni yozish uchun uchta
   capability), keyin o'zi uid 10001 ga tushadi va zombilarni yig'adi;
2. **worker** — o'z namespace'ida konteynerning cgroup'ini yoziladigan qilib
   ulaydi, `rankwant/` subtree'ni quradi va uid 10001 ga beradi, keyin o'zi
   ham uid 10001 ga tushadi. Sandbox'dagi dastur tashqarida uid 10001.

Ishga tushishda to'rt fail-closed tekshiruv: identity (worker root emas,
capability yo'q), tarmoq, cgroup limitlari va bitta haqiqiy nsjail yurishi
(`PreflightSandbox`). Ubuntu ≥ 23.10 host'da
`kernel.apparmor_restrict_unprivileged_userns=0` kerak (CI buni
`tools/ci_stack.sh` da qiladi).
