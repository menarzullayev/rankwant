# ADR-0016: Ro'yxatdan o'tish va kirish — uch maydon, uch provayder

**STATUS:** accepted (2026-09-10) — forma qarori kuchda; **sahifa tuzilishi 2026-09-15 da yangilandi**: uchta alohida sahifa o'rniga bitta sahifa, uch bo'lim (`/login?tab=...`). Tafsilot: «Yangilanish» bo'limi.
**Ta'siri:** [ADR-0008](0008-auth-session-plus-pat.md) (session + PAT),
[ADR-0015](0015-account-email.md) (hisob xatlari)

## Muammo

Kirish sahifamiz uchta maydondan iborat va boshqa hech narsasi yo'q:
parol qoidalari aytilmaydi, parolni ko'rish imkoni yo'q, va **bugun
qurilgan tiklash oqimiga UI'dan yo'l yo'q** — «parolni unutdingizmi»
havolasi umuman qo'yilmagan.

Uchta raqobatchi o'lchandi (2026-09-10):

| | RoboContest | kep.uz | AtCoder | RankWant |
| - | ----------- | ------ | ------- | -------- |
| Ro'yxat maydonlari | **11** | OAuth + 2 | 5 majburiy + 3 ixtiyoriy | 3 |
| Kaskadli tanlovlar | 2 | — | — | — |
| Ijtimoiy kirish | — | Google, GitHub | — | — |
| Qoidalar oldindan | — | — | **ha** | — |
| Parolni ko'rsatish | ha | ha | — | — |
| «Parolni unutdingizmi» | ha | — | ha | **—** |

Har biridan bitta xulosa:

- **RoboContest** viloyat→tuman va muassasa→sinf so'raydi. Bu ortiqchalik
  emas, **savdolashuv**: kirish to'sig'i baland, evaziga maktab va viloyat
  reytinglari hamda olimpiada saralashi mumkin bo'ladi.
- **kep.uz** OAuth ni yuqoriga qo'ygan — eng past to'siq. Lekin KIRISH
  sahifasidagi tugmada «Signup with Google» yozilgan: qaytib kelgan
  foydalanuvchi uchun chalkash.
- **AtCoder** qoidalarni yozishdan OLDIN aytadi va majburiy/ixtiyoriy
  maydonlarni vizual ajratadi. Uchtasining eng kuchli namunasi:
  **aytilgan qoidani buzib bo'lmaydi.**

## Qaror

### Forma

| Nima | Qaror |
| ---- | ----- |
| Maydonlar | **3 ta** — taxallus, email, parol |
| Viloyat/maktab | so'ralmaydi; keyin, kerak bo'lgan joyda |
| Sahifalar | `/login` va `/register` — **alohida** |
| Parol | tasdiqlash maydoni **va** ko'rsatish tugmasi |
| Qoidalar | maydon tagida, yozishdan **oldin** (AtCoder namunasi) |
| Tiklash | kirish sahifasida havola — busiz oqim yopiq qolardi |
| Keyin qayerga | bosh sahifaga |

### Yangilanish (2026-09-15) — sahifa tuzilishi

Yuqoridagi jadval **asl qaror** sifatida saqlanadi; quyidagi ikki qatori
amalda boshqacha qurildi. Bu ADR rad etgan «bitta sahifada tab'lar»
varianti keyinchalik AYNAN qabul qilindi.

| Qator | Asl qaror | Amaldagi holat |
| ----- | --------- | -------------- |
| Sahifalar | `/login` va `/register` — alohida | bitta karta, uch bo'lim: `login`, `register`, `reset-password` |
| Tiklash | kirish sahifasida havola | bo'lim (`?tab=reset-password`); havola kirish formasida qoladi |

O'lchangan holat:

- `/register` va `/reset-password` — sahifa emas, **307 yo'naltirish**:
  `apps/web/src/app/register/page.tsx` va `.../reset-password/page.tsx`
  `redirect('/login?tab=...')` qiladi. 307 ataylab: `next.config.ts` dagi
  301 qoidasi `?token=` va `?next=` ni tashlab yuborardi va xatdagi
  havola ishlamay qolardi.
- Haqiqiy sahifa — `apps/web/src/app/login/page.tsx`, bo'limlar ro'yxati
  bitta manbada: `apps/web/src/lib/auth-tabs.ts`.
- Qatorda ikki bo'lim ko'rinadi (`AuthTabs.tsx`); `reset-password`
  haqiqiy bo'lim bo'lib qolaveradi, lekin qatorga chiqarilmaydi — 10
  tildan 9 tasida yozuv kesilardi (o'lchov `auth-tabs.ts` izohida).
- `/kirish` degan manzil **yo'q** — bunday yo'l hech qachon qurilmagan.

**API o'zgarmadi.** Backend'da endpointlar avvalgidek alohida:
`auth/register/`, `auth/login/`, `auth/password-reset/`,
`auth/password-reset/confirm/` (`apps/api/core/urls.py`). O'zgarish faqat
frontend manzillarida.

### Parol qoidalari

Kamida 8 belgi; faqat raqamdan iborat bo'lmasin; taxallus yoki emailga
o'xshamasin; ommaviy parollar ro'yxatida bo'lmasin. **Tarkib majburiyati
yo'q** (harf + raqam + belgi talab qilinmaydi) — NIST aynan shuni tavsiya
qiladi, chunki bunday qoida odamni `Parol1!` yozishga majbur qiladi va
haqiqiy kuch qo'shmaydi. Hozirgi Django validatorlari shu, farqi —
**endi ular ko'rsatiladi**.

### Taxallus

Kirill, lotin, raqam, `_` va `.`. Bo'sh joy yo'q. O'zbekcha maxsus
harflar yo'q: lotinda `U+02BB` (`o'` va `g'` dagi belgi), kirillda
`U+045E`, `U+049B`, `U+0493`, `U+04B3`. Uzunligi 3–20.

**Skelet yagonaligi.** Ikki alifboda ko'zga bir xil ko'rinadigan, lekin
kompyuter uchun butunlay boshqa harflar bor. Ular bu yerda ataylab kod
nuqtasi bilan yoziladi — belgining o'zi bilan yozilsa, farqni ko'rib
bo'lmasdi:

| Lotin | Kirill | Ekranda |
| ----- | ------ | ------- |
| `U+0061` | `U+0430` | ikkalasi ham `a` |
| `U+0065` | `U+0435` | ikkalasi ham `e` |
| `U+006F` | `U+043E` | ikkalasi ham `o` |
| `U+0070` | `U+0440` | ikkalasi ham `p` |
| `U+0063` | `U+0441` | ikkalasi ham `c` |
| `U+0078` | `U+0445` | ikkalasi ham `x` |

Ularsiz kimdir `admin` ning birinchi harfini `U+0430` ga almashtirib,
standings'da mavjud odamga **aynan o'xshash** nom olardi. Shuning uchun
yagonalik ikki darajada: registrsiz (allaqachon bor) **va** o'xshash
harflar bir shaklga keltirilgan skelet bo'yicha. To'liq kirillcha yozilgan
ism bemalol ochiladi; mavjud nomga taqlid qiluvchi aralash yozuv rad
etiladi.

### Ijtimoiy kirish

Google, GitHub, Telegram — uchalasi, **formadan keyin**. Kalit
sozlanmagan provayder tugmasi ko'rinmaydi (email zanjiridagi qoida).

**Email to'qnashuvi:** OAuth bergan email allaqachon parolli hisobda
bo'lsa — **parol so'raladi, keyin bog'lanadi**. Avtomatik bog'lash
xavfli: emailni tasdiqlash majburiy emas, ya'ni kimdir begona manzilni
yozib hisob ochsa, o'sha manzilning haqiqiy egasi Google orqali kirib
**begona** hisobni egallab olardi. Parolni unutgan bo'lsa tiklash
oqimiga yuboriladi — u tayyor.

### Emailni tasdiqlash

**Hech qachon majburiy emas.** Tasdiqlanmagan manzil bilan hamma narsa
ishlaydi, profilda faqat eslatma turadi. Lekin **tiklash xati faqat
tasdiqlangan manzilga** yuboriladi — ya'ni sabab bor, to'siq yo'q.

### Hujjatlar

`/shartlar` va `/maxfiylik` yoziladi. Bu shunchaki rasmiyat emas:
**Google OAuth tasdig'i maxfiylik siyosati manzilisiz berilmaydi.**
Hisobni o'chirish va ma'lumot eksporti allaqachon qurilgan
([ADR-0015](0015-account-email.md) yonidagi ish), ya'ni yozadigan
haqiqiy mazmun bor.

## Rad etilgan variantlar

- **RoboContest kabi 11 maydon.** Maktab reytingi qimmatli, lekin uni
  ro'yxatdan o'tish paytida emas, kerak bo'lgan joyda so'rash mumkin.
- **Bitta sahifada tab'lar** yoki **aqlli bitta maydon.** Birinchisi
  2026-09-15 da QABUL QILINDI (yuqoridagi «Yangilanish» bo'limi) — rad
  etish sababi faqat ikkinchisiga tegishli bo'lib chiqdi. Ikkinchisi
  «bu email ro'yxatdan o'tganmi» ma'lumotini oshkor qiladi — biz uni
  tiklash endpointida ataylab yopgandik.
- **Avtomatik OAuth bog'lash.** Yuqorida — hisob egallash yo'li.
- **Parol tarkibi majburiyati.** Tanish, lekin kuch qo'shmaydi.
- **Ro'yxatdan keyin tanishtiruv.** Yana bir to'siq bo'lardi.

## Bog'liq hujjatlar

- [ADR-0008](0008-auth-session-plus-pat.md) — session + PAT
- [ADR-0015](0015-account-email.md) — hisob xatlari, tiklash oqimi
