# ADR-0023: Indexing — open to search engines, closed to AI crawlers

**STATUS:** accepted (2026-09-18)
**Affects:** [10-operations](../10-operations/README.md) (robots.txt row);
supersedes the closure decided on 2026-09-15 (PR #11)

## Problem

The site was closed to every crawler. `apps/web/src/lib/site.ts` had
`SITE_INDEXABLE = false`, so `robots.txt` answered `Disallow: /` and every page carried
`noindex, nofollow`.

That closure was measured, not cautious. On 2026-09-15, between 00:00 and 14:10 UTC, the
zone served **245,966 requests**:

| Source | Requests | Share |
| --- | --- | --- |
| GPTBot (verified OpenAI ranges) | 201,588 | 82% |
| Google (PTR `googlebot.com`) | ~40,000 | 16% |
| The owner's own IP | 2,966 | 1% |

The target was the profile pages of **10,001 seeded `neytron_*` users**, which multiply
into an endless URL space through filter and cursor parameters; 55% of GPTBot's requests
were 404s on `/users/*/urinishlar` paths that no longer exist. The `rankwant-maintenance`
Worker runs on every request, so the free Cloudflare quota of 100,000 requests a day was
spent on crawlers before noon.

The cost of the closure became visible on 2026-09-17, when Lighthouse 13.4.1 scored the
home page: Accessibility 100, Best Practices 100, SEO **66** with one failing audit —
`is-crawlable`. A platform that wants to be found cannot ship that.

## Options

1. **Stay closed until launch.** No work, no crawl load, SEO stays 66 and the site stays
   out of the index — including the 2,096 problems it exists to show.
2. **Open everything.** SEO 100, and the 2026-09-15 traffic comes back: the same seeded
   profiles, the same Workers quota, plus AI crawlers training on the content.
3. **Open to search engines, refuse AI crawlers, keep the crawl surface small.** What is
   open is what should be found; what burned the quota stays closed.

## Decision

Option 3, decided by the owner on 2026-09-18. It reverses the 2026-09-15 decision that
there would be no Cloudflare AI-bot blocking.

- `SITE_INDEXABLE = true`: `robots.txt` allows `*`, the root layout drops `noindex`, and
  the `Sitemap:` line returns (1,304 URLs).
- `robots.txt` refuses AI crawlers by name — `AI_CRAWLERS` in
  `apps/web/src/app/robots.ts`: GPTBot, ClaudeBot, CCBot, Google-Extended, PerplexityBot,
  Bytespider and the rest. `Google-Extended` is Google's training agent, not Googlebot:
  refusing it does not affect search.
- `/users/` stays disallowed while the seeded profiles exist. The sitemap lists no user
  URLs, so nothing contradicts it, and Lighthouse audits the home page, so the score is
  unaffected.
- A Cloudflare WAF custom rule blocks the same user agents at the edge. AI Crawl Control's
  own block action is a paid feature, but it enforces blocks through exactly such a rule,
  and custom rules are free (5 per zone).
- `tools/check_decisions.py` holds both halves that live in the repository, with negative
  tests in `tools/check_negative.py`.

## Why

robots.txt is a request, not a fence: GPTBot publishes that it honours it, Bytespider is
known not to. The WAF rule is the fence. Keeping only these two layers — and not, for
example, rate limiting the whole zone — keeps search engines fast while the crawlers that
produced 82% of the load get a 403 before the Worker runs.

## Consequences

- SEO returns to 100 on the home page; `is-crawlable` passes.
- Search Console and Yandex Webmaster are already verified through DNS TXT records
  (2026-09-11); the sitemap should be resubmitted after the deploy.
- The Workers quota is expected to hold: the 82% share is refused and `/users/` no longer
  invites an endless crawl. This has to be **measured** for a day in Cloudflare analytics
  after the deploy — the token in `.env.public` cannot read this zone, so the owner reads
  it in the dashboard.
- The WAF rule lives outside the repository. If the zone is rebuilt, the rule has to be
  recreated; `docs/10-operations` carries its expression.
- Open follow-up: delete the 10,001 `neytron_*` users (backup first — the local backup
  from 2026-09-17 restores cleanly), then drop `/users/` from the disallow list so real
  profiles can be indexed.
