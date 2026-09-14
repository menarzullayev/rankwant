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
#   bash tools/ci-local.sh fast     # ~5 s: ruff, format, hujjat, i18n, kontrast
#   bash tools/ci-local.sh api      # ~50 s: mypy, migratsiya, pytest
#   bash tools/ci-local.sh web      # ~1 min: lint, types, build
#   bash tools/ci-local.sh all      # hammasi
#   bash tools/ci-local.sh rebuild  # dev image'ni majburan qayta qurish
#
# ⚠️ BU SKRIPT MANBANI sinaydi, ISHLAB TURGAN KONTEYNERNI EMAS.
# Ya'ni "all" yashil bo'lishi produksiyada joriy kod ketayotganini
# BILDIRMAYDI: ishlab turgan `rankwant-web`/`rankwant-api` image'i eski
# bo'lsa ham bu yerda hech narsa qizarmaydi (2026-09-13 dagi uchala
# avariya aynan shundan chiqdi). Deploy holatini alohida so'rang:
#
#   bash tools/check_deploy.sh
#
# U shu ro'yxatga ATAYLAB qo'shilmagan: uni ishlatish uchun ishlab
# turgan stack kerak, CI esa faqat manba va vaqtinchalik konteyner bilan
# ishlashi shart (busiz u qurilmaga bog'lanib qoladi va yolg'on yashil
# beradi).
#
# Tezlik haqida: to'liq tekshiruv 30 soniyaga SIG'MAYDI — mypy (strict,
# 280 fayl) va 996 test o'zi ~60 s. Lekin ikki narsa kesilgan:
#   1) dev bog'liqliklar bir marta o'rnatiladi (`tools/ci.Dockerfile`) —
#      har safar `pip install` ~30 s yeyardi;
#   2) mypy va ruff keshi volume'da saqlanadi.
# Kundalik ish uchun `fast` bor — u 5 soniyada asosiy xatolarni topadi.

set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BASE_IMAGE="${BASE_IMAGE:-rankwant-api:latest}"
NETWORK="${NETWORK:-rankwant_default}"
CACHE_VOLUME="${CACHE_VOLUME:-rankwant-ci-cache}"
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

# ── Dev image: bog'liqliklar BIR MARTA o'rnatiladi ───────────────────────
# Teg `requirements-dev.lock` xeshiga bog'langan: fayl o'zgarsa yangi teg
# hosil bo'ladi va image o'zi qayta quriladi. Ya'ni eskirib qolmaydi.
LOCK="$ROOT/apps/api/requirements-dev.lock"
if command -v sha1sum >/dev/null 2>&1; then
  LOCK_HASH="$(sha1sum "$LOCK" | cut -c1-12)"
else
  LOCK_HASH="$(shasum -a 1 "$LOCK" | cut -c1-12)"
fi
DEV_IMAGE="${DEV_IMAGE:-rankwant-api-dev:${LOCK_HASH}}"

# ── mypy keshi — FAYLLAR RO'YXATI o'zgarsa bekor qilinadi ────────────────
#
# ⚠️ 2026-09-13 da o'lchandi: `core/turnstile.py` qo'shilgach mypy
# `Module "core" has no attribute "turnstile"` va
# `'Settings' object has no attribute 'TURNSTILE_SITE_KEY'` deb xato
# berdi — fayllar joyida va import qilinadigan bo'lsa ham. Yangi kesh
# (`--cache-dir /tmp/mc`) bilan XUDDI shu ikki fayl **0 xato** berdi.
#
# Sabab: mypy keshi paketdagi MODULLAR RO'YXATINI ham saqlaydi. Yangi
# fayl paydo bo'lganda u o'z ro'yxatini yangilamaydi — ilgari `core.turnstile`
# yo'q edi, ya'ni «yo'q» degan xulosa keshda qolib ketadi.
#
# Keshni butunlay olib tashlash ham yechim emas: to'liq mypy ~40 soniya,
# kesh bilan ~8. Shuning uchun kesh PAPKA nomiga fayllar ro'yxatining
# xeshini qo'shamiz: ro'yxat o'zgarsa yangi papka, o'zgarmasa eski kesh.
#
# Ruff keshi bunga muhtoj emas (u har faylni o'zi bo'yicha keshlaydi),
# shuning uchun u o'zgarmadi.
py_fingerprint() {
  cd "$ROOT/apps/api" || return 1
  if command -v sha1sum >/dev/null 2>&1; then
    find . -name '*.py' -not -path './.venv/*' -not -path './.pytest_cache/*' |
      LC_ALL=C sort | sha1sum | cut -c1-12
  else
    find . -name '*.py' -not -path './.venv/*' -not -path './.pytest_cache/*' |
      LC_ALL=C sort | shasum -a 1 | cut -c1-12
  fi
}
PY_FP="$(py_fingerprint || echo 'nohash')"
MYPY_CACHE="/cache/mypy-${PY_FP}"

build_dev_image() {
  # Kontekst ATAYLAB nisbiy (`.`): `MSYS_NO_PATHCONV=1` bilan Git Bash
  # yo'li (`/c/...`) docker'ga o'girilmasdan yetib boradi va u
  # "path not found" derdi. Repo ildiziga o'tib `.` berish esa har ikki
  # tomonda ham bir xil ma'noni bildiradi.
  printf 'Dev image qurilmoqda: %s (birinchi marta ~1 daqiqa)\n' "$DEV_IMAGE"
  cd "$ROOT" || return 1
  MSYS_NO_PATHCONV=1 docker build \
    -f tools/ci.Dockerfile \
    --build-arg "BASE=$BASE_IMAGE" \
    -t "$DEV_IMAGE" .
}

ensure_dev_image() {
  if docker image inspect "$DEV_IMAGE" >/dev/null 2>&1; then
    return 0
  fi
  if ! docker image inspect "$BASE_IMAGE" >/dev/null 2>&1; then
    printf '%sAsosiy image yo'"'"'q: %s%s\n' "$R" "$BASE_IMAGE" "$N"
    printf 'Avval: docker compose -p rankwant ... build api\n'
    return 1
  fi
  build_dev_image
}

# ── Hujjat va shartnoma (runner kerak emas) ──────────────────────────────
run_docs() {
  cd "$ROOT"
  "$PY" tools/check_docs.py &&
    "$PY" tools/check_contract.py &&
    "$PY" tools/check_i18n.py &&
    # `check_i18n.py` faqat kod -> lug'at yo'nalishini ko'radi: u
    # `t()` chaqirilgan kalitning 10 tilda borligini tekshiradi, lekin
    # qattiq yozilgan matnni KO'RMAYDI. Admin panelda 274 ta shunday
    # satr «toza ✓» ostida turgan edi — shuning uchun teskari
    # yo'nalish ham tekshiriladi.
    "$PY" tools/check_hardcoded.py &&
    "$PY" tools/check_email_locales.py &&
    "$PY" tools/check_locales_parity.py &&
    "$PY" tools/check_contrast.py &&
    "$PY" tools/check_gradient_styles.py &&
    # `t()` ning ZAXIRA yo'lini HAQIQIY modulda o'lchaydi: dev'da
    # otilishi, prod'da bir marta jurnalga yozilishi. `check_i18n.py`
    # buni ko'ra olmaydi — u faqat matnni o'qiydi.
    check_i18n_runtime &&
    # Tekshiruvlarning O'ZLARINI sinaydi: har biriga ataylab buzilgan
    # holat beriladi va `exit 1` talab qilinadi. Bu qadam eng muhimi —
    # "yashil, lekin yolg'on" natija shu loyihada bir kunda to'rt marta
    # uchragan, ya'ni tekshiruv o'zi ham tekshirilishi kerak.
    "$PY" tools/check_negative.py
}

# Node'ni topish: PATH'da bo'lmasa `NODE` orqali beriladi (Windows
# o'rnatuvchisida `node` ba'zan PATH'da bo'lmaydi). Topilmasa —
# o'tkazib yuborilmaydi, XATO qaytariladi: jimgina o'tkazib
# yuborish "yashil, lekin yolg'on" ning aynan o'zi.
check_i18n_runtime() {
  local node="${NODE:-}"
  if [ -z "$node" ]; then
    if command -v node >/dev/null 2>&1; then
      node="node"
    else
      printf '%snode topilmadi — `NODE` muhit o'"'"'zgaruvchisini bering%s\n' "$R" "$N"
      return 1
    fi
  fi
  "$node" tools/check_i18n_runtime.mjs
}

# ── API (konteynerda) ────────────────────────────────────────────────────
# `--entrypoint sh` — image'ning entrypoint'i serverni ko'taradi, bizga
# faqat muhit kerak. Kod HOST'dan ulanadi, ya'ni commit qilinmagan
# o'zgarish ham tekshiriladi. `/cache` — mypy va ruff keshi (volume).
api_run() {
  MSYS_NO_PATHCONV=1 docker run --rm --entrypoint sh \
    -v "${ROOT}:/repo" -v "${CACHE_VOLUME}:/cache" -w /repo/apps/api \
    --network "$NETWORK" \
    -e DATABASE_URL=postgres://rankwant:dev@postgres:5432/rankwant \
    -e REDIS_URL=redis://redis:6379/0 \
    -e DJANGO_SECRET_KEY=ci-local -e DJANGO_DEBUG=1 \
    -e PYTHONNOUSERSITE=1 -e MYPY_CACHE="$MYPY_CACHE" \
    "$DEV_IMAGE" -c "$1"
}

run_api_fast() {
  ensure_dev_image || return 1
  api_run 'ruff check --cache-dir /cache/ruff . && ruff format --check .'
}

run_api() {
  ensure_dev_image || return 1
  # `set -e`: biri yiqilsa to'xtaydi va qaysi qadam ekani chiqishda
  # ko'rinadi. Ketma-ket — chunki hammasi bitta konteynerda ishlaydi.
  api_run '
set -e
echo "--- ruff ---"
ruff check --cache-dir /cache/ruff . && ruff format --check .
echo "--- mypy (strict) ---"
mypy --cache-dir "$MYPY_CACHE" .
echo "--- migratsiyalar to'"'"'liq yozilganmi ---"
python manage.py makemigrations --check --dry-run
echo "--- pytest ---"
pytest -q -n 4
'
}

# ── Web ──────────────────────────────────────────────────────────────────
run_web_types() {
  cd "$ROOT/apps/web"
  npm run typecheck
}

run_web() {
  cd "$ROOT/apps/web"
  npm run lint && npm run typecheck && npm run build
}

# ── Tanlash ──────────────────────────────────────────────────────────────
TARGET="${1:-all}"

printf '%sRankWant — mahalliy CI%s\n' "$B" "$N"
printf 'Nishon: %s · image: %s\n\n' "$TARGET" "$DEV_IMAGE"

case "$TARGET" in
  fast)
    step "Hujjat, shartnoma, i18n, kontrast" run_docs
    step "Ruff (lint + format)" run_api_fast
    ;;
  docs) step "Hujjat, shartnoma, i18n, kontrast" run_docs ;;
  api)  step "API — ruff, mypy, migratsiya, pytest" run_api ;;
  web)  step "Web — lint, types, build" run_web ;;
  types) step "Web — types" run_web_types ;;
  rebuild) build_dev_image ;;
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

if [ "$TARGET" = "rebuild" ]; then
  printf '%sDev image qurildi: %s%s\n' "$G" "$DEV_IMAGE" "$N"
  exit 0
fi

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
