#!/usr/bin/env bash
# Start the stack containers that Docker itself tried and FAILED to start.
#
# Measured 2026-11-10: Docker Desktop stopped (~07:55 UTC, the WSL
# `docker-desktop` distro went down). After it came back every container
# was running again except the judge:
#   failed to create task for container: ... unable to apply cgroup
#   configuration: failed to write 872: write /sys/fs/cgroup/docker/<id>/
#   cgroup.procs: device or resource busy
# It stayed `Exited (128)`: `restart: unless-stopped` does not retry a
# container whose task could not even be created. The site answered 200 and
# the monitor said OK, so nothing showed that submissions were not being
# judged. One `docker start` brought it up with all four preflights passing.
#
# Only a container that is not running AND has a non-empty `.State.Error`
# is touched — Docker writes that field when a start fails and clears it on
# the next successful start. A container stopped by hand (`docker stop`, for
# example `worker` and `beat` during a bake-off, see CLAUDE.md) has an empty
# Error and is left alone.
#
# Usage:
#   bash tools/revive_containers.sh [project] [--dry-run]
# Prints one line per container it acted on (nothing when there is nothing
# to do). Exit: 0 — nothing to do, or every container came up;
#               1 — a container still would not start;
#               2 — Docker is not answering.

set -uo pipefail

PROJECT="${1:-rankwant}"
DRY_RUN=0
[ "${2:-}" = "--dry-run" ] && DRY_RUN=1
# Seconds to wait before checking that the container stayed up. The judge
# runs its preflights in ~50 ms and exits at once if one fails.
WAIT="${RANKWANT_REVIVE_WAIT:-5}"

docker info >/dev/null 2>&1 || { echo "Docker engine javob bermayapti"; exit 2; }

failed=0
names="$(docker ps -a --filter "label=com.docker.compose.project=$PROJECT" \
  --filter status=exited --filter status=created --format '{{.Names}}' 2>/dev/null)"

for name in $names; do
  state="$(docker inspect -f '{{.State.ExitCode}}{{"\t"}}{{.State.Error}}' "$name" 2>/dev/null)" || continue
  code="${state%%$'\t'*}"
  err="${state#*$'\t'}"
  # Stopped by hand, or never failed: not ours to start.
  [ -n "$err" ] || continue
  err="$(printf '%s' "$err" | tr '\n' ' ' | cut -c1-160)"
  if [ "$DRY_RUN" -eq 1 ]; then
    echo "qayta ko'tarilardi: $name (exit $code) — $err"
    continue
  fi
  docker start "$name" >/dev/null 2>&1
  sleep "$WAIT"
  after="$(docker inspect -f '{{.State.Running}}{{"\t"}}{{.State.Restarting}}{{"\t"}}{{.State.ExitCode}}{{"\t"}}{{.State.Error}}' "$name" 2>/dev/null)"
  IFS=$'\t' read -r running restarting code2 err2 <<< "$after"
  if [ "$running" = "true" ] && [ "$restarting" = "false" ]; then
    echo "qayta ko'tarildi: $name (exit $code edi) — $err"
  else
    failed=1
    echo "ko'tarilmadi: $name (exit ${code2:-?}) — ${err2:-$err}"
  fi
done

exit "$failed"
