# Browser spot-check — i18n migration

Real Chrome via the chrome-devtools MCP (`chrome-devtools-mcp` 1.9.0,
driven over the MCP stdio protocol). Locale is set through the
`rw_locale` cookie, which is exactly what `i18n/server.ts` reads.

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
