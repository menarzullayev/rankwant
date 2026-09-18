#!/usr/bin/env bash
# Run Playwright from a GHCR mirror of the official image.
#
# Hosted VMs pull `mcr.microsoft.com/playwright` on every smoke (~25–30 s).
# After the first successful push, the same digest lives at
# `ghcr.io/<repo>/playwright:<tag>` and the runner pulls from GitHub.
# Do NOT use `type=gha` for this — GHCR is the cache.
#
# Usage: bash tools/ci_playwright.sh -- [docker run args after the image]
# Env: GITHUB_TOKEN, GITHUB_ACTOR, GITHUB_REPOSITORY, CI_PUSH_IMAGE_CACHE
#      COMPOSE_PROJECT_NAME (for --network), HOST_REPO_ROOT
set -euo pipefail

src="${PLAYWRIGHT_SOURCE:-mcr.microsoft.com/playwright:v1.63.0-noble}"
tag="${src##*:}"
repo_lc="$(printf '%s' "${GITHUB_REPOSITORY:-menarzullayev/rankwant}" | tr '[:upper:]' '[:lower:]')"
mirror="ghcr.io/${repo_lc}/playwright:${tag}"
push="${CI_PUSH_IMAGE_CACHE:-0}"
image=""

if [ -n "${GITHUB_TOKEN:-}" ]; then
  printf '%s' "$GITHUB_TOKEN" | docker login ghcr.io -u "${GITHUB_ACTOR:-github}" --password-stdin
fi

if docker pull "$mirror"; then
  image="$mirror"
else
  echo "--> GHCR playwright miss — pull $src"
  docker pull "$src"
  docker tag "$src" "$mirror"
  image="$src"
  if [ "$push" = "1" ] && [ -n "${GITHUB_TOKEN:-}" ]; then
    docker push "$mirror" || echo "--> playwright mirror push failed (next run retries)"
  fi
fi

if [ "${1:-}" = "--" ]; then
  shift
fi

exec docker run --rm --user "$(id -u):$(id -g)" \
  --network "${COMPOSE_PROJECT_NAME}_default" \
  -v "${HOST_REPO_ROOT:-$PWD}/tests/e2e:/e2e" -w /e2e \
  -e E2E_BASE_URL="${E2E_BASE_URL:-http://web:3000}" \
  -e E2E_API_BASE="${E2E_API_BASE:-http://api:8000/api/v1}" \
  -e CI=1 \
  "$image" \
  "$@"
