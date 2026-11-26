"""A partial index for `User.last_active_date`.

The streak reminders (`notifications/reminders.py`) and the region map
(`profiles/regions.py`) filter `core_user` on this column. It had no index:
measured on production 2026-11-26, `last_active_date = current_date - 1`
was a parallel sequential scan over 974 513 rows, 88 ms, for 9 rows that
have the column set (the imported accounts never do). The index covers only
those rows, so it stays tiny.

Built CONCURRENTLY, as in `0031_search_trigram`: a plain `CREATE INDEX`
holds a write lock on `core_user`, and signing in writes that table. That is
why the migration is not atomic. SQLite (local tests) skips it.
"""

from django.db import migrations

NAME = "core_user_last_active_date"


def build(apps, schema_editor):  # type: ignore[no-untyped-def]
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute(
        f'CREATE INDEX CONCURRENTLY IF NOT EXISTS "{NAME}" ON "core_user" ("last_active_date") '
        'WHERE "last_active_date" IS NOT NULL'
    )


def drop(apps, schema_editor):  # type: ignore[no-untyped-def]
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute(f'DROP INDEX CONCURRENTLY IF EXISTS "{NAME}"')


class Migration(migrations.Migration):
    atomic = False

    dependencies = [("core", "0039_knowndevice")]

    operations = [migrations.RunPython(build, drop)]
