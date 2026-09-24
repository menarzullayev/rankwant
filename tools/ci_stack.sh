#!/usr/bin/env bash
# Build the CI compose images with GHCR layer reuse, then bring the stack up.
#
# Hosted `ubuntu-latest` is a fresh VM: Dockerfile `--mount=type=cache` dies
# with the machine. GHCR keeps the last successful `ci-*:main` image. If the
# build context hash matches the image label, skip `docker build` and only
# `docker tag` — a warm run measured 120–180 s when build still exported
# cached layers. Do NOT also write `type=gha` docker cache — the repo's
# 10 GB Actions cache quota is for pip/npm/mypy.
#
# Env:
#   COMPOSE_PROJECT_NAME  required (compose project / local image prefix)
#   GITHUB_TOKEN          GHCR login (optional on a cold first run)
#   GITHUB_ACTOR, GITHUB_REPOSITORY, GITHUB_SHA  — Actions defaults
#   CI_PUSH_IMAGE_CACHE   unused during build; `--push-only` reads it
#   CI_STACK_SERVICES     comma list, default api,web,judge
#   CI_STACK_UP           1 (default) compose up --no-build --wait; 0 skip
#   CI_STACK_UP_SERVICES  optional compose service list (bake-off: redis,judge)
#   NEXT_PUBLIC_API_BASE  web build-arg (same default as docker-compose.yml)
#
# Usage:
#   bash tools/ci_stack.sh              # pull / tag or build, then up
#   bash tools/ci_stack.sh --push-only  # push local images to GHCR
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"

project="${COMPOSE_PROJECT_NAME:?COMPOSE_PROJECT_NAME is required}"
# `docker-compose.ci.yml` host portlarini o'chiradi, ya'ni u JONLI
# `rankwant` loyihasida ishlatilsa tunnel 8301 ni topmaydi va API 503
# bo'ladi (o'lchandi 2026-09-24, run 35956178549). Faylning o'zida
# qo'riqchi bor — bu yerda o'sha sentinel qo'yiladi.
export CI_ONLY_STACK=1
repo_lc="$(printf '%s' "${GITHUB_REPOSITORY:-menarzullayev/rankwant}" | tr '[:upper:]' '[:lower:]')"
registry="ghcr.io/${repo_lc}"
sha="${GITHUB_SHA:-unknown}"
built_at="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
services="${CI_STACK_SERVICES:-api,web,judge}"
stack_up="${CI_STACK_UP:-1}"
up_services="${CI_STACK_UP_SERVICES:-}"
next_api="${NEXT_PUBLIC_API_BASE:-http://localhost:8000/api/v1}"
mode="${1:-build}"

export DOCKER_BUILDKIT=1

ghcr_login() {
  if [ -n "${GITHUB_TOKEN:-}" ]; then
    printf '%s' "$GITHUB_TOKEN" | docker login ghcr.io -u "${GITHUB_ACTOR:-github}" --password-stdin
  fi
}

remote_for() {
  printf '%s/ci-%s:main' "$registry" "$1"
}

# Hash of tracked files in a build context, plus extra strings (build-args).
# Untracked local dirt is ignored — CI checks out a clean tree.
#
# ⚠️ Bir nechta yo'l qabul qiladi (2026-09-24). Sabab: `web` obrazi endi
# REPO ILDIZIDAN quriladi (`apps/web/Dockerfile` + `COPY packages`), ya'ni
# uning konteksti `apps/web` bilan cheklanmaydi. Faqat `apps/web` ni
# xeshlash `packages/shared` o'zgarganda ESKI obrazni qayta ishlatardi —
# ya'ni jimgina eskirgan frontend. Shuning uchun ikkisi ham xeshga kiradi.
#
# Har bir argument: yo'l. `+` bilan boshlanadigani qo'shimcha satr
# (masalan build-arg), yo'l emas.
context_hash() {
  local -a paths=() extras=()
  local arg
  for arg in "$@"; do
    case "$arg" in
      +*) extras+=("${arg#+}") ;;
      *)  paths+=("$arg") ;;
    esac
  done
  {
    printf '%s\n' "${extras[@]}"
    git -C "$root" ls-files -- "${paths[@]}" | sort | git -C "$root" hash-object --stdin-paths
  } | sha256sum | awk '{print $1}'
}

image_context_hash() {
  docker image inspect -f '{{index .Config.Labels "org.rankwant.context-hash"}}' "$1" 2>/dev/null || true
}

wanted_names() {
  local name
  IFS=',' read -r -a raw <<<"$services"
  for name in "${raw[@]}"; do
    name="$(printf '%s' "$name" | tr -d '[:space:]')"
    [ -n "$name" ] || continue
    printf '%s\n' "$name"
  done
}

push_one() {
  local name="$1"
  local local_tag="${project}-${name}"
  local remote
  remote="$(remote_for "$name")"
  docker tag "$local_tag" "$remote"
  docker push "$remote"
}

# Pull GHCR `:main`. Tag it locally when the context hash matches.
# Otherwise rebuild with `--cache-from` (still no `type=gha`).
resolve_one() {
  local name="$1"
  local context="$2"
  local hash="$3"
  shift 3
  local local_tag="${project}-${name}"
  local remote
  remote="$(remote_for "$name")"
  local -a extra=("$@")
  local pulled=0
  local remote_hash=""

  if docker pull "$remote"; then
    pulled=1
    remote_hash="$(image_context_hash "$remote")"
    if [ -n "$remote_hash" ] && [ "$remote_hash" = "$hash" ]; then
      echo "--> reuse $remote (context $hash)"
      docker tag "$remote" "$local_tag"
      return 0
    fi
    echo "--> rebuild $name (GHCR hash=${remote_hash:-none} local=$hash)"
  else
    echo "--> cold build $name (no $remote)"
  fi

  local -a cache=()
  if [ "$pulled" = "1" ]; then
    cache+=(--cache-from "$remote")
  fi

  docker build \
    --build-arg BUILDKIT_INLINE_CACHE=1 \
    --build-arg GIT_SHA="$sha" \
    --build-arg BUILT_AT="$built_at" \
    --label "org.rankwant.context-hash=${hash}" \
    "${cache[@]}" \
    "${extra[@]}" \
    -t "$local_tag" \
    "$context"
}

build_wanted() {
  local name="$1"
  local hash
  case "$name" in
    api)
      hash="$(context_hash apps/api)"
      resolve_one api apps/api "$hash"
      docker tag "${project}-api" "${project}-migrate"
      docker tag "${project}-api" "${project}-worker"
      docker tag "${project}-api" "${project}-beat"
      ;;
    web)
      # ⚠️ Kontekst — REPO ILDIZI (2026-09-24). `apps/web/Dockerfile`
      # `COPY packages ./packages` qiladi, ya'ni kontekst ildiz bo'lishi
      # SHART. Ilgari bu yerda `apps/web` turardi va Nightly'ning 4 job'i
      # (E2E, Chaos, Load, Latency) shu sabab yiqilardi:
      #
      #     Dockerfile:72 >>> COPY packages ./packages
      #     ERROR: failed to compute cache key: "/packages": not found
      #
      # `docker-compose.yml` bilan bir xil (`context: .` +
      # `dockerfile: apps/web/Dockerfile`) — ikkisi ajralib ketmasin.
      hash="$(context_hash apps/web packages/shared "+NEXT_PUBLIC_API_BASE=${next_api}")"
      resolve_one web . "$hash" \
        -f apps/web/Dockerfile \
        --build-arg "NEXT_PUBLIC_API_BASE=${next_api}"
      ;;
    judge)
      hash="$(context_hash services/judge-go)"
      resolve_one judge services/judge-go "$hash"
      ;;
    *)
      echo "unknown CI_STACK_SERVICES entry: $name" >&2
      return 2
      ;;
  esac
}

wait_all() {
  local pid fail=0
  for pid in "$@"; do
    if ! wait "$pid"; then
      fail=1
    fi
  done
  return "$fail"
}

ghcr_login

if [ "$mode" = "--push-only" ]; then
  pids=()
  while IFS= read -r name; do
    push_one "$name" &
    pids+=("$!")
  done < <(wanted_names)
  wait_all "${pids[@]}"
  exit 0
fi

if [ "$mode" != "build" ]; then
  echo "usage: $0 [--push-only]" >&2
  exit 2
fi

pids=()
while IFS= read -r name; do
  build_wanted "$name" &
  pids+=("$!")
done < <(wanted_names)
wait_all "${pids[@]}"

if [ "$stack_up" = "1" ]; then
  if [ -n "$up_services" ]; then
    # shellcheck disable=SC2086
    docker compose -f docker-compose.yml -f docker-compose.ci.yml \
      up -d --no-build --wait $up_services
  else
    docker compose -f docker-compose.yml -f docker-compose.ci.yml up -d --no-build --wait
  fi
fi
