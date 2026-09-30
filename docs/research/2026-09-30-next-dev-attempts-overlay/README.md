# Next dev issues overlay on attempts tab (2026-09-30)

## Symptom

On `http://127.0.0.1:8312/problems/a-plus-b?tab=attempts`, Next.js dev shows an
issues badge; stack frame points at `apps/web/src/app/layout.tsx` (~267, theme
init `<script nonce={…}>`).

## Observed

- Urinishlar table still renders (attempt rows visible).
- Overlay also appeared on prior session when navigating to attempts.
- `.preview-server.log` is unrelated (static `index.html` server).

## Likely contributors (needs confirmation)

1. **`next.config.ts` comment (2026-09-30):** Turbopack dev + `@headlessui/react`
   Combobox — `aria-expanded` / hydration mismatch on filter UI (attempts page uses
   filters). `transpilePackages: ["@headlessui/react"]` mitigates production;
   dev overlay may remain benign.
2. **CSP nonce:** `layout.tsx` reads `x-nonce` from `headers()`. If a dev request
   path skips `src/proxy.ts`, inline theme scripts could mismatch CSP — **Needs
   verification** on whether `proxy.ts` runs for all `next dev` routes on port 8312.

## Impact on attempt-live SSE

Backend smoke (`tools/verify_live_judge_progress.py`) passes independently of this
overlay. UI live progress during submit was not fully captured in automation; not
proven blocked by this overlay.

## Follow-up

- Reproduce with `next dev` vs production build on same URL.
- If Combobox-only, accept dev-only noise or add Playwright regression on prod build.
