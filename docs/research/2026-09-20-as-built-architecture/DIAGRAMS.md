# Diagrammalar

**Sana:** 2026-09-20 · [orqaga](README.md)

GitHub Mermaid. Matnli tushuntirish: [README](README.md), [MODULES](MODULES.md), [FLOWS](FLOWS.md).

## Qatlamlar

```mermaid
flowchart TB
  subgraph edge["0 Chekka"]
    CF["Cloudflare CDN + Tunnel"]
    W503["maintenance-worker 503"]
  end
  subgraph web["1 Web"]
    NX["Next.js SSR + proxy.ts"]
  end
  subgraph api["2 API + worker"]
    DJ["Django 19 app"]
    CW["Celery worker / beat"]
  end
  subgraph data["3 Maʼlumot"]
    PG["Postgres 16"]
    RD["Redis 7"]
    S3["S3 / R2 / MinIO"]
  end
  subgraph judge["4 Judge — izolyatsiya"]
    JG["judge-go + nsjail"]
  end
  CF --> NX
  W503 -.-> CF
  NX -->|"SSR API_BASE_INTERNAL"| DJ
  NX -->|"cookie session"| DJ
  DJ --> PG
  DJ --> RD
  DJ --> S3
  CW --> PG
  CW --> RD
  CW -->|"LPUSH jobs"| RD
  JG -->|"BRPOP jobs"| RD
  JG -->|"LPUSH results"| RD
  JG --> S3
  JG -.->|"taqiqlangan"| DJ
  JG -.->|"taqiqlangan"| PG
```

## Submit zanjiri

```mermaid
sequenceDiagram
  actor U as Foydalanuvchi
  participant W as Next.js
  participant A as judging.views
  participant P as Postgres
  participant R as Redis
  participant J as judge-go
  participant B as Celery beat
  participant S as ratings / contests

  U->>W: yuborish
  W->>A: POST /api/v1/attempts/
  A->>P: Attempt PENDING
  A->>R: LPUSH rankwant:judge:jobs
  A-->>W: 201 PENDING
  J->>R: BRPOP jobs
  J->>J: nsjail compile / test
  J->>R: LPUSH rankwant:judge:results
  B->>R: BRPOP results (2s)
  B->>P: apply_result
  B->>S: on_attempt_judged / standings
```

## Birinchi AC

```mermaid
flowchart LR
  V["apply_result AC"] --> USP["UserSolvedProblem get_or_create"]
  USP -->|takror| X["chiqish"]
  USP -->|birinchi| SK["recalc_skills + RatingHistory"]
  SK --> Q["qvant.on_first_accepted"]
  Q --> ST["streak + quest + ledger"]
  ST --> ACT["recalc_activity"]
```

## Musobaqa yakuni

```mermaid
stateDiagram-v2
  [*] --> scheduled
  scheduled --> running: start_at
  running --> frozen: freeze_minutes
  frozen --> waitingHack: end_at
  running --> waitingHack: end_at va freeze yoq
  waitingHack --> finalized: close_due va not hack_phase_pending
  waitingHack --> waitingHack: finalize_due 60s, kutadi
  finalized --> [*]
```

## Drain marshruti

```mermaid
flowchart TD
  R["Redis results"] --> D["drain_results"]
  D --> H{"hack_id?"}
  H -->|ha| HS["hacks.apply_hack_result"]
  H -->|yoq| C{"custom_run_id?"}
  C -->|ha| CR["apply_custom_result"]
  C -->|yoq| AR["apply_result"]
  AR --> RT["ratings.on_attempt_judged"]
  AR --> ST["standings debounce 5s"]
```
