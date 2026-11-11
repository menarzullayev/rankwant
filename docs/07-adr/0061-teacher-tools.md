# ADR 0061 — O'qituvchi vositalari: sinf, murabbiy, savollar banki, generator va kvota

**STATUS:** accepted
**Sana:** 2026-11-11
**Tasdiqlagan:** Saidakbar (owner). Qaror yozuvlari:
- [o'qituvchi vositalari](../decisions/2026-11-11-teacher-tools.md);
- [batafsil, 4 raund](../decisions/2026-11-11-teacher-tools-details.md);
- [Judge kvotasi](../decisions/2026-11-11-plan-contents.md).

**Ta'sir doirasi:**
- `core` (kvota modeli va xizmati);
- `classroom`;
- murabbiy (yangi);
- `quizzes`;
- `problems` (generator);
- `judging` (urinish kodini ko'rish);
- `notifications`, web studiya va sinf sahifalari.

**Dalil:** joriy holatning kod xaritasi (2026-11-11). Hozir bor narsalar:
- sinfga kod bilan darhol qo'shilish;
- har sinfda 200 a'zo, sinflar soni esa cheksiz;
- uyqudagi `coach_can_view_attempts` maydoni;
- faqat xodimlar yuritadigan yagona savollar banki;
- hack dvigatelidagi «generator → validator → etalon → S3» zanjiri;
- qattiq yozilgan qoralama chegaralari: 20 masala, 5 musobaqa, 3 kurs.

## 1. Muammo

Robocontest'ning Judge paneli o'qituvchiga beradigan imkoniyatlar bizda yo'q:
- sinfga tasdiq bilan qo'shish;
- murabbiyning o'quvchi kodini ko'rishi;
- papkali savollar banki va sinf testi;
- test generatori;
- rejaga bog'langan kvota.

Bundan tashqari hozirgi kod ikki joyda zaif:
- sinf kodi tarqalsa, uni bilgan har kim kiradi va kodni yangilab bo'lmaydi;
- bitta hisob cheksiz sinf ochishi mumkin.

## 2. Kvota (`core`)

- **Model.** `core.PlanQuota` — har reja uchun bitta qator, raqamlari admin'da o'zgartiriladi.
  Reja kodlari: `free`, `plus`, `pro`, `judge`.

  | Reja | Masala | Musobaqa | Test | Sinf | Sinfdagi o'quvchi | Test ma'lumoti |
  |---|---:|---:|---:|---:|---:|---:|
  | Bepul | 20 | 5 | 3 | 3 | 40 | 200 MB |
  | Judge | 2 000 | 100 | 50 | 50 | 50 | 4 GB |

  Boshqa app'lar rejani faqat `User.plan` va `plan_expires_at` dan o'qiydi (ADR-0057), `billing`
  ga tegmaydi.
- **Nima sanaladi.** Egalik qilingan barcha narsa: nashr qilingan ham, qoralama ham.
  - Sanoqni har app o'zi bajaradi, `core.quotas` faqat chegarani beradi (ADR-0042: `core` boshqa
    app'ning modelini import qilmaydi).
  - Xodimlar kvotadan tashqari.
  - Muddati o'tgan reja bepul rejadek sanaladi.
  - Mavjud narsa o'chirilmaydi: chegaradan oshgan bo'lsa, faqat yangisi ochilmaydi.

## 3. Sinf

- **Qo'shilish rejimi.** `Classroom.join_mode`: `instant` yoki `approval`.
  - Yangi sinf `approval` bilan ochiladi, migratsiya mavjud sinflarni `instant` da qoldiradi.
  - So'rov alohida `ClassroomJoinRequest` qatori bo'ladi, `ClassroomMember` emas. Sababi:
    a'zo yaratilishi sinfning bepul kurslariga yozish signalini ishga tushiradi (ADR-0056 § 8).
  - So'rov kelganda o'qituvchiga bildirishnoma boradi, qaror o'quvchiga ham yetkaziladi.
- **Boshqaruv:**
  - masala biriktirish formasi (API bor edi, web'da yo'q edi);
  - a'zoni chiqarish va o'quvchining o'zi chiqishi;
  - kodni yangilash va taklif havolasi;
  - yordamchi tayinlash;
  - arxivlash: o'chirish o'rniga `is_active=False`.
- **Yordamchi o'qituvchi** so'rovlarni qabul qiladi va a'zolar ro'yxatini ko'radi. Sinf
  sozlamalarini o'zgartira olmaydi va sinfni arxivlay olmaydi. Hisobotlar sinf egasida qoladi
  ([2026-11-10 qarori](../decisions/2026-11-10-courses-classroom.md): kurs hisoboti faqat egasiga;
  yordamchiga ochish egasining alohida tasdig'ini talab qiladi).
- **A'zolar chegarasi** egasining rejasidan olinadi. Qattiq yozilgan `MAX_MEMBERS = 200` o'rniga
  shu chegara ishlaydi.

## 4. Murabbiy

- **Bog'lanish modeli.** O'quvchi so'rov yuboradi, murabbiy qabul qiladi yoki rad etadi. O'quvchi
  bog'lanishni istalgan payt bekor qiladi. Bitta o'quvchida ko'pi bilan 3 ta faol murabbiy.
- **Kodni ko'rish ruxsati** har bog'lanishda alohida (`can_view_attempts`). Uning standart qiymati
  `User.coach_can_view_attempts` dan olinadi, ya'ni ADR-0024 maydoni endi ishlatiladi.
- **Urinish kodi** (`judging/views.py` → `retrieve`): muallif, xodim va hack istisnosiga yana bitta
  holat qo'shiladi — ruxsati bor faol murabbiy. Musobaqa muzlatish qoidalari o'z kuchida.
- **Profil.** «Murabbiy» — qabul qilingan murabbiylar, «O'qituvchi» — sinf egalari. Ikkalasini ham
  maxfiylik sozlamasi bilan yashirish mumkin.
- **Murabbiy paneli:** o'quvchilarning so'nggi urinishlari, yechilganlari, seriyasi va reytingi.
- **Masala tavsiyasi.** Murabbiy o'quvchiga masala tavsiya qiladi, u o'quvchining vazifalari
  ro'yxatida chiqadi.

## 5. Savollar banki va o'qituvchi testi

- **Egasi va papkalar.** Savol va testning egasi bor; savollar papkalarga bo'linadi.
  - Yaratish huquqi har kimda bor, kvota bilan.
  - Xodimlarning mavjud ommaviy banki o'zgarmaydi.
- **Savol turlari:**
  - bitta to'g'ri javobli tanlov (hozirgisi);
  - bir nechta to'g'ri javob — faqat to'liq to'g'ri javobga ball;
  - son (aniqlik bilan);
  - qisqa matn (katta-kichik harf va probel e'tiborsiz);
  - kod parchali savol (Markdown, sintaksis rangi bilan).
- **Ko'rinish va topshiriq.** O'qituvchi testi faqat sinfga ko'rinadi. U `Assignment` ga biriktiriladi
  (kurs kabi).
- **Test sozlamalari:**
  - vaqt chegarasi;
  - bir martalik urinish;
  - to'g'ri javoblarni test tugagach yoki muddat o'tgach ko'rsatish.
- **Qvant berilmaydi.** O'z testini yaratib, o'ziga Qvant ishlash yo'li yopiladi (ADR-0002).
- **Natija** sinf hisobotida ko'rinadi: ball, urinishlar va xato qilingan savollar.

## 6. Test generatori

- **Generator** — masalaga biriktirilgan dastur, tili istalgan. Muallif test qatorlarini yozadi.
- **Bir test qanday yasaladi:**
  - test qatori generatorning stdin'iga uzatiladi;
  - generatorning stdout'i testning kirishi bo'ladi;
  - validator bo'lsa, kirishni tekshiradi;
  - javobni muallifning etalon yechimi beradi;
  - test S3 ga yoziladi va `TestCase.Origin.GENERATED` deb belgilanadi.
- **Judge protokoli o'zgarmaydi.** Mavjud `custom` rejim yetadi. Natijalar yangi yo'naltirish kaliti
  bilan qaytadi, aks holda bunday natija bugun tashlab yuborilardi.
  Amalda kalit — `hack_stage` qiymati `testgen:<yurish>:<test>:<bosqich>`: judge bu maydonni o'qimay
  qaytaradi, `judging/tasks.py` uni `problems.generation` ga yo'naltiradi. Testlar birma-bir
  yasaladi, ya'ni bitta yurish navbatda bir vaqtda ko'pi bilan bitta ish ushlaydi.
- **Kim ishlatadi:** muallif o'z qoralamasi uchun (studiyada) va xodim. Muallif etalon yechim va
  generatorni o'zi yuklaydi.
- **Chegaralar:** bir yurishda ko'pi bilan 100 test; har test 8 MiB; test ma'lumoti kvotaga
  sanaladi.

## 7. Bosqichlar (alohida PR'lar)

1. Kvota xizmati va sinf (§ 2, § 3).
2. Murabbiy (§ 4).
3. Savollar banki va o'qituvchi testi (§ 5).
4. Test generatori (§ 6).

## 8. Oqibatlar va rad etilganlar

- **Yangi chegaralar.** Hozir hamma bepul rejada (billing o'chiq), shuning uchun yangi sinf
  ochishda 3 × 40 chegarasi darhol amal qiladi. Mavjud sinflar saqlanadi.
- **«Coach» ma'nosi o'zgaradi.** ADR-0017 da bu so'z sinf egasini anglatardi. Endi «coach» —
  qabul qilingan murabbiy, sinf egasi esa «O'qituvchi».
- **Rad etilgan variantlar:**
  - Polygon'dagi kabi buyruq argumentlari: judge protokolini ikkala judge'da o'zgartirishni talab
    qilardi;
  - faqat qoralamani sanash: Judge kvotasining ma'nosi qolmasdi;
  - bitta umumiy kod ruxsati: o'quvchi murabbiylarni tanlab ruxsat bera olmasdi.
