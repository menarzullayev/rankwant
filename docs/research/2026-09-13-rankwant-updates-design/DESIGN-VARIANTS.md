# RankWant — Updates moduli: 5 dizayn varianti

Sana: 2026-09-13 · Muallif: WB · Holat: **tanlov kutilmoqda**

---

## Nima uchun bu hujjat

KEP.uz ning `updates` sahifasini o'lchadim (Chrome DevTools MCP orqali):

| Ko'rsatkich     | Qiymat  |
| --------------- | ------- |
| Yozuvlar        | 25      |
| Jami layk       | **36**  |
| O'rtacha layk   | **1.4** |
| **Median layk** | **0**   |

⚠️ **Bu raqamlar "format ishlamadi" degani EMAS.** Saidakbar aka aniqlashtirdi:
funksiya **ancha avval qo'shilgan, lekin foydalanuvchilarga ko'rsatilmagan**.

Ya'ni past layk **tarqatish yo'qligidan** kelib chiqqan, formatdan emas. Sahifa
mavjud, lekin unga olib boradigan yo'l yo'q — nav'da havola yo'q, bildirishnoma
yo'q, "yangi" belgisi yo'q.

Bu farq hal qiluvchi: o'lchov **kontent formatini** emas, **tarqatishning
yo'qligini** ko'rsatadi. Shu sababli **E (tarqatish)** variantining ahamiyati
**oshadi**, kamaymaydi.

Har bir variant muammoni boshqacha hal qiladi: ba'zilari kontentga, ba'zilari
tarqatishga, ba'zilari jamiyatga tayanadi.

---

## Variant A — "Xronologiya"

### Kontseptsiya

Klassik changelog. Teskari xronologiya, sana ustuni, tur belgilari. KEP'nikidan  
farqi: **modul bo'yicha filtr** va **obuna** (RSS + email dayjest). Maqsad —  
foydalanuvchi o'zini qiziqtirgan qismni topib, **qaytib kelishini** ta'minlash.

### Ekran tuzilishi

```
/updates
├── Sarlavha + "Obuna bo'lish" tugmasi
├── Filtr chiplari: Hammasi · Yangi · Yaxshilandi · Tuzatildi · <modul>
├── Timeline
│   ├── Sana ustuni (chap, 110px)     ─── nuqta
│   └── Yozuv kartalari (o'ng)
│       ├── Tur belgisi (Yangi/Yangilandi/Tuzatildi)
│       ├── Sarlavha
│       └── Bir qatorli tavsif
└── "Yana yuklash" · RSS · Email dayjest
```

**Sahifalar:** 1 ta (`/updates`). Yozuv tafsiloti — akkordeon, alohida sahifa emas.

### Foydalanuvchi oqimi

```
Kirish → filtr tanlash → ro'yxatni ko'rish → yozuvni ochish (akkordeon)
                                              ↓
                                        "Obuna bo'lish" → RSS/email
```

**Asosiy yo'l:** 4 qadam. Ro'yxatdan o'tish **shart emas**.

### Asosiy UI elementlari

| Element          | Vazifa                                                                                |
| ---------------- | ------------------------------------------------------------------------------------- |
| Filtr chiplari   | Modul/tur bo'yicha toraytirish                                                        |
| Timeline nuqtasi | Sana va yozuvni bog'lash                                                              |
| Tur belgisi      | 4 xil rang: Yangi (yashil) · Yangilandi (sariq) · Tuzatildi (ko'k) · Buzuvchi (qizil) |
| Yozuv kartasi    | Sarlavha + tavsif, akkordeon                                                          |
| Obuna tugmasi    | RSS + email dayjest                                                                   |
| "Yana yuklash"   | Kursorli sahifalash                                                                   |

### Afzalliklari

- **Tanish va oson.** Foydalanuvchi nima kutishini biladi.
- **SEO uchun eng yaxshi.** Har yozuv alohida havola olishi mumkin → qidiruvdan trafik.
- **Eng arzon.** Bitta ro'yxat sahifasi, server tomonda sahifalash.
- **Oflayn o'qish.** RSS bilan integratsiya qiluvchilar uchun qulay.

### Kamchiliklari

- **⚠️ Passiv.** Foydalanuvchi o'zi kelishi kerak. KEP'da bu sahifa past layk  
  oldi (median 0) — lekin sabab **format emas, sahifaning ko'rsatilmagani**.  
  Ya'ni bu kamchilik **isbotlangan emas, nazariy**.
- **Qaytib kelish sababi yo'q.** Bir marta o'qib, unutadi.
- **Fikr-mulohaza yo'q.** Muallif nima ishlaganini bilmaydi.
- **Bo'sh ko'rinadi** agar oyiga 2-3 yozuv bo'lsa.

---

## Variant B — "Oqim"

### Kontseptsiya

Har yangilanish — **post**. Muallif, vaqt, reaksiyalar, izohlar. Maqsad —  
**jamiyat orqali jalb qilish**: odam boshqalar reaksiya bergan narsani o'qiydi.

### Ekran tuzilishi

```
/updates (oqim)
├── Tab: "Barchasi" · "Kuzatayotganlarim"
├── Post kartalari
│   ├── Avatar + muallif + vaqt + "Kuzatish"
│   ├── Sarlavha
│   ├── Matn (2-3 qator, "davomini o'qish")
│   ├── Rasm (ixtiyoriy)
│   └── Reaksiya qatori: Foydali · Zo'r · Savol  +  izohlar soni
└── Cheksiz yuklash

/updates/<id> (post tafsiloti)
├── To'liq post
├── Reaksiyalar (ro'yxati bilan)
└── Izohlar ipi (javoblar bilan)
```

**Sahifalar:** 2 ta (oqim + post tafsiloti).

### Foydalanuvchi oqimi

```
Oqim → postni o'qish → reaksiya berish → izoh yozish → muallifni kuzatish
                                                            ↓
                                          yangi post → bildirishnoma
```

**Ijtimoiy halqa:** reaksiya → ko'rinish → yangi o'quvchi → reaksiya.

### Asosiy UI elementlari

| Element           | Vazifa                                                         |
| ----------------- | -------------------------------------------------------------- |
| Post kartasi      | Avatar, muallif, vaqt, matn, rasm                              |
| Reaksiya chiplari | **Nomlangan** reaksiyalar (emoji emas): Foydali · Zo'r · Savol |
| Izohlar ipi       | Muhokama, javoblar bilan                                       |
| "Kuzatish"        | Modul yoki muallifni kuzatish                                  |
| Bildirishnoma     | Kuzatilgan mavzuda yangi post                                  |

**Muhim qaror:** reaksiyalar **nomlangan**, emoji emas. Sabab: "Foydali" —  
o'lchanadigan signal, "❤️" — emas. Muallif qaysi funksiya foydali bo'lganini  
biladi.

### Afzalliklari

- **Jalb qilishning eng kuchli mexanizmi.** Ijtimoiy dalil ishlaydi.
- **Fikr-mulohaza halqasi.** Izohlar → muallif keyingi ishni to'g'rilaydi.
- **Kontent o'z-o'zidan ko'payadi.** Foydalanuvchi ham post yoza oladi  
  (masalan "men shu funksiyani ishlatdim, mana natija").
- **Mavzu bo'yicha kuzatish** — shovqinni kamaytiradi.

### Kamchiliklari

- **⚠️ Kritik massa kerak.** 50 foydalanuvchi bilan lenta bo'sh va g'amgin  
  ko'rinadi — bu **faol zarar**, passiv sahifadan yomonroq.
- **Moderatsiya yuki.** Izohlar, spam, haqorat — doimiy ish.
- **Bekend qimmat.** Reaksiya, izoh, kuzatish, bildirishnoma — 4 ta yangi jadval.
- **SEO zaif.** Cheksiz lenta indekslanmaydi.

---

## Variant C — "Yo'l xaritasi"

### Kontseptsiya

Yangilanish **kelajakka qaraydi**. Ochiq roadmap: foydalanuvchi nima  
rejalashtirilganini ko'radi va **ovoz beradi**. Maqsad — foydalanuvchini  
mahsulot qaroriga sherik qilish.

### Ekran tuzilishi

```
/roadmap
├── Ustunlar (kanban)
│   ├── Rejalashtirilgan  (ovoz tugmasi bilan, ovoz bo'yicha saralangan)
│   ├── Ishlanmoqda       (taxminiy muddat)
│   └── Chiqarildi        (sana + changelog havolasi)
└── "Taklif berish" tugmasi

/roadmap/<id>
├── Muammo tavsifi
├── Ovoz tugmasi + ovoz soni
├── Holat tarixi (Rejalashtirilgan → Ishlanmoqda → Chiqarildi)
└── Izohlar
```

**Sahifalar:** 2 ta. "Chiqarildi" ustuni **Variant A/D arxiviga** havola qiladi.

### Foydalanuvchi oqimi

```
Roadmap → rejalashtirilgan bandni ko'rish → ovoz berish
                                              ↓
                            holat o'zgarganda bildirishnoma
                                              ↓
                              chiqarildi → changelog yozuvi
```

**Halqa:** ovoz → ish → chiqarildi → bildirishnoma → qaytib keladi.

### Asosiy UI elementlari

| Element        | Vazifa                                                |
| -------------- | ----------------------------------------------------- |
| Kanban ustuni  | 3 holat, aniq chegaralar                              |
| Ovoz tugmasi   | Bosilgan/bosilmagan holat, jonli son                  |
| Holat belgisi  | Rang + matn (faqat rangga tayanmaydi)                 |
| Muddat         | "Sentabr oxiri" — aniq sana emas, **majburiyat emas** |
| Taklif formasi | Foydalanuvchi o'z g'oyasini qo'shadi                  |

**Muhim qaror:** muddat **chorak** darajasida ("Sentabr oxiri"), aniq sana  
emas. Aniq sana berilmasa, kechikish umidsizlik keltirmaydi.

### Afzalliklari

- **Eng kuchli jalb qilish.** Odam o'zi ovoz bergan narsani kutadi va qaytib keladi.
- **Shaffoflik ishonch quradi.** "Nima ustida ishlayapsiz?" savoli yo'qoladi.
- **Roadmap = kontent manbai.** Har band kelajakdagi changelog yozuvi.
- **Bepul mahsulot tadqiqoti.** Ovozlar — ustuvorlik ma'lumoti.

### Kamchiliklari

- **⚠️ Ommaviy majburiyat.** Ovoz bergan funksiya chiqmasa — ishonch buziladi.
- **Kuratsiya talab qiladi.** Har band yozilishi, holati yangilanishi kerak.
- **Ovoz tizimi o'zi qimmat** (foydalanuvchi boshiga cheklov, firibgarlik).
- **Kam foydalanuvchi = kam ovoz.** 342 ovoz ishonarli ko'rinmaydi.
- **"Rejalashtirilgan" abadiy qolib ketishi mumkin** — bu eng yomon holat.

---

## Variant D — "Reliz"

### Kontseptsiya

Yangilanish **versiyalarga** bog'lanadi. Semantik versiyalash (`v1.4.0`),  
o'zgarish turlari bo'yicha guruhlash, **buzuvchi o'zgarish** alohida  
ogohlantirish. Auditoriya — **kuchli foydalanuvchi va integrator** (API, bot,  
arxiv import qiluvchilar).

### Ekran tuzilishi

```
/releases
├── Reliz kartalari (teskari xronologiya)
│   ├── Sarlavha: v1.4.0 · 11 iyun 2026 · "Oxirgi" belgisi
│   ├── Yangi · N        (ro'yxat)
│   ├── Yaxshilandi · N  (ro'yxat)
│   ├── Tuzatildi · N    (ro'yxat)
│   └── ⚠ Buzuvchi · N   (rangli blok, alohida)
└── RSS

/releases/<versiya>
├── To'liq release notes (markdown)
├── Teglar
└── Oldingi/keyingi versiya havolalari
```

**Sahifalar:** 2 ta. Buzuvchi o'zgarish **har doim** yuqorida.

### Foydalanuvchi oqimi

```
RSS/email → reliz yozuvi → buzuvchi o'zgarishni tekshirish
                                ↓
                      (integrator) kodni moslashtirish
```

**Asosiy yo'l:** obuna → o'qish → harakat. **Sahifaga kirish shart emas.**

### Asosiy UI elementlari

| Element            | Vazifa                                        |
| ------------------ | --------------------------------------------- |
| Versiya sarlavhasi | `mono` shrift, aniq va qidiriladigan          |
| O'zgarish guruhi   | Tur bo'yicha ajratilgan ro'yxat               |
| Buzuvchi blok      | Qizil fon, ajralib turadi, yopilmaydi         |
| "Oxirgi" belgisi   | Hozirgi versiyani ko'rsatadi                  |
| RSS                | Integrator uchun asosiy kanal                 |
| Versiya havolasi   | Doimiy havola — hujjatda iqtibos qilish uchun |

### Afzalliklari

- **Eng aniq.** Integrator "nima o'zgardi" savoliga aniq javob oladi.
- **Avtomatlashtirish mumkin.** `git log` → guruhlangan release notes.
- **Buzuvchi o'zgarish ko'rinadi** — bu eng qimmatli signal.
- **Arzon.** Bitta ro'yxat + bitta tafsilot sahifasi.
- **Doimiy havola** — forumda, hujjatda iqtibos qilinadi.

### Kamchiliklari

- **⚠️ Sovuq va texnik.** Oddiy foydalanuvchi "v1.4.0" dan hech narsa his qilmaydi.
- **Versiyalash intizomi talab qiladi.** Har deploy versiya olmasa, mantiq buziladi.
- **Passiv.** Variant A bilan bir xil muammo: o'zi kelishi kerak.
- **Kichik tuzatishlar yo'qoladi.** "Tugma rangi tuzatildi" muhim emas ko'rinadi.

---

## Variant E — "Kontekst"

### Kontseptsiya

**Alohida sahifa yo'q.** Yangilik foydalanuvchi ishlayotgan **joyda** paydo  
bo'ladi: nav elementida "yangi" belgisi, qo'ng'iroqda o'qilmagan nuqta,  
birinchi ochilganda bir martalik ko'rsatma. Maqsad — **tarqatish muammosini**  
to'g'ridan-to'g'ri hal qilish.

### Ekran tuzilishi

```
Butun ilova
├── Yuqori panel: qo'ng'iroq + o'qilmagan nuqta
├── Nav elementlari: "yangi" chip (o'qilmagan modul)
└── Slide-over panel (qo'ng'iroqdan ochiladi)
    ├── "Hammasi o'qildi" tugmasi
    ├── O'qilmagan yozuvlar (nuqta bilan)
    ├── O'qilgan yozuvlar (xira)
    └── "Barchasini ko'rish" → /updates arxivi

Funksiya ichida
├── Bir martalik ko'rsatma (birinchi ochilganda)
└── "Yangi" belgisi (funksiya yonida)
```

**Sahifalar:** 0 ta yangi sahifa + 1 ta minimal arxiv (`/updates`).

### Foydalanuvchi oqimi

```
Mahsulotdan foydalanadi → nav'da "yangi" chipni ko'radi
                              ↓
                        qo'ng'iroqni bosadi → slide-over panel
                              ↓
                        o'qiydi → "Hammasi o'qildi"
                              ↓
                        (ixtiyoriy) batafsil → /updates arxivi
```

**Asosiy tamoyil:** foydalanuvchi **yangilik uchun sahifaga bormaydi** —  
yangilik uning oldiga keladi.

### Asosiy UI elementlari

| Element                       | Vazifa                          |
| ----------------------------- | ------------------------------- |
| Qo'ng'iroq + o'qilmagan nuqta | Asosiy kirish nuqtasi           |
| "yangi" chip                  | Nav darajasida, modul bo'yicha  |
| Slide-over panel              | Sahifadan chiqmasdan o'qish     |
| O'qilmagan nuqta              | Yozuv darajasida                |
| "Hammasi o'qildi"             | Tozalash                        |
| Bir martalik ko'rsatma        | Funksiya birinchi ishlatilganda |
| "Barchasini ko'rish"          | Arxivga havola                  |

**Muhim qaror:** har foydalanuvchi uchun **o'qilgan holat** saqlanadi  
(`UserUpdateRead`: user + update + read_at). Bu shaxsiylashtirishning asosi.

### Afzalliklari

- **⚠️ Muammoni to'g'ridan-to'g'ri hal qiladi.** "Hech kim ochmaydi" → endi  
  ochish shart emas.
- **Shaxsiylashtirish mumkin.** Faqat foydalanuvchiga tegishli modul ko'rsatiladi  
  ("Siz kuzatgan 'Masalalar'da yangi").
- **O'lchanadi.** O'qilgan/o'qilmagan nisbati — haqiqiy jalb ko'rsatkichi.
- **Kontekstda tushuntiradi.** Ko'rsatma funksiya ichida — eng tushunarli payt.
- **Sahifa yaratish shart emas** — mavjud qobiqqa qo'shiladi.

### Kamchiliklari

- **⚠️ Bezovta qilish xavfi.** Ko'p "yangi" belgisi = banner ko'rligi.  
  Chegara qo'yish shart (bir vaqtda 3 tadan ko'p emas).
- **Tarixni ko'rish qiyin.** Arxivi minimal bo'lsa, "o'tgan oyda nima o'zgardi?"  
  savoliga javob yo'q.
- **Har foydalanuvchi uchun holat** — qo'shimcha jadval va yozuv hajmi.
- **SEO yo'q.** Sahifa yo'q — indekslanadigan narsa yo'q.
- **Mehmonga ko'rsatilmaydi.** O'qilgan holat yo'q → chiplar mantiqsiz.

---

## Qiyoslash

| Mezon              | A Xronologiya       | B Oqim     | C Roadmap  | D Reliz        | E Kontekst     |
| ------------------ | ------------------- | ---------- | ---------- | -------------- | -------------- |
| Asosiy g'oya       | Kontent             | Jamiyat    | Ta'sir     | Aniqlik        | Tarqatish      |
| Yangi sahifa       | 1                   | 2          | 2          | 2              | **0**          |
| Jalb mexanizmi     | Zaif                | Kuchli     | **Kuchli** | Zaif           | **Kuchli**     |
| Kritik massa kerak | Yo'q                | **Ha**     | Ha         | Yo'q           | Yo'q           |
| Bekend yuki        | Past                | **Yuqori** | Yuqori     | Past           | O'rta          |
| Moderatsiya        | Yo'q                | **Ko'p**   | O'rta      | Yo'q           | Kam            |
| SEO                | **Yaxshi**          | Zaif       | Yaxshi     | Yaxshi         | Yo'q           |
| Integrator uchun   | O'rta               | Zaif       | Zaif       | **Eng yaxshi** | Zaif           |
| Ommaviy majburiyat | Yo'q                | Yo'q       | **Ha**     | Yo'q           | Yo'q           |
| O'lchanadi         | Zaif                | Yaxshi     | Yaxshi     | Zaif           | **Eng yaxshi** |
| KEP tajribasi      | Mavjud, lekin ko'rsatilmagan | Yo'q | Yo'q | Yo'q | Yo'q |

---


## Tavsiya: D + E gibrid

**Sabab.** KEP'da `updates` sahifasi **mavjud, lekin hech qayerdan
ko'rinmaydi** — nav'da havola yo'q, bildirishnoma yo'q, "yangi" belgisi yo'q.
Natijada 25 yozuv median **0** layk oldi.

⚠️ **Bu "A formati yaroqsiz" degani EMAS.** O'lchov shuni ko'rsatadi:
**tarqatish bo'lmasa, kontent formati muhim emas** — sahifa o'lik bo'ladi.
Demak tartib muhim: avval **E (tarqatish)**, keyin kontent formati.

**Taklif qilinadigan kombinatsiya:**

| Qatlam           | Variant          | Nima beradi                                                  |
| ---------------- | ---------------- | ------------------------------------------------------------ |
| **Kontent**      | **D — Reliz**    | Aniqlik, versiyalash, buzuvchi o'zgarish signali, arzon      |
| **Tarqatish**    | **E — Kontekst** | Foydalanuvchi oldiga boradi, o'lchanadi, shaxsiylashtiriladi |
| **Arxiv**        | **A (minimal)**  | SEO + "o'tgan oyda nima bo'ldi" + RSS                        |
| **Keyingi faza** | **C — Roadmap**  | Jalb qilish kuchaygach, ovoz berish qo'shiladi               |
| **Rad etiladi**  | **B — Oqim**     | Kritik massa yo'q; bo'sh lenta zarar keltiradi               |

**Bosqichlar:**

1. **1-faza (1 sprint):** D + minimal A. Reliz yozuvlari, arxiv sahifasi, RSS.  
   *O'lchov:* haftalik tashriflar, RSS obunachilar.
2. **2-faza (1 sprint):** E qatlami. `UserUpdateRead` jadvali, qo'ng'iroq,  
   slide-over panel, nav chiplari.  
   *O'lchov:* o'qilgan/o'qilmagan nisbati, panelni ochish darajasi.
3. **3-faza (2 sprint):** C — roadmap + ovoz berish. Jalb qilish isbotlangach.

**Nima uchun B emas:** RoboContest ham, KEP ham ijtimoiy lentani sinab  
ko'rmagan — lekin ikkalasining ham faol auditoriyasi biznikidan katta.  
Bo'sh lenta — ishlamayotgan lentadan yomonroq, chunki "hech kim yo'q" degan  
taassurot beradi. B ni keyinroq qayta ko'rib chiqish mumkin.

---

## Umumiy ma'lumot modeli (barcha variantlar uchun)

```python
class SystemUpdate:
    id: int
    title: str                    # 10 tilda (Translation model)
    description: str              # markdown, 10 tilda
    date: date
    update_type: str              # new | improved | fixed | breaking
    module: str                   # problems | contests | arena | shop | profile
    version: str | None           # faqat D uchun (v1.4.0)
    image: str | None
    likes_count: int              # denormalizatsiya
    is_published: bool

class UserUpdateRead:             # faqat E uchun
    user: FK
    update: FK
    read_at: datetime
    unique_together: (user, update)

class UpdateReaction:             # faqat B uchun
    user: FK
    update: FK
    kind: str                     # useful | great | question
```

**Muhim:** `module` maydoni **barcha variantlar uchun kerak** — u filtr (A),  
kuzatish (B), ovoz guruhi (C) va nav chipi (E) ning asosi.

---

## Dizayn tizimiga bog'lash

RankWant'da **12 uslub / 18 palitra** bor. Updates moduli:

- **Faqat mavjud tokenlardan** foydalanadi: `--rw-line`, `--rw-surface`,  
  `--rw-text-*`. Yangi token qo'shilmaydi.
- **4 tur belgisi** semantik ranglarga bog'lanadi va **har palitrada** kontrast  
  tekshirilishi kerak (`check_contrast.py`).
- **`dual: true` uslublarda** (dashboard, swiss, flat, material, editorial,  
  brutal) light/dark ikkalasi ham sinaladi. `dual: false` uslublar  
  (terminal, glass, neu, clay, aurora, skeu) faqat o'z muhitida.
- **Qo'lda yozilgan `grid-cols-N`** — Tailwind dinamik sinfni skanerlamaydi  
  (loyihada ma'lum tuzoq).
- Slide-over panel **`position: fixed`** ishlatadi — bu modul darajasida  
  qabul qilinadi, lekin vizualizatsiya widget'ida emas.

---

## Keyingi qadam

1. Variant tanlanadi (yoki gibrid tasdiqlanadi).
2. Tanlangan variant `rankwant/docs/` ga **inglizcha** texnik topshiriq  
   sifatida o'tkaziladi (loyiha qoidasi).
3. `04-prd` ga Phase 1 ga qo'shiladi.
4. Wireframe → implementatsiya.
