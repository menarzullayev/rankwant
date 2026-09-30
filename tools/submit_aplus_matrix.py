"""One-off: submit A+B for every active language as admin; print verdict matrix.

Usage (inside API container / same DB as preview):
  python /app/tools/submit_aplus_matrix.py
  python /app/tools/submit_aplus_matrix.py --file
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

from core.models import User  # noqa: E402
from judging.models import Attempt  # noqa: E402
from judging.services import enqueue  # noqa: E402
from judging.verdicts import Verdict  # noqa: E402
from problems.models import Language, Problem  # noqa: E402

from aplus_solutions import APLUS  # noqa: E402
from aplus_file_solutions import APLUS_FILE  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--file",
        action="store_true",
        help="Submit file-I/O solutions (input.txt / output.txt) instead of stdin/stdout",
    )
    args = parser.parse_args()
    catalog = APLUS_FILE if args.file else APLUS
    mode_label = "file" if args.file else "stdio"
    admin = User.objects.filter(username="admin").first()
    if admin is None:
        print("admin user not found", file=sys.stderr)
        return 2
    problem = Problem.objects.filter(slug="a-plus-b").first()
    if problem is None:
        print("a-plus-b not found", file=sys.stderr)
        return 2

    langs = list(Language.objects.filter(is_active=True).order_by("code"))
    missing = [lang.code for lang in langs if lang.code not in catalog]
    if missing:
        print("Missing A+B source for:", ", ".join(missing), file=sys.stderr)
        return 2

    print(f"mode={mode_label} languages={len(langs)}", flush=True)
    batch: list[tuple[str, int]] = []
    for lang in langs:
        attempt = Attempt.objects.create(
            user=admin,
            problem=problem,
            language=lang,
            source_code=catalog[lang.code],
            verdict=Verdict.PENDING,
        )
        enqueue(attempt)
        batch.append((lang.code, attempt.pk))

    pending = {aid for _, aid in batch}
    deadline = time.time() + 600
    while pending and time.time() < deadline:
        for aid in list(pending):
            v = Attempt.objects.filter(pk=aid).values_list("verdict", flat=True).first()
            if v and v not in (Verdict.PENDING, Verdict.RUNNING):
                pending.discard(aid)
        if pending:
            time.sleep(2)

    print("code\tverdict\tms\tfailed_test\tattempt_id")
    ac = 0
    for code, aid in batch:
        row = Attempt.objects.get(pk=aid)
        if row.verdict == Verdict.AC:
            ac += 1
        print(
            f"{code}\t{row.verdict}\t{row.time_ms or ''}\t"
            f"{row.failed_test_index or ''}\t{aid}"
        )
    print(f"\nAC: {ac}/{len(batch)}")
    if pending:
        print(f"Timed out waiting for {len(pending)} attempts", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
