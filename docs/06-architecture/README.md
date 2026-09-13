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

## Deployment

### Hozirgi holat — bitta mashina (preview)

```bash
docker compose -p rankwant --env-file .env.public \
  -f docker-compose.yml -f docker-compose.public.yml up -d --build --wait
```

| Narsa | Qiymat |
|---|---|
| Host | **bitta mashina** (dual-boot Linux/Windows) |
| Tashqi kirish | Cloudflare Tunnel — ochiq port yo'q |
| Domen | `rankwant.uz` (NS — Cloudflare) |
| Sirlar | `.env.public` (gitignore'da) |
| Debug | `DJANGO_DEBUG=0` |
| Django admin | tunnel'dan chiqarilmagan; faqat `127.0.0.1:8301/admin/` |

⚠️ Bu **production emas** — [10-operations](../10-operations/README.md) uni
"ommaviy preview" deb ataydi va sababini yozadi.

### Maqsad topologiyasi — to'rt host

`app` (API + worker) · `web` (Next.js) · `judge×N` · `data` (Postgres, Redis).
Xavfsizlik chegarasidan kelib chiqadi: judge hostda **kiruvchi port yo'q**.
Batafsil: [10-operations § Deploy topologiyasi](../10-operations/README.md).

### Muhitlar

| Muhit | Qayerda | Maqsad |
|---|---|---|
| **dev** | mahalliy mashina | ishlab chiqish (`docker-compose.ci.yml`) |
| **prod** | bitta mashina (hozir preview) | foydalanuvchilar |
| **staging** | — | **yo'q** |

⚠️ **Staging yo'q** — prod'ga chiqishdan oldin oraliq tekshiruv bosqichi
yo'q. Buni qisman `ci-local.sh` va `.githooks/pre-push` qoplaydi, lekin ular
**manbani** sinaydi, ishlab turgan konteynerni emas.

⚠️ **Nomuvofiqlik:** `10-operations` dagi CI/CD tavsifi *"…→ staging deploy"*
deb yozadi, lekin staging muhiti mavjud emas. Ikkalasidan biri noto'g'ri —
qaysi biri ekani aniqlanishi kerak.

### Deploy oqimi

GitHub Actions: lint → `mypy` strict → test → OpenAPI diff → build.
Prod deploy **qo'lda tasdiqlash** bilan (contest oynasi tekshiriladi).

### Rollback

```bash
git revert <sha>
docker compose -p rankwant --env-file .env.public \
  -f docker-compose.yml -f docker-compose.public.yml up -d --build --wait
bash tools/check_deploy.sh           # 0 bo'lishi shart
```

⚠️ **Migratsiya rollback qilinmaydi** — sxema oldinga mos yoziladi
(`add → backfill → switch → drop`, alohida deploylarda). Batafsil:
[10-operations § Release va rollback](../10-operations/README.md).

## Assumptions

1. **SSE + qisqa polling standings uchun yetarli.** *"standings 10–30s da
   yetarli; WS keyin"* — ya'ni real vaqt talabi past deb baholanadi.
2. **Redis bitta instans yetarli.** U bir vaqtda session, Celery broker va
   judge navbatini ko'taradi — uch vazifa uchun ajratish kerak emas degan taxmin.
3. **Judge izolyatsiyasi sandbox bilan ta'minlanadi.** *"Til obrazlari va
   sandbox versiyalari pin qilinadi"* — lekin qaysi sandbox hali tanlanmagan
   (ADR-0004 bake-off).
4. **Bitta mashina preview uchun yetarli.** Deploy topologiyasi *"alohida
   hostlarga"* deyilgan, lekin hozirgi preview bitta mashinada.

## Open questions

1. **Judge nomzodi** ([ADR-0004](../07-adr/0004-judge-engine.md) bake-off) — `JudgeProvider` interfeysi ortida, arxitekturani o'zgartirmaydi.
2. **`Deployment` — ✅ yozildi (2026-09-13).** Muhitlar, deploy oqimi va
   rollback yuqorida. **Ochiq qolgani:** staging muhiti yo'qligi va
   `10-operations` dagi CI/CD tavsifi bilan nomuvofiqlik (yuqoriga qarang).
3. **`Data flow` yozma emas.** Diagrammada strelkalar bor, lekin zanjir matnda yo'q: `submit → navbat → judge → verdict → AttemptTestResult → Standing → reyting`. NFR maqsadi (`p50 < 5s`) qaysi qadamga tegishli ekani ko'rinmaydi.
4. **`Reliability / scalability` yo'q.** `500 parallel submit` NFR bor, lekin unga qanday erishish: worker soni, navbat sig'imi, DB ulanish hovuzi, nosozlik holatlari (Redis yiqilsa nima bo'ladi).
5. **`Key trade-offs` yozma emas.** Rad etilgan variantlar ADR-0003 ga havola qilingan, lekin *nima yo'qotilgani* shu hujjatda yo'q (masalan API va web'ni ajratish → operatsion murakkablik).

## Qulflash

**Tasdiq:** Saidakbar Narzullayev — Repo owner / maintainer, 2026-09-06.

2026-09-06: maqsad arxitektura, stack, servis chegaralari, **xavfsizlik chegarasi** va auth kanallari tasdiqlandi.
Bog'liq qarorlar: [ADR-0003](../07-adr/0003-stack-django-next.md) · [ADR-0004](../07-adr/0004-judge-engine.md) · [ADR-0008](../07-adr/0008-auth-session-plus-pat.md).
O'zgartirish = yangi ADR (`docs/07-adr/`).

## Keyingi qadam

`09-development-plan` — sprintlar va bake-off spike.
