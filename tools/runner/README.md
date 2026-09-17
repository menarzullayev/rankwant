# Containerized CI runner (trial)

Runs GitHub Actions on a container attached to Docker Desktop's daemon, so the
second WSL engine can eventually go away.

## Status: trial, not adopted

The runner carries the **`rankwant-container` label**, and
`tools/check_decisions.py` permits only `runner-selftest.yml` to target it.
Production CI stays on the WSL runner. Two runners sharing the `rankwant`
label would race for the same jobs, and on 2026-09-17 one did exactly that.

## Known blocker

The runner accepts individual jobs (self-test and Security pass), then stops
taking new ones: its long-lived connection to the job broker dies and never
recovers, so the runner reads `online` while queued runs sit untouched.

```
[BrokerServer] System.Net.Sockets.SocketException (125): Operation canceled
[BrokerMessageListener] Get messages has been cancelled using local token source.
```

The container currently runs with `network_mode: host` as the candidate fix —
the theory is that Docker Desktop's NAT drops the long-lived connection. Set
`RUNNER_NETWORK_MODE=bridge` to compare. **Not yet proven.**

## Running it

```bash
# Registration token, valid about an hour, only needed on first start or
# after the container is recreated (a plain restart keeps the registration).
TOKEN=$(gh api -X POST repos/menarzullayev/rankwant/actions/runners/registration-token --jq .token)
RUNNER_TOKEN="$TOKEN" docker compose -f tools/runner/docker-compose.runner.yml up -d
```

Then trigger `Runner self-test` — it is the only workflow allowed on this
label.

## What the base image does not provide

Both measured on 2026-09-17:

- **`docker compose`.** The base ships the docker CLI but no compose plugin,
  and every CI job drives `docker compose`.
- **A socket the `runner` user can open.** Docker Desktop exposes
  `/var/run/docker.sock` as `root:root` mode 660 while the image's own
  `runner` is uid/gid 1001. The container runs as root and sets
  `RUNNER_ALLOW_RUNASROOT`. That is a permission fix, not a new privilege:
  anything able to drive this daemon can already mount the host filesystem.
- **An entrypoint.** `Cmd` is `/bin/bash` and there is no `ENTRYPOINT`, so
  without ours the container starts a shell with no TTY and exits 0 with
  empty logs.

## The two assumptions this setup breaks

Neither is visible from a green run on the WSL runner, which is why the
self-test asserts them directly:

- **Service containers publish on the Docker host**, not on the runner
  container's own loopback. Measured: `localhost:<port>` fails,
  `host.docker.internal:<port>` works, the bridge gateway `172.17.0.1` fails.
- **Bind mount sources are resolved by the daemon**, so a container-local
  `$PWD` mounts an empty directory. Measured: a Windows path resolves, a
  Linux-style path does not. `entrypoint.sh` derives `HOST_REPO_ROOT` for the
  workflows; the layout is `<workdir>/<repo>/<repo>` — there is no `_work`
  segment, which is what the first attempt got wrong.

## Rolling back to the WSL runner

```bash
docker rm -f rankwant-ci-runner
gh api -X DELETE repos/menarzullayev/rankwant/actions/runners/<id>
```

The WSL runner and `RankWant-Runner-Keepalive` are deliberately left running
during the trial, so there is nothing to restore.
