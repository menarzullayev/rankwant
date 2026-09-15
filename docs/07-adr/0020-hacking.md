# ADR-0020: Hacking — bitta dvigatel, to'rtta siyosat

**STATUS:** accepted (2026-09-16)
**Ta'siri:** [05-domain-model](../05-domain-model/README.md) 🔒 kengaytiriladi (`Hack`);
[ADR-0011](0011-competition-formats.md) formatlar jadvaliga tegadi;
[ADR-0002](0002-qvant-economy.md) ledger qoidasi o'zgarmaydi

## Muammo

Verdict katalogini raqobatchilar bilan solishtirish paytida ma'lum bo'ldiki,
Codeforces'ning 17 ta verdictidan **faqat bittasi** bizda yo'q: `CHALLENGED`
(UI'da «Hacked»). Qolgan 16 tasi allaqachon mavjud kodlarga to'liq mos
tushadi. Ya'ni yetishmayotgani verdict emas — **funksiya**.

Tadqiqot ikki narsani ko'rsatdi.

**Codeforces'da hacking bitta emas, uchta model:**

| Model | Qachon | Kim | Lock | Ball |
| ----- | ------ | --- | ---- | ---- |
| Div 1/2 ichki | raund davomida | faqat o'z xonasi (~40 kishi) | **ha** | +100 / −50 |
| Ochiq faza (Edu, Div 3/4) | tugagach 12 soat | istalgan tashrifchi | yo'q | **yo'q** |
| Uphacking | ~1 hafta | faqat yuqori divizion | yo'q | yo'q |

Rasmiy qoidalar hujjati ([blog 4088](https://codeforces.com/blog/entry/4088))
faqat **birinchi** modelni tavsiflaydi; ochiq faza esa atigi raund
e'lonlarida va [Educational Rounds e'lonida](https://codeforces.com/blog/entry/21496)
belgilangan. Ya'ni Codeforces'ning o'zida ham yagona normativ spetsifikatsiya
yo'q.

**KEP.uz'da to'rtinchisi bor:** e'lon (blog 89) so'zma-so'z aytadi —
«Added the ability to hack another user's accepted solution». Musobaqaga
bog'lanmagan, amaliyot rejimi.

Product owner qarori: **to'rttasi ham kerak**, chunki kelajakda har xil
musobaqa turi uchun har xil siyosat talab qilinadi.

## Qaror

**Bitta hack dvigateli quriladi, to'rtta model uning siyosati bo'ladi.**
Ular alohida modul emas: umumiy yadro ~80% — `Hack` entity, validator
ijrosi, sandbox yurgizish, test to'plamga o'tkazish, rejudge, manba
ko'rinish qoidasi, bildirishnoma, UI. Farq atigi to'rtta o'lchovda.

| Siyosat | Oyna | Kim hack qiladi | Ball | Jadvalga ta'siri |
| ------- | ---- | --------------- | ---- | ---------------- |
| `contest_room` | musobaqa davomida | o'z xonasi, masalani lock qilgan | +100 / −50 | darhol, jonli |
| `open_phase` | `end_at` → oyna yopilishi | hamma (yechgan bo'lsa) | yo'q | reyting oldidan qayta hisob |
| `practice` | doimiy | yechgan bo'lsa | Qvant | yo'q |
| `uphack` | musobaqadan keyin, uzoq | ishonchli foydalanuvchi | yo'q | **o'zgarmaydi** |

Umumiy tamoyillar:

1. **Siyosat — konfiguratsiya, kod emas.** To'rttasi bitta jadvalda
   e'lon qilinadi; yangi musobaqa turi yangi modul emas, yangi qator
   talab qiladi. Codeforces ham shunday ishlaydi: bitta dvigatel, raund
   turiga qarab siyosat.
2. **Manba ko'rinishi — IKKI shart birga.** Hacker (a) o'sha masalani
   o'zi `AC` qilgan bo'lishi va (b) siyosat oynasi ochiq bo'lishi kerak.
   Bittasi yetarli emas. Hozir manba ikki qatlamda ataylab yopiq:
   urinish detali faqat egaga va adminga ochiladi, solvers ro'yxati esa
   uni ORM darajasida `defer()` qiladi va faqat `code_length` beradi.
   Ikkala qatlam ham saqlanadi, ustiga nuqtali istisno qo'shiladi.
3. **Validator — MAJBURIY darvoza.** Hacker testi avval masalaning
   `Validator` dasturidan o'tadi, keyingina himoyachining kodi ishga
   tushadi. Aks holda cheklovni buzgan kiritma bilan istalgan to'g'ri
   yechimni «sindirish» mumkin bo'lardi. Validatordan o'tmagan test
   **jazolanmaydi** — u shunchaki hisobga olinmaydi (`IGNORED`).
   Sabab: noto'g'ri test arzon, muvaffaqiyatsiz hack qimmat bo'lishi
   kerak — rag'bat shakli aynan shunday.
4. **Hack natijasi va urinish verdicti — ikki xil narsa.** Hack
   urinishining o'z natijasi bor (`SUCCESSFUL`, `UNSUCCESSFUL`,
   `INVALID_INPUT`, `GENERATOR_CRASHED`, `IGNORED`, `TESTING`);
   himoyachining urinishi esa yangi `HACKED` verdictini oladi.
5. **Qvant faqat ledger orqali** ([ADR-0002](0002-qvant-economy.md)) —
   `Reason.HACK` qo'shiladi, balans hech qachon to'g'ridan-to'g'ri
   yozilmaydi.
6. **Reyting faqat masala va musobaqadan** ([ADR-0011](0011-competition-formats.md)
   5-tamoyili buzilmaydi): `practice` va `uphack` reytingga tegmaydi,
   `contest_room` va `open_phase` esa musobaqa orqali ta'sir qiladi.
7. **Ochiq faza reytingdan OLDIN yopiladi.** Muvaffaqiyatli hack testi
   asosiy to'plamga qo'shiladi, barcha `AC` qayta tekshiriladi, keyin
   reyting qo'llanadi — aks holda reyting bekor qilingan yechimlar
   ustiga hisoblanardi.

## Rad etilgan variantlar

- **To'rtta mustaqil modul.** Bir xil mantiq to'rt joyda turib jimgina
  ajralib ketardi. Shu naqsh repo'da allaqachon zarar keltirgan:
  `runner-keepalive.ps1` va `runner_keepalive.ps1` bir-biriga zid
  strategiya bilan yonma-yon yashagan va biri ikkinchisini ko'rmay
  dublikat jarayon ochib yuborardi.
- **Faqat bitta siyosat (ochiq faza) qurish.** Arzonroq, lekin siyosat
  qatlamining shakli faqat ikkinchi siyosat paydo bo'lganda tekshiriladi;
  keyinroq qo'shish qayta yozishga olib kelardi.
- **Manbani doimiy ochiq qilish.** Eng sodda, lekin yechim —
  foydalanuvchining mehnati, va launchdan keyin uni qaytarib yopib
  bo'lmaydi.
- **Verdictlarni funksiyasiz qo'shish.** Dastlabki taklif `CHALLENGED` ni
  shunchaki katalogga qo'shish edi. Rad etildi: hech kim chiqarmaydigan
  verdict — o'lik kod, ustiga har bir kod 10 tilga yorliq va ikonka
  talab qiladi.

## Oqibatlar

- **05-domain-model** 🔒 ga `Hack` entity qo'shiladi: hacker, himoyachi
  urinishi, masala, siyosat, test havolasi (S3/R2), natija, vaqt.
  Konventsiya bo'yicha `created_at`/`updated_at` va o'chirilmaslik
  qoidasi amal qiladi.
- **24-verdict:** `Verdict.HACKED`. Bu `tools/check_verdict_codes.py`
  talab qiladigan to'rt qadamni majburiy qiladi — ikonka, `verdict.ts`
  yozuvi, regeneratsiya va **10 tilga yorliq**; parity tekshiruvi
  ularsiz qizaradi.
- **`TestCase`** ga hack manbasini belgilaydigan maydon kerak; testlar
  DB'da emas, S3/R2 da saqlanadi, ya'ni hacker testi obyekt xotirasiga
  yuklanadi.
- **Judge protokoliga validator bosqichi** qo'shiladi. Hozir `Validator`
  modeli mavjud va KEP importi uni to'ldiradi, lekin uni ishga
  tushiradigan yo'l yo'q — ya'ni darvoza e'lon qilingan, hali jonsiz.
- **`contests.finalize_due` o'zgaradi.** Hozir u `end_at` dan keyin
  darhol reyting qo'llaydi (`ratings_applied_at__isnull=True`). Ochiq
  faza aynan shu ikkisi orasiga tushadi, ya'ni vazifa hack oynasi
  yopilishini kutishi shart.
- **Yangi beat vazifasi** `hacks.close_due` (60 s, mavjud
  `*.finalize_due` naqshi bilan bir xil): oyna yopiladi → testlar
  qo'shiladi → rejudge → reyting.
- **`QvantTransaction.Reason.HACK`** qo'shiladi (`max_length=16` ga
  sig'adi).
- **Cheklov.** Codeforces'da hack urinishlariga rasmiy tezlik cheklovi
  **hujjatlashtirilmagan** va bu amalda muammo bergan (bitta foydalanuvchi
  bir raundda 470 ta hack qilgani muhokama qilingan). Bizda mavjud
  `THROTTLE_SUBMIT` naqshi takrorlanadi: alohida `hack` tezligi va
  limitdan oshganda jim 429 emas, ko'rinadigan yozuv — `RATE_LIMITED`
  pretsedenti bo'yicha.
- **Xona (room)** tushunchasi hozir yo'q; u faqat `contest_room` siyosati
  uchun kerak va o'sha siyosat bilan birga qo'shiladi.
