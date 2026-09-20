# Deploy end-to-end o'lchov tizimi

**Sana:** 2026-09-20  
**Holat:** tadqiqot yozuvi (tirik siyosat emas)  
**Manba:** `tools/deploy.sh`, `tools/deploy_timer.sh`, `tools/measure_deploy.sh`

> Amaldagi qoidalar `docs/10-operations/deploy-runbook.md` va CLAUDE.md da.
> Shu yozuv **nima o'lchanadi** va **nima qilinmaydi** ni tushuntiradi.

Bog'liq: [METRICS.md](METRICS.md)

---

## 1. Bir jumla

Ha — deploy jarayonini boshidan oxirigacha (E2E) o'lchash mumkin.
`tools/deploy.sh` har bir bosqich atrofida wall-clock taymer yuritadi.
Sovuq qurilish = `compose build --no-cache`. Ishlab turgan
`rankwant-*:latest` ni `rmi -f` qilish **E2E o'lchov emas**, balki
preview ni 15–40 daqiqaga o'chirish.

## 2. Qanday yurgizish

```bash
# Hech narsa o'zgarmaydi — reja va taqiqlar
bash tools/measure_deploy.sh --plan

# Issiq (kesh ishlaydi) — oddiy deploy bilan bir xil
bash tools/measure_deploy.sh --warm --yes

# Sovuq: barcha obraz qatlamlari qayta quriladi, sayt qurilish paytida turadi
bash tools/measure_deploy.sh --cold --yes

# Sovuq + ishlatilmayotgan SHA/dangling teglar (:latest qoladi)
bash tools/measure_deploy.sh --cold --purge-idle --yes

# Diagnostika: ketma-ket --no-cache (parallel E2E emas)
bash tools/measure_deploy.sh --per-image --yes
```

Hisobot: `.handoff/deploy-timing/<utc>.{log,tsv,json,md}`

To'g'ridan-to'g'ri:

```bash
RANKWANT_DEPLOY_TIMING=.handoff/deploy-timing/manual.tsv \
RANKWANT_DEPLOY_TIMING_JSON=.handoff/deploy-timing/manual.json \
bash tools/deploy.sh --yes --no-cache
```

## 3. Nima uchun `rmi -f` emas

| Usul | Sayt | Nima o'lchanadi |
|---|---|---|
| `--no-cache` (sovuq) | Qurilish paytida eski konteynerlar ishlaydi | Haqiqiy sovuq qurilish + keyin `up` |
| `rmi` ishlatilmayotgan SHA | Tegilmaydi | Faqat o'chirish vaqti (odatda soniyalar) |
| `rmi -f …:latest` + qayta qurish | Stack yo'qoladi, 15–40 daqiqa 502 | Downtime, qurilish emas |
| `compose down` / `volume prune` | Ma'lumot ketishi mumkin | Taqiqlangan |

2026-09-20 da ikkita jonli yurish: issiq ~2.6 min, judge cache miss ~15.9 min.
To'liq `--no-cache` shu mashinada 20–40+ min bo'lishi mumkin; bu yozuv
yozilganda jonli sovuq yurish **qilinmadi**.

## 4. Bosqichlar

`TIMER finish name=… sec=…` — `time.perf_counter()` (Git Bash `%N` ishonchsiz).

| Nom | `deploy.sh` qadami | Nima |
|---|---|---|
| `e2e` | qulfdan keyin → prune oxiri | Butun yurish |
| `gate` | main CI | GitHub API |
| `preflight` | 0/8 | docker, env |
| `contest_window` | 1/8 | live oyna |
| `build` | 2/8 | compose bake (parallel) |
| `dump` | 3/8 | `backup.sh --dump-only` |
| `migrate` | 4/8 | `run --rm migrate` |
| `showmigrations` | 5/8 | tasdiq |
| `up` | 6/8 | `up -d --no-deps` |
| `verify` | 7/8 | sleep 10 + `check_deploy.sh` |
| `prune` | 8/8 | `prune_docker_disk.sh` |
| `purge_idle` | measure ixtiyoriy | SHA/dangling, `:latest` emas |
| `build.<svc>` | `--per-image` | Ketma-ket, E2E emas |

`build` qatori — bake wall-clock. `build.api + build.web + …` yig'indisi
undan katta (parallel yo'qoladi). E2E uchun `e2e` va `build` ishlatiladi.
