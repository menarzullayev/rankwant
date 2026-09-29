#!/usr/bin/env bash
# Fail when the committed visual baselines were NOT produced by this image.
#
# WHY THIS EXISTS
# ---------------
# Measured 2026-09-24: a baseline captured on Windows produced a 3-4% pixel
# diff on every page when re-run inside
# `mcr.microsoft.com/playwright:v1.63.0-noble` -- while `maxDiffPixelRatio`
# is 0.01 (1%). The diff image shows the ENTIRE text in red, so the cause is
# glyph antialiasing/hinting, not layout. The container ships ~50 fonts
# (FreeSans, DejaVu...); the app asks for `Inter` and the platform stack, and
# those are simply absent on Linux.
#
# Consequence: baselines must be generated inside the SAME image CI uses.
# Regenerating them anywhere else makes CI red on the next run, and the
# reason is not obvious from the diff alone.
#
# HOW IT DETECTS DRIFT
# --------------------
# Run `--update-snapshots` in this image against a checked-out tree. If the
# committed PNGs were produced by a DIFFERENT renderer, Playwright rewrites
# them; the hash before/after then differs and we fail with a pointer to the
# regeneration instructions.
#
# !! THE TRAP THIS SCRIPT ONCE FELL INTO (measured 2026-09-24) !!
# ---------------------------------------------------------------
# The first version ran the update with no `E2E_BASE_URL`, so every page
# failed to load (`ERR_CONNECTION_REFUSED at http://localhost:3000`). With
# no page loaded there is no new screenshot, so the hashes were identical
# and the guard printed "Baseline'lar shu image bilan mos ✓" while the real
# suite was failing 3/7. It was a DEAD GATE: green for the wrong reason.
#
# Two guarantees were added so it cannot regress:
#   1. A live stack is REQUIRED. If the base URL does not answer, exit 2
#      (unreadable), never 0.
#   2. After the update run, the guard asserts the run itself was clean when
#      snapshots were just rewritten -- a failed page must not be mistaken
#      for "nothing to change".
#
# Exit codes: 0 = baselines match this image; 1 = drift (mismatch);
#             2 = could not measure (no stack / no snapshots).
#
# Run INSIDE the playwright container with the repo mounted at /e2e:
#   bash tools/ci_playwright.sh -- bash /e2e/scripts/check-baseline-drift.sh
# Override the stack with E2E_BASE_URL.
set -euo pipefail

SNAP_DIR="visual/visual.spec.ts-snapshots"
BASE_URL="${E2E_BASE_URL:-http://web:3000}"

if [ ! -d "$SNAP_DIR" ]; then
  echo "::error::$SNAP_DIR topilmadi -- vizual baseline'lar commit qilinmagan"
  exit 2
fi

# Count so a "0 files hashed" run cannot masquerade as a pass.
count=$(find "$SNAP_DIR" -name '*.png' | wc -l)
if [ "$count" -eq 0 ]; then
  echo "::error::$SNAP_DIR da birorta PNG yo'q"
  exit 2
fi
echo "--> $count baseline topildi"

# A dead gate was the original bug: with no reachable stack the update run
# silently no-ops and the hashes match. Require a live server first.
if ! curl -fsS -o /dev/null --max-time 10 "$BASE_URL/"; then
  echo "::error::$BASE_URL javob bermadi -- o'lchab bo'lmadi (stek ko'tarilmagan?)"
  echo "Bu 0 EMAS: baseline mosligini tekshirish uchun web stek kerak."
  exit 2
fi
echo "--> stek javob berdi: $BASE_URL"

before=$(find "$SNAP_DIR" -name '*.png' -print0 | sort -z | xargs -0 sha1sum | sha1sum)

# Snapshots are rewritten on run; a mismatch here is the signal we want, so
# the command's exit status is deliberately ignored -- but we DO inspect its
# output below, because an unreachable page would otherwise look like
# "no change needed".
npx playwright test --project=visual --update-snapshots --reporter=line \
  > /tmp/baseline-drift.log 2>&1 || true

after=$(find "$SNAP_DIR" -name '*.png' -print0 | sort -z | xargs -0 sha1sum | sha1sum)

if [ "$before" != "$after" ]; then
  echo "::error::Vizual baseline'lar bu image'da olinmagan -- CI'da har yurish qizil bo'ladi"
  echo ""
  echo "Sabab: baseline boshqa OS'da (masalan Windows) olingan. Linux"
  echo "konteynerida shrift antialiasing boshqacha -- 3-4% piksel farqi,"
  echo "bizning chegara 1%."
  echo ""
  echo "Yechim (CI image'ida qayta yarating):"
  echo "  tests/e2e/README.md -> 'Vizual regressiya' bo'limi"
  echo ""
  echo "--- playwright chiqishi (oxirgi 25 qator) ---"
  tail -25 /tmp/baseline-drift.log || true
  exit 1
fi

# Hashes matched. That is only meaningful if the run actually exercised every
# page -- a connection failure produces no screenshot and therefore no hash
# change. Treat any failure in the update run as "could not measure".
if grep -qE '^[[:space:]]*[0-9]+ failed' /tmp/baseline-drift.log; then
  echo "::error::--update-snapshots yurishi qizil tugadi -- natija ishonchsiz"
  echo "Xesh o'zgarmadi, lekin sahifalar yuklanmagan bo'lishi mumkin:"
  grep -E 'ERR_|Error:|failed' /tmp/baseline-drift.log | head -15 || true
  exit 2
fi

echo "Baseline'lar shu image bilan mos ✓"
