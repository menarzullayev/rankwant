# Animatsiyali ikonkalar — to'liq manbalar ro'yxati

**Sana:** 2026-09-15 · **Manbalar:** rasmiy saytlar (Lordicon, LottieFiles, Unicorn Icons,
lucide-animated), GitHub repolar, Iconify metadata, mustaqil qiyoslar (2026-04…06).

Iconify'dagi 3 ta to'plamdan tashqari **yana 6+ manba** bor. Ular **to'rt xil
texnologiyada** — bu eng muhim farq.

---

## 1. Texnologiyalar — avval shuni tushunish kerak

| Texnologiya | Format | Nima kerak | Interaktiv | Hajm |
|---|---|---|---|---|
| **SVG `<animate>`** | inline SVG | **hech narsa** | ❌ | eng kichik |
| **Motion** (framer-motion) | React komponent | JS kutubxona (~30 KB) | ✅ hover/click | kichik |
| **Lottie** | JSON | `lottie-web` runtime (~60 KB) | ⚠️ qisman | o'rta |
| **Rive** | `.riv` | Rive runtime (~100 KB) | ✅ **state machine** | katta |

**Amaliy farq:**
- **SVG `<animate>`** — brauzer o'zi bajaradi. CSS ham, JS ham kerak emas.
- **Motion** — React loyihada tabiiy, lekin JS kutubxonasi qo'shiladi.
- **Lottie** — After Effects animatsiyalari, sifatli, lekin runtime kerak.
- **Rive** — **interaktiv**: hover/click/scroll ga **holat mashinasi** orqali javob beradi.

---

## 2. Ochiq va bepul manbalar

### 2.1. Iconify animatsiyali to'plamlari (SVG `<animate>`)
**Bizning `animated.html` da ko'rsatilgan** — 1 711 ikonka, hammasi **MIT**.

| To'plam | Ikonka | To'r |
|---|---|---|
| line-md | 1 218 | 24px |
| meteocons | 447 | 32px |
| svg-spinners | 46 | 24px |

✅ **Eng yengil yo'l** — runtime kerak emas, jsDelivr'dan olinadi.

### 2.2. lucide-animated — 350+ ikonka, **MIT**
`github.com/pqoqubbw/icons` · `lucide-animated.com`

- **Motion** (framer-motion) asosida, **Lucide** ikonkalari
- **shadcn** orqali o'rnatiladi: `pnpm dlx shadcn add @lucide-animated/`
- ⭐ **Bizga eng mos:** biz allaqachon Lucide'ni tavsiya qilganmiz — bu uning
  animatsiyali varianti, ya'ni **bir xil dizayn tili**

⚠️ React + Motion kerak (bizda Next.js + React bor ✅)

### 2.3. animateicons — bepul, ochiq
`github.com/Avijit07x/animateicons`

- Animatsiyali SVG ikonkalar, React uchun
- Mikro-interaksiyalar uchun (hover effektlari)
- Litsenziya: ochiq (repo'da tekshirish kerak)

### 2.4. IconPark (ByteDance) — 2 600+ ikonka
`iconpark.oceanengine.com`

- **Bitta SVG manba → 4 mavzu** (outline, filled, two-tone, multi-color)
- Ochiq litsenziya (Apache 2.0)
- Animatsiya — to'liq emas, lekin **mavzu almashtirish** kuchli imkoniyat

### 2.5. useAnimations — Lottie mikro-animatsiyalar
`useanimations.com`

- Lottie formatidagi tayyor mikro-animatsiyalar
- Bepul, lekin **Lottie runtime** kerak
- Kichik to'plam (o'nlab)

### 2.6. LottieFiles — minglab bepul
`lottiefiles.com/free-animations/icon`

- Eng katta jamoa kutubxonasi (millionlab fayl)
- ⚠️ **Sifat har xil** — jamoa yuklagan, tekshirilmagan
- ⚠️ Litsenziya har faylda boshqacha — **tekshirish shart**

---

## 3. Tijorat platformalar

| Platforma | Ikonka | Texnologiya | Narx | Izoh |
|---|---|---|---|---|
| **Lordicon** | **47 800+** | Lottie | $8/oy (yillik) | `<lord-icon>` web komponent, sifatli, bir uslub |
| **Unicorn Icons** | 400+ | Lottie + **Rive** | **$59 bir marta** | Yagona **native Rive** manbasi |
| **Icons8** | ko'p | Lottie | $14.99/oy | Animatsiya — ikkilamchi |
| **Iconscout** | ko'p | Lottie | $19/oy | Figma integratsiyasi kuchli |

⚠️ **Diqqat:** Lordicon'da **bepul qism ham bor** (o'lchandi: ~50-100 ikonka,
ro'yxatdan o'tmasdan yuklab olish mumkin). Lekin litsenziya **atribut talab qiladi**.

**3 yillik xarajat qiyosi:**
| Platforma | 3 yil |
|---|---|
| Unicorn Icons | **$59** (bir marta) |
| Lordicon | $288 |
| Icons8 | $540 |
| Iconscout | $684 |
| LottieFiles | $720 |

---

## 4. RankWant uchun tavsiya

### Eng mos — **lucide-animated** (MIT, 350+)
| Sabab | Tafsilot |
|---|---|
| **Bir xil dizayn tili** | Lucide'ni allaqachon tavsiya qilganmiz — bu uning animatsiyali varianti |
| **MIT litsenziya** | To'liq erkin, tijorat uchun ruxsat |
| **React + Motion** | Bizda Next.js + React bor |
| **shadcn** | CLI bilan o'rnatiladi, kod bizning repo'da qoladi |
| **Yengil** | Faqat kerakli ikonkalar import qilinadi |

### Qo'shimcha — **Iconify `svg-spinners`** (46, MIT)
Yuklanish holatlari uchun. **Runtime kerak emas** — eng arzon yechim.

### Nima uchun Lottie/Rive **tavsiya qilmayman**
| Sabab | Tafsilot |
|---|---|
| **Runtime og'irligi** | Lottie ~60 KB, Rive ~100 KB — 46 KB ikonka to'plami uchun juda ko'p |
| **Kontrast nazorati** | Bizda `check_contrast.py` bor — Lottie/Rive ranglarini **o'lchab bo'lmaydi** |
| **Litsenziya** | Sifatli to'plamlar tijorat; bepul qismi atribut talab qiladi |
| **SSR** | Lottie/Rive klient tomonida ishlaydi — bizning SSR naqshimizga zid |

---

## 5. Xulosa jadvali

| Manba | Ikonka | Texnologiya | Litsenziya | Narx | RankWant |
|---|---|---|---|---|---|
| **Iconify (line-md)** | 1 218 | SVG `<animate>` | **MIT** | bepul | ✅ |
| **Iconify (svg-spinners)** | 46 | SVG `<animate>` | **MIT** | bepul | ✅ **eng mos** |
| **Iconify (meteocons)** | 447 | SVG `<animate>` | MIT | bepul | ⚪ kerak emas |
| **lucide-animated** | 350+ | Motion | **MIT** | bepul | ✅ **asosiy tavsiya** |
| **animateicons** | o'nlab | SVG + JS | ochiq | bepul | ⚪ |
| **IconPark** | 2 600+ | SVG (4 mavzu) | Apache 2.0 | bepul | ⚪ |
| **useAnimations** | o'nlab | Lottie | bepul | bepul | ⚠️ runtime |
| **LottieFiles** | millionlab | Lottie | har xil | bepul/$. | ⚠️ sifat |
| **Lordicon** | 47 800+ | Lottie | tijorat | $96/yil | ❌ |
| **Unicorn Icons** | 400+ | Lottie + Rive | tijorat | $59 | ❌ |

---

## 6. Amaliy qadam (agar qaror qilinsa)

1. **`svg-spinners`** (46, MIT) — yuklanish holatlari, runtime yo'q, darhol
2. **`lucide-animated`** (350+, MIT) — asosiy animatsiyali to'plam, shadcn orqali
3. **`line-md`** (1 218, MIT) — zaxira, kerak bo'lsa

Uchtasi ham **MIT** — litsenziya xavfi yo'q, runtime yuklamasi minimal.
