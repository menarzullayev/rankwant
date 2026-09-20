# RankWant — joriy (as-built) tizim arxitekturasi

**Sana:** 2026-09-20  
**Holat:** tadqiqot yozuvi (tirik siyosat emas)  
**Manba:** `apps/api`, `apps/web`, `services/judge-go`, `docker-compose.yml`, ADR-0002…0026, `docs/06-architecture` (locked 2026-09-06)

> Amaldagi qoidalar `docs/06` / `docs/08` / ADR da. Shu yozuv **koddagi hozirgi tuzilma** ni tushuntiradi: 06 da ochiq qolgan «Data flow yozma emas» boʻshligʻini toʻldiradi. Zid kelganda locked hujjat + ADR ustun; kod ularni buzsa — yangi ADR.

Bogʻliq: [MODULES.md](MODULES.md) · [FLOWS.md](FLOWS.md) · [DIAGRAMS.md](DIAGRAMS.md)

---

## 1. Bir jumla

RankWant — **modular monolit**: foydalanuvchi bitta HTTPS saytni koʻradi; ichida Next.js web, Django/DRF API, Celery orkestr va **izolyatsiya qilingan** Go+nsjail judge ishlaydi. Yangi deployable biznes-servis ochilmagan (50k qarori: replica, mikroservis emas).

## 2. Qatlamlar

```
┌─────────────────────────────────────────────────────────────┐
│ 0. Chekka — Cloudflare (CDN, Tunnel, Worker 503, Vary)      │
└────────────────────────────┬────────────────────────────────┘
                             │ HTTPS  rankwant.uz
┌────────────────────────────▼────────────────────────────────┐
│ 1. Web — Next.js 16 + React 19 + proxy.ts + i18n            │
│    SSR: API_BASE_INTERNAL    brauzer: NEXT_PUBLIC_API_BASE  │
└────────────────────────────┬────────────────────────────────┘
                             │ REST /api/v1  (session cookie | PAT)
┌────────────────────────────▼────────────────────────────────┐
│ 2. API + Celery — Django 5.2, 19 app, gunicorn, worker/beat │
│    View = HTTP    services.py = yozuv                      │
└───────────────┬────────────────────────────┬────────────────┘
                │                            │
     ┌──────────▼──────────┐      ┌──────────▼──────────┐
     │ 3a. Postgres 16     │      │ 3b. Redis 7         │
     │ metadata, ledger,   │      │ sessiya, Celery,    │
     │ standings           │      │ judge jobs/results  │
     └─────────────────────┘      └──────────┬──────────┘
                                             │ PULL (BRPOP)
                                  ┌──────────▼──────────┐
                                  │ 4. Judge (alohida)  │
                                  │ Go + nsjail         │
                                  │ DB credential YOʻQ  │
                                  │ kiruvchi port YOʻQ  │
                                  └──────────┬──────────┘
                                             │ test fayllari
                                  ┌──────────▼──────────┐
                                  │ 3c. S3 / R2 / MinIO │
                                  │ statement, test,    │
                                  │ avatar              │
                                  └─────────────────────┘
```

| # | Qatlam | Vazifa | Masʼuliyat chegarasi |
|---|---|---|---|
| 0 | Chekka | Domen, kesh, tunnel | Mehmon HTML ni keshlaydi; `/api/*` ni API origin ga beradi. Kirgan sessiya `private, no-store`. |
| 1 | Web | SSR, i18n, UI | Biznes qoida yozmaydi. Cookie ni API ga uzatadi. PAT ishlatmaydi (ADR-0008). |
| 2 | API + worker | REST, sessiya, orkestr | Barcha yozuv service layer da. Judge ga HTTP yubormaydi — faqat Redis ga job. |
| 3 | Maʼlumot | Holat | Metadata Postgres da; test/statement S3 da; navbat/kesh Redis da. |
| 4 | Judge | Foydalanuvchi kodi | Faqat Redis + S3. `DATABASE_URL` berilsa process `exit 1`. |

## 3. Runtime (preview, bitta mashina)

`docker-compose.yml` + `docker-compose.public.yml`, loyiha nomi **`rankwant`**.

| Servis | Obraz | Vazifa |
|---|---|---|
| `web` | `apps/web` | Next.js SSR. Preview: `127.0.0.1:8300` |
| `api` | `apps/api` | gunicorn. Preview: `127.0.0.1:8301` |
| `worker` | **shu** `apps/api` | Celery: `drain_results`, standings, reyting |
| `beat` | **shu** `apps/api` | Jadval (2s / 60s / 1 soat) |
| `migrate` | **shu** `apps/api`, alohida obraz | Bir martalik `manage.py migrate` |
| `judge` | `services/judge-go` | privileged + cgroup host |
| `postgres` | postgres:16 | `pg_stat_statements` |
| `redis` | redis:7 | uch vazifa bitta instansda |
| `minio` | quay.io/minio | lokal S3 |

`api` / `worker` / `beat` / `migrate` — bitta Dockerfile, lekin **toʻrt obraz**. Faqat `api` ni qurish worker ni eski kodda qoldiradi (oʻlchangan: verdikt `IE`).

Maqsad topologiya (`compose/four-host`): `app` · `web` · `judge×N` · `data`. Hozir qurilmagan. `docker-compose.replicas.yml` (web×2 / api×2) sukutda oʻchiq; jonli preview ga qoʻllanmaydi.

## 4. Auth chegarasi

| Kanal | Mexanizm | Kod |
|---|---|---|
| Web (1-tomon) | Django session, Redis backend, `httpOnly` + `Secure` + `SameSite=Lax`, 30 kun | `core.views` Login/Logout; web `server-session.ts` |
| API / bot | PAT `rw_<32B>`, SHA-256, scope `read` \| `submit` \| `contest:manage`, ≤1 yil, ≤10 faol | `core.models.ApiToken` |
| Google / GitHub / Telegram | OIDC Authorization Code → session | `SocialStartView` / `SocialCallbackView` |

Telegram HMAC login vidjeti olib tashlangan — u ham OIDC.

## 5. Redis kalitlari (judge)

| Kalit | Yoʻnalish |
|---|---|
| `rankwant:judge:jobs` | API `LPUSH` → judge `BRPOP` |
| `rankwant:judge:results` | judge `LPUSH` → worker `BRPOP` (`judging.drain_results`, 2s) |

Protokol: `services/bakeoff/protocol.md`. Provider: `judging.provider.RedisJudgeProvider` (`JUDGE_PROVIDER=own|memory`).

## 6. Celery beat

| Task | Interval | Nima uchun |
|---|---|---|
| `judging.drain_results` | 2 s | Natija navbatda qolmasin |
| `judging.reap_stuck` | 60 s | Judge yiqilsa PENDING abadiy qolmasin |
| `contests.finalize_due` | 60 s | Reyting + standings; hack fazasini kutadi |
| `hacks.close_due` | 60 s | Hack oynasi yopilmasa musobaqa yakunlanmaydi |
| `hacks.reap_stuck` | 300 s | Javobsiz hack musobaqani ushlab turadi |
| `arena.finalize_due` / `duels.finalize_due` | 60 s | Vaqt oynasi |
| `blog.announce_published` | 300 s | Post eʼlon |
| `ratings.refresh_activity` | 3600 s | 30 kunlik oyna pasayishi |
| `core.warn_email_quota` | 3600 s | Bepul email zanjiri 80% |

## 7. Qattiq qoidalar (kodda majburiy)

1. **Judge izolyatsiyasi** — foydalanuvchi kodi faqat judge hostda (06 🔒, ADR-0004).
2. **Qvant ledger** — balans toʻgʻridan-toʻgʻri yozilmaydi (`qvant.ledger`, ADR-0002).
3. **Reyting audit** — har delta `RatingHistory` da sabab bilan (principle #2).
4. **Attempt avval DB** — keyin navbat (`judging.views.create` + `enqueue`).
5. **Soft-delete** — foydalanuvchi kontenti (attempt, transaction) oʻchirilmaydi.
6. **migrate ham quriladi** — aks holda sxema orqada qoladi.

## 8. Hujjat vs kod

`docs/06-architecture` 2026-09-06 da qulflangan. Oʻshandan beri kodda: 19 Django app, 10 til, OIDC, CDN mehmon kesh, auto-deploy watcher, Go+nsjail gʻolib. 06 dagi «judge bake-off ochiq» va «data flow yoʻq» — shu yozuv sanasida yopilgan **tahlil** sifatida, locked matnni almashtirmasdan.

Oʻzgartirish = yangi ADR, keyin 06 yangilash.
