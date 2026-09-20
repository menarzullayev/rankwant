# ADR-0027: Contest rating ladder - 9 to 16 tiers, English names, CF palette + nutella marker

**STATUS:** accepted (2026-09-20)
**Supersedes (part of):** ADR-0018 (Unvon zinapoyasi va Ism rangi).
**Impacted:** ADR-0006 (rating model), ADR-0018 (titles), ADR-0026 (CF sync).

## Context

ADR-0018 fixed the ladder at 9 tiers (kvark ... galaktika) and tuned
rw-rank-1..9 per palette for AA 4.5:1. Two things changed since.

1. Measurement against 974 498 CF users shows the floor band 0-1199 carries
   63.2 % of rated users - a single tier (Newbie) swallowed nearly two
   thirds of the population.
2. Owner policy (2026-09-20): rank names are English going forward
   (topics/02-til-siyosati.md). The codes in profiles/titles.py were Uzbek
   slugs; this becomes a policy violation the moment a non-Uzbek viewer
   reads them.

## Decision

### L1. Bounds and codes (16 tiers)

| # | Code | Block | rating_contest | CF equivalent | Users | Share |
| - | ---- | ----- | -------------- | ---------- | ----- | ----- |
| 1 | quark | Matter | 0-599 | Newbie | 205763 | 21.12% |
| 2 | atom | Matter | 600-899 | Newbie | 203708 | 20.90% |
| 3 | molecule | Matter | 900-1199 | Newbie | 206512 | 21.19% |
| 4 | droplet | Matter | 1200-1299 | Pupil | 75417 | 7.74% |
| 5 | meteorite | Cosmic Body | 1300-1399 | Pupil | 84408 | 8.66% |
| 6 | comet | Cosmic Body | 1400-1499 | Specialist | 75504 | 7.75% |
| 7 | moon | Cosmic Body | 1500-1599 | Specialist | 32353 | 3.32% |
| 8 | planet | Cosmic Body | 1600-1899 | Expert | 61906 | 6.35% |
| 9 | star | Stellar | 1900-2099 | Candidate Master | 14600 | 1.50% |
| 10 | supernova | Stellar | 2100-2299 | Master | 10261 | 1.05% |
| 11 | pulsar | Extreme | 2300-2399 | International Master | 1284 | 0.13% |
| 12 | magnetar | Extreme | 2400-2599 | Grandmaster | 1856 | 0.19% |
| 13 | black_hole | Extreme | 2600-2999 | International GM | 765 | 0.08% |
| 14 | galaxy | Cosmic Structure | 3000-3199 | Legendary GM | 119 | 0.01% |
| 15 | supercluster | Cosmic Structure | 3200-3499 | Legendary GM | 34 | 0.003% |
| 16 | cosmos | Everything | 3500+ | Legendary GM | 8 | 0.001% |

Bounds follow two rules:

- CF colour boundaries (1200, 1400, 1600, 1900, 2100, 2400, 2600, 3000) are
  sacred - splitting within a CF colour class keeps a tier from showing
  two different colours at once.
- Only the 0-1199 floor (a single CF colour, one tier, 63.2 % of users)
  is subdivided, into three balanced tiers (21.12 / 20.90 / 21.19 %).

User.rating_contest default drops from 1400 to 1200, so a brand-new account
lands at the first green tier (droplet) and has room to grow in both
directions. Source: apps/api/core/models.py:101; migration
0025_alter_user_rating_default.

### L2. Colour system - 7 CF canonical + nutella marker

Tier colour comes from one of Codeforces seven canonical palette anchors:

    grey  #808080  green  #008000  cyan  #03a89e  blue  #0000ff
    violet #aa00aa orange #ff8c00 red  #ff0000

A tier group index (0..4) is the marker count - the number of
black-leading characters on **both** the rendered username and the
rendered tier badge (--nutella-ink: #000 on light, #fff on dark). Within
a group, all tiers share the same hue; the marker tells them apart and
also helps colour-blind viewers. Example: atom is grey/1 (the A is
ink), molecule is grey/2 (Mo are ink), cosmos is red/4 (Cosm is ink).

The marker count is the same for the username and the badge within one
tier - the badge has its own length so it always splits visibly, the
username may be shorter (a short handle then has every character inked
because `marker >= length`). Codeforces' "LGM qora 1-harf"
convention is preserved this way: the LGM username starts with a black
letter, not because of the username text but because its tier has a
marker of 1 (or higher for higher tiers within the red group).

The owner dropped the WCAG-AA-on-rating-colours rule because the chosen
seven CF anchors cannot satisfy 4.5:1 against every palette worst
background (measured 0/18 palettes for grey and red). AA still binds
ordinary text - tools/check_contrast.py keeps `RANKS = ()` (the comment
there documents this carve-out). The marker is also a redundancy that
mitigates the relaxation.

The 18 --rw-rank-N palette tokens are kept: tier N reads --rw-rank-N. To
preserve per-palette tuning without exploding the CSS, this PR reuses
each palette existing tuned hex for the colour-group slot it already maps to:

    --rw-rank-1..3   <- old rank-1  (grey group)
    --rw-rank-4..5   <- old rank-2  (green group)
    --rw-rank-6..7   <- old rank-3  (cyan group)
    --rw-rank-8      <- old rank-4  (blue group)
    --rw-rank-9      <- old rank-5  (violet group)
    --rw-rank-10..11 <- old rank-7  (orange group)
    --rw-rank-12..16 <- old rank-8  (red group)

The old magenta slot (rank-6) and the old pink slot (rank-9) are dropped:
they belonged to the previous 9-colour aesthetic and have no analogue in
the new 7-anchor system. Future palette-tuned expansion is a follow-up PR.

### L3. Names

Codes are English (snake_case for multi-word): black_hole, supercluster.
Display strings live in the i18n catalogues under title.<code>; this PR
fills English (en.ts) and the source-of-truth catalogue (uz.ts). Other
locales fall back to the English string for the 16 new keys - to be
localised in a follow-up.

Block groupings (Matter, Cosmic Body, Stellar, Extreme, Cosmic Structure,
Everything) describe scale, not rarity, and are only used for the profile
legend - not for any logic.

## Consequences

- profiles/titles.py exposes 16 TITLES entries. title_for(rating,
  contests) and bands() keep the same signatures.
- core.User.rating_contest default becomes 1200 - a one-line schema change
  plus migration. Existing rows are untouched.
- tests/test_profile_phase2.py and tests/test_profile_stats.py had literal
  tier expectations ({code: kvark, level: 1}, etc.); updated for the
  16-tier scheme.
- The CF importer (ADR-0026) stores the imported rank_title separately
  from RankWant own title, so a CF-imported user still sees their CF
  colour alongside our ladder.

### When the ladder becomes visible (refines ADR-0018)

ADR-0018 made the title conditional on `rated_contest_count > 0`: "the
starting 1200 says nothing about skill yet". That rule kept the whole
ladder invisible in production, because the 974 498 Codeforces-imported
users have a rating but have not competed on RankWant.

Refinement: a rating is meaningful when **either**

1. the user has finished at least one rated contest on RankWant
   (`rated_contest_count > 0`), **or**
2. the rating is imported from an external source, detected via
   `rank_title` being set (ADR-0026).

`rated_contest_count` itself is **never** back-filled. It drives the
participation achievements (1 / 10 / 50 rated contests - bronze / silver /
gold, ADR-0018), so seeding it from Codeforces would grant those
achievements to all imported users at once.

A brand-new user with no contests and no import keeps no title, so the
original intent of ADR-0018 still holds.

### Peak tier (`max_title`)

The profile also exposes `max_title` — the tier for `max_rating_contest`.
That column is maintained in two places: the Codeforces import
(ADR-0026) and the contest rating service, which bumps it whenever a
user's rating rises. So the peak uses the same guard as the current
title, and a user with no contests and no import has neither.

`max_title` is RankWant's own ladder, distinct from `cf_max_title`
(Codeforces' own peak tier name). When the peak differs from the current
tier the profile card shows it as a second badge (▲ prefix), so a user
who has fallen from Cosmos to Supercluster still sees what they reached.

No new column was needed — `max_rating_contest` already existed.

## Rejected alternatives

- 15 tiers (2026-09-20 morning). Started as 15 with supernova replacing
  nova and red giant; the owner revised to 16 to add cosmos as a clear peak.
- Quantile cuts. Every quantile boundary tested produced non-CF numbers
  (364, 398, 585 ...). Kept CF anchors as the skeleton and only
  subdivided the 0-1199 floor.
- Hand-picked 15 hex with dE >= 0.08. Min dE 0.108, but no colour matches
  the CF anchors the audience already knows.
- Pure WCAG AA rating colours. 0/18 palettes for grey and red.

## Research artefacts

- research/2026-09-20-15-rang-tizimi/YAKUNIY-16.html - 16-tier dashboard
  with light/dark toggle, leaderboard, profile cards.
- research/2026-09-20-15-rang-tizimi/ladder16.json - machine-readable
  ladder used to generate the preview.
