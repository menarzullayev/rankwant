# Updates moduli — 20 bosqichli qaror sessiyasi

Sana: 2026-09-13 · Holat: **1-savol berildi**

## Sessiyaning maqsadi

Updates moduli bo'yicha **implementatsiyaga tayyor qaror** qabul qilish.
Yakunda qo'lda bo'lishi kerak:

1. Modulning maqsadi va o'quvchisi (aniq)
2. Tarqatish modeli (qayerda, qanday ko'rinadi)
3. Kontent manbasi — **GitHub'dan olinadimi yoki yo'qmi**
4. Bosqichma-bosqich chiqarish siyosati (faza, o'lchov, rollback)
5. Ma'lumot modeli va implementatsiya tartibi

## Ikki yangi talab (sessiya davomida hal qilinadi)

| # | Talab | Qaysi savollarda |
|---|---|---|
| **T1** | **Barcha o'zgarishlar shu paytdan boshlab bosqichma-bosqich chiqariladi** — nafaqat Updates moduli, butun mahsulot | 17–20 |
| **T2** | O'zgarishlar **GitHub'dan olinadimi**? (commit/PR/release → foydalanuvchi matni) | 13–16 |

## 20 savol — reja

### Blok 1 — Maqsad va o'quvchi (1–4)

| # | Savol | Nima hal qiladi |
|---|---|---|
| 1 | Modulning **asosiy maqsadi** nima? | Butun dizaynni belgilaydi |
| 2 | Kim **asosiy o'quvchi**? | Til, ton, joylashuv |
| 3 | Muvaffaqiyat **qanday o'lchanadi**? | Faza qarorlari uchun asos |
| 4 | Hozir foydalanuvchi yangilikni **qayerdan biladi**? | Boshlang'ich nuqta |

### Blok 2 — Tarqatish (5–8)

| # | Savol | Nima hal qiladi |
|---|---|---|
| 5 | Yangilik **qayerda ko'rinadi**? | E variantining shakli |
| 6 | **Nechta joyda** bir vaqtda? | Bezovta qilish chegarasi |
| 7 | **O'qilmagan holat** saqlansinmi? | `UserUpdateRead` kerakmi |
| 8 | **Mehmonga** ko'rsatilsinmi? | SEO va birinchi taassurot |

### Blok 3 — Kontent (9–12)

| # | Savol | Nima hal qiladi |
|---|---|---|
| 9 | Kontentni **kim yozadi**? | Ish yuki |
| 10 | Har o'zgarish alohida yoki **guruhlangan**? | Yozuv hajmi |
| 11 | **Tur belgilari** qanday? | Ranglar va filtr |
| 12 | **Rasm** kerakmi? | Media saqlash |

### Blok 4 — GitHub integratsiyasi (13–16) ← **T2**

| # | Savol | Nima hal qiladi |
|---|---|---|
| 13 | O'zgarishlar GitHub'dan **olinadimi**? | Asosiy arxitektura qarori |
| 14 | Qaysi **manbadan** (commit/PR/release/issue)? | Integratsiya nuqtasi |
| 15 | **Kim tasdiqlaydi**? | Nashr oqimi |
| 16 | Texnik yozuv **foydalanuvchi tiliga** qanday o'giriladi? | Tarjima/AI/qo'lda |

### Blok 5 — Reliz siyosati va fazalar (17–20) ← **T1**

| # | Savol | Nima hal qiladi |
|---|---|---|
| 17 | Bosqichma-bosqich chiqarish **mexanizmi**? | Feature flag / foiz / modul |
| 18 | **Nechta faza** va qanday tartibda? | Yo'l xaritasi |
| 19 | Har fazadan keyin **nima o'lchanadi**? | Davom/qaytarish qarori |
| 20 | **Rollback** rejasi? | Xavf boshqaruvi |

## Format

- Har savol **bitta** AskUserQuestion chaqiruvida (20 bosqich).
- Har javobdan keyin: qisqa tasdiq + keyingi savol.
- Har 4 savoldan keyin: oraliq xulosa (nima aniqlandi).
- Sessiya oxirida: **qaror hujjati** + implementatsiya tartibi.
- Javob noaniq bo'lsa — **qayta so'raladi**, o'zim to'ldirmayman.

## Tuzatilgan da'vo (kontekst)

Oldingi xulosa: *"A varianti KEP'da sinovdan o'tdi va muvaffaqiyatsiz bo'ldi"*.

**Tuzatildi:** KEP'da sahifa **mavjud, lekin ko'rsatilmagan** — nav'da havola
yo'q, bildirishnoma yo'q. Past layk (median 0) **tarqatish yo'qligini**
ko'rsatadi, formatni emas. `DESIGN-VARIANTS.md` shu asosda tahrirlandi.

---

## Javoblar

### Blok 1 — Maqsad va o'quvchi ✅

| # | Savol | Javob |
|---|---|---|
| 1 | Asosiy maqsad | **Xabardor qilish + ishonch** (ikkalasi, birinchi darajali) |
| 2 | Asosiy o'quvchi | **Barchaga, har doim ko'rinadi** — doimiy ochiq bo'lim |
| 3 | Muvaffaqiyat o'lchovi | **Ko'rish va o'qish** (Faza 1 uchun yagona ishlaydigan o'lchov) |
| 4 | Hozir qayerdan biladi | **Hech qayerdan** — tarqatish yo'q. Kelajakda: **Telegram kanal + Codeforces blog + platformaning o'zi** |

### Blok 1 — xulosa va oqibatlari

**1. Platforma pre-launch.** *"Development jarayonidamiz… platforma haqida hech
kim xabardor emas."* Ya'ni modul **foydalanuvchisiz** ishga tushadi.

**2. Kritik massa yo'q → Variant B (ijtimoiy lenta) rad etiladi.** Bo'sh lenta
"hech kim yo'q" degan taassurot beradi. Bu endi taxmin emas — bevosita javobdan
kelib chiqadi.

**3. Modul — manba, kanallar — ko'zgu.** Telegram va Codeforces blog
**tarqatish** kanallari; platformadagi modul esa **haqiqat manbai** (canonical).
Ya'ni har yozuv **ochiq, doimiy havola** olishi kerak — boshqa kanallar shunga
havola beradi.

**4. Modul ayni paytda marketing aktivi.** Foydalanuvchi yo'qligi sababli modul
**SEO va ulashish** uchun ishlashi shart — yopiq panel emas.

**5. "Har doim barchaga ko'rinadi" → E variantining sahifasiz shakli mos emas.**
E **qo'shimcha** qatlam sifatida qoladi (o'qilmagan belgisi), lekin asosiy
qatlam — **doimiy ochiq bo'lim**.

### Blok 2 — Tarqatish ✅

| # | Savol | Javob |
|---|---|---|
| 5 | Qayerda ko'rinadi | **Ikkalasi** — bosh sahifada qisqa ro'yxat + to'liq arxiv sahifasi |
| 6 | Qo'shimcha nuqtalar | **Nav'da "yangi" chip + qo'ng'iroq/panel** (tashqi kanal yo'q) |
| 7 | O'qilmagan holat | **Bazada, foydalanuvchi bo'yicha** (`UserUpdateRead`) |
| 8 | Mehmon | **To'liq ko'rinadi** — arxiv ham, bosh sahifa bo'limi ham |

### Blok 2 — xulosa va oqibatlari

**1. Ikki qavatli arxitektura shakllandi:**

| Qavat | Kimga | Nima |
|---|---|---|
| **Ochiq qavat** | Hamma, mehmon ham | Bosh sahifa bo'limi + `/updates` arxivi · har yozuv doimiy havola |
| **Shaxsiy qavat** | Faqat kirganlar | Nav chipi + qo'ng'iroq + slide-over panel · `UserUpdateRead` asosida |

**2. Har yozuv ochiq havola olishi SHART.** Sabab: Telegram va Codeforces blog
shunga havola beradi, va mehmon ham ko'radi. Bu **texnik talab**, bezak emas.

**3. O'qilmagan holat faqat kirganlarga.** Mehmon chip/qo'ng'iroq ko'rmaydi —
`UserUpdateRead` yozuvi yo'q. Bu **ataylab** shunday.

**4. Tashqi kanal yo'q.** Telegram bot ham, email ham tanlanmadi. Tarqatish
**platforma ichida** qoladi; Telegram kanal va Codeforces blog — **qo'lda**
e'lon qilinadigan tashqi ko'zgular.

**5. Bu Variant E ni qayta belgilaydi.** E "asosiy qatlam" emas — u **shaxsiy
qavat**. Asosiy qatlam: **A (arxiv) + bosh sahifa bo'limi**.

### Blok 3 — Kontent ✅

| # | Savol | Javob |
|---|---|---|
| 9 | Kim yozadi | **Faqat jamoa** |
| 10 | Bo'linish | **Aralash** — muhim alohida, kichik tuzatishlar guruhda |
| 11 | Tur belgilari | **10 tur** (quyida) |
| 12 | Rasm | **Faqat kerak bo'lganda** (KEP'da 20% edi) |

**Qabul qilingan 10 tur:**

| # | Tur | Guruh |
|---|---|---|
| 1 | Yangi | nima bo'ldi |
| 2 | Yaxshilandi | nima bo'ldi |
| 3 | Tuzatildi | nima bo'ldi |
| 4 | Tezlik | sifat |
| 5 | Xavfsizlik | sifat |
| 6 | Dizayn | ko'rinish |
| 7 | Kontent | nima bo'ldi |
| 8 | Infratuzilma | muhit |
| 9 | **Buzuvchi** | **ogohlantirish** |
| 10 | **Olib tashlanadi** | **ogohlantirish** |

⚠️ 9 va 10 **harakatga chaqiradi** (kodni yangilash, boshqa usulga o'tish) —
qolgan 8 tasi faqat xabar beradi. Rang va joylashuvda bu farq ko'rinishi shart.

### Blok 4 — GitHub integratsiyasi ✅ (T2)

| # | Savol | Javob |
|---|---|---|
| 13 | GitHub'dan olinadimi | **Ha, qoralama sifatida** — jamoa tahrirlab nashr qiladi |
| 14 | Manba | **PR + release/teg + commit + issue** (to'rttasi) |
| 15 | Tasdiq | **Har yozuv qo'lda tasdiqlanadi** |
| 16 | Matn | **AI qoralama (uz) → jamoa tahriri → AI tarjima ×10** |

### ⚠️ Yangi topshiriq — BACKFILL

Saidakbar aka ko'rsatmasi:

> *"Buni menimcha AI agent sifatida sen to'liq bazaga yozib berishing kerak.
> GitHub'dagi shu paytgacha qilingan commitlar asosida. Keyingilari esa
> avtomatik draft qilinadi."*

| Vazifa | Kim | Manba |
|---|---|---|
| **Backfill** — o'tgan o'zgarishlarni bazaga yozish | **WB (AI)** | `rankwant/` git tarixi |
| **Kelajak** — har yangi o'zgarish | avtomatik qoralama → jamoa tasdiqi | PR / release / commit / issue |

**Oqim (ikkalasi uchun bir xil):**

```
GitHub (commit/PR) → AI qoralama (o'zbekcha + 10 turdan biri)
                          ↓
                    jamoa tahriri va tasdiqi (15-savol)
                          ↓
                    AI tarjima ×10 til
                          ↓
                    nashr → Telegram + Codeforces blog (qo'lda ko'zgu)
```

**Backfill alohida dizayn talab qiladi:** nechta yozuv, qanday guruhlanadi,
qaysi commit'lar kirmaydi (refactor, test, chore). Sessiya tugagach boshlanadi.

### Blok 5 — Reliz siyosati ✅ (T1)

| # | Savol | Javob |
|---|---|---|
| 17 | Chiqarish mexanizmi | **Feature flag** — orqaga qaytarish bir tugma |
| 18 | Fazalar | **3 faza** (quyida) |
| 19 | Davom qarori | **Ko'rsatkich + sifat ko'rigi** |
| 20 | Rollback | **Ikki darajali** — modul (flag) + yozuv (nashrdan olish) |

---

# YAKUNIY QAROR

## 20 javob

| # | Savol | Javob |
|---|---|---|
| 1 | Asosiy maqsad | **Xabardor qilish + ishonch** |
| 2 | O'quvchi | **Barchaga, har doim ko'rinadi** |
| 3 | Muvaffaqiyat o'lchovi | **Ko'rish va o'qish** |
| 4 | Hozir qayerdan biladi | **Hech qayerdan** → Telegram + Codeforces blog + platforma |
| 5 | Qayerda ko'rinadi | **Ikkalasi** — bosh sahifa bo'limi + `/updates` arxivi |
| 6 | Qo'shimcha nuqtalar | **Nav chipi + qo'ng'iroq/panel** |
| 7 | O'qilmagan holat | **Bazada** (`UserUpdateRead`) |
| 8 | Mehmon | **To'liq ko'rinadi** |
| 9 | Kontent muallifi | **Faqat jamoa** |
| 10 | Bo'linish | **Aralash** — muhim alohida, kichik guruhda |
| 11 | Tur belgilari | **10 tur** |
| 12 | Rasm | **Faqat kerak bo'lganda** |
| 13 | GitHub'dan olinadimi | **Ha, qoralama sifatida** |
| 14 | Manba | **PR + release + commit + issue** |
| 15 | Tasdiq | **Har yozuv qo'lda** |
| 16 | Matn | **AI qoralama → jamoa → AI tarjima ×10** |
| 17 | Chiqarish mexanizmi | **Feature flag** |
| 18 | Fazalar | **3 faza** |
| 19 | Davom qarori | **Ko'rsatkich + sifat ko'rigi** |
| 20 | Rollback | **Ikki darajali** |

## Aniqlangan arxitektura

### Ikki qavat

| Qavat | Kimga | Nima |
|---|---|---|
| **Ochiq** | Hamma, mehmon ham | Bosh sahifa bo'limi + `/updates` arxivi · har yozuv doimiy havola |
| **Shaxsiy** | Faqat kirganlar | Nav chipi + qo'ng'iroq + slide-over panel · `UserUpdateRead` |

### Oqim

```
GitHub (PR / release / commit / issue)
      ↓
AI qoralama: o'zbekcha matn + 10 turdan biri
      ↓
jamoa tahriri va tasdiqi          ← sifat darvozasi
      ↓
AI tarjima ×10 til
      ↓
nashr (feature flag orqali)       ← rollback bir tugma
      ↓
Telegram kanal + Codeforces blog  ← qo'lda ko'zgu
```

### 3 faza

| Faza | Nima | Chiqish mezoni |
|---|---|---|
| **①** | Backfill + arxiv + bosh sahifa bo'limi | ≥100 tashrif · ≥30% yozuv ochilishi · matn ko'rigi |
| **②** | Shaxsiy qavat: chip, qo'ng'iroq, panel | O'qilganlik nisbati · panel ochilish darajasi |
| **③** | Roadmap va ovoz berish | Ovoz berish faolligi · taklif soni |

### Rollback

| Daraja | Qanday | Ma'lumot |
|---|---|---|
| **Modul** | Feature flag o'chirish | Bazada qoladi, yo'qolmaydi |
| **Yozuv** | Nashrdan olish | Arxivda qoladi — havola **sindirilmaydi** |

## Qaysi variant tanlandi

| Variant | Holat |
|---|---|
| **A — Xronologiya** | ✅ **Asosiy qavat** (arxiv) |
| **B — Oqim** | ❌ Rad etildi — kritik massa yo'q (4-savol) |
| **C — Roadmap** | ⏳ **3-faza** |
| **D — Reliz** | ✅ **Kontent formati** (10 tur + guruhlash) |
| **E — Kontekst** | ✅ **Shaxsiy qavat** (2-faza) |

Ya'ni dastlab taklif qilingan **D + E gibrid** tasdiqlandi — lekin **qatlamlari
aniqlandi**: A arxiv, D kontent, E shaxsiy qavat, C keyingi faza.

## Keyingi qadam — BACKFILL

Eng katta ochiq vazifa: **git tarixidan o'tgan o'zgarishlarni bazaga yozish**.

Boshlanishidan oldin hal qilinishi kerak:

1. **Qamrov** — nechta commit, qaysi davr
2. **Filtrlash** — qaysi commit'lar kirmaydi (`chore`, `test`, `refactor`, `ci`)
3. **Guruhlash** — har PR = bir yozuvmi yoki bir nechta
4. **Tur tasnifi** — 10 turdan qaysi biri (avtomatik taklif + qo'lda tasdiq)
5. **Til** — o'zbekcha qoralama, keyin ×10 tarjima
6. **Takrorlanish** — bir o'zgarish bir necha commit'da bo'lsa, birlashtirish

Bu alohida sessiya talab qiladi.
