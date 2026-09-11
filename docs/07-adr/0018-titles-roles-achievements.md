# ADR-0018: Unvon, ism rangi, rollar, onlayn holat va yutuqlar

**STATUS:** accepted (2026-09-11)
**Ta'siri:** [ADR-0002](0002-qvant-economy.md) (Qvant ledgeri),
[ADR-0006](0006-rating-model.md) (Contests reytingi),
[ADR-0017](0017-profile-and-settings.md) (profil sahifasi)

## Muammo

Profil raqamlarni ko'rsatardi, lekin odamning darajasi bir qarashda
ko'rinmasdi — robocontest.uz va Codeforces'da bu vazifani unvon va ism
rangi bajaradi. Kim masala muallifi, kim hakam, kim yaqinda g'olib
bo'lgani, odam hozir saytdami — bularning birortasi ko'rinmasdi.
Yutuqlar esa faqat «bajarildi / bajarilmadi» edi: darajasi, noyobligi va
mukofoti yo'q.

## Qaror

### Unvon zinapoyasi

| Pog'ona | Kod | Contests reytingi |
| ------- | --- | ----------------- |
| 1 | kvark | 1200 dan past |
| 2 | foton | 1200–1399 |
| 3 | elektron | 1400–1599 |
| 4 | proton | 1600–1799 |
| 5 | atom | 1800–1999 |
| 6 | molekula | 2000–2199 |
| 7 | kristal | 2200–2399 |
| 8 | yulduz | 2400–2699 |
| 9 | galaktika | 2700 va yuqori |

- Faqat Contests reytingidan (ADR-0006): Skills yechilgan masalalar
  hajmini, Activity faollikni o'lchaydi — musobaqadagi kuchni emas.
- Boshlang'ich reyting 1400 (`User.rating_contest`) — 3-pog'ona boshi.
  Birinchi musobaqadan keyin odam ikki pog'ona pastga ham, yuqoriga ham
  siljiy oladi.
- Reytingli musobaqasiz odam unvonsiz (`rated_contest_count = 0`):
  boshlang'ich 1400 hali hech narsa aytmaydi.
- Kod va chegara `profiles/titles.py` da, nom esa i18n'da (`title.<kod>`).
  Unvon mavzusi almashtirilsa faqat tarjimalar o'zgaradi.

### Ism rangi

- Ism unvon rangida yoziladi: profil, reyting jadvali, standings,
  urinishlar, jamoa, obunachilar. API foydalanuvchi obyektida `title`,
  standings va urinish qatorida `user_title` beradi — u yerda `title`
  masala yoki musobaqa nomi bilan adashtirilardi.
- Rang `--rw-rank-1…9` tokenlaridan, 18 palitraning har birida alohida:
  ton bir xil, yorug'lik esa shu palitraning eng yomon foniga nisbatan
  4.5:1 dan o'tadigan eng yorqin qiymat. `tools/check_contrast.py` ularni
  matn zinapoyasi bilan birga tekshiradi. Galaktika qalin yoziladi — 8 va
  9-pog'ona tonlari yaqin.

### Ramka

Do'kondan olingan ramka kiyilgan bo'lsa — u, bo'lmasa unvon ramkasi
(unvon rangida). Unvonsiz odamda ramka yo'q.

### Rollar

| Rol | Manba |
| --- | ----- |
| Xodim | `User.is_staff` |
| Masala muallifi | kamida bitta ommaviy masala (`Problem.author`) |
| Hakam | `Contest.jury`, admin paneldan |
| Chempion | oxirgi 365 kunda reytingli ommaviy musobaqada birinchi natija |

Chempion: virtual ishtirok va virtual musobaqa hisoblanmaydi.
`Standing.rank` ketma-ket raqam, shuning uchun birinchi bilan TENG natija
ham g'olib; hech narsa yechmagan «birinchi» esa chempion emas.

### Onlayn holat

- `UserSession.last_seen` dan — hamma qurilmalar bo'yicha eng oxirgisi. U
  har besh daqiqada yoziladi, «onlayn» oynasi — o'n daqiqa.
- Maxfiylikda alohida maydon (`online`), standart holatda ochiq;
  yashirilsa faqat egasiga ko'rinadi.
- Nisbiy vaqt serverda, tanlangan tilda (`Intl.RelativeTimeFormat`,
  Node'ning to'liq ICU'si) — Robocontest'da lotin interfeysida ham
  kirillcha chiqqan nisbiy vaqt takrorlanmaydi.

### Yutuqlar

| Yutuq | Daraja |
| ----- | ------ |
| 1 / 10 / 100 / 500 / 1000 masala | bronza / bronza / kumush / oltin / oltin |
| 7 / 30 / 365 kunlik streak | bronza / kumush / oltin |
| 1 / 10 / 50 reytingli musobaqa | bronza / kumush / oltin |
| Profil to'ldirilgan | bronza |

- Qo'lga kiritilgani `UserAchievement` jadvalida: qachon va qancha Qvant.
- Noyoblik — egalari faol foydalanuvchilarning necha foizi.
- Egasi uchtasini tanlaydi — profil kartasida turadi.
- Qvant: bronza 10, kumush 30, oltin 75 — faqat YANGI yutuq uchun, bir
  marta va faqat ledger orqali (`reason=achievement`). Streak va profil
  yutuqlarining Qvant'i quest orqali beriladi — bu yerda qayta berilmaydi.

## Oqibatlar

- **Nega quest emas.** Activity reytingi 30 kundagi HAR bajarilgan questni
  sanaydi (`qvant.services.activity_inputs`). Yutuq quest bo'lsa, tarixiy
  yutuqlarni tiklash hammaning Activity reytingini sun'iy oshirardi.
- **Tarixiy yutuqlar** migratsiyada Qvant'siz tiklandi (`awarded=0`). Sana
  iloji boricha haqiqiy: N-masala — N-yechim vaqti, N-musobaqa —
  N-reytingli musobaqa hisoblangan vaqt, streak va profil — quest vaqti.
- **Rejudge.** Yechilganlar soni bosqichdan tushsa, masala yutug'i olib
  tashlanadi va Qvant'i qaytariladi (ADR-0002 «rejudge da qaytarish»).
  Streak yutug'i tegilmaydi — streakning o'zi ham tegilmaydi.
- **Kunlik shift.** Yutuq Qvant'i kunlik 100 Qvant shiftiga bo'ysunadi,
  `profile_complete` questi kabi. Kam berilgan bo'lsa ham yutuq olingan
  hisoblanadi.
- **Katta musobaqa.** Musobaqa yutug'i sanog'i `rated_contest_count`:
  bosqichdan faqat sanoq unga TENG bo'lganda o'tiladi, ya'ni o'n ming
  ishtirokchining ko'pchiligi uchun so'rov ham yo'q.

## Rad etilgan variantlar

- **Unvon Skills reytingidan** — Skills hajmni o'lchaydi, kuchni emas.
- **Hamma uslub uchun bitta rang to'plami** — och va to'q fonda bir
  vaqtda 4.5:1 dan o'tadigan ton kulrangga yaqin bo'ladi, pog'onalar
  farqlanmay qolardi.
- **Yutuq quest sifatida** — yuqoridagi Activity sababi.
- **Rejudge'da yutuqni qoldirish** — ADR-0002 qaytarishni talab qiladi.
