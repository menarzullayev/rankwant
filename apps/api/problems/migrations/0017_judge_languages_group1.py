"""Group 1 judge languages (ADR-0022): C, C#, JavaScript, Rust, Go, PHP, Kotlin.

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
        "code": "c17",
        "name": "C",
        "version": "17",
        "source_file": "main.c",
        "compile_cmd": ["gcc", "-std=gnu17", "-O2", "-o", "{bin}", "{src}", "-lm"],
        "run_cmd": ["{bin}"],
        "process_limit": 1,
        "compile_time_ms": 10000,
        "proc_self": False,
        "open_files": 0,
    },
    {
        "code": "csharp14",
        "name": "C#",
        "version": "14 (.NET 10)",
        "source_file": "main.cs",
        "compile_cmd": [
            "/usr/bin/env",
            "DOTNET_EnableWriteXorExecute=0",
            "/opt/dotnet/dotnet",
            "/opt/rankwant/dotnet/roslyn/csc.dll",
            "@/opt/rankwant/dotnet/csc.rsp",
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
        "code": "js24",
        "name": "JavaScript",
        "version": "(Node.js 24)",
        "source_file": "main.js",
        "compile_cmd": [],
        "run_cmd": ["/opt/node/bin/node", "{src}"],
        "process_limit": 16,
        "compile_time_ms": 10000,
        "proc_self": False,
        "open_files": 0,
    },
    {
        "code": "rust185",
        "name": "Rust",
        "version": "1.85",
        "source_file": "main.rs",
        "compile_cmd": [
            "/usr/bin/env",
            "TMPDIR=/box",
            "rustc",
            "--edition=2021",
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
    },
    {
        "code": "go124",
        "name": "Go",
        "version": "1.24",
        "source_file": "main.go",
        "compile_cmd": [
            "/bin/sh",
            "-c",
            "GOROOT=/usr/lib/go-1.24 "
            "/usr/lib/go-1.24/pkg/tool/linux_amd64/compile -p main -complete "
            "-importcfg /opt/go-std/importcfg -o /box/main.a {src} && "
            "GOROOT=/usr/lib/go-1.24 /usr/lib/go-1.24/pkg/tool/linux_amd64/link "
            "-importcfg /opt/go-std/importcfg -o {bin} /box/main.a",
        ],
        "run_cmd": ["{bin}"],
        "process_limit": 16,
        "compile_time_ms": 10000,
        "proc_self": False,
        "open_files": 0,
    },
    {
        "code": "php84",
        "name": "PHP",
        "version": "8.4",
        "source_file": "main.php",
        "compile_cmd": [],
        "run_cmd": ["php", "{src}"],
        "process_limit": 1,
        "compile_time_ms": 10000,
        "proc_self": False,
        "open_files": 0,
    },
    {
        "code": "kotlin24",
        "name": "Kotlin",
        "version": "2.4",
        "source_file": "main.kt",
        "compile_cmd": ["/opt/kotlinc/bin/kotlinc", "{src}", "-include-runtime", "-d", "{bin}.jar"],
        "run_cmd": ["java", "-jar", "{bin}.jar"],
        "process_limit": 32,
        "compile_time_ms": 20000,
        "proc_self": False,
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
        ("problems", "0016_language_judge_fields"),
    ]

    operations = [
        migrations.RunPython(add_languages, remove_languages),
    ]
