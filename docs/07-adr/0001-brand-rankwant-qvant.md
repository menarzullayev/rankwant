# ADR-0001: Platforma brendi RankWant, ichki valyuta Qvant

**STATUS:** accepted (2026-09-06)

## Muammo

Yangi CP platformasi uchun global eshitiladigan nom va ichki coin kerak. KEP (kepcoin) va RoboContest (robocoin) pattern bor; `@olympiq` va mahalliy nomlar mos emas.

## Variantlar

1. **RankWant + Qvant** — platforma motivatsion, coin qisqa
2. **Rankvant + rankvantcoin** — professional, lekin coin og'ir
3. **RankWant + rankwantcoin** — bir brend, coin uzun
4. **OlympIQ** — band
5. **Boshqa Rank*** (Rankstell, Rankion, …) — Tier A, lekin ma'no zaifroq

## Tanlov

**RankWant** (platforma) + **Qvant** (coin).

## Sabab

- RankWant slogan sifatida ishlaydi: «reyting xohlaganlar uchun»
- Qvant 5 harf, alohida «olam» — UI da yaxshi (`+50 Qvant`)
- KEP↔kepcoin, Robo↔robocoin **rol ajratishi** saqlanadi, lekin coin qisqaroq
- @rankwant, @qvantcoin tekshiruv vaqtida bo'sh

## Oqibatlar

- Domen: rankwant.uz (asosiy), qvantcoin.uz (coin/marketing)
- Kodda prefix: `rankwant_*` repo/env; coin field `qvant` / `qvant_amount`
- `rankwantcoin` ishlatilmaydi
- Rankvant — zaxira yozuv (domenda), asosiy brend RankWant

## Xavflar (brend)

| Xavf                                                         | Mitigatsiya                                                             |
| ------------------------------------------------------------ | ----------------------------------------------------------------------- |
| **Kvants** / **Kuant** — crypto/DeFi loyihalar fonetik yaqin | CP platformasi + RankWant juftligi; marketingda to'liq «RankWant Qvant» |
| `@qvant` Telegram **TAKEN**                                  | Rasmiy: `@qvantcoin`; UI da «Qvant», handle ni coin kanaliga bog'lash   |
| `qvant.com` DNS band                                         | Asosiy: `rankwant.uz`; coin: `qvantcoin.uz`                             |
| Foydalanuvchi «kvant» deb qidiradi                           | SEO/branding: Qvant — RankWant ichki valyutasi (crypto emas)            |

## Bog'liq hujjatlar

- [../03-market-research/brand-discovery.md](../03-market-research/brand-discovery.md)
- [../01-vision/README.md](../01-vision/README.md)
