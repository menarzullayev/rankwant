# services/judge-py — bake-off nomzod B

**Python worker + [isolate](https://github.com/ioi/isolate)** (GPL-2.0+).
[ADR-0004](../../docs/07-adr/0004-judge-engine.md) bake-off · shartnoma: [../bakeoff/protocol.md](../bakeoff/protocol.md)

## Nega isolate

- **CP dunyosining standarti** — IOI va CMS ishlatadi, eng ko'p jang qilingan sandbox
- Worker Python'da → `apps/api` bilan bitta til, kod ulashish oson
- Verdict semantikasi CP uchun tayyor (`meta` faylida `status`, `time`, `cg-mem`)

## Ma'lum cheklov — cgroup v1

isolate **cgroup v1** ga tayanadi. Zamonaviy Linux (Ubuntu 24.04+, Debian 12, bu host ham)
cgroup **v2** da ishlaydi. Ishlatish uchun GRUB'ga:

```
systemd.unified_cgroup_hierarchy=0 systemd.legacy_systemd_cgroup_controller=1
```

yozib **hostni qayta yuklash** kerak. Bu operatsion narx va bake-off'ning asosiy
o'lchov nuqtalaridan biri — nomzod A (nsjail) buni talab qilmaydi.

Ikkinchi narx: `isolate` **setuid root** binary. Judge host izolyatsiyasi
([06-architecture](../../docs/06-architecture/README.md) 🔒) shuning uchun ham majburiy.

## Qoidalar

- **Pull** — `BRPOP rankwant:judge:jobs`; kiruvchi port ochilmaydi
- `DATABASE_URL` berilsa worker **ishga tushmaydi** (`main.py` da qattiq tekshiruv)
- `SIGTERM` da navbatni bo'shatib chiqadi

## Fayllar

| Fayl | Mas'uliyat |
| ---- | ---------- |
| `protocol.py` | job/result tuzilmalari — judge-go bilan **bir xil** |
| `sandbox.py` | isolate box, `meta` faylidan CPU/RSS o'qish |
| `judge.py` | kompilyatsiya, testlar, verdict klassifikatsiyasi |
| `main.py` | Redis pull sikli |

## Ishga tushirish

```bash
pip install -e '.[dev]'
REDIS_URL=redis://localhost:6379/0 python3 main.py
# yoki
docker build -t rankwant/judge-py . && docker run --privileged --cgroupns=host rankwant/judge-py
```
