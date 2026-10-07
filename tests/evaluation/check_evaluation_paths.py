"""Special checker, interactive and scorer — proven on a real judge.

Each of the three has a reference problem (`apps/api/problems/reference_problems.py`)
and, next to it, a table of submissions with the verdict and score each must
receive. This harness sends every one of them through the door a user uses:

    POST /attempts/ → queue → judge (nsjail) → checker / interactor
                    → result → database → GET /attempts/<id>/

and fails when a verdict or a score differs. Unit tests cannot see this
path: they replace the sandbox, the checker process and the pipes between
a solution and its interactor.

Run it inside the compose network, with `worker` and `judge` alive and the
problems installed:

    docker compose ... exec -T api python manage.py seed_reference_problems
    docker compose -f docker-compose.yml -f docker-compose.ci.yml \\
      --profile evaluation run --rm evaluation

| Variable | Default | Meaning |
| --- | --- | --- |
| `API` | `http://api:8000/api/v1` | Which API is checked |
| `EVALUATION_LANGUAGE` | `py313` | The language the samples are written in |
| `VERDICT_TIMEOUT` | `120` | Seconds to wait for one verdict |

Output: a table for a person and one line for a machine,
`EVALUATION_JSON: {...}` — printed on failure too.
"""

from __future__ import annotations

import json
import os
import secrets
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
# In the compose service the module is mounted at `/reference`; in a
# checkout it is read from where it lives.
for candidate in (Path("/reference"), HERE.parent.parent / "apps" / "api" / "problems"):
    if (candidate / "reference_problems.py").exists():
        sys.path.insert(0, str(candidate))
        break

from reference_problems import REFERENCES  # noqa: E402

API = os.environ.get("API", "http://api:8000/api/v1")
LANGUAGE = os.environ.get("EVALUATION_LANGUAGE", "py313")
DEADLINE = int(os.environ.get("VERDICT_TIMEOUT", "120"))

WAITING = ("", "PENDING", "RUNNING", "pending", "running")
REPORT_MARKER = "EVALUATION_JSON: "


def request(path: str, data: dict | None = None, cookie: str = "") -> tuple:
    url = API + path
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(url, data=body, method="POST" if data else "GET")  # noqa: S310
    if body:
        req.add_header("Content-Type", "application/json")
    if cookie:
        req.add_header("Cookie", cookie)
        token = dict(c.split("=", 1) for c in cookie.split("; ") if "=" in c).get("csrftoken")
        if token and body:
            req.add_header("X-CSRFToken", token)
            req.add_header("Referer", url)
    try:
        resp = urllib.request.urlopen(req, timeout=30)  # noqa: S310
    except urllib.error.HTTPError as error:
        detail = error.read().decode(errors="replace")[:500]
        print(f"✗ {req.get_method()} {path} → HTTP {error.code}: {detail}", file=sys.stderr)
        raise
    with resp:
        raw = resp.read().decode()
        parsed = json.loads(raw) if raw.startswith(("{", "[")) else raw
        return parsed, resp.headers.get_all("Set-Cookie") or []


def login() -> tuple[str, str]:
    suffix = f"{int(time.time())}{secrets.token_hex(3)}"
    creds = {
        "username": f"evaluation{suffix}",
        "email": f"evaluation{suffix}@rankwant.uz",
        "password": secrets.token_urlsafe(24),
        "terms_accepted": True,
    }
    request("/auth/register/", creds)
    _, cookies = request(
        "/auth/login/", {"identifier": creds["username"], "password": creds["password"]}
    )
    if not cookies:
        raise RuntimeError("login returned no session")
    return "; ".join(c.split(";")[0] for c in cookies), creds["username"]


def submit(session: str, slug: str, source: str, language: str = "") -> dict:
    """One submission to its final state, as the attempt endpoint returns it."""
    body, _ = request(
        "/attempts/",
        {"problem": slug, "language": language or LANGUAGE, "source_code": source},
        cookie=session,
    )
    attempt_id = body["id"]
    end = time.monotonic() + DEADLINE
    while time.monotonic() < end:
        body, _ = request(f"/attempts/{attempt_id}/", cookie=session)
        if (body.get("verdict") or "") not in WAITING:
            return body
        time.sleep(1)
    raise TimeoutError(f"no verdict in {DEADLINE}s (attempt {attempt_id})")


def main() -> int:
    body, _ = request("/health/")
    if body.get("status") != "ok":
        print(f"✗ a dependency is down: {body.get('checks')}", file=sys.stderr)
        return 1

    session, username = login()
    rows: list[dict] = []
    print(f"Evaluation paths on {API} (as {username}):")
    for ref in REFERENCES:
        problem, _ = request(f"/problems/{ref.slug}/")
        kind = ref.task_kind if ref.task_kind != "program" else ref.checker_type
        print(f"\n{kind}: {ref.slug} (#{problem.get('code')})")
        for case in ref.cases:
            attempt = submit(session, ref.slug, case.source, case.language)
            got = (attempt.get("verdict"), attempt.get("score"))
            # The list a visitor sees must say the same as the detail page.
            listed, _ = request(f"/attempts/?problem={ref.slug}&username={username}", cookie=session)
            in_list = next((r for r in listed["results"] if r["id"] == attempt["id"]), {})
            ok = got == (case.verdict, case.score) and (
                in_list.get("verdict"),
                in_list.get("score"),
            ) == got
            rows.append(
                {
                    "problem": ref.slug,
                    "checker_type": ref.checker_type,
                    "task_kind": ref.task_kind,
                    "language": case.language or LANGUAGE,
                    "case": case.name,
                    "attempt": attempt["id"],
                    "expected": {"verdict": case.verdict, "score": case.score},
                    "actual": {"verdict": got[0], "score": got[1]},
                    "listed": {"verdict": in_list.get("verdict"), "score": in_list.get("score")},
                    "time_ms": attempt.get("time_ms"),
                    "ok": ok,
                }
            )
            mark = "✓" if ok else "✗"
            print(
                f"  {mark} #{attempt['id']:<6} {case.name:<44} "
                f"expected {case.verdict}/{case.score}, got {got[0]}/{got[1]}"
            )

    failed = [row for row in rows if not row["ok"]]
    print(REPORT_MARKER + json.dumps({"api": API, "ok": not failed, "rows": rows}, ensure_ascii=False))
    if failed:
        print(f"\n✗ {len(failed)} of {len(rows)} submissions were graded wrongly", file=sys.stderr)
        return 1
    print(f"\n✓ {len(rows)} submissions, every verdict and score as expected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
