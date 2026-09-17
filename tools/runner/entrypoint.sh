#!/bin/sh
# Entrypoint for the containerized RankWant CI runner.
#
# Registers on first start, then runs. The registration is stored in the
# container's own filesystem, so a plain restart (including after a reboot,
# which is what `restart: unless-stopped` gives us) does NOT need a new
# token. Recreating the container does — see README.md.
set -eu

# The runner refuses to configure as root unless this is set. We run as root
# because Docker Desktop exposes /var/run/docker.sock as `root root` mode 660
# while the image's own `runner` user is uid/gid 1001 — it cannot open the
# socket. Driving this daemon is already root-equivalent, so this is a
# permission fix, not an added privilege.
export RUNNER_ALLOW_RUNASROOT=1

: "${RUNNER_REPO:?RUNNER_REPO is required}"
: "${RUNNER_NAME:=nsn-pc-rankwant-container}"
: "${RUNNER_LABELS:=self-hosted,Linux,X64,rankwant-test}"
: "${RUNNER_WORKDIR:=/work}"

cd /home/runner

if [ ! -f .runner ]; then
  : "${RUNNER_TOKEN:?RUNNER_TOKEN is required for the first start}"
  echo "==> registering as '$RUNNER_NAME' with labels '$RUNNER_LABELS'"
  ./config.sh --unattended --replace \
    --url "$RUNNER_REPO" \
    --token "$RUNNER_TOKEN" \
    --name "$RUNNER_NAME" \
    --labels "$RUNNER_LABELS" \
    --work "$RUNNER_WORKDIR"
else
  echo "==> already registered; starting without re-registering"
fi

exec ./run.sh
