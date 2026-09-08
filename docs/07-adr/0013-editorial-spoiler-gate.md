# ADR-0013: Yechim tahlili — spoyler darvozasi, paywall emas

**STATUS:** accepted (2026-09-09)
**Ta'siri:** [ADR-0002](0002-qvant-economy.md) 🔒 dagi «Kontent ochish — hozir emas» qatori

## Muammo

Yechim tahlili masala sahifasida ochiq turibdi. Bu ikki tomonlama zarar:

- **O'quvchi uchun.** Qiyin masalada tugma bosish tahlilni ochadi. Tahlil
  o'qilgach masala yechilmaydi — u faqat KO'CHIRILADI. Mashqning butun
  qiymati o'sha «qiynalgan yarim soat» ichida edi.
- **Qvant uchun.** [ADR-0002](0002-qvant-economy.md) da sink ro'yxati atigi
  to'rtta narsadan iborat va o'sha ADR ning o'zi «sink quriydi» ni xavf
  deb yozgan: to'rtta kosmetika ~3 oyda sotib olinadi, keyin valyuta
  ma'nosini yo'qotadi.

ADR-0002 kontent ochishni rad etmagan — «[ADR-0005](0005-content-strategy-own-content.md)
ziddiyati» deb keyinga qoldirgan. Ziddiyat aniq: o'z o'zbek kontenti
bizning ustunligimiz, uni pul devori ortiga qo'yish o'sha ustunlikni
yo'qotadi.

## Qaror

Tahlil **pul devori ortida emas, spoyler darvozasi ortida** turadi.

| Kim | Tahlilga kirish |
| --- | --------------- |
| Masalani yechgan | **bepul**, darhol |
| Staff | bepul |
| Yechmagan | `editorial_price` Qvant (standart 30) |
| Mehmon | ko'rinmaydi — avval kirish kerak |

Bitta ochish abadiy (`EditorialUnlock`), tranzaksiya odatdagi ledger orqali
(`reason=purchase`, `ref_type=editorial`).

## Sabab

Bu paywall EMAS, chunki **bepul yo'l har doim ochiq va u asosiy yo'l**:
masalani yech — tahlil o'zi ochiladi. Qvant faqat **sabrsizlikni** sotib
oladi, kontentni emas. ADR-0005 ustunligi «kontent bor» degani; u
yechgan har bir odam uchun bepul qolgani uchun ustunlik saqlanadi.

Ikkinchi foyda — narx pedagogik signal: 30 Qvant ~ bir kunlik emissiya,
ya'ni «bugungi mehnating». Bu «bepul tugma» dan ancha kuchli to'siq va
aynan shu to'siq kerak edi.

## Oqibatlar

- `Problem.editorial_price` qo'shiladi (0 = bepul). Import KEP dagi
  `solutionKepcoinValue` ni shu maydonga tushiradi.
- `ProblemDetailSerializer` tahlil MATNINI ochilmagan holda umuman
  yubormaydi — «frontendda yashirish» spoylerni himoya qilmaydi, matn
  baribir HTML da kelardi.
- ADR-0002 sink jadvaliga beshinchi qator qo'shiladi va u **takroriy**:
  har masala alohida. «Sink quriydi» xavfi shu bilan yopiladi.
- Activity reyting o'zgarmaydi — ADR-0002: formulada balans yo'q.

## Muqobillar

- **Hammaga ochiq qoldirish** — hozirgi holat; mashq qiymatini yo'qotadi.
- **Faqat yechganlarga, Qvantsiz** — spoylerni himoya qiladi, lekin
  yechishga urinib, taqalib qolgan odamga chiqish yo'li qoldirmaydi.
- **Obuna ortida** — narx modeli hali yo'q (ADR-0002), va bu haqiqiy
  paywall bo'lardi.
