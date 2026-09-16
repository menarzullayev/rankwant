# RankWant

A **competitive programming + contest (CP/OJ)** platform for Uzbekistan and
the global market.

- **Platform brand:** RankWant — _"Rank Want"_ = I want a rating
- **Internal currency:** **Qvant** (its own name; not `rankwantcoin`)
- **Docs:** [docs/README.md](docs/README.md) — a 10-stage pipeline in the
  `project-alpha` style

## Current status

Source of truth: the `**STATUS:**` line in each `docs/NN-*/README.md`.

| Stage                | Status                                   |
| -------------------- | ---------------------------------------- |
| Vision + brand       | 🔒 locked (2026-09-06)                   |
| Problem discovery    | 🔒 locked (2026-09-06)                   |
| Market + competitors | 🔒 locked (2026-09-06)                   |
| PRD (MVP scope)      | 🔒 locked (2026-09-06)                   |
| Domain model         | 🔒 locked (2026-09-06)                   |
| Architecture         | 🔒 locked (2026-09-06)                   |
| ADR                  | 🌱 living — decisions keep accumulating  |
| Technical spec       | 🔒 locked (2026-09-06)                   |
| Development plan     | 🔒 locked (2026-09-06)                   |
| Operations           | 📝 draft — policies and runbooks written |
| Phase 0 + Phase 1    | ✅ API + web + judge + Qvant             |

## Quick links

| Question                 | File                                                                                     |
| ------------------------ | ---------------------------------------------------------------------------------------- |
| What and why?            | [docs/01-vision/README.md](docs/01-vision/README.md)                                     |
| Problem and user         | [docs/02-problem-discovery/README.md](docs/02-problem-discovery/README.md)               |
| Market / competitors     | [docs/03-market-research/README.md](docs/03-market-research/README.md)                   |
| Brand + Qvant            | [docs/03-market-research/brand-discovery.md](docs/03-market-research/brand-discovery.md) |
| MVP requirements         | [docs/04-prd/README.md](docs/04-prd/README.md)                                           |
| Domain model             | [docs/05-domain-model/README.md](docs/05-domain-model/README.md)                         |
| ADR                      | [docs/07-adr/README.md](docs/07-adr/README.md)                                           |

## External analyses (full version)

> These files are **not part of this repo** and exist only on the Linux install
> of the dev machine; the Windows copy does not have them (searched 2026-09-13,
> see [docs/03-market-research/README.md](docs/03-market-research/README.md)).
> What was carried over lives in `docs/03-market-research/audit/` and
> [docs/research/](docs/research/README.md).

- `kep-uz-platform-analysis.md`
- `robocontest-uz-platform-analysis.md`
- cp.uz repo: `cp-uz/`

## Monorepo layout

[ADR-0009](docs/07-adr/0009-monorepo.md)

```
rankwant/
├── apps/api/            Django 5.2 LTS + DRF  (Sprint 1)
├── apps/web/            Next.js + React 19    (Sprint 1)
├── services/judge-go/   bake-off A — Go + nsjail
├── services/judge-py/   bake-off B — Python + isolate
├── docs/                docs pipeline 01–10
├── tests/               e2e · load · security · chaos
├── tools/               check_docs.py
└── .github/workflows/   CI · Security · Nightly
```

**The deploy layout is not the repo layout** — the judge runs on a separate
host with no inbound ports
([06-architecture § Security boundary](docs/06-architecture/README.md)).

## Getting started

```bash
docker compose up -d          # postgres + redis + minio
python3 tools/check_docs.py   # docs integrity check
```

Contribution rules: [CONTRIBUTING.md](CONTRIBUTING.md)

## Documentation principle

[menarzullayev/project-alpha](https://github.com/menarzullayev/project-alpha) —
**10 sequential stages** from zero to production. This project follows the same
principle. Rationale:
[docs/README.md#project-alpha-bilan-moslik](docs/README.md#project-alpha-bilan-moslik).
