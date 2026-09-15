# Verdikt turlari — hozirgi holat, raqobatchilar va takliflar

**STATUS:** qaror qabul qilindi (2026-09-10)

> **Qabul qilingan qarorlar.** Yorliqlar TO'LIQ tarjima qilinadi (kod
> API va bazada `AC`/`WA` bo'lib qoladi, faqat ko'rinadigan nom
> tarjima). To'rtala «o'lik» verdikt ham ulanadi. Ikkita yangi verdikt
> qo'shiladi: `WRONG_TEST` va `RE` ni `RE_SIGNAL`/`RE_EXIT` ga ajratish.
> `PE` haqiqatan ishlatiladi. Quyidagi tahlil o'sha qarorlarning asosi.

Savol uchta edi: bizda nima bor, boshqalarda nima bor, va yana nimani
qo'shish mantiqli. Quyidagi raqamlar jonli bazadan va koddan olingan.

---

## 1. Bizda hozir nima bor

`apps/api/judging/verdicts.py` da **20 ta** kod e'lon qilingan. Lekin
e'lon qilinish bilan ishlatilish bir narsa emas — o'lchandim:

| Verdikt               | Judge chiqara oladimi | Kodda yoziladimi  | Bazada uchraydi |
| --------------------- | --------------------- | ----------------- | --------------- |
| `PENDING`             | —                     | ha (submit)       | 0               |
| `RUNNING`             | —                     | ha                | 0               |
| `AC`                  | ha                    | ha                | 106 557         |
| `WA`                  | ha                    | ha                | 173 229         |
| `TLE`                 | ha                    | ha                | 77 604          |
| `MLE`                 | ha                    | ha                | 0               |
| `OLE`                 | ha                    | ha                | 0               |
| `RE`                  | ha                    | ha                | 18 163          |
| `CE`                  | ha                    | ha                | 8 977           |
| `PE`                  | **yo'q**              | 7 joyda (checker) | 0               |
| `PARTIAL`             | ha                    | ha                | 0               |
| `IE`                  | ha                    | ha                | 1               |
| `COMPILE_TIMEOUT`     | ha                    | ha                | 0               |
| `IDLENESS`            | ha                    | ha                | 0               |
| `SECURITY_VIOLATION`  | ha                    | ha                | 0               |
| `CHECKER_ERROR`       | ha                    | ha                | 0               |
| `SKIPPED`             | yo'q                  | **hech qayerda**  | 0               |
| `TESTING_ABORTED`     | yo'q                  | **hech qayerda**  | 0               |
| `RATE_LIMITED`        | yo'q                  | **hech qayerda**  | 0               |
| `DENIAL_OF_JUDGEMENT` | yo'q                  | **hech qayerda**  | 0               |

**Topilma 1 — to'rtta verdikt o'lik.** `SKIPPED`, `TESTING_ABORTED`,
`RATE_LIMITED`, `DENIAL_OF_JUDGEMENT` e'lon qilingan, web'da yorlig'i va
rangi ham bor, lekin ularni **hech qanday kod yozmaydi**. Ular kelajak
uchun rejalashtirilgan bo'lishi mumkin — quyida har biriga taklif bor.

**Topilma 2 — bazadagi nollar aldamchi.** `MLE`, `OLE`, `IDLENESS`,
`SECURITY_VIOLATION` bazada 0 marta uchraydi, lekin bu ular ishlamaydi
degani emas: judge ularni chiqara oladi va bake-off'ning 05/08/04/09–13
case'lari buni har ishga tushirishda tasdiqlaydi. Bazada 0 bo'lishining
sababi — mavjud urinishlarning deyarli hammasi **seed** qilingan
(384 569 tadan bittasi haqiqatan sudlangan).

**Topilma 3 — verdikt yorliqlari tarjima qilinmagan.**
`apps/web/src/components/VerdictBadge.tsx` da 20 ta yorliq **qattiq
yozilgan**: «Navbatda», «Tekshirilmoqda», «Qisman ball», «Xavfsizlik
buzildi», «Ichki xato». Ular `i18n` tizimidan o'tmaydi, ya'ni rus yoki
ingliz tilini tanlagan foydalanuvchi ham o'zbekcha matn ko'radi. Bu 10
tilli ishning ochiq qolgan qismi.

---

## 2. Raqobatchilarda nima bor

### Codeforces (17 qiymat, API `verdict` enum)

`OK`, `FAILED`, `PARTIAL`, `COMPILATION_ERROR`, `RUNTIME_ERROR`,
`WRONG_ANSWER`, `PRESENTATION_ERROR`, `TIME_LIMIT_EXCEEDED`,
`MEMORY_LIMIT_EXCEEDED`, `IDLENESS_LIMIT_EXCEEDED`, `SECURITY_VIOLATED`,
`CRASHED`, `INPUT_PREPARATION_CRASHED`, `CHALLENGED`, `SKIPPED`,
`TESTING`, `REJECTED`.

Bizda yo'q uchtasi diqqatga sazovor:

- **`CHALLENGED`** — hack qilingan yechim. Codeforces Div. 1/2 formatida
  qatnashchi boshqaning yechimini sindirishi mumkin; verdikt shu paytda
  qo'yiladi. Bu band **yopildi**: [ADR-0020](../07-adr/0020-hacking.md)
  hacking'ni qo'shdi, kod esa `HACKED` deb ataldi — foydalanuvchi bu
  funksiyani «hack» so'zi bilan biladi, «challenge» bilan emas.
- **`INPUT_PREPARATION_CRASHED`** — test **generatori** yiqilgan. Bu
  `CHECKER_ERROR` dan farq qiladi: checker javobni tekshiradi, generator
  esa testni yasaydi. Ikkalasini bir kodga yig'ish muallifni noto'g'ri
  joyga qaratadi.
- **`REJECTED`** — moderatsiya qarori (plagiat, qoida buzilishi). Bizning
  `SKIPPED` bilan qisman kesishadi.

### DMOJ (8 kod)

`AC`, `WA`, `IR`, `RTE`, `OLE`, `MLE`, `TLE`, `IE`.

Bitta muhim farq: **`IR` (Invalid Return) va `RTE` (Runtime Exception)
ajratilgan**. `IR` — dastur nolga teng bo'lmagan kod bilan chiqdi;
`RTE` — segfault, nolga bo'lish, xotira ajratish xatosi. Bizda ikkalasi
ham `RE`. Bu C++ o'rganayotgan o'quvchi uchun sezilarli farq: «kodim
`return 1` qildi» va «kodim segfault berdi» — butunlay boshqa xatolar.

DMOJ yana bir narsani hujjatlashtirgan: bitta testga bir nechta kod
tegishli bo'lsa, **ustuvorlik** bo'yicha bittasi ko'rsatiladi. Bizda
bunday tartib yozilmagan.

### AtCoder (10 kod)

`AC`, `WA`, `TLE`, `MLE`, `RE`, `CE`, `OLE`, `IE`, `WJ` (Waiting for
Judging), `WR` (Waiting for Re-judging).

Diqqat: **`WR` — qayta tekshirish navbati** alohida holat sifatida
ko'rsatiladi. Bizda rejudge endi bor (`manage.py rejudge`), lekin u
verdiktni `PENDING` ga qaytaradi — foydalanuvchi uchun bu yangi
yuborishdan farq qilmaydi.

### LeetCode (7 kod)

`Accepted`, `Wrong Answer`, `Time Limit Exceeded`,
`Memory Limit Exceeded`, `Output Limit Exceeded`, `Compile Error`,
`Runtime Error`.

Eng qisqa ro'yxat. LeetCode intervyuga tayyorlaydi, olimpiadaga emas —
`PE`, `IDLENESS`, `PARTIAL` kabi olimpiada tushunchalari unga kerak emas.

### RoboContest (O'zbekiston)

Verdikt ro'yxatini olib bo'lmadi: sayt JavaScript bilan chiziladi va
ochiq hujjati yo'q. Buni **qo'lda tekshirish kerak** — bizning to'g'ridan-
to'g'ri raqobatchimiz va foydalanuvchilar u yerdan keladi, ya'ni ular
o'rgangan atamalar muhim.

### Qisqa taqqoslash

|                 | RankWant        | Codeforces | DMOJ   | AtCoder | LeetCode |
| --------------- | --------------- | ---------- | ------ | ------- | -------- |
| Jami kod        | **20**          | 17         | 8      | 10      | 7        |
| `PARTIAL` (IOI) | ha              | ha         | —      | —       | —        |
| `PE`            | ha (ishlamaydi) | ha         | —      | —       | —        |
| `IDLENESS`      | ha              | ha         | —      | —       | —        |
| Xavfsizlik      | ha              | ha         | —      | —       | —        |
| `RE` ajratilgan | yo'q            | yo'q       | **ha** | yo'q    | yo'q     |
| Hack/challenge  | —               | ha         | —      | —       | —        |
| Rejudge holati  | —               | —          | —      | **ha**  | —        |

**Xulosa:** bizning ro'yxatimiz allaqachon eng uzuni. Muammo kamlik
emas — **to'rttasi o'lik va yorliqlar tarjima qilinmagan**.

---

## 3. Qo'shish mumkin bo'lgan verdiktlar

Har bir taklif uchun: nima uchun, kim ko'radi, va qancha ish.

### A. O'lik to'rttasini tiriltirish (yangi kod kerak emas)

| Verdikt               | Qachon qo'yiladi                          | Nega kerak                                                                                                                |
| --------------------- | ----------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| `TESTING_ABORTED`     | rejudge boshlanganda eski natija o'rniga  | Hozir rejudge verdiktni `PENDING` ga qaytaradi — foydalanuvchi buni yangi yuborish deb o'ylaydi                           |
| `DENIAL_OF_JUDGEMENT` | `reap_stuck` ish yo'qolganini aniqlaganda | Hozir u `IE` qo'yadi; `IE` esa masala sozlamasi xatosini ham bildiradi. Ikkalasini ajratish operatorga aniq signal beradi |
| `RATE_LIMITED`        | submit shifti urilganda                   | Hozir 429 HTTP kodi qaytadi va urinish umuman yozilmaydi — foydalanuvchi tarixida iz qolmaydi                             |
| `SKIPPED`             | plagiat/qoida buzilishi aniqlanganda      | Anti-plagiat hali yo'q; bu verdikt o'sha ish qilinganda kerak bo'ladi                                                     |

### B. Yangi takliflar

**1. `RE` ni ikkiga ajratish (DMOJ modeli) — tavsiya qilinadi**

`RE_SIGNAL` (segfault, nolga bo'lish, abort) va `RE_EXIT`
(nolga teng bo'lmagan qaytish kodi). Judge allaqachon `exit_code` va
signalni biladi — ma'lumot bor, faqat ajratilmagan.

_Kim ko'radi:_ C++ o'rganayotgan o'quvchi. «Massivdan chiqib ketdim» va
«`return 1` yozib qo'ydim» — butunlay boshqa tuzatish.

**2. `WRONG_TEST` / `INPUT_PREPARATION_CRASHED` — tavsiya qilinadi**

Masala **muallifi** aybdor bo'lgan holat: test fayli buzuq, generator
yiqilgan, kutilgan javob yo'q. Hozir bu `IE` yoki `CHECKER_ERROR` ga
qo'shilib ketadi.

_Nega muhim:_ bizda import qilingan 2 096 masaladan **870 tasida test
yo'q** (o'lchandi) va ular hozir `IE` qaytaradi — ya'ni foydalanuvchi
platforma buzilgan deb o'ylaydi, aslida masala tayyor emas.

**3. `PE` ni haqiqatan ishlatish yoki olib tashlash**

`PE` e'lon qilingan, web'da yorlig'i bor, checker kodida 7 joyda
uchraydi — lekin judge uni hech qachon chiqarmaydi. Ikki yo'l:
(a) `standard` checker uchun «faqat bo'shliq farqi» holatini aniqlab
`PE` qaytarish, (b) verdiktni olib tashlash. Yarim holat eng yomoni.

**4. `QUEUED_LONG` / navbat holati — ehtiyotkorlik bilan**

AtCoder `WJ`/`WR` ni ajratadi. Bizda `PENDING` ikkalasini ham bildiradi.
Musobaqa paytida navbat uzayganda foydalanuvchi «tizim qotdimi yoki
navbatmi?» deb o'ylaydi. Lekin bu verdikt emas, **holat** — uni
verdiktlar ro'yxatiga qo'shish o'rniga `Attempt` ga navbat pozitsiyasini
qo'shish to'g'riroq bo'lishi mumkin.

**5. Verdikt ustuvorligini yozib qo'yish — kod emas, hujjat**

DMOJ buni hujjatlashtirgan: bitta yuborishda bir nechta test har xil
verdikt bersa, qaysi biri ko'rsatiladi. Bizda amalda birinchi
muvaffaqiyatsiz test g'olib chiqadi, lekin bu qoida hech qayerda
yozilmagan.

---

## 4. Tavsiya etilgan tartib

1. **Yorliqlarni tarjima qilish** — 20 ta yorliq × 10 til. Kod
   o'zgarishi kichik, foydasi darhol. Bu yangi verdikt emas, mavjudini
   ishlatib bo'ladigan holatga keltirish.
2. **`TESTING_ABORTED` va `DENIAL_OF_JUDGEMENT` ni ulash** — ikkalasi
   ham allaqachon e'lon qilingan, ulanadigan joyi aniq (`rejudge`,
   `reap_stuck`), va operatorga real signal beradi.
3. **`WRONG_TEST`** — 870 ta testsiz masala shuni talab qilyapti.
4. **`RE` ni ajratish** — o'rganuvchi uchun eng katta foyda, lekin
   judge protokoli o'zgaradi (`services/bakeoff/protocol.md`).
5. **`PE` bo'yicha qaror** — ishlatish yoki olib tashlash.
6. **`SKIPPED`** — anti-plagiat ishi bilan birga.
7. ~~**`CHALLENGED`**~~ — bajarildi: `HACKED` ([ADR-0020](../07-adr/0020-hacking.md)).

Ochiq savol: **RoboContest atamalarini qo'lda tekshirish**. Foydalanuvchi
u yerdan kelsa, o'rgangan so'zi bilan bizniki mos kelishi ma'qul.

---

## Manbalar

- [Codeforces API verdict enum](https://rami-sabbagh.com/Codeforces-API/com/github/rami_sabbagh/codeforces/api/enums/Verdict.html)
- [Codeforces — Denial of Judgement](https://codeforces.com/blog/entry/128139) ·
  [Skipped](https://codeforces.com/blog/entry/74203) ·
  [Idleness limit](https://codeforces.com/blog/entry/14878)
- [DMOJ status codes](https://dmoj.readthedocs.io/en/latest/judge/status_codes/)
- [AtCoder glossary](https://atcoder.jp/contests/abc139/glossary)
- [e-olymp — how submissions are tested](https://blog.e-olymp.com/en/posts/online-judging/)
