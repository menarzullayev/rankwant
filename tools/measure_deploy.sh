#!/usr/bin/env bash
# Deploy end-to-end o'lchovi. Jonli stackni to'xtatmaydi.
#
# Sovuq qurilish = `compose build --no-cache` (ishlab turgan :latest
# o'chirilmaydi). `docker rmi -f rankwant-*:latest`, `compose down`,
# `volume prune`, `system prune` — YO'Q: preview 15–40 daqiqa yotadi
# yoki Postgres/MinIO ketadi.
#
#   bash tools/measure_deploy.sh --plan
#   bash tools/measure_deploy.sh --warm --yes
#   bash tools/measure_deploy.sh --cold --yes
#   bash tools/measure_deploy.sh --cold --purge-idle --yes
#   bash tools/measure_deploy.sh --per-image --yes
#
# Hisobot: `.handoff/deploy-timing/<utc>.{log,tsv,json,md}`
# Env: RANKWANT_ENV_FILE, RANKWANT_MEASURE_OUT

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# shellcheck disable=SC1091
. "$ROOT/tools/deploy_timer.sh"

G=$'\033[32m'; R=$'\033[31m'; Y=$'\033[33m'; N=$'\033[0m'
MODE=""
ASSUME_YES=0
PLAN=0
PURGE_IDLE=0
PER_IMAGE=0
OUT_DIR="${RANKWANT_MEASURE_OUT:-$ROOT/.handoff/deploy-timing}"

die() { printf '%s✗ %s%s\n' "$R" "$1" "$N"; exit 1; }

for arg in "$@"; do
  case "$arg" in
    --plan) PLAN=1 ;;
    --warm) MODE=warm ;;
    --cold) MODE=cold ;;
    --yes|-y) ASSUME_YES=1 ;;
    --purge-idle) PURGE_IDLE=1 ;;
    --per-image) PER_IMAGE=1 ;;
    -h|--help) sed -n '2,20p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) die "noma'lum argument: $arg" ;;
  esac
done

if [ "$PLAN" -eq 0 ] && [ "$ASSUME_YES" -eq 0 ]; then
  PLAN=1
fi

print_plan() {
  cat <<EOF
Deploy o'lchovi — reja
======================
Issiq E2E:
  bash tools/measure_deploy.sh --warm --yes

Sovuq E2E (barcha obraz qatlamlari qayta, kesh o'qilmaydi):
  bash tools/measure_deploy.sh --cold --yes

Sovuq + ishlatilmayotgan SHA/dangling teglar ( :latest tegilmaydi ):
  bash tools/measure_deploy.sh --cold --purge-idle --yes

Diagnostika — ketma-ket --no-cache (E2E wall-clock EMAS, parallel emas):
  bash tools/measure_deploy.sh --per-image --yes

Metrikalar (deploy.sh TIMER qatorlari):
  e2e, gate, preflight, contest_window, build, dump, migrate,
  showmigrations, up, verify, prune
  ixtiyoriy: purge_idle, build.<service>

Nima o'lchanadi:
  * wall-clock (time.perf_counter) — foydalanuvchi kutgan vaqt
  * bosqich = TIMER finish name=… sec=…
  * sovuq build = RANKWANT_BUILD_NO_CACHE=1 / --no-cache
  * o'chirish = faqat ishlatilmayotgan rankwant SHA teglari + dangling

Nima QILINMAYDI (jonli preview):
  * docker rmi -f  (ayniqsa rankwant-*:latest)
  * docker compose down / stop
  * docker volume prune   (Postgres/MinIO)
  * docker system prune
  * docker builder prune --all

Hisobot: $OUT_DIR/<utc>.{log,tsv,json,md}
EOF
}

if [ "$PLAN" -eq 1 ]; then
  print_plan
  exit 0
fi

if [ "$PER_IMAGE" -eq 0 ] && [ -z "$MODE" ]; then
  die "--warm, --cold yoki --per-image kerak (yoki --plan)"
fi
if [ "$PER_IMAGE" -eq 1 ] && [ -n "$MODE" ]; then
  die "--per-image alohida rejim: --warm/--cold bilan qo'shilmaydi (E2E raqami buziladi)"
fi

if [ -n "${DEPLOY_FREEZE:-}" ] && [ "${DEPLOY_FREEZE}" != "0" ]; then
  die "DEPLOY_FREEZE=$DEPLOY_FREEZE — o'lchov ham to'xtatiladi"
fi

STAMP="$(date -u '+%Y%m%d-%H%M%S')"
mkdir -p "$OUT_DIR" || die "hisobot papkasi ochilmadi: $OUT_DIR"
LOG="$OUT_DIR/$STAMP.log"
TSV="$OUT_DIR/$STAMP.tsv"
JSON="$OUT_DIR/$STAMP.json"
MD="$OUT_DIR/$STAMP.md"
export RANKWANT_DEPLOY_TIMING="$TSV"
export RANKWANT_DEPLOY_TIMING_JSON="$JSON"
export RANKWANT_MEASURE_MODE="${MODE:-per-image}"

PY="$(bash "$ROOT/tools/pick-python.sh" 2>/dev/null)" || die "Python topilmadi"

purge_idle() {
  # :latest va ishlab turgan image ID o'chirilmaydi. rmi -f YO'Q.
  time_begin purge_idle
  "$PY" - <<'PY'
import subprocess
import sys

def out(args):
    return subprocess.check_output(args, text=True, encoding="utf-8", errors="replace")

used = set()
ps = [x for x in out(["docker", "ps", "-q"]).split() if x]
if ps:
    for line in out(["docker", "inspect", "-f", "{{.Image}}", *ps]).splitlines():
        raw = line.strip()
        if not raw:
            continue
        used.add(raw)
        used.add(raw.replace("sha256:", "")[:12])

removed = 0
skipped = 0
for line in out(["docker", "images", "--format", "{{.ID}} {{.Repository}}:{{.Tag}}"]).splitlines():
    parts = line.split(" ", 1)
    if len(parts) != 2:
        continue
    iid, ref = parts
    repo = ref.rsplit(":", 1)[0]
    tag = ref.rsplit(":", 1)[-1]
    interesting = repo.startswith("rankwant/") or repo.startswith("rankwant-build-")
    if not interesting:
        continue
    if tag == "latest":
        skipped += 1
        continue
    short = iid.replace("sha256:", "")[:12]
    if iid in used or short in used or any(u.startswith(short) for u in used):
        skipped += 1
        continue
    proc = subprocess.run(["docker", "rmi", ref], capture_output=True, text=True)
    if proc.returncode == 0:
        print(f"  - {ref}")
        removed += 1
    else:
        skipped += 1
dangling = subprocess.run(["docker", "image", "prune", "-f"], capture_output=True, text=True)
print(f"purge_idle: removed={removed} skipped={skipped}")
if dangling.returncode != 0:
    sys.exit(dangling.returncode)
PY
  local st=$?
  time_finish purge_idle
  [ "$st" -eq 0 ] || die "purge-idle yiqildi"
}

write_md() {
  "$PY" - "$MD" "$TSV" "$JSON" "$LOG" "${MODE:-per-image}" <<'PY'
import json, sys
from pathlib import Path
md, tsv, js, log, mode = sys.argv[1:6]
rows = []
p = Path(tsv)
if p.is_file():
    for line in p.read_text(encoding="utf-8").splitlines():
        parts = line.split("\t")
        if len(parts) >= 2:
            rows.append((parts[0], parts[1], parts[2] if len(parts) > 2 else ""))
e2e = next((s for n, s, _ in rows if n == "e2e"), "")
payload = {}
jp = Path(js)
if jp.is_file():
    payload = json.loads(jp.read_text(encoding="utf-8"))
lines = [
    f"# Deploy o'lchovi — {mode}",
    "",
    f"- log: `{log}`",
    f"- tsv: `{tsv}`",
    f"- json: `{js}`",
    f"- e2e_sec: {payload.get('e2e_sec') or e2e or '—'}",
    f"- commit: {payload.get('commit') or '—'}",
    "",
    "| Bosqich | Soniyalar | UTC |",
    "|---|---|---|",
]
for n, s, iso in rows:
    lines.append(f"| {n} | {s} | {iso} |")
lines.append("")
lines.append("e2e — boshidan oxirigacha wall-clock. build qatori compose bake")
lines.append("(parallel). per-image yig'indisi e2e emas.")
Path(md).write_text("\n".join(lines) + "\n", encoding="utf-8")
PY
}

printf '%sHisobot: %s%s\n' "$Y" "$OUT_DIR/$STAMP" "$N"

if [ "$PURGE_IDLE" -eq 1 ]; then
  command -v docker >/dev/null 2>&1 || die "docker topilmadi"
  docker info >/dev/null 2>&1 || die "Docker engine javob bermayapti"
  purge_idle 2>&1 | tee -a "$LOG"
fi

if [ "$PER_IMAGE" -eq 1 ]; then
  ENV_FILE="${RANKWANT_ENV_FILE:-.env.public}"
  [ -f "$ENV_FILE" ] || die "$ENV_FILE yo'q"
  COMPOSE=(docker compose -p rankwant --env-file "$ENV_FILE"
           -f docker-compose.yml -f docker-compose.public.yml)
  export GIT_SHA="$(git rev-parse HEAD 2>/dev/null || echo unknown)"
  export BUILT_AT="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
  time_begin e2e
  for svc in api worker beat judge web migrate; do
    time_begin "build.$svc"
    "${COMPOSE[@]}" build --no-cache "$svc" || die "build $svc yiqildi"
    time_finish "build.$svc"
  done
  time_finish e2e
  time_summary
  write_md
  printf '%sPer-image tugadi. Konteynerlar almashtirilmadi (up yoq).%s\n' "$G" "$N"
  exit 0
fi

DEPLOY_ARGS=(--yes)
if [ "$MODE" = "cold" ]; then
  DEPLOY_ARGS+=(--no-cache)
  export RANKWANT_BUILD_NO_CACHE=1
fi
# Issiq o'lchov ham TO'LIQ bake qilisin: auto-scope jonli HEAD da
# bo'sh qaytaradi va wall-clock 0 ga tushardi.
export RANKWANT_DEPLOY_SCOPE=all

{
  printf 'measure_deploy mode=%s purge_idle=%s\n' "$MODE" "$PURGE_IDLE"
  bash "$ROOT/tools/deploy.sh" "${DEPLOY_ARGS[@]}"
} 2>&1 | tee -a "$LOG"
st=${PIPESTATUS[0]}
# deploy.sh o'zi time_summary yozadi; TSV/JSON shu env orqali to'ladi.
write_md
if [ "$st" -ne 0 ]; then
  die "deploy.sh exit $st — qisman hisobot: $OUT_DIR/$STAMP"
fi
printf '%sE2E olchov tugadi: %s%s\n' "$G" "$MD" "$N"
