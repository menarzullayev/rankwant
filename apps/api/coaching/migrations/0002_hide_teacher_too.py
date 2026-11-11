"""Who hid "coach" before ADR-0061 hid their classroom teacher: keep it hidden.

Until 2026-11-11 the "coach" privacy switch hid the owners of the user's
classrooms. That row is now "teacher"; without this, those users would see
their teachers shown on their profile again.
"""

from django.db import migrations


def forwards(apps, schema_editor):
    User = apps.get_model("core", "User")
    rows = User.objects.only("pk", "hidden_fields")
    if schema_editor.connection.vendor == "postgresql":
        # ~974k accounts in production: let the database find the few.
        rows = rows.filter(hidden_fields__contains=["coach"])
    for user in rows.iterator():
        if "coach" not in (user.hidden_fields or []):
            continue
        fields = list(user.hidden_fields or [])
        if "teacher" not in fields:
            fields.append("teacher")
            User.objects.filter(pk=user.pk).update(hidden_fields=fields)


class Migration(migrations.Migration):
    dependencies = [("coaching", "0001_initial"), ("core", "0038_plan_quota")]

    operations = [migrations.RunPython(forwards, migrations.RunPython.noop)]
