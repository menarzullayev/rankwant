# syntax=docker/dockerfile:1
#
# Containerized GitHub Actions runner for the single-engine topology.
#
# Why this exists: the runner used to live in its own WSL distribution with a
# separate Docker daemon. The 2026-09-17 decision collapses that into one
# engine, so the runner becomes a container on the same Docker Desktop daemon
# that serves the live site.
#
# Two gaps in the base image, both measured on 2026-09-17:
#
#   * `docker compose` is missing. The base ships the docker CLI but no
#     compose plugin, and every CI job drives `docker compose`.
#   * the socket is not openable by the `runner` user. Docker Desktop exposes
#     /var/run/docker.sock as `srw-rw---- root root`, while the image's runner
#     is uid/gid 1001 (its `docker` group is gid 123 and does not match).
#     The container therefore runs as root. That grants nothing beyond what
#     the socket already gives — anything that can drive this daemon can
#     mount the host filesystem — so it is a permission fix, not a new
#     privilege. See docs: https://docs.docker.com/engine/security/
FROM ghcr.io/actions/actions-runner:latest

USER root

RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates curl gnupg \
 && install -m 0755 -d /etc/apt/keyrings \
 && curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
      -o /etc/apt/keyrings/docker.asc \
 && chmod a+r /etc/apt/keyrings/docker.asc \
 && . /etc/os-release \
 && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu ${VERSION_CODENAME} stable" \
      > /etc/apt/sources.list.d/docker.list \
 && apt-get update \
 && apt-get install -y --no-install-recommends \
      docker-compose-plugin \
      python3-pip \
      python3-venv \
 && rm -rf /var/lib/apt/lists/*

# The runner drives the daemon through the mounted socket and writes its
# workspace to a bind mount, so it stays root inside its own container.
USER root

# The base image ships no ENTRYPOINT (Cmd is `/bin/bash`), so without this
# the container starts a shell with no TTY and exits 0 with empty logs.
COPY entrypoint.sh /home/runner/entrypoint.sh
RUN chmod +x /home/runner/entrypoint.sh
ENTRYPOINT ["/home/runner/entrypoint.sh"]

# Registration is supplied at run time (see docker-compose.runner.yml);
# nothing secret is baked into the image.
