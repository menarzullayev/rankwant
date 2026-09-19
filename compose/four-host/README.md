# To‘rt host — 50k qaror (2026-09-19)

K8s yo‘q. Har host o‘z `docker compose` ni yuritadi. Asosiy fayllar
repo ildizidagi `docker-compose.yml` (+ ixtiyoriy `docker-compose.public.yml`).

| Host | Servislar | Tarmoq |
|---|---|---|
| **data** | postgres, redis, minio | ichki; app/judge shu yerga ulanadi |
| **app** | migrate, api, worker, beat | → data; web → api:8000 |
| **web** | web | → app `API_BASE_INTERNAL`; CF → 8300 |
| **judge** ×N | judge | → data Redis/S3; kiruvchi port yo‘q, `DATABASE_URL` yo‘q |

Replica (bir hostda): ildizdagi `docker-compose.replicas.yml`.

## data

```bash
docker compose up -d postgres redis minio
# pg_stat_statements: image `shared_preload_libraries` bilan
docker compose exec postgres psql -U rankwant -d rankwant \
  -c "CREATE EXTENSION IF NOT EXISTS pg_stat_statements;"
```

## app

`DATABASE_URL`, `REDIS_URL`, `S3_ENDPOINT` — data host manzili.
`GUNICORN_WORKERS` — CPU-1 (masalan 8).

```bash
docker compose up -d migrate
docker compose up -d api worker beat
```

## web

`API_BASE_INTERNAL=http://<app-host>:8000/api/v1`

```bash
docker compose up -d web
```

## judge

`REDIS_URL` / S3 — data. `DATABASE_URL` qo‘ymang.

```bash
docker compose up -d judge
# contest oldidan host qo‘shing; HPA 10 s spike’ga ulgurmaydi
```

Live contest paytida deploy yo‘q (`docs/10-operations`).
