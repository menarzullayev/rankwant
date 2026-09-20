#!/usr/bin/env bash
# Disk: SHA teglar, dangling obrazlar, ishlatilmayotgan build cache.
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

# 4. Ishlatilmayotgan build cache. `--all` YO'Q: joriy qurilish
# layerlari keyingi deploy'ni isitadi; yuqori chegara daemon'da 5 GB.
docker builder prune -f >/dev/null || true
ok "ishlatilmayotgan builder cache prune qilindi"
