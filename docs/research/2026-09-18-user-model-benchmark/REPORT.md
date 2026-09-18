# User model benchmark: Codeforces, Robocontest and KEP

**Date:** 2026-09-18 · **Status:** research record; the owner decided on the same day (see [Decision](#decision)).

## Question

The owner (2026-09-18): the 46 fields of our `User` model are not enough. Study the user
models of codeforces.com, robocontest.uz and kep.uz: which fields, relations and field types
they use. Then decide which fields RankWant must add so that its model is not smaller than
theirs. Deliver a comparison table and a list of fields to add.

## Answer

1. **By size, RankWant is not behind.** The measured sizes:

   | | Codeforces | Robocontest | KEP | RankWant |
   |---|---|---|---|---|
   | Fields on the user record | 19 in the API `User` object | not published (Laravel); 22 user-object shapes observed | 19 in the admin serializer (Django user + 10 columns), about 12 profile attributes in separate endpoints | **46** |
   | User attributes in the inventory, computed ones included | 39 | 53 | 38 | 46 stored + about 10 computed |
   | User-owned relations | 31 | 45 | 36 | **60** |

   Competitor inventories include computed values and viewer-relative flags, so they
   overstate what those sites store. Robocontest does not publish its stored columns; its 53
   are everything its pages expose about a user.

2. **By coverage, 17 attributes are open.** The [catalogue](#attribute-catalogue) has 77
   attributes. 74 of them exist on at least one competitor, and RankWant covers 57 of those
   74: 35 on `User`, 12 in related tables, 8 computed on read and 2 differently by design.
   Coverage per site:

   | Site | Attributes it has | Covered by RankWant |
   |---|---|---|
   | Codeforces | 46 | 34 |
   | Robocontest | 49 | 40 |
   | KEP | 53 | 46 |

   The 17 open attributes:
   - **5 gaps.** Four are values the competitors store and we compute on every read: last
     seen, max rating, solved count and longest streak. The fifth is T-shirt size.
   - **3 partial.** First and last name exist but are never filled, `grade` is free text,
     and problemset toggles live only in the browser.
   - **7 need a feature first**, for example subscriptions, a postal address and private
     messages.
   - **2 not proposed**: the crypto wallet, and sidebar content blocks, which our layout
     does not have.

3. **Proposal.** [P1](#p1--new-columns-on-coreuser-8) adds 8 columns, taking the count from 46
   to **54**. [P2](#p2--changes-without-a-new-column-3) makes 3 changes that add no column.
   [P3](#p3--needs-its-own-feature-and-adr-first-7) lists 7 items that each need their own
   feature and ADR.

## Method

- **Read-only.** GET requests only: no sign-in, no forms, no accounts created. Robocontest got
  83 requests and KEP 65, at least 1 s apart. Codeforces got 10, 6 of them to the API; its
  HTML pages sit behind a Cloudflare challenge. The challenge was not bypassed, and HTML
  evidence comes from Internet Archive copies.
- **Names and types only.** Every value was masked. The samples were `tourist` on Codeforces
  and one public profile each on Robocontest and KEP.
- **Evidence levels** are given per row in the raw inventories:
  - API documentation;
  - observed JSON;
  - backend schema (KEP's live Swagger);
  - JS bundle (Robocontest's Inertia/Vue chunks);
  - frontend code (KEP's public `archon1999/kep-frontend`);
  - secondary sources;
  - inferred.

  None of the three publishes its models, so their database types are inferred.
- **RankWant** was measured on the production API container with Django model
  introspection (read-only). It has 46 concrete fields and 60 reverse relations: 55 visible,
  3 automatic M2M through tables and 2 hidden.
- **Raw evidence** stays outside the repository, as the [research index](../README.md)
  requires: `cp/research/2026-09-18-user-model-benchmark/` holds the inventories, key→type
  maps, request logs and the catalogue script.

## Attribute catalogue

Generated from `cp/research/2026-09-18-user-model-benchmark/rankwant/catalogue.py`. A leading
`~` in a competitor cell means partial or a different shape; `–` means not found.

Status column:

| Status | Meaning |
|---|---|
| *yes* | stored on `core.User` |
| *yes, table* | stored in a related table |
| *computed* | derived on read |
| *by design* | covered differently on purpose |
| **gap** | missing; proposed below |
| **partial** | covered in part |
| *needs feature* | missing, and it depends on a feature that does not exist yet |
| *not proposed* | deliberately left out |
| *only us* | RankWant has it, none of the three does |
| *nobody* | none of the four has it |

| Attribute | Codeforces | Robocontest | KEP | RankWant | Status |
|---|---|---|---|---|---|
| **Account** | | | | | |
| Numeric id | id (in avatar URL) | id | id | `id` | yes |
| Handle | `handle` (Latin, digits, _ -) | `username` 2-24 | `username` <=150 | `username` + case-insensitive + `username_skeleton` | yes |
| Handle change rules and history | yearly window, history, redirects | – | ~free edit, no history | `username_changed_at` + `UsernameHistory` | yes |
| Email | `email` (on consent) | `email` | `email` (anonymous GET leaks it) | `email` (hidden by default) | yes |
| Email verified | confirm before first login | `emailVerified` | – | `email_verified_at` | yes |
| Password | min 5, leak check | yes | yes | `password` | yes |
| First and last name | `firstName`, `lastName` x 2 languages | ~single `name` | `first_name`, `last_name` | `display_name`; `first_name`/`last_name` exist but are never filled | **partial** |
| Phone | ~postal address only | `phone` (required) | ~shop order only | `phone` (optional, never public) | yes |
| Telegram id | – | `telegramId` | linked account | `telegram_id` | yes |
| OAuth identities | Google, Facebook, VK, OpenID | Telegram | Google, GitHub (only way to sign up) | `SocialAccount` | yes, table |
| API keys | key + secret | – | ~legacy token | `ApiToken` (scopes, expiry) | yes, table |
| Sessions and devices | ~remember-me, fingerprints | list + revoke | – | `UserSession` | yes, table |
| Registered at | `registrationTimeSeconds` | `joinedAt` | `date_joined` | `date_joined` | yes |
| Last login | – | – | ~Django, not exposed | `last_login` | yes |
| Last seen, stored on the user | `lastOnlineTimeSeconds` | `last_seen_text` | `last_seen` column | max of `UserSession.last_seen`, per request | **gap** |
| Online now | – | `isOnline` | `isOnline` | from sessions | computed |
| Staff / admin | Headquarters | ~olympiad roles | `is_staff`, `is_superuser` | `is_staff`, `is_superuser` | yes |
| Fine-grained capabilities | trust, coach rights | ~moderator roles | 4 `can_*` booleans | `groups`, `user_permissions`, derived roles | yes |
| Disabled account | "user is disabled" | – | `is_active` | `is_active` | yes |
| Consent (terms, marketing) | ~per-contest terms | – | – | `terms_accepted_at`, `marketing_opt_in` | yes |
| Device fingerprint | `bfaa`/`ftaa` at sign-in | `pcUUID` on attempts | – | IP and user agent per session only | needs feature |
| **Profile** | | | | | |
| Avatar | `avatar` | `avatar` | `avatar` | `avatar_url` | yes |
| Cover / title photo | `titlePhoto` | – | `cover_photo` (upload, 5 coins) | shop cover in `UserInventory` (ADR-0017) | by design |
| Bio | – | `bio` | `bio` | `bio` | yes |
| Website | – | `website` | `website` | `website` | yes |
| Birth date | birth date (settings) | – | `date_of_birth` (public, no toggle) | `birth_date` (hideable) | yes |
| Country | `country` (reference table) | – | `country` | `country` ISO-3166 | yes |
| Region | – | `region_id` (14) | `region` (text) | `region` (code) | yes |
| District | – | `district_id` | – | `district` (code) | yes |
| City | `city` (geodata, 120k+) | – | – | `city` (text) | yes |
| School / organization | `organization` (reference, rankings) | `study_id` (reference) | ~education list | `school_ref` FK + `school` text | yes |
| Study type | – | school / university / other | – | `School.kind` (catalog schools only) | yes |
| Grade / course | – | structured: grade 1-11, bachelor 1-4, master 1-2, teacher | – | `grade` free text (40) | **partial** |
| Coach | – | `coach_id` (self-chosen, public) | – | owner of the student's classroom | by design |
| Coach may view my attempts | – | `allow_view_by_coach` | – | coaches see assignment progress only | needs feature |
| T-shirt size | – | `shirtSize` | – | – | **gap** |
| Postal address | 12 fields, English + native | – | ~per shop order | – | needs feature |
| Social links | ~`vkId`, `openId` | 8 links | `telegram`, `codeforces_handle` | `ExternalProfile` (11 kinds) | yes, table |
| Ratings on other judges | – | Codeforces, AtCoder, LeetCode | ~Codeforces badge | `ExternalProfile` rating, max, rank | yes, table |
| Skills | – | – | catalog of 105 + custom, 0-100 | `UserSkill` (catalog only, 0-100) | yes, table |
| Technologies | – | – | text, icon, colour | `UserTechnology` | yes, table |
| Education | – | – | organization, degree, years | `Education` | yes, table |
| Work experience | – | – | company, title, years | `WorkExperience` | yes, table |
| Streams | Twitch / YouTube | – | – | ~YouTube handle in `ExternalProfile` | yes, table |
| Crypto wallet | TON wallet | – | – | – | not proposed |
| **Rating** | | | | | |
| Contest rating | `rating` (shown from 0, computed from 1400) | `contest_rating` (1500) | separate 1:1 table | `rating_contest` (1400) | yes |
| Other ratings | – | ~`karma` (task points) | skills, activity, challenges, duels | `rating_skills`, `rating_activity`, `rating_challenges` | yes |
| Provisional period | hidden rating + bonus for first 6 | ~`~` prefix | – | `rated_contest_count` | yes |
| Max rating, stored | `maxRating` | – | contest `maxRating` | MAX over `RatingHistory`, per request | **gap** |
| Rank title / max title | `rank`, `maxRank` | `title` | `ratingTitle`, `maxRatingTitle` | `title` computed; no max title | computed |
| Global place / percentile | ~ratedList order | `robo_rank` | place, percentile | `ranks` (4 COUNTs) | computed |
| Contribution (votes on posts) | `contribution` | – | – | – | needs feature |
| Solved count, stored | ~profile only | `stats.solvedTasks` | `solved` | COUNT over `UserSolvedProblem` | **gap** |
| Solved by difficulty | – | ~complexity map | 7 levels | `solved_by_level` | computed |
| Current streak | ~computed | `streak` | `streak` | `streak_count` | yes |
| Longest streak, stored | ~computed | `longest` | `max_streak` column | computed from activity, cached 1 h | **gap** |
| Streak freeze | – | `freezeTokens` | `streak_freeze` | `streak_freeze_until` + consumable item | yes |
| Last active date | – | `lastActivityDate` | – | `last_active_date` | yes |
| Coin balance | – | Robocoin balance | `kepcoin` column (public) | `QvantWallet` (ledger cache) | yes, table |
| Coins earned, lifetime | – | `lifetimeEarned` | – | sum over the ledger | computed |
| Followers / friend-of count | `friendOfCount` | `followers`, `following` | ~list | COUNT over `Follow` | computed |
| Achievements | ~crowdfunding badges | ~achievement quests | catalog with progress | `UserAchievement` + `pinned_achievements` | yes, table |
| Duel wins / draws / losses | – | – | `wins`, `draws`, `losses` | from `Duel` | computed |
| Activity calendar | yes | yes | daily statistics | computed | computed |
| **Settings** | | | | | |
| Interface language | en, ru | uz, ru, en, qq | en, ru, uz | `locale` (10) | yes |
| Theme | – | light, dark | ~browser only | `theme` | yes |
| Appearance | – | ~task layout, browser only | ~12 keys, browser only | `ui_prefs` (synced) | yes |
| Notification preferences | 3 e-mail toggles | – | Telegram toggle | `notify_prefs` (type -> channels) | yes |
| Privacy | hide contacts; show private activity | – | ~`email_visible`, no UI | `hidden_fields` (9 keys) | yes |
| Problemset toggles (tags, solved, blogs) | 3 account settings | – | – | hide tags: device setting in `localStorage`; solved: URL filter only | **partial** |
| Sidebar content blocks | 7 toggles | – | – | no content blocks in our sidebar | not proposed |
| Who may message me | min rating, block list | – | – | – | needs feature |
| Duel availability | – | – | `ready`, `readyUntil` | – | needs feature |
| Subscription plan | – | plus / pro / judge + days left | – | – | needs feature |
| Time zone | – | – | – | – | nobody |
| Two-factor sign-in | – | – | – | – | nobody |
| Self-service account deletion | – | – | – | yes | only us |

## Relations

User-owned entities. ✓ present, ◐ partial or a different shape, – not found. Bold rows are
features RankWant does not have. They are features, not fields, so P3 lists them only where a
user field depends on them.

| Relation | Codeforces | Robocontest | KEP | RankWant |
|---|---|---|---|---|
| Submissions | ✓ | ✓ | ✓ | ✓ `Attempt` |
| Rating history | ✓ | ✓ | ✓ per rating type | ✓ `RatingHistory` (4 types) |
| Contest registration and results | ✓ | ✓ | ✓ | ✓ `ContestRegistration`, `Standing` |
| Virtual participation | ✓ | ✓ | ✓ | ✓ |
| Hacks | ✓ | – | – | ✓ `Hack`, `HackLock`, `HackRoomMember` |
| Teams | ✓ roster | ✓ leader, invitations, archive | ✓ join code, member status | ✓ `Team`, `TeamMember` (join code, roles) |
| Follow / friends | ✓ | ✓ | ✓ | ✓ `Follow` |
| Blog posts | ✓ | ✓ | ✓ | ✓ `blog.Post` |
| **Comments on problems and posts** | ✓ | ✓ | ✓ | – (roadmap comments only) |
| **Votes / likes on posts and comments** | ✓ | ✓ | ✓ | – |
| Favourite problems | ✓ | ✓ | ✓ | ✓ `Favourite` |
| Problem votes / stars | – | ✓ | ✓ | ✓ `ProblemVote`, `ProblemRating` |
| **Private messages** | ✓ talks | – | – | – |
| Groups / classrooms | ✓ groups | ✓ classrooms | – | ✓ `Classroom` |
| Notifications | ◐ e-mail | ✓ 14 types | ✓ 13 types | ✓ `Notification` |
| Achievements | ◐ badges | ◐ quests | ✓ with progress | ✓ `UserAchievement` |
| Certificates | – | ✓ | – | ✓ `Certificate` |
| **Competition prizes** | – | – | ✓ money, Telegram Premium, merchandise | – |
| Coin ledger | – | ✓ | ✓ earn / spend | ✓ `QvantTransaction` |
| Quests / daily tasks | – | ✓ | ✓ | ✓ `UserQuestCompletion` |
| Cosmetics inventory | – | ✓ with expiry | ◐ cover | ✓ `UserInventory` (no expiry) |
| **Subscriptions, payments, gift cards** | – | ✓ | – | – |
| **Physical shop orders** | – | – | ✓ | – |
| Quizzes | – | ✓ | ✓ | ✓ `QuizAttempt` |
| **Courses / study-plan progress** | – | ✓ | ✓ | – |
| Arena, tournaments, duels, hackathons | – | – | ✓ | ✓ |
| Reports | – | ✓ 18 categories | – | ◐ `ProblemReport` only |
| Activity feed | ◐ recent actions | – | ✓ | ◐ computed |
| API keys | ✓ | – | ◐ legacy token | ✓ `ApiToken` |
| Handle history | ✓ | – | – | ✓ `UsernameHistory` |
| Sessions | ◐ | ✓ | – | ✓ `UserSession` |
| **Olympiad device registration** | ◐ fingerprint | ✓ | – | – |
| User lists, trust / vouching, streams | ✓ | – | – | ◐ streams via `ExternalProfile` |
| AI assistant, year in review | – | ✓ | – | – |

## Proposal

### P1 — new columns on `core.User` (8)

These close the five gaps. Four of them are values RankWant already computes on every read.
Storing them follows all three competitors and makes them sortable. Count after P1: **54**.

| Field | Type | Who stores it | Why | Kept current by |
|---|---|---|---|---|
| `last_seen_at` | `DateTimeField(null, db_index)` | Codeforces `lastOnlineTimeSeconds`, KEP `last_seen`, Robocontest | The followers list runs a correlated subquery per row today, and KEP sorts users by it | the same 5-minute write as `UserSession.last_seen` (ADR-0018); hidden by the existing `online` privacy key |
| `max_rating_skills`, `max_rating_contest`, `max_rating_activity`, `max_rating_challenges` | `IntegerField(null)` × 4 | Codeforces `maxRating`, KEP contest `maxRating` | The public profile computes `max_ratings` with a `MAX` over `RatingHistory` on every view. A max title (Codeforces `maxRank`, KEP `maxRatingTitle`) follows from it | the transaction that writes `RatingHistory`; a contest rollback recomputes from history |
| `streak_max` | `PositiveIntegerField(default=0)` | KEP `max_streak`, Robocontest `longest` | Today it is computed from the whole activity history (`profiles.stats.streaks`, cached for an hour) | wherever `streak_count` changes |
| `solved_count` | `PositiveIntegerField(default=0, db_index)` | Robocontest `solvedTasks`, KEP `solved` | The leaderboard can sort by it; today it is a `COUNT` | `UserSolvedProblem` creation and rejudge removal, plus a reconciliation check |
| `shirt_size` | `CharField(max_length=4, choices XS…3XL, blank)` | Robocontest `shirtSize` | Olympiad prizes and merchandise | owner-only and never public, like `phone` |

The migration backfills the cache fields from existing rows.

### P2 — changes without a new column (3)

| Change | Who has it | Why |
|---|---|---|
| Collect `first_name` and `last_name` (the columns exist but are never filled) | Codeforces (English and native), KEP; Robocontest requires a full name at sign-up | Certificates and olympiad lists need a real name. `display_name` stays the public name |
| Turn `grade` from free text into a coded catalogue, like `UZ_REGIONS`: grade 1–11, bachelor 1–4, master 1–2, teacher, other | Robocontest | Free text cannot be filtered or grouped |
| Keep problemset toggles (hide tags, hide solved) in `ui_prefs` | Codeforces (account settings) | Hide tags is a device setting in `localStorage` today, and hide solved is only a URL filter. Both are lost on another device |

### P3 — needs its own feature and ADR first (7)

| Item | Who has it | Depends on |
|---|---|---|
| Subscription plan and expiry | Robocontest (plus / pro / judge) | A monetization ADR; money goes through the ledger (ADR-0002) |
| Postal address | Codeforces (12 fields), KEP (per order) | Physical prizes or merchandise |
| Coach may view my attempts | Robocontest `allow_view_by_coach` | Coaches seeing attempts at all (today: assignment progress only) |
| Who may message me | Codeforces | Private messages |
| Contribution | Codeforces | Votes on posts and comments |
| Device fingerprint | Codeforces, Robocontest | Olympiad integrity, after a privacy review |
| Duel availability (`ready_until`) | KEP | Random matchmaking for duels (today: direct challenges only) |

### Not proposed

| Item | Who has it | Reason |
|---|---|---|
| Four `can_*` capability booleans | KEP | Django `groups` and `user_permissions` already cover this |
| User-uploaded cover photo | Codeforces `titlePhoto`, KEP `cover_photo` | ADR-0017: covers come from the Qvant shop |
| Coin balance column on the user | KEP `kepcoin` | ADR-0002: the ledger is the source; `QvantWallet` is its cache |
| Crypto wallet, tax id | Codeforces | Out of scope; sensitive data with no use here |
| Sidebar content blocks | Codeforces | Our sidebar is navigation and has no content blocks |
| Time zone, two-factor sign-in | none of the three | Not a parity gap; each would be its own decision |

## Decision

The owner was offered four options on 2026-09-18:

| Option | Scope | Recommended |
|---|---|---|
| P1 + P2 | 8 columns and 3 changes | yes, by the CTO |
| P1 only | 8 columns | |
| P1 + P2 + P3 columns | also the P3 fields as columns, before their features exist | |
| No code yet | this report only | |

The owner chose **P1 + P2 + P3 columns**. The P3 fields are therefore added as columns now
and stay empty until their features exist. The implementation and its ADR follow in a
separate pull request.

## What not to copy

Seen while collecting evidence:

- **KEP leaks private data.** Anonymous GET requests return e-mail, birth date, team join
  codes and coin balances. Its `email_visible` flag exists, but there is no UI to change it.
- **Robocontest changes state with GET.** Following a user goes through
  `/profile/{u}/toggle-follow`.
- **KEP counters can go negative.** `kepcoin`, `streak` and `max_streak` are signed integers,
  and its schema shows no non-negative check.

## Sources

- **Codeforces:**
  - API objects and methods (`/apiHelp`);
  - live `user.info`, `user.rating`, `user.status` and `user.blogEntries`;
  - profile and register pages via the Internet Archive;
  - official blog posts on handles, ratings and trust.
- **Robocontest:** Inertia page props (`data-page`), Vite chunks under `/build/assets/`, public
  `/api/*` lookups.
- **KEP:** live Swagger (`/swagger/?format=openapi`, 430 operations), public
  `/api/users/{u}/…` endpoints, `archon1999/kep-frontend` at `84216de815`.
- **Full source lists** with URLs:
  `cp/research/2026-09-18-user-model-benchmark/competitors/*.md`.
