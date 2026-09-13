# Raqobatchi auditi — 2026-09-13

Manba: `C:\Users\nsn\rankwant-audit\` (2026-09-13 da repo'ga ko'chirildi).

## Nima bu

5 ta platforma sahifasining **haqiqiy brauzer surati** — HTML, skrinshot va
tuzilma ma'lumoti. Maqsad: RankWant'ning auth va ro'yxatdan o'tish oqimini
raqobatchilar bilan **o'lchov asosida** solishtirish.

| Papka | Sahifa |
|---|---|
| `01-robocontest-register` | `robocontest.uz/register` |
| `02-robocontest-login` | `robocontest.uz/login` |
| `03-kep-login` | `kep.uz` login |
| `04-rankwant-login` | `rankwant.uz` login |
| `05-rankwant-register` | `rankwant.uz` register |

Har papkada: `page.html` (xom HTML), `shot.png` (skrinshot),
`structure.json` (nodes, fields, buttons, tashqi hostlar).

`summary.json` — hammasining jamlanmasi. `XULOSA-VA-REJA.md` — xulosa va
amalga oshirish rejasi (1- va 2-bosqichlar bajarilgan: commitlar `710d850`,
`e74af03`).

## Nima bu EMAS

⚠️ **Bu audit foydalanuvchi sonlarini o'z ichiga olmaydi.** U UI tuzilmasini
o'lchaydi — nechta maydon, nechta tugma, qanday tashqi host.

Ya'ni bu **`03-market-research` dagi bozor hajmi raqamlarini tiklamaydi**.
Ular boshqa manbadan olingan: `kep-uz-platform-analysis.md` va
`robocontest-uz-platform-analysis.md` — **o'sha ikki fayl repo'da yo'q,
Linux bo'limida qolgan** ([../README.md](../README.md) ga qarang).

## Bog'liq

- [../README.md](../README.md) — bozor hajmi va uning manbasi
- [../competitor-summary.md](../competitor-summary.md) — qisqa jadval
- [../positioning.md](../positioning.md) — SWOT
