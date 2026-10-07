#!/usr/bin/env python3
"""Split the API test files into shards for the Nightly coverage job.

    python3 tools/pytest_shard.py 2 3      # files of shard 2 of 3, one per line
    python3 tools/pytest_shard.py --check 3

The whole suite took 323 s in one job (measured 2026-10-07) and was the
longest job of a warm Nightly. Shards run side by side.

The split is by file, never by test: fixtures are scoped to modules, and a
file is the unit `pytest -n` already balances inside a shard. Files are
dealt out largest first to the lightest shard, with size in bytes standing
in for run time. Nothing is stored — the same tree gives the same shards —
so a new test file lands in a shard without anybody editing a list. That
is the property `--check` proves: every test file is in exactly one shard.
"""

from __future__ import annotations

import sys
from pathlib import Path

API = Path(__file__).resolve().parent.parent / "apps" / "api"
TESTS = API / "tests"


def test_files(tests: Path = TESTS) -> list[Path]:
    """Every file pytest collects (`python_files = test_*.py`), sorted."""
    return sorted(tests.rglob("test_*.py"))


def shards(files: list[Path], count: int) -> list[list[Path]]:
    if count < 1:
        raise ValueError("the shard count must be at least 1")
    buckets: list[list[Path]] = [[] for _ in range(count)]
    weights = [0] * count
    # Largest first; ties and equal weights resolve by name and by index, so
    # the result does not depend on the order the file system lists files in.
    for path in sorted(files, key=lambda p: (-p.stat().st_size, p.as_posix())):
        lightest = weights.index(min(weights))
        buckets[lightest].append(path)
        weights[lightest] += path.stat().st_size
    return [sorted(bucket) for bucket in buckets]


def check(count: int, tests: Path = TESTS) -> list[str]:
    """Problems with the split; empty when every file is in exactly one shard."""
    files = test_files(tests)
    if not files:
        return [f"no test files under {tests}"]
    problems: list[str] = []
    seen: dict[Path, int] = {}
    for number, bucket in enumerate(shards(files, count), start=1):
        if not bucket:
            problems.append(f"shard {number}/{count} is empty")
        for path in bucket:
            if path in seen:
                problems.append(f"{path.name} is in shards {seen[path]} and {number}")
            seen[path] = number
    problems += [f"{path.name} is in no shard" for path in files if path not in seen]
    return problems


def main(argv: list[str]) -> int:
    if len(argv) == 2 and argv[0] == "--check":
        count = int(argv[1])
        problems = check(count)
        for problem in problems:
            print(f"FAIL {problem}", file=sys.stderr)
        if problems:
            return 1
        sizes = [len(bucket) for bucket in shards(test_files(), count)]
        print(f"ok: {sum(sizes)} test files in {count} shards: {sizes}")
        return 0
    if len(argv) == 2:
        index, count = int(argv[0]), int(argv[1])
        if not 1 <= index <= count:
            print(f"shard {index} of {count} does not exist", file=sys.stderr)
            return 2
        for path in shards(test_files(), count)[index - 1]:
            print(path.relative_to(API).as_posix())
        return 0
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
