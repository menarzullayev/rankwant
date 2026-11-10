# ADR 0057 — To'lov: tariflar, kurs xaridi, Click va Payme

**STATUS:** accepted (to'lov modeli, tariflar, provayderlar, qaytarish, yoqish)
**Sana:** 2026-11-10
**Tasdiqlagan:** Saidakbar (owner) — 2026-11-10, ikki bosqichda 8 savol
**Ta'sir doirasi:** yangi `apps/api/billing/` ilovasi; `courses` (pullik kursga kirish), `core.User.plan`; web `/plans`, `/checkout`, `/billing/return`, kurs sahifasi
**Dalil:** Robocontest tariflari va to'lov oqimi jonli brauzerda o'rganildi (2026-11-10, egasining Judge hisobi bilan; hech narsa sotib olinmadi) — [tahlil](../research/2026-11-10-robocontest-tariffs/README.md); Payme Merchant API va Click SHOP-API rasmiy hujjatlari o'qildi

## 1. Muammo

ADR-0056 pullik kurs va uchta tarifni (Plus / Pro / Judge) e'lon qilgan,
lekin to'lov yo'q edi: pullik kurs `402 course_payment_required` qaytarardi,
`User.plan` maydoni ADR-0024 dan beri bor, lekin uni hech narsa yozmasdi.

## 2. Qarorlar (egasi, 2026-11-10)

1. **Davrga bir martalik to'lov** — 1, 6 yoki 12 oy oldindan; avtomatik
   uzaytirish yo'q, karta saqlanmaydi. Xuddi shu tarif qayta olinsa davr
   joriy davrdan keyin qo'shiladi; pastroq tarif joriy yuqori tarif
   tugagach boshlanadi; yuqoriroq tarif darhol boshlanadi (pastrog'ining
   qolgan kunlari yo'qolmaydi).
2. **Click va Payme bitta PR'da** — ikkalasi test rejimida; merchant
   ma'lumotlari YaTT yoki MChJ ochilgach keladi.
3. **Pro barcha pullik kurslarni ochadi**, Judge Pro'ni o'z ichiga oladi;
   har pullik kurs alohida ham sotiladi (bir martalik, muddatsiz).
4. **Qvant pulga bog'lanmaydi** — sotilmaydi va tarif uchun to'lov emas
   (ADR-0002 ledger o'zgarmaydi).
5. **To'rt tarif chiqadi** — Bepul, Plus, Pro, Judge. Plus va Judge ning
   kurslardan tashqari imkoniyatlari xodim admin'da yozadigan matn; kodda
   kafolatlangan yagona huquq — pullik kurslar (Pro, Judge).
6. **Narxlarni xodim admin'da qo'yadi** — har tarif uchun 1/6/12 oy narxi va
   chizilgan eski narx; narx qo'yilmagan davr sotilmaydi; kurs narxi
   kursning o'zida (`Course.price_uzs`).
7. **Alohida `billing` bayrog'i, o'chiq** — merchant kalitlari va oferta
   tayyor bo'lguncha sahifalar ko'rinmaydi; kalitsiz provayder taklif
   qilinmaydi (API 503).
8. **Qaytarishda huquq darhol bekor bo'ladi** — obuna to'xtaydi, sotib
   olingan kurs yopiladi (dars progressi va berilgan sertifikat qoladi).

## 3. Qanday qurildi

- `billing.Order` — to'lanadigan narsa (tarif davri yoki kurs), summa
  yaratilganda muzlatiladi. `Subscription` — bitta to'langan davr.
  `PaymeTransaction` va `ClickTransaction` — har provayderning o'z yozuvi
  (tiyin va millisekund / so'm va kasr).
- Huquq faqat ikki joyda o'zgaradi: `services.fulfil` va `services.revoke`.
  Ikkala provayder ham shularni chaqiradi.
- Kurslar `billing` ni import qilmaydi: `billing` tarifni `User.plan` /
  `plan_expires_at` ga yozadi (`sync_user_plan`), `courses/access.py` esa
  muddatni har o'qishda tekshiradi, ya'ni tugagan tarif davriy sinxronni
  kutmasdan kursni yopadi. Tarif orqali yozilish `Enrollment.Source.PLAN`,
  xarid — `PURCHASE`.
- **Payme** (`/api/v1/billing/payme/`): JSON-RPC 2.0, Basic auth kalit bilan,
  har javob HTTP 200; oltita metod; tranzaksiya 12 soatdan keyin bekor
  (reason 4) — bekor qilish commit qilinadi va keyin -31008 qaytariladi;
  takroriy Create / Perform / Cancel birinchi javobni qaytaradi; bir
  martalik hisobda kutilayotgan tranzaksiya bo'lsa -31008 (sandbox talabi).
- **Click** (`/api/v1/billing/click/`, Prepare va Complete bitta URL):
  MD5 imzo, xatolar -1…-9; Complete'dagi manfiy `error` buyurtmani bekor
  qiladi va -9 qaytaradi; takroriy Complete -4. Click qaytarishi qayta
  chaqiruv yubormaydi — xodim admin'da «revoke» amali bilan belgilaydi.
- Davriy vazifalar: `billing.sync_plans` (10 daqiqa), `billing.expire_orders`
  (soatiga: Payme 12 soati, to'lanmagan buyurtma 24 soati).

## 4. Ochiq qolganlar

- Oferta matni (yurist, MChJ/YaTT) — to'lov yoqilishidan oldin shart.
- Merchant kalitlari, Payme sandbox sinovi va Click test xizmati — egasi.
- Click reversal (Merchant API) avtomatlashtirilmagan.
- Plus va Judge ning kurslardan tashqari imkoniyatlari — matn admin'da,
  funksiyalar alohida qarorlar bilan quriladi.
- To'lov kvitansiyasi bildirishnomasi va fiskal chek (`detail`) — keyin.
