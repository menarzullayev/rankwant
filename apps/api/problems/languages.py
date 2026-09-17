"""Judge languages — one entry per toolchain in the judge image (ADR-0004, ADR-0022).

`seed_demo` writes these rows, data migrations add them to deployed databases, and
`tests/compatibility/check_languages.py` compiles and runs every one inside the judge
image. Entries must stay plain literals: that check reads this file with
`ast.literal_eval`, without importing Django.

Commands are argv lists; `/bin/sh -c` appears only where one compile is two steps
(Go, and later Assembly). `{src}` is the saved source (`/box/<source_file>`) and `{bin}`
is `/box/prog`; `/box` is the only writable directory inside the sandbox.

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
    # ── Group 1: on KEP.uz, Robocontest and Codeforces (ADR-0022) ──
    {
        "code": "c17",
        "name": "C",
        "version": "17",
        "source_file": "main.c",
        # gnu17, not c17: glibc hides POSIX functions (strdup, getline) in strict
        # mode, and GCC 14 turns their implicit declarations into errors.
        "compile": ["gcc", "-std=gnu17", "-O2", "-o", "{bin}", "{src}", "-lm"],
        "run": ["{bin}"],
        "processes": 1,
    },
    {
        "code": "csharp14",
        "name": "C#",
        "version": "14 (.NET 10)",
        "source_file": "main.cs",
        # Roslyn straight from the SDK: a project build would need NuGet restore,
        # and the sandbox has no network. References come from csc.rsp.
        "compile": [
            "/usr/bin/env",
            "DOTNET_EnableWriteXorExecute=0",
            "/opt/dotnet/dotnet",
            "/opt/rankwant/dotnet/roslyn/csc.dll",
            "@/opt/rankwant/dotnet/csc.rsp",
            "-out:{bin}.dll",
            "{src}",
        ],
        "run": [
            "/usr/bin/env",
            "DOTNET_EnableWriteXorExecute=0",
            "/opt/dotnet/dotnet",
            "exec",
            "--runtimeconfig",
            "/opt/rankwant/dotnet/app.runtimeconfig.json",
            "{bin}.dll",
        ],
        "processes": 32,
        # CoreCLR reads /proc/self; under the mask it fails with 0x8007000E.
        "proc_self": True,
    },
    {
        "code": "js24",
        "name": "JavaScript",
        "version": "(Node.js 24)",
        "source_file": "main.js",
        "compile": [],
        "run": ["/opt/node/bin/node", "{src}"],
        "processes": 16,
    },
    {
        "code": "rust185",
        "name": "Rust",
        "version": "1.85",
        "source_file": "main.rs",
        # rustc writes its temporary files to TMPDIR; /tmp is read-only in the sandbox.
        "compile": [
            "/usr/bin/env",
            "TMPDIR=/box",
            "rustc",
            "--edition=2021",
            "-O",
            "-o",
            "{bin}",
            "{src}",
        ],
        "run": ["{bin}"],
        "processes": 1,
    },
    {
        "code": "go124",
        "name": "Go",
        "version": "1.24",
        "source_file": "main.go",
        # Compile and link against the standard library built into the image:
        # `go build` needs a writable cache and spends ~5.6 s filling it.
        "compile": [
            "/bin/sh",
            "-c",
            "GOROOT=/usr/lib/go-1.24"
            " /usr/lib/go-1.24/pkg/tool/linux_amd64/compile -p main -complete"
            " -importcfg /opt/go-std/importcfg -o /box/main.a {src}"
            " && GOROOT=/usr/lib/go-1.24"
            " /usr/lib/go-1.24/pkg/tool/linux_amd64/link"
            " -importcfg /opt/go-std/importcfg -o {bin} /box/main.a",
        ],
        "run": ["{bin}"],
        "processes": 16,
    },
    {
        "code": "php84",
        "name": "PHP",
        "version": "8.4",
        "source_file": "main.php",
        "compile": [],
        "run": ["php", "{src}"],
        "processes": 1,
    },
    {
        "code": "kotlin24",
        "name": "Kotlin",
        "version": "2.4",
        "source_file": "main.kt",
        "compile": ["/opt/kotlinc/bin/kotlinc", "{src}", "-include-runtime", "-d", "{bin}.jar"],
        "run": ["java", "-jar", "{bin}.jar"],
        "processes": 32,
        # kotlinc spends ~5 s of CPU on A+B alone.
        "compile_time_ms": 20_000,
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
