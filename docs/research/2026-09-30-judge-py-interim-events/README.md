# judge-py interim events vs judge-go (2026-09-30)

## Stack default

`docker-compose.yml` builds **`services/judge-go`** as the judge service. Preview smoke
(`tools/verify_live_judge_progress.py`) exercises that path only.

## Code parity (static)

| `kind` | judge-go (`emit.go`) | judge-py (`judge.py`) |
|--------|----------------------|------------------------|
| `progress` | yes | yes (`running_test_index`) |
| `compilation_started` | yes | yes |
| `compilation_finished` | yes | yes |
| `test_finished` | yes | yes |

Worker routing: `apps/api/judging/tasks.py` handles all four kinds before final
`apply_result`.

## Not verified in this note

- Running `judge-py` as the live judge container against Redis results queue.
- Nightly/CI job that swaps `JUDGE_PROVIDER` or judge image to Python.

## Scope recommendation

Treat **judge-go** as the launch gate for interim SSE. Add a dedicated harness test
for judge-py when Python judge is promoted to CI or production.
