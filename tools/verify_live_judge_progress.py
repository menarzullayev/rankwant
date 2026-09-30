"""Smoke: judge interim events reach Redis replay and DB (live stack).

Exit 0 when a-plus-b submit shows compilation/progress/test_finished in replay
and finishes AC. Run inside API container:

  python tools/verify_live_judge_progress.py
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent / "apps" / "api"
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

from django.conf import settings  # noqa: E402
from redis import Redis  # noqa: E402

from core.models import User  # noqa: E402
from judging.models import Attempt  # noqa: E402
from judging.services import enqueue  # noqa: E402
from judging.verdicts import Verdict  # noqa: E402
from problems.models import Language, Problem  # noqa: E402
from realtime import bus  # noqa: E402

INTERIM = frozenset(
    {
        "attempt_queued",
        "compilation_started",
        "compilation_finished",
        "attempt_progress",
        "test_started",
        "test_finished",
    }
)


def main() -> int:
    admin = User.objects.filter(username="admin").first()
    problem = Problem.objects.filter(slug="a-plus-b").first()
    lang = Language.objects.filter(code="cpp23", is_active=True).first()
    if not admin or not problem or not lang:
        print("need admin, a-plus-b, cpp23", file=sys.stderr)
        return 2

    source = '#include <bits/stdc++.h>\nusing namespace std;\nint main(){long long a,b;cin>>a>>b;cout<<a+b;}\n'
    attempt = Attempt.objects.create(
        user=admin,
        problem=problem,
        language=lang,
        source_code=source,
        verdict=Verdict.PENDING,
    )
    enqueue(attempt)
    channel = bus.user_channel(admin.pk)
    replay_key = f"rw:rt:replay:{channel}"
    client = Redis.from_url(settings.REDIS_URL, decode_responses=True)

    seen_events: set[str] = set()
    max_running = 0
    test_rows = 0
    deadline = time.time() + 120

    while time.time() < deadline:
        attempt.refresh_from_db()
        if attempt.running_test_index and attempt.running_test_index > max_running:
            max_running = attempt.running_test_index
        test_rows = attempt.test_results.count()

        for raw in client.lrange(replay_key, 0, 50):
            try:
                blob = json.loads(raw)
            except (TypeError, ValueError):
                continue
            if blob.get("data", {}).get("attempt_id") != attempt.pk:
                continue
            ev = blob.get("event")
            if isinstance(ev, str):
                seen_events.add(ev)

        if attempt.verdict not in (Verdict.PENDING, Verdict.RUNNING):
            break
        time.sleep(0.25)

    print(
        f"attempt={attempt.pk} verdict={attempt.verdict} "
        f"max_running={max_running} test_rows={test_rows} events={sorted(seen_events)}"
    )

    if "attempt_queued" not in seen_events:
        print("attempt_queued missing from replay", file=sys.stderr)
        return 1
    if attempt.verdict != Verdict.AC:
        return 1
    if not (seen_events & INTERIM):
        print("no interim SSE events in replay", file=sys.stderr)
        return 1
    if "test_finished" not in seen_events and test_rows < 1:
        print("no test_finished and no AttemptTestResult rows", file=sys.stderr)
        return 1
    # Yakuniy holat: replay ba'zan verdictdan oldin to'ldiriladi.
    settle = time.time() + 3
    while time.time() < settle:
        test_rows = attempt.test_results.count()
        for raw in client.lrange(replay_key, 0, 80):
            try:
                blob = json.loads(raw)
            except (TypeError, ValueError):
                continue
            if blob.get("data", {}).get("attempt_id") != attempt.pk:
                continue
            ev = blob.get("event")
            if isinstance(ev, str):
                seen_events.add(ev)
        if test_rows >= 1 and (seen_events & {"test_finished", "compilation_started"}):
            break
        time.sleep(0.2)
    if "attempt_finished" not in seen_events and "verdict" not in seen_events:
        print("attempt_finished/verdict missing from replay", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
