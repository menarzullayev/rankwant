# Containerized CI runner

Runs GitHub Actions on a container attached to Docker Desktop's daemon, so the
second WSL engine can eventually go away.

## Status: production CI runner since 2026-09-17

The runner carries **`rankwant`**, the label every CI job asks for, and
`rankwant-container`, which `tools/check_decisions.py` lets only
`runner-selftest.yml` target. The WSL runner is still registered and online,
with no custom label, as the fallback; see
[Rolling back](#rolling-back-to-the-wsl-runner). Two runners sharing `rankwant`
would race for the same jobs, and on 2026-09-17 a runner under trial did
exactly that.

It became production after a second full CI run, following the fixes below:
the workspace moved to a volume and the watchdog was installed. On `main`
`81b7d2d`, dispatched with `run_all`, every job ran here, one after another,
with no stall:

| Job | Container runner | WSL runner, earlier `main` runs |
| --- | --- | --- |
| Docs and integrity | 32 s | 17–20 s |
| Judge | 59 s (`setup-go` 21 s) | 22 s |
| OpenAPI | 89 s | 16 s |
| Web | 99 s | 74 s |
| API | 156 s | ~125 s |
| Smoke and E2E | 295 s | 123–149 s |
| Whole run | 12.5 min, success | ~8.5 min |

That first run on the volume filled cold caches (Python, pip, npm), which is
most of the gap. The live site answered all 44 probes during the run, all 200,
average 0.45 s.

### First trial (failed)

Measured 2026-09-17: **14/14 self-test jobs succeeded** — 9 on `host`
networking including after a 6-minute idle, 5 on `bridge`. Both network
modes behave the same, so the default is left at Docker's own.

The self-test is too light to prove the runner. On 2026-09-17 the production
label was moved here (the WSL runner lost it) and the full CI was dispatched on
`main` with `run_all`:

| Job | Container runner | WSL runner, same commit |
| --- | --- | --- |
| Docs and integrity | 38 s | 17–20 s |
| Judge | timed out at 3 min; `actions/setup-go` alone took 166 s | 22 s |
| API, Web, OpenAPI, Smoke and E2E | never started, queued for 7+ minutes | 125 s, 74 s, 16 s, 123 s |

Two separate problems:

- **The runner stopped taking jobs after the timed-out job.** It stayed
  `online` with `busy=false`, its log went quiet once that job ended, and it
  acquired none of the four queued jobs. The earlier "deaf runner" report was
  dismissed too early; see the update in the next section.
- **First-time tool setup is slow on the workspace.** The work directory is a
  Windows bind mount, and unpacking the Go toolchain into the tool cache ran
  past the job's 3-minute limit. `npm ci` and `uv sync` write to the same
  mount on every run, so a warm tool cache alone may not be enough.

The live site answered every probe during the trial (65 samples over 18
minutes, all 200, slowest 1.35 s), so sharing the engine was not the problem.

### Causes and fixes

**Slow workspace: 9p.** `/work` was `C:/Users/nsn/ci-work`, and inside the
container that is a 9p mount (`/proc/mounts`: `C:\134 /work 9p ...
aname=drvfs;path=C:\`). In the trial, setup-go downloaded Go in 8 s,
unpacked it in 32 s, and was still copying it into the tool cache when it
was cancelled 124 s later. The same archive (14,542 files), measured in one
container on each filesystem:

| Filesystem | Extract | Copy | Delete |
| --- | --- | --- | --- |
| Container overlay | 1 s | 2 s | 0 s |
| Docker named volume | 2 s | under 1 s | 0 s |
| `C:\` bind mount (9p) | 168 s | 70 s | 23 s |

Fix: `/work` is now the named volume `rankwant-ci-work`. Bind mounts in the
workflows still work, because the daemon mounts a volume's subdirectory by
its own path. This was measured: a file written into a volume was read back
through `-v /var/lib/docker/volumes/<volume>/_data/<dir>:/e2e`. The entrypoint
asks the daemon for that path and exports `HOST_REPO_ROOT` from it.

**Deaf runner: actions/runner#4444.** When a job ends, the listener cancels
its own long poll so it can poll again with the new status (that is the
`SocketException (125)` line, actions/runner#4644), and sometimes it never
polls again. Our log shows the same signature as the issue: the last line is
`Get messages has been cancelled using local token source. Continue to get
messages with new status.`, then nothing. The issue was closed without a fix,
and both runners here run 2.337.0, the WSL one included. A broker reconnect
wakes the runner: at 13:41:24 a label change sent `ForceTokenRefreshMessage`,
the listener recreated its broker connection, and later self-tests were picked
up on time. A restart does the same.

The runner's log cannot detect this, because a healthy idle listener is just
as quiet (two lines in 69 minutes). The queue can. Fix:
`tools/runner_watchdog.py` restarts a runner that two checks in a row find
online and idle while a job it could run has been queued for 3+ minutes. See
[Watchdog](#watchdog).

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

**Update (2026-09-17, full CI trial):** the runner did go deaf again, after a
job that hit its timeout, with no re-registration or container recreation in
between. `SocketException (125)` once per job is still normal. It does not
explain the deafness away: that is a real failure, actions/runner#4444 (see
[Causes and fixes](#causes-and-fixes)).

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
can leave a stale session. If you must, for example to pick up a change to
this directory, stop it cleanly first so the listener closes its session,
then delete the registration and start with a fresh token:

```bash
docker compose -f tools/runner/docker-compose.runner.yml down
gh api -X DELETE repos/menarzullayev/rankwant/actions/runners/<id>
TOKEN=$(gh api -X POST repos/menarzullayev/rankwant/actions/runners/registration-token --jq .token)
RUNNER_TOKEN="$TOKEN" docker compose -f tools/runner/docker-compose.runner.yml up -d --build
```

`down` keeps the `rankwant-ci-work` volume, so the tool cache survives.

## Watchdog

`tools/runner_watchdog.py` covers both runners on this machine: the container
(`docker restart rankwant-ci-runner`) and the WSL one (`systemctl restart` of
its service). It reads the runners and the queued jobs through `gh`, which is
already signed in here, so it needs no token of its own.

- A runner counts as stuck when it is `online`, not busy, and a job whose
  labels it carries has been queued for at least 180 s.
- The first check that sees this only records it. A restart needs a second
  check at least 90 s later: between two jobs a healthy runner is briefly idle
  with a long-queued job, and a restart then would break the pickup.
- After a restart, that runner is left alone for 10 minutes.
- Exit 2 means GitHub could not be read. That is never taken as healthy.

The scheduled task runs an installed copy from `origin/main`, not the main
checkout, which can be on any branch:

```bash
mkdir -p /c/Users/nsn/ci-runner
for f in runner_watchdog.py _console.py; do
  git show origin/main:tools/$f > /c/Users/nsn/ci-runner/$f
done
```

```powershell
$action = New-ScheduledTaskAction -Execute 'C:\WINDOWS\System32\conhost.exe' `
  -Argument '--headless "C:\Program Files\Git\bin\bash.exe" -lc "python /c/Users/nsn/ci-runner/runner_watchdog.py >> /c/Users/nsn/ci-runner/watchdog.log 2>&1"'
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 2)
$settings = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 1)
Register-ScheduledTask -TaskName 'RankWant CI Runner Watchdog' -Action $action -Trigger $trigger -Settings $settings
```

The log gets a line only when a runner is suspected, restarted, or cannot be
read. A dry run against GitHub restarts nothing and records nothing:
`python tools/runner_watchdog.py --dry-run`. Tests: `python
tools/check_negative.py runner_watchdog`.

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

If this runner was given the production label, give it back:

```bash
gh api -X PUT repos/menarzullayev/rankwant/actions/runners/<container-id>/labels -f 'labels[]=rankwant-container'
gh api -X POST repos/menarzullayev/rankwant/actions/runners/<wsl-id>/labels -f 'labels[]=rankwant'
```

Jobs already handed to a deaf runner do not move after the labels change;
they sat queued until the run was cancelled. Cancel it and rerun what did not
pass, which puts those jobs on the WSL runner within seconds:

```bash
gh run cancel <run-id>
gh run rerun <run-id> --failed
```

Leave `main` green: the deploy gate reads the latest `CI` run of the commit,
and a dispatched run counts.

To remove this runner entirely:

```bash
docker rm -f rankwant-ci-runner
gh api -X DELETE repos/menarzullayev/rankwant/actions/runners/<id>
```

The WSL runner and `RankWant-Runner-Keepalive` are deliberately left running
during the trial, so there is nothing else to restore.
