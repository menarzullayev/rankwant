from django.db import migrations


def seed(apps, schema_editor):
    """The three paid plans exist from the start, none on sale: staff set
    the prices and the features text, then switch a plan on (ADR-0057)."""
    Plan = apps.get_model("billing", "Plan")
    for code in ("plus", "pro", "judge"):
        Plan.objects.get_or_create(code=code)


class Migration(migrations.Migration):
    dependencies = [("billing", "0001_initial")]

    operations = [migrations.RunPython(seed, migrations.RunPython.noop)]
