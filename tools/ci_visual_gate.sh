#!/usr/bin/env bash
# Prove the visual pixel gate is LIVE on the host before CI reports green.
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
# requires a pixel COUNT in the output rather than a bare exit status.
#
# WHERE IT RUNS
# -------------
# On the HOST, not inside the playwright container: the check rebuilds
# `apps/web` and restarts the running `next start`, which a container with
# only `/e2e` mounted cannot do.
#
# Skips LOUDLY when no stack is listening, so a missing target is never
# mistaken for a passing gate.
set -euo pipefail

BASE="${E2E_BASE_URL:-http://localhost:3400}"

if ! curl -sf -o /dev/null "$BASE/"; then
  echo "::warning::Web stack $BASE da javob bermadi — mutatsiya isboti O'TKAZIB YUBORILDI"
  echo "Bu qadam o'lchovsiz qoldi. Stack ko'tarilgan muhitda (lokal yoki"
  echo "self-hosted runner) u qayta yuritilishi kerak:"
  echo "  E2E_BASE_URL=$BASE python tools/check_negative.py --group visual"
  exit 0
fi

echo "--> Stack $BASE da javob berdi, mutatsiya isboti yuritiladi"
python tools/check_negative.py --group visual
