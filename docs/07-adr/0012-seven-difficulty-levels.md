# ADR-0012: Qiyinlik shkalasi yetti darajaga bo'linadi

**STATUS:** accepted (2026-09-08)
**Ta'siri:** [04-prd](../04-prd/README.md) 🔒 dagi daraja jadvali almashadi

## Muammo

`Problem.difficulty` raqami o'zgarmaydi — 800–3500, qadam 100, Codeforces
bilan mos (o'lchandi: CF API'da 11 087 reytingli masala, aynan shu oraliq
va qadam). O'zgaradigani — raqam qanday **darajaga** aylanishi.

Beshta daraja bilan «Boshlang'ich» 800–1199 ni qamrardi. Bu arxivning eng
gavjum zonasi va yangi o'quvchi u yerda oylab turadi. Arxiv yon panelidagi
progress bloki esa aynan shu zonada **qimirlamaydigan bitta chiziq**
ko'rsatardi — ya'ni motivatsiya vositasi eng kerak bo'lgan joyda ishlamasdi.

KEP.uz shu sababli ettita daraja ishlatadi va pastki qismini maydalaydi.

## Qaror

| Raqam     | Daraja       | Kod            |
| --------- | ------------ | -------------- |
| 800–999   | Boshlang'ich | `beginner`     |
| 1000–1199 | Asosiy       | `basic`        |
| 1200–1499 | O'rta        | `intermediate` |
| 1500–1799 | Yaxshi       | `upper`        |
| 1800–2199 | Qiyin        | `hard`         |
| 2200–2699 | Ekspert      | `expert`       |
| 2700+     | Master       | `master`       |

Tamoyil: **pastki yarmi mayda, yuqorisi keng**. 800–1800 oralig'ida to'rtta
daraja, undan yuqorida uchta — chunki u yerda masala kam va o'quvchi kam.

## Oqibatlar

- Mavjud yorliqlar ma'nosini o'zgartiradi: ilgari «O'rta» 1200–1599 edi,
  endi 1200–1499. Masalalarning `difficulty` raqami tegilmagani uchun
  migratsiya kerak emas, faqat ko'rsatish o'zgaradi.
- `?level=` filtri qiymatlariga ikkita yangi kod qo'shildi (`basic`,
  `upper`); eskilari saqlanib qoldi.
- Ranglar beshta tokendan hosil qilinadi: oraliq ikkitasi CSS `color-mix`
  bilan, shunda o'n to'rtta vizual uslub blokining birortasi tegilmaydi.
- Reytingga ta'siri **yo'q**: Skills `difficulty` raqamidan hisoblanadi
  ([ADR-0007](0007-skills-uses-current-difficulty.md)), daraja yorlig'idan
  emas.

## Muqobillar

- **Beshta darajada qolish** — eng kam ish, lekin progress bloki asosiy
  vazifasini bajarmasdi.
- **Yorliqlar beshta, progress 100 ballik** — 28 ta ustun yon panelga
  sig'maydi va telefonda o'qilmaydi.
