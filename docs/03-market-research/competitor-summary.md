# Raqobatchilar — qisqa xulosa

> To'liq: `kep-uz-platform-analysis.md`, `robocontest-uz-platform-analysis.md`

## Jadval

| Jihat            | RoboContest           | KEP.uz                   | cp.uz               | RankWant (maqsad)   |
| ---------------- | --------------------- | ------------------------ | ------------------- | ------------------- |
| Stack            | Laravel + Inertia     | Django REST + Aurora SPA | Django REST + React | Django 5.2 + Next.js |
| API              | Yopiq                 | ~102 ochiq `/api/*`      | `/api/v1/*` qisman  | Ochiq REST (maqsad) |
| Foydalanuvchilar | ~197k                 | ~9k                      | n/a                 | 0 → growth          |
| Masalalar        | 1 477 + 8k maxfiy     | ~2 089                   | 35 practice         | import + original   |
| OJ               | ✅                    | ✅                       | ❌                  | ✅ MVP              |
| Musobaqa         | ICPC, virtual, mirror | ACM, IOI, golf           | ❌                  | ✅ MVP              |
| MCQ              | ✅                    | ❌                       | ❌                  | Phase 2?            |
| Kurslar          | video+masala          | study-plans              | articles/roadmap    | o'z maqola + roadmap |
| O'qituvchi sinfi | Judge rejasi          | ❌                       | ❌                  | Phase 2 B2B         |
| Gamification     | Robocoin              | kepcoin                  | bookmarks           | **Qvant**           |
| Monetizatsiya    | 4 tier obuna          | kepcoin + sovrin         | yo'q                | obuna + Qvant       |

## MVP uchun benchmark (prioritet)

**RoboContest** — to'liq mahsulot xaritasi (judge, contest, archive, subscription).  
**KEP** — API shape, kepcoin pattern, **4 reyting modeli** (qabul qilindi: [ADR-0006](../07-adr/0006-rating-model.md)).  
**cp.uz** — o'zbek kontent va olimpiada mavsum meta.

## O'zimizga olish kerak bo'lgan patternlar

1. Problems + difficulties + topics + langs
2. Attempts + verdicts (20 kod)
3. Contests + standings + statistics
4. Users + `/me` + rating
5. ACM scoring (boshlash uchun ACM10M)
6. Virtual contest
7. Mirror musobaqalar (Phase 2)
8. Qvant quest (Phase 1) + do'kon (Phase 2) — kepcoin/robocoin dan ilhom

## Nusxalamaymiz

- KEP Aurora engine yoki UI
- RoboContest Inertia monolit (API kerak bo'lsa)
- cp.uz kod bazasini fork qilib «platforma» qilish
