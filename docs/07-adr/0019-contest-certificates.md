# ADR-0019: Musobaqa sertifikatlari

**STATUS:** accepted (2026-09-11)
**Ta'siri:** [ADR-0011](0011-competition-formats.md) (musobaqa formatlari),
[ADR-0017](0017-profile-and-settings.md) (profil sahifasi),
[ADR-0018](0018-titles-roles-achievements.md) (yutuqlar)

## Muammo

Robocontest ishtirokchiga QR va ID bilan sertifikat beradi — maktab,
olimpiada tanlovi yoki rezyume uchun hujjat. RankWant'da natija faqat
standings'da edi: uni boshqa joyga olib borib, haqiqiyligini isbotlab
bo'lmasdi.

## Qaror

| Savol | Tanlov | Sabab |
| ----- | ------ | ----- |
| Kimga | Rasmiy (ommaviy, virtual emas) musobaqada kamida bitta yechim yuborgan har ishtirokchiga | Qatnashgani ham hujjat; yubormagan odam qatnashmagan |
| Qachon | Musobaqa yakunlanganda (`finalize_contest`), avtomatik | Qo'lda berish unutiladi |
| Dizayn | 1, 2, 3-o'rin (oltin, kumush, bronza), eng yaxshi 10%, ishtirokchi | G'olib va kuchlilar alohida ko'rinsin |
| O'rin | Teng natija bitta o'rinni bo'lishadi (33–35 → 33-o'rin) | Standings ketma-ket raqam beradi, sertifikat esa adolatli bo'lsin |
| Tekshirish | Noyob UUID; QR `/sertifikat/<id>` sahifasiga olib keladi | ID taxmin qilinmaydi, QR telefonda bir zumda ochiladi |
| Format | PDF (A4, yotiq), fpdf2 + segno | Chop etiladigan hujjat; ikkala kutubxona toza Python |
| Ism | Berilgan paytdagi ism saqlanadi | Keyin ism o'zgarsa ham hujjat o'zgarmaydi |

## Oqibatlar

- **Bog'liqliklar.** fpdf2 (Pillow, fontTools, defusedxml bilan) va segno
  production'da ham kerak — `requirements.txt` va lock'ga qo'shildi.
  Faqat dev muhitda qolib ketgan paket deployda migrate bosqichini
  yiqitgan edi (`requests` hodisasi).
- **Shrift repoda.** DejaVu Sans (`contests/fonts`, litsenziyasi bilan):
  production image'da tizim shriftlari yo'q, ism esa lotin yoki kirill
  yozuvida bo'lishi mumkin. Xitoycha ism glifi DejaVu'da yo'q.
- **QR rasm emas.** Modul-modul to'rtburchak bo'lib chiziladi: rasm
  kutubxonasi kerak emas va chop etilganda ham aniq chiqadi.
- **PDF bir kun keshlanadi** — hujjat o'zgarmaydi, chizish esa har safar
  shriftni qayta o'qiydi.
- **Oldingi musobaqalar** uchun bir martalik buyruq:
  `python manage.py issue_certificates` (takroriy ishga tushirish xavfsiz).
- **Hisob o'chirilsa** sertifikat ham o'chadi va tekshirish sahifasi 404
  beradi — shaxsiy ma'lumot qolmaydi.
- **Nol natija** medal olmaydi: hech narsa yechmagan «birinchi» ishtirokchi
  sertifikati bo'ladi.

## Rad etilgan variantlar

- **Faqat g'oliblarga** — foydalanuvchi hammaga berishni tanladi: ishtirok
  ham o'quvchi uchun hujjat.
- **WeasyPrint (HTML → PDF)** — tizim kutubxonalari (Pango, Cairo) kerak,
  production image og'irlashardi.
- **ReportLab** — ishlaydi, lekin fpdf2 + segno kichikroq va Unicode
  shriftni to'g'ridan-to'g'ri qabul qiladi.
- **Ketma-ket raqamli ID** — boshqalarning sertifikatini sanab chiqish
  mumkin bo'lardi.
