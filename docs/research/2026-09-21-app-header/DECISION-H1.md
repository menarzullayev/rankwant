# H1 — App Header chrome shartnomasi

**Sana:** 2026-09-21  
**Qaror:** shared-actions  
**Tanlangan variant:** `shared-actions`  
**CTO tavsiyasi:** shared-actions (qabul qilindi)

## Qaror

O‘ng klaster bitta `<HeaderActions />`. `AppHeader` va `AppTopNav`
faqat chap tomonda farq qiladi.

Tartib (o‘zgarmaydi):

`SearchBox` → `HeaderStatus` → `UpdatesBell` → `CustomizerTrigger` →
`ThemeToggle` → `LocaleSwitch` → `UserMenu`

## Yopiq eshiklar

- **D3.** `StylePicker` qaytmaydi. Palitra — `CustomizerTrigger`.
  `ThemeToggle` H6 da qaytdi (uslub sozlagichda).
- **Qaror 22.** Brend — `BrandMark`.
- **D46.** `navMode: "topnav"` da `AppTopNav` `AppHeader` o‘rnini oladi
  (ikkita lenta bo‘lmasin).

## Rad etilgan

| Variant | Nega emas |
|---|---|
| `one-chrome` | Topnav menubar + ikki xil mobil drawer + sidenav drawer bitta faylda chalkashadi |
| `keep-split` | Drift allaqachon bor edi («tartib bir xil bo‘lsin» izohi) |
| `density-first` | Kesish to‘g‘ri, lekin uni ikki faylda qilish xavfli — avval manba bitta |

## Ta’sir

Vizual o‘zgarish yo‘q. Keyingi header qarorlari (Ctrl+K, zichlik, mobil
qidiruv) bitta faylda yoziladi.
