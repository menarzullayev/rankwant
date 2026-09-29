# Statement builder prototype → production parity

Source: `prototypes/statement-builder.html` (in-page `.page`, not review chrome `.bar`/`.bar2`).

Status legend: **done** | **partial** | **missing** | **n/a** (platform differs by design).

| Prototype block | CHOICE / P0 | Production | Status |
| --- | --- | --- | --- |
| Two-column resizable split | 1 | `ProblemWorkspace.tsx` (`rw:problem-split-pct`) | done |
| Editor collapse | 2 | `ProblemWorkspace` + toolbar | done |
| Icon rail 56px | 3 | `AppSidebar` (full nav, not thin rail) | n/a |
| Header row 1 (code, title, limits chip, text size) | 4, 9 | `ProblemDescription` header | done |
| Header row 2 (badges, stats) | 4 | `ProblemDescription` metadata | done |
| Editorial below samples (P0) | P0 | `ProblemDescription` + `Editorial` | done (when published) |
| Sample table + per-cell copy | 5 | `SampleTests.tsx` | done |
| Statement typography 16/1.7 | 6 | `StatementSize` + `rw-md` | partial |
| Mono 14/1.6 in samples | 7 | sample `pre` classes | done |
| Inline math chip | 8 | `Markdown` / KaTeX | done |
| Statement text size A± | 9 | `StatementSize.tsx` | done (moving to row 1) |
| Card hairline + shadow | 10 | `Card` / kit | partial |
| Section separation (space/line/card) | 11 | `StatementSectionMode` | done |
| Prose max 100ch | 12 | `rw-md` measure | partial |
| Per-sample run icon + inline result | 13–14 | `SampleTests` + `ProblemSolveProvider` | done |
| Submit in editor panel | 14 | `SubmitPanel` | done |
| Verdict UI modes tab/column/toast/modal | 15–16 | `VerdictLayoutModeToggle` + layers | done |
| Empty/loading verdict states | 16 | `SubmitPanel` + `Loading` | done |
| Tablet/mobile bottom sheet + Kod FAB | 17–18 | `ProblemWorkspace` | done |
| Mobile section jump chips | 18 M4 | `StatementSectionNav` | done |
| WCAG targets | 19 | kit + a11y checks | ongoing |
| ProblemActions fav/votes/stars | P0 | `ProblemActions.tsx` | done |
| Editorial gate | P0 | inline on description + tab | done |
| Limits in header badge | P0 | `Badge` in header | done |
| Constraints inside statement | P0 | `Markdown` statement body | data-dependent |
| Page tabs (Tavsif / Urinishlar / …) | — | `ProblemTabs` + routes | done |
| Solve timer | — | `ProblemSolveTimer` | done |
| Meta accordion (topics/similar) | — | `ProblemMetaAccordion` | extra vs prototype |

## Verification

- Manual: open `/problems/<slug>?tab=description` at 390 / 834 / 1440 widths.
- Automated: `npm run typecheck`, `npm run lint`, `tools/check_i18n.py` after locale keys change.

### Measured (2026-09-29)

| Surface | URL | `<h1>` count | Statement-builder chrome |
| --- | --- | --- | --- |
| Local dev (branch `fix/problem-workspace-dup`) | `http://localhost:8310/...` | **1** | Section mode, verdict layout, collapse, sample ▶, `</> Code` FAB, section nav, updated sample hint |
| Preview stack (web image rebuilt from working tree) | `http://127.0.0.1:8300/...` | **1** | Same as dev: Space/Line/Card, Tab/Column/Toast/Modal, collapse, sample ▶, section chips @390px, `</> Code` FAB, English submit tabs |

Width matrix (2026-09-29, `a-plus-b`): **390** — section jump chips + Code FAB; **834** — bottom sheet + FAB (tablet); **1440** — sidebar + two-pane workspace + column verdict empty state in statement column. Verdict **Column** mode toggled: empty guidance in statement + editor panel cross-reference (CHOICE 16–17).

**Note:** 8300 was refreshed via `docker compose … build web && up -d --no-deps web` from uncommitted parity sources; merge PR #310 so the image survives the next deploy from `main`.

**Gate (durability):** commit parity files, merge, and deploy web from `main` — ad-hoc local rebuild is verification only.

Dev SSR against loopback API: set `API_BASE_INTERNAL=http://127.0.0.1:8301/api/v1` and use `npx next dev -p 8310` (not `npm run dev`, which pins port 3000). Loopback SSR uses `node:http` + `Host: localhost` in `api.server.ts`.

## Open tranches

1. **Ship** — commit all parity files on `fix/problem-workspace-dup`, extend or supersede PR #310, merge, deploy web.
2. **Post-deploy** — re-run manual width matrix on **8300**; close CHOICE 19 (WCAG spot-check) if needed.
3. **Visual** — limits icon row (gallery #3) remains n/a unless product asks; card/measure tokens already use kit + `theme.css`.
