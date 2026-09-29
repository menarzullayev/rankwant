# WP3: User.origin backfill — M3

from django.db import migrations


def _backfill(apps, schema_editor) -> None:
    """Data migration: backfill_origin command ni chaqiradi."""
    from django.core.management import call_command

    call_command("backfill_origin")


def _noop(apps, schema_editor) -> None:
    """Teskari yo'nalish — bo'sh (origin maydoni qoladi)."""
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0026_user_origin"),
    ]

    operations = [
        migrations.RunPython(_backfill, _noop),
    ]
