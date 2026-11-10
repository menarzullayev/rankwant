#!/usr/bin/env bash
# Disk: SHA teglar, dangling obrazlar, build cache.
#
# NEGA: 2026-09-15..20 da `docker_data.vhdx` 40 GB → 132 GB. Har deploy
# `rankwant/<svc>:<sha12>` tegini qoldirardi; VHDX prune'dan keyin ham
# kichraymaydi, shuning uchun teglar umuman saqlanmaydi (Saidakbar aka,
# 2026-09-20). Rollback — kerakli commitni qayta qurish, obraz arxivi emas.
#
# NIMANI O'CHIRMAYDI:
#   * `rankwant-<svc>:latest` (jonli stack shu nomni ishlatadi)
#   * `rankwant/ci-runner:latest` (self-hosted runner)
#   * named volume'lar (postgres / minio / CI work) — `volume prune` YO'Q
#
# `docker rmi repo:tag` faqat tegini olib tashlaydi. Bir xil ID da
# `rankwant-api:latest` qolsa, ishlab turgan obraz o'chmaydi.

set -uo pipefail

G=$'\033[32m'; Y=$'\033[33m'; N=$'\033[0m'
ok() { printf '%s✓%s %s\n' "$G" "$N" "$1"; }
warn() { printf '%s⚠ %s%s\n' "$Y" "$1" "$N"; }

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# Build cache budget and the disk guard (owner decision 2026-11-10).
CACHE_MAX_GB="${RANKWANT_BUILD_CACHE_MAX_GB:-10}"
DISK_MIN_FREE_GB="${RANKWANT_DISK_MIN_FREE_GB:-5}"
# The disk that holds Docker Desktop's VHDX. `/c` in Git Bash on the host.
if [ -n "${RANKWANT_DISK_GUARD_PATH:-}" ]; then
  GUARD_PATH="$RANKWANT_DISK_GUARD_PATH"
elif [ -d /c ]; then
  GUARD_PATH=/c
else
  GUARD_PATH=/
fi

# `docker system df` prints decimal units: 0B, 512.3kB, 1.2MB, 10.5GB.
to_bytes() {
  awk '{ n = $0; u = $0; gsub(/[^0-9.]/, "", n); gsub(/[0-9. ]/, "", u)
         m = 1
         if (u == "kB" || u == "KB") m = 1e3; else if (u == "MB") m = 1e6
         else if (u == "GB") m = 1e9; else if (u == "TB") m = 1e12
         if (n == "") { print ""; exit } printf "%.0f\n", n * m }'
}
gb() { awk -v b="$1" 'BEGIN { printf "%.1f", b / 1e9 }'; }

if ! command -v docker >/dev/null 2>&1; then
  printf '%sdocker topilmadi — tozalash otkazib yuborildi%s\n' "$Y" "$N"
  exit 0
fi
if ! docker info >/dev/null 2>&1; then
  printf '%sDocker engine javob bermayapti — tozalash otkazib yuborildi%s\n' "$Y" "$N"
  exit 0
fi

# 1. SHA / rollback teglari. `rankwant/ci-runner` bu naqshga tushMAYDI.
removed=0
while IFS= read -r img; do
  [ -n "$img" ] || continue
  if docker rmi "$img" >/dev/null 2>&1; then
    removed=$((removed + 1))
    printf '  - %s\n' "$img"
  fi
done < <(docker images --format '{{.Repository}}:{{.Tag}}' \
  | grep -E '^rankwant/(api|worker|beat|judge|web|migrate):' || true)
ok "SHA/rollback teglari olib tashlandi: ${removed}"

# 2. deploy.yml build job'ining `rankwant-build-<run_id>-*` obrazlari.
# Ular jonli `rankwant-<svc>:latest` EMAS — boshqa compose loyihasi.
build_removed=0
while IFS= read -r img; do
  [ -n "$img" ] || continue
  if docker rmi -f "$img" >/dev/null 2>&1; then
    build_removed=$((build_removed + 1))
    printf '  - %s\n' "$img"
  fi
done < <(docker images --format '{{.Repository}}:{{.Tag}}' \
  | grep -E '^rankwant-build-' || true)
ok "rankwant-build-* obrazlar: ${build_removed}"

# 3. Tegdan ajralgan layerlar (1–2-qadamdan keyin dangling).
# `-a` YO'Q: ishlatilmayotgan tagged postgres/redis ham ketardi.
docker image prune -f >/dev/null || true
ok "dangling obrazlar prune qilindi"

# 4. Old judge base images. `tools/deploy.sh` keeps the judge's toolchain
# layer as `rankwant-judge-base:<Dockerfile hash>`; only the current one is
# worth keeping, an older one belongs to a Dockerfile that no longer exists.
judge_base_tag=""
if [ -f "$ROOT/services/judge-go/Dockerfile" ]; then
  judge_base_tag="$(sha256sum "$ROOT/services/judge-go/Dockerfile" < /dev/null | cut -c1-12)"
fi
old_bases=0
while IFS= read -r img; do
  [ -n "$img" ] || continue
  [ "$img" = "rankwant-judge-base:$judge_base_tag" ] && continue
  if docker rmi "$img" >/dev/null 2>&1; then
    old_bases=$((old_bases + 1))
    printf '  - %s\n' "$img"
  fi
done < <(docker images --format '{{.Repository}}:{{.Tag}}' | grep -E '^rankwant-judge-base:' || true)
ok "eski judge base obrazlari: ${old_bases}"

# 5. Build cache — kept up to its budget (owner decision 2026-11-10).
# Until then every deploy cleared it all, so every deploy built cold:
# measured over 34 deploys, build was 79% of a deploy (median 136 s, of
# which `npm ci` 46 s) and a judge change took 22 minutes. Now it is
# cleared only above CACHE_MAX_GB, when its size cannot be read, or when
# the disk holding Docker's VHDX has less than DISK_MIN_FREE_GB left.
# Clearing stays `-af`: measured 2026-10-06, the cache reached 69.6 GB in
# 36 hours, `docker builder prune -f` freed 0 B and so did
# `--max-used-space 10GB`. Images and volumes are not touched.
cache_bytes="$(docker system df --format '{{.Type}}|{{.Size}}' 2>/dev/null \
  | awk -F'|' '$1 == "Build Cache" { print $2 }' | to_bytes)"
free_bytes="$(df -Pk "$GUARD_PATH" 2>/dev/null | awk 'NR == 2 { printf "%.0f\n", $4 * 1024 }')"
reason=""
if [ -z "$cache_bytes" ]; then
  reason="kesh hajmi o'qilmadi"
elif [ "$cache_bytes" -gt "$((CACHE_MAX_GB * 1000000000))" ]; then
  reason="kesh $(gb "$cache_bytes") GB > ${CACHE_MAX_GB} GB"
fi
if [ -n "$free_bytes" ] && [ "$free_bytes" -lt "$((DISK_MIN_FREE_GB * 1000000000))" ]; then
  reason="${reason:+$reason; }$GUARD_PATH da $(gb "$free_bytes") GB qoldi (< ${DISK_MIN_FREE_GB} GB)"
  warn "disk qo'riqchisi: $GUARD_PATH da atigi $(gb "$free_bytes") GB bo'sh"
fi
if [ -n "$reason" ]; then
  docker builder prune -af >/dev/null || true
  ok "builder cache tozalandi ($reason)"
else
  ok "builder cache saqlandi: $(gb "$cache_bytes") GB ≤ ${CACHE_MAX_GB} GB, $GUARD_PATH da $(gb "${free_bytes:-0}") GB bo'sh"
fi
vhdx="${LOCALAPPDATA:-}/Docker/wsl/disk/docker_data.vhdx"
if [ -n "${LOCALAPPDATA:-}" ] && [ -f "$vhdx" ]; then
  ok "VHDX: $(gb "$(wc -c < "$vhdx" | tr -d '[:space:]')") GB"
fi
