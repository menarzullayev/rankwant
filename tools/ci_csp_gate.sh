#!/usr/bin/env bash
# Prove the CSP nonce gate is LIVE against the running stack before CI is green.
#
# WHY THIS EXISTS
# ---------------
# 2026-09-24: `proxy.ts` minted a nonce per request and Next wrote it into its
# OWN inline tags — but never into the `<script>` tags the application writes
# by hand. CSP lists `'strict-dynamic'`, which makes `'self'` irrelevant, so a
# same-origin tag without the nonce is still blocked. Measured in the Chrome
# console on the live `/login`: four scripts blocked — the three pre-hydration
# bootstrap tags (`theme`, `style`, `appearance`) and `/i18n/<lang>.js`.
#
# The consequences were a white flash on every dark-mode load (the theme class
# was never applied before hydration) and `LocaleProvider` falling back to
# `loadDictionary()` on every page load — the race the `<head>` script exists
# to win. Every gate stayed green while that was true, because nothing looked
# at the rendered page.
#
# WHERE IT RUNS
# -------------
# Nightly, next to the visual gate, because it needs a running stack. It does
# NOT rebuild: it reads the HTML the stack already serves, so it costs seconds
# rather than the visual gate's ~20 minutes.
#
# Skips LOUDLY when no stack is listening, so a missing target is never
# mistaken for a passing gate.
set -euo pipefail

BASE="${E2E_BASE_URL:-http://localhost:3400}"

if ! curl -sf -o /dev/null "$BASE/"; then
  echo "::warning::Web stack $BASE da javob bermadi — CSP darvozasi O'TKAZIB YUBORILDI"
  echo "Bu qadam o'lchovsiz qoldi. Stack ko'tarilgan muhitda u qayta yuritilishi kerak:"
  echo "  E2E_BASE_URL=$BASE python tools/check_negative.py --group csp_nonce"
  exit 0
fi

echo "--> Stack $BASE da javob berdi, CSP qamrovi o'lchanadi"
python tools/check_csp_nonce.py --base "$BASE"
E2E_BASE_URL="$BASE" python tools/check_negative.py --group csp_nonce
