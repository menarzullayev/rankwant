# RankWant — Migration / Rollback Notes (M1 · M2 · M3 · M10)

**Sana**: 2026-09-29
**Muallif**: Software Company — Architect (Bob)
**Holat**: 🟢 Tayyor — har M# uchun forward yo'l, deploy sharti, dump, rollback, xavf va tasdiq
**Til qoidasi**: Hujjat **o'zbek (lotin)** tilida. Texnik atama, fayl yo'li va kod **inglizcha** qoladi.
**Asos hujjatlar**:
- `deliverables/software-company/implementation-plan-phase0-2026-09-29.md` §6 — migration rejasi
- `deliverables/software-company/phase0-reconciliation-table-2026-09-29.md` §4 — D11A migration/deploy siyosati
- `deliverables/independent-review-board/acceptance-criteria-lock-2026-09-29.md` — muzlatilgan mezonlar
- `tools/check_deploy_window.py` · `tools/backup.sh` · `tools/check_deploy.sh` · `tools/rollback.sh`

> ⚠️ **Barcha migratsiya forward-only.** Sxema **orqaga qaytarilmaydi**; tuzatish ham **oldinga** migratsiya bilan. Deploy-oldi dump — **yagona** orqaga qaytish imkoni (qo'lda). Contest oynasida deploy **yo'q**.

---

## 1. Umumiy tamoyillar (D11A)

| # | Qoida | Mazmun |
|---|---|---|
| 1 | Forward-only | `add → backfill → switch → drop`, har qadam **alohida deploy**; `git revert` sxemaga qo'llanmaydi |
| 2 | Deploy oynasi | `tools/check_deploy_window.py` **majburiy** (chaqiruv `.github/workflows/deploy.yml:230`) |
| 3 | Deploy-oldi dump | Har M# oldidan DB dump **majburiy** (`tools/backup.sh --dump-only`) |
| 4 | Contest oynasi | Faol contest/arena oynasida deploy **yo'q** (10-operations, qoida №1) |
| 5 | ADR bog'lanishi | Har arxitektura o'zgarishi ADR bilan (`check_decisions.py`) |
| 6 | Feature flag yo'q | `F62` kiritilmaydi (D11A) |

**`check_deploy_window.py` chiqish kodlari:** `0` — oyna bo'sh (davom) · `1` — faol contest/arena (deploy **taqiqlanadi**) · `2` — aniqlanmadi (API javob bermadi) — `2` **«0 ta» deb o'qilmaydi**, qo'lda tasdiq talab qiladi.

**Deploy-oldi dump:** `bash tools/backup.sh --dump-only` → `pg-deploy-<stamp>.sql.gz` (MinIO'siz, sinovsiz — tez). Butunlik: `bash tools/backup.sh --verify-dump <fayl.sql.gz>` (`gzip -t` + `PostgreSQL database dump complete` trailer). Saqlash: `RANKWANT_BACKUP_DEPLOY_KEEP` (standart **7 kun**). Tiklash: `restore_test()` **alohida** `restore_test` bazasiga tiklaydi — jonli `rankwant` bazasiga **tegilmaydi**.

---

## 2. M1 — `Problem.readiness` + `legacy_unverified` backfill (WP1 · D8 · D8-F)

| Maydon | Qiymat |
|---|---|
| WP | WP1 — Content readiness |
| Mazmun | `Problem.readiness` maydoni + `legacy_unverified` backfill (**1 226 qator**) |
| Forward yo'l | `add` (nullable maydon) → `backfill` (`legacy_unverified`) → `switch` (public uchun NOT NULL) |
| Deploy oynasi | `check_deploy_window.py` exit **0** (contest oynasi bo'sh) |
| Deploy-oldi dump | `tools/backup.sh --dump-only` → `pg-deploy-*.sql.gz` + `--verify-dump` |
| Rollback — mumkin | **Forward-fix**: qayta `backfill` yoki maydonni bo'shatish (nullable); oxirgi chora — dump'ni **qo'lda** tiklash |
| Rollback — mumkin emas | `git revert` bilan sxemani orqaga qaytarish; maydonni shu deploy'da `drop` qilish (faqat keyingi deploy) |
| Xavf | Backfill default noto'g'ri bo'lsa **hamma public masala** bloklanadi (graded contestga kirmaydi) |
| Aniqlash | SQL `SELECT count(*) WHERE is_public AND readiness IS NULL` = **0** bo'lmasa; pytest `test_problem_readiness.py` R8 (`graded_requires_validated`); `restore_test` dump butunligini tasdiqlaydi |
| Tasdiqlovchi | software-engineer (ijro) · `check_deploy_window.py` exit 0 (gate) · owner (deploy oynasi) |

---

## 3. M2 — Judge izolyatsiyasi (WP7 · D3 · D10)

| Maydon | Qiymat |
|---|---|
| WP | WP7 — Judge hardening |
| Mazmun | `privileged` + `cgroup: host` olib tashlash, userns + seccomp + `USER` — **bir bosqichda** |
| Forward yo'l | **Infratuzilma migratsiyasi** (DB emas): `docker-compose.yml` + `services/judge-go/Dockerfile` + `services/judge-go/sandbox.go` **bir deploy'da** (oraliq `cap_drop` bosqichi **yo'q**) |
| Deploy oynasi | `check_deploy_window.py` exit **0**; **qo'shimcha shart** — **U1 bake-off PASS** |
| Deploy-oldi dump | `tools/backup.sh --dump-only` → `pg-deploy-*.sql.gz` (rollback uchun asos; sxema o'zgarmaydi) |
| Rollback — mumkin | **Forward**: `privileged` ni qayta qo'shish (compose diff). Image teglari per-SHA bo'lmagani uchun eski image'ga qaytish **yo'q** — kodni qayta qurish kerak |
| Rollback — mumkin emas | Avtomatik sxema rollback (sxema o'zgarmaydi); `2026-09-20` dan SHA obraz teglari **saqlanmaydi** (`tools/rollback.sh:2-7`), `rollback.sh <sha>` ataylab rad etadi |
| Xavf | nsjail regressiyasi → **0 verdict** (judge ishlamaydi) |
| Aniqlash | **U1 bake-off 25 case** (xususan `05-mle` xavfsizlik darvozasi · `09-fork-bomb`); judge **p95 latency** raqami; `tests/security/run.sh` |
| Tasdiqlovchi | software-engineer (ijro) · **U1 PASS** (evidence gate, shart) · `check_deploy_window.py` exit 0 · owner (deploy oynasi) |

> ⚠️ **U1 FAIL** → M2 **boshlanmaydi**; **yangi owner decision** ochiladi (WP7 yo'li qayta ko'riladi). Bu — decision emas, evidence gate.

---

## 4. M3 — `User.origin` + backfill (WP3 · D9)

| Maydon | Qiymat |
|---|---|
| WP | WP3 — Data origin |
| Mazmun | `User.origin` ustuni + enum (`real` · `demo` · `imported` · `staff`); **`Attempt.origin` YO'Q** |
| Forward yo'l | `add` (ustun + enum) → `backfill` (tasnif) → `switch` |
| Deploy oynasi | `check_deploy_window.py` exit **0** |
| Deploy-oldi dump | `tools/backup.sh --dump-only` → `pg-deploy-*.sql.gz` + `--verify-dump` |
| Rollback — mumkin | **Forward-fix**: qayta `backfill` (tasnifni tuzatish); dump'ni **qo'lda** tiklash |
| Rollback — mumkin emas | Avtomatik sxema rollback; `imported` ni `real` bilan birlashtirish (alohida qiymat — D9 talabi) |
| Xavf | Backfill **~10 001 seed user**ni noto'g'ri tasniflasa segmentatsiya (North Star) buziladi |
| Aniqlash | Backfill **audit raqami** chop etiladi; North Star SQL `origin='real'` bilan (JOIN) xatosiz ishlaydi; U2 (seed user aniq soni) o'lchovi |
| Tasdiqlovchi | software-engineer (ijro) · `check_deploy_window.py` exit 0 (gate) · owner (deploy oynasi) |

---

## 5. M10 — Tarixiy `RE` qatorlarni qayta yorliqlash (WP2 · D11B)

| Maydon | Qiymat |
|---|---|
| WP | WP2 — Verdict taxonomy (faqat qolgan ish) |
| Mazmun | **18 163** `RE` qatorni `RE_SIGNAL` / `RE_EXIT` ga qayta yorliqlash |
| Forward yo'l | `backfill` (yorliq) → `switch` |
| Deploy oynasi | `check_deploy_window.py` exit **0** |
| Deploy-oldi dump | `tools/backup.sh --dump-only` → `pg-deploy-*.sql.gz` + `--verify-dump` |
| Rollback — mumkin | **Forward-fix**: yangi qayta yorliqlash; dump'ni **qo'lda** tiklash |
| Rollback — mumkin emas | Avtomatik rollback; shipped `RE_SIGNAL`/`RE_EXIT` split va i18n parity ni **qayta yozish** (D11B taqiqlaydi) |
| Xavf | Yorliq o'zgarsa **384 569 tarixiy `Attempt`** bilan mos kelmasligi (ko'rsatishda xato) |
| Aniqlash | `check_verdict_codes.py` yashil; `test_verdict_taxonomy.py`; i18n parity (**10 til**) testi |
| Tasdiqlovchi | software-engineer (ijro) · `check_deploy_window.py` exit 0 (gate) · owner (deploy oynasi) |

---

## 6. Umumiy deploy tartibi

Har M# uchun **bir xil** ketma-ketlik (forward-only):

1. **Oyna tekshiruvi** — `python tools/check_deploy_window.py` → exit `0` bo'lishi shart (`1` → to'xta; `2` → qo'lda tasdiq, «0 ta» deb o'qilmaydi).
2. **Deploy-oldi dump** — `bash tools/backup.sh --dump-only` → `pg-deploy-<stamp>.sql.gz`; `bash tools/backup.sh --verify-dump <fayl>` bilan butunlikni tasdiqla.
3. **ADR bog'lanishi** — `check_decisions.py` (o'zgarish ADR bilan bog'langan).
4. **Deploy** — `bash tools/deploy.sh --yes` (yoki CI `.github/workflows/deploy.yml`).
5. **Post-deploy tekshiruv** — `tools/check_deploy.sh`: konteynerlar manba kodga mos (Python fayl hash'i · Next.js `org.rankwant.git-sha` yorlig'i).
6. **Dalil yozish** — natija va audit raqami traceability matritsasiga (`acceptance-criteria-traceability-matrix-2026-09-29.md`) qayd etiladi.

**Har M# alohida deploy** — bir deploy'da bir M# (aralashmaydi).

---

## 7. Abort sharti

| Shart | Harakat |
|---|---|
| `check_deploy_window.py` exit **1** (faol contest/arena) | **ABORT** — contest tugagach qayta urinish |
| `check_deploy_window.py` exit **2** (aniqlanmadi) | **ABORT** — qo'lda tasdiq bo'lmaguncha davom etilmaydi |
| `--verify-dump` yiqildi (butunlik tasdiqlanmadi) | **ABORT** — dump tiklanmaydigan bo'lsa deploy qilinmaydi |
| Migratsiya jarayonida xato | **STOP** — forward-fix yoki `pg-deploy-*.sql.gz` dump'ni **qo'lda** tiklash |
| **M2** uchun: **U1 FAIL** | **ABORT** — yangi owner decision; WP7 shu qarorgacha **bloklangan** |
| `check_deploy.sh` mos emas (eskirgan konteyner) | **STOP** — qayta qurish (forward) |

> **Qoida:** shubhada — **to'xta**. «Yashil deb o'qish» taqiqlanadi (`exit 2` ≠ oyna bo'sh).

---

**STATUS:** Migration / Rollback Notes — tayyor. 4 M# (M1 · M2 · M3 · M10) — forward-only; har biriga deploy oynasi sharti, deploy-oldi dump, rollback doirasi, xavf+aniqlash va tasdiqlovchi yozildi. Abort sharti §7.
