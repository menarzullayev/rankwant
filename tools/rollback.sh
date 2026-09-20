#!/usr/bin/env bash
# Rollback — 2026-09-20 dan SHA obraz teglari SAQLANMAYDI.
#
# NEGA: har deploy `rankwant/<svc>:<sha12>` qoldirsa Docker VHDX o'saveradi
# (o'lchandi 2026-09-15..20: 40 GB → 132 GB). Prune Windows'ga joy
# qaytarmaydi. Shuning uchun `tools/deploy.sh` teg qo'ymaydi va muvaffaqiyatli
# deploy'dan keyin qolganlarini `tools/prune_docker_disk.sh` o'chiradi.
#
# Kodni qaytarish: kerakli commitni deploy worktree'da checkout qilib
# `bash tools/deploy.sh --yes` (qayta quriladi). Sxema — deploy oldidagi
# `pg-deploy-*.sql.gz` dump, QO'LDA. Migratsiya avtomatik qaytarilmaydi.
#
#   bash tools/rollback.sh --list
#   bash tools/rollback.sh <sha12>   # baribir rad etiladi — izoh chiqadi

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

G=$'\033[32m'; R=$'\033[31m'; Y=$'\033[33m'; N=$'\033[0m'

die() { printf '%s✗ %s%s\n' "$R" "$1" "$N"; exit 1; }

LIST_ONLY=0
for arg in "$@"; do
  case "$arg" in
    --list) LIST_ONLY=1 ;;
    --yes|-y) ;;
    -h|--help) sed -n '2,20p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    -*) die "noma'lum argument: $arg" ;;
    *) ;;
  esac
done

if [ "$LIST_ONLY" -eq 1 ]; then
  printf '%s2026-09-20: SHA obraz teglari saqlanmaydi.%s\n' "$Y" "$N"
  echo "Kodni qaytarish: deploy worktree'da kerakli commit + bash tools/deploy.sh --yes"
  echo "Sxema: <backup dir>/pg-deploy-*.sql.gz — qo'lda."
  echo
  echo "Agar eski teg qolgan bo'lsa (tozalanmagan mashina):"
  docker images --format '{{.Repository}}:{{.Tag}}\t{{.CreatedSince}}' \
    | grep -E '^rankwant/(api|worker|beat|judge|web|migrate):' | sort || true
  exit 0
fi

die "SHA obraz teglari saqlanmaydi (2026-09-20). Kod: kerakli commitni qayta quring (tools/deploy.sh). Sxema: pg-deploy dump, qo'lda. Qolgan teglar: bash tools/rollback.sh --list"
