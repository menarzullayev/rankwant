# LOCK-GATE vizual prototip

**Maqsad:** [`LOCK-GATE.md`](../LOCK-GATE.md) bandlarini ko‘z bilan baholash — tasdiqdan oldin.

## Ochish

Windows (PowerShell):

```powershell
Start-Process "d:\Linux\Web_Projects\rankwant\docs\brand\lock-gate-prototype\lock-gate-review.html"
```

Yoki faylni brauzerda oching: `lock-gate-review.html`.

PNG/SVG yo‘llari repo ildizidan HTTP orqali yuklanadi. `file://` ochilsa ko‘plab rasmlar va SVG **buziladi** — server shart.

## Fayllar

| Fayl | LOCK-GATE | Izoh |
|------|-----------|------|
| `lock-gate-review.html` | A–C | Barcha bo‘limlar bir sahifada |
| `crest-black.svg` | B5 | Monochrome prototip (hali production emas) |
| `crest-white.svg` | B5 | Qorong‘i fon uchun |
| `lockup-horizontal.svg` | B3, O3 | Crest + RankWant matn |

## Tasdiq

1. Sahifani ko‘rib chiqing (ayniqsa **16px** va **OG**).
2. Ma’qul bo‘lsa — `LOCK-GATE.md` qaror jadvalida PASS va ixtiyoriy izoh.
3. Monochrome / lockup qabul qilinsa — keyingi PR: `docs/brand/` + ixtiyoriy `tools/brand.py` kengaytmasi.

Bu papkadagi SVGlar **prototip**; `python3 tools/brand.py` ularni hozir chiqarmaydi.
