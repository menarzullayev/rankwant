# 5. Domain Model

**STATUS:** locked (2026-09-06)

Entitylar KEP/Robo modellaridan **ilhom**, RankWant nomlari va qarorlari bilan.
Stack: Django 5.2 + PostgreSQL ([ADR-0003](../07-adr/0003-stack-django-next.md)).

## Konventsiyalar

- PK: `BigAutoField`; tashqi ko'rinadigan resurslarda qo'shimcha `slug` yoki `code`
- Har entityda `created_at`, `updated_at`
- O'chirish: foydalanuvchi kontenti (attempt, transaction) **hech qachon** o'chirilmaydi — `is_active` / `is_public` bilan yashiriladi
- Pul/valyuta mantiqi: hech qachon `UPDATE balance`, faqat ledger yozuvi

## Entity diagram

```
                            ┌── UserSolvedProblem ──┐
                            │   (Skills manbasi)    │
User ──┬── Attempt ─────────┴─ Problem ─┬── Topic (M2M)
       │      └── AttemptTestResult     ├── TestCase ── Subtask
       │                                └── ProblemTranslation (Phase 2)
       ├── ContestRegistration ── Contest ── ContestProblem ── Problem
       │                             └── Standing
       ├── RatingHistory  (4 reyting uchun audit — ADR-0007)
       ├── QvantWallet ── QvantTransaction        ┐
       ├── UserQuestCompletion ── QvantQuest      │ Phase 1
       ├── UserInventory ── ShopItem              ┘
       └── Team (Phase 2) · Duel (Phase 3)

Language ── Attempt, TestCase (compile/run konfiguratsiyasi)
```

## Core

### User

| Maydon                                              | Tavsif                                      |
| --------------------------------------------------- | ------------------------------------------- |
| `id`, `username` (uniq), `email` (uniq)             | Auth                                        |
| `display_name`, `avatar_url`, `bio`                 | Profil                                      |
| `telegram_id` (null, uniq)                          | Telegram auth (Robo patterni)               |
| `rating_skills`                                     | Phase 0 — [ADR-0006](../07-adr/0006-rating-model.md) |
| `rating_contest`                                    | Phase 0 (Elo, boshlang'ich 1400)            |
| `rating_activity`                                   | Phase 1                                     |
| `rating_challenges`                                 | Phase 3                                     |
| `locale` (uz/ru/en), `theme`                        | UI                                          |
| `streak_count`, `streak_freeze_until`, `last_active_date` | Phase 1                               |
| `rated_contest_count`                               | Elo volatillik uchun (birinchi 6)           |
| `is_active`, `is_staff`, `date_joined`              |                                             |

4 reyting boshidan modellashtiriladi, UI da fazali ochiladi.
Formulalar: [04-prd § Reyting formulalari](../04-prd/README.md#reyting-formulalari).

### Problem

| Maydon                                    | Tavsif                                        |
| ----------------------------------------- | --------------------------------------------- |
| `slug` (uniq), `title`                    |                                               |
| `statement`, `statement_locale`           | Markdown + LaTeX; muallif tilida (04-prd P0-7) |
| `difficulty`                              | 800–3500, qadam 100 — **joriy qiymat reytingga kiradi** ([ADR-0007](../07-adr/0007-skills-uses-current-difficulty.md)) |
| `topics[]`                                | M2M → Topic                                   |
| `time_limit_ms`, `memory_limit_kb`        | Judge                                         |
| `checker_type`                            | `standard` / `special` / `interactive`        |
| `is_public`, `author_id`                  |                                               |
| `source`, `source_url`                    | original yoki import (atribut saqlash)        |
| `solved_count`, `attempt_count`           | denormalizatsiya — filtr va statistika uchun  |

### ApiToken — Phase 0

[ADR-0008](../07-adr/0008-auth-session-plus-pat.md). Ochiq API va Telegram bot uchun.

| Maydon                                   | Tavsif                                 |
| ---------------------------------------- | -------------------------------------- |
| `user_id`, `name`                        | foydalanuvchi bergan nom               |
| `prefix`                                 | ko'rsatish uchun (`rw_a1b2…`)          |
| `token_hash`                             | **SHA-256** — ochiq token saqlanmaydi  |
| `scopes[]`                               | `read` / `submit` / `contest:manage`   |
| `expires_at`, `last_used_at`, `revoked_at` | maksimal muddat 1 yil                |

Indeks: uniq `(token_hash)`, `(user_id, revoked_at)`.

### Topic · Language

- **Topic** — `slug`, `name_uz/ru/en`, `parent_id` (ierarxiya: DP → knapsack)
- **Language** — `code`, `name`, `version`, `source_file`, `compile_cmd`, `run_cmd`, `process_limit`,
  `compile_time_ms`, `proc_self`, `open_files`, `is_active`
  Judge til obrazlari bilan bir manbadan boshqariladi ([ADR-0004](../07-adr/0004-judge-engine.md));
  katalog — `apps/api/problems/languages.py` ([ADR-0022](../07-adr/0022-judge-languages.md))

### TestCase · Subtask

| Entity       | Maydonlar                                                                 |
| ------------ | ------------------------------------------------------------------------- |
| **TestCase** | `problem_id`, `order`, `input_ref`, `output_ref` (S3/R2 kaliti), `is_sample`, `points`, `subtask_id` (null) |
| **Subtask**  | `problem_id`, `order`, `points`, `scoring` (`min` / `sum`) — IOI uchun    |

Test ma'lumotlari **DB da emas, S3/R2 da** — hajmi GB darajasiga yetadi.

## Judging

### Attempt

| Maydon                                     | Tavsif                                      |
| ------------------------------------------ | ------------------------------------------- |
| `user_id`, `problem_id`, `contest_id` (null) |                                           |
| `language_id`, `source_code`, `source_size` | maksimal **64 KB** (DB da; kattasi rad etiladi) |
| `verdict`                                  | 20 kod (`AC`, `WA`, `TLE`, `MLE`, `RE`, `CE`, …) |
| `score`                                    | IOI/partial uchun; ACM da 0 yoki 100        |
| `time_ms`, `memory_kb`, `failed_test_index` |                                            |
| `compile_output`                           | CE holatida                                 |
| `created_at`, `judged_at`                  | latency o'lchash (NFR p50<5s, p95<15s)      |

**AttemptTestResult** — `attempt_id`, `test_index`, `verdict`, `time_ms`, `memory_kb`.
Contest davomida boshqa foydalanuvchiga ko'rsatilmaydi.

## Contest

| Entity                  | Maydonlar                                                                        |
| ----------------------- | -------------------------------------------------------------------------------- |
| **Contest**             | `slug`, `title`, `start_at`, `end_at`, `freeze_minutes`, `scoring_type` (ACM/IOI), `is_rated`, `is_virtual`, `is_public`, `mirror_of` (self FK) |
| **ContestProblem**      | `contest_id`, `problem_id`, `index_letter` (A, B, C…), `points`                  |
| **ContestRegistration** | `contest_id`, `user_id`, `registered_at`, `virtual_start_at` (null)              |
| **Standing**            | `contest_id`, `user_id`, `rank`, `solved_count`, `penalty`, `total_score`, `last_ac_at` |

`Standing` **materiallashtirilgan** — har judged attempt'dan keyin Celery inkremental yangilaydi.
Sabab: 500 parallel submit ostida live hisoblash standings so'rovini buzadi (04-prd NFR).

`is_rated` + **≥10 ishtirokchi** — Contests reytingi faqat shunda hisoblanadi.

## Hacking — ADR-0020

| Entity                | Maydonlar                                                                 |
| --------------------- | ------------------------------------------------------------------------- |
| **Hack**              | `hacker_id`, `defender_attempt_id`, `problem_id`, `contest_id` (null), `policy`, `status`, `stage`, `input_ref`, `output_ref` (S3/R2), `input_size`, `generator_language_id` (null), `generator_source`, `defender_verdict`, `detail`, `points`, `added_test_id` (null), `created_at`, `updated_at`, `judged_at` |
| **HackRoom**          | `contest_id`, `number` — `contest_room` siyosati uchun xona (~40 kishi)   |
| **HackRoomMember**    | `room_id`, `contest_id`, `user_id` — uniq `(contest, user)`               |
| **HackLock**          | `contest_id`, `problem_id`, `user_id`, `created_at` — lock qilingan masalaga qayta yuborib bo'lmaydi |
| **ReferenceSolution** | `problem_id` (OneToOne), `language_id`, `source`, `updated_at` — [ADR-0021](../07-adr/0021-hack-reference-solution.md) |

Hack natijasi va urinish verdicti — **ikki xil narsa** (ADR-0020, 4-qaror):
hack `TESTING` → `SUCCESSFUL` / `UNSUCCESSFUL` / `INVALID_INPUT` /
`GENERATOR_CRASHED` / `IGNORED` bo'ladi, himoyachining urinishi esa
`HACKED` verdictini oladi.

Hack testi ham odatdagidek **S3/R2 da**: hacker kiritmasi va etalon yechim
bergan javob obyekt xotirasiga yoziladi; test to'plamga qo'shilganda
`TestCase.origin = "hack"` bo'ladi va o'sha havolalar ishlatiladi.

`Contest` ga oyna maydonlari qo'shildi (`hack_room`, `hack_open_minutes`,
`uphack_days`, `hack_tests_added_at`, `hack_phase_closed_at`), `Standing`
ga esa hack ballari (`hack_score`, `hacks_successful`, `hacks_unsuccessful`).

## Reyting

### UserSolvedProblem — Skills manbasi

| Maydon                | Tavsif                                                     |
| --------------------- | ---------------------------------------------------------- |
| `user_id`, `problem_id` | **uniq birga** — faqat birinchi AC                       |
| `first_ac_at`         |                                                            |
| `first_ac_attempt_id` |                                                            |
| `difficulty_at_solve` | **audit uchun**; formulada ishlatilmaydi ([ADR-0007](../07-adr/0007-skills-uses-current-difficulty.md)) |

Skills = shu jadvaldagi masalalarning **joriy** `difficulty` lari bo'yicha hisoblanadi.

### RatingHistory — shaffoflik audit (majburiy)

| Maydon                              | Tavsif                                             |
| ----------------------------------- | -------------------------------------------------- |
| `user_id`, `rating_type`            | skills / contest / activity / challenges           |
| `value_before`, `value_after`, `delta` |                                                 |
| `reason`                            | `contest` / `problem_solved` / `problem_rerated` / `recalculation` |
| `ref_type`, `ref_id`                | contest yoki problem havolasi                      |
| `seed`, `rank`                      | contest holatida — Elo hisobini ko'rsatish uchun   |
| `created_at`                        |                                                    |

Bu entity vision principle #2 («reyting aniq») ni **texnik jihatdan bajaradi**: foydalanuvchi har bir o'zgarishning sababini ko'radi.

## Qvant — Phase 1

To'liq iqtisodiyot: [ADR-0002](../07-adr/0002-qvant-economy.md).

| Entity                   | Maydonlar                                                                |
| ------------------------ | ------------------------------------------------------------------------ |
| **QvantWallet**          | `user_id`, `balance` — **kesh**; haqiqat manbai ledger                   |
| **QvantTransaction**     | `user_id`, `amount` (±), `reason`, `ref_type`, `ref_id`, `balance_after`, `created_at` |
| **QvantQuest**           | `code`, `type` (daily/weekly/achievement), `title_uz/ru/en`, `reward`, `is_active` |
| **UserQuestCompletion**  | `user_id`, `quest_id`, `period_key` (kun/hafta), `completed_at`, `awarded` — **uniq (user, quest, period_key)** |
| **ShopItem**             | `code`, `category`, `title_uz/ru/en`, `price`, `asset_ref`, `is_active`  |
| **UserInventory**        | `user_id`, `shop_item_id`, `purchased_at`, `is_equipped`                 |

`UserQuestCompletion` dagi `period_key` **anti-farm kaliti** — bir kunlik quest kuniga bir marta.
`bajarilgan_quest` (Activity reytingi) shu jadvaldan 30 kunlik oynada sanaladi.

## Keyingi fazalar (eskiz)

- **Phase 2 (bajarildi):** `Classroom` + `ClassroomMember` + `Assignment`,
  `Article` + `ArticleProblemLink`, `Roadmap` + `RoadmapStep`
  (o'z kontent — [ADR-0005](../07-adr/0005-content-strategy-own-content.md)),
  `Notification`, `Post`
- **Phase 2 (qolgan):** `Team`, `Subscription` — narx ADR'idan keyin
- **Phase 3:** `Duel` (Challenges reytingi manbasi)

## Indekslar (kritik)

| Jadval                 | Indeks                                        | Nima uchun                              |
| ---------------------- | --------------------------------------------- | --------------------------------------- |
| `Attempt`              | `(user_id, problem_id, verdict)`              | «yechganmi?» tekshiruvi                 |
| `Attempt`              | `(contest_id, created_at)`                    | standings qayta hisoblash               |
| `Attempt`              | `(problem_id, created_at DESC)`               | masala bo'yicha oxirgi urinishlar       |
| `UserSolvedProblem`    | `(user_id)`                                   | Skills hisoblash                        |
| `UserSolvedProblem`    | **`(problem_id)`**                            | **qayta baholashda ta'sirlanganlarni topish (ADR-0007)** |
| `UserSolvedProblem`    | uniq `(user_id, problem_id)`                  | birinchi AC kafolati                    |
| `Standing`             | `(contest_id, rank)`                          | leaderboard sahifalash                  |
| `RatingHistory`        | `(user_id, rating_type, created_at DESC)`     | profil reyting tarixi                   |
| `QvantTransaction`     | `(user_id, created_at DESC)`                  | balans tarixi                           |
| `UserQuestCompletion`  | uniq `(user_id, quest_id, period_key)`        | anti-farm                               |
| `User`                 | `(rating_skills DESC)`, `(rating_contest DESC)` | leaderboard                           |
| `ApiToken`             | uniq `(token_hash)`, `(user_id, revoked_at)`  | har API so'rovida qidiruv               |

## Migration tartibi

1. `User`, `ApiToken`, `Topic`, `Language`
2. `Problem`, `TestCase`, `Subtask`, M2M
3. `Attempt`, `AttemptTestResult`
4. `Contest`, `ContestProblem`, `ContestRegistration`, `Standing`
5. `UserSolvedProblem`, `RatingHistory`
6. *(Phase 1)* Qvant guruhi
7. *(Phase 2)* Team, Classroom, Article, Subscription

## API resurs nomlari

```
/api/v1/problems/          /api/v1/problems/{slug}/
/api/v1/attempts/          /api/v1/attempts/{id}/
/api/v1/contests/          /api/v1/contests/{slug}/standings/
/api/v1/users/{username}/  /api/v1/users/{username}/rating-history/
/api/v1/me/
/api/v1/qvant/             (Phase 1: wallet, quests, shop)
/api/v1/schema/            OpenAPI — drf-spectacular
```

## Assumptions

1. **Test ma'lumoti GB darajasiga yetadi.** *"hajmi GB darajasiga yetadi"* —
   shu sababli S3/R2 da saqlanadi, DB da emas. Kichik hajmda bu qaror ortiqcha
   murakkablik bo'lardi.
2. **Denormalizatsiya maydonlari sinxron qoladi.** `Problem.solved_count` va
   `attempt_count` — *"filtr va statistika uchun"*. Ularni yangilovchi kod
   yozilmagan, lekin ajralib ketmasligi taxmin qilinadi.
3. **`QvantWallet.balance` — ishonchli kesh.** *"haqiqat manbai ledger"* —
   ya'ni kesh hech qachon ledgerdan ajralib qolmaydi degan taxmin.
4. **`Standing` materializatsiyasi yetarli.** Har judged attempt'dan keyin
   Celery inkremental yangilaydi — 500 parallel submit ostida ham ulguradi.

## Open questions

1. **Value objects va aggregates tushuncha sifatida yo'q.** Ularning mazmuni
   bor (verdict kodlari, qiyinlik shkalasi, ACM/IOI scoring — `04-prd` da;
   modul chegaralari — guruhlashda), lekin shu hujjatda **nomlanmagan**.
2. **Lifecycle holat mashinalari yo'q.** Faqat soft-delete qoidasi bor
   (`is_active` / `is_public`). Yo'q: contest (`scheduled → running → frozen →
   finished`), attempt (`pending → judging → judged`), Qvant quest
   (`available → completed`). Bularsiz arxitektura bosqichi ularni **taxmin**
   qiladi.
3. **Denormalizatsiya sinxronligi qanday ta'minlanadi?** Signal, service layer
   yoki Celery — yozilmagan.
4. **`difficulty_at_solve` nima uchun saqlanadi?** *"audit uchun; formulada
   ishlatilmaydi"* — lekin audit uni qanday ishlatishi ko'rsatilmagan.

## Qulflash

**Tasdiq:** Saidakbar Narzullayev — Repo owner / maintainer, 2026-09-06.

2026-09-06: entitylar, maydonlar, indekslar va migration tartibi tasdiqlandi.
Bog'liq qarorlar: [ADR-0002](../07-adr/0002-qvant-economy.md) Qvant · [ADR-0003](../07-adr/0003-stack-django-next.md) stack · [ADR-0006](../07-adr/0006-rating-model.md) 4 reyting · [ADR-0007](../07-adr/0007-skills-uses-current-difficulty.md) joriy qiyinlik.
O'zgartirish = yangi ADR (`docs/07-adr/`).

**Lock'dan keyingi tuzatishlar:**

- 2026-09-06 — [ADR-0008](../07-adr/0008-auth-session-plus-pat.md): `ApiToken` entity qo'shildi (session + PAT auth modeli).
- 2026-09-16 — [ADR-0020](../07-adr/0020-hacking.md): `Hack`, `HackRoom`, `HackRoomMember`, `HackLock` entitylari; `TestCase.origin`; `Contest` ga hack oynasi maydonlari; `Standing` ga hack ballari; 24-verdict `HACKED`.
- 2026-09-16 — [ADR-0021](../07-adr/0021-hack-reference-solution.md): `ReferenceSolution` — hack testining javobini beradigan etalon yechim.
- 2026-09-17 — [ADR-0022](../07-adr/0022-judge-languages.md): `Language` ga `source_file`, `compile_time_ms`, `proc_self`, `open_files` (36 til uchun tilga xos sandbox sozlamalari).

## Keyingi qadam

`08-technical-spec` — DB schema, OpenAPI, judge protokoli va auth qarori.
