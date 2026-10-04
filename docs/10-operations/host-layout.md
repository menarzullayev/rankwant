# RankWant — host layout

**Status:** living document. `docs/10-operations/` is `draft`, so this file needs no ADR to edit.
**Measured:** 2026-10-04, on the Windows side of the dual-boot machine.

The repository is not the whole system. The live stack also depends on
scheduled tasks, Docker state, a tunnel config, backups and agent folders
that live outside the checkout. This file is the map: one row per place,
what owns it, and whether it may go to GitHub.

Rule for adding a row: something belongs here when the **running system
points at it** (a task, a container, a compose file, the tunnel) or when it
is **needed to restore** (backups, secrets). A folder that merely has
"rankwant" in its name is not enough.

## Three layers

| Layer | What | Where |
| --- | --- | --- |
| In GitHub | code, docs, host scripts, task definitions (below) | this repo |
| Local only, one place | backups, archives, secrets, logs | canonical folders on `D:` |
| Cannot move | Docker volumes, `~/.cloudflared`, agent homes, `AppData` | where the tool puts them |

`D:` is the NTFS volume shared with Ubuntu (`/media/nsn/Shared`). `C:` is
Windows-only, so nothing that must survive an OS switch lives there.

## Code

| Path | Role |
| --- | --- |
| `D:\Linux\Web_Projects\rankwant` | canonical checkout; the live stack's `.env.public` and `.handoff/` logs are here |
| `D:\Windows\project\cp\rankwant` | junction to the canonical checkout, not a second clone |
| `D:\Windows\project\wt\deploy` | deploy worktree; `RankWant Auto Deploy` builds from it |
| `D:\Linux\Web_Projects\rankwant-deploy` | deploy worktree used when `RANKWANT_DEPLOY_DIR` is not set |
| `D:\Windows\project\wt\<tool>\` | per-agent worktrees ([parallel-agents.md](parallel-agents.md)) |
| `D:\Windows\project\wt\.agent\` | agent control plane: manifests, status, locks |

## Scheduled tasks

All five run under Task Scheduler as the logged-in user. They exist only on
the host; the commands that create them are in the linked documents.

| Task | Runs | Definition |
| --- | --- | --- |
| `RankWant Auto Deploy` | `tools/auto_deploy.sh` from the deploy worktree, every minute | [deploy-runbook.md](deploy-runbook.md) |
| `RankWant Monthly Backup` | `tools/backup.sh`, every 30 days at 13:00 | [README.md](README.md) § backup |
| `RankWant Tunnel Monitor` | `tools/monitor.ps1`, every 5 minutes | [README.md](README.md) |
| `RankWant CI Runner Watchdog` | `runner_watchdog.py`, every 2 minutes | [`tools/runner/README.md`](../../tools/runner/README.md) |
| `RankWant CI Daily Report` | `runner_report.py`, daily at 08:00 | [`tools/runner/README.md`](../../tools/runner/README.md) |

The two CI tasks run **copies** in `C:\Users\nsn\ci-runner\`
(`runner_watchdog.py`, `runner_report.py`, `_console.py`). On 2026-10-04 the
copies were byte-identical to `tools/` in this repo. They are copies, so a
change in `tools/` does not reach the task until the files are copied again.

Both `Auto Deploy` and `Monthly Backup` pass
`RANKWANT_BACKUP_DIR=/d/Windows/backups/rankwant`. Without it `tools/backup.sh`
falls back to `$HOME/backups/rankwant`, which on Windows is on `C:`.

## Host state

| Path | Written by |
| --- | --- |
| `D:\Windows\backups\rankwant\` | `tools/backup.sh` — full backups (`pg-*`, `minio-*`, 95 days) and pre-deploy dumps (`pg-deploy-*`, 7 days) |
| `C:\Users\nsn\.rankwant-auto-deploy-state` | `tools/auto_deploy.sh` |
| `C:\Users\nsn\AppData\Local\RankWant\runner-watchdog.json` | `runner_watchdog.py` |
| `C:\Users\nsn\ci-runner\*.log`, `daily-report.md` | the two CI tasks |
| `C:\Users\nsn\ci-runner-diag\`, `ci-runner-diag-2\` | bind-mounted into the runner containers |
| `D:\Linux\Web_Projects\rankwant\.handoff\` | deploy, tunnel and handoff logs (gitignored) |

Backups contain user data. The repository is public: a dump, `.env.public`
or a tunnel credential must never be copied into the checkout.

## Docker

Compose project `rankwant` (stack) and `rankwant-runner` (CI runners).

| Kind | Names |
| --- | --- |
| Volumes | `rankwant_pgdata`, `rankwant_miniodata`, `rankwant_api_cache`, `rankwant-ci-work`, `rankwant-ci-work-2`, `rankwant-ci-cache` |
| Networks | `rankwant_default`, `rankwant_judge-net`, `rankwant-runner_default` |
| Outside compose | `rankwant-postgres-mcp` (database access for agents) |

`rankwant_pgdata` and `rankwant_miniodata` are the production data. They
live inside the Docker Desktop VHDX and move only through backup and restore.

## Tunnel

`cloudflared` runs as a user process started by `tools/monitor.ps1`, with
`C:\Users\nsn\.cloudflared\config.yml`. That file is **shared with other
projects on this machine**: it must stay where it is, and editing it affects
hosts that are not RankWant. The RankWant ingress rules send `rankwant.uz`
and `www.rankwant.uz` to `127.0.0.1:8300` (web), `:8301` (API) and `:8302`
(realtime).

## Agent tooling

Not needed to run the stack, but it refers to the checkout by path, so a
move of the repository breaks it.

| Path | What |
| --- | --- |
| `C:\Users\nsn\.mcp-registry\` | MCP servers for every agent; `graphify` points at `graphify-out/graph.json` in the checkout |
| `C:\Users\nsn\.claude\projects\`, `.cursor\projects\`, `.workbuddy-ai\projects\` | per-agent session history keyed by checkout path |
| `C:\Users\nsn\.claude\skills\rankwant-incident-triage\` | incident skill |

## Archives

`D:\Windows\archive\` holds retired clones, exported stashes and old
worktrees (see `D:\Windows\DECISION-DUALBOOT-*.md`). Nothing running points
at it. `rankwant-quarantine-20261004\` inside it is the staging folder for
the 2026-10-04 cleanup: items wait there before the owner deletes them.

## Known drift

Measured 2026-10-04; fix the document when the drift is fixed.

- Other documents still name `C:\Users\nsn\project\...`. That junction was
  removed on 2026-09-23; the tree is at `D:\Windows\project\`.
- `docker compose ls` lists config files under `C:\Users\nsn\project\` for
  both projects. The containers were created from those paths and keep the
  label until they are recreated.
