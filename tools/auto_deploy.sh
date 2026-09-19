#!/usr/bin/env bash
# Avtomatik deploy — host watcher (`RankWant Auto Deploy` vazifasi).
#
# ⚠️ NEGA HOST, GITHUB ACTIONS EMAS (2026-09-19 da o'lchandi):
#   · runner konteyneri jonli `.env.public` ni KO'RMAYDI — u `/work` Docker
#     volume'ida ishlaydi, host repo esa ulanmagan. Workflow o'z env-faylini
#     yozsa, `.env.public` dagi 29 kalitdan faqat 4 tasi qoladi va email
#     zanjiri, Turnstile, OAuth, Cloudflare token JIMGINA yo'qoladi;
#   · runner'da `gh` YO'Q — `check_deploy_gate.py` har doim `exit 2` berardi.
# Host'da esa `deploy.sh`, `gh`, `.env.public`, `docker` va Task Scheduler —
# hammasi bor va o'lchangan. Naqsh `tools/monitor.ps1` (RankWant Tunnel
# Monitor) dan olingan: u ham har 5 daqiqada xuddi shunday yuguradi.
#
# ── Bu skript nima qiladi ────────────────────────────────────────────
# Har 5 daqiqada:
#   1. qulfni oladi (deploy.sh bilan BIR XIL qulf) — band bo'lsa chiqadi;
#   2. `origin/main` ni oladi va deploy worktree'ni unga keltiradi;
#   3. JONLI kod joriymi — konteynerlar tirikmi (o'zimiz) va
#      `tools/check_deploy.sh` «joriy» deydimi; joriy bo'lsa JIM chiqadi;
#   4. `tools/check_deploy_gate.py` (main CI yashil) va `DEPLOY_FREEZE`;
#   5. `tools/deploy.sh --yes`.
#
# ⚠️ Nega WORKTREE HEAD bilan solishtirilmaydi: merge bo'lib, deploy yiqilgan
# bo'lsa worktree allaqachon `origin/main` da bo'ladi — HEAD bilan solishtirish
# «ish yo'q» deb o'ylab, driftni ABADIY qoldirardi. Haqiqatni faqat JONLI
# holat ko'rsatadi (2026-09-19 da sayt `main` dan 4 commit orqada edi).
#
# ⚠️ Qayta urinish to'sig'i (`RANKWANT_AUTO_DEPLOY_BACKOFF`, standart 1800 s):
# deploy yiqilsa (yoki main CI qizil bo'lsa), keyingi 30 daqiqada shu SHA
# uchun qayta urinilmaydi. Usiz yiqilgan holat har 5 daqiqada obraz qurib,
# diskni to'ldirardi va logni ko'mib tashlardi. Qayta urinishni darhol
# majburlash uchun holat faylini o'chirish kifoya.
#
# Ishlatish:
#   bash tools/auto_deploy.sh              # oddiy yurish (vazifa shuni chaqiradi)
#   bash tools/auto_deploy.sh --dry-run    # hech narsa qilmaydi, faqat qaror
#   bash tools/auto_deploy.sh --status     # holatni ko'rsatadi
#
# ⚠️ Skript deploy WORKTREE'sidan yurgiziladi, asosiy checkout'dan EMAS:
# asosiy checkout'da agentlarning commit qilinmagan tahriri bo'ladi va deploy
# uni jimgina build qilib jonli chiqarardi.

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

G=$'\033[32m'; R=$'\033[31m'; Y=$'\033[33m'; N=$'\033[0m'
PROJECT=rankwant
# Jonli stack turgan asosiy checkout — env-fayl o'sha yerda qoladi.
LIVE_DIR="${RANKWANT_LIVE_DIR:-C:/Users/nsn/project/cp/rankwant}"
# Holat fayli: oxirgi urinish (qayta urinish to'sig'i shundan hisoblanadi).
STATE="${RANKWANT_AUTO_DEPLOY_STATE:-$HOME/.rankwant-auto-deploy-state}"
BACKOFF="${RANKWANT_AUTO_DEPLOY_BACKOFF:-1800}"

DRY_RUN=0
STATUS_ONLY=0
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=1 ;;
    --status) STATUS_ONLY=1 ;;
    -h|--help) sed -n '2,42p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) printf '%sNoma'"'"'lum argument: %s%s\n' "$R" "$arg" "$N"; exit 2 ;;
  esac
done

log()  { printf '[%s] %s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" "$1"; }
die()  { printf '%s✗ %s%s\n' "$R" "$1" "$N"; exit 1; }

# ── Yordamchilar ─────────────────────────────────────────────────────

#: Deploy qilinadigan konteynerlar (`check_deploy.sh` bilan bir to'plam).
CONTAINERS=(api web judge worker beat)

# ⚠️ Nega FAQAT `check_deploy.sh` ga tayanmaymiz: u konteyner YO'Q bo'lganda
# ham 0 bilan chiqadi — `missing` hisoblagichi faqat xabar uchun, `exit 1`
# esa faqat `stale`/`envbad` da (o'lchandi 2026-09-19, `check_deploy.sh`
# oxiri). Ya'ni stack butunlay yiqilgan bo'lsa u «Hamma konteyner joriy
# kodda» deb YOLG'ON YASHIL beradi. Shuning uchun tirikligini alohida
# tekshiramiz.
all_up() {
  local c
  for c in "${CONTAINERS[@]}"; do
    docker inspect "rankwant-$c-1" >/dev/null 2>&1 || return 1
  done
  return 0
}

# Jonli kod SHA'si — faqat LOG uchun. ⚠️ Qaror bunga TAYANMAYDI: yorliq
# `unknown` bo'lishi mumkin (deploy `deploy.sh` orqali bo'lmasa), va
# «o'qilmadi» ni «eski» ham, «yangi» ham deb o'qish yolg'on signal beradi.
live_sha() {
  local sha
  sha="$(docker inspect rankwant-web-1 \
    --format '{{index .Config.Labels "org.rankwant.git-sha"}}' 2>/dev/null)"
  [ -n "$sha" ] && [ "$sha" != "unknown" ] && [ "$sha" != "<no value>" ] || return 1
  printf '%s' "$sha"
}

# Holat faylidan oxirgi urinishni o'qish (`<sha> <epoch>`).
last_attempt() {
  [ -f "$STATE" ] || return 1
  cat "$STATE" 2>/dev/null || return 1
}

record_attempt() {
  printf '%s %s\n' "$1" "$(date -u '+%s')" > "$STATE" 2>/dev/null || true
}

if [ "$STATUS_ONLY" -eq 1 ]; then
  printf 'worktree HEAD : %s\n' "$(git rev-parse HEAD 2>/dev/null || echo '?')"
  printf 'origin/main   : %s\n' "$(git rev-parse origin/main 2>/dev/null || echo '?')"
  if live="$(live_sha)"; then printf 'jonli (web)   : %s\n' "$live"; else printf 'jonli (web)   : O‘QILMADI\n'; fi
  printf 'holat fayli   : %s\n' "$(last_attempt || echo "yo'q")"
  printf 'env-fayl      : %s\n' "$LIVE_DIR/.env.public"
  exit 0
fi

# ── 1. Qulf ──────────────────────────────────────────────────────────
# Deploy bilan bir xil qulf. Band bo'lsa bu XATO EMAS — boshqa deploy
# ketayapti, jimgina chiqamiz (vazifa 5 daqiqadan keyin qaytadi).
common="$(git rev-parse --path-format=absolute --git-common-dir 2>/dev/null)"
LOCK="${RANKWANT_DEPLOY_LOCK:-${common:+$common/rankwant-deploy.lock}}"
[ -n "$LOCK" ] || die "git katalogi topilmadi"
if ! mkdir "$LOCK" 2>/dev/null; then
  exit 0
fi
trap 'rm -rf "$LOCK"' EXIT
printf 'auto-deploy pid %s, %s\n' "$$" "$(date -u '+%Y-%m-%d %H:%M UTC')" > "$LOCK/owner"

# ── 2. Muzlatish kaliti ──────────────────────────────────────────────
if [ -n "${DEPLOY_FREEZE:-}" ] && [ "${DEPLOY_FREEZE}" != "0" ]; then
  log "muzlatilgan (DEPLOY_FREEZE=$DEPLOY_FREEZE) — deploy qilinmadi"
  exit 0
fi

# ── 3. origin/main ni olish ──────────────────────────────────────────
# Tarmoq yiqilishi NORMAL holat (Wi-Fi, GitHub). U holda jim chiqamiz:
# bu deploy nosozligi emas va log ko'milmasligi kerak.
if ! git fetch --quiet origin main 2>/dev/null; then
  log "fetch yiqildi (tarmoq?) — keyingi yurishda qayta uriniladi"
  exit 0
fi
TARGET="$(git rev-parse origin/main 2>/dev/null)" || die "origin/main o'qilmadi"
[ -n "$TARGET" ] || die "origin/main bo'sh"

# ── 4. Drift bormi? ──────────────────────────────────────────────────
# Qaror ikki manbadan: konteynerlar tirikmi (o'zimiz) va kod joriymi
# (`check_deploy.sh`). Ikkisi ham kerak — sabab yuqoridagi izohda.
if all_up && bash tools/check_deploy.sh >/dev/null 2>&1; then
  # Eng ko'p uchraydigan holat: ish yo'q. JIM chiqamiz — log shishmasin.
  exit 0
fi

if live="$(live_sha)"; then
  log "drift: jonli ${live:0:7} ≠ main ${TARGET:0:7}"
else
  log "drift: jonli SHA yorlig'i o'qilmadi (deploy.sh dan o'tmagan?) — deploy qilinadi"
fi

# ── 5. Qayta urinish to'sig'i ────────────────────────────────────────
if last="$(last_attempt)"; then
  set -- $last
  prev_sha="${1:-}"; prev_epoch="${2:-0}"
  now="$(date -u '+%s')"
  if [ "$prev_sha" = "$TARGET" ] && [ $((now - prev_epoch)) -lt "$BACKOFF" ]; then
    log "shu SHA uchun yaqinda urinilgan ($(( (now - prev_epoch) / 60 )) daqiqa oldin) — to'siq ${BACKOFF}s"
    exit 0
  fi
fi

# ── 6. Deploy worktree'ni origin/main ga keltirish ───────────────────
# ⚠️ `reset --hard` ATAYLAB yo'q: u tasodifan commit qilingan ishni yo'q
# qiladi. `--ff-only` ajralib ketgan holatda TO'XTAYDI va bu to'g'ri —
# jimgina tuzatishdan ko'ra to'xtash afzal.
if [ -n "$(git status --porcelain --untracked-files=no)" ]; then
  die "deploy worktree'da commit qilinmagan o'zgarish bor — avval hal qiling ($ROOT)"
fi
if ! git merge --ff-only --quiet origin/main 2>/dev/null; then
  die "worktree origin/main ga tekshira olmadi (ajralib ketgan?) — qo'lda hal qiling"
fi

# ── 7. Env-fayl ──────────────────────────────────────────────────────
ENV_FILE="$LIVE_DIR/.env.public"
[ -f "$ENV_FILE" ] || die "env-fayl topilmadi: $ENV_FILE (RANKWANT_LIVE_DIR ni tekshiring)"

if [ "$DRY_RUN" -eq 1 ]; then
  log "dry-run: deploy qilinardi (target ${TARGET:0:7}, env $ENV_FILE)"
  exit 0
fi

# ── 8. Deploy ────────────────────────────────────────────────────────
# ⚠️ Urinish deploy'dan OLDIN yoziladi: `deploy.sh` yiqilib ketsa ham to'siq
# hisobga oladi. Keyin yozilsa, yiqilgan yurish har 5 daqiqada takrorlanardi.
record_attempt "$TARGET"
log "deploy boshlandi (target ${TARGET:0:7})"
if RANKWANT_ENV_FILE="$ENV_FILE" bash tools/deploy.sh --yes; then
  log "deploy tugadi: ${TARGET:0:12}"
  rm -f "$STATE"
  exit 0
fi
log "deploy YIQILDI (target ${TARGET:0:7}) — ${BACKOFF}s to'siq qo'yildi"
printf '%s⚠ Rollback kerakmi? bash tools/rollback.sh --list%s\n' "$Y" "$N"
exit 1
