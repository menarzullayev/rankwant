# tests/load — k6

test-strategy.md § 7–10.

```bash
k6 run -e SCENARIO=load   tests/load/main.js   # kutilayotgan yuklama
k6 run -e SCENARIO=spike  tests/load/main.js   # contest boshlanishi
k6 run -e SCENARIO=stress tests/load/main.js   # sig'imdan oshirish
k6 run -e SCENARIO=soak -e SOAK_DURATION=12h tests/load/main.js

# Leaderboard — 974K qatorli o'qish yo'li
k6 run -e SCENARIO=leaderboard -e LB_VUS=50 -e LB_PAGES=1,1000,10000 tests/load/main.js

# Contest spike — CF Div3 #1996 ning o'lchangan profili
k6 run -e SCENARIO=contest-spike \
  -e SPIKE_TOKENS_FILE=/tmp/tokens.json \
  -e SPIKE_PROBLEM=<slug> -e SPIKE_MAX_VUS=1200 tests/load/main.js
```

## Chegaralar (04-prd NFR)

| Metrika | Chegara |
| ------- | ------- |
| Sahifa p95 | < 1000 ms |
| Standings p95 | < 300 ms |
| Xato darajasi | < 1% |
| Judge p50 / p95 | < 5 s / < 15 s |

## Ma'lum sig'im

[ADR-0004](../../docs/07-adr/0004-judge-engine.md) o'lchovi: bitta host'da
8 worker ≈ **8 submit/s**. Spike NFR (50 submit/s) uchun 6–8 judge host
yoki kompilyatsiya keshi kerak.

⚠️ **50 submit/s — dizayn taxmini, o'lchangan emas.** Codeforces Div. 3
#1996 (150 daqiqa) **122 242** submission oldi va cho'qqisi
**4 568/daq = 76.1/s** bo'ldi (2-daqiqa). Ya'ni real cho'qqi dizayn
taxminidan **1.5 barobar yuqori** → 6–8 emas, **~10 host** kerak.

⚠️ **Lokal judge seriyali** — `services/judge-go/main.go` da
`for { BRPOP → judge() → LPUSH }`, worker pool yo'q. Bitta konteyner =
bitta worker = **2.4 submit/s**. Sig'imni faqat `--scale judge=N` bilan
ko'tarish mumkin: [judge-scale.sh](judge-scale.sh).

```bash
tests/load/judge-scale.sh status      # nechta worker ishlayapti
tests/load/judge-scale.sh plan 76.1   # qancha host va hisob kerak
tests/load/judge-scale.sh up 8        # 8 workerga ko'tarish
tests/load/judge-scale.sh watch       # navbat chuqurligini kuzatish
```

## leaderboard ssenariysi — o'lchangan nuqson

2026-09-20 da 974 498 qator bilan o'lchandi (`?page=` bo'yicha):

| Ssenariy | p50 | p95 |
| -------- | --- | --- |
| `?page=1`, 20 parallel | 1 523 ms | **2 616 ms** ❌ |
| `?page=1000`, 20 parallel | 6 002 ms | **9 247 ms** ❌ |
| `?page=1`, 50 parallel | 4 666 ms | **8 532 ms** ❌ |
| `?ordering=-rating_contest`, 50 parallel | 616 ms | 1 065 ms ⚠️ |

NFR — sahifa p95 < 1000 ms, ya'ni **8.5 barobar buzilgan**.

Ildiz sabab (`EXPLAIN (ANALYZE)`):

```
Sort Key: rating_skills DESC, id DESC
Sort Method: external merge  Disk: 7536kB
  ->  Parallel Seq Scan on core_user   Filter: is_active
```

`rating_skills` taqsimoti **0 → 974 497 qator, 800 → 1**: deyarli hamma
yozuv bir xil qiymatga ega, `id` tiebreak indeksda yo'q, `is_active` da
indeks umuman yo'q. Natijada har so'rov 974K qatorni saralab **7.5 MB
diskka to'kadi**. `rating_contest` esa 8× tez, chunki qiymatlar xilma-xil
va `user_contest_desc` indeksi ishlaydi.

Chuqur sahifa (`page=1000`) sayoz sahifadan **3.5×** sekin — shuning uchun
`LB_PAGES` da chuqurlikni ham yuritish shart.

## contest-spike ssenariysi — ikki cheklov

Profil **o'lchangan**, taxmin emas: `main.js` dagi `PROFILE_MINUTES` —
CF Div3 #1996 ning daqiqama-daqiqa submit soni (150 qiymat). `SPIKE_MINUTES`
bilan qisqartiriladi (sukut 10 daqiqa — cho'qqi va eng gavjum 10 daqiqa
shu ichida); 150 qilsa butun contest qayta o'ynaladi.

1. **Hisob soni.** `submit` throttle — **6/min har foydalanuvchiga**, ya'ni
   bitta hisob 10 soniyada faqat bitta yuborish mumkin. 76/s uchun
   **760 ta token** kerak. Kam bo'lsa ssenariy ogohlantiradi va natija past
   chiqadi (o'lchov throttle'ni ko'rsatadi, judge'ni emas).
2. **Worker soni.** 76.1/s ÷ 8 = **10 host** (yuqoriga qarang).

Tokenlar `auth/login/` orqali olinmaydi — u throttle qilingan va 760 token
soatlab vaqt oladi. Retsept `main.js` izohida (ADR-0008 `ApiToken`, scope
`submit`, `Authorization: Bearer rw_...`).

## Boshqa

**Sahifa ochilishi alohida chegara** (2026-09-17, local origin, CF yo'q):
50 VU `GET /` p95 657 ms ✅; 100 VU p95 1.65 s ❌; xato 0%. 1000 bir
vaqtdagi tashrif shu `web` da NFR ni yiqitadi. Yozuv:
[docs/research/2026-09-17-homepage-load/REPORT.md](../../docs/research/2026-09-17-homepage-load/REPORT.md).
`main.js` hozir API o'qish + standings; bosh sahifa skripti repo tashqarida
(`cp/research/2026-09-17-homepage-load/rw-home-load.js`).

Ma'lumot tayyorlash (30K ro'yxatdan o'tish, 122K urinish):

```bash
python manage.py seed_contest_scale --contest <slug> --window-hours 2.5 --rebuild-standings
python manage.py seed_contest_scale --contest <slug> --purge   # tozalash
```
