# Local development (3 oy+ — web rebuildsiz)

**Maqsad:** UI o'zgarishlarini **Docker `web` obrazini qayta qurmasdan** ko'rish; backend (Postgres, Redis, API, judge, worker) Docker'da qoladi.

## Tez start (Windows)

```powershell
cd D:\Linux\Web_Projects\rankwant
powershell -File tools/dev-local.ps1
```

Brauzer: **http://127.0.0.1:8310/** (masalan `/about`).

Skript:

1. `docker-compose.dev-local.yml` ni ulaydi — **`web` konteyneri ishlamaydi** (profil `docker-web`).
2. Backend servislarni `--no-build` bilan ko'taradi (obraz yo'q bo'lsa bir marta `--build`).
3. `apps/web` da `next dev -p 8310` ishga tushiradi (Turbopack, hot reload).

Git Bash / Linux: `tools/dev-local.sh` (xuddi shu mantiq).

### Faqat backend yoki faqat UI

```powershell
powershell -File tools/dev-local.ps1 -BackendOnly
powershell -File tools/dev-local.ps1 -WebOnly   # API allaqachon :8301 da
```

## Muhit

| Nima | Qayerda |
| ---- | ------- |
| Next.js (UI) | Host, `:8310` |
| Django API | Docker, `127.0.0.1:8301` |
| SSE (`realtime`) | Docker, `127.0.0.1:8302` — brauzer split-stack dev'da shu portga ulanadi (prod'da tunnel same-origin) |
| Preview (eski usul) | `:8300` — faqat deploy/paritet tekshiruvi uchun |

`.env.public` **majburiy** (xuddi preview kabi). Namuna: `.env.example`.

Birinchi marta UI uchun:

```bash
cp apps/web/env.local.example apps/web/.env.local
```

(`dev-local` skripti `.env.local` yo'q bo'lsa o'zi nusxalaydi.)

## Deploy qachon kerak?

- **Kundalik frontend/backend kod** — shu oqim; PR → CI; production deploy **kerak bo'lmaguncha** kuting.
- **Production'da web/CSS/edge xatti-harakat** — vaqtincha `docker compose … --profile docker-web up -d --build web` yoki `tools/deploy.sh`.

## Portlar

`8310` — lokal UI (8300/3000 band). Boshqa port: `$env:RANKWANT_DEV_WEB_PORT=8311` va `docker-compose.dev-local.yml` dagi CORS avtomatik yangilanadi (`RANKWANT_DEV_WEB_PORT` compose env).

## Tekshiruv

```bash
curl -H "Host: rankwant.uz" http://127.0.0.1:8301/api/v1/health/
curl -s -o NUL -w "%{http_code}" http://127.0.0.1:8310/about
```

## Bog'liq

- Preview / deploy: [deploy-runbook.md](deploy-runbook.md)
- Agent port jadvali: [parallel-agents.md](parallel-agents.md) — slot ishlatganda `8310` o'rniga slot HTTP porti + compose'da `RANKWANT_DEV_WEB_PORT`
