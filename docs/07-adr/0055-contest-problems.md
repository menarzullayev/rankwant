# ADR 0055 — Musobaqa masalalari: oldin yopiq, paytida manzil bo'yicha ochiq, keyin arxivda

**STATUS:** accepted (qamrov va tartib); 2–4-qismlarning tafsiloti o'z PR'ida aniqlanadi
**Sana:** 2026-10-08
**Tasdiqlagan:** Saidakbar (owner) — 2026-10-08, 16 savol
**Ta'sir doirasi:** `problems/visibility.py`, `problems/views.py`, `problems/serializers.py`, `judging/`, `contests/services.py`, `contests/serializers.py`, masala va musobaqa sahifalari
**Dalil:** o'lchov 2026-10-08 — kod va jonli baza: 3 musobaqa (uchalasi tugagan demo), ro'yxatdan o'tgan 0, musobaqa urinishi 0

## 1. Muammo

Masala sahifasi faqat `is_public=True` bo'lsa ochilardi va musobaqa
ishtirokchisi uchun istisno yo'q edi. Oqibat:

- musobaqa uchun yozilgan masala **arxivda oldindan ochiq** turishi shart
  edi — aks holda ishtirokchining o'zi ham uni ocholmasdi (404);
- musobaqa sahifasi masalalar ro'yxatini (harf, nom) boshlanishdan oldin
  ham berardi;
- jadval muzlardi, lekin urinishlar lentasi, masalaning statistikasi va
  yechganlar ro'yxati yangilanishda davom etardi — muzlatish yashirgan
  narsani ular aytib berardi;
- musobaqa tugagach masalalar bilan hech narsa bo'lmasdi.

Codeforces, KEP va Robocontest'da masala musobaqa uchun tuziladi,
boshlangach musobaqa ichida ko'rinadi va tugagach arxivga o'tadi.

## 2. Qaror

Yangi maydon yo'q. `is_public=False` — «arxivda emas» degani bo'lib qoladi;
masalaning holati u biriktirilgan musobaqadan o'qiladi.

| Payt | Shart | Yechim yuborish | Ro'yxatlarda |
|---|---|---|---|
| Boshlanguncha | hech kimga (muallif va xodimdan boshqa) | yo'q | yo'q; musobaqa sahifasida faqat **soni** |
| Boshlangach | **hammaga**, mehmonga ham — manzil yoki musobaqa sahifasi orqali | faqat ro'yxatdan o'tganlar, faqat shu musobaqaga | arxiv, qidiruv, sitemap va sonlarda yo'q |
| Tugagach, yakunlanmaguncha | hammaga | yo'q | yo'q |
| Yakunlangach | arxiv masalasi | hamma | bor; ommaviy raqam shu paytda beriladi |

Tasdiqlangan qarorlar:

1. Boshlangach shart hammaga ochiq (Codeforces kabi).
2. Arxivga **yakunlanganda** avtomatik o'tadi (`finalize_contest` — hack
   bosqichi bo'lsa undan keyin, testlar o'zgarishdan to'xtaganda).
3. Boshlanguncha musobaqa sahifasida faqat masalalar soni.
4. Muallif, hakam va sinovchi o'z musobaqasida qatnashadi, lekin
   **reytingsiz** (2-qism).
5. Musobaqa paytida masala faqat musobaqa sahifasi yoki manzil orqali
   topiladi.
6. Yechimni faqat ro'yxatdan o'tganlar yuboradi; musobaqadan tashqari
   yuborish rad etiladi (aks holda javob ikkinchi hisobdan bepul tekshirilardi).
7. Urinishlar muzlatishgacha ochiq; muzlatishdan keyin har kim faqat
   o'zinikini ko'radi. Lenta, bitta urinish sahifasi, masala sonlari,
   statistika va yechganlar ro'yxati — hammasi jadval bilan birga muzlaydi.
8. Boshqaning manba kodi musobaqa yakunlangach, arxiv qoidasi bilan ochiladi.
9. Boshlangandan keyin ham ro'yxatdan o'tish mumkin (tugaguncha).
10. Ommaviy raqam arxivga o'tganda beriladi.
11. Tahlil (editorial) yakunlanguncha yopiq — yechgan odamga ham.
12. Sizib chiqish har bir yuza uchun test bilan isbotlanadi.
13. Savol-javob: savol yopiq, javobni hakam faqat so'raganga yoki hammaga
    e'lon qilib beradi (3-qism).
14. Ko'chirmachilik: hakamga hisobot + hakam tugmasi bilan
    diskvalifikatsiya (4-qism).
15. Reyting ko'chirmachilik tekshiruvini kutmaydi; kimdir chiqarilsa qayta
    hisoblanadi.
16. To'rt alohida PR, ketma-ket: ① ko'rinish, arxivga o'tish va sizib
    chiqish testlari; ② sinovchi roli va reytingsiz qatnashish;
    ③ savol-javob va e'lonlar; ④ ko'chirmachilik.

### 2.1. «Manzil bo'yicha ochiq» nima degani

Masalalarni **sanaydigan yoki ro'yxatlaydigan** hamma joy `is_public` ni
filtrlashda davom etadi. Faqat **bitta** masalani ochadigan joylar
(`problems.visibility.openable`) boshlangan musobaqaning masalasini ham
qabul qiladi: masala sahifasi, statistikasi, yechganlari va yuborish.

### 2.2. Muzlatish

Muzlatish — jadvalniki (`Contest.is_frozen`): yurayotgan musobaqaning
oxirgi `freeze_minutes` daqiqasi. U musobaqa bilan birga tugaydi. Yakunlashgacha
cho'zilmaydi: undan keyin kelishi mumkin bo'lgan hack bosqichi aynan o'sha
urinishlarni ochiq talab qiladi.

### 2.3. Arxivga o'tmaydigan holatlar

`release_problems` masalani ushlab qoladi, agar u hali yakunlanmagan boshqa
musobaqada ham bo'lsa yoki testlari bo'lmasa (arxiv uni hakamlay olmaydi).
Ikkalasi ham logga yoziladi.

## 3. Rad etilgan variantlar

- **Masalada alohida holat maydoni** (`visibility = draft/contest/public`) —
  holat musobaqa vaqtidan kelib chiqadi; maydon uni ikkinchi marta saqlab,
  ikkalasi ajralib ketishi mumkin edi.
- **Vaqt tugashi bilan arxivga** — hack bosqichida testlar hali o'zgaradi.
- **Shartni faqat ro'yxatdan o'tganlarga ochish** — egasi ochiq variantni tanladi.
- **Muzlatishni yakunlashgacha cho'zish** — hack bosqichini buzardi.

## 4. Bu qaror nimani hal qilmaydi

Ko'rinishni yopish «masalani oldindan ko'rib olish»ni yo'q qiladi. Qolganlari
ochiq va shunday deb yoziladi:

- masalani biladigan odamlar (muallif, sinovchi) — 2-qism reytingini oladi,
  bilimini emas;
- ikki hisob va kod almashish — 4-qism aniqlaydi, oldini olmaydi;
- tashqi yordam (sun'iy intellekt, tayyor yechim) — hech narsa;
- boshqa saytdan olingan masala — yashirish foyda bermaydi;
- tugagan musobaqaning virtual ishtirokchisi uchun masala allaqachon arxivda.

## 5. Oqibatlar

- Tugagan, lekin yakunlanmagan musobaqaning masalasiga yechim yuborib
  bo'lmaydi (hack bosqichi kunlab davom etishi mumkin).
- Musobaqa paytida lentada masala nomi o'rnida slug ko'rinadi (nom faqat
  arxiv masalasi uchun beriladi).
- Musobaqa masalasi boshlanguncha qidiruv tizimiga ham, ishtirokchiga ham
  yopiq; tayyorlovchilar uni xodim va tashkilotchi API'si orqali ko'radi.
