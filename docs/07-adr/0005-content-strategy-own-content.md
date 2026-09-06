# ADR-0005: Kontent strategiyasi — o'z kontent, cp.uz bog'liqlik emas

**STATUS:** accepted (2026-09-06)

## Muammo

Qulflangan vision (`01-vision`) cp.uz ni «alohida loyiha; RankWant unga bog'liq emas» deb belgiladi va long-term goal #2 ni **«o'zbek kontent ustunligi — o'z maqola, mavzu roadmap va masala izohlari»** qilib qo'ydi.

Lekin draft bosqichlarda cp.uz hali ham **bog'liqlik va differensiator** sifatida turgan edi — 9 faylda 10 ta joy:

- `03-market-research/positioning.md` — differensiator #2 = «cp.uz chuqur integratsiya»
- `04-prd` — P2-5 «cp.uz maqola ↔ masala link»
- `05-domain-model` — `cp_uz_article_id` maydoni
- `06-architecture`, `08-technical-spec`, `09-development-plan` — integratsiya API, «kontent hamkor»
- `INDEX.md`, `02-problem-discovery`, `03-market-research/competitor-summary.md`

Ya'ni qulflangan bosqich bilan draft bosqichlar bir-biriga zid edi.

## Variantlar

1. **To'liq mustaqil** — cp.uz faqat raqobatchi/benchmark; barcha bog'liqlik olib tashlanadi
2. **Ixtiyoriy hamkorlik** — bog'liqlik emas, lekin umumiy `external_article_url` bilan eshik ochiq qoladi
3. **Vision'ni yumshatish** — draftlar to'g'ri deb qabul qilinadi, qulflangan vision qatori o'zgartiriladi

## Tanlov

**Variant 1 — to'liq mustaqil.**

## Sabab

- Siz nazorat qilmaydigan uchinchi tomon **differensiator bo'la olmaydi** — hamkorlik buzilsa, pozitsiya ham quladi
- Vision goal #2 allaqachon «o'z maqola, roadmap» deydi; cp.uz integratsiyasi bu maqsad bilan **raqobatlashadi**, uni qo'llab-quvvatlamaydi
- `cp_uz_article_id` uchinchi tomon nomini **schema darajasida** kiritadi — bu eng qimmat va eng uzoq yashaydigan bog'liqlik turi
- YAGNI: hamkorlik keyinchalik kerak bo'lsa, o'shanda ADR yoziladi

## Oqibatlar

**O'zgaradi:**

| Fayl                                     | O'zgarish                                                        |
| ---------------------------------------- | ---------------------------------------------------------------- |
| `INDEX.md`                               | maqsad → «o'z o'zbek kontenti bilan»                             |
| `02-problem-discovery`                   | UC-5 → maqoladan masalaga o'tish, o'z kontent ichida             |
| `03-market-research/positioning.md`      | Strength va differensiator #2 → **o'z** kontent chuqurligi       |
| `03-market-research/competitor-summary.md` | «Kurslar» ustuni → o'z maqola + roadmap                        |
| `03-market-research/README.md`           | imkoniyat qatori aniqlashtirildi (o'zimiz quramiz)               |
| `04-prd`                                 | P2-5 «cp.uz link» → **«O'z o'qish kontenti — maqola + roadmap»** |
| `05-domain-model`                        | `cp_uz_article_id` olib tashlandi                                |
| `06-architecture`                        | «o'z/cp.uz kontent» → «o'z kontent»; integratsiya ro'yxatidan chiqdi |
| `08-technical-spec`                      | «cp.uz integratsiya API» bandi olib tashlandi                    |
| `09-development-plan`                    | link API olib tashlandi; Content roli va bog'liq loyihalar yangilandi |

**Saqlanadi** (raqobatchi tahlili sifatida to'g'ri): competitor jadval qatorlari, `INDEX.md` tashqi manba va «qilinmasin» bandlari, `04-prd` out-of-scope «cp.uz fork», `positioning.md` opportunity va positioning map.

**Diqqat:** P2-5 shunchaki o'chirilmadi — o'rniga **o'z o'qish kontenti** feature'i qo'yildi. Sabab: differensiator #2 endi «o'z kontent chuqurligi», va uni qo'llab-quvvatlaydigan PRD bandisiz differensiator bo'sh qolar edi.

**Kelajak uchun:** cp.uz yoki boshqa tashqi manba bilan integratsiya kerak bo'lsa — yangi ADR va **umumiy** `external_article_url` yondashuvi (bitta hamkorga bog'lanmagan schema).

## Bog'liq hujjatlar

- [../01-vision/README.md](../01-vision/README.md) — goal #2, «Emas» bo'limi
- [../03-market-research/positioning.md](../03-market-research/positioning.md)
- [0006-rating-model.md](0006-rating-model.md)
