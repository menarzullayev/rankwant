#!/usr/bin/env bash
# Prove the visual pixel gate is LIVE against the CI stack before CI reports green.
#
# WHY THIS EXISTS
# ---------------
# 2026-09-24: the first attempt at a "non-vacuous proof" mutated
# `--rw-rank-grey` and the visual suite stayed green. We read that as
# "the gate works". It was wrong: the token is not painted on any page we
# screenshot, so the mutation was dead — the gate was never exercised.
# Only after switching to `--rw-ground` (the page background) did a real
# 107,105-pixel difference appear.
#
# Lesson: "the suite stayed green" is evidence ONLY when the mutation is
# visible. This script runs the check that enforces exactly that, and it
# requires a pixel COUNT on every baseline rather than a bare exit status.
#
# 2026-11-10: this step had measured nothing on any hosted run. It looked
# for a host `next start` on `localhost:3400`; the CI stack publishes no
# host ports (`docker-compose.ci.yml` → `ports: !reset []`), so it printed a
# warning and exited 0 every night (runs 42716046958, 42721061218). And
# had it run, the mutation itself was dead again: it changed `--rw-ground`
# on `:root`, which the factory style `clay` overrides.
#
# WHAT IT DOES NOW
# ----------------
# `check_negative.py --group visual` with `VISUAL_STACK=compose`: next to
# the stack it serves the stack's own web image as a control (must be
# green) and the same image rebuilt with a visible mutation (must be red on
# every baseline, each with a pixel count). Neither touches the stack's
# `web`, so smoke and bake-off after this step see what they always saw.
#
# A missing stack FAILS this step. A warning nobody reads is how a gate
# stays dead for six weeks.
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"

fail() {
  echo "::error::$1"
  echo "Vizual darvoza o'lchanmadi — qadam yiqiladi (o'tkazib yuborilmaydi)."
  exit 1
}

project="${COMPOSE_PROJECT_NAME:-}"
[ -n "$project" ] || fail "COMPOSE_PROJECT_NAME yo'q — CI stack topilmadi"
web="$(docker ps -q \
  --filter "label=com.docker.compose.project=$project" \
  --filter "label=com.docker.compose.service=web" 2>/dev/null || true)"
[ -n "$web" ] || fail "$project stack'ida web konteyneri ishlamayapti — mutatsiya isboti yo'q"

echo "--> $project stack'i topildi (web $web), mutatsiya isboti yuritiladi"
log="$(mktemp)"
set +e
VISUAL_STACK=compose python3 tools/check_negative.py --group visual 2>&1 | tee "$log"
status=${PIPESTATUS[0]}
set -e

if [ -n "${GITHUB_STEP_SUMMARY:-}" ]; then
  {
    echo "### Visual gate is live (mutation proof)"
    echo '```'
    grep -E "visual:|salbiy test" "$log" || echo "natija qatori topilmadi (exit $status)"
    echo '```'
  } >>"$GITHUB_STEP_SUMMARY"
fi
[ "$status" = 0 ] || echo "::error::Vizual darvoza isboti yiqildi (exit $status) — yuqoridagi qatorga qarang"
exit "$status"
