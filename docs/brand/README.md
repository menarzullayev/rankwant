# Brend aktivlari

## Logotip — bitta manba

[`mark-choqqi.svg`](mark-choqqi.svg) — **haqiqat manbai**. U
[`10-choqqi.png`](belgi-generated/10-choqqi.png) dan 1:1 rekonstruksiya;
o'lchamlar va ranglar [`mark-choqqi-params.md`](mark-choqqi-params.md) da.

Boshqa hamma format shundan generatsiya qilinadi va **qo'lda tahrirlanmaydi**:

```bash
python3 tools/brand.py
```

| Chiqadigan fayl | Qayerda ishlatiladi |
| --------------- | ------------------- |
| `brand/mark-choqqi.svg` | sayt, hujjatlar |
| `brand/mark-choqqi-dark.svg` | ixtiyoriy — qorong'i fonda konturga ko'proq aniqlik kerak bo'lsa |
| `brand/mark-32.png` | kichik ikonka |
| `brand/mark-96.png` | **xat sarlavhasi** (48px, Retina uchun 2x) |
| `brand/mark-180.png` | Apple touch icon |
| `brand/mark-192.png` · `mark-512.png` | PWA manifesti |
| `favicon.ico` | brauzer yorlig'i (16/32/48 bitta faylda) |

Hammasi `apps/web/public/` ichida.

**Logotipni o'zgartirish** = `mark-choqqi.svg` ni tahrirlash va buyruqni qayta
ishga tushirish. Yettita joyni qo'lda yangilash kerak emas — aynan shu sababli
skript bor: kimdir bittasini unutsa, sayt ikki xil belgi ko'rsatib turardi.

Texnik jihatdan arzon bo'lgani bilan, ishga tushgandan keyin **brend jihatdan**
qimmatlashadi: yuborilgan xatlar eski logotip bilan qoladi.

## O'lchangan xususiyatlari

| Nima | Natija |
| ---- | ------ |
| Shaffoflik | bor (PNG `tRNS`) |
| 16px da ranglar | 54 — hammasi silliqlash soyalari |
| Qorong'i fonda navy kontur | `#202124` ga nisbatan **1.01:1**, ya'ni ko'rinmaydi |

Oxirgi qator muammo emas: siluetni **ko'k tana** ushlab turadi, kontur esa
shunchaki orqaga chekinadi — belgi qorong'i fonda ham to'liq o'qiladi.
Ko'proq aniqlik kerak bo'lgan joyda `mark-choqqi-dark.svg` ishlatiladi
(navy `#102038` → `#33507e`, qolgan ranglar tegilmaydi).

## Nusxalar

`belgi-generated/10-choqqi.svg` va `apps/web/public/brand/mark-choqqi.svg` —
manbaning nusxalari. Ikkinchisini skript qayta yozadi; birinchisi arxiv
snapshot'i. **Ikkalasi ham tahrirlanmaydi.**

## `belgi-generated/`

Rasm generatoridan chiqqan 24 ta konsepsiya — arxiv. Ular JPEG (nomi `.png`
bo'lsa ham), ya'ni shaffofligi yo'q va chetlari notekis. Ular tanlash uchun
edi, chop etish uchun emas — o'lchandi: 16px ga kichraytirilganda 101 xil
rang berardi.

Promptlar: [`belgi-promptlari.md`](belgi-promptlari.md).
