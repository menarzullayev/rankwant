#!/usr/bin/env bash
# Build the CI compose images with GHCR layer reuse, then bring the stack up.
#
# Hosted `ubuntu-latest` is a fresh VM: Dockerfile `--mount=type=cache` dies
# with the machine. GHCR keeps the last successful `ci-*:main` image so the
# next run only rebuilds changed layers. Do NOT also write `type=gha` docker
# cache — the repo's 10 GB Actions cache quota is for pip/npm/mypy, and the
# judge image would evict them.
#
# Env:
#   COMPOSE_PROJECT_NAME  required (compose project / local image prefix)
#   GITHUB_TOKEN          GHCR login (optional on a cold first run)
#   GITHUB_ACTOR, GITHUB_REPOSITORY, GITHUB_SHA  — Actions defaults
#   CI_PUSH_IMAGE_CACHE   unused during build; `--push-only` reads it
#   CI_STACK_SERVICES     comma list, default api,web,judge
#   CI_STACK_UP           1 (default) compose up --no-build --wait; 0 skip
#   NEXT_PUBLIC_API_BASE  web build-arg (same default as docker-compose.yml)
#
# Usage:
#   bash tools/ci_stack.sh              # pull cache, build in parallel, up
#   bash tools/ci_stack.sh --push-only  # push local images to GHCR
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"

project="${COMPOSE_PROJECT_NAME:?COMPOSE_PROJECT_NAME is required}"
repo_lc="$(printf '%s' "${GITHUB_REPOSITORY:-menarzullayev/rankwant}" | tr '[:upper:]' '[:lower:]')"
registry="ghcr.io/${repo_lc}"
sha="${GITHUB_SHA:-unknown}"
built_at="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
services="${CI_STACK_SERVICES:-api,web,judge}"
stack_up="${CI_STACK_UP:-1}"
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

build_one() {
  local name="$1"
  local context="$2"
  shift 2
  local local_tag="${project}-${name}"
  local remote
  remote="$(remote_for "$name")"
  local -a extra=("$@")
  local -a cache=()

  if docker pull "$remote"; then
    cache+=(--cache-from "$remote")
  fi

  docker build \
    --build-arg BUILDKIT_INLINE_CACHE=1 \
    --build-arg GIT_SHA="$sha" \
    --build-arg BUILT_AT="$built_at" \
    "${cache[@]}" \
    "${extra[@]}" \
    -t "$local_tag" \
    "$context"
}

build_wanted() {
  local name="$1"
  case "$name" in
    api)
      build_one api apps/api
      docker tag "${project}-api" "${project}-migrate"
      docker tag "${project}-api" "${project}-worker"
      docker tag "${project}-api" "${project}-beat"
      ;;
    web)
      build_one web apps/web --build-arg "NEXT_PUBLIC_API_BASE=${next_api}"
      ;;
    judge)
      build_one judge services/judge-go
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
  docker compose -f docker-compose.yml -f docker-compose.ci.yml up -d --no-build --wait
fi
