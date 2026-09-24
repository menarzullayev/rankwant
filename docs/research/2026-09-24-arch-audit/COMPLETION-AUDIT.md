# RW-ARCH-100 — Completion claim audit (12 open tasks)

**Date:** 2026-09-24
**Method:** `completion-claim-verification` — every status is treated as a
*claim*, not a measurement. A claim is only accepted when a cited artifact
proves it. `all()` semantics for path checks; unknown status = ERROR.

**Board:** `docs/tasks/BOARD-ARCH-100.html`
**State at audit start:** 5 done (001–004, 015) / 12 todo (005–014, 016, 017)

---

## 1. Verdict table

| ID | Claim (board title) | Measured state | Verdict | Artifact / evidence |
|----|--------------------|----------------|---------|---------------------|
| 005 | Type safety — OpenAPI → TS generatsiya | Schema exists (`apps/api/openapi/schema.yml`, 18 847 lines); CI diffs it; **no TS generator**, no `*.gen.ts`, no `openapi-typescript` dep | **GAP** | `grep openapi-typescript apps/web/package.json` → no match; `find -name "*.gen.ts"` → empty |
| 006 | Validation — zod sxemalari qatlami | Backend has 19 `serializers.py` (DRF); **zod not installed**, no web validation layer | **GAP** | `grep zod apps/web/package.json` → no match |
| 007 | Observability — oddiy logging | Backend: `LOGGING` dict in `config/settings.py:472` + 33 modules `import logging`. Web: only `lib/analytics.ts` (`track()` → `/analytics/events/`). **No web logger** | **GAP (web half)** | `apps/api/config/settings.py:472`; `apps/web/src/lib/analytics.ts` |
| 008 | Security — CSP va xavfsizlik headerlari | Backend cookies hardened (`SESSION_COOKIE_HTTPONLY/SAMESITE/SECURE`, `CSRF_*`, CORS + trusted origins). **No CSP / X-Frame-Options / HSTS**; `next.config.ts` has no `headers()`; `proxy.ts` sets only `Vary` + `Cache-Control` | **GAP** | `apps/api/config/settings.py:205-233`; `apps/web/next.config.ts` (no `headers`); `apps/web/src/proxy.ts:176,181` |
| 009 | Feature flags — umumiy flag tizimi | Only `lib/experiments.ts`: one hard-coded `GEO_EXPERIMENT`, cookie `rw_exp`, `parseVariants`. **Not a general flag system** | **GAP** | `apps/web/src/lib/experiments.ts` |
| 010 | Accessibility — axe avtomatik testi | Playwright harness exists (`tests/e2e/`, 6 specs, 4 browsers) but **no `@axe-core/playwright`**, no a11y spec | **GAP** | `tests/e2e/package.json` deps = `@playwright/test` only; `ls tests/e2e/specs` → 6 non-a11y specs |
| 011 | Auth — `Can` permission komponenti | Ad-hoc gate in `admin/layout.tsx`: `if (!user?.is_staff)`. Repeated inline in `UserMenu.tsx:123`, `CommandPalette.tsx:67`. **No `<Can>` component** | **GAP** | `apps/web/src/app/(site)/admin/layout.tsx:19`; `grep "<Can"` → empty |
| 012 | Error handling — global shoxlash + DataState | `lib/hooks/useAction.ts` has `describeError()` + busy/error/done; **no `DataState` component**, no code-based branching table | **GAP** | `grep -rn DataState apps/web/src` → empty; `components/ui/` has `EmptyState`/`Verdict` only |
| 013 | Monorepo — `packages/` karkasi | **No `packages/`**, no root `package.json`, no `pnpm-workspace.yaml`. `docs/07-adr/0009-monorepo.md` records the intent | **GAP (intent only)** | `ls packages/` → absent; `ls package.json` → absent |
| 014 | State — server state hook'lari | `lib/hooks/{useLoad,useAction,index}.ts` exist and are consumed by 15 files (all `features/account/*`, `HackPanel`, `AttemptView`, `UsersAdmin`) | **PARTIAL→OK**; `useLoad` is a bare `useEffect`+`fetch`, **no cache/dedup/revalidate** | `apps/web/src/lib/hooks/`; 15 consumer files |
| 016 | Testing/Perf — visual regression + bundle budget | Playwright E2E exists; **no visual-regression project** (`toHaveScreenshot`), **no bundle budget** (no `size-limit`/`bundlesize`, no CI budget step) | **GAP** | `grep size-limit` → empty; `tests/e2e/playwright.config.ts` has no screenshot assertion project |
| 017 | Yakuniy tekshiruv — barcha ko'rsatkichlar 100% | Cannot be 100 % while 005–016 have gaps | **BLOCKED by 005–016** | this document |

---

## 2. What is genuinely DONE (verified, not claimed)

These were audited with `all()` path semantics and negative tests:

| ID | Artifact that satisfies the claim |
|----|-----------------------------------|
| 001 | `tools/check_imports.py` — 1427 `@/…` imports, all resolve |
| 002 | 13 × `features/*/index.ts` barrels; `tools/check_features.py` clean |
| 003 | `tools/check_features.py` rule 3 (global layer ⇏ `@/features/*`) clean |
| 004 | `tools/check_features.py` rule 4 (client/server barrel split) — `auth`/`profile` split |
| 015 | `docs/08-technical-spec/ui-architecture.md` + 2 CI gates wired |

Negative tests performed earlier in the session: injecting a feature→feature
violation → exit 1; injecting a server-only barrel export → exit 1. Both
reverted. **The checks are not vacuous.**

---

## 3. Residual risk — what is unverified and why

1. **No runtime verification of 008.** CSP can only be validated against a
   live origin (`Content-Security-Policy-Report-Only` + real traffic). A
   static header is a *claim* until a browser reports zero violations.
2. **014 is "OK but thin".** `useLoad` has no cache, dedup, or revalidation.
   Calling it a "server state hook layer" at 100 % overstates it; it is a
   fetch-on-mount helper. Honest level: ~75 %.
3. **010/016 cannot be run here.** Both require a live compose stack (the
   E2E README states judge needs `--privileged`); the specs exist but were
   not executed in this session.
4. **013 is an architecture decision, not a code change.** Creating
   `packages/` without moving a real shared module would produce an empty
   skeleton — satisfying the letter, not the purpose.
5. **005/006/009 each introduce a new runtime dependency** (`openapi-typescript`,
   `zod`). Installing deps changes lockfiles and CI install time.

---

## 4. Honest final status

- **Technical implementation of 001–004, 015:** PASS.
- **Audit evidence completeness for those five:** COMPLETE.
- **Tasks 005–013, 016:** NOT DONE. Each is a confirmed, real gap — none was
  falsely marked done, and none can be closed by documentation alone.
- **Task 014:** FUNCTIONAL but not at the claimed 100 %.
- **Task 017:** BLOCKED — it is the aggregate of 005–016.

**Conclusion:** the 5 DONE claims survive verification; all 12 TODO claims are
correctly TODO. The board is honest. Moving the 12 to DONE requires real
implementation work (5 new dependency families, 3 new checkers, 2 new test
projects), which is a substantial build — not a verification exercise.
