# Browser check — weakest locales (kk, ky, tg, kaa)

Real Chrome through the chrome-devtools MCP, over the MCP stdio
protocol. Base: `http://localhost:8300`. The active locale is set
through the `rw_locale` cookie — the same cookie
`i18n/server.ts` reads.

Verdict: **PASS**

## A. The locale cookie really switches the language

| locale | `<html lang>` | first heading |
| --- | --- | --- |
| `uz` | `uz` | Asosiy mazmunga o'tish |
| `kk` | `kk` | Негізгі мазмұнға өту |
| `ky` | `ky` | Негизги мазмунга өтүү |
| `tg` | `tg` | Гузаштан ба мӯҳтавои асосӣ |
| `kaa` | `kaa` | Tiykarǵı mazmunǵa ótiw |

`<html lang>` is the server's own statement of the active locale.
If it did not change, a locale comparison would be meaningless —
this is the control that makes the rest of the table trustworthy.

## B–D. Render health per locale and page

| locale | page | result | `<html lang>` | body chars | leaked keys | crashed | console errors |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `kk` | `/rating` | ✅ | `kk` | 2224 | — | no | 0 |
| `kk` | `/problems` | ✅ | `kk` | 2846 | — | no | 0 |
| `ky` | `/rating` | ✅ | `ky` | 2229 | — | no | 0 |
| `ky` | `/problems` | ✅ | `ky` | 2863 | — | no | 0 |
| `tg` | `/rating` | ✅ | `tg` | 2222 | — | no | 0 |
| `tg` | `/problems` | ✅ | `tg` | 2850 | — | no | 0 |
| `kaa` | `/rating` | ✅ | `kaa` | 2237 | — | no | 0 |
| `kaa` | `/problems` | ✅ | `kaa` | 2876 | — | no | 0 |

`leaked keys` — a literal `namespace.key` token in the rendered
text: a `t()` call that never resolved.

`crashed` — a React error-boundary string instead of content.
This is the failure mode a `curl 200` cannot detect.

## Why these four locales

`kk`, `ky`, `tg` and `kaa` have **no ICU region data in Chrome**, so
`Intl.DisplayNames` falls back to English for them. Country names
for these locales come only from the table in `lib/countries.ts`.
That table previously served just `uz` and `ru`, so these four
rendered `Germany` (English) inside an otherwise translated UI.

The defect was invisible to every static checker and to a Node
measurement (Node reports Russian for `kk`/`ky`/`tg`; Chrome does
not). Only a browser measurement proves the fix.

## E. Country-name table coverage

The four weak locales take country names **only** from the table in
`lib/country-names.ts` — Chrome has no ICU region data for them and
`Intl.DisplayNames` silently returns English. Measured:

- `CODES` in `countries.ts`: **249**
- rows in `country-names.ts`: **249**
- codes without a row: **0**
- rows not in `CODES`: **0**
- rows with a blank value: **0**

A code missing from the table does not throw; it falls back to ICU and
renders English. The counts above are now locked by
`check_i18n.check_country_table_coverage()`.

### Values per locale (from the table, not guessed)

| code | O'zbekcha | Qoraqalpoqcha | Qozoqcha | Qirg'izcha | Tojikcha | Ruscha | Turkcha | Xitoycha |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `DE` | Germaniya | Germaniya | Германия | Германия | Германия | Германия | _(ICU)_ | _(ICU)_ |
| `KZ` | Qozogʻiston | Qozogʻiston | Казахстан | Казахстан | Казахстан | Казахстан | _(ICU)_ | _(ICU)_ |
| `UZ` | Oʻzbekiston | Oʻzbekiston | Узбекистан | Узбекистан | Узбекистан | Узбекистан | _(ICU)_ | _(ICU)_ |
| `TR` | Turkiya | Turkiya | Турция | Турция | Турция | Турция | _(ICU)_ | _(ICU)_ |
| `CN` | Xitoy | Xitoy | Китай | Китай | Китай | Китай | _(ICU)_ | _(ICU)_ |
| `US` | Amerika Qo‘shma Shtatlari | Amerika Qo‘shma Shtatlari | Соединенные Штаты | Соединенные Штаты | Соединенные Штаты | Соединенные Штаты | _(ICU)_ | _(ICU)_ |

`_(ICU)_` marks the locales that keep the runtime's own name
(`en`, `tr`, `zh`, `es`). `tr` must stay on ICU: adding it to the
table regressed `Germany` -> `Germaniya` instead of `Almanya`.

