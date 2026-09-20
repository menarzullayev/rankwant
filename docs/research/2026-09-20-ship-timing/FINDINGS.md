# Topilmalar va qisqartirish

**Sana:** 2026-09-20  
**Holat:** tadqiqot yozuvi

Raqamlar [README.md](README.md) da. Bu yerda nima qilish kerak.

---

## 1. Web job ichida (main #182, 100 s job)

| Qadam | s | Izoh |
|---|---|---|
| npm ci | 19 | tools-only da ham |
| lint + typecheck | 22 | faqat `apps/web/**` |
| vitest | 2 | faqat web |
| i18n / email / runtime | 3 | |
| check_negative | 30 | 4 parallel nusxa |
| npm run build | 8 | faqat web |
| checkout / node setup | ~8 | |

Tools-only (#187 main): npm ci 20 s + negative 32 s = job 62 s.
Lint/build o'tkazib yuboriladi, lekin `npm ci` qoladi — `check_i18n_runtime.mjs`
`apps/web/node_modules` dagi TypeScript ni o'qiydi.

## 2. Deploy ichida (o'lchangan)

Issiq (937901, 156 s): build ~87 s, dump→prune ~69 s.
Judge miss (937900, 954 s): build ~866 s (export 228 s), qolgani ~88 s.

`verify` = sleep 10 + `check_deploy.sh`. Dump/migrate/up kichik.

## 3. Amaliy takliflar (katta → kichik)

### A. Obraz qurilmasin, agar commit obrazga tushmasa (katta)

`apps/api`, `apps/web`, `services/*`, `Dockerfile*`, `docker-compose*.yml`
tashqarisidagi main commit (docs, `tools/check_*`, runbook) live kodni
o'zgartirmaydi. Hozir `check_deploy.sh` SHA farqini «ESKIRGAN» deydi va
watcher to'liq bake qiladi.

Kutilgan yutuq: har docs/tools PR dan keyin **2.6 min** (issiqlik) yoki
tasodifiy judge miss da **16 min**. Bugun shu yo'l bilan o'nlab docs PR
ketdi.

Shart: `deploy.sh` / compose o'zi o'zgarsa — qurish kerak (skript
ishlaydi, obraz yo'q). Faqat `docs/**` + `docs/research/**` — aniq o'tkazish.

### B. Merge'dan keyin darhol watcher (o'rta)

`schtasks /run /tn "RankWant Auto Deploy"` merge oxirida, yoki interval
5 min → 1 min. O'lchangan teshik: CI yashil 16:00:21, deploy 16:05:11
(~5 min).

Kutilgan yutuq: o'rtacha **~2.5 min** live'gacha. Xavf yo'q: darvoza
hali ham yashil main talab qiladi.

### C. Tools-only CI da `npm ci` ni ajratish (o'rta)

`tools/**` o'zgarganda web job `npm ci` (14–20 s) qiladi, keyin
salbiy test. Python-only o'zgarishda (`check_decisions.py`,
`deploy_timer.sh`) Node shart emas.

Kutilgan yutuq: **14–20 s × 2** (PR + main) har tools PR da.
`check_i18n_runtime.mjs` yoki `check_negative` NODE_CASES o'zgarsa —
`npm ci` qoladi.

### D. Judge ni faqat judge manbasi o'zgaganda qurish (katta, kamdan-kam)

`deploy.sh` doim `judge` ni bake qiladi. Kesh hit arzon; miss ~10–14 min.
`services/judge-go/**` va judge Dockerfile o'zgarmasa `build` dan
chiqarish (yoki compose cache'ga ishonish yetarli — `--no-cache`
bo'lmasa).

Kutilgan yutuq: miss bo'lmagan yurishda kichik; miss oldini olish —
**10+ min**.

### E. `verify` sleep 10 → health (kichik)

`check_deploy.sh` yoki `up --wait`. Kutilgan yutuq: 0–8 s, har deploy.

### F. Lokal: deploy.sh o'zgarsa `check_negative.py decisions` (kichik)

#187 birinchi CI 69 s qizil — `_on_exit` dagi ikkinchi
`RANKWANT_LOCK_HELD` salbiy testni o'lik qildi. `decisions` guruhi
~10 s lokal. Qizil hosted yurishni oldini oladi.

### G. Qilinmasin

- Pre-push ga mypy/tsc/153 test qaytarish — 2026-09-18 da 5.8 min edi.
- `rmi -f :latest` «sovuq o'lchov» — downtime.
- Jonli `rankwant.uz` ga k6.
- Main CI ni butunlay o'tkazib yuborish: squash yangi SHA, darvoza
  shu SHA ni tekshiradi.

## 4. Nima o'lchanmadi

- API job (ruff/mypy/makemigrations) — bugungi 40 CI da `skipped`.
- Judge CI job — `skipped`.
- To'liq `--no-cache` E2E — jonli yurgizilmadi.
- #187 dan keyingi avto-deploy — log 16:08 da 2557bd4 da to'xtagan
  (o'qilgan payt).
