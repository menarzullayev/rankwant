# Positioning — RankWant

**STATUS:** locked (2026-09-06) — `03` bilan birga

## One-liner

**RankWant** — O'zbek va global sport dasturlash platformasi: reyting xohlaganlar uchun judge, musobaqa va o'qish — **Qvant** mukofotlari bilan.

## SWOT

### Strengths (reja)

- Aniq motivatsion brend (RankWant)
- Raqobatchi tahlili tayyor (KEP/Robo/cp.uz)
- Qvant — qisqa, alohida coin brendi
- Ochiq API (DRF Spectacular) + **o'z judge engine** — [ADR-0003](../07-adr/0003-stack-django-next.md), [ADR-0004](../07-adr/0004-judge-engine.md)
- O'z o'zbek kontenti rejasi (maqola + roadmap)

### Weaknesses

- Yangi jamoa, 0 user
- Judge infra murakkab va qimmat — sandbox xavfsizligi mas'uliyati bizda ([ADR-0004](../07-adr/0004-judge-engine.md))
- RoboContest 197k network effect

### Opportunities

- cp.uz OJ bo'shliği
- Maktab B2B (Robo Judge rejasi isbotlangan)
- Mirror davlat olimpiadalari
- Telegram auth / bot (RoboContest pattern)

### Threats

- RoboContest/KEP tez yangilanishi
- Aurora white-label raqobatchilar
- Coin/regulyatsiya (real pul sovrin)

## Differensial (maqsad)

| #   | RankWant                                                     |
| --- | ------------------------------------------------------------ |
| 1   | **RankWant** brendi — reyting motivatsiyasi birinchi planada |
| 2   | **O'z o'zbek kontenti chuqurligi** — maqola ↔ masala ↔ mavsum |
| 3   | **Ochiq API** — mobile, bot, tashqi judge                    |
| 4   | **Qvant** — sodda coin nomi, KEP/Robo UX pattern             |
| 5   | **O'zbek + EN** — global nom, mahalliy kontent               |

## Positioning map (soddalashtirilgan)

```
O'qish chuqurligi
        ↑
   cp.uz │     RankWant (maqsad)
        │
        │  KEP
        │
        └──────────────────→ OJ / Contest kuchliligi
              RoboContest
```

## Narx (hozircha)

RoboContest 4 tier (Free/Plus/Pro/Judge) — benchmark. RankWant narxlari PRD/ADR dan keyin.
