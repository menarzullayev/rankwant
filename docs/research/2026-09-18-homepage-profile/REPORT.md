# Homepage profile — 2026-09-18

**Question:** where does one homepage render spend its time, and what caps how many visitors a
single `web` container can serve? Profiled before changing anything (owner decision S3).
**Follows:** [2026-09-17 homepage load](../2026-09-17-homepage-load/REPORT.md), which found p95
1.65 s at 100 VU and pointed at the Next.js render and the menu prefetch.

**Setup.** A local production build of `main` (`0d18320`, Next.js 16.3.4, Node 24.14.1) runs under
`next start` on the host. A pass-through proxy forwards its API calls to the live API
(`127.0.0.1:8301`, with the `Host` header) and logs each one with its duration. The live `web`
container is not involved. Requests come from a guest with no cookies unless stated otherwise.
CI jobs ran on the same machine during part of the work. The A/B comparison alternates rounds, so
background load hits both variants alike, and process CPU time is less sensitive to it than
latency.

Scripts, the CPU profile and the proxy are outside the repo, in
`C:\Users\nsn\project\cp\research\2026-09-18-homepage-profile\`.

---

## Summary

| Area | Finding |
|---|---|
| API | Once the data cache is warm, a guest render makes **one** API call: `/me/`, which returns 401. It was made unconditionally, and now it is skipped (0 calls). A cold cache makes up to 8 calls, 12–17 ms each, in parallel. The data cache works under `force-dynamic` (revalidate 30–300 s), so the API is not the bottleneck. |
| Server CPU | **12–17 ms per render**, all on one JS thread. That caps one Node process at ~64–84 renders/s. The 100 VU run of 2026-09-17 asked for more than that, which explains its p95 of 1.65 s. |
| HTML | 142 KB (36 KB gzip). **72 KB** of it is the whole uz dictionary, passed to `LocaleProvider` and serialized into every page. |
| Dictionary | With an empty dictionary: HTML 63 KB (11 KB gzip), CPU **−32%**, throughput **+37%**, p95 −25%. Every one of 6 alternating rounds moved in the same direction. |
| Prefetch | The page has 40 internal links; 25 of them are in the chrome (sidebar, top bar, header, footer). One prefetch costs **~5.6 ms** of server CPU, so the chrome alone costs ~130–150 ms per visit, **~9×** the page render. A real browser sent 42 RSC requests within 5 s of load; with intent prefetch it sends 7. |
| Locales | 400 concurrent renders in four languages: no request saw another's dictionary. The probe was first checked against a build that renders raw keys, to confirm it catches them. |

---

## 1. API calls per render

Five guest renders, three seconds apart. The proxy log is split by render window.

| Render | TTFB | API calls |
|---|---|---|
| 1 (cache partly cold) | 60 ms | 4 — `contests`, `posts`, `users`, `me` (401) |
| 2–5 | 18–62 ms | 1 — `me` (401) |

`page.tsx` asked for `/me/` even without a session cookie; the root layout already skipped it.
`problems`, `onboarding` and `settings` did the same.

`/me/` calls per render, counted by the proxy (a fake `sessionid` stands in for a signed-in user):

| Build | Guest | With a session cookie |
|---|---|---|
| Before | 1 | 1 |
| After (`getSessionUser` on all four pages) | **0** | 1 |

A signed-in render did **not** make two calls, although the layout and the page both ask.
Next.js memoizes identical `fetch` calls within one render, so the second call never reached
the API. This was expected from reading the code and disproved by measurement.

## 2. Server CPU per render

Measured as the change in the server process's own CPU time over a batch.

| Mode | CPU per render | Throughput | p95 |
|---|---|---|---|
| Sequential, 100 renders | 15.6 ms | 40/s | 62 ms |
| 10 in parallel, 200 renders | 12.0 ms | 99/s | 140 ms |

`next start` is a single process with no render workers, so one core's worth of JS is the limit.

## 3. Where the CPU goes

The inspector's sampling profiler ran on the server during 300 renders at concurrency 10, and
self time was grouped by source.

| Group | Share | ms per render |
|---|---|---|
| Node internals (writes, sockets, microtasks) | 40% | 6.7 |
| Next's bundled React renderer (HTML and RSC flight) | 39% | 6.6 |
| App code (server chunks) | 11% | 1.8 |
| Next server | 5% | 0.9 |
| Garbage collection | 3% | 0.5 |

The profile cannot separate HTML rendering from flight serialization, because Next ships both
in one minified file. The A/B test below measures the dictionary's cost directly instead.

## 4. What the HTML is made of

| Part | Size |
|---|---|
| RSC flight payload (inline scripts) | 105.9 KB |
| — of which the `dict` prop of `LocaleProvider` | 72.1 KB |
| Other inline scripts | 4.6 KB |
| Markup | 31.3 KB (13.3 KB of it inline SVG icons) |
| Total | 141.8 KB, 36.1 KB gzip |

By namespace, the dictionary is `admin` 22%, `settings` 13%, `profile` 9%, `customizer` 7%, and a
long tail of small groups. A public page carries all of it.

## 5. A/B: the same build without the dictionary

B is the same commit with `dict={{}}` in `layout.tsx`. That empties the client registry, so B
renders raw keys: it is a cost measurement, not a candidate fix. Rounds of 200 renders at
concurrency 10, alternating the order.

| Round | A CPU/render | B CPU/render |
|---|---|---|
| 1 | 22.7 ms | 14.1 ms |
| 2 | 16.2 ms | 14.5 ms |
| 3 | 17.7 ms | 10.9 ms |
| 4 | 13.0 ms | 9.5 ms |
| 5 | 16.2 ms | 11.2 ms |
| 6 | 15.0 ms | 9.5 ms |
| **Median** | **16.2 ms**, 78 renders/s, p95 166 ms | **11.1 ms**, 107 renders/s, p95 125 ms |

HTML: A 141.8 KB (36.1 KB gzip), B 63.4 KB (11.4 KB gzip).

## 6. Prefetch

The router's prefetch requests (`RSC: 1`, `Next-Router-Prefetch: 1`) were replayed for the links
that come before `<main>`: 130 requests, all 200, 1.3 KB gzip each on average, and
**5.6 ms of server CPU each**.

Links on the homepage: 23 before `<main>`, 15 inside it, 2 after it (footer).

A headless Chromium window (929 px wide, page visible) loaded the homepage and was left idle for
5 s:

| Build | RSC requests | What they were |
|---|---|---|
| Before | 42 | 17 sidebar routes twice each, `/login` 5×, `/rating` 2×, `/` once |
| After (intent prefetch) | **7** | only content links in view: the hero's `/login?tab=register` 3×, `/contests` 2×, `/leaderboard` 2× |

On the new build, hovering the footer's `/terms` link sent its prefetch (0 → 2 requests), and
keyboard focus on `/privacy` did the same (0 → 2). A click still navigated client-side, without a
full reload.

## 7. Locale isolation

`LocaleProvider` calls `registerMessages(locale, dict, true)` during SSR as well. Its comment
says the server does not evict, but the call does, which clears that module instance's registry.
If two requests in different languages interleaved inside one render, one of them could lose its
dictionary.

400 requests at concurrency 20, each in one of four languages (via the `rw_locale` cookie), were
checked for raw keys and for their own language's nav label: **400/400 correct**. The same probe
flagged 40/40 responses on build B, so it does detect raw keys. The homepage render does not
suspend between the provider and its children, so nothing interleaves. The risk stays theoretical
and is recorded here only.

## 8. Decisions (owner, 2026-09-18)

| Problem | Decision | Where |
|---|---|---|
| Chrome prefetch, ~130–150 ms CPU per visit | Prefetch on intent: hover, focus, touch | this change; CLAUDE.md decisions table |
| `/me/` for guests (and, it was thought, twice for signed-in users) | Skip it without a session cookie; one call per request | this change. The single call for signed-in users already held (section 1) |
| Dictionary in every page (72 KB, 32% of CPU) | Serve it as a separate cached file | next PR |
| Account templates never reach a new device (APP-13) | Merge by name, the account's copy wins | later PR |
| First paint ignores the team default style (APP-14) | Fix now | later PR |

Not decided yet: the 15 content links inside `<main>` still prefetch on sight.

## 9. Reproduce

With the proxy on `:8399` and a build under `next start` on `:3107` (`API_BASE_INTERNAL` pointing
at the proxy):

```bash
python census.py 5
python cpu_per_render.py <pid> 200 10
node cpu_profile.mjs 300 10 9230
python html_parts.py
python prefetch_cost.py <pid> 5
python locale_race.py 400 20
python me_calls.py http://127.0.0.1:3107/ 3
```

The RSC request counts come from a headless Chromium (Playwright) window: load the page, wait
5 s, then read `performance.getEntriesByType("resource")` for URLs carrying `_rsc=`.

---

## 10. Follow-up, same day: the dictionary as a file

Owner decision 3 was implemented: the browser gets the dictionary as `/i18n/<locale>.js?v=<content hash>`
(static, `Cache-Control: public, max-age=31536000, immutable`, outside the middleware), and the page
only carries its address. Measured on local production builds, as above.

| | Before (main with intent prefetch) | After |
|---|---|---|
| Homepage HTML | 141.8 KB, 36.1 KB gzip | **63.8 KB, 11.7 KB gzip** |
| RSC flight payload | 105.9 KB | 27.8 KB |
| Server CPU per render (6 alternating rounds, median) | 10.2 ms | **5.6 ms** (−45%) |
| Throughput at concurrency 10 | 132 renders/s | **235 renders/s** |
| p95 at concurrency 10 | 98 ms | 55 ms |

Against the build from before both changes (no intent prefetch, `/me/` for guests): 12.6 → 7.1 ms
per render, 100 → 200 renders/s.

Correctness, checked on the new build:

- The visible text of the homepage is identical in all ten languages, with no raw keys. The
  comparison was first checked against two different pages, which it reports as different.
- 400 concurrent renders in four languages: 400/400 correct.
- In a real browser, a guest load shows no raw keys and fetches one dictionary file. The panel
  opens once the page has hydrated.
- A language switch (en → ru) takes 129 ms without a reload. It fetches `ru.js`, and the old
  dictionary is dropped from memory.
- With the dictionary file delayed by 2.5 s and the cache cleared, the page kept its server-rendered
  Russian text and showed no keys while hydration waited. After the file arrived the page became
  interactive, with no console errors.
