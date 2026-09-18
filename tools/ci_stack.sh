#!/usr/bin/env bash
# Build the CI compose images with GHCR layer reuse, then bring the stack up.
#
# Hosted `ubuntu-latest` is a fresh VM: Dockerfile `--mount=type=cache` dies
# with the machine. GHCR keeps the last `main` image so the next run only
# rebuilds changed layers. Do NOT also write `type=gha` docker cache — the
# repo's 10 GB Actions cache quota is for pip/npm/mypy, and the judge image
# would evict them.
#
# Env:
#   COMPOSE_PROJECT_NAME  required (compose project / local image prefix)
#   GITHUB_TOKEN          GHCR login (optional on a cold first run)
#   GITHUB_ACTOR, GITHUB_REPOSITORY, GITHUB_SHA  — Actions defaults
#   CI_PUSH_IMAGE_CACHE   1 on main: push :main after a successful build
#   CI_STACK_SERVICES     comma list, default api,web,judge
#   CI_STACK_UP           1 (default) compose up --no-build --wait; 0 skip
#   NEXT_PUBLIC_API_BASE  web build-arg (same default as docker-compose.yml)
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"

project="${COMPOSE_PROJECT_NAME:?COMPOSE_PROJECT_NAME is required}"
repo_lc="$(printf '%s' "${GITHUB_REPOSITORY:-menarzullayev/rankwant}" | tr '[:upper:]' '[:lower:]')"
registry="ghcr.io/${repo_lc}"
sha="${GITHUB_SHA:-unknown}"
built_at="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
push="${CI_PUSH_IMAGE_CACHE:-0}"
services="${CI_STACK_SERVICES:-api,web,judge}"
stack_up="${CI_STACK_UP:-1}"
next_api="${NEXT_PUBLIC_API_BASE:-http://localhost:8000/api/v1}"

export DOCKER_BUILDKIT=1

if [ -n "${GITHUB_TOKEN:-}" ]; then
  printf '%s' "$GITHUB_TOKEN" | docker login ghcr.io -u "${GITHUB_ACTOR:-github}" --password-stdin
fi

build_one() {
  local name="$1"
  local context="$2"
  shift 2
  local local_tag="${project}-${name}"
  local remote="${registry}/ci-${name}:main"
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

  if [ "$push" = "1" ]; then
    docker tag "$local_tag" "$remote"
    docker push "$remote"
  fi
}

IFS=',' read -r -a wanted <<<"$services"
for name in "${wanted[@]}"; do
  name="$(printf '%s' "$name" | tr -d '[:space:]')"
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
      exit 2
      ;;
  esac
done

if [ "$stack_up" = "1" ]; then
  docker compose -f docker-compose.yml -f docker-compose.ci.yml up -d --no-build --wait
fi
