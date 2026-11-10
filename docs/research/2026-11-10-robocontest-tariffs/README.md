# Robocontest plans and payments — 2026-11-10

Measured on robocontest.uz in the built-in browser: first as a guest, then signed in with the owner's account (Judge plan). Nothing was bought, created or saved; payment buttons were not pressed. Texts are summarised, not copied. Used for [ADR-0057](../../07-adr/0057-billing.md).

## Public part

Sources: /plans, /legal/offer (in force 07.11.2026), /legal/judge (04.10.2026), /courses. Checkout (/checkout?plan_code=..&duration_months=..) redirects guests to /login.

## Plans (som; list price -> price with the running discount, which ends 13.11.2026 23:59, countdown banner on every page)
| Plan | 1 month (-10%) | 6 months (-25%) | 12 months (-40%) | Robocoin alternative (1 mo / 12 mo) |
|---|---|---|---|---|
| Free | 0 | | | |
| Plus | 29 000 -> 26 100 | 165 000 -> 123 750 | 310 000 -> 186 000 | 2 610 / 18 600 |
| Pro (marked "popular") | 49 000 -> 44 100 | 275 000 -> 206 250 | 525 000 -> 315 000 | 4 410 / 31 500 |
| Judge | 99 000 -> 89 100 | 569 000 -> 426 750 | 1 069 000 -> 641 400 | 8 910 / 64 140 |
Robocoin price = som price / 10.

Free: standard archive problems, all languages, AI tutor 5 questions/day, contests, virtual past contests, free courses, teams.
Plus: + AI tutor 100/day, problems from prestigious archived contests, compare your solution with others, premium study-plan materials, Plus badge.
Pro: + AI tutor 250/day, video courses (all paid courses "included in Pro"), roadmap for international olympiads, Pro badge.
Judge: + AI tutor 500/day, classroom, teach 50 students, judge panel, student progress analytics, own problems, closed contests, quizzes for students, priority support.
Note on the page: some features may not be ready, plan contents may change.

## Courses
One free course; paid courses are one-time purchases 97 000 / 297 000 / 497 000 / 647 000 som, each "included in Pro".

## Offer (seller: an LLC / MChJ)
- Products: Plus/Pro/Judge subscriptions, course access, gift cards (a code that adds Robocoin; transferable, never expires).
- Payment: Click only, 100% prepaid, card data only on Click's page; one-time, NO auto-renewal, no card charging.
- Contract formed when Click confirms; access immediately, or within 24 h on technical delay.
- Buying the same plan again stacks after the current period. Course access is lifetime (while the course exists).
- Under 18: parent/guardian consent required.
- Refunds: none except where law requires (e.g. service not provided by seller's fault); written request by email, answered within 10 days, refunded to the card via Click, access revoked.
- Account deletion or a ban ends the contract without refund. Planned downtime does not extend a subscription.
- Price changes never affect paid services. Offer published in uz and ru, uz prevails.

## Judge rules (separate acceptance before paying / in the panel)
- Public rated contests only together with the company (Telegram group, tester rated >= 2000, company decides rating).
- "GYM" contests: open, unrated, own problems only, contact info, educational purpose. Closed contests: Judge decides, may reuse archive problems.
- Judge's public problems show as "unofficial"; the company decides on the official archive.
- Blogs: topic limits, no unagreed ads.
- Students added with consent (parents for minors); student data only for teaching; never submit as a student.
- Penalties: warning -> hide/convert -> restrict -> revoke; no refund for the unused part when revoked for a breach.
- Judge must keep real name, school/work and phone in the profile.

## Signed-in part (owner's account, Judge plan until 01.09.2027)
- /plans shows "current plan: Judge, valid until, days left". Lower plans: "another subscription exists — switch after it ends" (downgrade scheduled after the current one; pay button disabled).
- Checkout: period radio (1/6/12 with per-month price and total), price breakdown (list price, discount, discount end), "pay now" amount, notes: one-time payment, no auto-renewal, offer acceptance by paying, parental consent under 18, "features may change". Payment goes to Click (not reached).
- Robocoin page: balance, total earned; tabs Tasks / Shop / Balance history. Tasks: daily login +1, solve 1 today +5, solve 3 today +15, weekly 15 problems +60; streaks 7/30/365 days +50/+200/+1500; first contest +10; profile completion (avatar +5, bio +5, Codeforces handle +20, education +8).
- Shop: Robocoin gift card (1 coin = 10 som; presets 2 900 / 4 900 / 9 900 coins = 29 000 / 49 000 / 99 000 som = Plus/Pro/Judge monthly list price; custom 10 000–200 000 coins); activate a code. Cosmetics: avatar frames 20–450 coins / 7 days, name effects 75–150 coins / 7 days, rating frames and rating colours unlocked by rating (forever).
- Courses when subscribed: paid courses show "included in your plan"; course page: progress, modules → lessons, video lessons, "what you will learn", requirements. Video: <video> with a blob source, HLS playlist and segments served from robocontest.uz itself.
- Judge panel is a separate app (judge.robocontest.uz): dashboard with quotas (problems 2 000, contests 100, quizzes 50, classrooms 50, storage 4 GB) and stats (participants, solvers, attempts, accepted, popular problems, recent contests); sections: contests, problems, testcase generator, test questions, quizzes, classrooms, blogs, study plans, my content, storage.
- New classroom form: name per language (uz required), description, visibility (closed: only owner and members), join mode "with approval" (code joiners wait in a queue the teacher approves), member limit 1–50 (owner not counted), invite link after saving.
- Student side: /my-classrooms, join by code.

## What RankWant took, and what it did not

| Robocontest | RankWant (ADR-0057) |
|---|---|
| Free / Plus / Pro / Judge, 1/6/12 months, one-time prepaid, no renewal | Same model |
| Click only | Click and Payme |
| Pro includes every paid course; courses also sold one by one | Same (Judge includes Pro) |
| Robocoin sold as gift cards, plans payable in coins | Not taken: Qvant is only earned (ADR-0002) |
| Lower plan blocked while a higher one runs | Allowed, starts after the higher one ends |
| Classroom joins "with approval" | Not yet: RankWant classrooms let anyone with the code join |
