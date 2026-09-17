"""Judge languages — one entry per toolchain in the judge image (ADR-0004, ADR-0022).

`seed_demo` writes these rows, data migrations add them to deployed databases, and
`tests/compatibility/check_languages.py` compiles and runs every one inside the judge
image. Entries must stay plain literals: that check reads this file with
`ast.literal_eval`, without importing Django.

Commands are argv lists, never shell strings. `{src}` is the saved source
(`/box/<source_file>`) and `{bin}` is `/box/prog`; `/box` is the only writable
directory inside the sandbox.

Optional keys, with the defaults `row_values` fills in:
  compile_time_ms  CPU budget for one compile (10_000)
  proc_self        mount a procfs of the sandbox's own processes (False)
  open_files       RLIMIT_NOFILE for programs, 0 = the judge's 64 (0)
"""

from __future__ import annotations

from typing import Any

LANGUAGES: list[dict[str, Any]] = [
    {
        "code": "cpp23",
        "name": "C++",
        "version": "23",
        "source_file": "main.cpp",
        "compile": ["g++", "-std=c++23", "-O2", "-o", "{bin}", "{src}"],
        "run": ["{bin}"],
        "processes": 1,
    },
    {
        "code": "py313",
        "name": "Python",
        "version": "3.13",
        "source_file": "main.py",
        "compile": [],
        "run": ["python3", "{src}"],
        "processes": 1,
    },
    {
        "code": "java21",
        "name": "Java",
        "version": "21",
        "source_file": "Main.java",
        "compile": ["javac", "{src}"],
        "run": ["java", "-cp", "/box", "Main"],
        # The JVM opens 18 threads even for an empty program (measured).
        "processes": 32,
    },
]


def row_values(spec: dict[str, Any]) -> dict[str, Any]:
    """Catalog entry → `Language` field values (everything but `code`)."""
    return {
        "name": spec["name"],
        "version": spec["version"],
        "source_file": spec["source_file"],
        "compile_cmd": spec["compile"],
        "run_cmd": spec["run"],
        "process_limit": spec["processes"],
        "compile_time_ms": spec.get("compile_time_ms", 10_000),
        "proc_self": spec.get("proc_self", False),
        "open_files": spec.get("open_files", 0),
    }
