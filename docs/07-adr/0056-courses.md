# ADR 0056 — Kurslar: Kurs → Modul → Bo'lim → Dars

**STATUS:** accepted (qamrov, tuzilish, kirish, video, to'lov modeli, tartib)
**Sana:** 2026-11-10
**Tasdiqlagan:** Saidakbar (owner) — 2026-11-10, 4 bosqichda 16 savol
**Ta'sir doirasi:** yangi `apps/api/courses/` ilovasi; `qvant`, `quizzes`, `judging`, `classroom`, `core` (sertifikat); web `/courses`, `/studio/courses`, `/admin`; R2 (video)
**Dalil:** o'lchov 2026-11-10 — Codeforces EDU, Robocontest va KEP jonli brauzerda o'rganildi; RankWant kodi va jonli bazasi

## 1. Muammo

RankWant'da kurs yo'q. O'quv bloklari bor, lekin bir-biriga bog'lanmagan
va deyarli bo'sh (jonli baza, 2026-11-10):

| Bo'lim | Model | Jonli bazada |
|---|---|---|
| `/learn` Maqolalar | `content.Article` + masala havolalari | 4 |
| `/roadmaps` Traektoriya | `content.Roadmap` + `RoadmapStep` | 1 (5 qadam) |
| `/algorithms` | `content.Article` (algoritm turi) | 1 |
| `/classroom` Auditoriya | `classroom.Classroom` + `Assignment` | 1 |
| `/quizzes` Testlar | `quizzes.Quiz` | 1 |

Bu yozuvlar development davridagi sinov kontenti — egasining qarori bilan
to'liq tozalanadi (alohida, tasdiq bilan) va kontent professional tarzda
qaytadan yoziladi.

## 2. Raqobatchilar (o'lchandi 2026-11-10)

| | Codeforces EDU | Robocontest | KEP |
|---|---|---|---|
| Bo'lim | Courses (beta, 2 kurs) | Kurslar (5) + O'quv rejalari (7) | Kurs yo'q (2023 da bor edi) → Study plans (11), «Recommend for me», Projects |
| Tuzilish | Kurs → Dars → Bosqich (nazariya + masalalar) | Kurs → Modul → Bo'lim → Dars (Video / Leksiya / Masala) | Reja → Kun (kuniga 3 masala) |
| Kirish | Bepul, `Enroll` + login; 240 569 talaba | 1 bepul, 4 pullik (97–647 ming so'm) yoki obuna: Plus 26 100, Pro 44 100, Judge 89 100 so'm/oy | Kepcoin bilan (5) |
| Video | YouTube embed (bilvosita: Xitoyda Bilibili'ga qayta yuklangan) | O'zlari: API `manifestUrl` → `.mpd` bo'lsa `dash.js`, aks holda `hls.js`; DRM yo'q, himoya — manifestni faqat sotib olganga berish | — |

## 3. Qaror

### 3.1 Tuzilish va dars turlari

**Kurs → Modul → Bo'lim → Dars** (to'rt daraja, Robocontest shakli).
Dars turlari: **matn** (Markdown + LaTeX), **masala** (judge, mavjud
`problems.Problem`), **test** (`quizzes.Quiz`), **video**.

### 3.2 Til

**Bitta kurs, ko'p tilli darslar.** Kurs va dars matnlari tillar bo'yicha
tarjima jadvalida; video subtitr bilan. Tarjima yo'q tilda zaxira — kursning
asosiy tili (ochiq belgi bilan, `ContentName` naqshi).

### 3.3 Kirish

To'rt tur birga ishlaydi:

1. **Bepul** — faqat ro'yxatdan o'tganlarga; mehmon kurs tavsifi va
   dasturini ko'radi, darslar — kirgandan keyin (ADR-0054 zonalari).
2. **Qvant bilan ochiladigan** — narx Qvant'da; yechish faqat ledger orqali
   (ADR-0002).
3. **Pullik** — bir martalik xarid **va** Robocontest kabi **3 tarif**
   (Plus / Pro / Judge); tariflarga keyinchalik boshqa pullik xizmatlar ham
   qo'shiladi.
4. **Auditoriya** — o'qituvchi kursni sinfga topshiriq qilib beradi va
   o'quvchilar progressini ko'radi.

### 3.4 Progress va motivatsiya

Yozilish (`Enroll`) va progress foizi; **ketma-ket ochilish** (kurs bo'yicha
yoqiladi); **sertifikat** — barcha majburiy darslar + yakuniy test
**≥ 70%** (kurs bo'yicha o'zgartiriladi), musobaqa sertifikatlari kabi
tekshiriladigan; **Qvant mukofoti** — modul va kurs tugaganda (ledger).

### 3.5 Video

- **Pullik:** Cloudflare **R2 + HLS**. Video yuklanganda `ffmpeg` bilan
  HLS'ga kodlanadi, R2 ga yoziladi; manifest va segmentlar faqat kirish
  huquqi borga muddatli imzolangan havola bilan beriladi. R2 bepul tarifi
  oyiga 10 GB saqlash, 10 mln o'qish, chiqish trafigi bepul — egasi:
  «10 GB bizga bemalol yetadi».
- **Bepul:** muallif tanlaydi — **YouTube**, **Vimeo** yoki **R2 + HLS**.
- ⚠️ Video **o'z kompyuterimizdan tunnel orqali berilmaydi**: Cloudflare
  Service-Specific Terms bepul CDN orqali video berishni taqiqlaydi
  (Developer Platform — R2 — bundan mustasno). Buzilsa butun sayt CDN'i
  cheklanishi mumkin.
- ⚠️ YouTube shartlari («Right to Monetize») videoga reklama qo'yishga
  ruxsat beradi — muallif bu narxni biladi.
- `R2` yoqilishi — egasining qadami (hisob, kalitlar). Lokal va CI'da MinIO.

### 3.6 Kontent va nashr

Manbalar: mualliflar `/studio` orqali, platforma jamoasi (`staff-content`),
AI qoralama + inson ko'rigi, mavjud masala arxividan yig'ish. Nashr —
**faqat xodim ko'rigidan keyin**; pullik kurs narxini faqat xodim
tasdiqlaydi.

### 3.7 To'lov

Hammasi hozir quriladi: buyurtma, to'lov, obuna va **Payme / Click**
integratsiyasi. Merchant ma'lumotlari YaTT yoki MChJ ochilgach qo'shiladi;
ungacha integratsiya faqat sinov rejimida, kalitlar bo'sh bo'lsa to'lov
tugmasi chiqmaydi va kursga kirishni xodim qo'lda bera oladi.

### 3.8 Tartib

Prototipsiz, **bosqichli PR'lar**, hammasi `courses` bayrog'i ortida —
bayroq egasi «ochamiz» deganda yoqiladi. Uzoq kutiladigan qismlar
qisqartiriladi; har PR o'z testlari va salbiy testlari bilan.

| PR | Qamrov |
|---|---|
| 1 | Modellar, tarjimalar, kirish turi, bayroq, admin |
| 2 | Ommaviy API: katalog, kurs, dars, yozilish, progress, ketma-ket ochilish |
| 3 | Web: katalog, kurs va dars sahifalari |
| 4 | Studio mualliflik va xodim ko'rigi |
| 5 | Video: YouTube/Vimeo embed, R2 + HLS kodlash va imzolangan havolalar |
| 6 | Sertifikat, Qvant mukofoti, Qvant bilan ochish |
| 7 | Xarid, 3 tarif, Payme/Click (sinov rejimi) |
| 8 | Auditoriyaga kurs berish va o'qituvchi progressi |

**2-qism qanday qurildi.** Katalog va kurs sahifasi (dastur bilan) mehmonga
ochiq, dars esa kirgan va yozilgan o'quvchiga; `is_preview` dars yozilmasdan
ochiladi (ADR-0054). Til: `?lang=` (faqat `uz`/`ru`/`en`), bo'lmasa so'rov
tili, tarjima yo'q bo'lsa kursning asosiy tili; javobdagi `locale` qaysi til
berilganini aytadi. Ketma-ket ochilish faqat **majburiy** darslarga qaraydi —
ixtiyoriy dars hech narsani yopmaydi, foiz ham faqat majburiylardan.
Matn va video darsni o'quvchi o'zi tugatadi; masala darsi birinchi qabul
qilingan urinishda (`ratings.UserSolvedProblem`), test darsi `quiz_pass_percent`
dan past bo'lmagan natijada o'zi yoziladi — signal satr nomi bilan ulanadi
va uning xatosi urinish yoki test natijasini bekor qilmaydi. Yopiq dars
tugatilmaydi, yozilmagan o'quvchining yechimi progressga yozilmaydi.
HLS videoning R2 kaliti javobda **hech qachon** berilmaydi (imzolangan
havola 5-qismda). Arxivda bo'lmagan masala darsda havolasiz qoladi.
Qvant va pullik kursga bepul yozilish 402 bilan rad etiladi
(`course_qvant_required`, `course_payment_required`) — ularning yo'li 6- va 7-qismda.
Tarjima ko'pincha qisman bo'ladi (sarlavha bor, tavsif yo'q), shuning uchun
matn **maydon bo'yicha** asosiy tilga qaytadi — bo'sh blok chiqmaydi.

**3-qism qanday qurildi.** Uch sahifa: `/courses` (katalog, daraja va kirish
filtrlari, kirgan odamga «Mening kurslarim»), `/courses/<slug>` (tavsif,
dastur, yozilish yoki «davom etish», progress) va
`/courses/<slug>/lessons/<id>` (dars, masala/test havolasi, video havolasi,
«Tugatdim», oldingi/keyingi dars, yon tomonda dastur). Uchalasi ham bayroq
o'chiq bo'lsa **404** beradi (`check_decisions` qo'riqlaydi). Bo'lim
`access.ts` da `public`: mehmon katalog va dasturni ko'radi, dars o'rnida
«kirish» kartasi (`SignInGate`, sabab `course`). Video hozircha tashqi
havola — o'rnatilgan pleyer va CSP 5-qismda. ⚠️ **Yon menyuga band
qo'shilmadi**: «21 band / 5 guruh» egasining qarori (2026-09-19), kurslar
bandi bayroq ochilganda alohida so'raladi. Sitemap'ga ham hali kirmaydi.

## 4. Ochiq qolganlar

- Robocontest tariflari va pullik xizmatlarining chuqur tahlili — egasi
  o'rnatilgan brauzerda kirib beradi (Judge tarifi bor); tarif tarkibi
  shundan keyin aniqlashtiriladi.
- Muallif ulushi (pullik kurs daromadidan) — alohida qaror.
- Kontent rejasi (qaysi kurslar, qaysi tartibda) — alohida qarorlar.
- Sinov kontentini tozalash — alohida, aniq ro'yxat bilan tasdiq.
