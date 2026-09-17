# Containerized CI runner

Runs GitHub Actions on a container attached to Docker Desktop's daemon. It is
the only CI runner: the WSL runner it replaced was deregistered and its
`Ubuntu-24.04` distro removed on 2026-09-17, by owner decision.

## Status: production CI runner since 2026-09-17

The runner carries **`rankwant`**, the label every CI job asks for, and
`rankwant-container`, which `tools/check_decisions.py` lets only
`runner-selftest.yml` target. There is no fallback runner: when this one
breaks, see [Recovering the runner](#recovering-the-runner). Two runners
sharing `rankwant` would race for the same jobs, and on 2026-09-17 a runner
under trial did exactly that.

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
can leave a stale session. When it has to be done, for example to pick up a
change to this directory, use the script. It stops the listener cleanly so it
closes its session, deletes the old registration, registers with a fresh
token, and refuses to run while a job is in progress or to finish without the
`rankwant` label:

```bash
bash tools/runner/recreate.sh --selftest
```

`down` keeps the `rankwant-ci-work` volume, so the tool cache survives.

## Watchdog

`tools/runner_watchdog.py` restarts the runner (`docker restart
rankwant-ci-runner`) when it stops taking jobs. It reads the runners and the
queued jobs through `gh`, which is already signed in here, so it needs no token
of its own.

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
for f in runner_watchdog.py runner_report.py _console.py; do
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

## Daily report

Neither the runner nor the watchdog tells anyone when something goes wrong.
`tools/runner_report.py` writes `C:\Users\nsn\ci-runner\daily-report.md` every
morning: the runs of the last 24 hours (failed ones with the runner they failed
on), the runners, watchdog events, the site and free disk. Anything that needs
attention is listed at the top. Nothing leaves the machine.

```powershell
$action = New-ScheduledTaskAction -Execute 'C:\WINDOWS\System32\conhost.exe' `
  -Argument '--headless "C:\Program Files\Git\bin\bash.exe" -lc "python /c/Users/nsn/ci-runner/runner_report.py >> /c/Users/nsn/ci-runner/report.log 2>&1"'
$trigger = New-ScheduledTaskTrigger -Daily -At 08:00
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Minutes 10)
Register-ScheduledTask -TaskName 'RankWant CI Daily Report' -Action $action -Trigger $trigger -Settings $settings
```

Its HTTP checks send their own User-Agent: Cloudflare answers Python's default
one with 403, which would report a healthy site as down (measured 2026-09-17).

A file waits for someone to open it, so when the report lists anything under
attention it also shows a Windows notification with the count, the first two
items and the path of the report (owner decision 2026-09-17; Telegram and e-mail
were declined, so nothing leaves the machine). Each notification replaces the
previous one instead of stacking, and it can only appear while the owner is
logged in — which is also the only time the task runs. `--notify off` skips it,
`--notify print` prints the toast XML instead, and the report is written either
way. If the notification cannot be shown, the script says so in `report.log` and
exits 3. Tests: `python tools/check_negative.py runner_report`.

## After a reboot

Owner decision: the recovery chain is measured at the next natural reboot.
Once the machine is back, one command checks each link that must return on
its own. These are Docker Desktop, the eight stack containers (api, postgres
and redis healthy), the runner container, origin and the public site through
the tunnel, the runner online with `rankwant`, and the watchdog, daily report,
backup and tunnel monitor tasks, with the watchdog run since boot:

```bash
python tools/check_after_reboot.py
```

Exit 0 means every link is back, 1 lists what is not, 2 means the facts could
not be collected. Tests: `python tools/check_negative.py after_reboot`.

## When an image pull keeps failing

`docker pull` from mcr.microsoft.com breaks mid-layer on this network and never
resumes (five attempts on 2026-09-17 for the Playwright image E2E needs).
`tools/fetch_image.py` downloads the same blobs with Range resume, checks each
against its digest and loads the result:

```bash
python tools/fetch_image.py mcr.microsoft.com/playwright:v1.63.0-noble --load
```

It also handles registries that issue anonymous tokens (Docker Hub). Tested on
`alpine:3.20` and `mcr.microsoft.com/dotnet/runtime-deps:8.0-alpine`.

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

## Recovering the runner

There is no second runner to fall back to, so recovery means bringing this one
back, in order of cost:

1. **Deaf but running.** The watchdog restarts it within about five minutes.
   By hand: `docker restart rankwant-ci-runner`. A restart keeps the
   registration.
2. **Jobs stuck on it.** Jobs already handed to a deaf runner stay queued even
   after it recovers; on 2026-09-17 they only moved once the run was cancelled
   and its failed jobs rerun:

   ```bash
   gh run cancel <run-id>
   gh run rerun <run-id> --failed
   ```

   Leave `main` green: the deploy gate reads the latest `CI` run of a commit,
   and a dispatched run counts.
3. **Broken beyond a restart**, or registered wrongly:
   `bash tools/runner/recreate.sh --selftest`.
4. **Docker Desktop itself is down.** The live site is down too, since both
   share the engine. Recover Docker Desktop first
   (docs/10-operations/deploy-runbook.md §4.2); the runner container comes
   back with it (`restart: unless-stopped`).
