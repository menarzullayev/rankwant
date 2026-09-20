#!/usr/bin/env bash
# Deploy bosqichlari uchun wall-clock taymer.
#
# Git Bash `date +%N` ni ko'pincha literal `N` deb chop etadi, shuning
# uchun interval `time.perf_counter()` orqali o'lchanadi. `date +%s`
# faqat Python yo'q bo'lsa (butun soniya) ishlatiladi.
#
# Manba: `. tools/deploy_timer.sh`
# Yozuv: `RANKWANT_DEPLOY_TIMING=path.tsv` (har finish qatori)
#        `RANKWANT_DEPLOY_TIMING_JSON=path.json` (`time_summary` da)
#
# Chiqish qatori (mashina o'qishi uchun):
#   TIMER start name=build
#   TIMER finish name=build sec=87.123
#
# O'zi: `bash tools/deploy_timer.sh --self-test`

# shellcheck disable=SC2034
_RW_TIMER_STACK_NAMES=()
_RW_TIMER_STACK_START=()
_RW_TIMER_DONE_NAMES=()
_RW_TIMER_DONE_SECS=()
_RW_TIMER_SUMMARIZED=0
_RW_TIMER_PY="${_RW_TIMER_PY:-}"

_rw_timer_init() {
  if [ -n "${_RW_TIMER_PY:-}" ]; then
    return 0
  fi
  local root pick
  root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
  pick="$root/tools/pick-python.sh"
  if [ -f "$pick" ]; then
    _RW_TIMER_PY="$(bash "$pick" 2>/dev/null)" || _RW_TIMER_PY=""
  fi
  if [ -z "${_RW_TIMER_PY:-}" ]; then
    if command -v python >/dev/null 2>&1; then
      _RW_TIMER_PY=python
    elif command -v python3 >/dev/null 2>&1; then
      _RW_TIMER_PY=python3
    fi
  fi
}

_rw_timer_now() {
  _rw_timer_init
  if [ -n "${_RW_TIMER_PY:-}" ]; then
    "$_RW_TIMER_PY" -c "import time; print(f'{time.perf_counter():.6f}')"
  else
    date +%s
  fi
}

_rw_timer_sub() {
  # $1 = end, $2 = start  (perf_counter yoki epoch)
  _rw_timer_init
  if [ -n "${_RW_TIMER_PY:-}" ]; then
    RW_T1="$1" RW_T0="$2" "$_RW_TIMER_PY" -c \
      "import os; print(f'{float(os.environ[\"RW_T1\"]) - float(os.environ[\"RW_T0\"]):.3f}')"
  else
    echo $(( ${1%%.*} - ${2%%.*} ))
  fi
}

time_begin() {
  local name="${1:?time_begin: nom kerak}"
  local start
  # init shu shell'da: `_rw_timer_now` command-substitution ichida,
  # u yerda qo'yilgan `_RW_TIMER_PY` yo'qoladi.
  _rw_timer_init
  start="$(_rw_timer_now)" || start="$(date +%s)"
  _RW_TIMER_STACK_NAMES+=("$name")
  _RW_TIMER_STACK_START+=("$start")
  printf 'TIMER start name=%s\n' "$name"
}

time_finish() {
  local expected="${1:-}"
  local n name start now sec iso
  _rw_timer_init
  n=${#_RW_TIMER_STACK_NAMES[@]}
  if [ "$n" -eq 0 ]; then
    return 0
  fi
  name="${_RW_TIMER_STACK_NAMES[$((n - 1))]}"
  start="${_RW_TIMER_STACK_START[$((n - 1))]}"
  unset "_RW_TIMER_STACK_NAMES[$((n - 1))]"
  unset "_RW_TIMER_STACK_START[$((n - 1))]"
  if [ -n "$expected" ] && [ "$expected" != "$name" ]; then
    printf 'TIMER warn expected=%s open=%s\n' "$expected" "$name" >&2
  fi
  now="$(_rw_timer_now)" || now="$(date +%s)"
  sec="$(_rw_timer_sub "$now" "$start")" || sec=0
  _RW_TIMER_DONE_NAMES+=("$name")
  _RW_TIMER_DONE_SECS+=("$sec")
  iso="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
  printf 'TIMER finish name=%s sec=%s\n' "$name" "$sec"
  if [ -n "${RANKWANT_DEPLOY_TIMING:-}" ]; then
    mkdir -p "$(dirname "$RANKWANT_DEPLOY_TIMING")" 2>/dev/null || true
    printf '%s\t%s\t%s\n' "$name" "$sec" "$iso" >> "$RANKWANT_DEPLOY_TIMING"
  fi
}

time_finish_open() {
  while [ ${#_RW_TIMER_STACK_NAMES[@]} -gt 0 ]; do
    time_finish
  done
}

time_summary() {
  local i name sec
  _rw_timer_init
  if [ "${_RW_TIMER_SUMMARIZED}" = "1" ]; then
    return 0
  fi
  _RW_TIMER_SUMMARIZED=1
  time_finish_open
  if [ ${#_RW_TIMER_DONE_NAMES[@]} -eq 0 ]; then
    return 0
  fi
  printf 'TIMER summary\n'
  for i in "${!_RW_TIMER_DONE_NAMES[@]}"; do
    name="${_RW_TIMER_DONE_NAMES[$i]}"
    sec="${_RW_TIMER_DONE_SECS[$i]}"
    printf '  %-18s %s\n' "$name" "$sec"
  done
  if [ -n "${RANKWANT_DEPLOY_TIMING_JSON:-}" ] && [ -n "${_RW_TIMER_PY:-}" ]; then
    mkdir -p "$(dirname "$RANKWANT_DEPLOY_TIMING_JSON")" 2>/dev/null || true
    # JSON ni bash yo'liga yozamiz: Windows Python `/tmp/...` ni boshqa joy
    # deb ochadi, TSV esa bash `printf >>` bilan shu yerda.
    {
      for i in "${!_RW_TIMER_DONE_NAMES[@]}"; do
        printf '%s\t%s\n' "${_RW_TIMER_DONE_NAMES[$i]}" "${_RW_TIMER_DONE_SECS[$i]}"
      done
    } | RW_MODE="${RANKWANT_MEASURE_MODE:-}" RW_SHA="${GIT_SHA:-}" \
      "$_RW_TIMER_PY" -c '
import json, os, sys
from datetime import datetime, timezone
steps = []
e2e = None
for line in sys.stdin:
    parts = line.rstrip("\n").split("\t")
    if len(parts) < 2:
        continue
    name, raw = parts[0], parts[1]
    try:
        val = float(raw)
    except ValueError:
        val = 0.0
    steps.append({"name": name, "sec": val})
    if name == "e2e":
        e2e = val
payload = {
    "mode": os.environ.get("RW_MODE") or None,
    "commit": os.environ.get("RW_SHA") or None,
    "finished_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "e2e_sec": e2e,
    "steps": steps,
}
json.dump(payload, sys.stdout, indent=2)
sys.stdout.write("\n")
' > "$RANKWANT_DEPLOY_TIMING_JSON"
  fi
}

_rw_timer_self_test() {
  local tmp sec
  tmp="$(mktemp -d "${TMPDIR:-/tmp}/rw-timer.XXXXXX")"
  RANKWANT_DEPLOY_TIMING="$tmp/t.tsv"
  RANKWANT_DEPLOY_TIMING_JSON="$tmp/t.json"
  _RW_TIMER_SUMMARIZED=0
  _RW_TIMER_DONE_NAMES=()
  _RW_TIMER_DONE_SECS=()
  time_begin selftest
  sleep 0.25
  time_finish selftest
  time_summary
  if [ ! -s "$RANKWANT_DEPLOY_TIMING" ]; then
    printf 'self-test: TSV yozilmadi\n' >&2
    rm -rf "$tmp"
    return 1
  fi
  sec="$(awk -F'\t' 'NR==1{print $2}' "$RANKWANT_DEPLOY_TIMING")"
  _rw_timer_init
  if [ -z "${_RW_TIMER_PY:-}" ]; then
    printf 'self-test: Python yoq — interval tekshirilmadi (sec=%s)\n' "$sec" >&2
    rm -rf "$tmp"
    return 1
  fi
  if ! RW_SEC="$sec" "$_RW_TIMER_PY" -c \
    "import os,sys; sys.exit(0 if float(os.environ['RW_SEC']) >= 0.20 else 1)"; then
    printf 'self-test: interval juda qisqa: %s\n' "$sec" >&2
    rm -rf "$tmp"
    return 1
  fi
  if [ ! -s "$RANKWANT_DEPLOY_TIMING_JSON" ]; then
    printf 'self-test: JSON yozilmadi\n' >&2
    rm -rf "$tmp"
    return 1
  fi
  rm -rf "$tmp"
  printf 'self-test: ok (sec=%s)\n' "$sec"
}

if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
  set -uo pipefail
  case "${1:-}" in
    --self-test) _rw_timer_self_test ;;
    -h|--help)
      sed -n '2,18p' "$0" | sed 's/^# \{0,1\}//'
      ;;
    *)
      printf 'Ishlatish: bash tools/deploy_timer.sh --self-test\n' >&2
      exit 2
      ;;
  esac
fi
