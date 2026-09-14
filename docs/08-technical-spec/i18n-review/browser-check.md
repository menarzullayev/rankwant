# Browser spot-check — i18n migration

Real Chrome via the chrome-devtools MCP (`chrome-devtools-mcp` 1.9.0).
The MCP tools were absent from this session's tool index, so the server was
driven directly over the MCP stdio protocol — same browser, same evidence.

Locale is set through the `rw_locale` cookie, which is exactly what
`i18n/server.ts` reads.

Verdict: **PASS**

| locale | page | result | body chars | leaked keys | missing text | crashed | console errors |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `ru` | `/rating` | ✅ | 2418 | — | — | no | 0 |
| `ru` | `/problems` | ✅ | 3374 | — | — | no | 0 |
| `kaa` | `/rating` | ✅ | 2402 | — | — | no | 0 |
| `kaa` | `/problems` | ✅ | 3405 | — | — | no | 0 |

`leaked keys` — a `namespace.something` token visible in the rendered
text, i.e. a `t()` call that never resolved.

`crashed` — the page shows a React error boundary string instead of
content. This is the failure mode that `curl 200` cannot detect.

## The control that makes this evidence, not a guess

A passing row only means something if the locale switch actually happened. If
the cookie were ignored, every page would render Uzbek and the `ru` rows would
have failed on `missing` — but it is worth showing the raw text rather than
inferring it. Same page, three cookies:

| cookie | rendered from `document.body.innerText` |
| --- | --- |
| `rw_locale=ru` | `Перейти к содержимому … Задачи · Попытки · Тесты … Соревнования · Арена · Дуэль · Чемпионат` |
| `rw_locale=kaa` | `Tiykarǵı mazmunǵa ótiw … Máseleler · Urınıslar · Testler … Jarıslar · Arena · Duel · Xakaton` |

Two different languages come back, so the cookie drives the render.

## Why `kaa` looks like Uzbek (and is not a silent fallback)

`kaa` renders `Máseleler` where `uz` renders `Masalalar` — close, but not the
same. Measured overlap against the `uz` source dictionary:

| locale | keys | identical to `uz` |
| --- | --- | --- |
| `kaa` | 1344 | 123 (9.2%) |
| `en` | 1344 | 58 (4.3%) |
| `tr` | 1344 | 46 (3.4%) |
| `ru`, `kk`, `ky`, `tg`, `zh` | 1344 | 24–25 (1.8–1.9%) |

`kaa` sharing 9.2% with Uzbek is expected: the two are sister languages and many
terms (`Arena`, `Duel`, `Menyu`, `Chempionat`) are genuine loanwords. A locale
stuck on the source dictionary would show ~100%, not 9%. The ratio is the
check; eyeballing two similar sentences is not.

## Follow-up: the `common.empty` rename

The bare `empty` key became `common.empty` (10 dictionary declarations, 34
call sites in 31 files). `tsc` proves the key exists and the call
type-checks; it does not prove the text reaches the screen.

`common.empty` is the fallback shown on every empty list, so `/blog` was
opened in three locales and the rendered text compared against the dictionary
value:

| locale | `<html lang>` | rendered | expected |
| --- | --- | --- | --- |
| `uz` | `uz` | `Hozircha bo'sh` | ✅ same |
| `ru` | `ru` | `Пока пусто` | ✅ same |
| `kaa` | `kaa` | `Házirshe bos` | ✅ same |

`<html lang>` is recorded because it proves the locale actually switched —
otherwise a matching string could just be a stale page.

Two traps met while writing this check, both worth remembering:

1. **The first locale reads as MISSING.** A freshly launched browser sits on
   `about:blank`; the cookie written there is discarded on the first real
   navigation. The tell was `html.lang='kaa'` on the `uz` row. Fix: write the
   cookie, navigate, write it again, navigate.
2. **`/attempts` was the wrong page.** It requires sign-in, so the empty
   state never renders and the check reported three false MISSINGs. A public
   page with an empty data set (`/blog`, `/updates`, `/roadmaps`) is required,
   confirmed first with `curl … | grep "Hozircha bo'sh"`.

## A real defect found in the content layer: country names

Checking the deliberately deferred files turned up a live bug.

`lib/countries.ts` used the `country-names.ts` table only for `uz` and `ru`
and fell through to `Intl.DisplayNames` for everything else. Measured in
Chrome, ICU has **no region data** for `kaa`, `kk`, `ky` or `tg` — it silently
returns English. A Karakalpak user reading an otherwise translated profile
would see `Germany`, `United States`, `China`.

| locale | before | after |
| --- | --- | --- |
| `uz` | `Germaniya` (table) | `Germaniya` |
| `kaa` | `Germany` ← leaked | `Germaniya` |
| `ru` | `Германия` (table) | `Германия` |
| `kk` | `Germany` ← leaked | `Германия` |
| `ky` | `Germany` ← leaked | `Германия` |
| `tg` | `Germany` ← leaked | `Германия` |
| `tr` | `Almanya` (ICU) | `Almanya` |
| `zh` | `德国` (ICU) | `德国` |
| `es` | `Alemania` (ICU) | `Alemania` |

The fix mirrors the pattern already used by `lib/regions.ts`: `CYRILLIC`
locales take the Russian name, `LATIN_UZ` takes the Uzbek one, and the rest
keep ICU.

### Node is not a valid ICU oracle here

The first measurement was run under Node, which reported Russian for `kk`,
`ky` and `tg` — so the defect looked like `kaa` only. Chrome disagreed: all
four fall through to English. The two runtimes ship different ICU data, and
the app runs in a browser. **Measure ICU in the engine that will execute it.**

### A regression the fix introduced, caught before commit

Adding `tr` to `LATIN_UZ` — copying `regions.ts` literally — replaced Turkish
`Almanya` with Uzbek `Germaniya`. Region names have no Turkish ICU data;
country names do. The lists are similar but must not be identical, and
`check_country_locales()` now enforces the distinction with two negative
tests.



