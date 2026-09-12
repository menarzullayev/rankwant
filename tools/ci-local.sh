#!/usr/bin/env bash
# CI ni MAHALLIY takrorlash — `.github/workflows/ci.yml` bilan bir xil qadamlar.
#
# Nega kerak: CI self-hosted runner'da ishlaydi va u LINUX tomonida
# (`runs-on: [self-hosted, rankwant]`). Windows'da turganda runner oflayn
# bo'ladi, ya'ni push qilingan ish `queued` holida qotib qoladi va hech
# qachon tekshirilmaydi. Bu skript o'sha tekshiruvlarni shu yerda
# o'tkazadi, ya'ni "yashil" ekanini bilish uchun qayta yuklash shart emas.
#
# Ishlatish (Git Bash, repo ildizidan):
#   bash tools/ci-local.sh            # hammasi
#   bash tools/ci-local.sh api        # faqat API (ruff, mypy, migratsiya, pytest)
#   bash tools/ci-local.sh web        # faqat Web (lint, types, build)
#   bash tools/ci-local.sh docs       # faqat hujjat/shartnoma/i18n/kontrast
#
# Docker kerak: API qadamlari `rankwant-api` image'ida ishlaydi, chunki
# loyihaning bog'liqliklari o'sha yerda (host'da emas).

set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
API_IMAGE="${API_IMAGE:-rankwant-api:latest}"
NETWORK="${NETWORK:-rankwant_default}"
PY="${PY:-python}"

# Ranglar faqat terminalda.
if [ -t 1 ]; then
  G=$'\033[32m'; R=$'\033[31m'; Y=$'\033[33m'; B=$'\033[1m'; N=$'\033[0m'
else
  G=""; R=""; Y=""; B=""; N=""
fi

FAILED=()
PASSED=()

step() {
  local name="$1"; shift
  printf '%s→ %s%s\n' "$B" "$name" "$N"
  if "$@"; then
    PASSED+=("$name")
    printf '%s  ✓ %s%s\n\n' "$G" "$name" "$N"
  else
    FAILED+=("$name")
    printf '%s  ✕ %s%s\n\n' "$R" "$name" "$N"
  fi
}

# ── Hujjat va shartnoma (runner kerak emas) ──────────────────────────────
run_docs() {
  cd "$ROOT"
  "$PY" tools/check_docs.py &&
    "$PY" tools/check_contract.py &&
    "$PY" tools/check_i18n.py &&
    "$PY" tools/check_contrast.py
}

# ── API (konteynerda) ────────────────────────────────────────────────────
# `--entrypoint sh` — image'ning entrypoint'i serverni ko'taradi, bizga
# faqat muhit kerak. Kod HOST'dan ulanadi, ya'ni commit qilinmagan
# o'zgarish ham tekshiriladi.
api_run() {
  MSYS_NO_PATHCONV=1 docker run --rm --entrypoint sh \
    -v "${ROOT}:/repo" -w /repo/apps/api \
    --network "$NETWORK" \
    -e DATABASE_URL=postgres://rankwant:dev@postgres:5432/rankwant \
    -e REDIS_URL=redis://redis:6379/0 \
    -e DJANGO_SECRET_KEY=ci-local -e DJANGO_DEBUG=1 \
    -e PYTHONNOUSERSITE=1 \
    "$API_IMAGE" -c "$1"
}

run_api() {
  # Bog'liqliklar bir marta o'rnatiladi, keyin to'rt qadam ketma-ket:
  # biri yiqilsa `set -e` butun blokni to'xtatadi va qaysi qadam
  # ekani chiqishda ko'rinadi.
  api_run '
set -e
pip install -q -r requirements-dev.lock 2>&1 | grep -v "Running pip as" || true
echo "--- ruff ---"
ruff check . && ruff format --check .
echo "--- mypy (strict) ---"
mypy .
echo "--- migratsiyalar to'\''liq yozilganmi ---"
python manage.py makemigrations --check --dry-run
echo "--- pytest ---"
pytest -q -n 4
'
}

# ── Web ──────────────────────────────────────────────────────────────────
run_web() {
  cd "$ROOT/apps/web"
  npm run lint && npm run typecheck && npm run build
}

# ── Tanlash ──────────────────────────────────────────────────────────────
TARGET="${1:-all}"

printf '%sRankWant — mahalliy CI%s\n' "$B" "$N"
printf 'Nishon: %s · image: %s\n\n' "$TARGET" "$API_IMAGE"

case "$TARGET" in
  docs) step "Hujjat, shartnoma, i18n, kontrast" run_docs ;;
  api)  step "API — ruff, mypy, migratsiya, pytest" run_api ;;
  web)  step "Web — lint, types, build" run_web ;;
  all)
    step "Hujjat, shartnoma, i18n, kontrast" run_docs
    step "API — ruff, mypy, migratsiya, pytest" run_api
    step "Web — lint, types, build" run_web
    ;;
  *)
    printf "%sNoma'lum nishon: %s%s\n" "$R" "$TARGET" "$N"
    exit 2
    ;;
esac

# ── Yakun ────────────────────────────────────────────────────────────────
printf '%s──────────────%s\n' "$B" "$N"
if [ "${#FAILED[@]}" -eq 0 ]; then
  printf "%sHAMMASI O'TDI (%d qadam)%s\n" "$G" "${#PASSED[@]}" "$N"
  exit 0
fi
printf '%sYIQILDI: %s%s\n' "$R" "${FAILED[*]}" "$N"
if [ "${#PASSED[@]}" -gt 0 ]; then
  printf "O'tgan qadamlar: %s\n" "${PASSED[*]}"
else
  printf "O'tgan qadam yo'q\n"
fi
exit 1
