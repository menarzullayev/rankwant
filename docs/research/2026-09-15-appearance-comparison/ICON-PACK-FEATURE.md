# Funksiya taklifi: foydalanuvchi o'zi uchun ikonka to'plamini tanlaydi

**Sana:** 2026-09-15 · **Asos:** RankWant'ning amaldagi Appearance moduli (39 sozlama,
12 uslub) + 15 ta kutubxona tadqiqoti + 5 ta raqobat sayti tahlili.

---

## 0. Mening fikrim — avval xulosa

**G'oya yaxshi, lekin aynan siz aytgandek "har bir foydalanuvchiga o'z to'plami"
shaklida emas.** Sabab quyida. To'g'ri shakl:

> **Uslub** (outline / solid / duotone) — asosiy, hamma tushunadigan tanlov.
> **To'plam** (Lucide / Phosphor / Tabler) — ikkilamchi, "Kengaytirilgan" ostida.

Ya'ni foydalanuvchi **avval "qanday ko'rinishni"**, keyin **"qaysi brendni"** tanlaydi.
Aks holda 200+ to'plam orasida odam qotib qoladi va foyda emas, charchoq oladi.

⚠️ **Muhim kontekst:** o'lchandi — **beshta raqobat saytining hech birida**
ikonka tanlovi yo'q (LeetCode, KEP.uz, RoboContest, CodeChef). Ya'ni bu
**haqiqiy differensiatsiya imkoniyati**, "hamma qilgan narsa" emas.

---

## 1. Asosiy maqsad

### 1.1. Brend farqlanishi (asosiy sabab)
Bugun 41 ta ikonka **qo'lda yozilgan** (`icons/index.tsx`) va bitta uslubda qotib
qolgan. Uslub almashtirilganda (Neo-brutalizm, Glassmorphism) ikonkalar
o'zgarmaydi — natijada **uslub va ikonka bir-biriga mos kelmaydi**.

**Funksiya shu uzilishni yopadi:** har uslub o'ziga mos ikonka uslubini olib keladi.

### 1.2. Foydalanuvchi qulayligi
- **Outline** — zich interfeys, ko'p ikonka yonma-yon (jadval, ro'yxat)
- **Solid** — katta tugmalar, mobil, kam ko'ruvchilar uchun aniqroq
- **Duotone** — brend hissi, marketing sahifalari

Bu **did masalasi emas, ehtiyoj**. Kimdir chiziqli ikonkani "yengil", kimdir
"ko'rinmas" deb biladi.

### 1.3. Korporativ moslashuv
Tashkilot o'z brend ikonkasini qo'yishi mumkin (hozir `siteAppearance` — jamoa
standarti allaqachon bor, D37). Ikonka to'plami unga tabiiy qo'shimcha.

---

## 2. Taqdim etish usuli

### 2.1. Joylashuv — mavjud Customizer ichida
Yangi panel **kerak emas**. `Customizer` da allaqachon 13 ta bo'lim bor
(Shablonlar · Mavzu · Uslub · Rang · Shrift · Sarlavha shrifti · O'lcham ·
Zichlik · Navigatsiya · Panel shakli · Kenglik · Karta · Fon naqshi).

Yangi bo'lim: **"Ikonkalar"** — Shrift bo'limi yonida (ikkalasi ham
"tipografik/vizual til" guruhi).

### 2.2. Ikki qavatli tanlov

**Qavat 1 — Uslub (asosiy, doim ko'rinadi):**
```
Ikonka uslubi
[ Chiziqli ]  [ To'ldirilgan ]  [ Ikki qatlamli ]
   outline        solid           duotone
```
Har tugma yonida **3 ta namuna ikonka** — odam bosmasdan ko'radi.

**Qavat 2 — To'plam (ikkilamchi, "Kengaytirilgan" ostida):**
```
To'plam                    ▾
[ Lucide ]  [ Phosphor ]  [ Tabler ]
  yengil      moslashuvchan  izchil
```
Faqat **3 ta** — 200+ emas (sabab 4.4 da).

### 2.3. Ko'rib tanlash (eng muhim qism)
Har variant ostida **jonli namuna** — 8-12 ta vakillik ikonka:
`Masalalar · Musobaqa · Reyting · Maqolalar · Qidiruv · Sozlamalar`

Odam **o'z sahifasidagi** ikonkalarni ko'rib tanlaydi, mavhum nomdan emas.

### 2.4. Saqlash va ulashish
Mavjud tizim **o'zgarishsiz** ishlaydi:
- `localStorage` (`rw:appearance`) — qurilmada
- Hisob (`ui_prefs` + `PrefsSync`) — qurilmalararo
- Havola (`?icon=phosphor-solid`) — ulashish
- JSON fayl — zaxira
- Shaxsiy shablonlar — ikonka tanlovi ham saqlanadi

**Ya'ni yangi infratuzilma kerak emas** — mavjud `AppearancePrefs` ga 2 ta maydon
qo'shiladi: `iconPack` va `iconStyle`.

---

## 3. Tanlov qanday amalga oshiriladi (texnik)

### 3.1. Eng katta muammo: nomlar MOS KELMAYDI

Bu **asosiy texnik qiyinchilik**. O'lchandi:

| Tushuncha | Lucide | Phosphor | Heroicons |
|---|---|---|---|
| Uy | `house` | `house` | `home` |
| Reyting | `bar-chart-3` | `chart-bar` | `chart-bar` |
| Maqola | `newspaper` | `article` | `document-text` |
| Yopish | `x` | `x` | `x-mark` |
| Jamoa | `users` | `users-three` | `users` |

Ya'ni **mapping jadvali shart** — bizning har bir ikonka uchun har to'plamdagi nom.

**Yechim:**
```ts
// icons/packs.ts
export const ICON_MAP = {
  problems: { lucide: "book",    phosphor: "books",       tabler: "book" },
  contest:  { lucide: "trophy",  phosphor: "trophy",      tabler: "trophy" },
  rating:   { lucide: "bar-chart-3", phosphor: "chart-bar", tabler: "chart-bar" },
  // ...
};
```
41 ta ikonka × 3 to'plam = **123 ta yozuv**. Bir marta yoziladi, keyin
`tools/check_icons.py` bilan tekshiriladi (nom mavjudmi).

⚠️ **Agar ikonka biror to'plamda bo'lmasa** — zaxira (fallback) kerak:
eng yaqin to'plamdan olinadi va **jimgina** ishlamaydi (ogohlantirish logda).

### 3.2. Texnologiya tanlovi

| Variant | Yaxshi | Yomon |
|---|---|---|
| **Iconify paketlari** (`@iconify-json/*`) | bitta API, 200+ to'plam | har to'plam alohida o'rnatiladi |
| **Alohida React paketlar** | tayyor komponentlar | 3 ta dependency, har biri o'z API |
| **SVG'larni o'zimiz saqlash** | to'liq nazorat, offline | 41 × 3 = 123 SVG qo'lda |

**Tavsiya:** `@iconify-json/*` + kichik o'ram (wrapper). Sabab: biz allaqachon
Iconify bilan ishladik (dashboard'da), va u **bir xil JSON formatda** beradi —
ya'ni `Icon` komponenti bitta kod bilan uch to'plamni o'qiy oladi.

### 3.3. Komponent

```tsx
// icons/Icon.tsx
export function Icon({ name, className }: { name: IconName; className?: string }) {
  const { iconPack, iconStyle } = useCustomizer().appearance;
  const pack = iconPack ?? "lucide";
  const style = iconStyle ?? "outline";
  const key = ICON_MAP[name]?.[pack];
  if (!key) return <FallbackIcon name={name} className={className} />;
  const data = PACKS[pack]?.icons[key];       // paket allaqachon yuklangan
  if (!data) return <FallbackIcon name={name} className={className} />;
  return (
    <svg viewBox={`0 0 ${PACKS[pack].width} ${PACKS[pack].height}`}
         className={className} aria-hidden="true"
         dangerouslySetInnerHTML={{ __html: data.body }} />
  );
}
```

**Muhim:** `aria-hidden="true"` **shart** — ikonka bezak, matn yonida turadi.
Faqat ikonkali tugmada `aria-label` kerak (hozir ham shunday).

### 3.4. Yuklash strategiyasi (bundle hajmi)

**Muammo:** Phosphor 9 161 ikonka = **4.5 MB**. Hammasini yuklash mumkin emas.

**Yechim — faqat kerakli 41 ta:**
```ts
// build vaqtida: kerakli ikonkalarnigina ajratib olamiz
import phIcons from "@iconify-json/ph/icons.json";
const NEEDED = Object.values(ICON_MAP).map((m) => m.phosphor);
const phSubset = Object.fromEntries(NEEDED.map((k) => [k, phIcons.icons[k]]));
```
Natija: 41 ta ikonka × 3 to'plam ≈ **30-40 KB** (gzip) — bu **qabul qilinadi**.

⚠️ `next.config.ts` da tree-shaking tekshirilishi kerak.

---

## 4. Afzalliklari

### 4.1. Differensiatsiya (eng katta)
**O'lchandi:** LeetCode, KEP.uz, RoboContest, CodeChef — **hech birida** ikonka
tanlovi yo'q. Bizda **Appearance moduli hamda 12 uslub** bor — ikonka unga
tabiiy davomi. Raqobatchilar uslubni umuman taklif qilmaydi.

### 4.2. Uslub ↔ ikonka uyg'unligi
Hozirgi **asosiy nuqson**: Neo-brutalizm uslubi qalin chegara va solid
shakllar bilan ishlaydi, ikonkalar esa **nozik chiziqli**. Funksiya shu
nomuvofiqlikni yo'q qiladi.

### 4.3. Texnik qarzni yopadi
41 ta qo'lda yozilgan ikonka — **texnik qarz**:
- yangi ikonka kerak bo'lganda **chizish** kerak
- uslub almashganda **o'zgarmaydi**
- chiziq qalinligi qo'lda sozlangan (1.7) — izchillik tasodifiy

To'plamga o'tish = **1500+ ikonka tayyor**, izchil chizilgan.

### 4.4. Accessibility
- **Solid** ikonkalar kam ko'ruvchilar uchun aniqroq (to'ldirilgan shakl)
- **Outline** — disleksiya uchun (kam vizual shovqin)
- **Duotone** — rang ajratolmaslik uchun yaxshiroq (ikki qatlam)

Bu `A11yPrefs` bilan **birga ishlaydi** (hozir rang ajratish, harakat, katta
maydon, kuchli fokus bor).

---

## 5. ⚠️ E'tiborga olish kerak bo'lgan jihatlar

### 5.1. Tanlov charchog'i (eng katta xavf)
**200+ to'plam taklif qilish — xato.** Foydalanuvchi qotib qoladi, tanlamaydi.
**Yechim:** 3 ta to'plam, har biri **aniq xarakter bilan**:
- Lucide — "Yengil va neytral"
- Phosphor — "Moslashuvchan (6 og'irlik)"
- Tabler — "Izchil va to'liq"

### 5.2. Nom mapping — doimiy xizmat
Har yangi ikonka qo'shilganda **3 to'plamda** qidirish kerak. Bu **bir martalik
ish emas** — jarayon. `tools/check_icons.py` avtomatik tekshiruvi shart.

### 5.3. Izchillik buzilishi
Agar foydalanuvchi **aralash** ishlatsa (bir joyda Lucide, boshqasida Phosphor) —
chiziq qalinligi va burchaklar farq qiladi. **Yechim:** butun sahifa uchun
**bitta** tanlov, alohida ikonka uchun emas.

### 5.4. Kontrast va o'lcham
Har to'plamning chiziq qalinligi boshqa:
- Lucide — 2 px
- Phosphor — 1.5-2 px (og'irlikka qarab)
- Tabler — 2 px

**Outline** rejimida 20 px dan kichik o'lchamda ba'zi ikonkalar **yo'qolib
ketadi**. Har to'plamni **3 o'lchamda** (20/24/40) tekshirish kerak.

`check_contrast.py` ikonkalarni ham qamrab olishi shart.

### 5.5. Bundle hajmi
- 3 to'plam × 41 ikonka ≈ 30-40 KB gzip — **maqbul**
- Lekin noto'g'ri import butun paketni tortadi (Phosphor = 4.5 MB)
- **Tekshirish:** `npm run build` da hajmni o'lchash, `next.config.ts` da
  tree-shaking tasdiqlash

### 5.6. SSR va chaqnash (FOUC)
Ikonka tanlovi `localStorage` da — SSR paytida noma'lum. Ya'ni sahifa
**noto'g'ri to'plam** bilan chizilib, keyin almashadi.

**Yechim:** `layout.tsx` dagi mavjud SSR script'ga `data-icon-pack` qo'shish
(uslub, o'lcham, zichlik bilan bir xil naqsh — **allaqachon bor**).

### 5.7. Test yuki
3 to'plam × 3 uslub = **9 kombinatsiya**. Har biri:
- 41 ikonkaning mavjudligi
- 3 o'lchamda ko'rinishi
- Kontrast (AA)
- SSR chaqnashi

`tools/check_icons.py` + Playwright sinovi kerak.

### 5.8. Foydalanuvchi kutgan narsa
"O'z ikonkamni yuklayman" degan kutish bo'lishi mumkin. **Chegara ochiq
aytilishi kerak:** bu funksiya **tayyor to'plamlardan tanlash**, o'z SVG'ini
yuklash emas. (Ikkinchisi — moderatsiya, xavfsizlik, saqlash talab qiladi;
alohida katta ish.)

---

## 6. Bosqichma-bosqich reja (agar qaror qilinsa)

| Bosqich | Ish | Natija |
|---|---|---|
| **1** | `ICON_MAP` — 41 × 3 nomni yozish + `check_icons.py` | poydevor |
| **2** | `Icon` komponenti + subset import (faqat 41 ta) | kod ishlaydi |
| **3** | Customizer bo'limi (uslub + to'plam + namuna) | UI tayyor |
| **4** | `apply.ts` + SSR script + `share.ts` (4 joy) | saqlash/ulashish |
| **5** | 10 tilga kalitlar | i18n |
| **6** | Test: 9 kombinatsiya × 3 o'lcham + kontrast | tasdiq |
| **7** | Deploy | jonli |

**Baho:** bosqich 1 eng ko'p vaqt oladi (mexanik ish), qolgani mavjud
infratuzilmaga tayanadi.

---

## 7. Xulosa — nima qilishni tavsiya qilaman

✅ **Qilish kerak:**
1. **Uslub tanlovi** (outline / solid / duotone) — hamma tushunadi, darhol foyda
2. **3 ta to'plam** — Lucide · Phosphor · Tabler (200+ emas)
3. **Jonli namuna** — foydalanuvchi o'z sahifasidagi ikonkalarni ko'rib tanlaydi
4. **Mavjud infratuzilma** — yangi tizim qurmaslik, `AppearancePrefs` ga 2 maydon

⚠️ **Ehtiyot bo'lish kerak:**
1. Nom mapping — doimiy xizmat, avtomatik tekshiruvsiz qoldirmaslik
2. Bundle hajmi — subset import **shart**, aks holda 4.5 MB
3. SSR chaqnashi — mavjud naqshni takrorlash
4. Kontrast — har to'plamni 3 o'lchamda sinash

❌ **Qilmaslik kerak:**
1. 200+ to'plam taklif qilish — tanlov charchog'i
2. Alohida ikonka uchun alohida to'plam — izchillik buziladi
3. "O'z SVG'ini yuklash" — bu butunlay boshqa funksiya (moderatsiya, xavfsizlik)
