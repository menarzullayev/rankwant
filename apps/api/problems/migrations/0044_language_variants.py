"""Judge language variants: C++17, C++20, Java 8, C# 8, C# 10, Rust 2024 edition.

Decision 2026-11-15 (docs/decisions/2026-11-15-language-variants.md). Codeforces offers
several versions of the same language; every one of these runs on a toolchain the judge
image already holds, so none of them adds a byte to the image:

  * C++17 and C++20 — the same g++ 14 with another `-std`;
  * Java 8 — `javac --release 8` (syntax and API of Java 8) on the JDK 21 runtime;
  * C# 8 and C# 10 — the same Roslyn with `-langversion`, on the .NET 10 runtime;
  * Rust 2024 — the same rustc 1.85 with `--edition=2024` (the existing row is 2021).

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
        "code": "cpp17",
        "name": "C++",
        "version": "17",
        "source_file": "main.cpp",
        "compile_cmd": ["g++", "-std=c++17", "-O2", "-o", "{bin}", "{src}"],
        "run_cmd": ["{bin}"],
        "process_limit": 1,
        "compile_time_ms": 10000,
        "proc_self": False,
        "open_files": 0,
        "memory_overhead_kb": 2048,
    },
    {
        "code": "cpp20",
        "name": "C++",
        "version": "20",
        "source_file": "main.cpp",
        "compile_cmd": ["g++", "-std=c++20", "-O2", "-o", "{bin}", "{src}"],
        "run_cmd": ["{bin}"],
        "process_limit": 1,
        "compile_time_ms": 10000,
        "proc_self": False,
        "open_files": 0,
        "memory_overhead_kb": 2048,
    },
    {
        "code": "java8",
        "name": "Java",
        "version": "8",
        "source_file": "Main.java",
        "compile_cmd": ["javac", "--release", "8", "-Xlint:-options", "{src}"],
        "run_cmd": ["java", "-cp", "/box", "Main"],
        "process_limit": 32,
        "compile_time_ms": 10000,
        "proc_self": False,
        "open_files": 0,
        "memory_overhead_kb": 21504,
    },
    {
        "code": "csharp8",
        "name": "C#",
        "version": "8 (.NET 10)",
        "source_file": "main.cs",
        "compile_cmd": [
            "/usr/bin/env",
            "DOTNET_EnableWriteXorExecute=0",
            "/opt/dotnet/dotnet",
            "/opt/rankwant/dotnet/roslyn/csc.dll",
            "@/opt/rankwant/dotnet/csc.rsp",
            "-langversion:8",
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
        "memory_overhead_kb": 7168,
    },
    {
        "code": "csharp10",
        "name": "C#",
        "version": "10 (.NET 10)",
        "source_file": "main.cs",
        "compile_cmd": [
            "/usr/bin/env",
            "DOTNET_EnableWriteXorExecute=0",
            "/opt/dotnet/dotnet",
            "/opt/rankwant/dotnet/roslyn/csc.dll",
            "@/opt/rankwant/dotnet/csc.rsp",
            "-langversion:10",
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
        "memory_overhead_kb": 7168,
    },
    {
        "code": "rust2024",
        "name": "Rust",
        "version": "1.85 (edition 2024)",
        "source_file": "main.rs",
        "compile_cmd": [
            "/usr/bin/env",
            "TMPDIR=/box",
            "rustc",
            "--edition=2024",
            "-O",
            "-o",
            "{bin}",
            "{src}",
        ],
        "run_cmd": ["{bin}"],
        "process_limit": 1,
        "compile_time_ms": 10000,
        "proc_self": False,
        "open_files": 0,
        "memory_overhead_kb": 2048,
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
        ("problems", "0043_go_127"),
    ]

    operations = [
        migrations.RunPython(add_languages, remove_languages),
    ]
