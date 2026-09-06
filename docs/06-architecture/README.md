# 6. System Architecture

**STATUS:** locked (2026-09-06)

## Maqsad arxitektura

```
        Next.js + React 19 + TS + Tailwind        (SSR → SEO, uz/ru/en)
                        │
                        │  REST /api/v1  ← drf-spectacular → OpenAPI
                        │  session cookie (web) · Bearer PAT (API/bot)
               ┌────────▼─────────┐
               │ Django 5.2 LTS   │  + Django admin (P0-2)
               │ + DRF  (Py 3.12+)│  + mypy, service layer
               └────────┬─────────┘
       ┌────────────────┼────────────────┐
 ┌─────▼─────┐   ┌──────▼──────┐   ┌──────▼──────┐
 │ Postgres  │   │    Redis    │   │   S3 / R2   │
 │ metadata  │   │  session +  │   │  statement, │
 │           │   │  Celery +   │   │  test data  │
 │           │   │ judge navbat│   └──────┬──────┘
 └───────────┘   └──┬───────▲──┘          │
                    │       │             │
               job  │       │  natija     │ test data
                    ▼       │             ▼
        ╔═══════════════════╧═════════════════════════╗
        ║  judge.rankwant.uz — alohida host           ║
        ║  worker PULL qiladi · kiruvchi port YO'Q    ║
        ║  DB credential YO'Q · tashqi internet YO'Q  ║
        ║                                             ║
        ║  JudgeProvider ortida:                      ║
        ║    Judge0 (oraliq) · Go+nsjail · Py+isolate ║
        ╚═════════════════════════════════════════════╝
```

## Stack (qaror qilingan)

| Qatlam       | Tanlov                                                   | Sabab                                    |
| ------------ | -------------------------------------------------------- | ---------------------------------------- |
| **Backend**  | Django 5.2 LTS + DRF, Python 3.12+                       | admin → P0-2, spectacular → goal #5      |
| **Frontend** | Next.js + React 19 + TypeScript + Tailwind 4 + shadcn/ui | SSR → SEO; rankglass tajribasi           |
| **DB**       | PostgreSQL                                               | relyatsion, transaksion standings        |
| **Queue**    | Redis + Celery                                           | submit, rejudge, reyting; session va judge navbat ham shu yerda |
| **Storage**  | S3 / Cloudflare R2                                       | statement assets, test data (GB darajasi) |
| **Judge**    | o'z engine — bake-off                                    | [ADR-0004](../07-adr/0004-judge-engine.md) |
| **Realtime** | SSE + qisqa polling                                      | standings 10–30s da yetarli; WS keyin    |

Rad etilgan variantlar va sabablari: [ADR-0003](../07-adr/0003-stack-django-next.md#rad-etilgan-variantlar).

## Servislar

Monorepo `rankwant` ([ADR-0009](../07-adr/0009-monorepo.md)); deploy esa alohida hostlarga:

1. **API** (`apps/api`) — auth, problems, contests, users, ratings, qvant; Django admin
2. **Web** (`apps/web`) — Next.js SSR, uz/ru/en
3. **Worker** — Celery: submit orkestratsiya, rejudge, standings, 4 reyting hisoblash
4. **Judge** (`services/judge-*`) — alohida domen `judge.rankwant.uz`, alohida host
5. **Storage** — S3/R2

## Xavfsizlik chegarasi

Foydalanuvchi kodi **faqat** judge hostda ishlaydi. Bu muzokara qilinmaydigan shart:

- Judge host API/DB bilan bir serverda emas
- Judge host'da **kiruvchi port yo'q** — worker navbatdan ish tortadi (pull, [ADR-0004](../07-adr/0004-judge-engine.md))
- Tarmoq: judge → Redis ✅ · judge → S3 ✅ · judge → API/DB ❌ · tashqi internet ❌
- Judge host'da **DB credential bo'lmaydi**
- Til obrazlari va sandbox versiyalari pin qilinadi

Batafsil: [ADR-0004 § Xavfsizlik shartlari](../07-adr/0004-judge-engine.md).

## Auth chegarasi

| Kanal            | Mexanizm                                    |
| ---------------- | ------------------------------------------- |
| Web (birinchi tomon) | Django session, `httpOnly` cookie, Redis backend |
| API / bot        | Personal Access Token (`rw_…`, SHA-256 saqlanadi) |
| Telegram         | login widget imzosi → **session** ochiladi  |

Batafsil: [ADR-0008](../07-adr/0008-auth-session-plus-pat.md).

## Qulflash

2026-09-06: maqsad arxitektura, stack, servis chegaralari, **xavfsizlik chegarasi** va auth kanallari tasdiqlandi.
Bog'liq qarorlar: [ADR-0003](../07-adr/0003-stack-django-next.md) · [ADR-0004](../07-adr/0004-judge-engine.md) · [ADR-0008](../07-adr/0008-auth-session-plus-pat.md).
O'zgartirish = yangi ADR (`docs/07-adr/`).

**Ochiq:** judge nomzodi ([ADR-0004](../07-adr/0004-judge-engine.md) bake-off) — `JudgeProvider` interfeysi ortida, arxitekturani o'zgartirmaydi.

## Keyingi qadam

`09-development-plan` — sprintlar va bake-off spike.
