# RankWant · Contest reytingi — qarorlar

> **Arxiv yozuvi.** Repoga 2026-10-04 da ko'chirildi; matn yozilgan kunidagi holatni aks ettiradi. `QARORLAR.html`, `QARORLAR.png`, `outputs/…` va `2026-09-20-kep-rank-icons/…` repodan tashqarida, `cp/` da qoladi. Amaldagi qaror: 16 pog'ona, 7 rang guruhi (`CLAUDE.md`).

Sana: 2026-09-20. Maqsad: contest reytingi doirasidagi barcha ochiq qarorlar
bitta hujjatda — o'lchangan holat, variantlar, tavsiya. **Qaror — Saidakbar
akada**, hujjat asoslash uchun.

## Asosiy topilma (hujjatni o'qishdan oldin)

**RankWant'da `rated_contest_count > 0` bo'lgan foydalanuvchi yo'q — 0 ta.**
Unvon olgan hech kim yo'q. Zinapoyani, rangni, nomni, chegaralarni
**hozir bepul** o'zgartirish mumkin — hech kimga zarar yetkazmaydi.

Bevosita o'lchov (2026-09-20):
- 974 498 foydalanuvchi bor, lekin hammasi **CF'dan import** — ularning
  `cf_title` (CF'niki) to'la, `title` (RankWant'niki) **None**.
- CF taqsimoti juda pastga og'ir: **63%** newbie (0–1199).

## 7 ta qaror

| # | Savol | Tavsiya |
| --- | --- | --- |
| **Q1** | Pog'ona soni | **10** — o'lchov bo'yicha optimum (ΔE ≥ 0.076) |
| **Q2** | Rang sxemasi | **E — Ajratilgan 10** — Kvark↔Elektron 0.081 (eng yaxshi) |
| **Q3** | Chegaralar | **Pastki qismni maydalash** + 10 pog'ona (gavjum zona uchun) |
| **Q4** | Nomlash | **Alohida qaror**, hozircha Qvant oilasi (jonli) |
| **Q5** | CF unvoni bilan | **Parallel + «Codeforces» nishoni** (974k uchun) |
| **Q6** | Ikonka | **Hozircha yo'q** (CF usuli), keyin geometrik/harf |
| **Q7** | Faqat rang yetarlimi | **Rang + qalin shrift + matn** (ADR-0018 davomi) |

## Bitta butun tavsiya

```
10 pog'ona · ajratilgan ranglar · CF bilan parallel · ikonkasiz
```

Bu — **eng xavfsiz va eng kuchli** boshlang'ich nuqta: o'lchov bilan
asoslangan, brend uzluksiz, vaqt sinovi bor (CF shunday qilgan).

Qarorlar bog'liq:
- Q1 → Q2: 10 pog'ona tanlanadi → sxema E ishlatiladi.
- Q3 → Q1: 10 pog'onaga mos chegaralar tanlanadi.
- Q5 → Q1: CF unvoni bilan parallel — 974k import uchun zarur.

## Manba (barcha raqamlar o'lchangan)

| Topilma | Manba |
| --- | --- |
| ΔE 0.076/0.081 ajralish | `2026-09-20-contest-rating-decisions/QARORLAR.html` |
| AA 4.50–4.61 18 palitrada | `outputs/rankwant-rating-colors.html` |
| KEP rang/ikonalar | `2026-09-20-kep-rank-icons/TAHLIL.html` |
| ADR-0006 (4 reyting) | `rankwant/docs/07-adr/0006-rating-model.md` |
| ADR-0018 (9 pog'ona) | `rankwant/docs/07-adr/0018-titles-roles-achievements.md` |
| ADR-0012 (pastki maydalash) | `rankwant/docs/07-adr/0012-seven-difficulty-levels.md` |
| ADR-0026 (CF sync) | `rankwant/docs/07-adr/0026-codeforces-user-sync.md` |

## Yetkazildi

- `research/2026-09-20-contest-rating-decisions/QARORLAR.html` —
  7 ta qaror, har biri o'lchov + 3–4 variant + tavsiya + meta
- `research/2026-09-20-contest-rating-decisions/QARORLAR.png` —
  vizual tasdiq
- `research/2026-09-20-contest-rating-decisions/HISOBOT.md` — shu hujjat

## Qaror sharti

Har qaror mustaqil — siz barchasini bir vaqtda qabul qilishingiz shart emas.
Tavsiya: Q1+Q2+Q5 birgalikda, Q3 Q1 ga bog'liq, Q4 va Q6 alohida vaqt
bilan, Q7 qolganlar bilan birga.