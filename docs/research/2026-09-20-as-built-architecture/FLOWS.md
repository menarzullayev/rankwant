# Maʼlumot oqimlari — bosqichma-bosqich

**Sana:** 2026-09-20 · [orqaga](README.md) · [modullar](MODULES.md)

Har qadam: **kim** → **nima** → **qayerga yoziladi**. NFR: judge p50 &lt; 5s, p95 &lt; 15s (`Attempt.created_at` → `judged_at`).

---

## 1. Submit → verdikt

Maqsad: yuborish yoʻqolmasin; judge DB ni koʻrmasin; nomaʼlum verdikt bazaga tushmasin.

```
Brauzer                API                    Redis                 Judge
  │                     │                       │                     │
  │ POST /attempts/     │                       │                     │
  │────────────────────►│ Attempt PENDING (PG)  │                     │
  │                     │ attempt_count += 1    │                     │
  │                     │ LPUSH jobs ──────────►│                     │
  │ 201 + PENDING       │                       │◄──── BRPOP ─────────│
  │◄────────────────────│                       │     S3 tests        │
  │                     │                       │     nsjail          │
  │                     │                       │◄──── LPUSH result ──│
  │                     │ beat 2s: BRPOP        │                     │
  │                     │ apply_result (PG)     │                     │
  │ GET /attempts/id    │                       │                     │
  │────────────────────►│ AC/WA/…               │                     │
```

| # | Qadam | Modul | Yozuv | Izoh |
|---|---|---|---|---|
| 1 | `POST /api/v1/attempts/` | web → `judging.views` | — | Session. `CanSubmit` + throttle `submit` (1/10s). |
| 2 | Rate limit urilsa | `AttemptViewSet.throttled` | `Attempt(RATE_LIMITED)` | Tarix uchun; portlashda bitta qator. 429. |
| 3 | Validatsiya | `AttemptCreateSerializer` | — | problem slug, language, source ≤64KB, contest oynasi. |
| 4 | Saqlash | `judging.views.create` | `Attempt(PENDING)` | **Avval DB** — navbat yiqilsa ham qoladi. |
| 5 | Navbat | `judging.enqueue` | `Problem.attempt_count`, Redis jobs | `build_job`: har test S3 ref (ADR-0010), checker, til override. |
| 6 | Ishlash | `judge-go` | — | BRPOP → compile → N test → checker. `DATABASE_URL` boʻlsa exit 1. |
| 7 | Natija | `judge-go` | Redis results | `verdict`, `per_test`, `score`, `compile_output`. |
| 8 | Drain | `judging.drain_results` | — | 2s, max 500. `hack_id` / `custom_run_id` / attempt. |
| 9 | Yozish | `judging.apply_result` | Attempt + AttemptTestResult | Katalogdan tashqari verdikt → `IE`. `ALERTING` → `log.error`. |
| 10 | Keyingi | `ratings` / `contests` | pastga qarang | AC boʻlmasa reyting toʻxtaydi; contest boʻlsa standings debounce 5s. |

**Qotib qolish:** `reap_stuck` (60s). Navbat boʻsh + 5 daqiqa PENDING → bir marta qayta enqueue; yana qotsa `DENIAL_OF_JUDGEMENT` (IE emas — infra vs masala xatosi).

**Custom-test:** `CustomRun`, `mode=custom`, reytingga kirmaydi, bir xil throttle.

---

## 2. Birinchi AC → Skills → Qvant → Activity

`apply_result` oxirida, verdikt `AC` boʻlganda.

| # | Qadam | Modul | Yozuv |
|---|---|---|---|
| 1 | `on_attempt_judged` | `ratings.services` | Profil kesh `on_commit` invalidate |
| 2 | `UserSolvedProblem.get_or_create` | `ratings` | Uniq (user, problem). Takroriy AC → **return** |
| 3 | Hisoblagich | `problems` / `core` | `Problem.solved_count += 1`; public boʻlsa `User.solved_count += 1` |
| 4 | `recalc_skills` | `ratings` | Joriy difficulty lar. `User.rating_skills` + `RatingHistory` + `max_rating_*` |
| 5 | `qvant.on_first_accepted` | `qvant` | `try/except` — yiqilsa ham 1–4 saqlanadi |
| 5a | `streak.touch` | `qvant.streak` | `User.streak_*`; streak quest ledger orqali |
| 5b | `quests.on_accepted` | `qvant.quests` | `UserQuestCompletion` + `ledger.credit` (kunlik cap) |
| 5c | `profiles.achievements.on_solved` | `profiles` | Yutuq; yiqilsa ham streak/quest davom |
| 5d | `recalc_activity` | `qvant` → `ratings.formulas` | 30 kunlik oyna; `RatingHistory` type=activity |
| 6 | Decay | `ratings.refresh_activity` | Soatiga: hech kim yubormasa ham pasayadi |

**Qaytarish (rejudge AC→boshqa):**

1. Shu attempt `first_ac` boʻlmasa — chiqish.
2. Boshqa AC bor → `first_ac` koʻchadi, Skills/Qvant tegilmaydi.
3. Yoʻq → qator oʻchadi, `solved_count` floor 0, Skills `RECALCULATION`, Qvant **kun sharti** qayta oʻlchanadi (attempt ref bilan emas). Streak **tegilmaydi**.

---

## 3. Musobaqa: live → hack → reyting

| # | Qadam | Modul | Yozuv |
|---|---|---|---|
| 1 | Roʻyxat | `contests` | `ContestRegistration` |
| 2 | Submit | `judging` | `Attempt.contest_id` |
| 3 | Verdikt | `apply_result` | `_schedule_standings_rebuild` — Redis `standings-rebuild:{id}` 5s |
| 4 | `rebuild_standings` | `contests.services` | ACM: solved + 20 daq jarima. IOI: ball + hack_score. `Standing` upsert + kesh delete |
| 5 | Hack (ixtiyoriy) | `hacks.submit` | `Hack(TESTING)` + judge job `validate_input=True` |
| 6 | Hack natija | `hacks.apply_hack_result` | SUCCESSFUL / UNSUCCESSFUL / INVALID_… Himoyachi `HACKED` → `on_accept_revoked` |
| 7 | `hacks.close_due` | beat 60s | Oyna yopiladi; yangi test; AC qayta enqueue |
| 8 | `finalize_contest` | beat 60s | `select_for_update`. `hack_phase_pending` → return 0. `ratings_applied_at` qoʻyiladi |
| 9 | `apply_contest_ratings` | `ratings` | `is_rated` va ≥ `MIN_RATED_PARTICIPANTS` (10). Virtual yoʻq. Elo + `RatingHistory` |
| 10 | Quest | `qvant.on_contest_finished` | +30, contest boshiga (anti-farm) |

Mijoz standings ni ~10s da qayta soʻraydi (`StandingsTable`). Toʻliq SSE yoʻq — 06 dagi «SSE + polling» qisman.

---

## 4. Kirish

### 4.1 Email / parol

1. Web `POST /api/v1/auth/login/` (CSRF).
2. Django session → Redis.
3. Cookie `httpOnly`. SSR `GET /me/` cookie ni `API_BASE_INTERNAL` ga uzatadi.

### 4.2 OIDC (Google, GitHub, Telegram)

1. `GET /auth/<provider>/start/` — state sessiyaga, redirect.
2. Provayder callback → `SocialCallbackView`.
3. `SocialAccount` bogʻlanadi yoki User yaratiladi.
4. Session ochiladi. Telegram ham shu yoʻl (HMAC vidjet yoʻq).

### 4.3 PAT

1. `POST /me/tokens/` — ochiq `rw_…` **bir marta**.
2. Saqlash: SHA-256. Header `Authorization: Bearer`.
3. Scope tekshiruvi (`CanSubmit` va hokazo).

### 4.4 Parol tiklash / email

1. Token DB da (hash).
2. `core.send_email` → `EMAIL_CHAIN`.
3. `EmailDelivery` (provayder, sabab). **Tanasi saqlanmaydi.**

---

## 5. Mehmon oʻqish (CDN)

50k / homepage qarori: origin ni HTML bilan toʻldirmaslik.

| # | Qadam | Qayerda |
|---|---|---|
| 1 | `GET /` yoki `GET /problems` sessiya/`rw_locale`/`?lang=`/RSC yoʻq | Cloudflare Cache Rule |
| 2 | `proxy.ts` canonical 301; `?lang=` → header + cookie (`next()` dan **oldin**) | web |
| 3 | Origin `Cache-Control: public, s-maxage=30, stale-while-revalidate=86400` | `home-cache.ts` |
| 4 | SSR katalogni `API_BASE_INTERNAL` dan oladi | web → api |
| 5 | Lugʻat `/i18n/<til>.js?v=hash` `immutable` | alohida kesh |
| 6 | Kirgan foydalanuvchi | `private, no-store` — CDN yoʻq |

`/users/` — noindex (ADR-0023 + HITL: 974k import profil).

---

## 6. Hack job marshruti (drain tartibi)

`drain_results` **tartibi qatʼiy** — `hack_id` birinchi, chunki hack job `attempt_id=0` yuboradi va `apply_result` uni «topilmadi» deb yutib yuborardi.

```
result
  ├─ hack_id?        → hacks.apply_hack_result
  ├─ custom_run_id?  → judging.apply_custom_result
  └─ else            → judging.apply_result
```

Hack job da `validate_input=True`: ishonchsiz kiritma `Validator` dan oʻtadi; validator yoʻq boʻlsa judge ochiq xato (jim oʻtkazmaydi).

---

## 7. Xato va tiklanish

| Holat | Nima boʻladi |
|---|---|
| Redis jobs yiqildi, Attempt yozilgan | `reap_stuck` qayta enqueue |
| Judge OOM / deploy | ish yoʻqoladi → reap → DOJ |
| Nomaʼlum verdikt | `IE`, `log.error` |
| `SECURITY_VIOLATION` | ALERTING, incident |
| Qvant exception | Skills/Attempt saqlanadi |
| Ikki `finalize_contest` | `select_for_update` + `ratings_applied_at` |
| Standings spike | 5s debounce, toʻliq skaner har verdiktda emas |
| Email provayder kvota | zanjir keyingisiga; `warn_email_quota` |

---

## 8. Oʻqish yoʻli (masala sahifasi)

Yozuvsiz, lekin qatlamlar aralashadi:

1. Chekka: mehmon kesh yoki origin.
2. `proxy.ts` til.
3. `app/problems/[slug]/page.tsx` SSR `getJson('/problems/'+slug)`.
4. API `problems.views` — statement, samples (`is_sample=True`), til limiti.
5. Yashirin test **qaytmaydi** (faqat S3, judge uchun).
6. Editorial — `EditorialUnlock` / spoiler darvoza (ADR-0013).
