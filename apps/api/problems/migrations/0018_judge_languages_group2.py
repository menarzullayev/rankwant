"""Group 2 judge languages (ADR-0022): Pascal, Ruby, Haskell, R, Swift, Perl, D, OCaml,
TypeScript, Dart, Scala.

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
        "code": "pascal322",
        "name": "Pascal",
        "version": "(Free Pascal 3.2)",
        "source_file": "main.pas",
        "compile_cmd": ["fpc", "-O2", "-XS", "-o{bin}", "{src}"],
        "run_cmd": ["{bin}"],
        "process_limit": 1,
        "compile_time_ms": 10000,
        "proc_self": False,
        "open_files": 0,
    },
    {
        "code": "ruby33",
        "name": "Ruby",
        "version": "3.3",
        "source_file": "main.rb",
        "compile_cmd": [],
        "run_cmd": ["ruby", "{src}"],
        "process_limit": 8,
        "compile_time_ms": 10000,
        "proc_self": False,
        "open_files": 0,
    },
    {
        "code": "haskell96",
        "name": "Haskell",
        "version": "(GHC 9.6)",
        "source_file": "main.hs",
        "compile_cmd": ["/usr/bin/env", "TMPDIR=/box", "ghc", "-O2", "-o", "{bin}", "{src}"],
        "run_cmd": ["{bin}"],
        "process_limit": 1,
        "compile_time_ms": 10000,
        "proc_self": False,
        "open_files": 0,
    },
    {
        "code": "r45",
        "name": "R",
        "version": "4.5",
        "source_file": "main.R",
        "compile_cmd": [],
        "run_cmd": ["/usr/bin/env", "TMPDIR=/box", "Rscript", "{src}"],
        "process_limit": 8,
        "compile_time_ms": 10000,
        "proc_self": False,
        "open_files": 256,
    },
    {
        "code": "swift60",
        "name": "Swift",
        "version": "6.0",
        "source_file": "main.swift",
        "compile_cmd": [
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
        "run_cmd": ["{bin}"],
        "process_limit": 8,
        "compile_time_ms": 10000,
        "proc_self": True,
        "open_files": 0,
    },
    {
        "code": "perl540",
        "name": "Perl",
        "version": "5.40",
        "source_file": "main.pl",
        "compile_cmd": [],
        "run_cmd": ["perl", "{src}"],
        "process_limit": 1,
        "compile_time_ms": 10000,
        "proc_self": False,
        "open_files": 0,
    },
    {
        "code": "d140",
        "name": "D",
        "version": "(LDC 1.40)",
        "source_file": "main.d",
        "compile_cmd": ["ldc2", "-O", "-of={bin}", "{src}"],
        "run_cmd": ["{bin}", "--DRT-gcopt=parallel:0"],
        "process_limit": 4,
        "compile_time_ms": 10000,
        "proc_self": False,
        "open_files": 0,
    },
    {
        "code": "ocaml53",
        "name": "OCaml",
        "version": "5.3",
        "source_file": "main.ml",
        "compile_cmd": [
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
        "run_cmd": ["{bin}"],
        "process_limit": 1,
        "compile_time_ms": 10000,
        "proc_self": False,
        "open_files": 0,
    },
    {
        "code": "ts24",
        "name": "TypeScript",
        "version": "(Node.js 24)",
        "source_file": "main.ts",
        "compile_cmd": [],
        "run_cmd": ["/opt/node/bin/node", "--experimental-transform-types", "{src}"],
        "process_limit": 16,
        "compile_time_ms": 10000,
        "proc_self": False,
        "open_files": 0,
    },
    {
        "code": "dart313",
        "name": "Dart",
        "version": "3.13",
        "source_file": "main.dart",
        "compile_cmd": [
            "/usr/bin/env",
            "TMPDIR=/box",
            "/opt/dart-sdk/bin/dart",
            "compile",
            "exe",
            "{src}",
            "-o",
            "{bin}",
        ],
        "run_cmd": ["{bin}"],
        "process_limit": 16,
        "compile_time_ms": 10000,
        "proc_self": True,
        "open_files": 0,
    },
    {
        "code": "scala39",
        "name": "Scala",
        "version": "3.9",
        "source_file": "Main.scala",
        "compile_cmd": ["/opt/scala/bin/scalac", "-color:never", "-d", "/box", "{src}"],
        "run_cmd": ["java", "-cp", "/opt/scala/lib/scala.jar:/box", "Main"],
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
        ("problems", "0017_judge_languages_group1"),
    ]

    operations = [
        migrations.RunPython(add_languages, remove_languages),
    ]
