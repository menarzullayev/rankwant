# `tests/security` — a suite that claimed to run on every PR and ran nowhere

**Status:** living record. `docs/research/` holds dated records, not policy.
**Owner:** Saidakbar Narzullayev
**Written:** 2026-09-21
**Divergence closed:** [`2026-09-21-security-boundary`](../2026-09-21-security-boundary/README.md) § 5,
last table row — `tests/security/run.sh` / "nowhere automatic"
**Suite:** [`tests/security/run.sh`](../../../tests/security/run.sh)
**Runs in:** [`.github/workflows/nightly.yml`](../../../.github/workflows/nightly.yml) → job `security`
**Related:** [threat model](../../10-operations/threat-model.md) · [test strategy](../../10-operations/test-strategy.md) ·
[ADR-0004 judge engine](../../07-adr/0004-judge-engine.md)

---

## 1. Why this record exists

The first line of `tests/security/run.sh` said the suite ran on every PR. It did
not, and had not for some time. The only caller was
`.github/workflows/security.yml` (lines 94–95), and that workflow is **disabled**:
`on:` is `workflow_dispatch` only and the `audit` job carries `if: false` (owner
decision 2026-09-21, guarded by a `check_decisions` rule and two negative tests).

A disabled caller is not a loud failure. The file kept its confident header, the
`PR template` kept asking contributors to update the suite, and the test-strategy
document kept listing it as a ✅ layer. Nothing in the repository disagreed,
because nothing ran it.

The gap was found while writing the boundary record, which listed it as a
divergence rather than fixing it. This record closes it.

## 2. What was measured

Not inferred — each row is a command whose output is in the session log.

| Question | Measurement | Answer |
|---|---|---|
| Who invokes the suite? | `grep -rn tests/security` across workflows, scripts, tools | exactly one caller: `.github/workflows/security.yml:94-95` |
| Is that caller alive? | read `security.yml` | no — `workflow_dispatch` only, job `if: false` |
| Does anything else run it? | same grep, all file types | no |
| Is the *dynamic* half covered elsewhere? | `ls services/bakeoff/cases/` → 25 files; `runner.py --cases` default `""` | yes — `--cases` unset loads **all** 25, the five isolation cases included |
| Does the static half need a stack? | read the suite | no — it reads repository files |
| What does the static half need? | `check_compose.py` imports `yaml` | PyYAML, which the runner does not ship |

So the marginal loss was **the static half only**: judge host isolation rules,
IDOR on `source_code`, PAT hashing, rate-limit configuration. The dynamic half was
already being exercised every night.

That distinction is the whole reason this change is shaped the way it is.

## 3. What the suite actually does

Three sections, two different natures.

| § | Nature | Checks |
|---|---|---|
| 1 | static, YAML-parsed | `judge` publishes no DB credentials, is `privileged`, does not depend on `postgres`; `judge-go`/`judge-py` reject `DATABASE_URL`; `judge-go` runs a `PreflightCgroup` |
| 2 | static, grep | `source_code` is filtered by ownership (`is_staff`); PATs are stored as `sha256`; `DEFAULT_THROTTLE_RATES` exists |
| 3 | **dynamic** | `services/bakeoff/harness/runner.py` under real nsjail — fork bomb, file write, network, `/proc`, symlink |

Sections 1–2 are greps and one YAML parse over committed files. Section 3 submits
real work to a real judge worker over Redis.

## 4. Why the dynamic half is not duplicated

`ISOLATION_CASES` in `runner.py` is `{09-fork-bomb, 10-file-write, 11-network,
12-proc-read, 13-symlink}`. The Nightly `e2e` job already runs
`--profile bakeoff run --rm bakeoff`, whose command is
`python /bakeoff/harness/runner.py --worker judge-go` — **no `--cases` filter**,
so all 25 cases load, isolation cases included.

Running section 3 again from this suite would therefore execute the same
harness, with the same cases, against the same worker. It would not add
assurance; it would add a full compose stack (the only reason section 3 needs
`REDIS_URL`) to a job that otherwise needs no stack at all.

One asymmetry is worth naming rather than hiding: the bake-off step uses the
harness default `--timeout 180`, while section 3 passes `--timeout 300`. The
bake-off bound is the **stricter** of the two, so nothing is loosened by leaving
section 3 to it.

So the suite gains an explicit mode instead:

```bash
SECURITY_STATIC_ONLY=1 tests/security/run.sh
```

The flag is not a shortcut around a broken check — it skips work that is already
done elsewhere, and says so in the log.

## 5. Where it runs now

A new `security` job in `nightly.yml`. Three design choices, each with a reason
that was measured rather than assumed:

- **Its own job, not a step in `e2e`.** The same reasoning the latency job
  records: a security failure inside the browser matrix would go red under the
  name "E2E — full browser matrix", and the failure would be attributed to the
  wrong thing.
- **PyYAML from `setup-python`, not the `api` image.** The suite reads
  repository files. Building an image (measured: 120–180 s warm) or installing
  the whole Django stack to parse one YAML file would cost more than the job
  does. `setup-python` + `pip install pyyaml` is seconds.
- **`timeout-minutes: 3`.** The repository rule is that no job may wait forever;
  jobs over three minutes must justify it. This one does not need the exception.

## 6. What guards it

`tools/check_decisions.py` → rule `xavfsizlik to'plami avtomatik yuriydi`. It
walks the chain and fails if any link is cut:

| Link | Why it can break quietly |
|---|---|
| `tests/security/run.sh` contains `SECURITY_STATIC_ONLY` | without it, Nightly would silently start running section 3 as well |
| the old header claim is gone | a restored "runs on every PR" line would be false again, and false confidence is the original bug |
| `nightly.yml` invokes `tests/security/run.sh` | deleting the step returns the suite to "nowhere automatic" with no other symptom |
| `nightly.yml` passes `SECURITY_STATIC_ONLY: '1'` | dropping it turns the job into a duplicate of the bake-off |
| `nightly.yml` installs `pyyaml` | without it the job fails at section 1 with `ModuleNotFoundError` |
| the `security` job declares a timeout | an unbounded job can hang the self-hosted runner |
| the record exists and is indexed | the *reason* for static-only mode is the part that gets lost first |
| the record names the isolation-case set | proves the coverage argument was checked, not asserted |

Negative tests cover each link, plus a positive control that the rule passes on
the pristine tree.

The rule is a **guard, not a measurement**. It cannot prove the suite's checks
are correct; only the Nightly job's own run does that.

## 7. What this record is not

- Not a re-enablement of `security.yml`. That decision stands, and its two
  negative tests still guard it.
- Not coverage for `gitleaks`, `pip-audit` or `npm audit`. Those live inside the
  same disabled workflow, so they too run nowhere automatically. **This change
  does not touch them.** They are a separate decision, and they are named here so
  that closing one gap is not mistaken for closing three.
- Not a claim that the static checks are strong. They are greps and one YAML
  parse; they catch regressions in rules already decided, not new weaknesses.
- Not a substitute for the external audit. ADR-0004 still makes that mandatory
  before public launch.

## 8. Open items

1. **`gitleaks` / `pip-audit` / `npm audit` run nowhere.** The disabled workflow
   is their only caller. Secret scanning in particular is the kind of check that
   is worthless when it is not running.
2. **The static half could also run per PR.** It needs no stack and takes under a
   second, so the cost is a `setup-python` step. The owner chose Nightly for this
   change; per-PR is a separate decision with a different failure mode — Nightly
   finds a regression up to 24 hours late.
3. **Section 3's `--timeout 300` is now dead code.** Nothing invokes it in
   automatic mode. Either the bake-off should pass 300 as well, or the suite's
   value should be dropped; leaving two numbers for one bound invites drift.
4. **`tests/security/README.md` is thin.** It now answers "where does this run",
   but a contributor updating a security rule still has no checklist for which
   section to extend.
