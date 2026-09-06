# RankWant

O'zbekiston va global bozor uchun **sport dasturlash + musobaqa (CP/OJ)** platformasi.

- **Platforma brendi:** RankWant — _«Rank Want»_ = reyting xohlayman
- **Ichki valyuta:** **Qvant** (alohida nom; `rankwantcoin` emas)
- **Hujjatlar:** [docs/README.md](docs/README.md) — `project-alpha` uslubidagi 10 bosqichli pipeline

## Hozirgi holat

| Bosqich           | Holat                            |
| ----------------- | -------------------------------- |
| Vision + brend    | 🔒 locked (2026-09-06)           |
| Problem discovery | 🔒 locked (2026-09-06)           |
| Market + raqobatchi | 🔒 locked (2026-09-06)         |
| PRD (MVP scope)   | 🔒 locked (2026-09-06)           |
| Domain / arxitektura | 📝 draft                      |
| Kod               | ❌ hali yo'q                     |

## Tez havolalar

| Savol                   | Fayl                                                                                     |
| ----------------------- | ---------------------------------------------------------------------------------------- |
| Nima va nima uchun?     | [docs/01-vision/README.md](docs/01-vision/README.md)                                     |
| Muammo va foydalanuvchi | [docs/02-problem-discovery/README.md](docs/02-problem-discovery/README.md)               |
| Bozor / raqobatchilar   | [docs/03-market-research/README.md](docs/03-market-research/README.md)                   |
| Brend + Qvant           | [docs/03-market-research/brand-discovery.md](docs/03-market-research/brand-discovery.md) |
| MVP talablar            | [docs/04-prd/README.md](docs/04-prd/README.md)                                           |
| Domen modeli            | [docs/05-domain-model/README.md](docs/05-domain-model/README.md)                         |
| ADR                     | [docs/07-adr/README.md](docs/07-adr/README.md)                                           |

## Tashqi tahlillar (to'liq versiya)

- [../kep-uz-platform-analysis.md](../kep-uz-platform-analysis.md)
- [../robocontest-uz-platform-analysis.md](../robocontest-uz-platform-analysis.md)
- cp.uz repo: [../cp-uz/](../cp-uz/)

## Monorepo tuzilishi

[ADR-0009](docs/07-adr/0009-monorepo.md)

```
rankwant/
├── apps/api/            Django 5.2 LTS + DRF  (Sprint 1)
├── apps/web/            Next.js + React 19    (Sprint 1)
├── services/judge-go/   bake-off A — Go + nsjail
├── services/judge-py/   bake-off B — Python + isolate
├── docs/                hujjat pipeline 01–10
├── tests/               e2e · load · security · chaos
├── tools/               check_docs.py
└── .github/workflows/   CI · Security · Nightly
```

**Deploy tuzilishi repo tuzilishi emas** — judge alohida hostga, kiruvchi portsiz chiqadi
([06-architecture § Xavfsizlik chegarasi](docs/06-architecture/README.md)).

## Boshlash

```bash
docker compose up -d          # postgres + redis + minio
python3 tools/check_docs.py   # hujjat yaxlitligi tekshiruvi
```

Hissa qo'shish qoidalari: [CONTRIBUTING.md](CONTRIBUTING.md)

## Hujjatlashtirish prinsipi

[menarzullayev/project-alpha](https://github.com/menarzullayev/project-alpha) — 0 dan production gacha **ketma-ket 10 bosqich**. Bu loyiha ham shu prinsipdan foydalanadi. Sabab: [docs/README.md#project-alpha-bilan-moslik](docs/README.md#project-alpha-bilan-moslik).
