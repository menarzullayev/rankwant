# Attempt live progress — browser E2E evidence (2026-09-30)

## Automated backend (pass)

```text
docker cp tools/verify_live_judge_progress.py rankwant-api-1:/tmp/
docker exec -w /app -e PYTHONPATH=/app rankwant-api-1 python /tmp/verify_live_judge_progress.py
# attempt=442740 verdict=AC max_running=82 test_rows=100
# events: attempt_queued, compilation_*, test_started/finished, attempt_progress, verdict, attempt_finished
```

## Browser session (partial)

- Logged-in user on `8312`, problem `a-plus-b`.
- Submit disabled until editor has code + allowed language (page showed Julia-only hint).
- In-page `fetch('/api/v1/...')` returned HTML (wrong origin path for API on dev-local;
  client uses `NEXT_PUBLIC_API_BASE=http://127.0.0.1:8301/api/v1`).

## Manual checklist (8310/8312 + Docker backend)

1. `powershell -File tools/dev-local.ps1` (or port 8312 if `RANKWANT_DEV_WEB_PORT` set).
2. Open `/problems/a-plus-b`, choose **C++23**, paste A+B solution, **Yuborish**.
3. **Natija** tab: compiling → per-test list → AC; DevTools → EventSource
   `/api/v1/attempts/{id}/events/` (rewrite to `:8302`).
4. **Urinishlar** tab: pending row shows compact live progress.

## Dev SSE rewrite

`apps/web/next.config.ts` rewrites attempt events to `http://127.0.0.1:8302` in development only.
