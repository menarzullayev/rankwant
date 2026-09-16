# Ikonka kutubxonalari — qiyoslama tadqiqot

**Sana:** 2026-09-15 · **Manbalar:** rasmiy hujjatlar (Google Fonts, Iconify, Radix UI,
Font Awesome), mantlr.com mustaqil qiyosi (2026-04), GitHub repolar.

---

## 1. Asosiy jadval

| Kutubxona | Ikonkalar | Uslublar | To'r | Litsenziya | Figma |
|---|---|---|---|---|---|
| **Phosphor** | **9 000+** | **6** og'irlik (thin · light · regular · bold · fill · **duotone**) | 24×24 | MIT | ✅ |
| **Tabler Icons** | **5 900+** | 2 (outline · filled) | 24×24 | MIT | ✅ |
| **Simple Icons** | 3 000+ | 1 (brend logotiplari) | 24×24 | **CC0 1.0** | ✅ |
| **Remix Icon** | 2 800+ | 2 (line · fill) | 24×24 | Apache 2.0 | — |
| **Material Symbols** | 2 500+ | 3 (outlined · rounded · sharp) + **4 o'zgaruvchan o'q** | o'zgaruvchan | Apache 2.0 | ✅ |
| **Bootstrap Icons** | 2 000+ | 2 | **16×16** | MIT | — |
| **Font Awesome Free** | 2 000+ | 3 (solid · regular · brands) | — | **CC BY 4.0** (ikonka) | ✅ |
| **Iconoir** | 1 600+ | 1 (outline) | 24×24 | MIT | — |
| **Boxicons** | 1 600+ | 3 (regular · solid · logo) | 24×24 | MIT | ✅ |
| **Lucide** | 1 500+ | 1 (outline) | 24×24 | ISC | ✅ |
| **Akar Icons** | 700+ | 1 (outline) | 24×24 | MIT | ✅ |
| **Eva Icons** | 490+ | 2 (outline · fill) | 24×24 | MIT | — |
| **Heroicons** | 300+ / uslub | 4 (outline · solid · mini · micro) | 24/20/16 | MIT | — |
| **Radix Icons** | ~300 | 1 (outline) | **15×15** | MIT | ✅ |
| **Feather** | 287 | 1 (outline) | 24×24 | MIT | — |

### Aggregator

| | |
|---|---|
| **Iconify** | **200+ to'plam · 250 000+ ikonka** — bitta sintaksis bilan. MIT. Bu kutubxona emas, **qatlam**: Lucide, Tabler, Phosphor va boshqalarni bir joydan beradi. |

---

## 2. Har biri qachon mos keladi

### Phosphor — maksimal moslashuvchanlik
6 ta og'irlik, jumladan **duotone** (ikki qatlamli) — boshqa hech kimda yo'q.
Marketing sahifasida `thin`, interfeysda `regular`, tugmalarda `bold` — hammasi
bitta vizual tilda. ⚠️ 9000 ta ikonka ichida chekka holatlar notekis chizilgan
bo'lishi mumkin — tree-shaking shart.

### Tabler — ishonchli ish otı
5900+ ikonka, outline va filled. **Har biri bir xil 24×24 to'r, 2 px chiziq,
6 px burchak** — ko'p ikonkani aralashtirganda ham izchillik saqlanadi. Chiziq
Lucide'dan yupqoroq, interfeys "yengil" ko'rinadi. "Ikonka topilmadi" degan
holat deyarli bo'lmaydi.

### Lucide — ekotizim standarti
`shadcn/ui` ning standarti, ya'ni Next.js/Vercel shablonlarida o'zi keladi.
ISC litsenziya (MIT bilan bir xil amalda). ⚠️ Shu sababli **ko'p mahsulot bir
xil ko'rinadi** — brend farqlanishi muhim bo'lsa, bu kamchilik.

### Heroicons — sifat, miqdor emas
Tailwind Labs tomonidan, 4 ta o'lcham varianti (24/20/16) — zichlikni
boshqarish uchun noyob imkoniyat. ⚠️ 300 ta ikonka — "ombor" yoki "mikroskop"
kabi narsalar yo'q, aralashtirishga to'g'ri keladi.

### Material Symbols — tizim integratsiyasi
**O'zgaruvchan shrift**: bitta fayl, `font-variation-settings` bilan
`fill`/`weight`/`grade`/`optical-size` ni sozlash mumkin. Google ekotizimi
bilan mos. ⚠️ Material dizayn tili — boshqa uslublar yonida begona ko'rinadi.

### Simple Icons — faqat brend logotiplari
3000+ kompaniya logotipi (GitHub, Telegram, Visa...). **CC0** — eng erkin
litsenziya, atribut ham shart emas. ⚠️ Interfeys ikonkalari **yo'q** — faqat
brendlar. Uni alohida ishlatish kerak, asosiy to'plam o'rniga emas.

### Font Awesome — eski standart
Keng tanilgan, lekin **web-shrift davridan**: butun shrift fayli yuklanadi,
tree-shaking yo'q. Pro — obuna. Ikonkalar CC BY 4.0 (atribut talab qiladi).
Ko'chish uchun eng oson yo'l — Lucide (bir xil 24 px chiziqli uslub).

### Bootstrap Icons / Radix Icons — o'z kontekstida
Bootstrap Icons — **16×16** to'r, framework'siz (vanilla, WordPress) ishlash
uchun qulay. Radix Icons — **15×15**, juda ixcham, Radix UI bilan mos.

### Iconify — boshqa yondashuv
Kutubxona emas, **qatlam**: 200+ to'plamni bitta sintaksis bilan beradi va
kerak bo'lgan ikonkani o'sha paytda yuklaydi. ⚠️ Tashqi so'rov (yoki o'z
serveringiz) kerak — offline ishlamaydi.

---

## 3. RankWant uchun baholash

Bizda **41 ta qo'lda yozilgan ikonka** bor (`icons/index.tsx`), `stroke-width: 1.7`,
24×24 to'r. Muammo: **bitta uslub** — uslub almashtirilganda (Neo-brutalizm,
Glassmorphism) ikonkalar o'zgarmaydi.

| Kutubxona | Bizga moslik | Sabab |
|---|---|---|
| **Phosphor** | ⭐⭐⭐⭐⭐ | Yagona kutubxona — **uchala uslubni** beradi. 12 uslubimiz uchun ideal |
| **Tabler** | ⭐⭐⭐⭐ | 5900+ ikonka, izchil to'r, outline↔filled almashinuvi bor |
| **Lucide** | ⭐⭐⭐ | Yengil, lekin faqat outline — uslub bilan moslashmaydi |
| **Heroicons** | ⭐⭐⭐ | Sifatli, lekin 300 ta — qoplash yetmaydi |
| **Simple Icons** | ⭐⭐ | Faqat brendlar — **qo'shimcha** sifatida foydali |
| **Iconify** | ⭐⭐ | Tashqi so'rov — bizning SSR/offline talabimizga zid |

**Xulosa:** bizga **Phosphor** eng mos — chunki u yagona kutubxona bo'lib
`duotone` ni ham beradi, va 12 ta uslubimiz (ayniqsa Neo-brutalizm,
Glassmorphism, Skeuomorfizm) uchun solid/duotone varianti kerak bo'ladi.

**Aralash strategiya ham mumkin:** Phosphor (asosiy interfeys) + Simple Icons
(brend logotiplari: Telegram, GitHub, Google — hozir qo'lda chizilgan).

---

## 4. Litsenziya — amalda nima farq qiladi

| Litsenziya | Kutubxonalar | Nima talab qiladi |
|---|---|---|
| **MIT** | Phosphor, Tabler, Heroicons, Bootstrap, Boxicons, Akar, Eva, Radix, Feather, Iconify | Copyright qaydini kodda saqlash. Boshqa shart yo'q |
| **ISC** | Lucide | MIT bilan amalda bir xil |
| **CC0 1.0** | Simple Icons | **Hech narsa** — atribut ham shart emas |
| **Apache 2.0** | Remix Icon, Material Symbols | O'zgartirilgan bo'lsa, o'zgarishni hujjatlashtirish |
| **CC BY 4.0** | Font Awesome (ikonkalar) | **Atribut majburiy** — kod MIT, shrift OFL |

⚠️ **GPL yo'q** — ro'yxatdagi hech bir kutubxona loyihangizni ochiq kodli
qilishga majburlamaydi.
