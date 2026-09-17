"""Judge languages — one entry per toolchain in the judge image (ADR-0004, ADR-0022).

`seed_demo` writes these rows, data migrations add them to deployed databases, and
`tests/compatibility/check_languages.py` compiles and runs every one inside the judge
image. Entries must stay plain literals: that check reads this file with
`ast.literal_eval`, without importing Django.

Commands are argv lists; `/bin/sh -c` appears only where one compile is two steps
(Go and Assembly). `{src}` is the saved source (`/box/<source_file>`) and `{bin}`
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
        # With colours on, kotlinc loads jansi, which unpacks a native library into the
        # read-only /tmp and prefixes every compile error with that failure.
        "compile": [
            "/opt/kotlinc/bin/kotlinc",
            "-J-Dkotlin.colors.enabled=false",
            "{src}",
            "-include-runtime",
            "-d",
            "{bin}.jar",
        ],
        "run": ["java", "-jar", "{bin}.jar"],
        "processes": 32,
        # kotlinc spends ~5 s of CPU on A+B alone.
        "compile_time_ms": 20_000,
    },
    # ── Group 2: on two rival judges or one (ADR-0022) ──
    {
        "code": "pascal322",
        "name": "Pascal",
        "version": "(Free Pascal 3.2)",
        "source_file": "main.pas",
        "compile": ["fpc", "-O2", "-XS", "-o{bin}", "{src}"],
        "run": ["{bin}"],
        "processes": 1,
    },
    {
        "code": "ruby33",
        "name": "Ruby",
        "version": "3.3",
        "source_file": "main.rb",
        "compile": [],
        "run": ["ruby", "{src}"],
        "processes": 8,
    },
    {
        "code": "haskell96",
        "name": "Haskell",
        "version": "(GHC 9.6)",
        "source_file": "main.hs",
        # ghc finds its own libraries through the loader cache (see the Dockerfile).
        "compile": ["/usr/bin/env", "TMPDIR=/box", "ghc", "-O2", "-o", "{bin}", "{src}"],
        "run": ["{bin}"],
        "processes": 1,
    },
    {
        "code": "r45",
        "name": "R",
        "version": "4.5",
        "source_file": "main.R",
        "compile": [],
        "run": ["/usr/bin/env", "TMPDIR=/box", "Rscript", "{src}"],
        "processes": 8,
        # R refuses to start with fewer open files ("limit on the number of open
        # files is too low"): it failed at 128 and started at 192.
        "open_files": 256,
    },
    {
        "code": "swift60",
        "name": "Swift",
        "version": "6.0",
        "source_file": "main.swift",
        "compile": [
            "/usr/bin/env",
            "TMPDIR=/box",
            "swiftc",
            "-O",
            "-static-stdlib",
            "-module-cache-path",
            "/box/.swiftcache",
            "-o",
            "{bin}",
            "{src}",
        ],
        "run": ["{bin}"],
        "processes": 8,
        # swiftc dies with signal 4 under the /proc mask.
        "proc_self": True,
    },
    {
        "code": "perl540",
        "name": "Perl",
        "version": "5.40",
        "source_file": "main.pl",
        "compile": [],
        "run": ["perl", "{src}"],
        "processes": 1,
    },
    {
        "code": "d140",
        "name": "D",
        "version": "(LDC 1.40)",
        "source_file": "main.d",
        "compile": ["ldc2", "-O", "-of={bin}", "{src}"],
        # Without this the GC starts a marking thread for every core but one.
        "run": ["{bin}", "--DRT-gcopt=parallel:0"],
        "processes": 4,
    },
    {
        "code": "ocaml53",
        "name": "OCaml",
        "version": "5.3",
        "source_file": "main.ml",
        "compile": [
            "/usr/bin/env",
            "TMPDIR=/box",
            "ocamlfind",
            "ocamlopt",
            "-package",
            "str,unix",
            "-linkpkg",
            "-o",
            "{bin}",
            "{src}",
        ],
        "run": ["{bin}"],
        "processes": 1,
    },
    {
        "code": "ts24",
        "name": "TypeScript",
        "version": "(Node.js 24)",
        "source_file": "main.ts",
        "compile": [],
        # Node.js strips the types and does not check them. Without the transform
        # flag it rejects enums and constructor parameter properties.
        "run": ["/opt/node/bin/node", "--experimental-transform-types", "{src}"],
        "processes": 16,
    },
    {
        "code": "dart313",
        "name": "Dart",
        "version": "3.13",
        "source_file": "main.dart",
        "compile": [
            "/usr/bin/env",
            "TMPDIR=/box",
            "/opt/dart-sdk/bin/dart",
            "compile",
            "exe",
            "{src}",
            "-o",
            "{bin}",
        ],
        "run": ["{bin}"],
        "processes": 16,
        # The Dart VM reads its stack bounds from /proc/self, in the compiler and in
        # the compiled program alike.
        "proc_self": True,
    },
    {
        "code": "scala39",
        "name": "Scala",
        "version": "3.9",
        "source_file": "Main.scala",
        # scalac colours its errors even when stdout is not a terminal.
        "compile": ["/opt/scala/bin/scalac", "-color:never", "-d", "/box", "{src}"],
        # scala.jar lists only the runtime libraries: the compiler stays off the classpath.
        "run": ["java", "-cp", "/opt/scala/lib/scala.jar:/box", "Main"],
        "processes": 32,
        "compile_time_ms": 20_000,
    },
    # ── Group 3: the rest of the TIOBE top 50, plus PyPy and F# (ADR-0022) ──
    {
        "code": "vbnet17",
        "name": "Visual Basic .NET",
        "version": "17.13 (.NET 10)",
        "source_file": "main.vb",
        "compile": [
            "/usr/bin/env",
            "DOTNET_EnableWriteXorExecute=0",
            "/opt/dotnet/dotnet",
            "/opt/rankwant/dotnet/roslyn/vbc.dll",
            "@/opt/rankwant/dotnet/vbc.rsp",
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
        "proc_self": True,
    },
    {
        "code": "fortran14",
        "name": "Fortran",
        "version": "(GFortran 14)",
        "source_file": "main.f90",
        "compile": ["gfortran", "-O2", "-o", "{bin}", "{src}"],
        "run": ["{bin}"],
        "processes": 1,
    },
    {
        "code": "nasm216",
        "name": "Assembly",
        "version": "(NASM 2.16, x86-64)",
        "source_file": "main.asm",
        "compile": [
            "/bin/sh",
            "-c",
            "nasm -f elf64 -o /box/prog.o {src} && ld -o {bin} /box/prog.o",
        ],
        "run": ["{bin}"],
        "processes": 1,
    },
    {
        "code": "ada14",
        "name": "Ada",
        "version": "(GNAT 14)",
        "source_file": "main.adb",
        "compile": ["gnatmake", "-O2", "-o", "{bin}", "{src}"],
        "run": ["{bin}"],
        "processes": 1,
    },
    {
        "code": "objc14",
        "name": "Objective-C",
        "version": "(GCC 14, GNUstep)",
        "source_file": "main.m",
        # GCC's runtime: no ARC and no @autoreleasepool, NSAutoreleasePool works.
        "compile": [
            "gcc",
            "-O2",
            "-fconstant-string-class=NSConstantString",
            "-fobjc-exceptions",
            "-I/usr/include/x86_64-linux-gnu/GNUstep",
            "-o",
            "{bin}",
            "{src}",
            "-lgnustep-base",
            "-lobjc",
        ],
        "run": ["{bin}"],
        "processes": 8,
    },
    {
        "code": "cobol32",
        "name": "COBOL",
        "version": "(GnuCOBOL 3.2)",
        "source_file": "main.cob",
        "compile": ["/usr/bin/env", "TMPDIR=/box", "cobc", "-x", "-O2", "-o", "{bin}", "{src}"],
        "run": ["{bin}"],
        "processes": 1,
    },
    {
        "code": "julia113",
        "name": "Julia",
        "version": "1.13",
        "source_file": "main.jl",
        "compile": [],
        # Julia finds its own libraries from its executable's path, read from /proc/self.
        "run": [
            "/usr/bin/env",
            "JULIA_DEPOT_PATH=/box/.julia",
            "/opt/julia/bin/julia",
            "--startup-file=no",
            "--history-file=no",
            "{src}",
        ],
        "processes": 32,
        "proc_self": True,
    },
    {
        "code": "caml53",
        "name": "Caml",
        "version": "(OCaml 5.3 toplevel)",
        "source_file": "main.ml",
        "compile": [],
        "run": ["ocaml", "{src}"],
        "processes": 1,
    },
    {
        "code": "prolog92",
        "name": "Prolog",
        "version": "(SWI-Prolog 9.2)",
        "source_file": "main.pl",
        "compile": [],
        "run": ["swipl", "{src}"],
        "processes": 8,
    },
    {
        "code": "lua54",
        "name": "Lua",
        "version": "5.4",
        "source_file": "main.lua",
        "compile": [],
        "run": ["lua5.4", "{src}"],
        "processes": 1,
    },
    {
        "code": "powershell76",
        "name": "PowerShell",
        "version": "7.6",
        "source_file": "main.ps1",
        "compile": [],
        "run": [
            "/usr/bin/env",
            "DOTNET_EnableWriteXorExecute=0",
            "POWERSHELL_TELEMETRY_OPTOUT=1",
            "TMPDIR=/box",
            "/opt/powershell/pwsh",
            "-NoProfile",
            "-NonInteractive",
            "-File",
            "{src}",
        ],
        "processes": 64,
        "proc_self": True,
        # PowerShell fails with FileNotFound below ~192 open files.
        "open_files": 256,
    },
    {
        "code": "lisp25",
        "name": "Common Lisp",
        "version": "(SBCL 2.5)",
        "source_file": "main.lisp",
        "compile": [],
        "run": ["sbcl", "--script", "{src}"],
        "processes": 8,
    },
    {
        "code": "pypy73",
        "name": "PyPy",
        "version": "7.3",
        "source_file": "main.py",
        "compile": [],
        "run": ["pypy3", "{src}"],
        "processes": 4,
    },
    {
        "code": "fsharp10",
        "name": "F#",
        "version": "10 (.NET 10)",
        "source_file": "main.fs",
        # fsc copies FSharp.Core.dll next to the program, where the run loads it from.
        "compile": [
            "/usr/bin/env",
            "DOTNET_EnableWriteXorExecute=0",
            "/opt/dotnet/dotnet",
            "/opt/rankwant/dotnet/fsharp/fsc.dll",
            "@/opt/rankwant/dotnet/fsc.rsp",
            "--out:{bin}.dll",
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
        "proc_self": True,
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
