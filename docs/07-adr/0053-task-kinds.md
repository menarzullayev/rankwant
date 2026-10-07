# ADR 0053 — Masala turlari: funksiya, faqat javob, ikki bosqichli, SQL

**STATUS:** accepted (qamrov va tartib); har turning tafsiloti o'z PR'ida aniqlanadi
**Sana:** 2026-10-07
**Tasdiqlagan:** Saidakbar (owner) — 2026-10-07, to'rt savol: «to'rt turning hammasi», «eng mashhur 10 til», «10 MB, 50 fayl», prototip chizildi
**Ta'sir doirasi:** `problems/models.py`, `problems/evaluation.py`, `judging/`, `services/judge-go/`, `services/bakeoff/protocol.md`, `apps/web` yuborish paneli
**Dalil:** o'lchov 2026-10-07 — production'da 2096 masalaning hammasi `standard`; `io_mode`: 2095 `stdio`, 1 `both`. Boshqa platformalar: CMS (Batch, OutputOnly, Communication, TwoSteps), Kattis (pass-fail, scoring, interactive, multi-pass, submit-answer), Codeforces (interactive, run-twice, grader, output-only), HackerEarth (SQL)

## 1. Muammo

Bugun masala bitta shaklda yechiladi: yechuvchi **butun dasturni** yuboradi,
u testlarda yuritiladi. Ikki maydon buni sozlaydi va ikkalasi boshqa savolga
javob beradi:

- `io_mode` (`stdio` / `both`) — dastur javobni **qayerga** yozadi;
- `checker_type` (`standard` / `special` / `interactive` / `scorer`) —
  javobni **kim** baholaydi.

«Nima yuboriladi va u qanday yuritiladi» degan savolga maydon yo'q, chunki
javob hozir bitta. To'rt yangi tur aynan shu savolga boshqa javob beradi.

## 2. Variantlar

1. **Yangi maydon `Problem.task_kind`** — uchinchi, mustaqil o'q.
2. `checker_type` ga yangi qiymatlar qo'shish — rad etildi: «funksiya»
   masalasi ham maxsus checker'li bo'lishi mumkin, ya'ni ikki xossa bitta
   maydonda to'qnashadi (2026-10-07 dagi `both` + checker nuqsonining sinfi).
3. `io_mode` ga qo'shish — rad etildi: bu turlarning hech biri kirish/chiqish
   rejimi emas.

## 3. Tanlov

**Variant 1.** `task_kind`, standart qiymati `program` (bugungi xatti-harakat;
mavjud 2096 masalaga tegilmaydi):

| `task_kind` | Yechuvchi yuboradi | Judge qiladi |
| --- | --- | --- |
| `program` | butun dastur | bugungidek |
| `function` | faqat funksiya (yoki sinf) | muallifning hakam dasturi bilan birga kompilyatsiya qiladi, keyin bugungidek |
| `answer` | javob fayllari (zip) | kod yuritilmaydi; har fayl uchun checker |
| `two_pass` | butun dastur | ikki marta yuritadi; orasida muallif dasturi 1-yurish chiqishidan 2-yurish kirishini yasaydi |
| `sql` | bitta so'rov | har testga toza baza; natija jadvali etalon bilan solishtiriladi |

Ruxsat etilgan birikmalar (qolgani saqlashda, tayyorlik tekshiruvida va nashr
darvozasida rad etiladi — `problems/evaluation.py`, `EVALUATION_MODE_INVALID`):

| `task_kind` | `io_mode` | `checker_type` |
| --- | --- | --- |
| `program` | `stdio`, `both` | bugungi qoidalar |
| `function` | `stdio` | `standard`, `special`, `scorer` |
| `answer` | — (`stdio` saqlanadi) | `special`, `scorer` |
| `two_pass` | `stdio` | `standard`, `special` |
| `sql` | — (`stdio` saqlanadi) | `standard` (jadval solishtiruvi) |

Qaror qilingan tafsilotlar:

- **Funksiya turi 10 tilda boshlanadi:** C++, C, Python (PyPy o'sha qolip
  bilan), Java, Kotlin, C#, JavaScript, TypeScript, Go, Rust. Tanlov umumiy
  tarqalganlik bo'yicha: production'dagi 1116 urinish sinov trafigi (tillar
  bo'yicha deyarli teng taqsimlangan), ya'ni undan xulosa chiqmaydi. Masala
  muallifi shu o'ntadan istalganicha til uchun hakam dasturi beradi; masala
  faqat o'sha tillarda ochiladi.
- **Faqat javob:** zip eng ko'pi 10 MB va 50 fayl; yuborilmagan test uchun
  oldingi eng yaxshi natija saqlanadi.
- **SQL:** PostgreSQL, faqat o'qish, tarmoqsiz; alohida sandbox — judge
  privilegiya modeli (ADR-0046) va chegara bayonoti shu PR'da yangilanadi.

## 4. Sabab

- Uch o'q ortogonal qoladi: har biri bitta savolga javob beradi va yaroqsiz
  birikma bitta joyda rad etiladi.
- Standart qiymat mavjud masalalarni o'zgartirmaydi: migratsiya faqat ustun
  qo'shadi.
- `TwoSteps` (CMS) **olinmaydi**: CMS hujjatining o'zi uni ommaviy musobaqaga
  tayyor emas deydi.

## 5. Oqibatlar

- Yetkazish tartibi — **to'rt alohida PR**, har biri mustaqil deploy
  qilinadi: ① `task_kind` + `function`; ② `answer`; ③ `two_pass`; ④ `sql`.
- Har tur 2026-10-07 dagi uslubda isbotlanadi: etalon masala
  (`problems/reference_problems.py`), kutilgan hukmlar jadvali va haqiqiy
  judge'da yurish (`tests/evaluation/`); isbotsiz tur ochilmaydi.
- Judge shartnomasi (`services/bakeoff/protocol.md`) har PR'da kengayadi:
  `job.task` bloki. `judge-py` yangilanmaydi (bake-off nomzodi).
- `docs/05-domain-model` (qulflangan) dagi `checker_type` qatori eskirgan —
  unda `scorer` yo'q. Model hujjati shu ADR va ADR-0052 orqali o'qiladi;
  hujjatni yangilash alohida, egasi tasdiqlaydigan ish.

### Ma'lum chegaralar

- `function`: hakam dasturi yechim bilan bitta jarayonda — yechim uning
  xotirasini o'qiy oladi. IOI ham shu chegara bilan yashaydi; maxfiy javob
  hakam dasturida saqlanmaydi (javobni checker tekshiradi).
- `answer`: urinish bugun faqat matn saqlaydi; fayllar uchun saqlash joyi
  (S3) va saqlash muddati shu PR'da belgilanadi.
- `sql`: bu yangi auditoriya va yangi xavfsizlik chegarasi — eng oxirgi va
  eng katta ish; boshlanishidan oldin o'lchov bilan qayta ko'riladi.

## 6. Amalga oshirishda aniqlangani (2026-10-07)

To'rt tur ham shu kuni yetkazildi; ikki joyda yechim shu hujjatdagidan farq qildi.

- **`sql` — PostgreSQL emas, SQLite.** So'rov mavjud sandbox ichida, Python'ning
  `sqlite3` moduli bilan, xotiradagi bazada bajariladi (o'lchandi: judge
  obrazida Python 3.13.5, SQLite 3.46.1 — oyna funksiyalari va rekursiv CTE
  ishlaydi). Sabab: har testga PostgreSQL serveri — platformaning o'z bazasi
  turgan mashinada yangi, imtiyozli sirt (ADR-0046, tahdid modeli A-1); SQLite
  esa judge'ga bitta qator ham qo'shmaydi va har Python yechimi bilan bir xil
  qafasda ishlaydi. Narxi: dialekt SQLite (`ILIKE`, `DISTINCT ON`, `::` yo'q).
  PostgreSQL kerak bo'lsa — alohida qaror va alohida sandbox.
- **`answer` — «eng yaxshi» emas, oxirgi javob.** Yuborilmagan test uchun
  yechuvchining oxirgi yuborgan fayli saqlanadi (CMS qoidasi): «eng yaxshi»
  uchun har test balini saqlash kerak, u hozir saqlanmaydi.
- `function` va `sql` judge shartnomasini o'zgartirmadi (API yechimni dasturga
  joylaydi); `answer` va `two_pass` `job.task` ni qo'shdi.
