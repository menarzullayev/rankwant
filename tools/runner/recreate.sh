#!/usr/bin/env bash
# Recreate the containerized CI runner, the only CI runner since the WSL one was
# removed on 2026-09-17. Use it when the container must pick up a change to
# tools/runner/ or is broken beyond a restart. A plain `docker restart
# rankwant-ci-runner` keeps the registration and is what the watchdog does.
#
#   bash tools/runner/recreate.sh              # recreate, then wait until it listens
#   bash tools/runner/recreate.sh --selftest   # ...and prove it takes a job
#
# The order matters, and each step fixes something that broke once:
#   1. `down` stops the listener cleanly so it closes its broker session. A
#      killed listener leaves "A session for this runner already exists".
#   2. The old registration is deleted before registering again.
#   3. A fresh registration token (valid about an hour) is minted for `up`.
# The rankwant-ci-work volume survives `down`, so the tool cache is kept.
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/../.."
REPO=menarzullayev/rankwant
NAME=nsn-pc-rankwant-container
COMPOSE=(docker compose -f tools/runner/docker-compose.runner.yml)

selftest=0
for arg in "$@"; do
  case "$arg" in
    --selftest) selftest=1 ;;
    *) echo "unknown argument: $arg" >&2; exit 2 ;;
  esac
done

runner() { gh api "repos/$REPO/actions/runners" --jq ".runners[] | select(.name==\"$NAME\") | $1"; }

old_id=$(runner .id)
if [ -n "$old_id" ] && [ "$(runner .busy)" = "true" ]; then
  echo "✗ $NAME (id $old_id) is running a job; recreate it once the job ends" >&2
  exit 1
fi

"${COMPOSE[@]}" down -t 60
if [ -n "$old_id" ]; then
  gh api -X DELETE "repos/$REPO/actions/runners/$old_id"
  echo "→ deleted registration $old_id"
fi

RUNNER_TOKEN=$(gh api -X POST "repos/$REPO/actions/runners/registration-token" --jq .token) \
  "${COMPOSE[@]}" up -d --build

for _ in $(seq 1 60); do
  if docker logs rankwant-ci-runner 2>&1 | grep -q "Listening for Jobs"; then
    break
  fi
  sleep 2
done
docker logs rankwant-ci-runner 2>&1 | grep -E "HOST_REPO_ROOT|registering|Listening for Jobs" | tail -3
labels=$(runner '[.labels[].name] | join(",")')
echo "→ $NAME id=$(runner .id) status=$(runner .status) labels=$labels"
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
echo "✓ runner recreated"
