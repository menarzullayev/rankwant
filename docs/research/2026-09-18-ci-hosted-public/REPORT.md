# Public GitHub Actions is not unlimited max compute

**Date:** 2026-09-18 (Tashkent)
**Question:** If RankWant becomes a public repository, do GitHub-hosted runners become unlimited and maximum-power?
**Answer:** Standard runners become $0 per minute and are documented as “free and unlimited.” They are not maximum power. Larger runners stay paid, including on public repos.

## Facts (GitHub Docs, checked 2026-09-18)

| Kind | Public | Private Free |
|---|---|---|
| `ubuntu-latest` | 4 vCPU, 16 GB, $0 | 2 vCPU, 8 GB, 2000 min/month then $0.006/min |
| Larger 8–96 core | Always billed; Team/Enterprise | Always billed; Team/Enterprise |
| Self-hosted | $0 minutes; fork PRs are unsafe | $0 minutes (current RankWant path) |
| Concurrent hosted jobs | 20 on Free | 20 on Free |

Linux larger-runner list prices: 8-core $0.022, 16-core $0.042, 64-core $0.162 per minute. Included plan minutes do not apply.

Sources: [GitHub-hosted runners](https://docs.github.com/en/actions/reference/runners/github-hosted-runners), [Actions runner pricing](https://docs.github.com/en/billing/reference/actions-runner-pricing).

## What was slow here

Measured on 2026-09-18 for `#90`:

- Windows `.githooks/pre-push` (full copy of CI): **5.8 min**
- GitHub CI on two Docker runners on this PC: **4.0 min** (Web queued ~2 min behind `#89` Security)

Opening the repo does not remove the 5.8 min hook. That hook was the human wait.

## Locked choice

First HITL (same day): keep the repo private; slim pre-push to `ruff` / `format` / `check_i18n` / `check_hardcoded` plus `push_guard`. mypy, pytest, tsc, eslint, and the 153 negative tests stay on CI.

Second HITL (same day, after fold-jobs): three full API+Web PRs were still ~18 min of work on two laptop runners. No VPS, no second PC, no payment. Remaining free levers were PR-thin/main-fat, public `ubuntu-latest`, private hosted 2000 min, or a third runner on this PC. Owner locked **public + `ubuntu-latest`** for CI/Security/Nightly. Deploy and `runner-selftest` stay self-hosted. Flip visibility only after that workflow change is on `main`, so fork PRs never land on the laptop.
