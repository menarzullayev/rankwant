# deploy-panel

A Claude Code mod: a pane showing `origin/main` next to the commit the live
site reports, and how long they have differed. Two images answer: the API at
`/api/v1/version/` and the web app at `/version`. A deploy rebuilds only what
changed, so the site counts as current when either one matches main.

```bash
claude --plugin-dir tools/mods/deploy-panel   # then /deploy-panel
```

- Refreshes at session start, after a turn (at most every 30 s), on the
  "Yangilash" button and on `/deploy-panel`.
- A difference older than 15 minutes is shown as stuck. It cannot see the
  deploy lock or the watcher log: those live on the host only.
- Needs the host to reach `rankwant.uz` and `git ls-remote origin`.

Tests: `claude plugin test tools/mods/deploy-panel`.
