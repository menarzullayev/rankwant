# RankWant — threat model

**Status:** living document. `docs/10-operations/` is `draft` (2026-09-06), so this
file needs no ADR to edit.
**Owner:** Saidakbar Narzullayev
**Written:** 2026-09-21
**Companion:** [`docs/research/2026-09-21-security-boundary/`](../research/2026-09-21-security-boundary/README.md)
— the measured boundary this model reasons about.
**External audit:** pending. ADR-0004 makes it mandatory before public launch.

> This is written in English on purpose: its primary reader is the external
> auditor. The rest of `rankwant/docs/` is Uzbek; the migration is a separate,
> owner-approved change.

---

## 1. Why this document exists

An auditor needs a threat model, not a control list. What existed before this
file was five checklist lines (`docs/08 § Xavfsizlik checklist`) and a design
statement (`docs/06 § Xavfsizlik chegarasi`). Neither says who the adversaries
are, what they want, or which risks we have **decided to accept**.

Everything marked *measured* below was observed on 2026-09-21, not inferred.

## 2. Scope and method

**In scope:** the system as deployed today (one host behind a Cloudflare
Tunnel) and the target topology where it differs.

**Out of scope:** physical security of the development machine; the laptop's
dual-boot setup; GitHub's and Cloudflare's internal security; end-user device
compromise.

**Method:** STRIDE per trust boundary, plus an explicit register of accepted
risks. Accepted risks are the part an auditor cannot reconstruct from code, so
they are stated with the date and the owner's decision.

## 3. Environment, as measured

| Fact | Value |
|---|---|
| Published ports | **2**, both `127.0.0.1` — `api:8301`, `web:8300` |
| Ingress | Cloudflare Tunnel only; `rankwant.uz` → `/api/*` to `:8301`, everything else to `:8300` |
| Not in the tunnel | `/admin`, MinIO, Adminer, Redis, Postgres |
| Accounts | 974,498 rows — of which **2** registered in the last 7 days and **1** has ever logged in. The rest is a load-test seed |
| Privileged accounts | 1 superuser, 1 staff |
| Repository visibility | **public** — every line of code is public; only `.env.public` is secret |
| Judge capacity | 1 worker 2.4 submit/s (p95 857 ms) · 4 workers 5.4/s · 8 workers 8.0/s (p95 1 360 ms) |

The account numbers matter for prioritisation: today's realistic adversary is an
automated crawler, not an organised attacker. **Public launch changes that**, and
most of this document is about what happens then.

## 4. Assets

| Asset | Why it is wanted | Where it lives |
|---|---|---|
| Hidden problem tests and reference solutions | solve problems without solving them; sell answers | S3/MinIO |
| Submission source code | users' private code; also who solved what | Postgres |
| Sessions and personal access tokens | account takeover | Redis (session) / Postgres (hash only) |
| Qvant ledger | economy integrity — minting currency, duplicate rewards | Postgres |
| Email addresses | spam, phishing, credential stuffing lists | Postgres |
| Compute | crypto-mining, DDoS reflection | judge |
| Admin access | everything above | Django admin (loopback), `admin` account |
| Availability and reputation | exam-day outage, defacement | whole stack, edge quota |

## 5. Adversaries

| Adversary | Capability | Motivation | Realistic today |
|---|---|---|---|
| Anonymous scanner | port scans, known-CVE probes, credential stuffing | opportunism | **yes** — constant background noise |
| AI/SEO crawler | unbounded request volume over generated URL space | training data, indexing | **yes** — measured at 82% of zone traffic on 2026-09-15 |
| Registered contestant | **submits arbitrary code** — the highest-capability input the platform accepts | curiosity, competitive edge | yes, once users exist |
| Cheating contestant | read hidden tests, read other users' solutions, submit on another's behalf | contest placement | yes, during contests |
| Scraper / competitor | copy the problem bank and user list | product cloning | yes |
| Credential-stuffing attacker | re-use leaked passwords from other sites | account takeover | yes |
| Compromised staff/insider | legitimate access to the admin panel and the DB | various | low, single-operator today |
| Supply chain | a malicious dependency or base image | backdoor at build time | yes, unmonitored |

## 6. Trust boundaries

```
Internet
  │
  ▼  ① edge — Cloudflare CDN, Tunnel, WAF rule, maintenance Worker
Cloudflare Tunnel  ──►  127.0.0.1 only
  │
  ├─► ② web   (Next.js 16, SSR, i18n)
  └─► ③ api   (Django 5.2 / DRF)  ──► ④ Redis (sessions, Celery, judge queue)
                                  ──► ⑤ Postgres (metadata, ledger, submissions)
                                  ──► ⑥ S3/MinIO (statements, tests, avatars)
                                            ▲
                                            │ pull
                                   ⑦ judge (Go + nsjail, privileged, no ports)
  │
  ▼  ⑧ host & deploy (watcher, deploy lock, CI)
```

Boundaries ⑦ and ⑧ are where the residual risk concentrates; boundaries ①–⑥ are
in reasonable shape and are described here mainly so the auditor can check the
reasoning rather than rediscover it.

## 7. STRIDE per boundary

### ① Edge — Cloudflare

| | Threat | Control | Residual |
|---|---|---|---|
| S | Spoofing the origin | Origin publishes no port; Tunnel is outbound-only from the host. `TRUSTED_CLIENT_IP_HEADER=HTTP_CF_CONNECTING_IP` is safe **because** the port is loopback-only — the tunnel cannot be bypassed | none known |
| T | Header injection to fake client IP | same as above | none known |
| R | — | Cloudflare access logs | no retention review |
| I | Data exposed at the edge | Cache rules keep authenticated responses `private, no-store`; `Vary: Accept-Language` at the edge | none known |
| D | **Quota exhaustion** | Free plan: **100 000 requests/day** for the maintenance Worker, which runs on *every* request. Measured 2026-09-15: 245 966 requests in 14 h, 82% from GPTBot | **open** — see A-4 |
| E | — | — | — |

**A note the auditor should have:** the AI-crawler WAF rule (ADR-0023) lives in
the Cloudflare zone, **not in this repository**. Rebuilding the zone loses it
silently. There is no check that it exists.

### ② Web — Next.js

| | Threat | Control | Residual |
|---|---|---|---|
| S | Session cookie theft | `httpOnly`, `SameSite=Lax`, `Secure` when not DEBUG, 30-day age | 30 days is long; no rotation on privilege change |
| T | XSS in SSR output | React escaping; no `dangerouslySetInnerHTML` on user input | not systematically audited |
| I | Dictionary or private page leaking via CDN | guest-only caching keyed on path + language; authenticated responses `private, no-store` | none known |
| D | Render cost per request | homepage render measured 12–17 ms CPU | fine at current scale |
| E | — | Web holds no credentials and no PAT (ADR-0008); it proxies cookies | none known |

### ③ API — Django / DRF

| | Threat | Control | Residual |
|---|---|---|---|
| S | Credential stuffing, weak passwords | per-scope throttles (anon 1 500/h, user 300/min, register 40/h, password reset 20/h); Turnstile before the register throttle | **no lockout, no MFA, no breach-list check** |
| T | CSRF | `SameSite=Lax` + Django CSRF; same-origin deployment means no cross-origin path exists | none known |
| R | Denial of authorship | `Attempt.user` recorded; contest submissions bound to the session | no device fingerprinting |
| I | **IDOR on submissions** | `source_code` and `compile_output` are stripped unless the requester owns the attempt, is staff, or the ADR-0020/0021 hack exception applies (`hacks/services.py: can_view_source`) | this is the highest-value object in the API; the rule is centralised but untested by a dedicated negative test |
| I | User enumeration | `/users/` was closed; the register endpoint's responses are uniform | not re-measured |
| D | Expensive endpoints | `submit` 6/min, `hack` 10/min, `export` 3/h; `ResilientScopedRateThrottle` keeps the counter available if Redis blips | none known |
| E | Privilege escalation via admin | Django admin is **not** in the tunnel; reachable only at `127.0.0.1:8301/admin/` | a local process can reach it |

### ④ Redis

| | Threat | Control | Residual |
|---|---|---|---|
| I | Session and queue data readable | No published port; internal compose network only | any container on that network can read it |
| D | Session loss | Redis is a single instance serving sessions, the Celery broker and the judge queue (`docs/08 § Assumptions`) | **no persistence review**; one instance for three duties is a single point of failure |

### ⑤ Postgres

| | Threat | Control | Residual |
|---|---|---|---|
| I | Bulk data exfiltration | No published port | the judge shares the compose network — see ⑦ and § 9 |
| T | Direct writes bypassing the ledger | all writes go through the service layer; ADR-0002 asserts cache + transaction sums always agree | audit exists but is not scheduled |
| D | Availability | no replica in the preview topology | accepted for preview |

### ⑥ S3 / MinIO

| | Threat | Control | Residual |
|---|---|---|---|
| S | **Shared static credentials** | `S3_KEY=rankwant` / `S3_SECRET=devdevdev`, the same value in `docker-compose.yml` and in the judge's environment — in a **public** repository | **open** — A-2. Not reachable from the internet, so this is defence-in-depth, not an open door |
| I | Hidden tests readable | bucket is not published (`curl 127.0.0.1:9000` → `HTTP 000`); only api/worker/judge hold credentials | any of those three can read every test |

### ⑦ Judge — the critical boundary

User code runs here and nowhere else. This is the only boundary where a
successful attack means **arbitrary code execution inside our infrastructure**.

| | Threat | Control | Residual |
|---|---|---|---|
| S | — | judge accepts no connections; it pulls work from Redis (ADR-0004) | none known |
| T | Job forgery on the queue | Redis is internal-only; a forged job still lands in the sandbox | a network neighbour could inject jobs |
| R | — | verdicts carry the judge's own timestamps | none known |
| I | Reading hidden tests or other submissions from inside the sandbox | nsjail: namespaces + cgroup limits; five isolation cases (`09-fork-bomb`, `10-file-write`, `11-network`, `12-proc-read`, `13-symlink`) run in Nightly against real nsjail | **the sandbox is verified, the container is not** — see E below |
| D | Fork bomb, memory exhaustion, TLE loops | cgroup limits, process limits, `PreflightCgroup` fails closed at startup | a flood of submissions is bounded by `submit 6/min` per user, not globally |
| E | **Container escape** | **`privileged: true` + `cgroup: host`** — required by nsjail. No inbound port. No DB credential (`DATABASE_URL` absent; the worker exits 1 if it is set). Only documented mitigation: `docker compose … stop judge` | **open, and the largest single risk in this document** — A-1 |

**The judge is the reason the boundary is a container boundary, not a host
boundary.** See § 9.

### ⑧ Host and deploy

| | Threat | Control | Residual |
|---|---|---|---|
| S | Unauthorised deploy | host watcher + `check_deploy_gate.py` require a green `main`; `deploy.lock`; `.env.public` is gitignored | the host is a single operator workstation |
| T | Malicious commit reaching production | every change goes through a PR; ruleset `23667814` blocks force-push and deletion on `main`; `push_guard` hook blocks direct pushes | `required_approving_review_count: 0` — a PR is required but **no second reviewer** |
| I | Secret leakage into git | `.env.public` gitignored; `gitleaks` exists in `security.yml` — which is **disabled** | **open** — A-3: secret scanning runs nowhere |
| D | Disk exhaustion | image pruning, log rotation, builder GC 5 GB (`docker_disk_stays_bounded`) | the deploy log itself is not rotated |
| E | Container escape reaching the DB host | see ⑦ | **open** |

## 8. Accepted risks

Every row is a decision, not an oversight. An auditor should treat these as
inputs, not as findings.

| # | Risk | Why accepted | Decided | Revisit when |
|---|---|---|---|---|
| **A-1** | Judge runs `privileged: true` with `cgroup: host`, on the same machine as Postgres and Redis | Narrowing capabilities is not possible while nsjail needs namespaces; the owner chose to keep the model and let the external audit verify it | 2026-09-21 | the audit reports; or the target four-host topology lands |
| **A-2** | MinIO root credentials are the literal `devdevdev`, in a public repo | Not internet-reachable; judged defence-in-depth rather than exposure | 2026-09-21 (recorded) | before public launch — this is cheap to fix and should be |
| **A-3** | Secret scanning, dependency audit and the static security checks run nowhere (`security.yml` disabled) | The owner turned the run off; the deploy gate is `CI` only | 2026-09-21 | if the escape suite or scanning is wanted back, it belongs in Nightly, not PR CI |
| **A-4** | The Cloudflare Free Worker quota (100 k/day) can be spent by crawlers before noon | Mitigated by the zone-side WAF rule; upgrading is a cost decision | 2026-09-18 (ADR-0023) | a second quota exhaustion, or launch traffic |
| **A-5** | Backups are local-only; `RANKWANT_BACKUP_OFFSITE=off`; one NVMe hosts both `C:` and `D:` | The owner deferred it until after launch | 2026-09-21 | after launch, or after the first real user data |
| **A-6** | Alerting is local-only: `tools/monitor.ps1` writes a file that no code reads; there is no Sentry | The owner chose to keep alerting local for now | 2026-09-21 | the first incident nobody noticed |
| **A-7** | Registration is open with no abuse layer; demo accounts with weak passwords were documented | Weak-password accounts no longer exist (see § 10); the abuse layer is still unbuilt | 2026-09-10 | before public announcement |
| **A-8** | Ten languages' translations are unreviewed by native speakers | Keys are complete and checked; text quality is not | 2026-09-10 | on complaint |

## 9. Deviations from the locked design

These are not new findings — they are the gap between what `docs/06` and
ADR-0004 describe and what runs today. They matter because the *security
argument* in ADR-0004 depends on them.

| Locked statement | Today | Consequence |
|---|---|---|
| ADR-0004: "Judge host **never** on the same server as API/DB" | one host; everything in one compose project | the judge↔data isolation is a **container** boundary, not a host boundary. A container escape lands on the machine holding Postgres and Redis |
| ADR-0004: "outbound network from the judge host closed" | no `network_mode` restriction; the judge can reach the compose network and the internet | a submission cannot exfiltrate through nsjail, but an **escape** could |
| `docs/06`: target topology is four hosts | one host | all of the above |
| `docs/06`: "no inbound port on the judge host" | satisfied at the container level (verified) | none — this one holds |

`docs/06` marks the current state as "preview, not production" and the owner
knows it. The point of this table is that **A-1's severity is a direct
consequence of the single-host preview**, and the audit should be scoped with
that in mind.

## 10. Stale documentation found while writing this

| Claim | Reality (measured 2026-09-21) |
|---|---|
| `10-operations § Ochiq risklar`: demo accounts (`ustoz`, `oquvchi1..3`) have weak passwords | Those accounts do not exist. `demo` exists but its password field is empty, so it cannot log in. The row is stale |
| `08 § Xavfsizlik checklist`: judge isolation, PAT hashing, rate limits all unchecked | All three are implemented in code; the checklist is behind the code, not the code behind the checklist |

## 11. Open items, mapped to launch gates

| Item | Gate | Owner |
|---|---|---|
| External security audit | ADR-0004 — **on the critical path** | owner |
| Judge latency p50 < 5 s / p95 < 15 s measured | `docs/09` launch gate — the Nightly gate exists, no number yet | agent |
| Dependency licence inventory → lawyer | `docs/09` launch gate | owner + lawyer |
| A-2 MinIO credentials | cheap, do before launch | agent |
| A-3 escape suite / scanning back into automation | owner decision | owner |

## 12. Review triggers

Re-open this document when any of these happens:

- the four-host topology is deployed (removes A-1's precondition);
- a new trust boundary appears (a payment provider, an external judge, a public API);
- a real user base arrives (invalidates the "no real users" assumption in § 3);
- the external audit reports;
- any accepted risk in § 8 is revisited.
