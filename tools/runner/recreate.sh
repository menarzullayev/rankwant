#!/usr/bin/env bash
# Recreate ONE containerized CI runner. Never `compose down` the project:
# that would stop the other runner and dump any job it is running.
#
#   bash tools/runner/recreate.sh              # runner (rankwant-ci-runner)
#   bash tools/runner/recreate.sh --second     # runner-2 (compose profile `second`)
#   bash tools/runner/recreate.sh --selftest   # ...and prove it takes a job
#
# Use this when the container must pick up a change to tools/runner/ or is
# broken beyond a restart. A plain `docker restart <container>` keeps the
# registration and is what the watchdog does.
#
# The order matters, and each step fixes something that broke once:
#   1. `stop` + `rm` this service only, so the listener closes its broker
#      session. A killed listener leaves "A session for this runner already
#      exists".
#   2. The old registration is deleted before registering again.
#   3. A fresh registration token (valid about an hour) is minted for `up`.
# The matching work volume survives, so the tool cache is kept.
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/../.."
REPO=menarzullayev/rankwant

service=runner
name=nsn-pc-rankwant-container
container=rankwant-ci-runner
profile=()
selftest=0
for arg in "$@"; do
  case "$arg" in
    --second)
      service=runner-2
      name=nsn-pc-rankwant-container-2
      container=rankwant-ci-runner-2
      profile=(--profile second)
      ;;
    --selftest) selftest=1 ;;
    *) echo "unknown argument: $arg" >&2; exit 2 ;;
  esac
done

COMPOSE=(docker compose -f tools/runner/docker-compose.runner.yml "${profile[@]}")

runner() { gh api "repos/$REPO/actions/runners" --jq ".runners[] | select(.name==\"$name\") | $1"; }

old_id=$(runner .id)
if [ -n "$old_id" ] && [ "$(runner .busy)" = "true" ]; then
  echo "✗ $name (id $old_id) is running a job; recreate it once the job ends" >&2
  exit 1
fi

# Service-only teardown. `down` is forbidden here: it stops every runner
# in this compose project, including the one we did not name.
"${COMPOSE[@]}" stop -t 60 "$service" || true
"${COMPOSE[@]}" rm -f "$service" || true
if [ -n "$old_id" ]; then
  gh api -X DELETE "repos/$REPO/actions/runners/$old_id"
  echo "→ deleted registration $old_id"
fi

RUNNER_TOKEN=$(gh api -X POST "repos/$REPO/actions/runners/registration-token" --jq .token) \
  "${COMPOSE[@]}" up -d --no-deps --build "$service"

for _ in $(seq 1 60); do
  if docker logs "$container" 2>&1 | grep -q "Listening for Jobs"; then
    break
  fi
  sleep 2
done
docker logs "$container" 2>&1 | grep -E "HOST_REPO_ROOT|registering|Listening for Jobs" | tail -3
labels=$(runner '[.labels[].name] | join(",")')
echo "→ $name id=$(runner .id) status=$(runner .status) labels=$labels"
case ",$labels," in
  *,rankwant,*) ;;
  *) echo "✗ registered without the production label rankwant: CI jobs will wait forever" >&2; exit 1 ;;
esac

if [ "$selftest" -eq 1 ]; then
  gh workflow run runner-selftest.yml -R "$REPO" --ref main >/dev/null
  sleep 6
  run=$(gh run list -R "$REPO" --workflow runner-selftest.yml --limit 1 --json databaseId --jq '.[0].databaseId')
  for _ in $(seq 1 48); do
    [ "$(gh api "repos/$REPO/actions/runs/$run" --jq .status)" = "completed" ] && break
    sleep 5
  done
  conclusion=$(gh api "repos/$REPO/actions/runs/$run" --jq '.conclusion // "not finished"')
  echo "→ self-test run $run: $conclusion"
  [ "$conclusion" = "success" ] || exit 1
fi
echo "✓ $name recreated"
