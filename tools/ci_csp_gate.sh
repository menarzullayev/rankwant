#!/usr/bin/env bash
# Prove the CSP nonce gate is LIVE against the running CI stack before CI is green.
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
# NOT rebuild: it reads the HTML the stack already serves.
#
# 2026-11-10: until now it read `localhost:3400`, which the CI stack never
# serves (`docker-compose.ci.yml` resets every host port) — so it warned and
# exited 0 on every hosted run (runs 42716046958, 42721061218). It now reads
# the stack's web container at its address on the compose network, and a
# missing stack FAILS the step instead of skipping it.
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"

fail() {
  echo "::error::$1"
  echo "CSP darvozasi o'lchanmadi — qadam yiqiladi (o'tkazib yuborilmaydi)."
  exit 1
}

project="${COMPOSE_PROJECT_NAME:-}"
[ -n "$project" ] || fail "COMPOSE_PROJECT_NAME yo'q — CI stack topilmadi"
web="$(docker ps -q \
  --filter "label=com.docker.compose.project=$project" \
  --filter "label=com.docker.compose.service=web" 2>/dev/null || true)"
[ -n "$web" ] || fail "$project stack'ida web konteyneri ishlamayapti — CSP qamrovi yo'q"
# The host reaches a container on a user-defined bridge network by its address
# (Linux runner); no port has to be published for that.
ip="$(docker inspect -f \
  "{{with index .NetworkSettings.Networks \"${project}_default\"}}{{.IPAddress}}{{end}}" \
  "$web" 2>/dev/null || true)"
[ -n "$ip" ] || fail "web konteynerining ${project}_default dagi manzili topilmadi"
base="http://$ip:3000"
curl -sf -o /dev/null --max-time 15 "$base/login" || fail "web $base/login da javob bermadi"

echo "--> $project stack'i $base da javob berdi, CSP qamrovi o'lchanadi"
log="$(mktemp)"
set +e
{
  python3 tools/check_csp_nonce.py --base "$base" &&
    E2E_BASE_URL="$base" python3 tools/check_negative.py --group csp_nonce
} 2>&1 | tee "$log"
status=${PIPESTATUS[0]}
set -e

if [ -n "${GITHUB_STEP_SUMMARY:-}" ]; then
  {
    echo "### CSP nonce coverage is live"
    echo '```'
    grep -E "skript nonce bilan|csp_nonce/|qamrovi|salbiy test" "$log" || echo "natija qatori topilmadi (exit $status)"
    echo '```'
  } >>"$GITHUB_STEP_SUMMARY"
fi
[ "$status" = 0 ] || echo "::error::CSP nonce darvozasi yiqildi (exit $status)"
exit "$status"
