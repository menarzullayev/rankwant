# Appearance bo'limi: RankWant vs kep.uz — qiyosiy tahlil

**Sana:** 2026-09-15 · **Usul:** Playwright (headless Chromium 1440×1000), har bir sozlama alohida bosildi;
bosishdan oldin/keyin `<html>` atributlari, `--rw-*` CSS o'zgaruvchilari, `body` hisoblangan stillari va
barcha elementlarning CSS-histogrami solishtirildi. Faqat o'lchangan farqlar yozilgan.

---

## 1. Umumiy qiyos

| | **RankWant** (`rankwant.uz`) | **kep.uz** |
|---|---|---|
| Panel nomi | «Ko'rinish sozlagichi» | «Customize» |
| Joylashuvi | Suzuvchi tugma (o'ng chetda) · `Ctrl+.` · Sozlamalar sahifasi | Vertikal tugma (o'ng chetda) |
| Bo'limlar soni | **2 ta tab** (Ko'rinish · Qulaylik), jami 11 ta bo'lim | 1 ta ro'yxat, 12 ta bo'lim |
| Ishlamaydigan sozlama | **0 ta** | **4 ta** (Nav Color · Background Pattern · Card Style · Vision Mode) |
| Saqlash | `localStorage` + **hisob** (qurilmalararo) | faqat `localStorage` |
| Bekor qilish | **Undo** (1 qadam) + tasdiqli Reset | faqat Reset |
| Ulashish | **Havola** (`?style=flat`) | yo'q |

---

## 2. Parametr-ma-parametr

| Parametr | RankWant | kep.uz | Kimda yaxshi |
|---|---|---|---|
| **Tayyor shablonlar** | 8 ta: Klassik · Kun · Tun · Konsol · Jurnal · Fokus · Yumshoq · Aurora — har biri **uslub + mavzu + shrift + zichlik** ni bir bosishda qo'llaydi | 8 ta: Default · Luxury · Retro · Arctic · Nature · Ember · Dracula · Midnight — faqat **rang palitrasi** | **RankWant** (shablon ko'proq narsani qamrab oladi) |
| **Uslub (dizayn tili)** | **12 ta**: Dashboard · Shveycha · Flat · Material · Editorial · Neo-brutalizm · Terminal · Glassmorphism · Neumorphism · Claymorphism · Aurora · Skeuomorfizm | yo'q | **RankWant** |
| **Mavzu (light/dark)** | 3 ta, **faqat ikki muhitli uslubda**; bir muhitli uslubda o'rniga sabab yoziladi: *«Bu uslub faqat bitta muhitga chizilgan»* | 3 ta, har doim | **kep.uz** (har doim mavjud), lekin RankWant sababni tushuntiradi |
| **Asosiy rang** | 14 ta tus namunasi + **2 ta slider** (tus 0–359, to'yinganlik 0–100) + jonli kontrast ko'rsatkichi + «Uslubning o'z rangi» | 9 ta qat'iy rang kvadrati | **RankWant** (erkin tanlov + kontrast nazorati) |
| **Shrift** | 5 ta: Uslubning o'zi · Inter · Plus Jakarta · Roboto · DM Sans | 4 ta: Plus Jakarta Sans · Inter · Roboto · DM Sans | **RankWant** («uslubning o'zi» — uslubga mos shrift) |
| **Shrift o'lchami** | 4 ta: 90 / 100 / 110 / 120 % — **shrift bilan birga padding va radius ham moslashadi** (o'lchandi: 8px→7.2px) | Slider 12–20 px | **RankWant** (proporsional), kep.uz (erkinroq diapazon) |
| **Zichlik** | 3 ta: Zich · Qulay · Keng (`data-density`) | yo'q | **RankWant** |
| **Navigatsiya** | yo'q | Sidenav / Topnav + Topnav Shape (Slim · Stacked) — **ishlaydi** | **kep.uz** |
| **Nav rangi** | yo'q | Default / Vibrant — **ishlamaydi** | teng (kep.uz da bor, lekin buzilgan) |
| **Fon naqshi** | yo'q | None / Grid / Dots / Diagonal / Mesh — **faqat atribut, vizual yo'q** | — |
| **Karta ko'rinishi** | yo'q | Card Style (4) — **ishlamaydi**; Card Background (4) — **ishlaydi** | **kep.uz** qisman |
| **Rang ajratish (daltonizm)** | 3 ta: Oddiy · Qizil-yashil · Ko'k-sariq — **holat ranglari haqiqatan almashadi** (`--rw-ok-ink`, `--rw-warn-ink`, `--rw-bad-ink`) | 5 ta: Normal · Protanopia · Deuteranopia · Tritanopia · Achromatopsia — **hech qanday filter qo'llanilmaydi** | **RankWant** aniq |
| **Harakat (motion)** | 2 ta: Tizim · Kamaytirish (`data-motion`) | yo'q | **RankWant** |
| **Katta bosish maydonlari** | bor (`data-targets=big`) | yo'q | **RankWant** |
| **Kuchli fokus halqasi** | bor (`data-focus=strong`) | yo'q | **RankWant** |
| **Tovush** | bor — «Tovush» belgisi + **«Sinab ko'rish»** tugmasi (Settings sahifasida) | yo'q | **RankWant** |
| **Effekt (animatsiya)** | 3 ta: none / fade / circle (Settings sahifasida) | yo'q | **RankWant** |
| **Til** | 10 ta locale (Settings sahifasida) | yo'q (bu panelda) | **RankWant** |
| **Shaxsiy shablon** | bor — nom bilan saqlash (≤24 belgi), **mehmon 2 / kirgan 5** | yo'q | **RankWant** |
| **Ulashish havolasi** | bor — `https://rankwant.uz/?style=flat` | yo'q | **RankWant** |
| **Undo** | bor (1 qadam, «Bekor qilish») | yo'q | **RankWant** |
| **Reset** | tasdiq bilan: «Ha, hammasini tiklash» / «Yopish» | oddiy tugma | **RankWant** (tasodifiy bosishdan himoya) |
| **Klaviatura** | `Ctrl+.` ochish · `Esc` yopish | yo'q | **RankWant** |

---

## 3. Ishlash sifati (o'lchandi)

| Ko'rsatkich | RankWant | kep.uz |
|---|---|---|
| Sinovdan o'tgan sozlama | 39 ta | 43 ta |
| **Vizual o'zgarish bermagan** | **0 ta** | **4 ta** (9 %) |
| Eng katta ta'sir (o'zgargan element) | 7 330 (Aurora shabloni) | 2 204 (DM Sans) |
| O'rtacha ta'sir | ~4 500 (shablon/uslub) | ~1 100 |
| Kontrast nazorati | **bor** — AA dan o'tmasa rang saqlanmaydi | yo'q |

**kep.uz da ishlamaydigan 4 ta sozlama:**

| Sozlama | Belgisi | Haqiqat |
|---|---|---|
| Nav Color (Vibrant) | tanlov saqlanadi | menyu rangi ham, fon rasmi ham o'zgarmaydi |
| Background Pattern (5 ta) | `data-kep-bg-pattern` o'rnatiladi | fon naqshi hech qayerda qo'llanilmaydi |
| Card Style (Outline/Corners/Glow) | `data-kep-card-style` o'rnatiladi | karta ramkasi, radiusi, soyasi o'zgarmaydi |
| Vision Mode (4 ta filtr) | `data-vision` o'rnatiladi | hech qanday CSS/SVG filter qo'shilmaydi |

---

## 4. RankWant'ning kuchli tomonlari

1. **Hech narsa buzilgan emas** — 39 ta sozlamaning barchasi o'lchangan vizual o'zgarish berdi.
2. **Kontrast nazorati (D11).** Rang tanlashda jonli ko'rsatkich (`4.52:1 ✓`) — AA dan o'tmagan kombinatsiya **saqlanmaydi**. kep.uz da bunday himoya yo'q.
3. **Uslub → rang bog'liqligi (D10).** Uslub o'zgarganda accent ham moslashadi: `#7c3aed` → `#7b2ff7`. Qo'lda accent o'rnatilsa «Uslubning o'z rangi» tugmasi bilan qaytarish mumkin.
4. **Bir muhitli uslublar tushuntiriladi.** `clay`, `terminal`, `aurora` da mavzu tanlovi o'rniga sabab yoziladi — foydalanuvchi «nima uchun tugma yo'q» deb hayron qolmaydi.
5. **Qulaylik alohida tab.** Rang ajratish haqiqatan ishlaydi (holat ranglari almashadi), harakatni kamaytirish, katta bosish maydonlari, kuchli fokus.
6. **Ulashish va shaxsiy shablonlar.** `?style=flat` havolasi va nom bilan saqlash (chegara: mehmon 2 / kirgan 5 — *«Shablon chegarasiga yetdingiz — 2»* o'lchandi).
7. **Undo + tasdiqli Reset.** Bitta xato rangni qaytarish uchun butun ko'rinish yo'qolmaydi.
8. **Klaviatura** (`Ctrl+.`) va **tovushni sinab ko'rish** tugmasi.

## 5. kep.uz ning kuchli tomonlari

1. **Navigatsiya sozlamalari** — Sidenav/Topnav va Topnav Shape (Slim 83→39 px, Stacked 83→103 px) haqiqatan layout'ni o'zgartiradi. **RankWant'da bunday sozlama umuman yo'q.**
2. **Karta va fon naqshi** g'oyasi — RankWant'da mos keladigan parametr yo'q (garchi kep.uz da ularning yarmi ishlamasa ham).
3. **Erkin shrift o'lchami** (slider 12–20 px) — RankWant'da faqat 4 ta qat'iy qiymat (90–120 %).
4. **Mavzu har doim mavjud** — uslubdan qat'i nazar.

## 6. Tavsiyalar (RankWant uchun)

| # | Taklif | Asos |
|---|---|---|
| 1 | **Navigatsiya sozlamasi qo'shish** (Sidenav/Topnav) | kep.uz da bor va ishlaydi; RankWant'da umuman yo'q — eng katta bo'shliq |
| 2 | **Erkin rang: hue/sat slaiderdan tashqari HEX kiritish** | Hozir 14 ta tus + 2 slider; aniq rang kerak bo'lsa imkon yo'q |
| 3 | **Undo tarixini 1 qadamdan ko'proqqa oshirish** | Hozir faqat oxirgi o'zgarish qaytadi |
| 4 | **Fon naqshi / karta uslubi** | kep.uz g'oyasi yaxshi, faqat ishlamaydi — to'g'ri qilib qo'shish mumkin |
| 5 | **Shrift o'lchamiga erkin diapazon** (masalan 80–140 %) | kep.uz da slider bor |

---

## 7. Xulosa

**RankWant ancha oldinda.** Uning Appearance bo'limi **ko'proq parametr** (11 ta bo'lim, 39 ta sozlama),
**to'liq ishlaydi** (0 ta buzilgan), va **sifat himoyasi** bor (kontrast nazorati, undo, tasdiqli reset,
qulaylik tab'i). kep.uz esa **g'oya jihatdan qiziqarli** (navigatsiya, karta, fon naqshi), lekin
**12 ta bo'limdan 4 tasi ishlamaydi** va hech qanday himoya mexanizmi yo'q.

**Eng muhim farq:** RankWant'da *«ishlamaydigan»* sozlama yo'q — har bir parametr o'lchangan
o'zgarish beradi. kep.uz da esa atribut o'rnatilib, vizual effekt berilmaydigan to'rtta sozlama bor;
foydalanuvchi o'zgartirdim deb o'ylaydi, lekin sahifa o'zgarmaydi.
