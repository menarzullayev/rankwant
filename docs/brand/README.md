# Brend aktivlari

## Logotip — bitta manba

`logo.svg` — **haqiqat manbai**. Boshqa hamma format shundan generatsiya
qilinadi va qo'lda tahrirlanmaydi:

```bash
python3 tools/brand.py
```

Chiqadigan fayllar (`apps/web/public/` ichida, `.gitignore` da emas):

| Fayl | Qayerda ishlatiladi |
| ---- | ------------------- |
| `brand/logo.svg` · `logo-dark.svg` | sayt, hujjatlar |
| `brand/logo-32.png` | kichik ikonka |
| `brand/logo-96.png` | **xat sarlavhasi** (48px, Retina uchun 2x) |
| `brand/logo-180.png` | Apple touch icon |
| `brand/logo-192.png` · `logo-512.png` | PWA manifesti |
| `favicon.ico` | brauzer yorlig'i (16/32/48 bitta faylda) |

**Logotipni o'zgartirish** = `logo.svg` dagi ikkita shaklni tahrirlash va
buyruqni qayta ishga tushirish. Yetti joyni qo'lda yangilash kerak emas —
aynan shu sababli skript bor: kimdir bittasini unutsa, sayt ikki xil belgi
ko'rsatib turardi.

Texnik jihatdan arzon bo'lgani bilan, ishga tushgandan keyin **brend
jihatdan** qimmatlashadi: yuborilgan xatlar eski logotip bilan qoladi va
odamlar tanigan belgi o'zgaradi.

## Belgining o'zi

**10 · Cho'qqi** — ikki cho'qqi va ustidagi nuqta.

Bitta rangda (`#4470e6`, qorong'i fonda `#7ea4ff`). Ikkinchi rang favicon
o'lchamida qo'shimcha ma'lumot bermaydi, faqat loyqalik beradi — o'lchandi:
generatsiya qilingan variant 16px ga kichraytirilganda 101 xil rang berardi,
toza vektor 34 ta (hammasi bitta ko'kning silliqlash soyalari).

## `belgi-generated/`

Rasm generatoridan chiqqan 24 ta konsepsiya — **arxiv**, ishlatilmaydi.
Ular JPEG (nomi `.png` bo'lsa ham), ya'ni shaffofligi yo'q va chetlari
notekis. Ular tanlash uchun edi, chop etish uchun emas.

Promptlar: [`belgi-promptlari.md`](belgi-promptlari.md).
