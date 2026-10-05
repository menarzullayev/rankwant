"""Trigram index on the problem title's search form (see core 0031)."""

from django.db import migrations

NAME = "problems_title_search_trgm"


def build(apps, schema_editor):  # type: ignore[no-untyped-def]
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute(
        f'CREATE INDEX CONCURRENTLY IF NOT EXISTS "{NAME}" '
        'ON "problems_problem" USING gin ("title_search" gin_trgm_ops)'
    )


def drop(apps, schema_editor):  # type: ignore[no-untyped-def]
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute(f'DROP INDEX CONCURRENTLY IF EXISTS "{NAME}"')


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ("problems", "0030_judge_env_base"),
        ("core", "0031_search_trigram"),
    ]

    operations = [migrations.RunPython(build, drop)]
