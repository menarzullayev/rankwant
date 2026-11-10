# Robocontest features worth taking — 2026-11-10 / 11

Measured on robocontest.uz and judge.robocontest.uz in the built-in browser, signed in with the
owner's account (Judge plan). Nothing was bought, created or saved. One side effect: toggling the
editor's "function mode" on problem A+B replaced the owner's draft with the template; the draft was
typed back (`print(sum(map(int, open(0).read().split())))`). Texts are summarised, not copied.

Plans and payments were analysed the day before: [2026-11-10-robocontest-tariffs](../2026-11-10-robocontest-tariffs/README.md).
Owner decisions from this analysis: [ai-tutor](../../decisions/2026-11-11-ai-tutor.md),
[plan-contents](../../decisions/2026-11-11-plan-contents.md),
[teacher-tools](../../decisions/2026-11-11-teacher-tools.md),
[content-and-archive](../../decisions/2026-11-11-content-and-archive.md),
[new-alphabet](../../decisions/2026-11-11-new-alphabet.md),
[community-and-contests](../../decisions/2026-11-11-community-and-contests.md).

## What Robocontest has, by area

**Problem list.** Categories (LeetCode-like tags), difficulty filter (easy / medium / hard / expert),
unsolved, favourites, "unofficial problems" toggle, problem star rating, editorial badge, a "download
the book" button (not pressed: it may download a file).

**Problem page.** Tabs: statement, editorial ("Tahlil": video or text), discussion (comments,
10–1000 characters), attempts, "rating" (fastest solutions: time, memory, code length, language).
1–5 star vote, "report a problem", text size, text-to-speech ("Tinglash"), function mode (a
`def solve(a: int, b: int) -> int` template for any problem), code file upload, custom tests,
character counter. Header on the problem page: RoboAI, stopwatch / timer, layout (standard,
vertical three columns, focus mode).

**RoboAI.** Side panel: history, new chat, quick prompts "explain the statement" and "give a hint",
a daily message counter (500 on Judge; plans say 5 / 100 / 250 / 500).

**Contests.** Official, training (GYM) and private tabs; official olympiad qualifiers and mirrors
(TATU, KHIMIO); a contest page with format (ICPC), individual / team, rated, upsolve, statements as
PDF, overview / problems / standings / attempts / participants, virtual participation with its own
standings; partner contests with sponsor prizes; standings filter by participant and region.

**Learning.** Study plans (Abramyan 1100 problems, basics, Uzbekistan olympiad archives by year and
stage: school, specialised schools agency, higher education, teachers) with sections and progress;
an algorithms library of 163 articles from cp.uz (CC BY-SA 4.0) with difficulty, reading time and
saved items; a 10-stage roadmap with general / olympiad tracks, reading progress and the next step.

**Profile and community.** Streak page (current, longest, freezes bought for 50 coins, milestones
3/7/14/30/100/365, 12-month calendar); users table with contest rating, "RoboRating" and karma;
profile with activity heatmap, rating history, problem map, certificates, languages, follow and
share; user blogs with tags, comments, likes and views; settings with T-shirt size and a coach who
may see the student's attempts; appearance menu with a grayscale mode.

**Judge panel** (separate app). Quotas (2 000 problems, 100 contests, 50 quizzes, 50 classrooms,
4 GB), statistics, testcase generator (JavaScript in the browser, ZIP download), question bank in
folders, study plans, "my content" (reports about the author's content), problem editor (statement
per language with live preview, tests, checker, attempts), classroom form (closed visibility, join
"with approval", member limit 1–50, invite link).

## Already in RankWant

Virtual contests (`Contest.is_virtual`, `virtual_start_at`), streak freeze (Qvant shop item),
custom tests on the submit panel, fastest solutions on the stats panel, problem votes and ratings,
favourites, the problem map on profiles, T-shirt size, paid editorials (Qvant), classrooms,
courses, plans and payments (ADR-0057), certificates, the appearance customiser, reports, follow.

## Measured details that shaped decisions

- **Archive tiers.** Abramyan problems are "unofficial": random 10-character codes, hidden until
  the unofficial filter is on (`unofficial=1`), no editorial tab. They count in neither solved
  problems nor problem points: the owner's profile shows "661 / 1477" solved and "12528 / 29235"
  points, and 1477 is the number of official public problems. Judge rules: a Judge's public
  problems appear as unofficial; the company decides what becomes official.
- **Alphabet.** Robocontest shows its interface in the new alphabet (Kiriş, Öquv, çiqing,
  Boşqariş), while problem statements stay in the old one ("chiqaring", "koʻpi bilan").
- **New alphabet law** (lex.uz, read 2026-11-11): [O'RQ-1184 of 21.10.2026](https://lex.uz/docs/8548754)
  restates article 1 of Law 931-XII: 28 letters and one tutuq belgisi (ʼ); oʻ→ö, gʻ→ğ, sh→ş,
  ch→ç; "ng" is no longer a letter combination of the alphabet. In force from 22.04.2027 (six
  months after publication); documents in the old form stay valid; the Cabinet adopts a programme
  within two months.
- **RankWant content today** (live API): 4 articles, 1 of them an algorithm article; 1 236 public
  problems; 1 trajectory. The Abramyan export (1 100 problems, 4 languages, 21 836 tests,
  verified) is ready at `D:\Linux\coding\abramyan-export\package\`.

## Proposed order of work

1. Problem translation model, then the new-alphabet converter and its search folding (both
   underpin everything below).
2. Official / unofficial archive tier; Abramyan import after the File and Text rework.
3. Teacher tools: classroom join approval, coach access, question bank and class quizzes.
4. cp.uz algorithms import (after confirming the one live article to delete); trajectory as
   study plans; olympiad archive.
5. Problem page: discussion, code file upload, stopwatch / timer, focus mode; "my content".
6. AI tutor (adapter, limits, history, budget), then Plus and Judge contents (editorials, solution
   code after solving, badges, quotas, closed and GYM contests).
7. Contests: region filter, statements PDF, partner contests; streak page, region map; user blogs
   and karma.
8. Text-to-speech: models measured and chosen with the owner.
