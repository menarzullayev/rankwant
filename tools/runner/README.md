# Containerized CI runner (trial)

Runs GitHub Actions on a container attached to Docker Desktop's daemon, so the
second WSL engine can eventually go away.

## Status: trial, stable for light jobs

The runner carries the **`rankwant-container` label**, and
`tools/check_decisions.py` permits only `runner-selftest.yml` to target it.
Production CI stays on the WSL runner. Two runners sharing the `rankwant`
label would race for the same jobs, and on 2026-09-17 one did exactly that.

Measured 2026-09-17: **14/14 self-test jobs succeeded** — 9 on `host`
networking including after a 6-minute idle, 5 on `bridge`. Both network
modes behave the same, so the default is left at Docker's own.

## A false alarm worth recording

An earlier round concluded the runner "went deaf" — it read `online` while
queued runs sat untouched — and blamed the broker connection:

```
[BrokerServer] System.Net.Sockets.SocketException (125): Operation canceled
[BrokerMessageListener] Get messages has been cancelled using local token source.
```

That diagnosis was wrong, and the log line is why. Those errors appear
**exactly when a job completes**, one per job, and every one of those jobs
succeeded. Cancelling the long-poll on completion is how the runner works;
`SocketException (125)` is that cancellation surfacing, not a fault.

What actually broke the earlier attempt was churn in the registration, not
the container model: the container was recreated and re-registered several
times, which left a stale broker session ("A session for this runner already
exists") and, at one point, a runner carrying a stale label — jobs requiring
`rankwant` could not match `rankwant-container`. Registering once and
leaving it alone is stable.

**Lesson:** before blaming a component, check whether the symptom's timing
lines up with its supposed cause. One error per completed job pointed at the
job lifecycle, not at the network.

## Running it

```bash
# Registration token, valid about an hour, only needed on first start or
# after the container is recreated (a plain restart keeps the registration).
TOKEN=$(gh api -X POST repos/menarzullayev/rankwant/actions/runners/registration-token --jq .token)
RUNNER_TOKEN="$TOKEN" docker compose -f tools/runner/docker-compose.runner.yml up -d
```

Then trigger `Runner self-test` — it is the only workflow allowed on this
label.

**Do not recreate the container casually.** Each recreation re-registers and
can leave a stale session; delete the runner registration first if you must:

```bash
gh api -X DELETE repos/menarzullayev/rankwant/actions/runners/<id>
```

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
