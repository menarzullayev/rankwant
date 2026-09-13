# RankWant — agent indeksi

**Workspace:** `/home/nsn/Workspace/Web_Projects/rankwant/`  
**Maqsad:** CP/OJ + musobaqa platformasi (KEP/RoboContest darajasida, o'z o'zbek kontenti bilan)

## O'qish tartibi

1. [README.md](README.md)
2. [docs/README.md](docs/README.md) — pipeline holati
3. [docs/01-vision/README.md](docs/01-vision/README.md)
4. [docs/03-market-research/README.md](docs/03-market-research/README.md)
5. Kerak bo'lsa: [docs/04-prd/README.md](docs/04-prd/README.md), [docs/05-domain-model/README.md](docs/05-domain-model/README.md)

## Tashqi manbalar (o'zgartirmaslik)

⚠️ Quyidagi uchta yo'l **Linux o'rnatilmasiga** tegishli
(`/home/nsn/...`). Windows nusxasida ular **yo'q** — 2026-09-13 da
qidirildi. Windows'da ishlayotganingizda bu fayllar mavjud emas deb
hisoblang.

| Fayl                    | Yo'l                                                                    |
| ----------------------- | ----------------------------------------------------------------------- |
| KEP tahlili             | `../kep-uz-platform-analysis.md` — ⚠️ Linux'da, Windows'da yo'q          |
| RoboContest tahlili     | `../robocontest-uz-platform-analysis.md` — ⚠️ Linux'da, Windows'da yo'q   |
| cp.uz klon (benchmark)  | `../cp-uz/`                                                             |
| Brend availability JSON | `/home/nsn/Telegram/handlechecker/results/rank_brand_availability.json` |

## Qattiq qarorlar (locked)

- Platforma: **RankWant** — `docs/01-vision/` 🔒 2026-09-06
- Coin: **Qvant** — ADR [0001](docs/07-adr/0001-brand-rankwant-qvant.md) accepted
- Problem discovery + **North Star** (haftalik faol yechuvchi) — `docs/02-problem-discovery/` 🔒 2026-09-06
- Kontent: **o'z kontent**, cp.uz bog'liqlik emas — ADR [0005](docs/07-adr/0005-content-strategy-own-content.md) accepted
- Reyting: **4 ta** (Skills/Activity/Contests/Challenges), fazali ochilish — ADR [0006](docs/07-adr/0006-rating-model.md) accepted
- Stack: **Django 5.2 LTS + DRF** (backend) + **Next.js** (frontend) — ADR [0003](docs/07-adr/0003-stack-django-next.md) accepted
- Kod **yopiq/tijorat** → AGPL loyihalarni (DMOJ, Hydro) fork qilmaymiz
- Judge: **o'z engine**, sandbox tayyor olinadi — ADR [0004](docs/07-adr/0004-judge-engine.md) bake-off (Go+nsjail vs Python+isolate)
- Qvant: **yopiq loop**, faqat kosmetik sink — ADR [0002](docs/07-adr/0002-qvant-economy.md) accepted
- Market + bozor hajmi — `docs/03-market-research/` 🔒 2026-09-06
- PRD (MVP scope, reyting formulalari, Qvant) — `docs/04-prd/` 🔒 2026-09-06
- Domain model (entity, indeks, migration) — `docs/05-domain-model/` 🔒 2026-09-06
- Arxitektura + xavfsizlik chegarasi — `docs/06-architecture/` 🔒 2026-09-06
- Tech spec (auth, API, judge protokoli) — `docs/08-technical-spec/` 🔒 2026-09-06
- Dev plan (kritik yo'l, DoD, launch gate) — `docs/09-development-plan/` 🔒 2026-09-06
- Auth: **session (web) + PAT (API)** — ADR [0008](docs/07-adr/0008-auth-session-plus-pat.md) accepted
- Clone emas — feature/UX pattern benchmark

## Qilinmasin

- KEP/Robo UI yoki API ni 1:1 nusxalash
- Sandbox primitivini o'zimiz yozish (namespace/seccomp/cgroup) — tayyor nsjail/isolate olinadi
- Foydalanuvchi kodini API yoki DB hostida ishga tushirish
- cp.uz security fix (alohida so'rov bo'lmasa)
- `rankwantcoin` Telegram handle — foydalanuvchi rad etgan
