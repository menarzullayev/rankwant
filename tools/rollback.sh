#!/usr/bin/env bash
# Rollback — oldingi deploy'ning obrazlariga qaytish.
#
# ⚠️ NEGA KERAK: `deploy.yml` izohi «Use the rollback job if needed» deydi,
# lekin 2026-09-19 da o'lchandi — na job, na skript bor edi
# (`grep -rn rollback .github/ tools/` → 2 ta izoh, kod yo'q). Ya'ni avtomatik
# deploy yiqilsa orqaga qaytish yo'li YO'Q edi. Avtomatik rollback'siz
# avtomatik deploy — pasayish, yaxshilanish emas.
#
# ── Nima qaytaradi ───────────────────────────────────────────────────
# Faqat KOD: `api`, `worker`, `beat`, `judge`, `web` obrazlari.
# `tools/deploy.sh` har build'dan keyin shu obrazlarni
# `rankwant/<svc>:<sha12>` deb teglaydi — rollback o'sha teglardan o'qiydi.
#
# ── Nima QAYTARMAYDI ─────────────────────────────────────────────────
# ⚠️ MIGRATSIYANI QAYTARMAYDI. Django'da «orqaga» migratsiya yo'q va uni
# avtomatik yurgizish sxemani buzardi (`migrate <app> <oldingi>` ma'lumotni
# yo'qotadi). Shuning uchun:
#   · kod rollback — bu skript;
#   · sxema rollback — deploy oldidan olingan dump
#     (`tools/backup.sh --dump-only` → `<backup dir>/pg-deploy-*.sql.gz`),
#     ya'ni tiklash QO'LDA qilinadi va egasining tasdig'ini talab qiladi.
# Bu cheklov ataylab: jimgina yarim rollback — eng yomon holat (kod eski,
# sxema yangi).
#
# ── Ishlatish (repo ildizidan, Git Bash) ─────────────────────────────
#   bash tools/rollback.sh --list          # mavjud SHA teglari
#   bash tools/rollback.sh <sha12>         # interaktiv tasdiq so'raydi
#   bash tools/rollback.sh <sha12> --yes   # tasdiqsiz (avtomatlashtirish)
#
# ⚠️ Deploy bilan BIR XIL qulfdan foydalanadi: rollback va deploy bir vaqtda
# yurmasligi kerak (ikkisi ham `up` qiladi).

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

G=$'\033[32m'; R=$'\033[31m'; Y=$'\033[33m'; N=$'\033[0m'
PROJECT=rankwant
ENV_FILE="${RANKWANT_ENV_FILE:-.env.public}"
COMPOSE=(docker compose -p "$PROJECT" --env-file "$ENV_FILE"
         -f docker-compose.yml -f docker-compose.public.yml)
# Rollback'da qaytariladigan servislar. `migrate` YO'Q — u bir martalik
# konteyner va uni «qaytarish» ma'nosiz (u har yurishda `run --rm`).
SERVICES=(api worker beat judge web)

step() { printf '\n%s── %s%s\n' "$Y" "$1" "$N"; }
ok()   { printf '%s✓%s %s\n' "$G" "$N" "$1"; }
die()  { printf '%s✗ %s%s\n' "$R" "$1" "$N"; exit 1; }

SHA=""
ASSUME_YES=0
LIST_ONLY=0
for arg in "$@"; do
  case "$arg" in
    --list) LIST_ONLY=1 ;;
    --yes|-y) ASSUME_YES=1 ;;
    -h|--help) sed -n '2,40p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    -*) die "noma'lum argument: $arg" ;;
    *) [ -z "$SHA" ] || die "faqat bitta SHA beriladi (berildi: $SHA va $arg)"
       SHA="$arg" ;;
  esac
done

if [ "$LIST_ONLY" -eq 1 ]; then
  step "Mavjud rollback teglari (rankwant/<svc>:<sha12>)"
  docker images --format '{{.Repository}}:{{.Tag}}\t{{.CreatedSince}}' \
    | grep -E '^rankwant/(api|worker|beat|judge|web|migrate):' | sort || true
  echo
  echo "Eslatma: «latest» teglari bu ro'yxatda YO'Q — ular joriy kod."
  exit 0
fi

[ -n "$SHA" ] || die "SHA berilmadi. Ishlatish: bash tools/rollback.sh <sha12> (yoki --list)"
# Teg `deploy.sh` da SHA'ning 12 belgisi bilan qo'yiladi, lekin to'liq SHA ham
# berilishi mumkin — 12 belgiga keltiramiz. ⚠️ FAQAT hex SHA qisqartiriladi:
# `pre-rollback-20260919-052530` kabi tegni qisqartirish uni topilmaydigan
# qilib qo'yardi (`pre-rollback`).
if printf '%s' "$SHA" | grep -qE '^[0-9a-f]{13,}$'; then
  SHA="${SHA:0:12}"
fi

# ── Qulf (deploy.sh bilan bir xil) ───────────────────────────────────
common="$(git rev-parse --path-format=absolute --git-common-dir 2>/dev/null)"
LOCK="${RANKWANT_DEPLOY_LOCK:-${common:+$common/rankwant-deploy.lock}}"
[ -n "$LOCK" ] || die "git katalogi topilmadi — qulfni qo'yib bo'lmadi"
if ! mkdir "$LOCK" 2>/dev/null; then
  owner="$(cat "$LOCK/owner" 2>/dev/null || echo "egasi yozilmagan")"
  die "boshqa deploy/rollback ishlayapti ($owner). Qulf eskirgan bo'lsa: rm -rf \"$LOCK\""
fi
trap 'rm -rf "$LOCK"' EXIT
printf 'rollback pid %s, %s, target %s\n' "$$" "$(date -u '+%Y-%m-%d %H:%M UTC')" "$SHA" > "$LOCK/owner"

# ── 0. Old shartlar ──────────────────────────────────────────────────
step "0/5 Old shartlar"
[ -f "$ENV_FILE" ] || die "$ENV_FILE yo'q — usiz \${VAR} bo'sh qoladi va API har so'rovga 400 beradi"
command -v docker >/dev/null 2>&1 || die "docker topilmadi"
docker info >/dev/null 2>&1 || die "Docker engine javob bermayapti"
ok "docker ishlayapti, env-fayl joyida"

# ── 1. Teglar borligini tekshirish ───────────────────────────────────
# ⚠️ Hamma servis uchun teg SHART: yarmini qaytarish «api eski, worker yangi»
# holatini beradi va bu jimgina noto'g'ri natija beradi (masalan yangi kod
# yozgan vazifani eski worker o'qiy olmaydi).
step "1/5 Teglar tekshirilmoqda (rankwant/<svc>:${SHA})"
missing=0
for svc in "${SERVICES[@]}"; do
  if docker image inspect "rankwant/${svc}:${SHA}" >/dev/null 2>&1; then
    ok "rankwant/${svc}:${SHA}"
  else
    printf '%s✗%s rankwant/%s:%s topilmadi\n' "$R" "$N" "$svc" "$SHA"
    missing=1
  fi
done
if [ "$missing" -ne 0 ]; then
  echo
  echo "Mavjud teglar:" >&2
  docker images --format '{{.Repository}}:{{.Tag}}' \
    | grep -E '^rankwant/(api|worker|beat|judge|web):' | sort >&2 || true
  die "teg to'liq emas — rollback TO'XTATILDI (yarim qaytarish xavfli)"
fi

# ── 2. Tasdiq ────────────────────────────────────────────────────────
if [ "$ASSUME_YES" -ne 1 ]; then
  printf '\n%sJONLI stack %s ga qaytariladi: %s%s\n' "$Y" "$SHA" "${SERVICES[*]}" "$N"
  printf '%s⚠ Migratsiya QAYTARILMAYDI — sxema hozirgicha qoladi.%s\n' "$Y" "$N"
  printf 'Davom etamizmi? [ha/yo'"'"'q] '
  read -r answer
  case "$answer" in
    ha|h|yes|y|Y) ;;
    *) die "bekor qilindi" ;;
  esac
fi

# ── 3. Joriy holatni saqlab qo'yish ──────────────────────────────────
# ⚠️ Rollback ham yiqilishi mumkin. Unda qaytish uchun HOZIRGI obrazlarni
# teg bilan qotiramiz — aks holda noto'g'ri rollback'dan keyin orqaga yo'l
# yo'q bo'lardi.
step "2/5 Joriy obrazlar saqlanmoqda"
KEEP_TAG="pre-rollback-$(date -u +%Y%m%d-%H%M%S)"
for svc in "${SERVICES[@]}"; do
  if docker image inspect "rankwant-${svc}:latest" >/dev/null 2>&1; then
    docker tag "rankwant-${svc}:latest" "rankwant/${svc}:${KEEP_TAG}" \
      || die "joriy obrazni saqlab bo'lmadi: rankwant/${svc}:${KEEP_TAG}"
  fi
done
ok "saqlandi: rankwant/<svc>:${KEEP_TAG}"

# ── 4. Qaytarish ─────────────────────────────────────────────────────
# Compose build-servislar uchun obrazni `rankwant-<svc>` deb nomlaydi
# (o'lchandi 2026-09-19: jonli konteynerlarning `Config.Image` aynan shu).
# Ya'ni `latest` tegini qayta qo'yish yetarli — override fayl kerak emas.
step "3/5 Obrazlar ${SHA} ga o'tkazilmoqda"
for svc in "${SERVICES[@]}"; do
  docker tag "rankwant/${svc}:${SHA}" "rankwant-${svc}:latest" \
    || die "rankwant-${svc}:latest ni qayta teg qilib bo'lmadi"
done
ok "teglar almashtirildi"

step "4/5 Konteynerlar qayta ko'tarilmoqda"
"${COMPOSE[@]}" up -d --no-deps "${SERVICES[@]}" || die "up yiqildi"
ok "ko'tarildi"

# ── 5. Tasdiq ────────────────────────────────────────────────────────
# ⚠️ `check_deploy.sh` «joriy kodda» deydi, agar konteyner obrazi repo
# kodiga mos kelsa. Rollback'da bu SHART EMAS: biz ataylab eski commitga
# qaytdik, ya'ni skript «ESKIRGAN» deyishi mumkin va bu XATO EMAS.
step "5/5 Holat"
sleep 10
if bash tools/check_deploy.sh; then
  printf "\n%sRollback tugadi: %s (kod joriy commit bilan mos)%s\n" "$G" "$SHA" "$N"
else
  printf "\n%s⚠ check_deploy.sh «ESKIRGAN» dedi — rollback paytida bu KUTILGAN holat:%s\n" "$Y" "$N"
  printf "   konteyner ataylab %s (eski commit) da. «ESKIRGAN» xabari shu sababdan.\n" "$SHA"
  printf "   ⚠️ Agar SABAB boshqa bo'lsa (konteyner ko'tarilmadi, API 500), tekshiring:\n"
  printf "      docker compose -p %s --env-file %s logs --tail 80 api worker\n" "$PROJECT" "$ENV_FILE"
  printf "   Orqaga qaytish uchun: bash tools/rollback.sh %s\n" "$KEEP_TAG"
  exit 0
fi
