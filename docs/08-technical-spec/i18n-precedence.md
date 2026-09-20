# Locale precedence: the link, then the device, then the account

**Status:** accepted (2026-09-14; URL parameter added 2026-09-19) · **deliberate divergence from [ADR-0017](../07-adr/0017-profile-and-settings.md)**

## The rule

| State | Wins | Effect |
|---|---|---|
| `?lang=<code>` in the URL | the link | the cookie is rewritten to the same code, so later pages follow |
| `rw_locale` cookie holds a locale code | the device | account locale is *not* consulted |
| `rw_locale=auto` | the device (explicitly automatic) | detected from `Accept-Language` |
| no cookie at all | the account (as a seed only) | account locale is copied to the cookie |

Resolution order as implemented: `?lang=` → cookie → `Accept-Language` →
`uz` (owner decision S5, 2026-09-19).

In one sentence: **a shared link carries its own language; otherwise the device
chooses, and the account only seeds a device that has not chosen yet — it is
also the language used for email.**

The link is the only source that outranks the device, and it does so for one
reason: the person opening it has not chosen anything, so there is no device
preference to respect — only the sender's intent. It is also the narrowest
possible override: it applies once and then *becomes* the cookie, so no
internal link has to be rewritten (S5b). An explicit pick in the switcher
strips `?lang=` for the same reason in reverse — leaving it would let the stale
parameter beat the new choice on the next render.

## Why this diverges from ADR-0017

ADR-0017 settles appearance (theme, style, a11y) with **account wins**: sign in
on another device and the site looks the same. Language does not follow that
rule, on purpose:

- Language is a property of the *situation*, not of the person. The same
  person may read Uzbek on a phone and English on a work laptop. An account
  value that overrides the device would overwrite that choice on every
  sign-in.
- Switching language is a per-session act. A user who picks Russian on a
  shared machine expects Russian for that session, not a permanent account
  change.
- The account locale still matters — it is the only signal available when
  sending email, where there is no device to ask.

So the two policies coexist: appearance is account-scoped, language is
device-scoped. This is intentional, not an oversight.

## The `auto` marker

Clearing the cookie outright cannot express "automatic", because a *missing*
cookie already means "has not chosen yet" — and that triggers the account
seed, which would immediately undo the choice. `rw_locale=auto` therefore
encodes a third state:

- cookie absent → not chosen; account seed applies
- `rw_locale=auto` → chosen to be automatic; account seed does **not** apply
- `rw_locale=<code>` → chosen a specific language

`getLocaleState()` in `apps/web/src/i18n/server.ts` is the single reader of
these three states and returns `{ locale, auto }`. The decision itself lives in
the pure function `resolveLocale()` (`apps/web/src/i18n/resolve.ts`), so the
order can be unit-tested without a request, a cookie jar or `next/headers`.

## Where this is enforced

- `apps/web/src/i18n/locale-params.ts` — the three names (`rw_locale`, `lang`,
  `x-rw-locale`) in one place, because the edge proxy cannot import
  `next/headers`
- `apps/web/src/i18n/resolve.ts` — `resolveLocale()`: `?lang=` → cookie →
  header → default
- `apps/web/src/i18n/server.ts` — `getLocaleState()` reads the three sources
  and hands them to `resolveLocale()`
- `apps/web/src/proxy.ts` — turns `?lang=` into the request header (this
  response) and into the cookie (later ones)
- `apps/web/src/context/PrefsSync.tsx` — seeds the cookie from the account only when no cookie exists
- `apps/web/src/layout/LocaleSwitch.tsx` — writes `auto` or a locale code, and
  strips `?lang=`

⚠️ Ordering inside the proxy is load-bearing. `NextResponse.next()` copies
`request.headers` into `x-middleware-request-*` **at call time** (measured:
`next@16.3.4`, `dist/server/web/spec-extension/response.js:128`), so a header
written *after* the response is built never reaches the current render. The
page then answers in the cookie's language and the feature looks like it
"works one request late". `tools/check_decisions.py` asserts the order, not
just the presence of the call.

⚠️ If you are here because you noticed language does not follow ADR-0017's
"account wins" rule: that is the point of this document. Changing it back
would silently discard the device choice on every sign-in.

⚠️ **Re-affirmed 2026-09-19 (owner decision S6 = T6-a).** The owner was shown
three options — keep the current rule, make the account win, or add a visible
"language: device / account" control in settings — and chose **to keep it as
it is, with no new control**. So do not "improve" this by adding a
precedence switch: it was offered and declined. The same decision also
accepted that the second-device behaviour stays **unmeasured** for now; if
you do measure it (a signed-in account whose locale differs, opened in a
clean browser context), report the result rather than acting on it.

### What CI checks, and what it cannot

Three checkers guard this area. They are complementary — no one of them
covers the others' blind spots.

| Checker | Guards | Cannot see |
| --- | --- | --- |
| `tools/check_i18n.py` | every key present in all 10 dictionaries, no blank values, every key the code calls exists, dynamic template families | runtime behaviour |
| `tools/check_locales_parity.py` | `User.Locale` ↔ `settings.LANGUAGES` ↔ `email_text.LOCALES` stay in step | anything outside those three lists |
| `tools/check_i18n_runtime.mjs` | `t()`'s fallback path, measured in the real module | source completeness |

The runtime check exists because the first two read *text*, so they cannot
detect the difference between `throw new Error(...)` and `return key`. It
runs the real `messages.ts` under Node in four combinations
(server/client × dev/prod) and asserts 13 measured values. Among them: a
missing key **throws** in dev, the same key is logged **once** in prod, the
registry is shared through `globalThis`, and `evictOtherLocales` leaves one
dictionary in the browser but none of the ten on the server.

Since 2026-09-18 the browser gets its dictionary as a separate cached file
(`/i18n/<locale>.js?v=<content hash>`, `app/i18n/[file]/route.ts`), not as a
prop serialized into every page. The server registers all ten languages in
the shared registry, where both server components and SSR-rendered client
components read them. If the file has not run by hydration, `LocaleProvider`
suspends until it has. Measured: HTML 142 → 64 kB, render CPU −45%
(`docs/research/2026-09-18-homepage-profile`).
`tools/check_negative.py` mutates the source to prove each of those
assertions can fail; a check that cannot fail is not a check.

⚠️ `check_i18n_runtime.mjs` needs Node. `tools/ci-local.sh` and
`tools/check_negative.py` both read the `NODE` environment variable and
fail loudly if it is absent — they never skip the step, because a silent
skip is exactly the "green but lying" outcome this project has been bitten
by four times.

## Caching — and a framework limit we could not work around

Because the response depends on `Accept-Language`, correct HTTP caching requires
`Vary: Accept-Language` on every response. **We set it, and Next.js 16 discards
it.** This is measured, not assumed:

```
$ curl -s -D - -H 'Host: rankwant.uz' http://127.0.0.1:8300/
Vary: rsc, next-router-state-tree, next-router-prefetch,
      next-router-segment-prefetch, Accept-Encoding
```

`Accept-Language` is absent — while the *same URL* returns three different
documents:

```
Accept-Language: ru → lang="ru"
Accept-Language: zh → lang="zh"
Accept-Language: kk → lang="kk"
```

Three placements were tried and all three were **measured** to fail:

1. `next.config.ts` `headers()` — the rule *is* emitted into
   `routes-manifest.json`, but never reaches the response. Next.js overwrites
   `Vary` with its own list.
2. `src/proxy.ts` (the Next.js 16 file convention; `middleware.ts` is rejected
   in 16.x) using `headers.set("Vary", ...)` — a control header proves the proxy
   runs: `x-rw-probe: alive` survives while `Vary` does not. The clobbering is
   specific to `Vary`.
3. The same proxy using `headers.append("Vary", ...)`. The hypothesis was that
   Next.js replaces the *value* but preserves a *list*, so appending would
   survive. It does not — the response is byte-for-byte the same as (2). The
   replacement is unconditional.

This is undocumented internal behaviour — the `proxy` file-convention reference
does not mention `Vary` at all, and the `headers` config reference does not
either. Note that `middleware.ts` and `proxy.ts` cannot coexist; Next.js 16
fails the build with *"Both middleware file and proxy file are detected"*.

⚠️ The lesson from (3): when a framework discards a header, check whether it
discards the *value* or the *key*. Here it is the key, so no amount of
in-process header manipulation will work — the fix has to sit outside Next.js.

**Homepage cache (2026-09-19):** guest GET `/`, `/login` (faqat `?tab=`),
`/register`, `/terms`, `/privacy` is cached. The cached body is
forced to `uz` via `x-rw-locale` (`home-cache.ts`); `?lang=` and locale/session
cookies are excluded from the cacheable set, so `Accept-Language` cannot
poison that one URL.

**Archive list (2026-09-20 HITL problems-al):** guest GET `/problems` with an
empty query is also cached, but **not** forced to `uz`. Origin instrumentation
adds `Vary: Accept-Language` (`guest-al` mark). Cloudflare Free does not key
on `Vary` by itself; the Cache Rule sets `vary.headers.accept-language`
to `normalize` over the ten UI locales. `?page=` / `?level=` / `?lang=` stay
uncached. Logged-in HTML stays `private, no-store` (favourites / solved).
Worker route is `problems/*` (slug only) so the list does not burn the 100k
Worker quota.

Other routes stay `no-store`. The `Vary` gap below still applies to
non-uz-forced HTML.

⚠️ Since 2026-09-19 the locale also travels in the URL (`?lang=<code>`). That
sharpens the same defect rather than adding a second one: one path now has
several URLs whose bodies differ, so a cache keyed on the URL alone can hand a
`?lang=ru` body to a `?lang=uz` request. The cookie write softens it — later
requests carry the cookie — but it does not remove it, because the *first*
response still has to be keyed correctly. Guest GET `/` is not cached when a
query string is present, so `/?lang=ru` stays a private miss. Same for
`/problems?lang=`.

**What must happen before caching other routes** (HITL 2026-09-20 cf-transform:
applied): a Cloudflare Response Header Transform Rule **adds**
`Vary: Accept-Language` on HTML that is **not** the uz-forced guest-cache set
(`/`, `/login`, `/register`, `/terms`, `/privacy`). `add` keeps Next's RSC
tokens; `set` would wipe them. Those bodies are forced `uz` — varying them
would fragment the 100k homepage cache without changing the HTML.
`/problems` is **not** in that exclusion: it is locale-aware. `cloudflared`
still cannot rewrite headers.

Former options (not chosen): in-front reverse proxy; `/uz/` prefix.

## Known gaps

- **Content names.** `topicName()` / `localName()` only read `name_uz`,
  `name_ru`, `name_en`. Users of the other seven languages see Uzbek topic and
  skill names. This is a *content* task (145 topics), tracked separately —
  not something the locale switcher can fix. The switch marks the fallback at
  the point of use instead of claiming full coverage.
- **Date formats.** `kaa`, `ky`, and `tg` are not in the ICU database, so
  `intlLocale()` falls back to `uz` rather than letting `toLocaleString`
  silently degrade to `en-US`. Users of those three languages therefore see
  Uzbek date formatting — closer than US formatting, but still not their own.
