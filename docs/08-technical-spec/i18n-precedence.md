# Locale precedence: the device wins

**Status:** accepted (2026-09-14) · **deliberate divergence from [ADR-0017](../07-adr/0017-profile-and-settings.md)**

## The rule

| State | Wins | Effect |
|---|---|---|
| `rw_locale` cookie holds a locale code | the device | account locale is *not* consulted |
| `rw_locale=auto` | the device (explicitly automatic) | detected from `Accept-Language` |
| no cookie at all | the account (as a seed only) | account locale is copied to the cookie |

In one sentence: **the device chooses the language; the account only seeds a
device that has not chosen yet, and it is the language used for email.**

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
these three states and returns `{ locale, auto }`.

## Where this is enforced

- `apps/web/src/i18n/server.ts` — `getLocaleState()` resolves cookie → header → default
- `apps/web/src/context/PrefsSync.tsx` — seeds the cookie from the account only when no cookie exists
- `apps/web/src/layout/LocaleSwitch.tsx` — writes `auto` or a locale code

⚠️ If you are here because you noticed language does not follow ADR-0017's
"account wins" rule: that is the point of this document. Changing it back
would silently discard the device choice on every sign-in.

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
(server/client × dev/prod) and asserts 11 measured values — including that
a missing key **throws** in dev, that the same key is logged **once** in
prod, and that `registerMessages(..., evict: true)` leaves one dictionary.
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

**Why this is latent rather than live:** responses currently carry
`Cache-Control: private, no-cache, no-store, max-age=0, must-revalidate`, so no
shared cache may store them. The defect becomes a cache-poisoning bug the day
caching is enabled.

**What must happen before caching is enabled** (options, none yet applied):

- put a small reverse proxy in front of Next.js that appends `Accept-Language`
  to `Vary`;
- or set a CDN Transformation Rule at the edge;
- or add the locale to the URL (`/uz/...`), which removes the dependence on
  `Accept-Language` entirely — the option already recorded as a later step in
  the decision log.

`cloudflared` cannot do it: version `2026.9.1` has no header-rewrite directive
in tunnel ingress rules.

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
