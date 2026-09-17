"""Kotlin compiles with colours off.

With colours on, kotlinc loads jansi, which unpacks a native library into /tmp. /tmp is
read-only in the sandbox, so every Kotlin compile error began with
"/tmp/jansi-2.4.0-….lck (Read-only file system)". Without colours jansi is never loaded.

A row an admin has already changed is left alone.
"""

from django.db import migrations

BEFORE = ["/opt/kotlinc/bin/kotlinc", "{src}", "-include-runtime", "-d", "{bin}.jar"]
AFTER = [
    "/opt/kotlinc/bin/kotlinc",
    "-J-Dkotlin.colors.enabled=false",
    "{src}",
    "-include-runtime",
    "-d",
    "{bin}.jar",
]


def replace(apps, old, new):
    Language = apps.get_model("problems", "Language")
    for language in Language.objects.filter(code="kotlin24"):
        if language.compile_cmd == old:
            language.compile_cmd = new
            language.save(update_fields=["compile_cmd"])


def forwards(apps, schema_editor):
    replace(apps, BEFORE, AFTER)


def backwards(apps, schema_editor):
    replace(apps, AFTER, BEFORE)


class Migration(migrations.Migration):
    dependencies = [
        ("problems", "0018_judge_languages_group2"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
