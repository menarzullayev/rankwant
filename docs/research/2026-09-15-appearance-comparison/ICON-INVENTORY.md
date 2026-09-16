# RankWant — ikonka inventarizatsiyasi (to'liq)

**Sana:** 2026-09-15 · **Usul:** kod tahlili — 79 ta sahifa (`app/**/page.tsx`),
40+ komponent (`components/`), 24 ta fayl ikonka ishlatadi.

**Xulosa:** hozir **43 ta** ikonka ishlatiladi, lekin platforma uchun
**~220 ta** kerak. Ya'ni qamrov **20 %** — bu sizning "41 ta emas, ancha ko'p"
degan fikringizni tasdiqlaydi.

---

## 1. Hozirgi holat — o'lchandi

| Ko'rsatkich | Qiymat |
|---|---|
| Mavjud ikonkalar | **43 ta** (42 ta `export` + `BrandIcon`) |
| Ikonka ishlatadigan fayllar | **24 ta** |
| Sahifalar | **79 ta** |
| Komponentlar | **40+ ta** |
| **Eng ko'p ishlatilgan** | `CloseIcon` (16) · `CheckIcon` (13) · `BrandIcon` (12) · `PaletteIcon` (8) · `QvantIcon` (7) |

---

## 2. Kerakli ikonkalar — 20 ta kategoriya

### 🧭 1. Navigatsiya (18 ta)
| Ikonka | Qayerda | Holat |
|---|---|---|
| uy / home | header, breadcrumb | ✅ bor |
| menyu (burger) | mobil | ✅ bor |
| yopish (X) | modal, drawer | ✅ bor |
| chevron-left / right / down / up | navigatsiya, ochish | ⚠️ 2 tasi bor |
| orqaga (arrow-left) | sahifa sarlavhasi | ❌ **yo'q** |
| oldinga (arrow-right) | sahifa sarlavhasi | ❌ **yo'q** |
| tashqi havola | tashqi link | ❌ **yo'q** |
| yuqoriga (scroll-to-top) | uzun sahifa | ✅ bor |
| panel yig'ish | sidebar | ❌ **yo'q** |
| ko'proq (…) | kontekst menyu | ❌ **yo'q** |
| panjara / ro'yxat ko'rinishi | masalalar | ❌ **yo'q** |
| filtr panelini ochish | mobil filtr | ❌ **yo'q** |

### 🔘 2. Tugma va amallar (26 ta)
| Ikonka | Qayerda | Holat |
|---|---|---|
| qidiruv | header, jadval | ✅ bor |
| filtr | masalalar, urinishlar | ❌ **yo'q** |
| saralash (asc/desc) | jadval ustuni | ❌ **yo'q** |
| qo'shish (+) | admin, jamoa | ❌ **yo'q** |
| tahrirlash (qalam) | profil, maqola | ❌ **yo'q** |
| o'chirish (savat) | admin, jamoa | ❌ **yo'q** |
| nusxa olish | kod, havola | ✅ bor |
| yuklab olish | sertifikat, kod | ❌ **yo'q** |
| yuklash (upload) | rasm, fayl | ❌ **yo'q** |
| ulashish | natija, sertifikat | ❌ **yo'q** |
| chop etish | sertifikat, natija | ❌ **yo'q** |
| saqlash | forma | ❌ **yo'q** |
| bekor qilish | forma | ❌ **yo'q** |
| qayta urinish (refresh) | xato holati | ❌ **yo'q** |
| ko'z (parolni ko'rsatish) | login, ro'yxat | ❌ **yo'q** |
| ko'z yopiq | login | ❌ **yo'q** |
| pin / mahkamlash | masala, jamoa | ❌ **yo'q** |
| belgi (bookmark) | maqola | ✅ bor (Star) |
| sozlash (sliders) | filtr | ❌ **yo'q** |
| tozalash (X doira) | qidiruv maydoni | ❌ **yo'q** |
| nusxa (clipboard) | kod bloki | ✅ bor |
| tashqi havola | manba | ❌ **yo'q** |
| ovoz / tovush | bildirishnoma | ❌ **yo'q** |
| to'liq ekran | kod muharriri | ❌ **yo'q** |
| formatlash | kod muharriri | ❌ **yo'q** |
| yordam (?) | onboarding | ❌ **yo'q** |

### ✅ 3. Status va holat (16 ta)
| Ikonka | Qayerda | Holat |
|---|---|---|
| tasdiq (check) | hamma joyda | ✅ bor |
| xato (X doira) | forma, verdikt | ❌ **yo'q** |
| ogohlantirish (uchburchak) | forma | ✅ bor |
| ma'lumot (i) | tooltip, hint | ✅ bor |
| qulf (yopiq) | premium, kontest | ❌ **yo'q** |
| qulf ochiq | kontest boshlandi | ❌ **yo'q** |
| ko'z (kuzatilmoqda) | jamoa | ❌ **yo'q** |
| soat | kontest vaqti | ❌ **yo'q** |
| taymer | urinish | ❌ **yo'q** |
| yashil nuqta (onlayn) | foydalanuvchi | ❌ **yo'q** |
| qizil nuqta (oflayn) | foydalanuvchi | ❌ **yo'q** |
| jonli (live) | kontest | ❌ **yo'q** |
| tugagan | kontest | ❌ **yo'q** |
| kutilmoqda | kontest | ❌ **yo'q** |
| tasdiqlangan (verified) | profil | ❌ **yo'q** |
| bloklangan | admin | ❌ **yo'q** |

### ⚖️ 4. Judge verdiktlari (10 ta) — **eng muhim, hozir yo'q**
| Verdikt | Ma'nosi | Ikonka |
|---|---|---|
| **AC** | Accepted | ✅ yashil tasdiq |
| **WA** | Wrong Answer | ❌ qizil X |
| **TLE** | Time Limit | ⏱ soat |
| **MLE** | Memory Limit | 🧠 xotira |
| **RE** | Runtime Error | 💥 portlash |
| **CE** | Compilation Error | 🔧 asbob |
| **PE** | Presentation Error | 📐 format |
| **OLE** | Output Limit | 📤 chiqish |
| **IE** | Internal Error | ⚙️ tizim |
| **Pending** | navbatda | ⏳ soat |

⚠️ **Hozir bular matn yoki rang bilan ko'rsatiladi** — 10 ta ikonka kerak.

### 🏆 5. Reyting va yutuq (20 ta)
| Ikonka | Qayerda | Holat |
|---|---|---|
| olov (streak) | profil, leaderboard | ✅ bor |
| yulduz | sevimli, reyting | ✅ bor |
| kubok | musobaqa | ✅ bor (Contest) |
| medal (1/2/3) | leaderboard | ❌ **yo'q** (3 ta kerak) |
| olmos | yuqori daraja | ❌ **yo'q** |
| toj | chempion | ❌ **yo'q** |
| qalqon | himoya, verified | ❌ **yo'q** |
| nishon (badge) | yutuq | ❌ **yo'q** |
| sertifikat | sertifikatlar | ❌ **yo'q** |
| grafik ustun | statistika | ❌ **yo'q** |
| grafik chiziq | reyting tarixi | ❌ **yo'q** |
| doira diagramma | foiz | ❌ **yo'q** |
| o'sish (trend up) | reyting o'zgarishi | ❌ **yo'q** |
| pasayish (trend down) | reyting o'zgarishi | ❌ **yo'q** |
| nishoncha (rank) | o'rin | ❌ **yo'q** |
| olmos to'plami | daraja | ❌ **yo'q** |
| yulduz to'plami | daraja | ❌ **yo'q** |
| qalqon to'plami | daraja | ❌ **yo'q** |
| bosh barmoq yuqori | ovoz | ❌ **yo'q** |
| bosh barmoq past | ovoz | ❌ **yo'q** |

### 👤 6. Foydalanuvchi va jamoa (16 ta)
| Ikonka | Qayerda | Holat |
|---|---|---|
| foydalanuvchi | profil | ✅ bor |
| foydalanuvchilar (jamoa) | jamoa | ✅ bor |
| avatar placeholder | profil | ✅ bor (Avatar) |
| obuna bo'lish (+) | profil | ❌ **yo'q** |
| obunani bekor qilish (−) | profil | ❌ **yo'q** |
| obunachilar | profil | ❌ **yo'q** |
| bloklash | sozlamalar | ❌ **yo'q** |
| chiqish (logout) | profil menyu | ✅ bor |
| taklif qilish | jamoa | ❌ **yo'q** |
| rol (admin) | jamoa | ❌ **yo'q** |
| rol (o'qituvchi) | sinf | ❌ **yo'q** |
| rol (o'quvchi) | sinf | ❌ **yo'q** |
| ish joyi | profil | ❌ **yo'q** |
| ta'lim | profil | ❌ **yo'q** |
| joylashuv (pin) | profil | ❌ **yo'q** |
| havola (link) | profil | ❌ **yo'q** |

### 🏁 7. Musobaqa (14 ta)
| Ikonka | Qayerda | Holat |
|---|---|---|
| kalendar | kontest sanasi | ✅ bor |
| soat | boshlanish vaqti | ❌ **yo'q** |
| bayroq | finish, davlat | ✅ bor |
| qulf | kontest yopiq | ❌ **yo'q** |
| jonli (live) | davom etmoqda | ❌ **yo'q** |
| ro'yxatdan o'tish | tugma | ❌ **yo'q** |
| jadval (standings) | natijalar | ❌ **yo'q** |
| ACM belgisi | format | ❌ **yo'q** |
| IOI belgisi | format | ❌ **yo'q** |
| reyting (Rated) | belgi | ❌ **yo'q** |
| jamoa (team) | jamoaviy | ✅ bor |
| duel (qilich) | duel | ❌ **yo'q** |
| arena | arena | ✅ bor |
| hackathon | hackathon | ✅ bor |

### 📚 8. Kontent (18 ta)
| Ikonka | Qayerda | Holat |
|---|---|---|
| masala (kitob) | navigatsiya | ✅ bor |
| maqola (hujjat) | blog | ✅ bor |
| kurs | kurslar | ❌ **yo'q** |
| video | video dars | ❌ **yo'q** |
| audio | podkast | ❌ **yo'q** |
| rasm | media | ❌ **yo'q** |
| fayl | biriktirma | ❌ **yo'q** |
| PDF | hujjat | ❌ **yo'q** |
| kod | kod bloki | ❌ **yo'q** |
| terminal | konsol | ❌ **yo'q** |
| yo'l xaritasi | roadmap | ✅ bor |
| algoritm | algoritmlar | ✅ bor |
| test | testlar | ✅ bor |
| quiz | testlar | ✅ bor |
| daraja (level) | o'quv | ❌ **yo'q** |
| qadam (step) | onboarding | ❌ **yo'q** |
| yorliq (tag) | teglar | ❌ **yo'q** |
| toifa (category) | toifalar | ❌ **yo'q** |

### 💻 9. Dasturlash tillari (12 ta)
| Til | Ikonka | Holat |
|---|---|---|
| Python | 🐍 | ❌ **yo'q** |
| C++ | `C++` belgisi | ❌ **yo'q** |
| C | `C` | ❌ **yo'q** |
| Java | ☕ | ❌ **yo'q** |
| JavaScript | `JS` | ❌ **yo'q** |
| TypeScript | `TS` | ❌ **yo'q** |
| Go | `Go` | ❌ **yo'q** |
| Rust | ⚙️ | ❌ **yo'q** |
| Kotlin | `K` | ❌ **yo'q** |
| C# | `C#` | ❌ **yo'q** |
| PHP | 🐘 | ❌ **yo'q** |
| SQL | `SQL` | ❌ **yo'q** |

⚠️ **12 tasi ham yo'q** — hozir matn bilan ko'rsatiladi.

### 🔔 10. Bildirishnoma (10 ta)
| Ikonka | Qayerda | Holat |
|---|---|---|
| qo'ng'iroq | header | ✅ bor |
| qo'ng'iroq (o'qilgan) | header | ❌ **yo'q** |
| xat (envelope) | email | ❌ **yo'q** |
| xabar (chat) | izohlar | ❌ **yo'q** |
| izoh | maqola | ❌ **yo'q** |
| javob | izoh | ❌ **yo'q** |
| belgi (badge) | yangi | ❌ **yo'q** |
| qo'ng'iroq o'chirilgan | sozlamalar | ❌ **yo'q** |
| yangilanish | changelog | ✅ bor (Updates) |
| e'lon (megafon) | e'lonlar | ❌ **yo'q** |

### 🛒 11. Do'kon va valyuta (10 ta)
| Ikonka | Qayerda | Holat |
|---|---|---|
| tanga (qvant) | do'kon | ✅ bor |
| do'kon | navigatsiya | ✅ bor |
| savat | do'kon | ❌ **yo'q** |
| sovg'a | bonus | ❌ **yo'q** |
| chegirma (%) | narx | ❌ **yo'q** |
| yulduzcha (narx) | narx | ❌ **yo'q** |
| sotib olish | tugma | ❌ **yo'q** |
| tarix | xaridlar | ❌ **yo'q** |
| hamyon | balans | ❌ **yo'q** |
| karta | to'lov | ❌ **yo'q** |

### ✏️ 12. Markdown muharriri (14 ta)
| Ikonka | Holat |
|---|---|
| qalin (B) | ❌ **yo'q** |
| kursiv (I) | ❌ **yo'q** |
| sarlavha (H) | ❌ **yo'q** |
| ro'yxat | ❌ **yo'q** |
| raqamli ro'yxat | ❌ **yo'q** |
| havola | ❌ **yo'q** |
| rasm | ❌ **yo'q** |
| kod (inline) | ❌ **yo'q** |
| kod bloki | ❌ **yo'q** |
| iqtibos | ❌ **yo'q** |
| jadval | ❌ **yo'q** |
| chiziq (hr) | ❌ **yo'q** |
| ko'rib chiqish (preview) | ❌ **yo'q** |
| LaTeX / formula | ✅ bor (Formula) |

⚠️ **13 tasi yo'q** — admin panel va blog uchun kerak.

### 🌐 13. Til va davlat (6 ta)
| Ikonka | Holat |
|---|---|
| globus | ✅ bor |
| bayroq (davlat) | ❌ **yo'q** — 10 til uchun 10 ta bayroq |
| til almashtirish | ❌ **yo'q** |
| tarjima | ❌ **yo'q** |
| mintaqa (region) | ❌ **yo'q** |
| vaqt mintaqasi | ❌ **yo'q** |

### 📊 14. Statistika va ma'lumot (12 ta)
| Ikonka | Holat |
|---|---|
| ustunli grafik | ❌ **yo'q** |
| chiziqli grafik | ❌ **yo'q** |
| doira diagramma | ❌ **yo'q** |
| jadval | ❌ **yo'q** |
| filtr (funnel) | ❌ **yo'q** |
| foiz (%) | ❌ **yo'q** |
| kalkulyator | ❌ **yo'q** |
| ma'lumotlar bazasi | ❌ **yo'q** |
| server | ❌ **yo'q** |
| tezlik (performance) | ❌ **yo'q** |
| yuklanish | ❌ **yo'q** |
| xotira | ❌ **yo'q** |

### 🔧 15. Tizim va sozlama (12 ta)
| Ikonka | Holat |
|---|---|
| tishli (sozlama) | ✅ bor |
| palitra | ✅ bor |
| quyosh (light) | ✅ bor |
| oy (dark) | ✅ bor |
| monitor (system) | ❌ **yo'q** |
| qalqon (xavfsizlik) | ❌ **yo'q** |
| kalit (parol) | ❌ **yo'q** |
| qurilma (device) | ❌ **yo'q** |
| sessiyalar | ❌ **yo'q** |
| jurnal (log) | ❌ **yo'q** |
| zaxira (backup) | ❌ **yo'q** |
| API kalit | ❌ **yo'q** |

### 📱 16. Mobil va qurilma (8 ta)
| Ikonka | Holat |
|---|---|
| telefon | ❌ **yo'q** |
| planshet | ❌ **yo'q** |
| noutbuk | ❌ **yo'q** |
| ish stoli | ❌ **yo'q** |
| brauzer | ❌ **yo'q** |
| QR kod | ❌ **yo'q** |
| ilova yuklab olish | ❌ **yo'q** |
| sensor (touch) | ❌ **yo'q** |

### 🚫 17. Bo'sh holatlar (8 ta) — katta ikonkalar
| Holat | Ikonka |
|---|---|
| qidiruv natijasi yo'q | 🔍 katta |
| urinishlar yo'q | 📋 katta |
| bildirishnoma yo'q | 🔔 katta |
| jamoa yo'q | 👥 katta |
| xabar yo'q | 💬 katta |
| fayl yo'q | 📁 katta |
| xatolik 404 | 🧭 katta |
| xatolik 500 | ⚙️ katta |

### ⚠️ 18. Xatolik holatlari (6 ta)
| Holat | Ikonka |
|---|---|
| tarmoq xatosi | 📡 |
| server xatosi | 🔥 |
| ruxsat yo'q | 🚫 |
| topilmadi | 🔍 |
| muddat tugadi | ⏰ |
| noto'g'ri ma'lumot | ⚠️ |

### 🔗 19. Ijtimoiy tarmoqlar (10 ta)
Telegram · GitHub · Google · Instagram · YouTube · LinkedIn · X · Facebook · Discord · Website

### 📎 20. Fayl va media (12 ta)
| Ikonka | Holat |
|---|---|
| biriktirish (clip) | ❌ **yo'q** |
| papka | ❌ **yo'q** |
| yuklab olish | ❌ **yo'q** |
| o'ynatish | ❌ **yo'q** |
| to'xtatish | ❌ **yo'q** |
| oldinga/ orqaga (media) | ❌ **yo'q** |
| ovoz balandligi | ❌ **yo'q** |
| to'liq ekran | ❌ **yo'q** |
| kattalashtirish | ❌ **yo'q** |
| kichraytirish | ❌ **yo'q** |
| aylantirish | ❌ **yo'q** |
| kesish (crop) | ❌ **yo'q** |

---

## 3. Yakuniy hisob

| Kategoriya | Kerak | Bor | Yetishmaydi |
|---|---|---|---|
| 1. Navigatsiya | 18 | 6 | 12 |
| 2. Tugma va amallar | 26 | 4 | 22 |
| 3. Status va holat | 16 | 4 | 12 |
| 4. **Judge verdiktlari** | 10 | 0 | **10** |
| 5. Reyting va yutuq | 20 | 4 | 16 |
| 6. Foydalanuvchi va jamoa | 16 | 5 | 11 |
| 7. Musobaqa | 14 | 6 | 8 |
| 8. Kontent | 18 | 8 | 10 |
| 9. **Dasturlash tillari** | 12 | 0 | **12** |
| 10. Bildirishnoma | 10 | 2 | 8 |
| 11. Do'kon va valyuta | 10 | 2 | 8 |
| 12. **Markdown muharriri** | 14 | 1 | **13** |
| 13. Til va davlat | 6 | 1 | 5 |
| 14. Statistika | 12 | 0 | 12 |
| 15. Tizim va sozlama | 12 | 4 | 8 |
| 16. Mobil va qurilma | 8 | 0 | 8 |
| 17. Bo'sh holatlar | 8 | 0 | 8 |
| 18. Xatolik holatlari | 6 | 1 | 5 |
| 19. Ijtimoiy tarmoqlar | 10 | 0 | 10 |
| 20. Fayl va media | 12 | 0 | 12 |
| **JAMI** | **250** | **48** | **202** |

⚠️ **Diqqat:** 48 — takrorlanuvchilarni hisobga olgan (masalan `check` bir necha
kategoriyada). Unikal kerak: **~220 ta**.

---

## 4. To'plam tanlashga ta'siri

**220 ta ikonka** — bu endi boshqa savol:

| To'plam | Ikonka | 220 tasi bormi? |
|---|---|---|
| **Phosphor** | 9 072 | ✅ **ortig'i bilan** (duotone ham) |
| **Tabler** | 6 184 | ✅ to'liq |
| **Lucide** | 1 909 | ⚠️ **dasturlash tillari yo'q** (brands) |
| **Heroicons** | 300+ | ❌ **yetmaydi** |
| **IconPark** | 2 658 | ✅ to'liq |
| **Simple Icons** | 3 460 | ⚠️ faqat brendlar (ijtimoiy, tillar) |

### Muhim topilma: **dasturlash tillari** alohida muammo
Python, C++, Java logotiplari — **brand ikonkalar**. Ularni beradigan to'plamlar:
- **Simple Icons** (3 460, CC0) — `python`, `cplusplus`, `java`, `javascript` ✅
- **Iconify `logos`** — texnologiya logotiplari ✅
- Phosphor/Tabler/Lucide — **yo'q** (ular umumiy ikonkalar)

**Ya'ni ikkita to'plam kerak:**
1. **Asosiy** (Phosphor) — 220 ta umumiy ikonka
2. **Brend** (Simple Icons, CC0) — tillar, ijtimoiy tarmoqlar, texnologiyalar

---

## 5. Nomlash — 220 ta kalit

Semantik kalit tizimi (1-bosqichda tanlandi) shu hajmda **majburiy**:

```ts
// icons/keys.ts — 220 ta mavhum kalit
export const ICON = {
  // navigatsiya
  home:        { phosphor: "house",        tabler: "home",      lucide: "house" },
  back:        { phosphor: "arrow-left",   tabler: "arrow-left", lucide: "arrow-left" },
  // verdiktlar
  verdictAC:   { phosphor: "check-circle", tabler: "circle-check", lucide: "check-circle" },
  verdictWA:   { phosphor: "x-circle",     tabler: "circle-x",   lucide: "x-circle" },
  verdictTLE:  { phosphor: "timer",        tabler: "clock",      lucide: "timer" },
  // tillar (brand to'plamdan)
  langPython:  { simpleIcons: "python" },
  langCpp:     { simpleIcons: "cplusplus" },
  // ...
};
```

⚠️ **220 × 3 to'plam = 660 nom** — bu **mexanik ish**, skript bilan
avtomatlashtirish kerak (nom o'xshashligi bo'yicha taklif + qo'lda tasdiq).
