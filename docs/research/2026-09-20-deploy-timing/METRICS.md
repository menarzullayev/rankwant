# Deploy metrikalar va o'lchov usullari

**Sana:** 2026-09-20  
**Holat:** tadqiqot yozuvi

Qisqa javob: asosiy metrika — **wall-clock soniya** har bosqich uchun.
CPU foizi yoki layer hajmi ikkinchi darajali: foydalanuvchi kutgan narsa
vaqt. Git Bash da `date +%N` ishonchsiz; soat `time.perf_counter()`.

---

## 1. E2E o'lchanadimi?

Ha. Bitta yurish = bitta `e2e` qiymati, ichida 2/8–8/8 va darvoza.
Ikki xil E2E bor va ularni aralashtirmaslik kerak:

| Rejim | Buyruq | Savolga javob |
|---|---|---|
| Issiq | `--warm` | Oddiy kod o'zgarishi qancha turadi? |
| Sovuq | `--cold` (`--no-cache`) | Barcha obrazlar noldan qancha turadi? |
| Per-image | `--per-image` | Qaysi Dockerfile qimmat? (E2E emas) |

CI hosted smoke (~9 min) va `check_deploy.sh --check` E2E deploy emas.

---

## 2. Qimmat bosqichlar

### 2.1 Image qurish (`build`)

| Metrika | Usul | Izoh |
|---|---|---|
| Wall-clock | `TIMER finish name=build` | Bake parallel; asosiy E2E qism |
| Per-service | `--per-image` yoki BuildKit `# DONE Xs` | Diagnostika |
| Cache hit | `CACHED` qatorlari soni | Issiq vs sovuq farqi |
| Export/unpack | BuildKit `exporting to docker image` | Judge da ~228 s o'lchangan |

Nima qimmat (o'lchangan, 2026-09-20):

- Judge nsjail/apt qadamlari: 35 + 132 + 107 + 48 s
- Judge export + unpack: 195.5 + 31.9 = 227.6 s
- Web Next compile: ~23–29 s (parallel, lekin bake judge oxirini kutadi)

Sovuq usul: `RANKWANT_BUILD_NO_CACHE=1` / `--no-cache`.
Dockerfile ichiga `CACHEBUST` commit **yozilmaydi**.

### 2.2 O'chirish (`purge_idle` / `prune`)

| Metrika | Usul | Izoh |
|---|---|---|
| Idle delete | `TIMER name=purge_idle` | SHA teg + dangling; `:latest` qoladi |
| Post-deploy prune | `TIMER name=prune` | `prune_docker_disk.sh` (builder prune, `--all` yo'q) |
| O'chirilgan son | `removed=` qatori | Vaqtdan ko'ra disk |

`rmi -f` ishlab turgan image ga — **metrika emas**, downtime.
`volume prune` / `system prune` — o'lchanmaydi, taqiqlangan.

Haqiqiy «hamma qatlam noldan» — o'chirish emas, `--no-cache`.
O'chirish odatda soniyalar; qurilish — o'nlab daqiqa.

### 2.3 Qayta qurish

Sovuq `build` bilan bir xil metrika. Issiq `build` dan ayirma =
kesh foydasi. Ikkalasini ketma-ket yurgizish:

```bash
bash tools/measure_deploy.sh --warm --yes   # issiq baseline
bash tools/measure_deploy.sh --cold --yes   # sovuq; sayt qurilishda turadi
```

Ikkinchi yurish `up` qiladi — qisqa reconnect. Contest oynasida
ikkalasi ham to'xtaydi (qoida №1).

### 2.4 Deploy (builddan keyin)

| Metrika | Usul | Odatiy (issiqlik) |
|---|---|---|
| `dump` | pg_dump wall-clock | ~5 s |
| `migrate` | yangi obraz `run --rm` | soniyalar–o'nlab s |
| `showmigrations` | tasdiq | soniyalar |
| `up` | yangi konteyner | ~10 s |
| `verify` | majburiy sleep 10 + check | ≥10 s |
| `prune` | SHA/dangling/builder | ~8 s |

Bu zanjir ikkala yurishda ~70–90 s edi. E2E farqining deyarli hammasi
`build` da.

---

## 3. Hisobot formati

TSV (`name`, `sec`, `utc`), JSON (`e2e_sec`, `steps[]`), MD jadval.
Log — to'liq `deploy.sh` chiqishi (`tee`).

Solishtirish: bir xil host, bir xil `RANKWANT_ENV_FILE`, contest oynasi
yopiq. `e2e` ni `build` + qolganlarga ajratish — regressiyani topadi
(masalan verify doim 10 s, build o'ssa Dockerfile).

---

## 4. Nima o'lchanmaydi (va nega)

- Jonli `rankwant.uz` ga k6 — taqiqlangan
- `replicas.yml` ni preview ga qo'llash
- Foydalanuvchilarni tozalash
- Ikkinchi Postgres / live migrate `deploy.sh` dan tashqari
- Builder `prune --all` — keyingi issiq deploy ham sovuq bo'ladi
