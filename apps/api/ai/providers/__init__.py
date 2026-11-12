"""Model providers behind one call: `complete(model, system, text, config)`.

`claude-cli` — `claude -p` on the owner's subscription (decision ⑨);
`anthropic` — the Claude API through the official SDK (decision ⑤), used
only with a key and switched back to `claude -p` when the month's budget is
spent (`tutor.tasks.config`).
"""
