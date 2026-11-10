| Sana | Qaror | Kodda qayerda |
|---|---|---|
| 2026-09-20 | **Bosh sahifa CSS inline** (HITL: lh-inline-css). Lighthouse Slow 4G: 2 ta render-blocking `/_next/static/chunks/*.css` (~4.5 + 23 KiB, ~150 ms). App Router da `optimizeCss`/Critters yo'q. `experimental.inlineCss: true` — `<style>`, alohida CSS so'rovi yo'q. Cloudflare `email-decode` alohida | `apps/web/next.config.ts`; `tools/check_decisions.py` → `homepage_css_is_inlined`; salbiy test 1 ta |
