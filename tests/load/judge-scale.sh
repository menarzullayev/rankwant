#!/usr/bin/env bash
# Judge horizontal scale — recipe.
#
# Capacity (ADR-0004 bake-off, measured 2026-09-06):
#
#   workers   throughput      p95
#   1         2.4 submit/s    857 ms
#   4         5.4 submit/s    952 ms
#   8         8.0 submit/s   1360 ms
#
# Scaling is sub-linear: 8 workers give 8.0/s, not 19.2/s. About 830 ms of
# `total_ms` is compilation, which is CPU-bound, so past the core count
# extra workers buy very little.
#
# Two independent limits decide how many you need.
#
#   1. Throughput.  hosts = ceil(rate / 8)
#        design assumption   50.0/s -> 6.3 -> 6-8 hosts
#        measured CF peak    76.1/s -> 9.5 -> 10 hosts
#      The 50/s figure is what `apps/api/judging/services.py` assumes
#      ("Contest spike'da 500 submit/10s bo'ladi"). The 76.1/s figure is
#      what Codeforces Div. 3 #1996 actually did, measured 2026-09-20.
#      So the platform's own design note under-provisions by ~1.5x.
#
#   2. Accounts. `submit` is throttled at 6/min per user, so one account
#      cannot send more than one submission per 10 seconds. A 76/s spike
#      needs 76 * 60 / 6 = 760 distinct accounts. Fewer than that and the
#      run measures the throttle, not the judge.
#
# Locally the judge is a SINGLE serial process — `services/judge-go/main.go`
# is `for { BRPOP -> judge() -> LPUSH }` with no worker pool. One container
# is therefore one worker (2.4/s), and `--scale judge=N` is the only lever.
#
# Usage:
#   tests/load/judge-scale.sh status
#   tests/load/judge-scale.sh plan 76.1
#   tests/load/judge-scale.sh up 8
#   tests/load/judge-scale.sh watch
#   tests/load/judge-scale.sh down
#
# Run from the repo root.

set -euo pipefail

PROJECT=rankwant
ENV_FILE=.env.public
COMPOSE=(
  docker compose -p "$PROJECT" --env-file "$ENV_FILE"
  -f docker-compose.yml -f docker-compose.public.yml
)

JOBS_KEY=rankwant:judge:jobs
RESULTS_KEY=rankwant:judge:results

#: Measured throughput of one 8-worker host (ADR-0004).
PER_HOST=8.0
#: `submit` throttle, submissions per minute per user.
SUBMIT_PER_MIN=6
#: Which container the queue can be inspected through.
REDIS=rankwant-redis-1

die() { echo "xato: $*" >&2; exit 1; }

require_root() {
  [ -f docker-compose.yml ] || die "repo ildizida emas (docker-compose.yml yo'q)"
  [ -f "$ENV_FILE" ] || die "$ENV_FILE yo'q"
}

cmd_status() {
  require_root
  echo "=== judge konteynerlari ==="
  docker ps --filter "label=com.docker.compose.project=$PROJECT" \
            --filter "label=com.docker.compose.service=judge" \
            --format "table {{.Names}}\t{{.Status}}" || true
  local n
  n=$(docker ps -q --filter "label=com.docker.compose.project=$PROJECT" \
                   --filter "label=com.docker.compose.service=judge" | wc -l)
  echo
  echo "worker soni : $n"
  echo "nazariy     : $(awk -v n="$n" -v p="$PER_HOST" 'BEGIN{printf "%.1f", n*p}') submit/s (chiziqli emas, yuqori chegara)"
  echo "navbat      : $(queue_depth) job"
}

queue_depth() {
  docker exec "$REDIS" redis-cli LLEN "$JOBS_KEY" 2>/dev/null || echo "?"
}

# plan <rate> — how many hosts and accounts a target rate needs.
cmd_plan() {
  local rate="${1:?rate kerak, masalan: plan 76.1}"
  awk -v r="$rate" -v p="$PER_HOST" -v s="$SUBMIT_PER_MIN" 'BEGIN{
    printf "maqsad tezlik   : %.1f submit/s\n", r
    printf "kerak host      : %.1f -> %d host (har biri 8 worker)\n", r/p, int(r/p)+1
    printf "kerak worker    : %d\n", int(r/p*8)+1
    printf "kerak hisob     : %d ta (submit %d/min, ya'\''ni 1 ta / 10 s)\n", int(r*60/s)+1, s
  }'
}

cmd_up() {
  require_root
  local n="${1:?worker soni kerak, masalan: up 8}"
  [ "$n" -ge 1 ] || die "worker soni musbat bo'lishi kerak"
  echo "judge ni $n ga ko'taraman..."
  "${COMPOSE[@]}" up -d --no-deps --scale "judge=$n" judge
  sleep 3
  cmd_status
}

cmd_down() {
  require_root
  echo "judge ni 1 ga qaytaraman..."
  "${COMPOSE[@]}" up -d --no-deps --scale judge=1 judge
  sleep 3
  cmd_status
}

# watch — live queue depth, so a saturating judge is visible while it runs.
cmd_watch() {
  local interval="${1:-2}"
  echo "navbat chuqurligi (har ${interval}s, Ctrl-C to'xtatadi)"
  echo "  vaqt      jobs   results"
  while true; do
    printf "  %s  %6s  %7s\n" "$(date +%H:%M:%S)" "$(queue_depth)" \
      "$(docker exec "$REDIS" redis-cli LLEN "$RESULTS_KEY" 2>/dev/null || echo '?')"
    sleep "$interval"
  done
}

case "${1:-status}" in
  status) cmd_status ;;
  plan)   shift; cmd_plan "$@" ;;
  up)     shift; cmd_up "$@" ;;
  down)   cmd_down ;;
  watch)  shift; cmd_watch "$@" ;;
  *) die "noma'lum buyruq: $1 (status|plan|up|down|watch)" ;;
esac
