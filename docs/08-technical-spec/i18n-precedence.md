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

## Caching

Because the response depends on `Accept-Language`, every response carries
`Vary: Accept-Language` (set in `apps/web/next.config.ts`). Today responses are
`no-store`, so this is belt-and-braces — but the moment any shared cache or
`revalidate` is introduced, a missing `Vary` poisons the cache: one URL would
serve Russian users an English page.

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
