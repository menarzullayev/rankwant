"""Fill the team page with what it launched with (2026-10-05).

Only into an empty table: a database where somebody has already edited
the team keeps what it has. The roles are read from `team/seed.py` at the
time this migration runs — the same values the page shipped with as a
static file before the admin panel existed.
"""

from __future__ import annotations

from typing import Any

from django.db import migrations

from team import seed


def fill(apps: Any, schema_editor: Any) -> None:
    Department = apps.get_model("team", "Department")
    Role = apps.get_model("team", "Role")
    Member = apps.get_model("team", "Member")
    if Department.objects.exists() or Role.objects.exists() or Member.objects.exists():
        return
    departments = [Department.objects.create(**row) for row in seed.DEPARTMENTS]
    for row in seed.ROLES:
        fields = dict(row)
        fields["department"] = departments[fields["department"]]
        Role.objects.create(**fields)
    Member.objects.create(**seed.FOUNDER)


class Migration(migrations.Migration):
    dependencies = [("team", "0001_initial")]

    operations = [migrations.RunPython(fill, migrations.RunPython.noop)]
