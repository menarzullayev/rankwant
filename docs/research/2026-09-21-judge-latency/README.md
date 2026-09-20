# Judge latency — the launch gate that had a job but no record

**Status:** living record. `docs/research/` holds dated records, not policy.
**Owner:** Saidakbar Narzullayev
**Written:** 2026-09-21
**Gate:** [`docs/09-development-plan/README.md`](../../09-development-plan/README.md) § "Launch gate —
public chiqishdan oldin" → `- [ ] Judge latency o'lchangan: p50 < 5s, p95 < 15s`
**Metric definition:** [`docs/10-operations/README.md`](../../10-operations/README.md) § "SLO va metrikalar" —
`Attempt.created_at → judged_at`
**Harness:** [`tests/latency/check_judge_latency.py`](../../../tests/latency/check_judge_latency.py)
**Related:** [ADR-0004 judge engine](../../07-adr/0004-judge-engine.md) · [security boundary](../2026-09-21-security-boundary/README.md) · [threat model](../../10-operations/threat-model.md)

---

## 1. Why this record exists

The launch gate has six rows. Three are open:

| Row | Who can close it |
|---|---|
| `08 § Xavfsizlik checklist` fully applied | 🔒 `docs/08` is locked — a documentation change, needs an ADR |
| **External security audit** (ADR-0004) | the owner — a firm has to be engaged |
| **Judge latency measured** | **the agent** — this record |
| Legal: licence analysis signed off | the owner — a lawyer |

Judge latency is therefore the **only** open gate that agent work can close. It
matters beyond bookkeeping: the NFR budget is `p50 < 5 s, p95 < 15 s`, and if the
real figure breaches it the remedy is **architectural** (months of work). Finding
that out late is expensive, which is exactly why the gate is in the launch list.

### The state this record found

The gate looked handled. It was not:

1. **A dedicated job exists** — `.github/workflows/nightly.yml` job `latency`
   ("Latency — judge budget"), added by PR #204 (`a5f7878`).
2. **It had never executed.** #204 merged `2026-09-21T02:26+05`; the last
   Nightly before it was `2026-09-20T07:12+05` (run `35496258448`, head
   `3cb8003`). The cron is `0 2 * * *` (UTC), so the first execution is
   **2026-09-21T07:00+05**.
3. **The job wrote its number only into the CI log.** Nothing reached a
   document, an artefact, or the gate row — so the gate would have stayed open
   even on a green job. A measured number that nobody records is not a closed
   gate.

So the gap was not the measurement machinery. The gap was that **nothing
carried the number anywhere durable**.

## 2. What is measured

The wall-clock time from a solution being submitted to the final verdict
arriving — `submit → Redis queue → judge → nsjail → verdict`. That is the number
a user experiences.

**Not** measured: queueing behaviour under load. The harness submits **one at a
time** by default (`LATENCY_SAMPLES` submissions, sequentially), so the figure is
the **pure path time**. The gate asks for exactly that. Behaviour under heavy
load is a different question and would be a separate decision.

## 3. How it is measured

| Knob | Default | Meaning |
|---|---|---|
| `API` | `http://api:8000/api/v1` | which API is measured |
| `LATENCY_SAMPLES` | `20` | submissions measured |
| `LATENCY_WARMUP` | `2` | discarded warm-up submissions |
| `LATENCY_P50_MS` | `5000` | gate budget |
| `LATENCY_P95_MS` | `15000` | gate budget |
| `LATENCY_PROBLEM` | `a-plus-b` | seeded problem |
| `LATENCY_LANGUAGE` | `cpp23` | C++ — the most expensive compile path |
| `VERDICT_TIMEOUT` | `120` | per-verdict deadline, seconds |

`20` samples is deliberate: a nearest-rank p95 needs at least 20 points, and the
20th sample *is* the p95. Percentiles use **nearest-rank** (`ceil(p/100 * n)`),
no interpolation — simple and reproducible on a small sample.

The harness exits `1` on a budget breach, on any non-`AC` verdict (an unhealthy
environment), or if `/health/` is not `ok`.

## 4. Why the CI number is not the gate figure

The harness measures **whatever environment it is pointed at**. The Nightly job
points it at a GitHub runner — 4 vCPU, not the production machine. The job's own
comment says so, and the harness docstring repeats it:

> the number here is the regression baseline; point the same harness at
> production with `API=` for the launch-gate figure

The **launch-gate figure** therefore requires:

```bash
API=https://rankwant.uz/api/v1 LATENCY_SAMPLES=20 \
  python tests/latency/check_judge_latency.py
```

The budget is identical in both environments, so the two numbers are
comparable. The CI number is the **regression baseline** — it tells us when
something has got slower, not whether production meets the NFR.

⚠️ That production command is **not** free. The harness registers a fresh user
(`latency<timestamp>`) and submits 22 solutions (2 warm-up + 20 samples) to the
seeded `a-plus-b` problem. On production that is an irreversible data change —
a new account and 22 attempts landing in `a-plus-b` standings. The owner
deliberately chose the CI baseline first rather than pointing an **unproven**
harness at live data.

## 5. Measurements

### 5.1 The gate harness

| Date | Environment | p50 | p95 | Samples | Budget met |
|---|---|---|---|---|---|
| 2026-09-21T07:00+05 | GitHub runner (`ubuntu-latest`) | — | — | 20 | ⏳ first scheduled run |

The row is filled in from the run's `LATENCY_JSON:` line. Until it is, the gate
row in `docs/09` stays unchecked.

### 5.2 Prior data points — **not** the gate harness

| Date | Source | p50 | p95 | Sample size | Note |
|---|---|---|---|---|---|
| 2026-09-19 | Nightly run `35466663452`, E2E job, "Latency (funksional to'plam)" | 173 ms | 1683 ms | not recorded | a **different** selection (the E2E functional set), same budget. Context only — it is not the gate figure |

Included because it is the only judge-latency number this project has ever
produced, and it sits ~9× inside the budget. It is **not** a substitute for the
gate measurement: different harness, different sample, unknown size.

## 6. Why there is no passive alternative

Reading the metric off real traffic would need no synthetic load and no new
accounts. It was measured on 2026-09-21 and it is not available:

```
judging_attempt: 1 row total, 1 judged
```

The platform has essentially no real judging traffic yet, so a p50/p95 cannot be
computed from existing attempts. The figure has to be **generated**. This is
recorded because "just query production" is the obvious idea and it does not
work — better to know that than to rediscover it before launch.

## 7. The recording chain

The fix for the actual gap (§1.3). Three pieces:

1. **The harness emits a machine-readable line.** `check_judge_latency.py` now
   prints one line prefixed `LATENCY_JSON: ` alongside its human report. It is
   printed **on failure too** (`"ok": false`), so the number that breached the
   budget is recorded as well.
2. **`tools/latency_summary.py` reads that line and writes it to the run page**
   (`$GITHUB_STEP_SUMMARY`). The figure becomes visible on the run page instead
   of buried in a log. If the marker is missing it exits **2** — "could not be
   measured" is never treated as fine.
3. **The Nightly job pipes the harness through `tee`** (`set -o pipefail`, so a
   budget breach still turns the job red) and runs the summary step with
   `if: always()` — a red latency job is exactly when the number matters most.

## 8. What this record is not

- **Not the launch-gate figure.** That requires the production measurement
  (§4), which has not been made.
- **Not a load test.** Sequential submissions measure the pure path (§2).
- **Not a decision to change the budget.** `p50 < 5 s, p95 < 15 s` comes from
  [`docs/04-prd`](../../04-prd/README.md) and is not ours to move.
- **Not a reason to check the gate row.** The checkbox in `docs/09` means
  "measured against the budget". No production number exists, so it stays
  unchecked — and `docs/09` is locked anyway.

## 9. Open items

1. **Read the first CI baseline** from the 2026-09-21T07:00+05 run and fill in
   §5.1. If the job fails, diagnose before drawing any conclusion about the
   budget.
2. **Decide on the production measurement** — it is a separate decision because
   it writes to live data (§4). The most likely shape: a dedicated measurement
   account, or a window where 22 attempts on a seeded problem are acceptable.
3. **Tighten the guard once a number exists.** The `check_decisions` rule
   currently asserts the record exists, is indexed, and that the wiring
   (harness marker → summary step → Nightly) is intact. It deliberately does
   **not** require a numeric row yet, because no number has been produced. Once
   §5.1 has one, the rule should require it — otherwise the table can silently
   empty out.
