"""Trigram indexes for the site search.

`core_user` holds ~974k rows and the search matched them with
`LIKE '%x%'` on two columns no index could serve. A GIN trigram index
over the folded text serves a substring of three or more characters and
a prefix of any length.

Built CONCURRENTLY: a plain `CREATE INDEX` holds a write lock on
`core_user` for the whole build, and signing in writes that table. That
is why the migration is not atomic. SQLite (local tests) skips it.
"""

from django.contrib.postgres.operations import TrigramExtension
from django.db import migrations

from core.search import FOLD_PG

INDEXES = {
    "core_user_username_trgm": ("core_user", "username"),
    "core_user_display_trgm": ("core_user", "display_name"),
}


def build(apps, schema_editor):  # type: ignore[no-untyped-def]
    if schema_editor.connection.vendor != "postgresql":
        return
    for name, (table, column) in INDEXES.items():
        expression = FOLD_PG.format(column=f'"{column}"')
        schema_editor.execute(
            f'CREATE INDEX CONCURRENTLY IF NOT EXISTS "{name}" '
            f'ON "{table}" USING gin (({expression}) gin_trgm_ops)'
        )


def drop(apps, schema_editor):  # type: ignore[no-untyped-def]
    if schema_editor.connection.vendor != "postgresql":
        return
    for name in INDEXES:
        schema_editor.execute(f'DROP INDEX CONCURRENTLY IF EXISTS "{name}"')


class Migration(migrations.Migration):
    atomic = False

    dependencies = [("core", "0030_deletion_grace")]

    operations = [TrigramExtension(), migrations.RunPython(build, drop)]
