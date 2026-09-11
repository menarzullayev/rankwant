# ADR-0017: Profil va sozlamalar — KEP'dan ilhomlangan, global

**STATUS:** accepted (2026-09-11)
**Yangilangan:** 2026-09-11 — profil sahifasi (pastdagi bo'lim)
**Ta'siri:** [ADR-0002](0002-qvant-economy.md) (Qvant ledgeri),
[ADR-0015](0015-account-email.md) (hisob xatlari),
[ADR-0016](0016-signup-and-login.md) (ro'yxat va kirish)

## Muammo

Sozlamalar sahifasida uchta narsa bor edi: ulangan hisoblar, eksport va
o'chirish. Profil faqat reytingni ko'rsatardi. Rasm qo'yish, parolni
almashtirish, pochtani o'zgartirish, kirilgan qurilmalarni ko'rish —
bularning birortasiga UI yo'q edi; ijtimoiy hisob bilan kirgan odam esa
parol o'rnata olmasdi, ya'ni provayderni uzish imkonsiz edi.

kep.uz sozlamalari bo'limma-bo'lim o'rganildi va 20 savol bo'yicha
qaror qabul qilindi (2026-09-11). Platforma global — mamlakat, viloyat
va til shunga qarab tanlandi.

## Qaror

| Savol | Tanlov | Sabab |
| ----- | ------ | ----- |
| Tuzilma | Chapda bo'limlar, telefonda tanlash maydoni | KEP kabi; o'nta havola tor ekranni egallardi |
| Manzil | Har bo'lim o'z manzilida (`/settings/<bo'lim>`) | Havolani ulashish va «orqaga» to'g'ri ishlaydi |
| Avatar | Yuklash yoki ulangan hisobdan olish | Tashqi manzilni yozish mumkin emas — kuzatuv |
| Muqova | Qvant do'konidan | Kosmetika allaqachon do'konda (ADR-0002) |
| Parol | Almashtirish va o'rnatish | Ijtimoiy hisobda parol yo'q — uzish uchun kerak |
| Pochta | Yangi manzil kod bilan tasdiqlangach | Tasdiqlanmagan manzil tiklash kanaliga aylanardi |
| Taxallus | Yiliga bir marta bepul, keyin 500 Qvant | Standings va havolalar taxallusga bog'langan |
| Sessiyalar | Ro'yxat va birma-bir uzish | Parol almashganda boshqa qurilmalar yopiladi |
| Ma'lumot | Mamlakat, viloyat, maktab, sinf, sayt | Global platforma; O'zbekistonda viloyat ro'yxatdan |
| Maxfiylik | Standart holatda ochiq (pochtadan tashqari), har maydon yashiriladi | Foydalanuvchi tanlovi; pochta — quyida |
| Tug'ilgan sana | To'liq sana | Yosh toifalari va olimpiada saralashi uchun |
| Profil | Hammaga ochiq | Reyting platformasida profil — vitrina |
| Ko'nikmalar | 0–100 slayder, o'zini baholash | KEP kabi; reytingga ta'sir qilmaydi |
| Texnologiyalar | Tayyor ro'yxat, belgilar bilan | `simple-icons` (CC0), erkin matn emas |
| Karyera | Ta'lim va ish tajribasi | KEP kabi |
| Tashqi profillar | Codeforces, AtCoder, LeetCode, LinkedIn | Reyting ochiq API'dan, bizning reytingga aralashmaydi |
| Bildirishnomalar | Sayt va Telegram, tur bo'yicha | Pochta keyinroq |
| Ko'rinish | Hisobda saqlanadi, ovoz va effekt bilan | Boshqa qurilmadan kirganda ham shunday |
| Jamoalar | Hozir quriladi | 10 kishigacha, kod yoki havola bilan |
| Profil bo'limlari | Faoliyat, yutuqlar, xaridlar, obunachilar | Profil faqat raqam emas, tarix ham |

## Oqibatlar

- **Maxfiylik.** Ma'lumot standart holatda ochiq, pochta esa yopiq:
  mavjud o'n mingdan ortiq hisob pochtasini «ommaviy profilda
  ko'rinmaydi» sharti bilan bergan. Birinchi deployda bu yo'q edi va
  pochta hammaga ochilib qoldi — migratsiya uni barcha mavjud hisoblarda
  yopdi. Ochish — egasining ongli tanlovi (sozlamalar → Ma'lumotlar).
- **Taxallus.** Eski nom 90 kun boshqaga berilmaydi va yangi profilga
  yo'naltiradi: aks holda yangi egasi eski egasining obro'si bilan
  standings'da tura olardi. Pullik almashtirish ledger orqali
  (`ref_type=username_change`), bepul muddatni qayta boshlamaydi.
- **Pochta.** Kod YANGI manzilga boradi; tasdiqlangach eski manzilga
  «pochta almashtirildi» xati yuboriladi. Xatda parolni tiklash tavsiya
  etilmaydi — hisobni egallagan odam eski egasiga tiklash havolasini
  ham o'zi olib qo'ygan bo'lardi.
- **Avatar.** Rasm MinIO'da, API orqali o'zgarmas nom bilan beriladi va
  abadiy keshlanadi. Provayder rasmi ham yuklab olinib qayta
  joylashtiriladi; faqat ruxsat etilgan domenlardan (SSRF).
- **Telegram.** Bot odamga faqat ruxsat bergan bo'lsa yoza oladi —
  vidjet endi yozish ruxsatini so'raydi. Standart holatda Telegram
  kanali o'chiq: so'ramasdan yozadigan bot spamga aylanardi.
- **Hisobni o'chirish.** Profil qatorlari, obunalar, ijtimoiy
  bog'lanishlar va eski taxalluslar o'chadi; jamoa esa qoladi — egalik
  eng eski a'zoga o'tadi. Ijtimoiy bog'lanish qolsa, o'sha provayder
  bilan qaytgan odam yangi hisob ocha olmasdi.
- **Router.** Taxallusda nuqta bo'lishi mumkin (`ali.valiyev`);
  standart `[^/.]+` qolipi uni kesib, profilni 404 qilardi.

## Rad etilgan variantlar

- **Taxallusni istalgancha bepul almashtirish** — standings va
  havolalar buziladi, eski nomni boshqa odam egallaydi.
- **Profil standart holatda yopiq** — foydalanuvchi ochiqni tanladi.
- **Avatar uchun ixtiyoriy tashqi manzil** — har profil ko'rilishi
  uchinchi tomonga bildirilardi.
- **Ko'nikmani yechimlardan avtomatik hisoblash** — keyinga qoldirildi;
  hozircha KEP kabi o'zini baholash.

## Yangilanish: profil sahifasi (2026-09-11)

robocontest.uz profili tahlil qilindi va 30 savol bo'yicha qaror qabul
qilindi. Ish uch bosqichda: bu bo'lim birinchisini — tuzilma,
statistika va grafiklarni yozadi. Unvon va sertifikat qarorlari alohida
ADR'larda (0018, 0019) bo'ladi.

### Qaror

| Savol | Tanlov | Sabab |
| ----- | ------ | ----- |
| Tuzilma | Chapda profil kartasi, o'ngda reytinglar va tablar; telefonda bitta ustun | Kim ekani doim ko'rinadi, grafiklar keng ustunda |
| Tablar | Har biri o'z manzilida (`/users/<nick>/urinishlar` va h.k.); eski `?tab=` yo'naltiriladi | Havola ulashiladi, «orqaga» ishlaydi, har tabning o'z sarlavhasi |
| Reyting grafigi | To'rt reyting almashtirgich bilan, standart Contests; unvon bantlari; nuqtada musobaqa, o'rin, o'zgarish; ostida sababli jadval | Raqam emas, yo'l ko'rinadi |
| Faollik xaritasi | Kunlik urinish va yangi yechim, yil tanlash, joriy va eng uzun streak | Doimiylik bir qarashda |
| Masalalar xaritasi | Raqam tartibida yoki 7 daraja bo'yicha; katak shu masala urinishlarini ochadi | Arxivdagi o'rni ko'rinadi |
| Tillar, verdiktlar | Kartalar va halqa; infra va muallif xatolari hisobga olinmaydi | Checker yoki judge aybi odamniki emas |
| Mavzu kuchi | `/problems/skills/` hisobi, lekin hammaga ochiq | Bitta formula, ikki joyda |
| Musobaqalar | O'rin oralig'i (33–35), reyting o'zgarishi, hajm, rasmiy/virtual, qidiruv | Natija to'liq, sahifaga o'tmasdan |
| Ochiqlik | Yangi statistikalar hammaga ochiq | «Profil — vitrina» qarori saqlanadi |
| Grafiklar | O'z SVG'imiz, kutubxonasiz | CSP va to'plam hajmi |

### Oqibatlar

- **Kesh.** Og'ir hisoblar (faollik, tillar, verdiktlar, yechilgan va
  urinilgan to'plamlar, mavzular) foydalanuvchi bo'yicha versiyali kalit
  ostida bir soat turadi. Versiya urinish baholangan tranzaksiya commit
  bo'lgach oshadi: ichkarida oshirilsa, parallel so'rov commitgacha
  bo'lgan eski ma'lumotni yangi versiya ostida keshlab qo'yardi.
  Masalalar katalogi hamma uchun bitta, 10 daqiqa.
- **Teng o'rinlar.** `Standing.rank` ketma-ket raqam — teng natija
  alohida belgilanmaydi. Oraliq natijaning o'zidan olinadi: ACM'da
  yechilganlar va jarima, IOI'da ball bir xil bo'lganlar.
- **Grafik nuqtalari.** Bir reytingda 400 tadan ortiq nuqta siqiladi;
  birinchi, oxirgi va eng yuqori nuqta saqlanadi.
- **Izohlar.** Har ko'rsatkich yonida qisqa izoh — Robocontest'dagi
  izohsiz raqamlar takrorlanmasin. Tab qatori telefonda ikki qatorga
  tushmaydi, gorizontal aylanadi.
- **Ulashish.** Web Share, bo'lmasa havola nusxalanadi. OG karta avatar,
  reytinglar va yechilganlar bilan; Satori WebP o'qimaydi, shunday
  avatar o'rniga bosh harf chiziladi.

### Rad etilgan variantlar

- **Chart.js** (Robocontest shuni ishlatadi) — to'plamga o'nlab kilobayt
  qo'shardi, bizning grafiklar esa chiziq va kataklardan iborat.
- **Tablar `?tab=` bilan, bitta sahifada** — sahifa hamma tabning
  ma'lumotini kutardi, sarlavha va havola esa hammasiga bitta bo'lardi.
