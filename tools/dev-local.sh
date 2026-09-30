#!/usr/bin/env bash
# RankWant — daily local dev: Docker backend only + Next.js on the host.
#
#   tools/dev-local.sh
#   tools/dev-local.sh --backend-only
#   tools/dev-local.sh --web-only

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

WEB_PORT="${RANKWANT_DEV_WEB_PORT:-8310}"
ENV_FILE="${RANKWANT_ENV_FILE:-$ROOT/.env.public}"
BACKEND_ONLY=0
WEB_ONLY=0

for arg in "$@"; do
  case "$arg" in
    --backend-only) BACKEND_ONLY=1 ;;
    --web-only) WEB_ONLY=1 ;;
    -h|--help)
      echo "Usage: tools/dev-local.sh [--backend-only|--web-only]"
      exit 0
      ;;
  esac
done

if [[ ! -f "$ENV_FILE" ]]; then
  echo "✗ Env fayl topilmadi: $ENV_FILE" >&2
  exit 1
fi

COMPOSE=(
  docker compose -p rankwant --env-file "$ENV_FILE"
  -f docker-compose.yml
  -f docker-compose.public.yml
  -f docker-compose.dev-local.yml
)

SERVICES=(
  postgres redis minio judge-queue
  migrate api worker beat judge realtime
)

ensure_env_local() {
  local local="$ROOT/apps/web/.env.local"
  local sample="$ROOT/apps/web/env.local.example"
  if [[ ! -f "$local" && -f "$sample" ]]; then
    cp "$sample" "$local"
    echo "✓ apps/web/.env.local yaratildi"
  fi
}

if [[ "$WEB_ONLY" -eq 0 ]]; then
  export RANKWANT_DEV_WEB_PORT="$WEB_PORT"
  echo "→ Docker backend (--no-build)..."
  "${COMPOSE[@]}" stop web 2>/dev/null || true
  if ! "${COMPOSE[@]}" up -d --no-build --wait "${SERVICES[@]}"; then
    echo "⚠ Bir marta build..."
    "${COMPOSE[@]}" up -d --build --wait "${SERVICES[@]}"
  fi
  echo "✓ API http://127.0.0.1:8301/api/v1/health/"
fi

[[ "$BACKEND_ONLY" -eq 1 ]] && exit 0

ensure_env_local
echo "→ Next.js http://127.0.0.1:${WEB_PORT}/"
cd "$ROOT/apps/web"
export NEXT_PUBLIC_API_BASE="http://127.0.0.1:8301/api/v1"
export API_BASE_INTERNAL="http://127.0.0.1:8301/api/v1"
exec npx next dev -p "$WEB_PORT" -H 127.0.0.1
