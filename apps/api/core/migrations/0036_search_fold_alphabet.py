"""The search fold learns the new alphabet (ADR-0059).

`FOLD_PG` now also maps `ö ğ ş ç` onto `o g sh ch` and drops `ʼ`. An
expression index is only used when the query spells the expression the
same way, so the user indexes of 0031 are rebuilt: the new ones first,
under new names, then the old ones go — searching never runs without an
index on `core_user` (~974k rows). CONCURRENTLY, as in 0031: a plain
`CREATE INDEX` holds a write lock for the build and signing in writes
that table. SQLite (local tests) skips it.
"""

from django.db import migrations

from core.search import FOLD_PG

NEW = {
    "core_user_username_trgm2": ("core_user", "username"),
    "core_user_display_trgm2": ("core_user", "display_name"),
}
OLD = ("core_user_username_trgm", "core_user_display_trgm")


def build(apps, schema_editor):  # type: ignore[no-untyped-def]
    if schema_editor.connection.vendor != "postgresql":
        return
    for name, (table, column) in NEW.items():
        expression = FOLD_PG.format(column=f'"{column}"')
        schema_editor.execute(
            f'CREATE INDEX CONCURRENTLY IF NOT EXISTS "{name}" '
            f'ON "{table}" USING gin (({expression}) gin_trgm_ops)'
        )
    for name in OLD:
        schema_editor.execute(f'DROP INDEX CONCURRENTLY IF EXISTS "{name}"')


def drop(apps, schema_editor):  # type: ignore[no-untyped-def]
    # Going back: the fold of 0031 is not kept anywhere, so the indexes of
    # this migration stay; they still serve the old queries' substrings.
    return


class Migration(migrations.Migration):
    atomic = False

    dependencies = [("core", "0035_plan_judge")]

    operations = [migrations.RunPython(build, drop)]
