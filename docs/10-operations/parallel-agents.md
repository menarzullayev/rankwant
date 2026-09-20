# Agent Operating Procedure (AOP)

This PC runs **3 Cursor + 2 WorkBuddy + other** agents against **one git
repo** and **one live Docker stack**. The agent count is not the problem.
**Shared state** is: the same file, branch, port, build dir, lockfile, DB,
Docker, and Git index.

Model: **isolated workers + a shared coordination layer**, not “five AIs
editing one checkout”. Vendor (Cursor / WorkBuddy / Claude) is secondary.
Every worker obeys the same **Agent Contract**.

Live board (not in git): `C:/Users/nsn/project/wt/.agent/`
Worktrees: `C:/Users/nsn/project/wt/<cursor|workbuddy|claude>/<topic>`
Deploy tree: `C:/Users/nsn/project/wt/deploy`

## Contract (10 rules)

1. **One agent = one task.**
2. **One task = one owner.** Others do not implement it in parallel.
3. **Each coding agent = its own Git worktree** under `wt/<tool>/`.
4. **No parallel writes to the same path.** First writer takes `.agent/locks/`; others yield.
5. **Ports are pre-allocated.** Never grab `:3000`, `:8000`, `:8300`, `:8301`.
6. **Do not spawn a second RankWant stack.** Live Docker project is `rankwant`.
7. **Heavy jobs: max 2. Package-manager write: 1. Live migration: 1.**
8. **Global destructive commands are forbidden** unless the owner names the
   exact PID / container / worktree.
9. **Every session writes status + a handoff** under `.agent/`.
10. **Merge only after tests; deploy only via `tools/deploy.sh`. **

Ownership each agent must have (or namespace):

```text
Agent → Task → Git branch/worktree → Workspace/files → Ports → Runtime
```

## Slots (identity only)

Slots are **not roles**. Any slot may take backend, frontend, infra, research,
QA, or docs. The owner assigns whatever is free. Isolation is the **task
card** (`owned_paths`) plus `.agent/locks/` — HITL 2026-09-20 `task-lock`.

| Slot | Tool | HTTP | API | unused DB bind | CPU | RAM |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| C1 | Cursor | 3101 | 8101 | 5511 | 3 | 4 GB |
| C2 | Cursor | 3102 | 8102 | 5512 | 3 | 4 GB |
| C3 | Cursor | 3103 | 8103 | 5513 | 2 | 3 GB |
| W1 | WorkBuddy | 3201 | 8201 | 5611 | 2 | 2 GB |
| W2 | WorkBuddy | 3202 | 8202 | 5612 | 2 | 2 GB |
| X6 | other | 3301 | 8302 | 5711 | 2 | 2 GB |
| X7 | other | 3302 | 8303 | 5712 | 2 | 2 GB |

**Reserved (live, never bind):** `127.0.0.1:8300` web, `:8301` api, `:5432`
Postgres, `:6379` Redis, `:9000`/`:9001` MinIO. `:3000`/`:8000` are the
non-public compose ports — do not `up` that file set on this PC.

DB columns above are **allocated so nobody collides if** a sidecar is ever
needed. RankWant agents **do not** start `cursor1-postgres`. Production data
lives in the live volume; a second Postgres is a wipe/split-brain risk and
fills the Docker VHDX (C: has already hit <11 GB free).

Flexible assignment does **not** drop isolation. It drops *role walls*. Two
agents may both work in `apps/web` only if their globs do not overlap. A
forgotten lock goes stale after 4 hours. Width is **no-star-star** (HITL
2026-09-20): `**` / repo-root / one-segment directory globs are illegal.
Context stays task-scoped: do not ingest the whole repo because this slot
“might do backend later”.

## This machine (measured 2026-09-20)

| | |
| --- | --- |
| CPU | i7-13700F, 16 cores / 24 threads |
| RAM | 31.8 GB |
| Disk | C: ~300 GB (Docker VHDX lives here) |

Soft budget — not cgroups, a **stop line**:

| Consumer | CPU | RAM |
| --- | ---: | ---: |
| C1 | 3 | 4 GB |
| C2 | 3 | 4 GB |
| C3 | 2 | 3 GB |
| W1 | 2 | 2 GB |
| W2 | 2 | 2 GB |
| OS + IDE + browsers + live Docker + 2 CI runners | rest | **≥16 GB reserve** |

Thresholds: RAM > 85% → do not start another agent; CPU > 90% → no new heavy
job; C: free < 15% (~45 GB) → no `npm ci` / Docker build, prune **your**
trees first.

### Concurrency levels

| Level | Work | Cap |
| --- | --- | --- |
| 1 Light | read, plan, review, docs, HITL text | all slots |
| 2 Medium | normal coding, targeted tests | 3–5 |
| 3 Heavy | full build, Docker rebuild, large pytest, live migrate | **1–2** |

```text
MAX_HEAVY_TASKS = 2
MAX_BUILD_TASKS = 2
MAX_DB_MIGRATION = 1   # live: only tools/deploy.sh
MAX_PACKAGE_MANAGER_WRITE = 1
```

What actually burns RAM/CPU: `npm`/`tsc`, Docker, Postgres, Redis, language
servers, tests, browser, local LLM — **the process tree**, not the chat PID.

## Git

```text
1 task → 1 branch → 1 worktree → 1 PR
```

```bash
git -C C:/Users/nsn/project/cp/rankwant fetch origin main
git -C C:/Users/nsn/project/cp/rankwant worktree add -b feat/<topic> \
  C:/Users/nsn/project/wt/<cursor|workbuddy|claude>/<topic> origin/main
```

Push with an explicit ref (`git push -u origin HEAD:feat/<topic>`). A branch
created from `origin/main` must not track `main`.

Keep `C:/Users/nsn/project/cp/rankwant` on **`main` and clean**. Scheduled
tasks read `backup.sh` / `monitor.ps1` from that path.

### Canonical checkout — HITL 2026-09-20 `restore-when-idle`

If porcelain is empty **and** no manifest lists `cp/rankwant` as `workspace`,
the next agent restores it:

```bash
python tools/restore_canonical.py
```

That is `fetch` + `checkout main` + `merge --ff-only origin/main`. Dirty or
claimed trees are skipped. **Never** `git reset --hard` or `git clean -fd`
on this path (`never-touch` / `hook-block-off-main` were rejected).

**Own folder only.** Git author is the same person on every agent — **path is
ownership**. Do not `git pull` / `checkout` / `reset` another agent’s tree.
Do not `git worktree remove` a path under another tool’s folder.

Forbidden on a shared or foreign tree: `git push --force` (of `main`),
`git reset --hard`, `git clean -fd`. Update a PR with
`gh api -X PUT repos/menarzullayev/rankwant/pulls/<n>/update-branch`.

## Task-lock

Before the first edit:

1. Put `owned_paths` on the task card (globs this task will write).
2. For each glob, if `.agent/locks/<name>` exists and is not stale (heartbeat
   < 4 h and `UNTIL` in the future), **stop**. Do not write that glob; pick
   another task or wait.
3. Else write the lock: `OWNER`, `TASK`, `UNTIL`. First writer wins.
4. Stay inside those globs. Need another path? Take a new lock or a new task.
   Do not “just this one file” outside the card.
5. On DONE / BLOCKED: delete **your** lock files.

Filename: path with `/` → `__` (example `apps__web__package.json`). Named
mutexes use the same folder: `PACKAGE_WRITE`, `DEPLOY` (also `deploy.sh`
lock), `HITL`.

Two agents on the same layer (both under `apps/web`) is allowed **if** their
globs do not overlap. Overlap → second agent yields.

### Width — HITL 2026-09-20 `no-star-star`

`owned_paths` is not honor-tight. Predicate: `tools/owned_paths.py`
(`legal_owned_path`). A task may list **several packages**; each glob still
gets its own lock file.

**Forbidden**

- Repo-root locks: `**`, `*`, `.`, `/`
- One-segment directory globs: `apps/**`, `docs/**`, `tools/**`, `apps`

**Required** for a directory glob (`…/**` or `…/*`): **at least two** path
segments (`apps/web/**`, `docs/10-operations/**`,
`apps/web/src/layout/**`).

**Allowed**

- Exact files at any depth, including repo-root hot files (`CONTRIBUTING.md`,
  `CLAUDE.md`)
- Several packages on one card (`apps/api/profiles/titles.py` **and**
  `tools/check_decisions.py`)

`apps/web/**` is legal (two segments) but blocks every other web task —
prefer a tighter glob when the edit is local. `package-one` (one top-level
package per PR) was rejected: a check+API+docs encode would split for no
isolation gain.

## Hot files (always lock, even as the only writer)

Lock under `.agent/locks/` or yield to the older PR.

```text
package.json  package-lock.json
apps/api/requirements*.txt  requirements*.lock
docker-compose*.yml  Dockerfile*  .github/workflows/*
.env  .env.*          # never commit
schema migrations     CLAUDE.md HITL table
tools/check_decisions.py  tools/check_negative.py
apps/web/src/lib/site.ts  apps/web/src/app/robots.ts
```

`check_negative.py` mutates its worktree — no commit during that run.

If two agents need `package.json`: queue (lock → modify → test → release),
or independent branches then rebase. Never two `npm install` on one tree.

## Docker and DB

Live project name: `rankwant`. Compose files: `docker-compose.yml` +
`docker-compose.public.yml` via `tools/deploy.sh` only.

**Forbidden without an explicit owner order naming the target:**

```bash
docker compose down          # unless -p rankwant and you hold deploy.lock
docker system prune
docker volume prune
killall node / python
pkill -f ...
rm -rf <project>
```

Stop **one** thing: `docker stop <container>`, `kill <PID>`.

Agents do **not** create `agent-cursor-1-network` or `cursor1-db` for
RankWant. Isolation here is worktree + branch + `.agent` locks. Feature
trees do not `docker compose up`. `127.0.0.1:8300` is **production origin**
(Cloudflare Tunnel), not a dev server.

Live migrations: `MAX_DB_MIGRATION = 1`, inside `deploy.sh`. Do not migrate
the production volume from a feature tree. Do not wipe users.

## Control plane

```text
C:/Users/nsn/project/wt/.agent/
  manifests/     # contract YAML per slot
  tasks/         # TASK / OWNER / SCOPE / STATUS
  locks/         # one file per hot path
  status/        # heartbeat; stale after 4 hours
  handoffs/      # written on DONE / BLOCKED
  decisions/     # pointers to ADRs / HITL, not a second CLAUDE.md
```

Agents do not chat with each other. This directory is the bus. WorkBuddy
memory and Cursor rules are not a bus.

### Manifest (write before the first edit)

```yaml
agent: cursor-1
task: AOP-002
workspace: C:/Users/nsn/project/wt/cursor/aop-task-lock
branch: docs/aop-task-lock
owned_paths:
  - docs/10-operations/parallel-agents.md
  - CONTRIBUTING.md
ports:
  http: 3101
  api: 8101
resources:
  cpu: 3
  memory: 4GB
forbidden:
  - production-db-migrate
  - docker compose down
```

### Task card

```text
TASK: <id>
OWNER: <slot>
SCOPE: <globs>
DEPENDENCIES: <or none>
STATUS: QUEUED | READY | IN_PROGRESS | BLOCKED | REVIEW | DONE
```

### Handoff (required when leaving the task)

```text
TASK / STATUS / CHANGES / FILES / TESTS / KNOWN_ISSUES / DECISIONS / NEXT
```

### Lifecycle

```text
QUEUED → ALLOCATE → ISOLATE → IN_PROGRESS → TEST → REVIEW → MERGE → DONE
                ↘ BLOCKED → (dependency READY) → IN_PROGRESS
```

Dependency graph, not a flat list. Example: DB schema → API → web → tests →
deploy. An agent on the web task does not re-implement the API because that
PR is not merged — even if this slot did API last week.

Context: Global rules > subsystem > task > agent preference. Do not ingest
the whole monorepo “to understand the project”.

## Session start

1. Read `.agent/status/*` and `.agent/locks/*` (and `CLAIMS.md` if present).
2. `git worktree list` · `gh pr list --repo menarzullayev/rankwant`.
3. `python tools/restore_canonical.py` (HITL `restore-when-idle`).
4. If RAM > 85% or C: < 15% free: do not allocate a heavy job.
5. Write `manifests/<slot>.yml`, `tasks/<id>.md`, `status/<slot>.md`.
6. Take a worktree under **your** tool folder. Lock `owned_paths` (task-lock).
7. Optional local `next dev -p <HTTP from the table>` — never 3000/8300.

## Session finish

1. Push even if unfinished (`wip/<topic>`). Disk-only commits die with the tree.
2. Handoff file. Clear locks. Status `DONE` or `BLOCKED`.
3. Merge **your** PR when CI is green (squash; `--auto` is disabled).
4. Deploy only with Git Bash `tools/deploy.sh --yes`,
   `RANKWANT_ENV_FILE=C:/Users/nsn/project/cp/rankwant/.env.public`,
   HEAD == `origin/main`, CI + Security green. Hold `rankwant-deploy.lock`.
5. Remove **your** worktree after merge (stop processes with that cwd first).

### Stale worktrees — HITL 2026-09-20 `stale-reap`

There is no janitor slot. An agent **may** remove a worktree under **its own**
`wt/<cursor|workbuddy|claude>/` when all of these hold:

- no fresh `.agent` manifest lists that workspace (heartbeat < 4 h)
- `gh pr list --head <branch>` is empty
- the tree is clean (`git status --porcelain` empty)

Script: `python tools/reap_stale_worktrees.py --tool cursor` (dry-run),
`--yes` to apply.

**Never** reap `wt/deploy`, `cp/rankwant`, or another tool's folder. Dirty
trees stay. `keep-manual` was rejected: Windows often fails `worktree remove`
at DONE, and leftover trees already numbered ~17.

HITL: one RankWant product question on the machine at a time (`HITL` lock).
A second agent does not open AskQuestion while that lock is fresh.

## Why these constraints exist

| Incident | Rule |
| --- | --- |
| Main checkout, no branch; live `api` without `deploy.sh`; git-sha `unknown` | never work in `cp/rankwant` |
| “Delete all worktrees” removed another agent’s unpushed commits | own `wt/<tool>/` only |
| Two deploys; compose from a feature tree mixed commits | one stack, `deploy.sh` + lock |
| `next dev` in a worktree locked `node_modules` junctions | prefer live verify after deploy |
| C: < 11 GB from Docker VHDX + many `node_modules` | cap write trees; stale-reap your tool folder |
| Three API PRs on two 4 CPU / 4 GB runners sharing Docker | serialize heavy merges |
