# ADR-0015: Hisob xatlari — brendlangan shablon, kuzatuvsiz, kod + havola

**STATUS:** accepted (2026-09-10)
**Ta'siri:** `core.mailer` zanjiri ([08-technical-spec](../08-technical-spec/README.md)),
parolni tiklash va emailni tasdiqlash oqimlari

## Muammo

Zanjir qurildi va to'rt provayder ulandi, lekin xatning O'ZI haqida hech
qanday qaror yo'q edi: nima yuboriladi, qanday ko'rinadi, qaysi tilda,
qancha yashaydi, kim suiiste'mol qila oladi.

Bu savollarni keyinga qoldirib bo'lmaydi, chunki ular bir-biriga bog'liq:
kuzatuv yoqilgan bo'lsa havola provayder domeniga almashadi va xat
fishingga o'xshab qoladi; dark mode o'ylanmasa matn o'qib bo'lmaydi;
muddat uzun bo'lsa o'g'irlangan pochta hisobni beradi.

## Qaror

### Qamrov

Hozircha **faqat hisob xavfsizligi**: parolni tiklash, emailni
tasdiqlash, notanish qurilmadan kirish ogohlantirishi. Musobaqa, reyting,
ijtimoiy va digest xatlari platforma daromad keltira boshlagach.

Sabab: bepul zanjir kuniga ~600 xat ko'taradi va bu miqdorni birinchi
navbatda **hisobni tiklab bo'lmaslik** muammosiga sarflash kerak — qolgan
xatlar qulaylik, bu esa yagona yo'l.

### Ko'rinish

| Nima | Qaror |
| ---- | ----- |
| Uslub | To'liq brendlangan shablon |
| Logotip | Rasm (yasaladi) + matn zaxira |
| Palitra | Sayt asosiy ko'ki — `#5b8cff`, tugma `#4470e6` |
| Rejim | Yorug' va qorong'i — ikkalasi ham |
| Tuzilma | Kulrang fonda 600px oq kartochka |
| Jo'natuvchi | `RankWant <no-reply@…>` — bitta manzil |
| Til | `User.locale` bo'yicha uz / ru / en |
| Ohang | Xolis va qisqa, salomlashuvsiz |
| Mavzu | `RankWant — <harakat>` |
| Footer | Minimal: nega keldi + sayt manzili |

### Xavfsizlik

**Kuzatuv butunlay o'chiriladi** — na click tracking, na piksel. Sabab
pedagogik: foydalanuvchi havolada `rankwant` so'zini ko'rishi va
ko'rmasa shubhalanishi kerak. Provayder domeniga almashgan havola aynan
fishing xatiga o'xshaydi va biz odamni o'sha ko'rinishga o'rgatib
qo'yardik.

**Havola + 6 xonali kod.** Ikkalasi ham **1 soat** yashaydi va **bir
martalik**. Kod qurilmalar aralashganda (pochta telefonda, brauzer
kompyuterda) va korporativ filtr havolani buzganda yo'l qoldiradi.

**Kontekst ko'rsatiladi:** so'rov vaqti, IP va brauzer. Foydalanuvchi
«bu men emasman» degan xulosaga o'zi kelishi uchun.

**Cheklov:** hisobga 3/soat, IP'ga 10/soat. IP chegarasi kengroq, chunki
maktab sinfi bitta IP ortida bo'ladi ([10-operations](../10-operations/README.md)
dagi ochiq risk).

**DMARC bosqichma-bosqich:** hozir `p=none` va hisobot yig'iladi, 2–4
haftadan keyin `quarantine`, so'ng `reject`. Birdan `reject` qo'yish
noto'g'ri sozlangan subdomen xatlarini jimgina yo'q qilardi.

### Zanjir yiqilganda

Qayta urinish (1, 5, 15 daqiqa) + staff kanaliga ogohlantirish.

Kod ekranda **faqat emailni tasdiqlashda** ko'rsatiladi — u yerda
foydalanuvchi allaqachon tizimga kirgan, ya'ni kod unga hech narsa yangi
oshkor qilmaydi. **Parolni tiklashda ko'rsatilmaydi:** so'rovchi anonim
va kodni ekranda berish har kimga istalgan hisobni ochib berardi.
Hujumchi kvotani ataylab tugatib, «nosozlik rejimi» ni o'zi chaqira
olardi — ya'ni bu zaxira yo'l emas, doimiy teshik bo'lardi.

### Staff yordami

Staff panelida «Tiklash havolasini yaratish» — havola ekranda chiqadi va
staff uni foydalanuvchiga Telegram orqali beradi. Staff parolni ko'rmaydi
va o'zgartirmaydi.

### Sinov

Ikki bosqich: `/staff/email-preview` da hamma shablon × 3 til ×
yorug'/qorong'i, so'ng haqiqiy pochtalarga (Gmail, mail.ru, Outlook)
`send_test_email` bilan yuborish. Brauzer email mijozi emas — Gmail CSS
ning yarmini olib tashlaydi, shuning uchun ikkinchi bosqich shart.

## Rad etilgan variantlar

- **Faqat matn (plain text).** Yetkazish eng yuqori, lekin brendlangan
  xat qarori bilan zid va tugmasiz tiklash havolasi yalang'och URL
  bo'lib qolardi.
- **Har maqsadga alohida jo'natuvchi manzili** (`hisob@`, `musobaqa@`).
  Filtrlash qulay bo'lardi, lekin hozir bitta xat turi bor va har manzil
  alohida sozlanishi kerak.
- **Faqat o'zbekcha.** Arxiv KEP'dan kelgan va u yerda rus tilli
  auditoriya bor.
- **Kod mavzu qatorida.** Eng qulay, lekin kod qulflangan ekrandagi
  bildirishnomada ham ko'rinardi.
- **24 soatlik havola.** Qulayroq, lekin o'g'irlangan pochta bir kun
  davomida hisobni berardi.

## Bog'liq hujjatlar

- [08-technical-spec](../08-technical-spec/README.md) — zanjir, subdomenlar, tuzoqlar
- [ADR-0008](0008-auth-session-plus-pat.md) — session + PAT
- [10-operations](../10-operations/README.md) — NAT ortidagi sinflar
