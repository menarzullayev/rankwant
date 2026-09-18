# ADR-0024: User model — fields for parity with Codeforces, Robocontest and KEP

**STATUS:** accepted (2026-09-18)
**Approved by:** Saidakbar aka on 2026-09-18, who chose the option "P1 + P2 + P3 columns"
(the CTO had recommended P1 + P2)
**Research:** [User model benchmark](../research/2026-09-18-user-model-benchmark/REPORT.md)
**Affects:**
- [05-domain-model](../05-domain-model/README.md) (`User`);
- [ADR-0017](0017-profile-and-settings.md) (profile and settings);
- [ADR-0018](0018-titles-roles-achievements.md) (where "last seen" is read);
- [ADR-0002](0002-qvant-economy.md) (future plan payments go through the ledger).

## Problem

The owner judged the 46 fields of `User` not enough next to Codeforces, Robocontest and
KEP. The benchmark found that RankWant is not behind in size: their user records expose 19
fields, an unpublished set, and 19 plus about 12. It did find gaps in coverage. Of the 74
attributes the three sites have, 17 were open:

- **5** were values they store and we either computed on every read or lacked;
- **3** were only partly covered;
- **7** needed a feature first;
- **2** were not proposed at all.

## Decision

`User` grows from 46 to **67** fields.

1. **Stored caches (P1).** The new columns are `last_seen_at`, `max_rating_skills`,
   `max_rating_contest`, `max_rating_activity`, `max_rating_challenges`, `streak_max` and
   `solved_count`. Each is written where its source is written:
   - `last_seen_at` in `core.sessions.record`, with the session row;
   - `max_rating_*` in every writer of `RatingHistory`, including the batch contest path;
   - `streak_max` in `qvant.streak.touch`;
   - `solved_count` when `UserSolvedProblem` is created or removed by a rejudge,
     and when a problem is published or hidden. It counts public problems only, the
     same rule as the profile's solved figures: a contest problem that is not public
     yet must not show up in a public count.

   `core.user_stats` derives the same values from the source tables. `max_rating_*` and
   `solved_count` must equal their source. `streak_max` and `last_seen_at` may only run
   ahead of it: a freeze keeps a streak alive without an accepted attempt that day, and
   signing out deletes the session that recorded the visit.
2. **`shirt_size` (P1).** It is used for olympiad prizes. Only the owner sees it, and it is
   never public, like `phone`.
3. **Names, grade and problemset toggles (P2).**
   - `first_name` and `last_name` existed but were never filled. `/me` now accepts them for
     certificates and olympiad lists, and `display_name` stays the public name.
   - `ui_prefs` gains a `problemset` group (`hideTags`, `hideSolved`), so these toggles
     follow the account instead of one browser.
   - `grade` becomes a coded catalogue in the settings change that also ships its select
     box. That way no deployed form sends free text to a validator that rejects it.
4. **Dormant columns (P3).** These are `plan`, `plan_expires_at`, six `postal_*` fields,
   `coach_can_view_attempts`, `message_min_rating`, `contribution`, `device_fingerprint`
   and `duel_ready_until`. They exist before the features that use them. The API does not
   expose them and there is no UI for them. Each feature that starts using one needs its
   own decision:
   - money goes through the ledger (ADR-0002);
   - a device fingerprint needs a privacy review first.

## Consequences

- **Reads move to the columns.**
  - The public profile's `max_ratings` reads the columns instead of a `MAX` over
    `RatingHistory` on every view.
  - The profile and the followers list read `last_seen_at`. Before, the profile ran a
    `MAX` over sessions and the list ran a subquery per row.
  - ADR-0018's online rule is unchanged, because `record` writes both values at the same
    moment. Last seen now survives signing out.
- **The leaderboard** can sort by `solved_count`.
- **`/me` PATCH saves only the fields the client sent.** A full save wrote back the counters
  read at the start of the request, including ratings, over concurrent updates from the
  judge worker.
- **Account deletion.**
  - `core.account` classifies every field as cleared or kept, and a test fails on a field in
    neither list.
  - The same tests found that `phone`, `email_verified_at`, `pinned_achievements` and
    `marketing_opt_in` survived deletion. `phone` was also missing from the export. Both are
    fixed.
- **Migration.** `0020_user_competitor_parity` fills the caches with one bulk write; the
  running code does not write these columns yet. After a deploy,
  `python manage.py recount_user_stats --check` reports drift from events in between, and
  the same command without `--check` repairs it.
- **Guard.** The dormant columns look unused, so the decisions table in `CLAUDE.md` lists
  them and `tools/check_decisions.py` fails if one disappears.

## Rejected

- **P1 + P2 without the P3 columns** was the CTO's recommendation. The owner chose to add
  the P3 columns now.
- **A separate 1:1 profile table.** Profile fields have lived on `User` since ADR-0017, and
  moving them was not asked for.
- **Not proposed in the benchmark:** KEP's four `can_*` booleans, user-uploaded covers, a
  coin-balance column and Codeforces' crypto wallet. Time zone and two-factor sign-in were
  left out as well; none of the three competitors has them.
