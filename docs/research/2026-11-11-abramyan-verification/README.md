# Abramyan import: production run and verification (2026-11-11)

This is stage 6 of [ADR-0060](../../07-adr/0060-abramyan-import.md) § 2.6.
It covers the owner's round-4 decision to verify now, on the production
judge, and the round-5 decision to publish only after every problem is
green. Production was at commit `66e45f6` (#538).

## Import

```bash
docker cp …/abramyan-export/package rankwant-api-1:/tmp/abramyan-package
docker exec rankwant-api-1 python manage.py import_abramyan --package /tmp/abramyan-package --author admin
```

The full run took 292 s. All counts below were measured in the production
database:

| What | Count |
|---|---:|
| Problems (drafts, unofficial, no number) | 1 100 |
| Tests (in S3) | 21 836, of them 2 200 samples |
| Translations (`ru`, `en`, `kaa`) | 3 300 |
| Study plan `abramyan-masalalar` | 19 sections, 1 100 steps |
| Mirrored images (Integer29) | 1 |

A four-problem trial ran first: Begin1, Integer29, File1 and Text2. It
covered a real answer, an image, file I/O, and a problem whose statement
gained a note. All four references were AC and all four empty programs got
WA.

## Verification

```bash
docker exec rankwant-api-1 python manage.py verify_abramyan --wait 7200 --report /tmp/verify-all.json
```

| What | Result |
|---|---|
| Submissions | 2 200: a reference solution and an empty program per problem |
| Reference solutions | **1 100 / 1 100 AC** |
| Empty programs | **1 100 / 1 100 WA**, all on test 1 |
| Wall time | 475 s |
| Reference CPU time | p50 13 ms, p99 52 ms, max 171 ms (`while14`) — the limit is 1 000 ms |
| Reference memory | p50 5 060 kB, max 23 460 kB (`begin1`) — the limit is 64 MB plus Python's 5 MB |

No problem failed, so there was nothing to fix before publishing. The
difference between the package's own check (`1e-5`) and the shipped checker
(`1e-6`) caused no failure.

## Publication

`publish_abramyan` ran with `--dry-run` first (1 100 ready), then for real.
It published all 1 100 problems at once, set their readiness to
`validated`, and published the plan. There was no announcement (owner
decision).

| Check, measured after publishing | Value |
|---|---|
| Abramyan problems public / numbered / official | 1 100 / 0 / 0 |
| `GET /problems/?tier=unofficial` count | 1 100 |
| Official archive count, `/stats/` problems | 1 236, unchanged |
| `/roadmaps/abramyan-masalalar`, `/roadmaps/abramyan-masalalar/1`, `/problems/begin1`, `/problems/file1`, `/problems/integer29` | 200 |
| `begin1` in a browser (`en`) | translated title, 7 KaTeX formulas, no raw `$`, "Unofficial" and "Precision 10⁻⁶" chips, 1000 ms · 64 MB |

## The verification trace (the owner decides later whether to delete it)

The owner decided to keep the trace for now. It is left by the system
account `abramyan-verify`, which is inactive:

| Rows | Count |
|---|---:|
| Attempts | 2 208 (8 trial + 2 200), about 947 kB of row data |
| Per-test results | 23 020 |
| `UserSolvedProblem` | 1 100 |
| Activity events | 1 100 |

Because of these rows, every Abramyan problem shows "1 solved · 2 attempts".
The four trial problems show 4 attempts. To remove the trace, delete this
account's attempts, solve rows and events, then recount the problems'
counters with `recount_problems`.
