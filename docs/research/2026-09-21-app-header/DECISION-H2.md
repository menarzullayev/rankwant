# H2 — Ctrl+K egasi

**Sana:** 2026-09-21  
**Qaror:** search-owns  
**Tanlangan variant:** `search-owns`  
**CTO tavsiyasi:** search-owns (qabul qilindi)

## Qaror

`Ctrl+K` / `Cmd+K` faqat `SearchBox` ga tegishli (D61 ⑦).
`CommandPalette` mahsulot `AppShell` dan chiqarildi va `Ctrl+K`
tinglovchisini yo‘qotdi.

Kit fayli qoladi: tanlangan kit muzlatuvi clipboard toastni
(`problem.copyFailed`) shu faylda saqlaydi.

## Rad etilgan

| Variant | Nega emas |
|---|---|
| `palette-owns` | Header `Ctrl K` yorlig‘i yolg‘on bo‘ladi |
| `unify` | To‘g‘ri mahsulot (studio p01), lekin ikki eshikni hozir yopmaydi |
| `leave-race` | Hozirgi xato |

## Ta’sir

Qidiruv maydoni `md+` da ko‘rinadi; `Ctrl+K` fokusni shu yerga olib
keladi. Mobilida maydon yashirin — bu H3 masalasi.
