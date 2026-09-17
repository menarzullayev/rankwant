"""Group 3 judge languages (ADR-0022): Visual Basic .NET, Fortran, Assembly, Ada,
Objective-C, COBOL, Julia, Caml, Prolog, Lua, PowerShell, Common Lisp, PyPy, F#.

The rows are frozen here as problems/languages.py had them when this migration was
written; tests/test_languages.py checks that the migrated rows still match the catalog.

A problem whose allow-list names all three founding languages was imported with every
language allowed, so it receives the new ones as well. A problem restricted to a subset
(Python-only exercises, for example) keeps its restriction.
"""

from django.db import migrations
from django.db.models import Count

FOUNDING = ("cpp23", "java21", "py313")

LANGUAGES = [
    {
        "code": "vbnet17",
        "name": "Visual Basic .NET",
        "version": "17.13 (.NET 10)",
        "source_file": "main.vb",
        "compile_cmd": [
            "/usr/bin/env",
            "DOTNET_EnableWriteXorExecute=0",
            "/opt/dotnet/dotnet",
            "/opt/rankwant/dotnet/roslyn/vbc.dll",
            "@/opt/rankwant/dotnet/vbc.rsp",
            "-out:{bin}.dll",
            "{src}",
        ],
        "run_cmd": [
            "/usr/bin/env",
            "DOTNET_EnableWriteXorExecute=0",
            "/opt/dotnet/dotnet",
            "exec",
            "--runtimeconfig",
            "/opt/rankwant/dotnet/app.runtimeconfig.json",
            "{bin}.dll",
        ],
        "process_limit": 32,
        "compile_time_ms": 10000,
        "proc_self": True,
        "open_files": 0,
    },
    {
        "code": "fortran14",
        "name": "Fortran",
        "version": "(GFortran 14)",
        "source_file": "main.f90",
        "compile_cmd": ["gfortran", "-O2", "-o", "{bin}", "{src}"],
        "run_cmd": ["{bin}"],
        "process_limit": 1,
        "compile_time_ms": 10000,
        "proc_self": False,
        "open_files": 0,
    },
    {
        "code": "nasm216",
        "name": "Assembly",
        "version": "(NASM 2.16, x86-64)",
        "source_file": "main.asm",
        "compile_cmd": [
            "/bin/sh",
            "-c",
            "nasm -f elf64 -o /box/prog.o {src} && ld -o {bin} /box/prog.o",
        ],
        "run_cmd": ["{bin}"],
        "process_limit": 1,
        "compile_time_ms": 10000,
        "proc_self": False,
        "open_files": 0,
    },
    {
        "code": "ada14",
        "name": "Ada",
        "version": "(GNAT 14)",
        "source_file": "main.adb",
        "compile_cmd": ["gnatmake", "-O2", "-o", "{bin}", "{src}"],
        "run_cmd": ["{bin}"],
        "process_limit": 1,
        "compile_time_ms": 10000,
        "proc_self": False,
        "open_files": 0,
    },
    {
        "code": "objc14",
        "name": "Objective-C",
        "version": "(GCC 14, GNUstep)",
        "source_file": "main.m",
        "compile_cmd": [
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
        "run_cmd": ["{bin}"],
        "process_limit": 8,
        "compile_time_ms": 10000,
        "proc_self": False,
        "open_files": 0,
    },
    {
        "code": "cobol32",
        "name": "COBOL",
        "version": "(GnuCOBOL 3.2)",
        "source_file": "main.cob",
        "compile_cmd": ["/usr/bin/env", "TMPDIR=/box", "cobc", "-x", "-O2", "-o", "{bin}", "{src}"],
        "run_cmd": ["{bin}"],
        "process_limit": 1,
        "compile_time_ms": 10000,
        "proc_self": False,
        "open_files": 0,
    },
    {
        "code": "julia113",
        "name": "Julia",
        "version": "1.13",
        "source_file": "main.jl",
        "compile_cmd": [],
        "run_cmd": [
            "/usr/bin/env",
            "JULIA_DEPOT_PATH=/box/.julia",
            "/opt/julia/bin/julia",
            "--startup-file=no",
            "--history-file=no",
            "{src}",
        ],
        "process_limit": 32,
        "compile_time_ms": 10000,
        "proc_self": True,
        "open_files": 0,
    },
    {
        "code": "caml53",
        "name": "Caml",
        "version": "(OCaml 5.3 toplevel)",
        "source_file": "main.ml",
        "compile_cmd": [],
        "run_cmd": ["ocaml", "{src}"],
        "process_limit": 1,
        "compile_time_ms": 10000,
        "proc_self": False,
        "open_files": 0,
    },
    {
        "code": "prolog92",
        "name": "Prolog",
        "version": "(SWI-Prolog 9.2)",
        "source_file": "main.pl",
        "compile_cmd": [],
        "run_cmd": ["swipl", "{src}"],
        "process_limit": 8,
        "compile_time_ms": 10000,
        "proc_self": False,
        "open_files": 0,
    },
    {
        "code": "lua54",
        "name": "Lua",
        "version": "5.4",
        "source_file": "main.lua",
        "compile_cmd": [],
        "run_cmd": ["lua5.4", "{src}"],
        "process_limit": 1,
        "compile_time_ms": 10000,
        "proc_self": False,
        "open_files": 0,
    },
    {
        "code": "powershell76",
        "name": "PowerShell",
        "version": "7.6",
        "source_file": "main.ps1",
        "compile_cmd": [],
        "run_cmd": [
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
        "process_limit": 64,
        "compile_time_ms": 10000,
        "proc_self": True,
        "open_files": 256,
    },
    {
        "code": "lisp25",
        "name": "Common Lisp",
        "version": "(SBCL 2.5)",
        "source_file": "main.lisp",
        "compile_cmd": [],
        "run_cmd": ["sbcl", "--script", "{src}"],
        "process_limit": 8,
        "compile_time_ms": 10000,
        "proc_self": False,
        "open_files": 0,
    },
    {
        "code": "pypy73",
        "name": "PyPy",
        "version": "7.3",
        "source_file": "main.py",
        "compile_cmd": [],
        "run_cmd": ["pypy3", "{src}"],
        "process_limit": 4,
        "compile_time_ms": 10000,
        "proc_self": False,
        "open_files": 0,
    },
    {
        "code": "fsharp10",
        "name": "F#",
        "version": "10 (.NET 10)",
        "source_file": "main.fs",
        "compile_cmd": [
            "/usr/bin/env",
            "DOTNET_EnableWriteXorExecute=0",
            "/opt/dotnet/dotnet",
            "/opt/rankwant/dotnet/fsharp/fsc.dll",
            "@/opt/rankwant/dotnet/fsc.rsp",
            "--out:{bin}.dll",
            "{src}",
        ],
        "run_cmd": [
            "/usr/bin/env",
            "DOTNET_EnableWriteXorExecute=0",
            "/opt/dotnet/dotnet",
            "exec",
            "--runtimeconfig",
            "/opt/rankwant/dotnet/app.runtimeconfig.json",
            "{bin}.dll",
        ],
        "process_limit": 32,
        "compile_time_ms": 10000,
        "proc_self": True,
        "open_files": 0,
    },
]


def open_problem_ids(apps, founding_ids):
    """Problems whose allow-list includes every founding language."""
    ProblemLanguage = apps.get_model("problems", "ProblemLanguage")
    return list(
        ProblemLanguage.objects.filter(language_id__in=founding_ids)
        .values("problem_id")
        .annotate(allowed=Count("language_id", distinct=True))
        .filter(allowed=len(founding_ids))
        .values_list("problem_id", flat=True)
    )


def add_languages(apps, schema_editor):
    Language = apps.get_model("problems", "Language")
    ProblemLanguage = apps.get_model("problems", "ProblemLanguage")
    added = []
    for row in LANGUAGES:
        fields = {key: value for key, value in row.items() if key != "code"}
        language, _ = Language.objects.update_or_create(code=row["code"], defaults=fields)
        added.append(language)

    founding_ids = list(Language.objects.filter(code__in=FOUNDING).values_list("pk", flat=True))
    if len(founding_ids) < len(FOUNDING):
        return  # no founding rows yet (a fresh database): no allow-lists to extend
    ProblemLanguage.objects.bulk_create(
        [
            ProblemLanguage(problem_id=problem_id, language=language)
            for problem_id in open_problem_ids(apps, founding_ids)
            for language in added
        ],
        ignore_conflicts=True,
    )


def remove_languages(apps, schema_editor):
    """Attempts point at these rows with PROTECT, so they are switched off, not deleted."""
    Language = apps.get_model("problems", "Language")
    ProblemLanguage = apps.get_model("problems", "ProblemLanguage")
    codes = [row["code"] for row in LANGUAGES]
    ProblemLanguage.objects.filter(language__code__in=codes).delete()
    Language.objects.filter(code__in=codes).update(is_active=False)


class Migration(migrations.Migration):
    dependencies = [
        ("problems", "0019_kotlin_colors_off"),
    ]

    operations = [
        migrations.RunPython(add_languages, remove_languages),
    ]
