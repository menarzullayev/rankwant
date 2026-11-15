#!/usr/bin/env python3
"""Write `tools/negative_rule_map.json` from a recording of the decisions negatives.

    NEGATIVE_RECORD=/tmp/rec.tsv python3 tools/check_negative.py decisions
    python3 tools/negative_rule_map.py /tmp/rec.tsv

Each line of the recording is `test_function<TAB>rule label`. The map lets a
decision negative test run only the rule it exercises (`check_decisions.py
--only LABEL`) instead of all of them. A test missing from the map runs every
rule, so a stale map costs time and never changes a verdict.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent / "negative_rule_map.json"


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print(__doc__)
        return 2
    mapping: dict[str, str] = {}
    for line in Path(argv[0]).read_text(encoding="utf-8").splitlines():
        test, _, label = line.partition("\t")
        if test and label:
            mapping[test] = label
    text = json.dumps(dict(sorted(mapping.items())), ensure_ascii=False, indent=0) + "\n"
    OUT.write_bytes(text.encode("utf-8"))  # bytes: LF on Windows too
    print(f"{len(mapping)} tests mapped -> {OUT.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
