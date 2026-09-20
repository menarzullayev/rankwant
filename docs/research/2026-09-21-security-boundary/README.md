# RankWant — deployed security boundary (as built)

**Date:** 2026-09-21
**Status:** research record — a snapshot of one day, not living policy
**Sources:** `docker-compose.yml`, `docker-compose.public.yml`, `tools/deploy.sh`,
live host measurements (`docker ps`, `docker inspect`, `curl`), `docs/06-architecture`
(locked 2026-09-06), `docs/08-technical-spec` (locked 2026-09-06), ADR-0004

> Binding rules live in `docs/06` / `docs/08` and the ADRs. Where this record and
> those disagree, they win. This record exists because the locked documents state
> the *target* boundary ("four hosts"); nothing stated the boundary **as it runs
> today**, and nothing checked it. An external audit needs the second one.

---

## 1. In one sentence

The only way in is the Cloudflare Tunnel. Every published port on the host is
bound to `127.0.0.1`, the judge container publishes nothing and holds no database
credential, and user code runs only inside that judge container.

## 2. The chain, and why reading one file lies

`tools/deploy.sh` merges two files, in this order:

```
docker compose -p rankwant --env-file .env.public \
  -f docker-compose.yml -f docker-compose.public.yml up -d --build --wait
```

The overlay uses two Compose extensions that **change what the base file means**:

| Directive | Effect | Example |
|---|---|---|
| `ports: !reset []` | deletes the base file's published port | `postgres`, `redis`, `minio` |
| `ports: !override [...]` | replaces it wholesale | `api`, `web` |

`docker-compose.yml` alone declares `postgres: 5432:5432`, `redis: 6379:6379`,
`minio: 9000:9000, 9001:9001`, `api: 8000:8000`, `web: 3000:3000` — all host-wide.
After the overlay, none of that is true. On 2026-09-21 a conclusion drawn from the
base file alone ("MinIO is exposed") was wrong for exactly this reason. It was
caught by measuring the live host, not by re-reading the file.

## 3. The boundary, measured

Authoritative cross-check — the engine's own view of the merged chain, run on
2026-09-21 (`docker compose -p rankwant -f docker-compose.yml -f
docker-compose.public.yml config`; it resolves without `.env.public`):

| Service | Published | Host IP | Target |
|---|---|---|---|
| `api` | 8301 | `127.0.0.1` | 8000 |
| `web` | 8300 | `127.0.0.1` | 3000 |

**Two published ports. Both loopback. Nothing else.**

Live host (`docker ps`, same day) — the port column of the running stack:

| Container | Ports as reported | Reading |
|---|---|---|
| `rankwant-web-1` | `127.0.0.1:8300->3000/tcp` | loopback |
| `rankwant-api-1` | `127.0.0.1:8301->8000/tcp` | loopback |
| `rankwant-adminer` | `127.0.0.1:8081->8080/tcp` | loopback — **not in the compose chain**, see § 6 |
| `rankwant-judge-1` | *(none)* | no inbound port at all |
| `rankwant-minio-1` | `9000/tcp` | container port only, not published |
| `rankwant-redis-1` | `6379/tcp` | container port only |
| `rankwant-postgres-1` | `5432/tcp` | container port only |
| `rankwant-worker-1`, `rankwant-beat-1` | `8000/tcp` | container port only |

MinIO re-probed the same day: `curl 127.0.0.1:9000/minio/health/live` → `HTTP 000`
(no listener). Cloudflare Tunnel ingress carries only `rankwant.uz` / `api` /
`www` plus the bugvector subdomains; MinIO is not among them.

## 4. The judge

The judge is the only place user code runs. Its properties, from
`docker-compose.yml`:

- **no `ports:` key** — nothing is published, and the worker pulls jobs from
  Redis rather than accepting connections (ADR-0004).
- **no database credential** — environment keys are `REDIS_URL`, `S3_ENDPOINT`,
  `S3_BUCKET`, `S3_KEY`, `S3_SECRET`. `DATABASE_URL`, `DJANGO_SECRET_KEY` and
  `POSTGRES_PASSWORD` are absent, and the worker exits 1 if `DATABASE_URL` is
  ever set.
- **`privileged: true`** with **`cgroup: host`**, because nsjail needs
  namespaces and cgroup access.

That last point is the open tension, stated plainly for the auditor: **ADR-0004
chose nsjail over Judge0 partly because "Judge0's `--privileged` requirement
disappears" — and the deployed service is nevertheless privileged.** The only
documented mitigation today is a manual `docker compose … stop judge`. On
2026-09-21 the owner reviewed this and chose to keep the privilege model and
**rely on the external audit** for verification, rather than narrow capabilities
now. That choice is recorded; it is not an oversight.

## 5. Where the boundary is verified, and where it is not

| Check | Runs where | What it proves |
|---|---|---|
| `tools/check_security_boundary.py` | CI, `Docs and contract integrity` | merges the chain, asserts every published port is loopback and that `judge`/`postgres`/`redis`/`minio` publish nothing |
| `check_decisions.py` rule `chegara faqat loopback` | CI, same job | the check is still wired, the overlay still resets, `judge` still declares no port |
| bake-off isolation cases `09-fork-bomb`, `10-file-write`, `11-network`, `12-proc-read`, `13-symlink` | Nightly, `e2e` job (`--profile bakeoff run --rm bakeoff`) | real nsjail blocks the escapes |
| `tests/security/run.sh` — **static half** | **nowhere automatic** | judge host rules, IDOR, PAT hashing, rate limits |

The last row is a real gap, not a subtlety. `tests/security/run.sh` is invoked only
from `.github/workflows/security.yml` (lines 94–95), and that workflow is disabled:
`on:` is `workflow_dispatch` only and the `audit` job carries `if: false`
(owner decision 2026-09-21, guarded by the `Security run o'chiq` rule and two
negative tests). The suite's *dynamic* half is duplicated by the Nightly bake-off
step, so the marginal loss is the static checks.

> **Update, later on 2026-09-21 — the last row above was closed.** The static half
> now runs in Nightly, job `security`, invoked with `SECURITY_STATIC_ONLY=1`
> precisely *because* the dynamic half is already covered by the bake-off step.
> See [`2026-09-21-security-suite`](../2026-09-21-security-suite/README.md). The
> table above is left as written: it records what was true when this document was
> produced, and an auditor should be able to see both the gap and its closure.
> Note that `gitleaks`, `pip-audit` and `npm audit` live in the same disabled
> workflow and are **still** not covered — that remains open.

The five `ISOLATION_CASES` are wired by construction: the `bakeoff` service in
`docker-compose.ci.yml` runs `runner.py --worker judge-go` with **no `--cases`
filter**, so `runner.py` loads every case in `services/bakeoff/cases/`. No
repository variables are set, so the step's `if: ${{ vars.STAGING_URL == '' }}`
guard holds and the step is not skipped.

## 6. Divergences the auditor should see

1. **`rankwant-adminer` is not managed by anything in the repository.**
   `docker inspect` shows no compose labels at all and image `adminer:4`
   (a floating major tag, not a digest), `restart: unless-stopped`, created
   2026-09-20T17:07:43Z, reachable only on `127.0.0.1:8081`. It is a full
   PostgreSQL client UI holding database credentials, outside the declared
   stack, invisible to every compose file and every check in this repository.
   It is not reachable from the internet. It is also not reviewed, not pinned,
   and not recreated by any deployment.
2. **MinIO root credentials are the literal `devdevdev`**, and the repository is
   public (`gh repo view --json visibility` → `PUBLIC`). Not externally
   reachable (§ 3), so this is a defence-in-depth weakness rather than an open
   door: any container on the compose network — including an escaped judge —
   could read or rewrite problem test data with a publicly known password.
3. **No threat model document existed when this record was written.** `docs/08 §
   Xavfsizlik checklist` is five lines; `docs/06 § Xavfsizlik chegarasi` is a
   design statement. This record is a boundary measurement, not a threat model.
   *Later the same day the owner chose to write one:*
   [`docs/10-operations/threat-model.md`](../../10-operations/threat-model.md) —
   assets, adversaries, STRIDE per trust boundary, and the accepted-risk
   register (A-1…A-8) that this record could only point at.
4. **Alerting is local-only.** `tools/monitor.ps1` detects seven failure classes
   and writes `.handoff/monitor-alert.txt`; no code reads that file. There is no
   Sentry. The owner reviewed this on 2026-09-21 and chose to keep alerting
   local for now — do not "fix" the missing delivery as an obvious bug.
5. **Backups are local-only and there is no offsite copy.** `RANKWANT_BACKUP_OFFSITE`
   defaults to `off`; one NVMe hosts both `C:` and `D:`. Deferred by the owner on
   2026-09-21. Same instruction: do not flip it helpfully.

## 7. What is still missing before an audit can start

- ~~The threat model (§ 6.3)~~ — written later on 2026-09-21:
  [`docs/10-operations/threat-model.md`](../../10-operations/threat-model.md).
- A dependency licence inventory for a lawyer's sign-off — the second long-lead
  launch-gate item, and coupled to ADR-0004's nsjail choice.
- The judge latency gate exists in Nightly but has not yet produced a number, so
  `docs/09`'s "p50 < 5 s, p95 < 15 s" checkbox stays open.

## 8. Reproducing this record

```bash
docker compose -p rankwant -f docker-compose.yml -f docker-compose.public.yml config \
  | grep -A2 'published'
docker ps --filter name=rankwant --format '{{.Names}}\t{{.Ports}}'
python3 tools/check_security_boundary.py
```
