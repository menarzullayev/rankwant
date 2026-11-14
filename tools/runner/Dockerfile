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
FROM ghcr.io/actions/actions-runner:latest AS runtime

USER root

RUN apt-get update \
 && apt-get upgrade -y \
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
      docker-ce-cli \
      docker-buildx-plugin \
      docker-compose-plugin \
      python3-pip \
      python3-venv \
 && rm -f /usr/local/lib/docker/cli-plugins/docker-buildx \
 && rm -rf /var/lib/apt/lists/*
# `docker-ce-cli` and `docker-buildx-plugin` replace the client and the buildx the
# base image unpacks from static archives, which trail Docker's own repository
# (measured 2026-11-14: buildx 0.38.1 with a critical advisory in its x/net, 0.39.0
# in the repository). The base's buildx sits in /usr/local/lib and would win over
# the package's in /usr/libexec, so it is removed.

# What the base image carries and this runner never starts (Docker Scout counted
# 5 critical and 77 high advisories in the image on 2026-11-14, most of them here):
#
#   * a whole Docker engine — dockerd, containerd, runc and their helpers. The
#     runner drives the HOST daemon through the mounted socket and needs the
#     client only (`docker`, buildx, compose).
#   * npm, npx and corepack beside each bundled Node. The runner executes an
#     action with `externals/node*/bin/node <file>`; nothing installs packages
#     with these copies (a job that needs npm gets its own Node from setup-node).
#   * `add-apt-repository` and the Python libraries only it pulls in (PyJWT,
#     cryptography, httplib2, oauthlib, launchpadlib).
RUN rm -f /usr/bin/dockerd /usr/bin/containerd /usr/bin/containerd-shim-runc-v2 \
      /usr/bin/runc /usr/bin/ctr /usr/bin/docker-proxy /usr/bin/docker-init \
 && for node in /home/runner/externals/node*; do \
      rm -rf "$node/lib/node_modules" "$node/bin/npm" "$node/bin/npx" "$node/bin/corepack"; \
      test -x "$node/bin/node" || { echo "no node binary left in $node" >&2; exit 1; }; \
    done \
 && apt-get purge -y software-properties-common python3-software-properties \
      python3-launchpadlib python3-lazr.restfulclient \
      python3-oauthlib python3-cryptography python3-httplib2 python3-jwt \
 && docker --version && docker compose version && docker buildx version

# The base image ships no ENTRYPOINT (Cmd is `/bin/bash`), so without this
# the container starts a shell with no TTY and exits 0 with empty logs.
COPY entrypoint.sh /home/runner/entrypoint.sh
RUN chmod +x /home/runner/entrypoint.sh

# Flatten. A file removed in a later layer is still in the earlier one: it stays
# on disk in the image, and a scanner that reads every layer keeps counting it
# (measured with Docker Scout on another image of this host, 2026-11-14). One
# layer holds only what is left. The settings below restate the base image's own
# (`docker image inspect`), which `FROM scratch` does not inherit.
FROM scratch
COPY --from=runtime / /
ENV PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin \
    DOTNET_RUNNING_IN_CONTAINER=true \
    DEBIAN_FRONTEND=noninteractive \
    RUNNER_MANUALLY_TRAP_SIG=1 \
    ACTIONS_RUNNER_PRINT_LOG_TO_STDOUT=1 \
    ImageOS=ubuntu24
WORKDIR /home/runner

# The runner drives the daemon through the mounted socket and writes its
# workspace to a bind mount, so it stays root inside its own container.
USER root
ENTRYPOINT ["/home/runner/entrypoint.sh"]

# Registration is supplied at run time (see docker-compose.runner.yml);
# nothing secret is baked into the image.
