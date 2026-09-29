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
        ("core", "0027_user_origin"),
        # Upstream zanjiriga ulash — aks holda 0026_client_log alohida barg
        # bo'lib qoladi ("multiple leaf nodes" xatosi, merge'dan keyin
        # o'lchandi).
        ("core", "0026_client_log"),
    ]

    operations = [
        migrations.RunPython(_backfill, _noop),
    ]
