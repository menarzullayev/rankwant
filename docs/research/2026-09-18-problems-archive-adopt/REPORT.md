# Problems archive: adopt from Codeforces and KEP

Session note (2026-09-18). Not a living spec — the code is the source after merge.

## Locked choices

- Surface: the whole `/problems` page (table + filters + sidebar).
- Stance: mix CF filter power, KEP social signals, and the current sidebar — one PR.
- Difficulty: one control — `difficulty__gte` / `difficulty__lte`. The seven level chips are presets for that range (`beginner` → 800–999, … `master` → 2700–3500). Old `?level=` URLs still work.
- Topics: KEP two-level UI (root direction, then child tag) plus CF `exclude_topics` (hide a problem that has **any** of those slugs). Include stays AND (`?topics=a,b`).
- Table row: keep stars; add like/dislike counts and author. Author has no profile link when `has_profile` is false (`kep-…` shadow accounts).
- Sidebar: keep current blocks; add most-liked (`ordering=-likes_count`) and a tag cloud (`problem_count` on `/topics/`).

## URL

Allowed on `/problems` in addition to the existing keys: `difficulty__gte`, `difficulty__lte`, `exclude_topics`.

`exclude_topics` is a comma list, same slug grammar as `topics`.
