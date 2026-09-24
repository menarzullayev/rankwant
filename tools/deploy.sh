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
# Since 2026-09-17 the CI runner is a container on engine A and the WSL engine
# is gone, but deploying stays manual by owner decision (CLAUDE.md): deploy.yml
# is `workflow_dispatch` only and asks for `confirm: deploy`.
# Batafsil: `docs/10-operations/deploy-runbook.md` § «Deploy — qo'lda».
#
# Ishlatish (repo ildizidan, Git Bash):
#   bash tools/deploy.sh            # interaktiv tasdiq so'raydi
#   bash tools/deploy.sh --yes      # tasdiqsiz (avtomatlashtirish uchun)
#   bash tools/deploy.sh --check    # hech narsani o'zgartirmaydi, faqat holat
#   bash tools/deploy.sh --skip-ci-gate  # owner-approved only: skip the main CI gate
#   bash tools/deploy.sh --no-cache # compose build --no-cache (sovuq qurilish)
#   RANKWANT_ALLOW_LIVE_CONTEST=1 RANKWANT_DEPLOY_SCOPE=all \
#     bash tools/deploy.sh --yes    # SHOSHILINCH: faol contest paytida redeploy
#                                   # (qoida №1 chetga suriladi — faqat odam
#                                   # qo'li bilan; scope=all shart: auto scope
#                                   # bir xil SHA'da bo'sh chiqadi va hech
#                                   # narsa qilmaydi)
#   RANKWANT_BUILD_NO_CACHE=1       # xuddi --no-cache, env orqali
#   RANKWANT_DEPLOY_TIMING=path.tsv # TIMER qatorlarini TSV ga yozadi
#   RANKWANT_DEPLOY_SCOPE=auto|all|web  # bake doirasi (standart: auto)
#   O'lchov: bash tools/measure_deploy.sh --plan
#   Tasdiq: health (api/web), `sleep 10` emas
#
# ⚠️ Live contest paytida deploy QILINMAYDI (10-operations, qoida №1).
# Skript buni API orqali tekshiradi va faol contest bo'lsa TO'XTAYDI.
#
# ⚠️ DEPLOY_FREEZE=1 — muzlatish kaliti. Berilgan bo'lsa skript HECH NARSA
# qilmaydi (hatto qulfni ham olmaydi) va 1 bilan chiqadi. Avtomatik deploy
# ishlayotganda egaga «to'xta» deyish imkonini beradi — workflow faylini
# yoki rejalashtirilgan vazifani tahrirlash shart emas.
#
# ⚠️ RANKWANT_ENV_FILE — env-faylning yo'li (standart: repo ildizidagi
# `.env.public`). Deploy WORKTREE'dan yurgizilganda kod worktree'dan quriladi,
# env-fayl esa ASOSIY checkout'da qoladi (o'sha yerda 29 kalit bor) — shuning
# uchun yo'lni almashtirish kerak bo'ladi. Nusxa ko'chirilmaydi: ikkinchi
# nusxa jimgina ajralib ketadi.
#
# ⚠️ Migratsiyadan OLDIN `tools/backup.sh --dump-only` chaqiriladi: sxemaga
# tegadigan deploy zaxirasiz ketmasin (oylik to'liq zaxira bunga yetarli emas
# — u 30 kun orqada bo'lishi mumkin).

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

G=$'\033[32m'; R=$'\033[31m'; Y=$'\033[33m'; N=$'\033[0m'
PROJECT=rankwant
# Env-fayl: standart — repo ildizidagi `.env.public` (o'zgarishsiz). Deploy
# worktree'dan yurgizilsa `RANKWANT_ENV_FILE` bilan absolyut yo'l beriladi.
ENV_FILE="${RANKWANT_ENV_FILE:-.env.public}"
COMPOSE=(docker compose -p "$PROJECT" --env-file "$ENV_FILE"
         -f docker-compose.yml -f docker-compose.public.yml)
# Deploy'da yangilanadigan servislar.
#
# `judge` ham shu yerda: u Go binari va o'z obrazidan quriladi, ya'ni kod
# o'zgarganda uni ham qayta qurish kerak — aks holda «api yangi, judge
# eski» holati paydo bo'ladi va buni `check_deploy.sh` KO'RMAYDI
# (binary'ning manbadagi hash'i yo'q).
#
# `web` is built and restarted here too (owner decision, 2026-09-17). It used
# to be left out because `NEXT_PUBLIC_*` values are baked into the bundle at
# build time, but COMPOSE passes `--env-file .env.public` to the build as well,
# so this script bakes the right values in. Leaving it out cost a manual step
# after every web change and ended each such deploy red on the web row
# (measured on the #49 and #50 deploys).
SERVICES=(api worker beat judge web)

# Manba commit — image yorlig'iga (`org.rankwant.git-sha`) uzatiladi.
# `check_deploy.sh` judge va web'ning eskiligini AYNAN shu yorliq orqali
# aniqlaydi; usiz ular ko'r nuqta bo'lib qoladi (2026-09-16 da judge
# shunday qolgan edi). Compose `${GIT_SHA:-unknown}` ni o'qiydi.
GIT_SHA="$(git rev-parse HEAD 2>/dev/null || echo unknown)"
export GIT_SHA

# Qurilish vaqti — `org.rankwant.built-at` yorlig'i uchun. `GIT_SHA` bilan
# birga ishlatiladi: commit bir xil bo'lib, obraz eski bo'lishi mumkin
# (masalan `docker compose build` xatosiz o'tib, `up` yangilanmasa), va
# o'shanda qaysi biri yangiroq ekanini faqat vaqt ko'rsatadi.
BUILT_AT="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
export BUILT_AT

ASSUME_YES=0
CHECK_ONLY=0
SKIP_CI_GATE=0
NO_CACHE=0
for arg in "$@"; do
  case "$arg" in
    --yes|-y) ASSUME_YES=1 ;;
    --check)  CHECK_ONLY=1 ;;
    --skip-ci-gate) SKIP_CI_GATE=1 ;;
    --no-cache) NO_CACHE=1 ;;
    -h|--help) sed -n '2,40p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) printf '%sNoma'"'"'lum argument: %s%s\n' "$R" "$arg" "$N"; exit 2 ;;
  esac
done
if [ "${RANKWANT_BUILD_NO_CACHE:-0}" != "0" ]; then
  NO_CACHE=1
fi

step() { printf '\n%s── %s%s\n' "$Y" "$1" "$N"; }
ok()   { printf '%s✓%s %s\n' "$G" "$N" "$1"; }
die()  { printf '%s✗ %s%s\n' "$R" "$1" "$N"; exit 1; }

# Jonli health — `sleep 10` emas. Compose healthcheck interval 10–15 s;
# o'zimiz 1 s da so'raymiz (0–8 s, o'lchangan taklif).
health_api() {
  docker exec rankwant-api-1 python -c \
    "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health/', timeout=2)" \
    >/dev/null 2>&1
}

health_web() {
  docker exec rankwant-web-1 node -e \
    "fetch('http://127.0.0.1:3000/').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))" \
    >/dev/null 2>&1
}

wait_health() {
  local started=$SECONDS
  local limit="${RANKWANT_VERIFY_WAIT:-30}"
  while [ $((SECONDS - started)) -lt "$limit" ]; do
    if health_api && health_web; then
      return 0
    fi
    sleep 1
  done
  return 1
}

# Obraz doirasi. `SERVICES=(...)` to'liq qoladi (qaror: deploy hamma
# servisni QURISHI MUMKIN). Haqiqiy bake `BUILD_SERVICES` da.
# Docs/tools — bo'sh; judge faqat `services/judge-go` o'zgaganda.
BUILD_SERVICES=()
SKIP_BAKE=0
NEED_MIGRATE=0

resolve_build_services() {
  BUILD_SERVICES=()
  SKIP_BAKE=0
  if [ "$NO_CACHE" -eq 1 ]; then
    BUILD_SERVICES=("${SERVICES[@]}")
    return
  fi
  case "${RANKWANT_DEPLOY_SCOPE:-auto}" in
    all)
      BUILD_SERVICES=("${SERVICES[@]}")
      ;;
    auto|"")
      local computed=""
      if [ -n "${PY:-}" ] && [ -f tools/deploy_scope.py ]; then
        computed="$("$PY" tools/deploy_scope.py --from-live --to HEAD)" || computed="__fail__"
      else
        computed="__fail__"
      fi
      if [ "$computed" = "__fail__" ]; then
        BUILD_SERVICES=("${SERVICES[@]}")
      elif [ -z "$computed" ]; then
        SKIP_BAKE=1
      else
        # shellcheck disable=SC2206
        BUILD_SERVICES=($computed)
      fi
      ;;
    *)
      # shellcheck disable=SC2206
      BUILD_SERVICES=(${RANKWANT_DEPLOY_SCOPE})
      if [ ${#BUILD_SERVICES[@]} -eq 0 ]; then
        SKIP_BAKE=1
      fi
      ;;
  esac
}

need_migrate_from_scope() {
  NEED_MIGRATE=0
  local s
  for s in "${BUILD_SERVICES[@]}"; do
    case "$s" in
      api|worker|beat) NEED_MIGRATE=1; return ;;
    esac
  done
}

if [ -f "$ROOT/tools/deploy_timer.sh" ]; then
  # shellcheck disable=SC1091
  . "$ROOT/tools/deploy_timer.sh"
else
  time_begin() { :; }
  time_finish() { :; }
  time_finish_open() { :; }
  time_summary() { :; }
fi

RANKWANT_LOCK_OWNED=0
_on_exit() {
  time_finish_open
  time_summary
  if [ "${RANKWANT_LOCK_OWNED:-0}" = "1" ] && [ -n "${LOCK:-}" ]; then
    rm -rf "$LOCK"
  fi
}

# ── Muzlatish kaliti ─────────────────────────────────────────────────
# Qulfdan OLDIN turadi: muzlatilgan tizim qulfni ham olmasligi kerak, aks
# holda boshqa agentning yugurishi «band» deb xato o'qilardi.
# `0` va bo'sh qiymat — muzlatilmagan (kalitni o'chirish uchun `0` yetarli).
if [ "$CHECK_ONLY" -ne 1 ] && [ -n "${DEPLOY_FREEZE:-}" ] && [ "${DEPLOY_FREEZE}" != "0" ]; then
  printf '%s⚠ DEPLOY_FREEZE=%s — deploy muzlatilgan, hech narsa qilinmadi%s\n' \
    "$Y" "$DEPLOY_FREEZE" "$N"
  exit 1
fi

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
  # ⚠️ `RANKWANT_LOCK_HELD=1` — chaqiruvchi (`tools/auto_deploy.sh`)
  # allaqachon AYNAN SHU qulfni ushlab turadi. Usiz watcher o'zini
  # bloklaydi: u qulfni oladi, keyin bu yerga keladi va `mkdir` yiqiladi
  # (o'lchandi 2026-09-19 — «boshqa deploy ishlayapti (auto-deploy pid …)»),
  # ya'ni avtomatik deploy HECH QACHON ishlamasdi. Bayroqni faqat qulfni
  # haqiqatan ushlab turgan chaqiruvchi beradi; qulfning o'zi, `owner`
  # fayli va qulfni bo'shatish chaqiruvchining `trap` ida qoladi.
  if [ "${RANKWANT_LOCK_HELD:-0}" != "1" ]; then
    if ! mkdir "$LOCK" 2>/dev/null; then
      owner="$(cat "$LOCK/owner" 2>/dev/null || echo "egasi yozilmagan")"
      die "boshqa deploy ishlayapti ($owner). U tugaganini tekshiring; qulf eskirgan bo'lsa: rm -rf \"$LOCK\""
    fi
    RANKWANT_LOCK_OWNED=1
    printf 'pid %s, %s, commit %s\n' "$$" "$(date -u '+%Y-%m-%d %H:%M UTC')" "$GIT_SHA" > "$LOCK/owner"
  fi
  trap _on_exit EXIT
  time_begin e2e

  time_begin gate
  step "Deploy darvozasi (main CI)"
  if [ "$SKIP_CI_GATE" -eq 1 ]; then
    printf '%s⚠ --skip-ci-gate: main CI tekshirilmadi — faqat Saidakbar akaning aniq ruxsati bilan%s\n' "$Y" "$N"
  else
    GATE_PY="$(bash tools/pick-python.sh 2>/dev/null)" || die "Python topilmadi — deploy darvozasi o'lchanmadi"
    "$GATE_PY" tools/check_deploy_gate.py || die "deploy darvozasi yopiq — main CI yashil emas yoki o'lchanmadi"
  fi
  time_finish gate
fi

# ── 0. Old shartlar ──────────────────────────────────────────────────
time_begin preflight
step "0/8 Old shartlar"
[ -f docker-compose.yml ] || die "repo ildizida emas (docker-compose.yml yo'q)"
command -v docker >/dev/null 2>&1 || die "docker topilmadi"
docker info >/dev/null 2>&1 || die "Docker engine javob bermayapti"
ok "docker ishlayapti"
[ -f "$ENV_FILE" ] || die "$ENV_FILE yo'q — usiz \${VAR} bo'sh qoladi va API har so'rovga 400 beradi"
ok "$ENV_FILE joyida"
[ -f tools/backup.sh ] || die "tools/backup.sh yo'q — migratsiyadan oldingi zaxira olinmaydi"

# `backup.sh` o'z ildizidan `.env.public` ni qidiradi. Deploy worktree'dan
# yurgizilsa u yerda env-fayl YO'Q, shuning uchun absolyut yo'lni uzatamiz —
# nusxa ko'chirmaymiz (ikkinchi nusxa jimgina ajralib ketadi).
ENV_ABS="$(cd "$(dirname "$ENV_FILE")" && pwd)/$(basename "$ENV_FILE")" \
  || die "env-fayl yo'lini aniqlab bo'lmadi: $ENV_FILE"
ok "env-fayl: $ENV_ABS"
time_finish preflight

# ── 1. Live contest oynasi (qoida №1) ────────────────────────────────
time_begin contest_window
step "1/8 Live oyna tekshiruvi"
PY="$(bash tools/pick-python.sh 2>/dev/null)" || PY=""
if [ -z "$PY" ]; then
  printf '%s⚠ Python topilmadi — live oynani QO'"'"'LDA tekshiring%s\n' "$Y" "$N"
else
  "$PY" tools/check_deploy_window.py
  case $? in
    0) : ;;
    1)
      # ⚠️ Ataylab chetlab o'tish (2026-09-24, Saidakbar aka qarori).
      # Sayt contest paytida yiqilsa, tuzatishning yagona yo'li — deploy;
      # yopiq darvoza tizimni qulflab qo'yardi. Override faqat odam
      # qo'li bilan beriladi.
      #
      # ⚠️ `tools/auto_deploy.sh` bu o'zgaruvchini BERMAYDI — avtomatik
      # yo'lda odam yo'q, ya'ni qoida №1 u yerda qat'iy qoladi.
      if [ -n "${RANKWANT_ALLOW_LIVE_CONTEST:-}" ]; then
        printf '%s⚠ ATAYLAB CHETLAB O'"'"'TILDI (RANKWANT_ALLOW_LIVE_CONTEST) — faol contest bor, davom etilmoqda; qoida №1 chetga surildi%s\n' \
          "$Y" "$N"
      else
        die "faol contest/arena bor — qoida №1: live paytida deploy QILINMAYDI"
      fi
      ;;
    2) printf '%s⚠ Oyna aniqlanmadi (API javob bermadi) — davom etishdan oldin qo'"'"'lda tasdiqlang%s\n' \
         "$Y" "$N" ;;
  esac
fi
time_finish contest_window

if [ "$CHECK_ONLY" -eq 1 ]; then
  step "Holat (--check: hech narsa o'zgartirilmadi)"
  bash tools/check_deploy.sh
  exit $?
fi

resolve_build_services
need_migrate_from_scope

# ── 2. Tasdiq ────────────────────────────────────────────────────────
if [ "$ASSUME_YES" -ne 1 ]; then
  if [ "$SKIP_BAKE" -eq 1 ]; then
    printf '\n%sobrazga tushmaydi — qurilish yo'"'"'q (docs/tools).%s\n' "$Y" "$N"
  else
    printf '\n%sBu PRODUKSIYA deploy'"'"'i: %s qayta quriladi va qayta ko'"'"'tariladi.%s\n' \
      "$Y" "${BUILD_SERVICES[*]}" "$N"
  fi
  printf 'Davom etamizmi? [ha/yo'"'"'q] '
  read -r answer
  case "$answer" in
    ha|ha|h|yes|y|Y) ;;
    *) die "bekor qilindi" ;;
  esac
fi

# ── 3. Qurish ────────────────────────────────────────────────────────
# `migrate` ham ALOHIDA obraz: usiz u eski obraz bilan yuradi va yangi
# migration fayllarini ko'rmaydi. Docs/tools doirasi bo'sh bo'lsa bake yo'q.
BUILD_OPTS=()
if [ "$NO_CACHE" -eq 1 ]; then
  BUILD_OPTS+=(--no-cache)
  printf '%s⚠ --no-cache: obraz qatlamlari keshdan o'"'"'qilmaydi (sovuq qurilish)%s\n' "$Y" "$N"
fi
time_begin build
if [ "$SKIP_BAKE" -eq 1 ]; then
  step "2/8 Obrazlar — o'tkazib yuborildi (docs/tools, obrazga tushmaydi)"
  ok "bake yo'q"
elif [ "$NEED_MIGRATE" -eq 1 ]; then
  step "2/8 Obrazlar qurilmoqda (${BUILD_SERVICES[*]} migrate)"
  "${COMPOSE[@]}" build "${BUILD_OPTS[@]}" "${BUILD_SERVICES[@]}" migrate || die "build yiqildi"
  ok "obrazlar tayyor"
else
  step "2/8 Obrazlar qurilmoqda (${BUILD_SERVICES[*]})"
  "${COMPOSE[@]}" build "${BUILD_OPTS[@]}" "${BUILD_SERVICES[@]}" || die "build yiqildi"
  ok "obrazlar tayyor"
fi
time_finish build

# SHA obraz tegi QO'YILMAYDI (2026-09-20). Har deploy `rankwant/<svc>:<sha>`
# qoldirsa VHDX o'saveradi va prune Windows'ga joy qaytarmaydi. Kodni
# qaytarish — kerakli commitni qayta qurish; sxema — deploy oldidagi dump.

# ── 4. Migratsiyadan OLDIN zaxira ────────────────────────────────────
# ⚠️ Sxemaga tegadigan deploy zaxirasiz ketmasin. Oylik to'liq zaxira
# (MinIO + offsite + tiklash sinovi) bunga YETARLI EMAS: u oyiga bir marta
# olinadi, ya'ni migratsiya buzsa 30 kungacha orqaga qaytish kerak bo'lardi.
# `--dump-only` — faqat Postgres: MinIO ham, tiklash sinovi ham o'tkazib
# yuboriladi (migratsiya ularga tegmaydi), shuning uchun tez.
# api/worker/beat doirada bo'lmasa sxema o'zgarmaydi — dump/migrate yo'q.
time_begin dump
if [ "$SKIP_BAKE" -eq 1 ] || [ "$NEED_MIGRATE" -eq 0 ]; then
  step "3/8 Zaxira — o'tkazib yuborildi (api obraziga tushmaydi)"
else
  step "3/8 Migratsiyadan oldin zaxira (pg_dump)"
  RANKWANT_ENV_FILE="$ENV_ABS" bash tools/backup.sh --dump-only \
    || die "zaxira olinmadi — migratsiya TO'XTATILDI (zaxirasiz sxema o'zgarishi xavfli)"
  ok "zaxira olindi"
fi
time_finish dump

# ── 6. Migratsiya — DEPLOY'DAN OLDIN ─────────────────────────────────
time_begin migrate
if [ "$SKIP_BAKE" -eq 1 ] || [ "$NEED_MIGRATE" -eq 0 ]; then
  step "4/8 Migratsiya — o'tkazib yuborildi"
else
  step "4/8 Migratsiya"
  "${COMPOSE[@]}" run --rm migrate || die "migrate yiqildi"
fi
time_finish migrate

# ── 7. Tasdiq: `migrate` chiqishiga ISHONMAYMIZ ──────────────────────
# «No migrations to apply» eski obrazda ham aynan shunday deydi.
time_begin showmigrations
if [ "$SKIP_BAKE" -eq 1 ] || [ "$NEED_MIGRATE" -eq 0 ]; then
  step "5/8 Migration tekshiruvi — o'tkazib yuborildi"
else
  step "5/8 Qo'llanmagan migration tekshiruvi"
  pending="$("${COMPOSE[@]}" run --rm api python manage.py showmigrations 2>/dev/null | grep -c '\[ \]')"
  if [ "$pending" != "0" ]; then
    die "$pending ta migration qo'llanmagan — deploy TO'XTATILDI (runbook §1)"
  fi
  ok "qo'llanmagan migration: 0"
fi
time_finish showmigrations

# ── 8. Ko'tarish ─────────────────────────────────────────────────────
time_begin up
if [ "$SKIP_BAKE" -eq 1 ]; then
  step "6/8 Ko'tarish — o'tkazib yuborildi (bake yo'q)"
else
  # ── 6a/8 Infra: judge-queue + minio-init (ADR-0028) ────────────────
  # Ular BUILD doirasiga kirmaydi (obraz qurilmaydi: redis:7 / minio),
  # lekin api (JUDGE_QUEUE_URL) va judge (REDIS_URL + read-only kalit)
  # ularga bog'liq. `up --no-deps` depends_on kutishini o'tkazib yuboradi
  # va BUILD_SERVICES ularni o'z ichiga olmaydi — shu sababli alohida
  # ko'tariladi va tayyorligi O'ZIMIZ tekshiramiz (bounded).
  # Rollback (eski commit) bu serviszlari compose'da bo'lmasligi mumkin —
  # `config --services` bilan mavjudligi tekshiriladi.
  INFRA=()
  case " ${BUILD_SERVICES[*]} " in
    *" api "*|*" judge "*)
      defined="$(${COMPOSE[*]} config --services 2>/dev/null || true)"
      printf '%s\n' "$defined" | grep -qx "judge-queue" && INFRA+=("judge-queue")
      printf '%s\n' "$defined" | grep -qx "minio-init" && INFRA+=("minio-init")
      ;;
  esac
  if [ "${#INFRA[@]}" -gt 0 ]; then
    step "6a/8 Infra: judge-queue + minio-init"
    "${COMPOSE[@]}" up -d --no-deps "${INFRA[@]}" || die "infra up yiqildi"
    # judge-queue: healthcheck → healthy (Docker birinchi tekshiruvni
    # `interval` dan keyin qiladi — 10 s; 30 s chegara).
    q_ok=0
    for _ in $(seq 1 30); do
      h="$(docker inspect -f '{{.State.Health.Status}}' rankwant-judge-queue-1 2>/dev/null || echo none)"
      [ "$h" = "healthy" ] && { q_ok=1; break; }
      sleep 1
    done
    [ "$q_ok" = "1" ] || die "judge-queue 30 s ichida healthy bo'lmadi — api/judge ko'tarilmaydi (eski stack joyida qoladi)"
    # minio-init: chiqishi 0 bo'lishini kutamiz (judge-ro kalit yaratildi).
    # Eski (exit 0) konteyner konfiguratsiyasi o'zgarmagan bo'lsa compose
    # uni qayta yurgizmaydi — inspect darhol exited:0 beradi.
    m_ok=0
    for _ in $(seq 1 120); do
      st="$(docker inspect -f '{{.State.Status}}:{{.State.ExitCode}}' rankwant-minio-init-1 2>/dev/null || echo none)"
      case "$st" in
        "exited:0") m_ok=1; break ;;
        "exited:"*|"dead:"*|"removing:"*) die "minio-init yiqildi ($st) — judge-ro kalit yo'q; judge ko'tarilmaydi (eski stack joyida qoladi)" ;;
      esac
      sleep 1
    done
    [ "$m_ok" = "1" ] || die "minio-init 120 s ichida tugamadi — judge ko'tarilmaydi (eski stack joyida qoladi)"
    ok "judge-queue healthy, minio-init tugadi (judge-ro tayyor)"
  fi
  step "6/8 Konteynerlar qayta ko'tarilmoqda"
  "${COMPOSE[@]}" up -d --no-deps "${BUILD_SERVICES[@]}" || die "up yiqildi"
  ok "ko'tarildi"
fi
time_finish up

# ── 8. Tasdiq: konteyner HAQIQATAN yangi kodda ───────────────────────
step "7/8 Deploy tasdiqi"
time_begin verify
if ! wait_health; then
  printf '%s⚠ health %ss ichida javob bermadi — check_deploy davom etadi%s\n' \
    "$Y" "${RANKWANT_VERIFY_WAIT:-30}" "$N"
fi
if bash tools/check_deploy.sh; then
  ok "konteynerlar joriy kodda"
else
  die "check_deploy.sh «ESKIRGAN» dedi — konteyner eski kodda qolgan"
fi
time_finish verify

# ── 9. Disk: SHA teglar, dangling, builder cache ─────────────────────
# Faqat TASDIQ'DAN KEYIN: yiqilgan deploy cache ni ham o'chirmasin,
# qayta urinish sovuq qurilishga tushmasin. `prune_docker_disk.sh`
# `rankwant-<svc>:latest` va `rankwant/ci-runner` ni o'chirmaydi.
time_begin prune
if [ "$SKIP_BAKE" -eq 1 ]; then
  step "8/8 Disk tozalash — o'tkazib yuborildi (bake yo'q)"
else
  step "8/8 Disk tozalash (SHA teglar, dangling, builder)"
  bash tools/prune_docker_disk.sh || die "disk tozalash yiqildi"
fi
time_finish prune
time_finish e2e
time_summary
printf '\n%sDeploy tugadi.%s\n' "$G" "$N"
