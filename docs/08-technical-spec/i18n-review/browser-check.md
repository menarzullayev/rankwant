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


