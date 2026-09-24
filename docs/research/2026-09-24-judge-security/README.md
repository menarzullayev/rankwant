# Judge container boundary — the A-1 measurement (Phase 1)

**Date:** 2026-09-24
**Status:** research record — a snapshot of one day, not living policy
**Owner of the follow-up task:** `docs/tasks/TASK-judge-security-a1.md`
(branch `feat/judge-security-a1`, worktree `wt/freebuff/judge-security`)
**Sources:** live probes against the running `rankwant` stack
(`docker network inspect`, `docker inspect`, `docker exec`, one `--rm` probe
container), the merged compose chain
(`docker compose -p rankwant -f docker-compose.yml -f docker-compose.public.yml config`),
ADR-0004 § Xavfsizlik shartlari, threat model § 7⑦ / § 8 A-1 / § 9

> Binding rules live in ADRs and `docs/06`–`docs/10`. Where this record and
> those disagree, they win. This record exists because threat model § 9 states
> the ADR-0004 deviations **as design intent**; nothing had measured the
> judge's network position **as it runs**. A-1's severity claim ("a container
> escape lands on the machine holding Postgres and Redis") is now measured,
> not inferred.

---

## 1. In one sentence

Every service on the host — the privileged judge included — sits on the single
`rankwant_default` network, the judge resolves `postgres` by name and opens a
TCP connection to `postgres:5432` **and** reaches the internet; the only thing
that keeps user code out of the database is the absence of credentials, which
is exactly the layer A-1 assumes an escape defeats.

## 2. Method (read-only, no live changes)

- No service was created, stopped or restarted inside the live project.
- The judge was probed from inside (`docker exec`) — read commands and TCP
  dial attempts only.
- One neutral probe (`python:3.12-slim`, `docker run --rm --network
  rankwant_default`) ran the same TCP matrix and removed itself on exit, so
  the matrix reflects the **network layer**, not any judge-specific quirk.
- The merge chain was read via `docker compose … config` (resolves the
  `!reset`/`!override` overlay semantics that make single-file reads lie —
  the 2026-09-21 boundary lesson).

## 3. Measured facts (2026-09-24, +05)

### 3.1 Live network membership — `rankwant_default`

| Container | IPv4 |
|---|---|
| `rankwant-judge-1` | 172.18.0.6 |
| `rankwant-postgres-1` | 172.18.0.4 |
| `rankwant-redis-1` | 172.18.0.2 |
| `rankwant-minio-1` | 172.18.0.3 |
| `rankwant-api-1` | 172.18.0.10 |
| `rankwant-worker-1` | 172.18.0.7 |
| `rankwant-beat-1` | 172.18.0.8 |
| `rankwant-web-1` | 172.18.0.9 |
| `rankwant-adminer-1` | 172.18.0.5 |

**Nine containers, one network.** The judge is a network neighbour of the
database, the queue, the object store, the API and the web tier.

### 3.2 The judge container, as configured

| Property | Measured |
|---|---|
| `privileged` | **true** |
| `cgroupns` | **host** |
| Published ports | none (`PortBindings: {}`) |
| Networks | `rankwant_default` only |
| `DATABASE_URL` | absent (the worker exits 1 if set — intact) |
| `S3_SECRET` | **`devdevdev`** — MinIO root credential (the A-2 overlap) |
| Compose label `org.rankwant.git-sha` | `4f1321c` (deploy worktree; one commit behind `main` @ `462e327`) |

### 3.3 The merged compose chain

`internal:` matches in the resolved config: **0**. No service declares a
second network. The `judge → data` split of `compose/four-host/README.md`
exists only as documentation, not in any deployed file.

### 3.4 DNS from inside the judge

`getent hosts postgres redis minio api web` → all five resolve on
172.18.0.x. A running (or escaped) process does not need to scan; the
database has a **name**.

### 3.5 TCP matrix — from the judge itself, and from the neutral probe

Identical results from both vantage points (judge: bash `/dev/tcp` +
`timeout`; probe: Python `socket.connect`):

| Target | Result | Reading |
|---|---|---|
| `postgres:5432` | **OPEN** | the database accepts TCP from the judge's network position |
| `redis:6379` | **OPEN** | expected — the queue is the judge's legitimate dependency |
| `minio:9000` | **OPEN** | expected — test data comes from here |
| `api:8000` | **OPEN** | ADR-0004 says judge → API must not exist; it is reachable |
| `web:3000` | **OPEN** | irrelevant to the judge's job, still reachable |
| `judge:8000` | REFUSED | **negative control** — the matrix is not trivially all-OPEN |
| internet `1.1.1.1:443` | **OPEN** | unrestricted egress from the judge |

## 4. What this proves, against ADR-0004 § Xavfsizlik shartlari

| Locked clause | Today (measured) |
|---|---|
| «Judge host **hech qachon** API/DB bilan bir serverda emas» | **violated at container level** — one host, one network, TCP to `postgres:5432` and `api:8000` succeeds from the judge's position |
| «Judge hostdan tashqi tarmoqqa chiqish yopiq» | **violated at container level** — internet egress is open |
| Inbound port on the judge | holds — nothing published, `judge:8000` REFUSED (the service accepts no connections) |

Threat model § 9 called the first two deviations; § 3 above is their proof on
the live stack.

## 5. The asymmetry an auditor should see

The two isolation layers are in opposite states:

- **Credential layer — intact.** No `DATABASE_URL` in the judge env; the
  worker exits 1 if one appears; no DB password is reachable. A TCP `connect`
  is not a login.
- **Network layer — absent.** Nothing in the network configuration distinguishes
  the judge from the web tier.

A-1's premise is that an escape is arbitrary code execution *with the judge's
capabilities and none of its discipline*. The credential-only defence assumes
the escaped code cannot read a credential — but the MinIO root secret
(`devdevdev`, a **public** repository value) already sits in the judge env
(§ 3.2), and hidden-test data is the asset it unlocks (threat model § 6:
"any container on the compose network — including an escaped judge — could
read or rewrite problem test data"). The network layer is what bounds the
blast radius when a credential leaks; today it is the same single network for
everything.

## 6. What this record does NOT claim

- No database authentication was attempted (the judge holds no credential —
  attempting one would itself require fabricating one).
- No sandbox escape was demonstrated. The nsjail layer is a different layer
  and it **is** verified — five `ISOLATION_CASES` run against real nsjail in
  Nightly. This record measures the **container** boundary, the layer threat
  model § 7⑦ calls "verified sandbox, unverified container".
- Not a claim that exfiltration is trivial — it is a measurement of the
  precondition A-1 is priced on.

## 7. Closure path

The fix is proposed as [ADR-0028](../../07-adr/0028-judge-container-isolation.md)
(`STATUS: proposed` — owner sign-off pending), phased in
`docs/tasks/TASK-judge-security-a1.md`:

1. `judge-net` network with `internal: true` — judge leaves `default`;
   Postgres/API/Web become unreachable by construction (compose change).
2. Separate `judge-queue` Redis instance (also narrows the § ④ SPOF).
3. `PreflightNetwork` in `judge-go`/`judge-py` — fail closed at startup if
   `postgres:5432` is reachable (code layer, the `DATABASE_URL`-refusal
   pattern applied to the network).
4. MinIO credential for the judge scoped read-only (closes the judge-side
   half of A-2).
5. Static guard + negative tests (`check_compose.py`,
   `check_decisions.py`, `check_negative.py`) and a Nightly dynamic proof in
   the existing `e2e` stack — no new heavy job.

Details and phase gates: `docs/tasks/TASK-judge-security-a1.md`.

## 7b. Compose topology as implemented (Phase 4, same day)

The remediation shipped the same day (one PR, per HITL decision ④). The
resolved chain `docker-compose.yml + docker-compose.public.yml` now yields
(measured via `docker compose config` on 2026-09-24):

- `judge` → `['judge-net']` only; `judge-net` has `internal: true` —
  the two broken ADR-0004 security lines are now enforced at the
  container layer (no route to the database network, no egress);
- `judge-queue` (new Redis) and `minio` → `['default', 'judge-net']`;
  `postgres`, `api`, `worker`, `beat`, `web`, `migrate` stay
  default-only — the judge cannot reach them even in principle;
- the judge queue endpoint is a code seam: `JUDGE_QUEUE_URL`
  (`apps/api/config/settings.py`) — the API/worker write judge jobs to the
  queue Redis, the session/broker Redis keeps `REDIS_URL`; the judge itself
  gets `REDIS_URL=redis://judge-queue:6379/0`;
- A-2 (judge half): the root MinIO password is gone from the judge env;
  a `minio-init` one-shot creates the `judge-ro` user with a read-only
  bucket policy and self-tests it (read OK, write FAILS the init);
  the judge depends on it via `service_completed_successfully`.

Guards: `tests/security/check_compose.py` and
`tools/check_security_boundary.py` parse the topology and fail on any
regression (judge net membership, internal flag, both-networks membership,
root password value in the judge env).

## 7c. Live deployment proof (2026-09-24 09:22 UTC)

The auto-deploy watcher shipped commit `9402e69` (which contains the whole
chain) and the result was measured on the live stack:

- `check_deploy.sh`: "Hamma konteyner joriy kodda" — all five deployed
  containers match HEAD (api/worker/beat content-diff, web/judge by
  `org.rankwant.git-sha`);
- judge container networks = `rankwant_judge-net` ONLY, log shows
  `tarmoq preflighti o'tdi` (network preflight passed — postgres/api
  unreachable) and `cgroup preflight o'tdi`, then `judge-go ishga tushdi`;
- `rankwant-judge-queue-1` healthy, `rankwant-minio-init-1` exited 0
  (judge-ro self-test: read OK, write denied);
- `https://rankwant.uz/api/v1/health/` → 200; from inside the api
  container both Redis instances answer PING (`judge-queue` via
  `JUDGE_QUEUE_URL`, session via `REDIS_URL`); the provider reads the
  queue length from judge-queue (0).

Two real gaps were found by the deploy itself and fixed the same hour:

1. The base compose never declared a MinIO healthcheck, so any stack
   started from the base chain (CI, Nightly, dev) died on
   `minio-init: dependency failed to start: container minio has no
   healthcheck configured` (#254); measured in an isolated compose
   project first, then merged.
2. `deploy.sh` runs `up -d --no-deps $BUILD_SERVICES` — the new infra
   services are never built and never in the build scope, so the first
   live deploy left the judge crash-looping on `lookup judge-queue`.
   Step 6a/8 (#255) now brings judge-queue up (bounded wait for healthy)
   and runs minio-init (bounded wait for exited:0) before the service
   recreate; an infra failure dies before anything is recreated, so the
   previous stack stays in place.

## 8. Reproducing this record

```bash
docker network inspect rankwant_default \
  --format '{{range .Containers}}{{.Name}}  {{.IPv4Address}}{{println}}{{end}}'
docker inspect rankwant-judge-1 \
  --format 'privileged={{.HostConfig.Privileged}} cgroupns={{.HostConfig.CgroupnsMode}} nets={{range $k,$v := .NetworkSettings.Networks}}{{$k}} {{end}}'
docker exec rankwant-judge-1 sh -c 'getent hosts postgres redis minio api web'
docker exec rankwant-judge-1 bash -c 'timeout 3 bash -c "</dev/tcp/postgres/5432" && echo OPEN'
docker compose -p rankwant -f docker-compose.yml -f docker-compose.public.yml config | grep -c 'internal:'
```
