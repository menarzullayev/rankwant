# Asosiy modullar — vazifa, masʼuliyat, chegara

**Sana:** 2026-09-20 · [orqaga](README.md) · [oqimlar](FLOWS.md)

Har Django app — **bounded context**. HTTP `views.py` da; yozuv `services.py` da (ADR-0003). `ratings` URL prefix bermaydi — boshqa app lar chaqiradigan domen servisi.

Web tomonda yagona import: `@/lib/api` (`apps/web/src/lib/api/`).

---

## A. Identitet va platforma

### `core` — `apps/api/core/`

| | |
|---|---|
| **Vazifa** | Foydalanuvchi, auth, sessiya, PAT, email zanjiri, qidiruv, kalendar, SLO, maktab, tashqi koʻrinish, analytics |
| **Entity** | `User`, `ApiToken`, `SocialAccount`, `UserSession`, `UsernameHistory`, `EmailDelivery`, `EmailVerifyToken`, `PasswordResetToken`, `School`, `SiteAppearance`, `AnalyticsEvent` |
| **Kirish** | `/api/v1/auth/*`, `/me/`, `/users/`, `/health/`, `/slo/`, `/search/`, `/calendar/`, `/stats/`, `/appearance/`, `/analytics/events/`, `/staff/*` |
| **Chiqish** | Barcha app lar `User` ga FK. Email: `core.mailer` → Brevo/Mailjet/Resend/MailerSend |
| **Masʼuliyat** | Session + PAT (ADR-0008). `User.role` CharField **yoʻq** — staff Groups (ADR-0025). Parity maydonlar olib tashlanmaydi (ADR-0024). |
| **Emas** | Reyting formulasi (`ratings`), pul (`qvant.ledger`), submit (`judging`) |

### `profiles` — `apps/api/profiles/`

| | |
|---|---|
| **Vazifa** | Profil kengaytmasi: koʻnikma, ish/taʼlim, tashqi OJ, follow, jamoa, yutuq |
| **Entity** | `Skill`, `UserSkill`, `Education`, `WorkExperience`, `ExternalProfile`, `Follow`, `Team`, `TeamMember`, `UserAchievement` |
| **Kirish** | `/api/v1/` profiles marshrutlari; yutuq `qvant.on_first_accepted` dan |
| **Chiqish** | `profiles.refresh_external` (beat emas, task); `profiles.stats.bump` — kesh |
| **Masʼuliyat** | Codeforces maydonlari neytral nom (ADR-0026). Yutuq yiqilsa ham AC zanjiri davom etadi. |

---

## B. Katalog va tekshirish

### `problems` — `apps/api/problems/`

| | |
|---|---|
| **Vazifa** | Masala katalogi, til, test, checker, editorial, ovoz, shikoyat |
| **Entity** | `Problem`, `Topic`, `Language`, `TestCase`, `Subtask`, `ProblemLanguage`, `Validator`, `ReferenceSolution`, `Favourite`, `ProblemVote`, `EditorialUnlock`, `ProblemRating`, `ProblemReport`, `SimilarProblem`, `ProblemAttachment` |
| **Kirish** | `/api/v1/problems/` |
| **Chiqish** | `judging` test havolalarini oʻqiydi; `hacks` `ReferenceSolution` + `Validator` |
| **Masʼuliyat** | Test **S3 da**, DB da ref. Yashirin testsiz yangi eʼlon toʻsiladi. Til katalogi `languages.py` (ADR-0022, 35 til). |
| **Emas** | Verdikt yozish, reyting hisoblash |

### `judging` — `apps/api/judging/`

| | |
|---|---|
| **Vazifa** | Submit, custom-test, job qurish, natijani yozish |
| **Entity** | `Attempt`, `AttemptTestResult`, `CustomRun` |
| **Kirish** | `POST /api/v1/attempts/`, `/custom-test/` |
| **Chiqish** | Redis job; `ratings.on_attempt_judged`; `contests.rebuild_standings` (5s debounce) |
| **Masʼuliyat** | Attempt avval saqlanadi. Nomaʼlum verdikt = `IE`. `HACKED` judge dan kelsa rad. `API_ONLY` verdiktlar judge dan qabul qilinmaydi. |
| **Emas** | Sandbox (bu `services/judge-go`); hack bosqichlari (`hacks`) |

`JudgeProvider` (`judging/provider.py`): API judge ga HTTP yubormaydi. `submit` = LPUSH, `poll` = BRPOP.

### `hacks` — `apps/api/hacks/`

| | |
|---|---|
| **Vazifa** | Bitta dvigatel, toʻrt siyosat (ADR-0020): contest_room, global, lock, uphack |
| **Entity** | `Hack`, `HackRoom`, `HackRoomMember`, `HackLock` |
| **Kirish** | `/api/v1/hacks/` |
| **Chiqish** | Judge job `hack_id` + `validate_input=True`. SUCCESSFUL → himoyachi `HACKED`. Test qoʻshilsa `TestCase.origin=hack`. |
| **Masʼuliyat** | Hack statusi ≠ attempt verdikti. `close_due` boʻlmasa `finalize_contest` reyting qoʻllamaydi. |
| **Emas** | Etalon yechim saqlash (`problems.ReferenceSolution`) |

---

## C. Reyting va iqtisod

### `ratings` — `apps/api/ratings/`

| | |
|---|---|
| **Vazifa** | Toʻrt reyting: Skills, Contest, Activity, Challenges (ADR-0006) |
| **Entity** | `UserSolvedProblem`, `RatingHistory` |
| **Kirish** | Boshqa app lar `on_attempt_judged`, `apply_contest_ratings`, `recalc_skills_for_problem` |
| **Chiqish** | `User.rating_*`, `RatingHistory`, `notifications` (problem_rerated), `qvant.on_first_accepted` |
| **Masʼuliyat** | Skills = **joriy** `Problem.difficulty` (ADR-0007). Formula `ratings.formulas` da sof. Har delta audit qatori. |
| **Emas** | HTTP resurs (urlpatterns yoʻq). Pul. |

Birinchi AC tartibi (qatʼiy): `UserSolvedProblem` → `recalc_skills` → keyin Qvant (Qvant yiqilsa ham Skills qoladi).

### `qvant` — `apps/api/qvant/`

| | |
|---|---|
| **Vazifa** | Yopiq loop iqtisodiyot: quest, streak, doʻkon (ADR-0002) |
| **Entity** | `QvantWallet`, `QvantTransaction`, `QvantQuest`, `UserQuestCompletion`, `ShopItem`, `UserInventory` |
| **Kirish** | `/api/v1/qvant/`; `ratings` / `contests` hodisalari |
| **Chiqish** | Faqat `qvant.ledger` orqali balans. Activity uchun `ratings.formulas` |
| **Masʼuliyat** | `QvantWallet.balance` — kesh; haqiqat — ledger. Kunlik earn cap; streak/admin ozod. Anti-farm: `uniq(user, quest, period_key)`. |
| **Emas** | Toʻgʻridan-toʻgʻri `UPDATE balance` |

---

## D. Musobaqa formatlari (ADR-0011)

### `contests`

| | |
|---|---|
| **Vazifa** | Vaqt oynali masala toʻplami, ACM/IOI, virtual, sertifikat |
| **Entity** | `Contest`, `ContestProblem`, `ContestRegistration`, `Standing`, `Certificate` |
| **Kirish** | `/api/v1/contests/` |
| **Chiqish** | `ratings.apply_contest_ratings` (≥10, `is_rated`); `qvant.on_contest_finished`; hack oynasi maydonlari |
| **Masʼuliyat** | `Standing` materializatsiya. `finalize_contest` `select_for_update` + `ratings_applied_at`. Virtual ishtirok reytingga kirmaydi. |
| **Emas** | Judge ishini qurish |

### `arena` · `duels` · `tournaments` · `hackathons` · `quizzes`

| App | Vazifa | Judge? | Yakun |
|---|---|---|---|
| `arena` | Tezkor savol raundi | Yoʻq (javob tanlash) | `arena.finalize_due` |
| `duels` | 1v1, Challenges reytingi | Ha (masala submit) | `duels.finalize_due` |
| `tournaments` | Bosqichlar + umumiy standing | Contest orqali | stage model |
| `hackathons` | Jamoa topshirigʻi | Yoʻq (fayl/repo) | staff baholash |
| `quizzes` | Test / tanlov | Yoʻq | `quizzes.services.submit` |

---

## E. Kontent va jamoa

| App | Vazifa | Entity | Izoh |
|---|---|---|---|
| `content` | Oʻquv maqola + yoʻl xaritasi | `Article`, `Roadmap`, `RoadmapStep`, `ArticleProblemLink` | Oʻz kontent (ADR-0005) |
| `classroom` | Sinf, aʼzo, vazifa | `Classroom`, `ClassroomMember`, `Assignment` | Oʻqituvchi |
| `blog` | Yangilik | `Post` | `announce_published` |
| `updates` | Platforma changelog | `SystemUpdate`, `Translation`, `UpdateRead` | 10 til |
| `roadmap` | Mahsulot yoʻl xaritasi | `RoadmapItem`, `Vote`, `Comment` | `content.Roadmap` dan **boshqa** |
| `notifications` | In-app + Telegram | `Notification` | `notifications.send_telegram` |

---

## F. Web (`apps/web`)

| Qism | Vazifa |
|---|---|
| `src/app/*` | 80+ App Router sahifa (katalog, profil, admin, arena, …) |
| `src/proxy.ts` | Canonical host, `?lang=`, mehmon CDN, eksperiment |
| `src/lib/api/` | Domain client: account, problems, contests, qvant, … |
| `src/lib/api.server.ts` | SSR fetch + cookie |
| `src/i18n/` | 10 til; lugʻat `/i18n/<til>.js?v=hash` |
| `src/lib/home-cache.ts` | Mehmon `/` va `/problems` Cache-Control |

Web **biznes yozuvini** takrorlamaydi: verdikt, ledger, Elo — faqat API.

## G. Judge (`services/judge-go`)

| | |
|---|---|
| **Vazifa** | Job ni sandboxda bajarish, verdikt qaytarish |
| **Kirish** | Redis jobs (PULL). S3 test refs. |
| **Chiqish** | Redis results: `attempt_id` / `custom_run_id` / `hack_id` |
| **Masʼuliyat** | nsjail + cgroup preflight. `DATABASE_URL` → exit 1. Tashqi internet yoʻq. |
| **Emas** | Reyting, standings, Qvant, Attempt qatori |

`services/judge-py` — bake-off nomzod, preview da ishlamaydi.

## H. Chekka va ops

| Komponent | Vazifa |
|---|---|
| Cloudflare Tunnel | Ochiq port yoʻq; `rankwant.uz` → `8300`/`8301` |
| `services/maintenance-worker` | Tunnel oʻchiq: 503 sahifa, `/api/*` loyiha xato formatida |
| `tools/deploy.sh` | Yagona jonli deploy; `check_deploy_gate.py` |
| `tools/auto_deploy.sh` | Host watcher (Actions emas — runner `.env.public` ni koʻrmaydi) |

---

## Bogʻliqlik (kim kimni chaqiradi)

```
core.User
  ↑
problems ──► judging ──► ratings ──► qvant
                 │            │
                 ▼            ▼
              contests     notifications
                 │
                 ▼
               hacks ──► judging (hack job)

profiles ◄── qvant (yutuq)
content / classroom / quizzes    (katalogni oʻqiydi, judge yoʻq)
arena / duels / tournaments / hackathons   (formatlar)
```
