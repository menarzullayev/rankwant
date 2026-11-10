# ADR 0055 — Musobaqa masalalari: oldin yopiq, paytida manzil bo'yicha ochiq, keyin arxivda

**STATUS:** accepted (qamrov va tartib); 2-qism — § 6; 3-qism — § 7; 4-qismning tafsiloti o'z PR'ida aniqlanadi
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

## 6. 2-qism: sinovchi va reytingsiz qatnashish (2026-11-10)

**Tasdiqlagan:** Saidakbar (owner) — 2026-11-10, 4 savol, prototip
(`prototypes/contest-insiders.html`); to'rttasida ham tavsiya tanlandi.
**O'lchov:** production'da 3 musobaqa (uchalasi demo), ro'yxatdan o'tgan 0,
hakam 0, tashkilotchi 0, masala muallifi (M2M) 0 — ya'ni hammasi noldan.

### 6.1. Kim «ichkarida»

Masalalarni boshlanishdan oldin biladigan to'rt rol — `contests.insiders`:

| Rol | Manba |
|---|---|
| muallif | musobaqa masalalarining `Problem.authors` va `Problem.author` |
| sinovchi | yangi `Contest.testers` (M2M) |
| hakam | `Contest.jury` |
| tashkilotchi | `Contest.organizers` |

Bir odam bir necha rolda bo'lsa, shu tartibda birinchisi aytiladi.
Barcha xodimlar ataylab kirmaydi: aks holda egasi va har xodim hech bir
reytingli musobaqada reyting ololmasdi.

### 6.2. Sinovchi boshlanishdan oldin

- Masalalarni ochadi (`visibility.openable_q(user=...)`) va yechim yuboradi —
  ro'yxatdan o'tmasdan.
- **Sinov urinishi** — musobaqaga boshlanishidan oldin yuborilgan urinish.
  U hakamlanadi va hech qayerda sanalmaydi: jadvalda, «yechilgan» hisobida,
  Skills reytingida, masalaning `attempt_count`, statistikasi va yechganlar
  ro'yxatida yo'q.
- Musobaqa tugaguncha uni faqat muallifi (va xodim) ko'radi — lenta va
  bitta urinish sahifasi muzlatish bilan bir xil qoida orqali
  (`testing_windows`).
- Boshqalar uchun hech narsa o'zgarmaydi: musobaqa sahifasi masalalar
  sonini aytadi, masala sahifasi 404.

### 6.3. Reytingsiz qatnashish

- Ichkaridagi odam ro'yxatdan o'tib qatnasha oladi. Jadvalda u **«*» bilan,
  o'rinsiz** turadi (`Standing.insider_role`, `rank = 0`); rasmiy o'rinlar
  faqat rasmiylar orasida sanaladi, jadval `Standing.position` bo'yicha.
- Reyting, sertifikat, Qvant (+30), yutuqlar, «chempion» nishoni va
  chempionat bali — faqat `Standing.objects.official()`. Rasmiy minimum
  (10 ishtirokchi) ham ularsiz sanaladi.
- Uning sinov urinishlari musobaqa jadvaliga kirmaydi; musobaqa paytidagi
  urinishlari kiradi (reytingsiz qatorda).

### 6.4. Ommaga

- Musobaqa sahifasida doim «Musobaqani tayyorlaganlar»: mualliflar,
  sinovchilar, hakamlar (nofaol import akkauntlari chiqarilmaydi).
- Profilda «Sinovchi» nishoni (ADR-0018 dagi «Hakam» kabi).
- Sinovchi qilib qo'shilgan odamga bildirishnoma (`contest_tester`).
- Sinovchilarni xodim (admin panel) va tashkilotchi (`contests/mine/`)
  tayinlaydi; hakamni faqat xodim.

### 6.5. Yo'lda topilgan

Saytda musobaqaga **ro'yxatdan o'tish tugmasi yo'q edi**: API bor edi,
web uni hech qayerda chaqirmasdi — masala sahifasidagi «Musobaqa sahifasi»
kartasi odamni tugmasiz sahifaga olib borardi. Endi musobaqa sahifasida
ishtirok bloki bor.

### 6.6. Hal qilinmagan

- Sinovchi musobaqa **nashr qilingandan keyin** ishlaydi (`is_public=True`):
  qoralama musobaqa sinovchiga ham yopiq.
- Sinovchining mulohazasi uchun alohida kanal yo'q (3-qism — savol-javob).
- `start_at` musobaqa boshlangandan keyin kechroqqa surilsa, undan oldingi
  urinishlar «sinov» bo'lib qoladi — bunday surish o'zi xato amal.

## 7. 3-qism: savol-javob va e'lonlar (2026-11-10)

**Tasdiqlagan:** Saidakbar (owner) — 2026-11-10, 4 savol, prototip
(`prototypes/contest-clarifications.html`). Bitta savolda tavsiyadan farq
qildi: savolni **har qanday kirgan foydalanuvchi** beradi (tavsiya — faqat
ro'yxatdan o'tgan ishtirokchi edi). Qo'shimchalarning to'rttasi ham tanlandi.

| Qaror | Tafsilot |
|---|---|
| Kim so'raydi | har qanday kirgan foydalanuvchi, musobaqa tugaguncha; masala bo'yicha savol — faqat boshlangandan keyin (oldin masalalar yopiq, faqat «umumiy») |
| Kim javob beradi va e'lon yozadi | hakam, tashkilotchi, staff-ops (`can_moderate`) |
| Yopiqlik | savol — muallifi va moderatorlarniki; javob muallifga yoki «hammaga» |
| Yetkazish | bildirishnoma (mavjud SSE; Telegram — sozlamaga ko'ra) + musobaqa sahifasidagi «Savol-javob» bloki, e'lonlar tepada |
| Tez javoblar | Ha / Yo'q / Shartni o'qing / Izoh yo'q — **kod** bo'lib saqlanadi, har o'quvchi o'z tilida o'qiydi |
| Chegaralar | bir kishiga musobaqada 20 savol, 1000 belgi, daqiqasiga bitta (`429` + `Retry-After`) |
| Hakamga xabar | har yangi savolda hakam va tashkilotchilarga; ular yo'q bo'lsa staff-ops'ga |
| Yakunlangach | javob berilgan barcha savollar hammaga ochiq; so'raganning ismi hech qachon ommaga chiqmaydi |

Model — `contests.Clarification`: savol, javob va e'lon bitta jadvalda (e'lon
— muallifsiz, savolsiz, ommaviy qator). Endpoint'lar:
`GET/POST contests/<slug>/clarifications/`,
`POST contests/<slug>/clarifications/<id>/answer/`,
`POST contests/<slug>/announcements/`. Bildirishnoma kodlari:
`contest_question`, `contest_answer`, `contest_announcement`
(`ref_type = contest_qa` → sahifaning `#clarifications` qismi).

### 7.1. Hal qilinmagan

- 200 dan ortiq qabul qiluvchili e'lon qo'ng'iroqqa darhol emas, keyingi
  so'rovda (60 s) yetadi — mavjud `announce` qoidasi.
- Sahifadagi blok musobaqa davomida 30 s da qayta o'qiladi (SSE emas).
- Savolni tahrirlash yoki o'chirish yo'q; javobni o'zgartirish — qayta
  javob berish bilan.

