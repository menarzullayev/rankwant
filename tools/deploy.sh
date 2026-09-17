#!/usr/bin/env bash
# Qo'lda deploy — runbook §1 ni bajariladigan ko'rinishga keltiradi.
#
# NEGA SKRIPT KERAK: deploy tartibi 6 qadamdan iborat va tartib MUHIM
# (migratsiya deploy'DAN OLDIN, `migrate` alohida obraz, tasdiq faqat
# `showmigrations` orqali). Yodda saqlashga tayanadigan tartib — bu
# bir kun o'tkazib yuboriladigan qadam. 2026-09-16 da aynan shunday
# bo'ldi: 6 ta migration qo'llanmagan, `migrate` esa «No migrations to
# apply» degan (eski obraz) va bu faqat qo'lda payqaldi.
#
# NEGA AVTOMATIK EMAS: `deploy.yml` dagi GitHub job bu mashinada
# produksiyani deploy QILA OLMAYDI — o'lchandi (2026-09-16):
#   * jonli stack — Docker Desktop engine'i (A), `rankwant-api:latest`;
#   * CI runner — WSL Ubuntu ichidagi alohida engine (B),
#     `rankwant/api:<sha>` teglari bilan.
# Ya'ni job o'z stack'ini B da ko'tarardi: 8300/8301 band → `up` yiqiladi,
# yoki parallel stack paydo bo'ladi va unga hech kim yo'naltirmagan.
# Batafsil: `docs/10-operations/deploy-runbook.md` § «Deploy — qo'lda».
#
# Ishlatish (repo ildizidan, Git Bash):
#   bash tools/deploy.sh            # interaktiv tasdiq so'raydi
#   bash tools/deploy.sh --yes      # tasdiqsiz (avtomatlashtirish uchun)
#   bash tools/deploy.sh --check    # hech narsani o'zgartirmaydi, faqat holat
#   bash tools/deploy.sh --skip-ci-gate  # owner-approved only: skip the main CI gate
#
# ⚠️ Live contest paytida deploy QILINMAYDI (10-operations, qoida №1).
# Skript buni API orqali tekshiradi va faol contest bo'lsa TO'XTAYDI.

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

G=$'\033[32m'; R=$'\033[31m'; Y=$'\033[33m'; N=$'\033[0m'
PROJECT=rankwant
ENV_FILE=.env.public
COMPOSE=(docker compose -p "$PROJECT" --env-file "$ENV_FILE"
         -f docker-compose.yml -f docker-compose.public.yml)
# Deploy'da yangilanadigan servislar.
#
# `judge` ham shu yerda: u Go binari va o'z obrazidan quriladi, ya'ni kod
# o'zgarganda uni ham qayta qurish kerak — aks holda «api yangi, judge
# eski» holati paydo bo'ladi va buni `check_deploy.sh` KO'RMAYDI
# (binary'ning manbadagi hash'i yo'q).
#
# `web` bu yerda YO'Q: u Next.js va `NEXT_PUBLIC_*` qiymatlari build
# vaqtida singadi, ya'ni uni alohida qaror bilan qayta qurish kerak
# (runbook § NEXT_PUBLIC).
SERVICES=(api worker beat judge)

# Manba commit — image yorlig'iga (`org.rankwant.git-sha`) uzatiladi.
# `check_deploy.sh` judge va web'ning eskiligini AYNAN shu yorliq orqali
# aniqlaydi; usiz ular ko'r nuqta bo'lib qoladi (2026-09-16 da judge
# shunday qolgan edi). Compose `${GIT_SHA:-unknown}` ni o'qiydi.
GIT_SHA="$(git rev-parse HEAD 2>/dev/null || echo unknown)"
export GIT_SHA

ASSUME_YES=0
CHECK_ONLY=0
SKIP_CI_GATE=0
for arg in "$@"; do
  case "$arg" in
    --yes|-y) ASSUME_YES=1 ;;
    --check)  CHECK_ONLY=1 ;;
    --skip-ci-gate) SKIP_CI_GATE=1 ;;
    -h|--help) sed -n '2,30p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) printf '%sNoma'"'"'lum argument: %s%s\n' "$R" "$arg" "$N"; exit 2 ;;
  esac
done

step() { printf '\n%s── %s%s\n' "$Y" "$1" "$N"; }
ok()   { printf '%s✓%s %s\n' "$G" "$N" "$1"; }
die()  { printf '%s✗ %s%s\n' "$R" "$1" "$N"; exit 1; }

# ── Lock and main CI gate ────────────────────────────────────────────
# Owner decision (2026-09-17, CLAUDE.md § Saidakbar aka qarorlari): agents deploy
# without asking once `main` CI is green. Two agents work on this machine, so
# only one deploy may run: the lock sits in the git common dir, which every
# worktree of this clone shares. It is taken before anything else, so a blocked
# run touches neither GitHub nor Docker. `--check` changes nothing and skips both.
if [ "$CHECK_ONLY" -ne 1 ]; then
  common="$(git rev-parse --path-format=absolute --git-common-dir 2>/dev/null)"
  LOCK="${RANKWANT_DEPLOY_LOCK:-${common:+$common/rankwant-deploy.lock}}"
  [ -n "$LOCK" ] || die "git katalogi topilmadi — deploy qulfini qo'yib bo'lmadi"
  if ! mkdir "$LOCK" 2>/dev/null; then
    owner="$(cat "$LOCK/owner" 2>/dev/null || echo "egasi yozilmagan")"
    die "boshqa deploy ishlayapti ($owner). U tugaganini tekshiring; qulf eskirgan bo'lsa: rm -rf \"$LOCK\""
  fi
  trap 'rm -rf "$LOCK"' EXIT
  printf 'pid %s, %s, commit %s\n' "$$" "$(date -u '+%Y-%m-%d %H:%M UTC')" "$GIT_SHA" > "$LOCK/owner"

  step "Deploy darvozasi (main CI)"
  if [ "$SKIP_CI_GATE" -eq 1 ]; then
    printf '%s⚠ --skip-ci-gate: main CI tekshirilmadi — faqat Saidakbar akaning aniq ruxsati bilan%s\n' "$Y" "$N"
  else
    GATE_PY="$(bash tools/pick-python.sh 2>/dev/null)" || die "Python topilmadi — deploy darvozasi o'lchanmadi"
    "$GATE_PY" tools/check_deploy_gate.py || die "deploy darvozasi yopiq — main CI yashil emas yoki o'lchanmadi"
  fi
fi

# ── 0. Old shartlar ──────────────────────────────────────────────────
step "0/6 Old shartlar"
[ -f docker-compose.yml ] || die "repo ildizida emas (docker-compose.yml yo'q)"
command -v docker >/dev/null 2>&1 || die "docker topilmadi"
docker info >/dev/null 2>&1 || die "Docker engine javob bermayapti"
ok "docker ishlayapti"
[ -f "$ENV_FILE" ] || die "$ENV_FILE yo'q — usiz \${VAR} bo'sh qoladi va API har so'rovga 400 beradi"
ok "$ENV_FILE joyida"

# ── 1. Live contest oynasi (qoida №1) ────────────────────────────────
step "1/6 Live oyna tekshiruvi"
PY="$(bash tools/pick-python.sh 2>/dev/null)" || PY=""
if [ -z "$PY" ]; then
  printf '%s⚠ Python topilmadi — live oynani QO'"'"'LDA tekshiring%s\n' "$Y" "$N"
else
  "$PY" tools/check_deploy_window.py
  case $? in
    0) : ;;
    1) die "faol contest/arena bor — qoida №1: live paytida deploy QILINMAYDI" ;;
    2) printf '%s⚠ Oyna aniqlanmadi (API javob bermadi) — davom etishdan oldin qo'"'"'lda tasdiqlang%s\n' \
         "$Y" "$N" ;;
  esac
fi

if [ "$CHECK_ONLY" -eq 1 ]; then
  step "Holat (--check: hech narsa o'zgartirilmadi)"
  bash tools/check_deploy.sh
  exit $?
fi

# ── 2. Tasdiq ────────────────────────────────────────────────────────
if [ "$ASSUME_YES" -ne 1 ]; then
  printf '\n%sBu PRODUKSIYA deploy'"'"'i: %s qayta quriladi va qayta ko'"'"'tariladi.%s\n' \
    "$Y" "${SERVICES[*]}" "$N"
  printf 'Davom etamizmi? [ha/yo'"'"'q] '
  read -r answer
  case "$answer" in
    ha|ha|h|yes|y|Y) ;;
    *) die "bekor qilindi" ;;
  esac
fi

# ── 3. Qurish ────────────────────────────────────────────────────────
# `migrate` ham ALOHIDA obraz: usiz u eski obraz bilan yuradi va yangi
# migration fayllarini ko'rmaydi.
step "2/6 Obrazlar qurilmoqda (${SERVICES[*]} migrate)"
"${COMPOSE[@]}" build "${SERVICES[@]}" migrate || die "build yiqildi"
ok "obrazlar tayyor"

# ── 4. Migratsiya — DEPLOY'DAN OLDIN ─────────────────────────────────
step "3/6 Migratsiya"
"${COMPOSE[@]}" run --rm migrate || die "migrate yiqildi"

# ── 5. Tasdiq: `migrate` chiqishiga ISHONMAYMIZ ──────────────────────
# «No migrations to apply» eski obrazda ham aynan shunday deydi.
step "4/6 Qo'llanmagan migration tekshiruvi"
pending="$("${COMPOSE[@]}" run --rm api python manage.py showmigrations 2>/dev/null | grep -c '\[ \]')"
if [ "$pending" != "0" ]; then
  die "$pending ta migration qo'llanmagan — deploy TO'XTATILDI (runbook §1)"
fi
ok "qo'llanmagan migration: 0"

# ── 6. Ko'tarish ─────────────────────────────────────────────────────
step "5/6 Konteynerlar qayta ko'tarilmoqda"
"${COMPOSE[@]}" up -d --no-deps "${SERVICES[@]}" || die "up yiqildi"
ok "ko'tarildi"

# ── 7. Tasdiq: konteyner HAQIQATAN yangi kodda ───────────────────────
step "6/6 Deploy tasdiqi"
sleep 10
if bash tools/check_deploy.sh; then
  printf '\n%sDeploy tugadi.%s\n' "$G" "$N"
else
  die "check_deploy.sh «ESKIRGAN» dedi — konteyner eski kodda qolgan"
fi
