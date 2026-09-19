# 50k qarorlari — implementatsiya va o‘lchov

**Sana:** 2026-09-19  
**Asos:** [RECOMMENDATIONS.md](RECOMMENDATIONS.md) §12 (7 ta qulflangan qaror).  
**Usul:** kod working tree; o‘lchov shu kechada qayta yuritildi. k6 20/50/100 **qayta yuritilmadi** — login origin hali eski image, 8300 jonli origin, 1000+ VU taqiqlangan.

> Tirik siyosat emas. Deploy/commit so‘ralmagan.

---

## 1. Bajarilgan ishlar

| # | Qaror | Modul / fayl |
|---|---|---|
| 1 | Modular monolit + replica | Yangi biznes-servis yo‘q. `docker-compose.replicas.yml` + `compose/Caddyfile.replicas` (`origin-lb`, sticky yo‘q). Sukutda preview **bunisiz**. |
| 2 | Bitta Postgres + indeks | `attempt_pending_feed`, `attempt_user_feed` (`judging` 0007); `problem_public_diff` (`problems` 0022). `docker-compose.yml`: `shared_preload_libraries=pg_stat_statements`. `CREATE EXTENSION` — data hostda qo‘lda (CI image preload’siz). Replica/shard yo‘q. |
| 3 | Redis + mehmon CDN | `core/cache.py` `cache_delete`. Redis: `platform-stats` (60 s), `auth-providers` (60 s), contest standings 10 s + `_write` invalidatsiya, arena standings 3 s. Mehmon HTML: `/`, `/login` (`?tab=`), `/register`, `/terms`, `/privacy`; `rw_exp` yozilmaydi. Worker: `l*`/`p*`/`r*`/`t*` olib tashlandi, aniq yo‘llar. |
| 4 | Celery + Redis | O‘zgarmagan. `requirements.lock` da Kafka/Sentry yo‘q. Judge navbati Redis. |
| 5 | CF + web×2/api×2 | Overlay + `GUNICORN_WORKERS` (Dockerfile/compose/`.env.example`). Web healthcheck `GET /`. Sticky yo‘q. |
| 6 | CF + SLO, Sentry yo‘q | `GET /api/v1/slo/` (`SloView`) — `judge_queue` + checks; readiness `HealthView` o‘zgarmagan. `tools/check_slo.py`. |
| 7 | Compose to‘rt host | `compose/four-host/README.md`. K8s/managed yo‘q. |

Darvoza: `tools/check_decisions.py` → **27** qoida (`scale_50k_locked` + login CDN). Salbiy: `neg_decisions_login_*`.

---

## 2. O‘lchov — oldingi baseline bilan

### 2.1 Performance (jonli origin `127.0.0.1:8300`, CF’siz)

`curl -w time_starttransfer`, mehmon, `Host: rankwant.uz`, 12 ketma-ket so‘rov. k6 emas.

| Yo‘l | Baseline tinch TTFB | Hozir min / med / p95 | `Cache-Control` hozir | Baseline header |
|---|---|---|---|---|
| `GET /` | 27–29 ms (09-17); keyin 18 ms | **8 / 10 / 17 ms** | `public, s-maxage=30, stale-while-revalidate=86400` | 09-17: `private, no-store` |
| `GET /login?tab=login` | 12–13 ms (09-19) | **13 / 13 / 16 ms** | `private, no-store` + `Set-Cookie: rw_exp` | xuddi (eski image) |
| `GET /login?tab=register` | 13 ms (09-19) | **11 / 13 / 24 ms** | `private, no-store` + `rw_exp` | xuddi |
| `GET /terms` | — | **6 / 7 / 8 ms** | `private, no-store` + `rw_exp` | — |
| `GET /api/v1/auth/providers/` | — | **2 / 3 / 3 ms** | — | — |
| `GET /api/v1/stats/` | — | **3 / 3 / 4 ms** | — | — |
| `GET /api/v1/health/` | — | **8 / 9 / 12 ms** | — | — |

k6 HTML-only (qayta yuritilmadi; 09-17/19 sonlari):

| Ssenariy | 20 VU p95 | 50 VU p95 | 100 VU p95 | Spike 100/200/300 p95 | Shift |
|---|---|---|---|---|---|
| `/` (09-17) | 521 ms | 657 ms | **1.65 s** | — | — |
| `/login?tab=login` (09-19) | 42 ms | 46 ms | 214 ms | 527 ms / 1.00 s / 1.56 s | ~180/s |
| `/login?tab=register` (09-19) | 24 ms | 51 ms | 105 ms | 494 ms / 997 ms / 1.43 s | ~185–192/s |

### 2.2 Performance (CF, bitta/bir necha `curl`, k6 emas)

| | 09-17/19 baseline | 2026-09-19 qayta |
|---|---|---|
| `https://rankwant.uz/` | `DYNAMIC`, Worker **151 ms**, TTFB **431 ms**, `private, no-store` | `Cache-Control: public, s-maxage=30…`, **`cf-cache-status: HIT`** (`Age: 7`), Worker sarlavhasi **yo‘q**. Yangi TLS har `curl` da TTFB 463–687 ms (med **507 ms**) — usul farqi; kesh holati — yutuq. |
| `https://rankwant.uz/login?tab=login` | `DYNAMIC`, Worker **194 ms**, `rw_exp` | Hali **`DYNAMIC`**, `private, no-store`, `rw_exp`. TTFB 627–696 ms (shu mashina). |
| `https://rankwant.uz/login?tab=register` | `DYNAMIC`, Worker **203 ms** | Hali **`DYNAMIC`**, `rw_exp`. |

Bosh sahifa CDN (#110) jonli. Login/huquqiy kengaytirish **kodda bor, image/Worker/CF qoidasi yo‘q**.

### 2.3 Coverage

| | Oldin | Hozir |
|---|---|---|
| `core.cache` (fail-open + `cache_delete`) | alohida o‘lchov yo‘q | **100%** (27 stmt, 0 miss) |
| Scale to‘plam (`test_scale_cache` + Slo + oauth + arena + contests, 107 test) | `test_scale_cache.py` yo‘q edi | **73%** tanlangan 7 modul (1315 stmt, 351 miss) |
| Yangi API testlar | 0 | **6** (`providers` hit, standings hit, standings invalidate, arena hit, delete, fail-open) + `TestSlo` |
| `home-cache` vitest | 8 (faqat `/`) | **11/11** (145 ms). `@vitest/coverage-v8` o‘rnatilmagan — reporter yo‘q. |

### 2.4 Complexity (AST / decision token)

| Modul | Chiziq | Ko‘rsatkich |
|---|---|---|
| `core/cache.py` | 65 | max CC **2** (`get`/`set`/`delete`) |
| `home-cache.ts` | 165 | ~24 decision token (`isGuestCachePath` + cookie) |
| `SloView` + `check_slo.py` | 54 (tool) | max CC **4** |
| `contests/services.py` | 397 | max CC 14 (`rebuild_standings` — avvaldan) |
| `check_decisions.scale_50k_locked` | — | CC 14 (ko‘p `if`, darvoza) |

### 2.5 Darvozalar

| Tekshiruv | Natija |
|---|---|
| `check_decisions.py` | **27/27** (oldingi 26 + `scale_50k_locked`) |
| `check_negative.py` | **200/200** |
| `check_docs.py` | 134 markdown, 0 xato |
| `check_env_example.py` | 72 o‘zgaruvchi |
| `check_slo.py` → `:8301` | health **200 ok**; slo **404** (eski API image) |
| ruff (API o‘zgarishlar) | yashil |
| OpenAPI | `/api/v1/slo/` `schema.yml` da |

---

## 3. Aniqlangan muammolar

1. **Jonli preview yangilanmagan.** `:8300` login/terms/privacy hali `private, no-store` + `rw_exp`. `:8301` `/api/v1/slo/` **404**. Indeks/Redis kesh/SLO image’da yo‘q.
2. **Worker deploy qilinmagan.** `wrangler.toml` repo’da `l*` ni olib tashlaydi; jonli login hali `DYNAMIC` (Worker).
3. **CF Cache Rule** hali asosan `/`. Login HIT uchun dashboard qoidasini kengaytirish + origin header kerak.
4. **`pg_stat_statements`:** compose preload yozilgan; mavjud volume recreate + `CREATE EXTENSION` qilinmagan.
5. **`docker-compose.replicas.yml` preview’ga qo‘yilmagan** (qasddan — RAM). To‘rt host VM yo‘q.
6. **k6 20/50/100** yangi login kodi ustida qayta o‘lchanmadi — eski image ni «yutuq» deb yozish noto‘g‘ri bo‘lardi.
7. Vitest coverage paketi `package.json` da yo‘q — web qamrovi foizi o‘rniga 11/11 test.

NFR (sahifa p95 < 1 s) 100 VU homepage baseline’da yiqilgan (1.65 s). CDN HIT shu tashriflarni origin’dan olib tashlaydi; login origin shift ~180/s **deploy qilinmaguncha** o‘zgarishsiz.
